"""Generate high-resolution visual demonstration figures for the README from real experimental results."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

repo_root = Path(__file__).parent.parent
results_dir = repo_root / 'results'
out_dir = repo_root / 'docs' / 'images'
out_dir.mkdir(parents=True, exist_ok=True)

# Set clean aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Load comparison data
with open(repo_root / 'dashboard' / 'public' / 'data' / 'comparison.json', 'r') as f:
    comp = json.load(f)

# 1. Figure 1: Benchmark Comparison (Accuracy & Loss)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
rounds = list(range(1, 11))

styles = {
    'byzagent_gradual': {'label': 'ByzAgent (Ours)', 'color': '#10b981', 'lw': 3.0, 'ls': '-', 'marker': 'o'},
    'rule_gradual': {'label': 'Rule Baseline', 'color': '#0284c7', 'lw': 2.0, 'ls': '--', 'marker': 's'},
    'fedavg_clean': {'label': 'FedAvg (Clean Ref)', 'color': '#64748b', 'lw': 2.0, 'ls': ':', 'marker': '^'},
    'krum_gradual': {'label': 'Krum (Poisoned)', 'color': '#f59e0b', 'lw': 2.0, 'ls': '-.', 'marker': 'x'},
    'trimmed_mean_gradual': {'label': 'Trimmed-Mean (Poisoned)', 'color': '#8b5cf6', 'lw': 1.8, 'ls': '-.', 'marker': '+'},
    'fedavg_gradual': {'label': 'FedAvg (Poisoned)', 'color': '#ef4444', 'lw': 2.2, 'ls': '-', 'marker': 'v'},
}

for key, style in styles.items():
    if key in comp:
        acc = [v * 100 for v in comp[key]['acc_history']]
        loss = comp[key]['loss_history']
        ax1.plot(rounds, acc, label=style['label'], color=style['color'], linewidth=style['lw'], linestyle=style['ls'], marker=style['marker'], markersize=6)
        ax2.plot(rounds, loss, label=style['label'], color=style['color'], linewidth=style['lw'], linestyle=style['ls'], marker=style['marker'], markersize=6)

ax1.set_title('Global Test Accuracy Across 10 Rounds', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Federated Round', fontsize=11, labelpad=8)
ax1.set_ylabel('Accuracy (%)', fontsize=11, labelpad=8)
ax1.set_xticks(rounds)
ax1.set_ylim(-2, 105)
ax1.legend(loc='lower left', frameon=True, framealpha=0.9, fontsize=9.5)

ax2.set_title('Global Test Loss Across 10 Rounds', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Federated Round', fontsize=11, labelpad=8)
ax2.set_ylabel('Cross-Entropy Loss', fontsize=11, labelpad=8)
ax2.set_xticks(rounds)
ax2.legend(loc='upper left', frameon=True, framealpha=0.9, fontsize=9.5)

plt.tight_layout()
fig1_path = out_dir / 'benchmark_comparison.png'
plt.savefig(fig1_path, bbox_inches='tight')
plt.close()
print(f"Generated {fig1_path}")

# 2. Figure 2: Client Behavioral Telemetry (Why LLM Can Differentiate)
with open(repo_root / 'dashboard' / 'public' / 'data' / 'history.json', 'r') as f:
    hist = json.load(f)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), dpi=300)

c_styles = {
    'client_0': {'label': 'Client 0 (Honest)', 'color': '#10b981', 'lw': 2.5, 'marker': 'o'},
    'client_1': {'label': 'Client 1 (Attacker)', 'color': '#ef4444', 'lw': 2.2, 'marker': 's'},
    'client_2': {'label': 'Client 2 (Attacker)', 'color': '#dc2626', 'lw': 2.2, 'marker': '^', 'ls': '--'},
}

for cid, style in c_styles.items():
    if cid in hist:
        r_nums = [entry['round'] for entry in hist[cid]]
        val_accs = [entry['val_accuracy'] * 100 for entry in hist[cid]]
        losses = [entry['local_loss'] for entry in hist[cid]]
        
        ax1.plot(r_nums, val_accs, label=style['label'], color=style['color'], linewidth=style['lw'], marker=style['marker'], linestyle=style.get('ls', '-'), markersize=6)
        ax2.plot(r_nums, losses, label=style['label'], color=style['color'], linewidth=style['lw'], marker=style['marker'], linestyle=style.get('ls', '-'), markersize=6)

ax1.set_title('Client Validation Accuracy (Clean Server Split)', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Federated Round', fontsize=11, labelpad=8)
ax1.set_ylabel('Validation Accuracy (%)', fontsize=11, labelpad=8)
ax1.set_xticks(rounds)
ax1.set_ylim(-5, 105)
ax1.legend(loc='lower left', frameon=True, framealpha=0.9, fontsize=10)

ax2.set_title('Client Local Training Loss (Label Noise Impact)', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Federated Round', fontsize=11, labelpad=8)
ax2.set_ylabel('Local Loss', fontsize=11, labelpad=8)
ax2.set_xticks(rounds)
ax2.legend(loc='upper left', frameon=True, framealpha=0.9, fontsize=10)

plt.tight_layout()
fig2_path = out_dir / 'client_telemetry_curves.png'
plt.savefig(fig2_path, bbox_inches='tight')
plt.close()
print(f"Generated {fig2_path}")

# 3. Figure 3: ByzAgent Confusion Matrix Heatmap
with open(repo_root / 'dashboard' / 'public' / 'data' / 'analytics.json', 'r') as f:
    analytics = json.load(f)

cm = np.array(analytics['confusion_matrix'])
class_names = analytics['class_names']

# Normalize by row (recall per class)
cm_norm = cm.astype('float') / (cm.sum(axis=1)[:, np.newaxis] + 1e-9)

plt.figure(figsize=(9, 7.5), dpi=300)
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', xticklabels=class_names, yticklabels=class_names, cbar_kws={'label': 'Recall rate'})
plt.title('ByzAgent Multi-Class Test Confusion Matrix (Normalized)', fontsize=13, fontweight='bold', pad=14)
plt.xlabel('Predicted Class', fontsize=11, labelpad=8)
plt.ylabel('Ground Truth Class', fontsize=11, labelpad=8)
plt.xticks(rotation=45, ha='right', fontsize=9.5)
plt.yticks(rotation=0, fontsize=9.5)

plt.tight_layout()
fig3_path = out_dir / 'confusion_matrix.png'
plt.savefig(fig3_path, bbox_inches='tight')
plt.close()
print(f"Generated {fig3_path}")
