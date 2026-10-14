"""Script to export real experimental results and evaluation metrics into dashboard/public/data/ for Vercel/static deployment"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import torch
import numpy as np
import config
from src.model import IDSModel
from src.dataset import load_cicids2017, IDSDataset
from torch.utils.data import DataLoader

def export_data():
    results_dir = config.RESULTS_DIR
    models_dir = config.MODEL_DIR
    out_dir = config.BASE_DIR / 'dashboard' / 'public' / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting frontend data to: {out_dir}")

    # 1. comparison.json
    strategy_files = {
        "fedavg_clean": results_dir / "federated_iid_fedavg_clean.json",
        "fedavg_gradual": results_dir / "federated_iid_fedavg_gradual.json",
        "krum_gradual": results_dir / "federated_iid_krum_gradual.json",
        "trimmed_mean_gradual": results_dir / "federated_iid_trimmed_mean_gradual.json",
        "rule_gradual": results_dir / "federated_iid_rule_gradual.json",
        "byzagent_gradual": results_dir / "federated_iid_byzagent_gradual.json",
    }

    comparison = {}
    for strat_key, filepath in strategy_files.items():
        if filepath.exists():
            with open(filepath, 'r') as f:
                d = json.load(f)
            comparison[strat_key] = {
                "name": strat_key,
                "final_acc": float(d.get("final_accuracy", 0.0)),
                "final_f1": float(d.get("final_f1", 0.0)),
                "final_loss": float(d.get("final_loss", 0.0)),
                "total_tp": int(d.get("total_tp", 0)),
                "total_fp": int(d.get("total_fp", 0)),
                "acc_history": [float(x) for x in d.get("history", {}).get("global_acc", [])],
                "loss_history": [float(x) for x in d.get("history", {}).get("global_loss", [])],
                "round_history": d.get("history", {}).get("round", list(range(1, 11)))
            }
        else:
            print(f"  [WARN] {filepath.name} does not exist yet.")

    with open(out_dir / "comparison.json", 'w') as f:
        json.dump(comparison, f, indent=2)
    print("  -> Saved comparison.json")

    # 2. analytics.json (from ByzAgent run)
    byz_file = results_dir / "federated_iid_byzagent_gradual.json"
    if byz_file.exists():
        with open(byz_file, 'r') as f:
            byz_data = json.load(f)
        analytics = {
            "confusion_matrix": byz_data.get("confusion_matrix", []),
            "class_names": byz_data.get("label_names", config.ATTACK_CLASSES),
            "per_class_metrics": byz_data.get("per_class", []),
            "overall_accuracy": byz_data.get("final_accuracy", 0.0),
            "overall_f1": byz_data.get("final_f1", 0.0)
        }
        with open(out_dir / "analytics.json", 'w') as f:
            json.dump(analytics, f, indent=2)
        print("  -> Saved analytics.json")

    # 3. decisions.json
    dec_file = results_dir / "byzagent_decisions.json"
    if dec_file.exists():
        with open(dec_file, 'r') as f:
            decisions = json.load(f)
        with open(out_dir / "decisions.json", 'w') as f:
            json.dump(decisions, f, indent=2)
        print("  -> Saved decisions.json")

    # 4. history.json
    hist_file = results_dir / "byzagent_history.json"
    if hist_file.exists():
        with open(hist_file, 'r') as f:
            history = json.load(f)
        with open(out_dir / "history.json", 'w') as f:
            json.dump(history, f, indent=2)
        print("  -> Saved history.json")

    # 5. alerts.json (50 real sampled test rows evaluated using the ByzAgent model)
    byz_model_path = models_dir / "federated_iid_byzagent_gradual.pt"
    if byz_model_path.exists():
        print("  Evaluating test samples using saved ByzAgent model for alerts.json...")
        X_train, X_test, y_train, y_test, _, label_names = load_cicids2017()
        model = IDSModel(input_dim=X_train.shape[1], num_classes=len(label_names))
        model.load_state_dict(torch.load(byz_model_path, map_location='cpu'))
        model.eval()

        np.random.seed(config.RANDOM_SEED)
        
        # Sample uniformly across attack classes to get balanced variety for the demo
        indices = []
        for c in range(len(label_names)):
            c_idx = np.where(y_test == c)[0]
            if len(c_idx) > 0:
                count = 6 if c == 0 else 7 # 6 benign, 7 for each attack
                chosen = np.random.choice(c_idx, size=min(len(c_idx), count), replace=False)
                indices.extend(chosen)
        np.random.shuffle(indices)
        indices = indices[:50]

        X_sample = torch.tensor(X_test[indices], dtype=torch.float32)
        y_sample = y_test[indices]

        nodes = ['Hospital-Node-1', 'Bank-Node-2', 'Uni-Node-3']
        alerts = []

        with torch.no_grad():
            outputs = model(X_sample)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1).numpy()
            confs = torch.max(probs, dim=1).values.numpy()

        for idx, (true_c, pred_c, conf) in enumerate(zip(y_sample, preds, confs)):
            type_name = label_names[pred_c]
            status = 'normal' if type_name == 'BENIGN' else ('critical' if conf > 0.90 else 'warning')
            alerts.append({
                "id": f"AL-{1040 + idx}",
                "type": type_name,
                "true_label": label_names[true_c],
                "confidence": round(float(conf * 100), 1),
                "sourceIp": f"192.168.{np.random.randint(1, 10)}.{np.random.randint(10, 250)}",
                "node": nodes[idx % len(nodes)],
                "status": status
            })

        with open(out_dir / "alerts.json", 'w') as f:
            json.dump(alerts, f, indent=2)
        print("  -> Saved alerts.json (50 real test evaluations)")

if __name__ == '__main__':
    export_data()
