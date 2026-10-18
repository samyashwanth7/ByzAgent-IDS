"""ByzAgent-IDS: Federated Training Simulation with Byzantine Attacks and Defenses"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

import argparse
import config
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import time
import copy
import json
import math
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from config import (NUM_ROUNDS, NUM_CLIENTS, BATCH_SIZE, LEARNING_RATE,
                    LOCAL_EPOCHS, NON_IID_ALPHA, RESULTS_DIR, MODEL_DIR,
                    RANDOM_SEED, FEDPROX_MU, DP_ENABLED, DP_EPSILON,
                    DP_DELTA, DP_CLIP_NORM)
from src.monitoring.client_stats import ByzAgentMonitor
from src.agents.byz_agent import ByzAgentTrustArbiter
from src.aggregation.robust_baselines import krum_aggregate, trimmed_mean_aggregate
from src.model import IDSModel, count_parameters
from src.dataset import (load_cicids2017, partition_data_iid, partition_data_non_iid, IDSDataset)
from src.utils import (set_seed, get_device, train_one_epoch, evaluate, print_metrics, save_results, save_model)

def fedavg_aggregate(global_model, client_models, client_sizes, use_dp=DP_ENABLED):
    old_dict = {k: v.clone().float() for k, v in global_model.state_dict().items()}
    new_dict = global_model.state_dict()
    total_size = sum(client_sizes)

    for key in new_dict.keys():
        new_dict[key] = torch.zeros_like(new_dict[key], dtype=torch.float32)
        for i, client_model in enumerate(client_models):
            weight = client_sizes[i] / total_size
            new_dict[key] += weight * client_model.state_dict()[key].float()

    if use_dp:
        sigma = DP_CLIP_NORM * math.sqrt(2.0 * math.log(1.25 / DP_DELTA)) / DP_EPSILON
        for key in new_dict.keys():
            delta = new_dict[key] - old_dict[key]
            delta_norm = torch.norm(delta)
            clip_factor = min(1.0, DP_CLIP_NORM / (delta_norm.item() + 1e-8))
            delta = delta * clip_factor
            noise = torch.normal(mean=0.0, std=sigma / len(client_models), size=delta.shape)
            new_dict[key] = old_dict[key] + delta + noise
        print('    [DP] Noise on updates (eps={}, clip={})'.format(DP_EPSILON, DP_CLIP_NORM))

    global_model.load_state_dict(new_dict)
    return global_model

def train_local_fedprox(model, global_model, dataloader, optimizer, criterion, device, mu=0.01):
    model.train()
    model.to(device)
    global_model.to(device)
    total_loss = 0.0
    correct = 0
    total = 0
    global_params = list(global_model.parameters())
    for batch_x, batch_y in dataloader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        prox_term = 0.0
        for local_param, global_param in zip(model.parameters(), global_params):
            prox_term += ((local_param - global_param.detach()) ** 2).sum()
        loss += (mu / 2) * prox_term
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch_x.size(0)
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)
    return {'loss': total_loss / total, 'accuracy': correct / total}

def evaluate_rule_baseline(round_stats):
    """Simple rule-based heuristic baseline for Byzantine client detection."""
    losses = [s['local_loss'] for s in round_stats.values()]
    med_loss = float(np.median(losses)) if len(losses) > 0 else 1.0
    decisions = []
    for cid, s in round_stats.items():
        if s['val_accuracy'] < config.RULE_VAL_ACC_THRESHOLD or s['local_loss'] > (config.RULE_LOSS_MEDIAN_FACTOR * med_loss):
            dec = 'quarantine'
            exp = f"Rule: val_acc {s['val_accuracy']:.2f} < {config.RULE_VAL_ACC_THRESHOLD} or loss {s['local_loss']:.2f} > {config.RULE_LOSS_MEDIAN_FACTOR * med_loss:.2f}"
        elif s['cos_sim_peer_mean'] < config.RULE_COS_SIM_THRESHOLD:
            dec = 'downweight'
            exp = f"Rule: cos_sim {s['cos_sim_peer_mean']:.2f} < {config.RULE_COS_SIM_THRESHOLD}"
        else:
            dec = 'trust'
            exp = "Rule: metrics within normal thresholds"
        decisions.append({'client_id': cid, 'decision': dec, 'explanation': exp})
    return {'decisions': decisions}

def aggregate_with_decisions(global_model, client_models, client_sizes, decisions_list):
    """Applies trust/downweight/quarantine weights and performs FedAvg on trusted subset."""
    trusted_models = []
    trusted_sizes = []
    for d in decisions_list:
        try:
            c_idx = int(d['client_id'].split('_')[1])
        except Exception:
            continue
        decision = str(d.get('decision', 'trust')).lower().strip()
        explanation = d.get('explanation', '').encode('ascii', 'replace').decode('ascii')
        print(f"    -> {d['client_id']}: {decision.upper()} | {explanation}")

        if decision == 'trust':
            trusted_models.append(client_models[c_idx])
            trusted_sizes.append(client_sizes[c_idx])
        elif decision == 'downweight':
            trusted_models.append(client_models[c_idx])
            trusted_sizes.append(client_sizes[c_idx] * 0.3)
        elif decision == 'quarantine':
            pass # completely excluded

    if len(trusted_models) > 0:
        return fedavg_aggregate(global_model, trusted_models, trusted_sizes)
    else:
        print("  [WARNING] All clients quarantined! Skipping model update this round.")
        return global_model

def evaluate_full(model, dataloader, criterion, device, label_names):
    """Computes overall accuracy/loss, confusion matrix, and per-class metrics."""
    model.eval()
    model.to(device)
    total_loss = 0.0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            total_loss += loss.item() * batch_x.size(0)
            _, predicted = torch.max(outputs, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_y.cpu().numpy())

    total = len(all_labels)
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    rec = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)

    num_classes = len(label_names)
    cm = confusion_matrix(all_labels, all_preds, labels=list(range(num_classes)))
    prec_per = precision_score(all_labels, all_preds, labels=list(range(num_classes)), average=None, zero_division=0)
    rec_per = recall_score(all_labels, all_preds, labels=list(range(num_classes)), average=None, zero_division=0)
    f1_per = f1_score(all_labels, all_preds, labels=list(range(num_classes)), average=None, zero_division=0)

    per_class = []
    for c in range(num_classes):
        per_class.append({
            'name': label_names[c],
            'precision': float(prec_per[c]),
            'recall': float(rec_per[c]),
            'f1': float(f1_per[c])
        })

    return {
        'loss': float(total_loss / total),
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1': float(f1),
        'confusion_matrix': cm.tolist(),
        'per_class': per_class
    }

def run_federated_experiment(non_iid=False, strategy_name=None, alpha=NON_IID_ALPHA, num_rounds=NUM_ROUNDS):
    set_seed(RANDOM_SEED)
    device = get_device()
    strategy = strategy_name if strategy_name is not None else config.AGG_STRATEGY
    partition_type = 'Non-IID' if non_iid else 'IID'
    poison_status = f"{config.POISON_MODE.upper()} POISON" if config.POISON_ENABLED else "CLEAN"

    print('=' * 60)
    print(f'  ByzAgent-IDS: Federated Training Experiment')
    print(f'  Partition: {partition_type} | Strategy: {strategy} | Mode: {poison_status}')
    print('=' * 60)

    print('\nLoading dataset...')
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    input_dim = X_train.shape[1]
    num_classes = len(label_names)

    print(f'\nPartitioning data across {NUM_CLIENTS} organizations ({partition_type})...')
    if non_iid:
        partitions = partition_data_non_iid(X_train, y_train, num_clients=NUM_CLIENTS, alpha=alpha)
    else:
        partitions = partition_data_iid(X_train, y_train, num_clients=NUM_CLIENTS)

    client_train_loaders = []
    for p in partitions:
        train_dataset = IDSDataset(p['X'], p['y'])
        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        client_train_loaders.append(train_loader)
    client_sizes = [len(p['y']) for p in partitions]

    # A1 Fix: Separate server validation set (10%) and final test set (90%)
    raw_test_dataset = IDSDataset(X_test, y_test)
    val_len = int(len(raw_test_dataset) * 0.10)
    test_len = len(raw_test_dataset) - val_len
    generator = torch.Generator().manual_seed(RANDOM_SEED)
    server_val_dataset, final_test_dataset = torch.utils.data.random_split(
        raw_test_dataset, [val_len, test_len], generator=generator
    )
    # Use 2048 for inference/evaluation passes for fast CPU matrix operations
    server_valloader = DataLoader(server_val_dataset, batch_size=2048, shuffle=False)
    final_testloader = DataLoader(final_test_dataset, batch_size=2048, shuffle=False)
    print(f"  Validation split: {len(server_val_dataset):,} samples (server val) | {len(final_test_dataset):,} samples (final test)")

    global_model = IDSModel(input_dim=input_dim, num_classes=num_classes)
    print('\nModel: IDSModel (MLP)')
    print('  Parameters: {:,}'.format(count_parameters(global_model)))
    print('  Rounds:     {}'.format(num_rounds))
    print('  Clients:    {}'.format(NUM_CLIENTS))
    print('  Strategy:   {}'.format(strategy))

    criterion = nn.CrossEntropyLoss()
    monitor = ByzAgentMonitor(config.RESULTS_DIR / "byzagent_history.json")
    arbiter = ByzAgentTrustArbiter() if strategy == 'byzagent' else None
    all_decisions = []

    history = {
        'round': [],
        'global_loss': [],
        'global_acc': [],
        'global_f1': [],
        'global_precision': [],
        'global_recall': [],
        'detect_tp': [],
        'detect_fp': []
    }

    attackers = set(config.ATTACKER_CLIENTS) if config.POISON_ENABLED else set()
    honest_clients = set(range(NUM_CLIENTS)) - attackers

    print('\nStarting Federated Learning...')
    print('-' * 70)
    start_time = time.time()

    for round_num in range(1, num_rounds + 1):
        client_models = []
        client_losses = []
        client_val_accs = []

        for client_id in range(NUM_CLIENTS):
            local_model = IDSModel(input_dim=input_dim, num_classes=num_classes)
            local_model.load_state_dict(copy.deepcopy(global_model.state_dict()))
            trainloader = client_train_loaders[client_id]

            # Apply Poisoning
            if config.POISON_ENABLED and client_id in config.ATTACKER_CLIENTS:
                from src.attacks.label_flip import apply_label_flip
                trainloader = apply_label_flip(
                    trainloader, 
                    round_num, 
                    mode=config.POISON_MODE, 
                    sudden_frac=config.POISON_FRACTION_SUDDEN, 
                    gradual_step=config.POISON_FRACTION_GRADUAL_STEP,
                    num_classes=num_classes
                )

            optimizer = torch.optim.Adam(local_model.parameters(), lr=config.LEARNING_RATE)
            final_loss = 0.0
            for epoch in range(config.LOCAL_EPOCHS):
                if strategy == 'fedprox':
                    res = train_local_fedprox(local_model, global_model, trainloader, optimizer, criterion, device, mu=config.FEDPROX_MU)
                    final_loss = res['loss'] if isinstance(res, dict) else res
                else:
                    res = train_one_epoch(local_model, trainloader, optimizer, criterion, device)
                    final_loss = res['loss'] if isinstance(res, dict) else res

            client_models.append(local_model)
            client_losses.append(final_loss)

            # Validation accuracy on clean server validation split (NOT test set)
            val_res = evaluate(local_model, server_valloader, criterion, device)
            client_val_accs.append(val_res['accuracy'])

        # Compute Behavioral Stats per client
        round_stats = monitor.compute_round_stats(
            round_num=round_num,
            global_model=global_model,
            client_models=client_models,
            local_losses=client_losses,
            val_accuracies=client_val_accs
        )

        print(f"  [Round {round_num}] Client Stats:")
        for cid, stats in round_stats.items():
            print(f"    {cid}: norm={stats['update_norm']:.4f}, cos_peer={stats['cos_sim_peer_mean']:.4f}, loss={stats['local_loss']:.4f}, val_acc={stats['val_accuracy']:.4f}")

        # Aggregation Logic
        current_decisions = []
        if strategy == 'byzagent':
            decisions_json = arbiter.evaluate_clients(round_num, round_stats, history=monitor.history)
            decisions_json['round'] = round_num
            all_decisions.append(decisions_json)
            with open(config.RESULTS_DIR / 'byzagent_decisions.json', 'w') as df:
                json.dump(all_decisions, df, indent=2)
            current_decisions = decisions_json.get('decisions', [])
            global_model = aggregate_with_decisions(global_model, client_models, client_sizes, current_decisions)

        elif strategy == 'rule':
            decisions_json = evaluate_rule_baseline(round_stats)
            decisions_json['round'] = round_num
            all_decisions.append(decisions_json)
            with open(config.RESULTS_DIR / 'rule_decisions.json', 'w') as df:
                json.dump(all_decisions, df, indent=2)
            current_decisions = decisions_json.get('decisions', [])
            global_model = aggregate_with_decisions(global_model, client_models, client_sizes, current_decisions)

        elif strategy == 'krum':
            global_model, best_idx = krum_aggregate(global_model, client_models, f=len(config.ATTACKER_CLIENTS) if config.POISON_ENABLED else 1)
            print(f"  [Aggregation] Krum selected client_{best_idx}")

        elif strategy == 'trimmed_mean':
            global_model = trimmed_mean_aggregate(global_model, client_models, trim_count=1)
            print("  [Aggregation] Trimmed-Mean applied")

        else: # fedavg / default
            global_model = fedavg_aggregate(global_model, client_models, client_sizes)

        # Detection metrics calculation for byzagent / rule
        if strategy in ['byzagent', 'rule'] and len(current_decisions) > 0:
            tp = 0
            fp = 0
            for d in current_decisions:
                try:
                    c_idx = int(d['client_id'].split('_')[1])
                except Exception:
                    continue
                dec = str(d.get('decision', 'trust')).lower().strip()
                if dec in ['quarantine', 'downweight']:
                    if c_idx in attackers:
                        tp += 1
                    elif c_idx in honest_clients:
                        fp += 1
            history['detect_tp'].append(tp)
            history['detect_fp'].append(fp)
        else:
            history['detect_tp'].append(0)
            history['detect_fp'].append(0)

        # Round evaluation on clean test set
        test_result = evaluate(global_model, final_testloader, criterion, device)
        history['round'].append(round_num)
        history['global_loss'].append(test_result['loss'])
        history['global_acc'].append(test_result['accuracy'])
        history['global_f1'].append(test_result['f1'])
        history['global_precision'].append(test_result['precision'])
        history['global_recall'].append(test_result['recall'])
        print('  Round {:2d}/{} | Loss: {:.4f} | Acc: {:.4f} | F1: {:.4f}'.format(
            round_num, num_rounds, test_result['loss'], test_result['accuracy'], test_result['f1']))

    elapsed = time.time() - start_time
    final_result = evaluate_full(global_model, final_testloader, criterion, device, label_names)
    print_metrics(final_result, f'Federated {partition_type} {strategy} -- Final Results')
    print('  Training time: {:.1f}s'.format(elapsed))

    results = {
        'experiment': f'federated_{partition_type.lower()}_{strategy}',
        'partition_type': partition_type,
        'strategy': strategy,
        'num_rounds': num_rounds,
        'num_clients': NUM_CLIENTS,
        'non_iid_alpha': alpha if non_iid else 'N/A',
        'training_time_seconds': elapsed,
        'final_accuracy': final_result['accuracy'],
        'final_f1': final_result['f1'],
        'final_precision': final_result['precision'],
        'final_recall': final_result['recall'],
        'final_loss': final_result['loss'],
        'confusion_matrix': final_result['confusion_matrix'],
        'per_class': final_result['per_class'],
        'total_tp': int(sum(history['detect_tp'])),
        'total_fp': int(sum(history['detect_fp'])),
        'history': history,
        'label_names': label_names,
    }

    # Consistent file naming
    poison_tag = '_clean' if not config.POISON_ENABLED else f'_{config.POISON_MODE}'
    result_filename = f'federated_{partition_type.lower()}_{strategy}{poison_tag}.json'
    save_results(results, RESULTS_DIR / result_filename)

    model_filename = f'federated_{partition_type.lower()}_{strategy}{poison_tag}.pt'
    save_model(global_model, MODEL_DIR / model_filename)

    print(f'\n[OK] Federated experiment complete! Saved {result_filename}')
    print('   Accuracy: {:.2f}%'.format(final_result['accuracy']*100))
    print('   F1 Score: {:.4f}'.format(final_result['f1']))
    return global_model, final_result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ByzAgent-IDS Federated Training')
    parser.add_argument('--non-iid', action='store_true', help='Use non-IID partitioning')
    parser.add_argument('--strategy', choices=['fedavg', 'krum', 'trimmed_mean', 'rule', 'byzagent'], default=None)
    parser.add_argument('--alpha', type=float, default=NON_IID_ALPHA)
    parser.add_argument('--rounds', type=int, default=NUM_ROUNDS)
    args = parser.parse_args()
    strat = args.strategy if args.strategy is not None else config.AGG_STRATEGY
    run_federated_experiment(non_iid=args.non_iid, strategy_name=strat, alpha=args.alpha, num_rounds=args.rounds)
