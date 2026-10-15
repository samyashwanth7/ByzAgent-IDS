"""Generate professional architecture and mechanism diagrams as high-resolution PNGs for the README."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

out_dir = Path(__file__).parent.parent / 'docs' / 'images'
out_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Architecture Flowchart Diagram (docs/images/architecture_diagram.png)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 7.5), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 8.5)
ax.axis('off')

# Background canvas
fig.patch.set_facecolor('#0f172a') # Slate 900 dark theme
ax.set_facecolor('#0f172a')

# Helper function to draw rounded boxes
def draw_card(ax, x, y, w, h, bg_color, border_color, title, subtitle=None, title_color="#ffffff", corner_radius=0.15):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.1,rounding_size={corner_radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.8
    )
    ax.add_patch(rect)
    if title:
        ax.text(x + w/2, y + h - 0.45, title, color=title_color, fontsize=11, fontweight='bold', ha='center', va='center')
    if subtitle:
        ax.text(x + w/2, y + h/2 - 0.25, subtitle, color="#94a3b8", fontsize=8.5, ha='center', va='center', multialignment='center')

# Title Header
ax.text(8.0, 8.0, "ByzAgent-IDS: End-to-End System Architecture", color="#f8fafc", fontsize=16, fontweight='bold', ha='center')
ax.text(8.0, 7.6, "Decentralized Federated Fleet  ->  Server Telemetry Extraction  ->  LLM Security Arbiter  ->  Adaptive Aggregation", color="#38bdf8", fontsize=9.5, ha='center')

# Column 1: Fleet
draw_card(ax, 0.5, 4.8, 3.2, 2.2, "#1e293b", "#10b981", "Client 0 (Honest)", "• Clean CICIDS Traffic\n• Low Loss (~0.025)\n• High Val Acc (~99%)", title_color="#10b981")
draw_card(ax, 0.5, 2.5, 3.2, 2.0, "#1e293b", "#ef4444", "Client 1 (Attacker)", "• Label-Flipping Attack\n• Rising Loss (0.5->1.8)\n• Val Acc Drops to 0%", title_color="#ef4444")
draw_card(ax, 0.5, 0.3, 3.2, 2.0, "#1e293b", "#ef4444", "Client 2 (Sybil Attacker)", "• Colluding Label-Flipper\n• Mimics Client 1 Objective\n• High Cosine Similarity", title_color="#ef4444")

# Column 2: Telemetry Engine
draw_card(ax, 4.3, 0.6, 3.6, 6.4, "#1e293b", "#3b82f6", "Server Telemetry Engine", 
          "Multi-Metric Profiler\n(src/monitoring/client_stats.py)\n\n"
          "1. Held-out Val Accuracy (10%)\n   Clean server-side split (no leakage)\n\n"
          "2. Local Training Loss Slope\n   Tracks label disruption\n\n"
          "3. Peer Cosine Similarity\n   Alignment vs fleet consensus\n\n"
          "4. Weight Update L2 Norm\n   Detects abnormal gradient scale\n\n"
          "5. 3-Round Rolling Trajectory\n   Slices recent history trend", 
          title_color="#60a5fa")

# Column 3: LLM Arbiter
draw_card(ax, 8.5, 0.6, 3.8, 6.4, "#1e293b", "#a855f7", "ByzAgent LLM Arbiter",
          "AI Security Reasoner\n(src/agents/byz_agent.py)\n\n"
          "Powered by Cloud Groq LPU\n(LangChain + Zero Local GPU Load)\n\n"
          "Temporal Analysis Prompt:\n'Evaluate metric slopes across 3 rounds.'\n\n"
          "Deterministic JSON Schema:\n"
          "• Client 0 -> TRUST (1.0x)\n"
          "  Low loss, stable val accuracy\n\n"
          "• Client 1 -> QUARANTINE (0.0x)\n"
          "  Loss exploding, val accuracy near 0\n\n"
          "• Client 2 -> QUARANTINE (0.0x)\n"
          "  Coordinated attack detected",
          title_color="#c084fc")

# Column 4: Aggregation & Model
draw_card(ax, 12.8, 4.1, 2.8, 2.9, "#1e293b", "#10b981", "Adaptive FedAvg",
          "Weighted Aggregation\n\n"
          "• Trust: 1.0x Weight\n"
          "• Downweight: 0.3x\n"
          "• Quarantine: 0.0x\n(Completely Excluded)",
          title_color="#34d399")

draw_card(ax, 12.8, 0.6, 2.8, 2.9, "#1e293b", "#38bdf8", "Global IDS Model",
          "Protected Classifier\n(8 Multi-Class Attacks)\n\n"
          "Final Benchmark Result:\n"
          "• Accuracy: 99.04%\n"
          "• Macro-F1: 0.9897\n"
          "• Attackers Stopped: 100%",
          title_color="#38bdf8")

# Arrows
arrow_style = dict(arrowstyle="->", color="#38bdf8", lw=2, mutation_scale=15)
ax.annotate("", xy=(4.3, 5.8), xytext=(3.7, 5.8), arrowprops=arrow_style)
ax.annotate("", xy=(4.3, 3.5), xytext=(3.7, 3.5), arrowprops=arrow_style)
ax.annotate("", xy=(4.3, 1.3), xytext=(3.7, 1.3), arrowprops=arrow_style)

# Telemetry -> LLM
ax.annotate("", xy=(8.5, 3.8), xytext=(7.9, 3.8), arrowprops=dict(arrowstyle="->", color="#c084fc", lw=2.5, mutation_scale=18))

# LLM -> Aggregator
ax.annotate("", xy=(12.8, 5.5), xytext=(12.3, 5.5), arrowprops=dict(arrowstyle="->", color="#34d399", lw=2.5, mutation_scale=18))

# Aggregator -> Global Model
ax.annotate("", xy=(14.2, 3.5), xytext=(14.2, 4.1), arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2.5, mutation_scale=18))

# Global Model feedback loop
ax.annotate("Broadcast to Clients", xy=(2.0, 0.1), xytext=(12.8, 0.2), 
            arrowprops=dict(arrowstyle="->", color="#64748b", lw=1.5, linestyle="--", connectionstyle="arc3,rad=0.15"),
            color="#94a3b8", fontsize=8.5, ha='center')

plt.tight_layout()
fig1_path = out_dir / 'architecture_diagram.png'
plt.savefig(fig1_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print(f"Generated {fig1_path}")


# -----------------------------------------------------------------------------
# 2. Sybil Collapse vs ByzAgent Diagram (docs/images/krum_sybil_collapse.png)
# -----------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=300)
fig.patch.set_facecolor('#0f172a')

for ax in (ax1, ax2):
    ax.set_facecolor('#1e293b')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

# Left Panel: Krum Failure
rect1 = patches.FancyBboxPatch((0.2, 0.2), 9.6, 8.1, boxstyle="round,pad=0.1,rounding_size=0.15", facecolor="#1e293b", edgecolor="#ef4444", linewidth=2)
ax1.add_patch(rect1)
ax1.text(5.0, 7.8, "Classical Defense: Krum Failure", color="#ef4444", fontsize=13, fontweight='bold', ha='center')
ax1.text(5.0, 7.3, "Sybil Majority Trap: Distance = Honesty Assumption Breaks", color="#94a3b8", fontsize=9, ha='center')

# Points representation
ax1.scatter([7.0, 7.8], [4.5, 4.0], color="#ef4444", s=350, zorder=5)
ax1.text(7.0, 5.0, "Attacker 1", color="#fca5a5", fontsize=9.5, fontweight='bold', ha='center')
ax1.text(7.8, 3.4, "Attacker 2", color="#fca5a5", fontsize=9.5, fontweight='bold', ha='center')

# Line between attackers (tight cluster)
ax1.plot([7.0, 7.8], [4.5, 4.0], color="#ef4444", lw=2.5, ls="--")
ax1.text(7.5, 4.5, "d12 = 0.08\n(Very Small!)", color="#f87171", fontsize=8.5, ha='center')

# Honest Client
ax1.scatter([2.5], [4.2], color="#10b981", s=350, zorder=5)
ax1.text(2.5, 4.8, "Client 0 (Honest)", color="#6ee7b7", fontsize=9.5, fontweight='bold', ha='center')

# Large distance to honest
ax1.plot([2.5, 7.0], [4.2, 4.5], color="#f59e0b", lw=2, ls=":")
ax1.text(4.7, 4.6, "d01 = 0.85 (Large)", color="#f59e0b", fontsize=8.5, ha='center')

# Explanatory card below
ax1.text(5.0, 2.0, "Krum selects the node with smallest sum of neighbor distances:\n\n"
                    "• Attacker 1 distance sum = 0.08  ->  KRUM PICKS ATTACKER!\n"
                    "• Honest Client 0 distance sum = 0.85  ->  REJECTED AS OUTLIER!\n\n"
                    "Outcome: Global Model Poisoned -> Accuracy Collapses to 1.77%", 
         color="#fca5a5", fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.5", facecolor="#2d1215", edgecolor="#ef4444", lw=1))


# Right Panel: ByzAgent Solution
rect2 = patches.FancyBboxPatch((0.2, 0.2), 9.6, 8.1, boxstyle="round,pad=0.1,rounding_size=0.15", facecolor="#1e293b", edgecolor="#10b981", linewidth=2)
ax2.add_patch(rect2)
ax2.text(5.0, 7.8, "ByzAgent Defense: Behavioral Reasoning", color="#10b981", fontsize=13, fontweight='bold', ha='center')
ax2.text(5.0, 7.3, "Temporal Telemetry Evaluation (Loss + Held-out Val Accuracy)", color="#94a3b8", fontsize=9, ha='center')

# Diagram
draw_card(ax2, 0.8, 3.8, 3.8, 2.8, "#0f172a", "#10b981", "Client 0 (Honest)", 
          "• Held-out Val Acc: 99.2%\n• Local Loss: 0.025 (Low)\n• Status: Clean Trajectory\n\nDecision: TRUST (1.0x)", title_color="#10b981")

draw_card(ax2, 5.4, 3.8, 3.8, 2.8, "#0f172a", "#ef4444", "Attackers 1 & 2", 
          "• Held-out Val Acc: 0.0% (Crashed)\n• Local Loss: 1.85 (Exploding)\n• Status: Colluding Flipped Labels\n\nDecision: QUARANTINE (0.0x)", title_color="#ef4444")

# Explanatory card below
ax2.text(5.0, 2.0, "ByzAgent inspects functional telemetry across 3 rolling rounds:\n\n"
                    "• Detects label corruption even when attackers outnumber honest nodes.\n"
                    "• Quarantines Attacker 1 & 2 updates regardless of distance clusters.\n\n"
                    "Outcome: Attackers Neutralized -> Accuracy Maintained at 99.04%", 
         color="#a7f3d0", fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.5", facecolor="#064e3b", edgecolor="#10b981", lw=1))

plt.tight_layout()
fig2_path = out_dir / 'krum_sybil_collapse.png'
plt.savefig(fig2_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print(f"Generated {fig2_path}")
