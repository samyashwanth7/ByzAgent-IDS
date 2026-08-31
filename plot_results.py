import json
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path('results')

def load_history(strategy):
    file_path = RESULTS_DIR / f'federated_iid_{strategy}.json'
    if not file_path.exists():
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['history']

strategies = {
    'fedavg': 'FedAvg (No Defense)',
    'krum': 'Krum',
    'byzagent': 'ByzAgent (LLM Arbiter)'
}

histories = {}
for s in strategies.keys():
    hist = load_history(s)
    if hist:
        histories[s] = hist

if not histories:
    print(\"No results found to plot!\")
    exit()

# Plot Accuracy
plt.figure(figsize=(10, 6))
for s, label in strategies.items():
    if s in histories:
        plt.plot(histories[s]['round'], histories[s]['global_acc'], marker='o', label=label, linewidth=2)

plt.title('Global Model Accuracy vs Communication Round (2 Attackers)', fontsize=14)
plt.xlabel('Round', fontsize=12)
plt.ylabel('Accuracy', fontsize=12)
plt.ylim(0.7, 1.0)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig('accuracy_comparison.png', dpi=300)
print(\"Saved accuracy_comparison.png\")

# Plot Loss
plt.figure(figsize=(10, 6))
for s, label in strategies.items():
    if s in histories:
        plt.plot(histories[s]['round'], histories[s]['global_loss'], marker='x', label=label, linewidth=2)

plt.title('Global Model Loss vs Communication Round (2 Attackers)', fontsize=14)
plt.xlabel('Round', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig('loss_comparison.png', dpi=300)
print(\"Saved loss_comparison.png\")
