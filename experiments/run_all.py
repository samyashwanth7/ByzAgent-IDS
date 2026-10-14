"""Automated runner for the full ByzAgent benchmark experiment suite.
Runs all remaining poisoned experiments in sequence:
  1. fedavg (gradual)
  2. krum (gradual)
  3. trimmed_mean (gradual)
  4. rule (gradual)
  5. byzagent (gradual)

After completion:
  - Exports data for the frontend
  - Prints the complete final metrics table
  - Restores config.py defaults
"""
import sys
import time
import json
from pathlib import Path

# Ensure repo root is on path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import config
from experiments.run_federated import run_federated_experiment
from scripts.export_frontend_data import export_data

STRATEGIES = [
    'fedavg',
    'krum',
    'trimmed_mean',
    'rule',
    'byzagent'
]

def main():
    print("=" * 80)
    print("  ByzAgent-IDS Benchmark Suite Execution")
    print("  Setup: 3 Clients, 2 Attackers ([1, 2]), Gradual Poisoning, 10 Rounds")
    print("=" * 80)

    # Verify poison settings in config
    assert config.POISON_ENABLED == True, "POISON_ENABLED must be True for benchmark runs"
    assert config.ATTACKER_CLIENTS == [1, 2], "ATTACKER_CLIENTS must be [1, 2]"
    assert config.POISON_MODE == 'gradual', "POISON_MODE must be 'gradual'"

    suite_start = time.time()
    completed = []

    for idx, strat in enumerate(STRATEGIES, 1):
        target_file = config.RESULTS_DIR / f"federated_iid_{strat}_gradual.json"
        if target_file.exists():
            print(f"\n[{idx}/{len(STRATEGIES)}] Strategy {strat.upper()} already completed ({target_file.name}). Skipping.")
            completed.append(strat)
            continue

        print(f"\n[{idx}/{len(STRATEGIES)}] Running strategy: {strat.upper()} ...")
        t0 = time.time()
        
        try:
            model, res = run_federated_experiment(
                non_iid=False,
                strategy_name=strat,
                num_rounds=config.NUM_ROUNDS
            )
            elapsed = time.time() - t0
            print(f"  [DONE] {strat.upper()} finished in {elapsed/60:.1f} min | Acc: {res['accuracy']*100:.2f}% | F1: {res['f1']:.4f}")
            completed.append(strat)
        except Exception as e:
            print(f"  [ERROR] Strategy {strat} failed with error: {e}")
            import traceback
            traceback.print_exc()
            # If an error happens, continue to next if possible or pause
            break

    print("\n" + "=" * 80)
    print("  All scheduled benchmark experiments finished!")
    print(f"  Total suite time: {(time.time() - suite_start)/60:.1f} minutes")
    print("=" * 80)

    # Export frontend data
    print("\nExporting results to frontend public/data/ ...")
    export_data()

    # Print Final Summary Table
    print("\n" + "=" * 80)
    print("  FINAL BENCHMARK COMPARISON TABLE")
    print("=" * 80)
    header = f"{'Strategy':<20} | {'Final Acc (%)':<15} | {'Final F1':<12} | {'Total TP':<10} | {'Total FP':<10}"
    print(header)
    print("-" * len(header))

    # All files to report (including clean reference)
    all_runs = [
        ("Clean FedAvg (ref)", config.RESULTS_DIR / "federated_iid_fedavg_clean.json"),
        ("Poisoned FedAvg", config.RESULTS_DIR / "federated_iid_fedavg_gradual.json"),
        ("Poisoned Krum", config.RESULTS_DIR / "federated_iid_krum_gradual.json"),
        ("Poisoned Trimmed-Mean", config.RESULTS_DIR / "federated_iid_trimmed_mean_gradual.json"),
        ("Poisoned Rule Baseline", config.RESULTS_DIR / "federated_iid_rule_gradual.json"),
        ("Poisoned ByzAgent (Ours)", config.RESULTS_DIR / "federated_iid_byzagent_gradual.json"),
    ]

    for label, filepath in all_runs:
        if filepath.exists():
            with open(filepath, 'r') as f:
                d = json.load(f)
            acc = d.get('final_accuracy', 0.0) * 100
            f1 = d.get('final_f1', 0.0)
            tp = d.get('total_tp', 'N/A')
            fp = d.get('total_fp', 'N/A')
            print(f"{label:<20} | {acc:>14.2f}% | {f1:>12.4f} | {str(tp):>10} | {str(fp):>10}")
        else:
            print(f"{label:<20} | {'MISSING':>15} | {'N/A':>12} | {'N/A':>10} | {'N/A':>10}")

    print("=" * 80)

if __name__ == '__main__':
    main()
