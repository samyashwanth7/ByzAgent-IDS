"""XFed-IDS: Federated Retraining with Continual Learning

Loads the current global model, merges analyst-confirmed feedback samples
into the CICIDS-2017 training set, re-partitions via Non-IID Dirichlet,
and runs FedAvg for NUM_ROUNDS rounds starting from the existing weights.
"""
import sys
import copy
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    BASE_DIR, MODEL_DIR, NUM_ROUNDS, NUM_CLIENTS, BATCH_SIZE,
    LEARNING_RATE, LOCAL_EPOCHS, NON_IID_ALPHA, RANDOM_SEED,
    INPUT_DIM, NUM_CLASSES, DP_ENABLED, DP_EPSILON, DP_DELTA, DP_CLIP_NORM,
)
from src.model import IDSModel, count_parameters
from src.dataset import (
    load_cicids2017,
    partition_data_non_iid,
    create_dataloaders,
)
from src.utils import (
    set_seed, get_device, train_one_epoch, evaluate,
    print_metrics, save_model,
)
import math

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GLOBAL_MODEL_PATH = MODEL_DIR / "federated_iid_fedavg.pt"
FEEDBACK_DIR = BASE_DIR / "data" / "feedback"
CONFIRMED_ATTACKS = FEEDBACK_DIR / "confirmed_attacks.csv"
CONFIRMED_BENIGN = FEEDBACK_DIR / "confirmed_benign.csv"


# ---------------------------------------------------------------------------
# Differential Privacy noise injection
# ---------------------------------------------------------------------------
def add_dp_noise(state_dict, clip_norm, epsilon, delta, num_clients):
    """Apply (epsilon, delta)-Differential Privacy via Gaussian mechanism."""
    sigma = clip_norm * math.sqrt(2.0 * math.log(1.25 / delta)) / epsilon
    noisy_dict = {}
    for key, tensor in state_dict.items():
        norm = torch.norm(tensor.float())
        clip_factor = min(1.0, clip_norm / (norm.item() + 1e-8))
        clipped = tensor.float() * clip_factor
        noise = torch.normal(mean=0.0, std=sigma / num_clients, size=clipped.shape)
        noisy_dict[key] = clipped + noise
    return noisy_dict


# ---------------------------------------------------------------------------
# FedAvg aggregation with optional DP
# ---------------------------------------------------------------------------
def fedavg_aggregate(global_model, client_models, client_sizes, use_dp=DP_ENABLED):
    """Weighted average of client model parameters with optional DP noise."""
    global_dict = global_model.state_dict()
    total_size = sum(client_sizes)
    for key in global_dict.keys():
        global_dict[key] = torch.zeros_like(global_dict[key], dtype=torch.float32)
        for i, client_model in enumerate(client_models):
            weight = client_sizes[i] / total_size
            global_dict[key] += weight * client_model.state_dict()[key].float()

    if use_dp:
        global_dict = add_dp_noise(global_dict, DP_CLIP_NORM, DP_EPSILON, DP_DELTA, len(client_models))
        print('    [DP] Gaussian noise applied (eps={}, delta={})'.format(DP_EPSILON, DP_DELTA))

    global_model.load_state_dict(global_dict)
    return global_model


# ---------------------------------------------------------------------------
# Feedback loader
# ---------------------------------------------------------------------------
def load_feedback_samples():
    """Load analyst-confirmed CSVs and return (X, y) arrays or (None, None)."""
    frames = []

    for csv_path in (CONFIRMED_ATTACKS, CONFIRMED_BENIGN):
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if "label" not in df.columns:
                print("[WARN] Skipping {} -- missing 'label' column".format(csv_path.name))
                continue
            print("  Loaded {} rows from {}".format(len(df), csv_path.name))
            frames.append(df)

    if not frames:
        return None, None

    combined = pd.concat(frames, ignore_index=True)
    y = combined["label"].values.astype(np.int64)
    X = combined.drop(columns=["label"]).values.astype(np.float32)
    return X, y


# ---------------------------------------------------------------------------
# Main retraining routine
# ---------------------------------------------------------------------------
def retrain():
    set_seed(RANDOM_SEED)
    device = get_device()

    print("=" * 65)
    print("  XFed-IDS: Federated Retraining (Continual Learning)")
    print("=" * 65)

    # ------------------------------------------------------------------
    # 1. Load CICIDS-2017 base dataset
    # ------------------------------------------------------------------
    print("\n[1/6] Loading CICIDS-2017 dataset...")
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    input_dim = X_train.shape[1]
    num_classes = len(label_names)

    # ------------------------------------------------------------------
    # 2. Load analyst feedback and merge
    # ------------------------------------------------------------------
    print("\n[2/6] Checking for analyst feedback samples...")
    fb_X, fb_y = load_feedback_samples()
    if fb_X is not None:
        n_feedback = len(fb_y)
        n_attacks = int((fb_y == 1).sum())
        n_benign = int((fb_y == 0).sum())
        print("  Merging {} feedback samples ({} attack, {} benign) "
              "into training data".format(n_feedback, n_attacks, n_benign))
        X_train = np.vstack([X_train, fb_X])
        y_train = np.concatenate([y_train, fb_y])
        print("  Combined training set: {:,} samples".format(len(y_train)))
    else:
        print("  No feedback files found -- using base dataset only")

    # ------------------------------------------------------------------
    # 3. Load current global model (continual learning)
    # ------------------------------------------------------------------
    print("\n[3/6] Loading current global model...")
    global_model = IDSModel(input_dim=input_dim, num_classes=num_classes)

    if GLOBAL_MODEL_PATH.exists():
        state = torch.load(GLOBAL_MODEL_PATH, map_location="cpu", weights_only=True)
        global_model.load_state_dict(state)
        print("  Loaded weights from {}".format(GLOBAL_MODEL_PATH.name))
    else:
        print("  [WARN] No existing model at {} -- starting from random init"
              .format(GLOBAL_MODEL_PATH))

    # Evaluate BEFORE retraining so we can compare later
    criterion = nn.CrossEntropyLoss()
    from src.dataset import IDSDataset
    from torch.utils.data import DataLoader
    test_loader = DataLoader(
        IDSDataset(X_test, y_test), batch_size=BATCH_SIZE, shuffle=False
    )
    old_result = evaluate(global_model, test_loader, criterion, device)
    print("  Old model accuracy: {:.4f} ({:.2f}%)".format(
        old_result["accuracy"], old_result["accuracy"] * 100))

    # ------------------------------------------------------------------
    # 4. Partition data (Non-IID Dirichlet)
    # ------------------------------------------------------------------
    print("\n[4/6] Partitioning data across {} clients "
          "(Non-IID Dirichlet alpha={})...".format(NUM_CLIENTS, NON_IID_ALPHA))
    partitions = partition_data_non_iid(
        X_train, y_train, num_clients=NUM_CLIENTS, alpha=NON_IID_ALPHA
    )
    client_loaders = create_dataloaders(partitions, X_test, y_test, batch_size=BATCH_SIZE)
    client_sizes = [len(p["y"]) for p in partitions]

    # ------------------------------------------------------------------
    # 5. Federated training loop (FedAvg)
    # ------------------------------------------------------------------
    print("\n[5/6] Starting FedAvg training ({} rounds, {} local epochs)...".format(
        NUM_ROUNDS, LOCAL_EPOCHS))
    print("-" * 65)

    start_time = time.time()
    for round_num in range(1, NUM_ROUNDS + 1):
        client_models = []
        for client_id in range(NUM_CLIENTS):
            local_model = IDSModel(input_dim=input_dim, num_classes=num_classes)
            local_model.load_state_dict(copy.deepcopy(global_model.state_dict()))

            trainloader, _ = client_loaders[client_id]
            optimizer = torch.optim.Adam(local_model.parameters(), lr=LEARNING_RATE)

            for _epoch in range(LOCAL_EPOCHS):
                train_one_epoch(local_model, trainloader, optimizer, criterion, device)

            client_models.append(local_model)

        global_model = fedavg_aggregate(global_model, client_models, client_sizes)

        test_result = evaluate(global_model, test_loader, criterion, device)
        print("  Round {:2d}/{} | Loss: {:.4f} | Acc: {:.4f} | F1: {:.4f}".format(
            round_num, NUM_ROUNDS,
            test_result["loss"], test_result["accuracy"], test_result["f1"]))

    elapsed = time.time() - start_time

    # ------------------------------------------------------------------
    # 6. Save models
    # ------------------------------------------------------------------
    print("\n[6/6] Saving retrained model...")
    new_result = evaluate(global_model, test_loader, criterion, device)

    # Overwrite current global model
    save_model(global_model, GLOBAL_MODEL_PATH)

    # Versioned backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = MODEL_DIR / "federated_v{}.pt".format(timestamp)
    save_model(global_model, backup_path)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  Retraining Summary")
    print("=" * 65)
    print("  Training time:   {:.1f}s".format(elapsed))
    print("  Rounds:          {}".format(NUM_ROUNDS))
    print("  Clients:         {}".format(NUM_CLIENTS))
    print("  Dirichlet alpha: {}".format(NON_IID_ALPHA))
    if fb_X is not None:
        print("  Feedback samples: {}".format(n_feedback))
    else:
        print("  Feedback samples: 0")
    print("-" * 65)
    print("  OLD Accuracy:  {:.4f} ({:.2f}%)".format(
        old_result["accuracy"], old_result["accuracy"] * 100))
    print("  NEW Accuracy:  {:.4f} ({:.2f}%)".format(
        new_result["accuracy"], new_result["accuracy"] * 100))
    delta = new_result["accuracy"] - old_result["accuracy"]
    direction = "+" if delta >= 0 else ""
    print("  Delta:         {}{:.4f} ({}{:.2f}%)".format(
        direction, delta, direction, delta * 100))
    print("-" * 65)
    print("  OLD F1: {:.4f}  |  NEW F1: {:.4f}".format(
        old_result["f1"], new_result["f1"]))
    print("  OLD Loss: {:.4f} | NEW Loss: {:.4f}".format(
        old_result["loss"], new_result["loss"]))
    print("=" * 65)
    print("[OK] Federated retraining complete.")
    print("  Model saved to: {}".format(GLOBAL_MODEL_PATH))
    print("  Backup saved to: {}".format(backup_path))

    return global_model, old_result, new_result


if __name__ == "__main__":
    retrain()
