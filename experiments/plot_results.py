import json
import matplotlib.pyplot as plt
from pathlib import Path

results_dir = Path('../results')

def load_json(name):
    with open(results_dir / name, 'r') as f:
        return json.load(f)

# Load data
cent = load_json('centralized_baseline.json')
fed_iid = load_json('federated_iid_fedavg.json')
fed_noniid_avg = load_json('federated_non-iid_fedavg.json')
fed_noniid_prox = load_json('federated_non-iid_fedprox.json')

plt.figure(figsize=(10, 6))

# Centralized is over 20 epochs, Federated over 10 rounds.
# We can just plot them side by side based on their respective 'step' (epoch or round).
plt.plot(cent['history']['epoch'], cent['history']['test_acc'], label='Centralized (Epochs)', marker='o')
plt.plot(fed_iid['history']['round'], fed_iid['history']['global_acc'], label='Fed IID FedAvg (Rounds)', marker='s')
plt.plot(fed_noniid_avg['history']['round'], fed_noniid_avg['history']['global_acc'], label='Fed Non-IID FedAvg (Rounds)', marker='^')
plt.plot(fed_noniid_prox['history']['round'], fed_noniid_prox['history']['global_acc'], label='Fed Non-IID FedProx (Rounds)', marker='d')

plt.title('Validation Accuracy over Time')
plt.xlabel('Training Epoch / FL Round')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(results_dir / 'training_curves.png', dpi=150)
print('Saved training_curves.png')

# Accuracy Comparison Bar Chart
local = load_json('local_only.json')
labels = ['Centralized', 'Fed IID', 'Fed Non-IID (Avg)', 'Fed Non-IID (Prox)', 'Local Only (Avg)']
accuracies = [
    cent['final_accuracy'],
    fed_iid['final_accuracy'],
    fed_noniid_avg['final_accuracy'],
    fed_noniid_prox['final_accuracy'],
    local['avg_accuracy']
]

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, accuracies, color=['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974'])
plt.ylim(0.9, 1.0) # Zoom in to see differences
plt.title('Final Accuracy Comparison')
plt.ylabel('Accuracy')
plt.xticks(rotation=15)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.4f}', va='bottom', ha='center')
plt.tight_layout()
plt.savefig(results_dir / 'accuracy_comparison.png', dpi=150)
print('Saved accuracy_comparison.png')
