"""Generate all 4 paper figures from batch log data."""

import json
import re
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(SCRIPT_DIR, "figures")
LOGS_DIR = os.path.join(PROJECT_DIR, "data", "logs")
os.makedirs(FIGURES_DIR, exist_ok=True)

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.transparent": False,
    "savefig.bbox": "tight",
})

COLORS = {
    "a": "#4C72B0",   # blue - Raw
    "b": "#DD8452",   # orange - Markdown
    "delta_pos": "#55A868",
    "delta_neg": "#C44E52",
}

# ============================================================
# Figure 1 - Score per modello (barre affiancate A/B)
# ============================================================

def figure1_scores():
    models = ["Gemma 3 4B\n(4B)", "Nemotron 3\n(~3B)", "DeepSeek V4\nFlash", "Gemma 4 26B\n(26B)"]
    scores_a = [2.29, 2.46, 2.98, 3.12]
    scores_b = [1.99, 2.28, 2.76, 2.86]
    
    x = np.arange(len(models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    bars_a = ax.bar(x - width/2, scores_a, width, label="Pipeline A (Raw)",
                    color=COLORS["a"], edgecolor="white", linewidth=0.5)
    bars_b = ax.bar(x + width/2, scores_b, width, label="Pipeline B (Markdown)",
                    color=COLORS["b"], edgecolor="white", linewidth=0.5)
    
    # Add delta labels
    deltas = [f"+{b-a:.2f}" if b-a >= 0 else f"{b-a:.2f}" for a, b in zip(scores_a, scores_b)]
    for i, (a_val, b_val, d) in enumerate(zip(scores_a, scores_b, deltas)):
        y_max = max(a_val, b_val) + 0.15
        color = COLORS["delta_pos"] if float(d) >= 0 else COLORS["delta_neg"]
        ax.text(i, y_max, f"Δ={d}", ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=color)
    
    ax.set_ylabel("Mean Score (0–5)")
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=9)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, 4.0)
    
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "figure1_scores.png"), dpi=300)
    fig.savefig(os.path.join(FIGURES_DIR, "figure1_scores.pdf"))
    plt.close(fig)
    print("  Figure 1 OK")


# ============================================================
# Figure 2 - Delta vs model size
# ============================================================

def figure2_delta():
    # Use log scale for params, ordered by pipeline B-A delta
    models = ["Gemma 3 4B", "Nemotron 3", "DeepSeek V4 Flash", "Gemma 4 26B"]
    sizes = [4e9, 3e9, 10e9, 26e9]  # DeepSeek size unknown, placeholder at 10B
    deltas = [-0.30, -0.18, -0.22, -0.26]
    colors = [COLORS["delta_neg"] if d < 0 else COLORS["delta_pos"] for d in deltas]
    
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    
    # DeepSeek marker: diamond with border
    markers = ["o", "o", "D", "o"]
    alphas = [1.0, 1.0, 0.6, 1.0]
    
    for m, s, d, c, mk, al in zip(models, sizes, deltas, colors, markers, alphas):
        ax.scatter(s, d, s=150, color=c, marker=mk, zorder=5, alpha=al,
                   edgecolors="black", linewidth=0.5)
        offset = (5, 12) if d < 0 else (5, -12)
        ax.annotate(f"  {m}\n  Δ={d:+.2f}", (s, d),
                    textcoords="offset points", xytext=offset,
                    fontsize=8, color=c, fontweight="bold")
    
    ax.set_xscale("log")
    ax.set_xlabel("Model Size (parameters, log scale)")
    ax.set_ylabel("Pipeline B−A (Markdown − Raw)")
    ax.grid(alpha=0.3, linestyle="--")
    
    # Format x-axis ticks
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e9:.0f}B" if v >= 1e9 else f"{v/1e6:.0f}M"))
    ax.set_xlim(0.5e9, 50e9)
    ax.set_ylim(-0.35, 0.15)
    
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "figure2_delta.png"), dpi=300)
    fig.savefig(os.path.join(FIGURES_DIR, "figure2_delta.pdf"))
    plt.close(fig)
    print("  Figure 2 OK")


# ============================================================
# Figure 3 - Shallow chunks: distribution of chunk lengths
# ============================================================

def strip_markdown(text: str) -> str:
    """Remove Markdown syntax tokens, keeping informative text."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)          # bold/italic
    text = re.sub(r'`{1,3}.+?`{1,3}', '', text)                 # inline code
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)        # links
    text = re.sub(r'\|[-\s|:]*\|', '', text, flags=re.MULTILINE)  # table separators
    text = re.sub(r'^[>\s]*', '', text, flags=re.MULTILINE)     # blockquotes
    text = re.sub(r'[-*+]\s', '', text)                         # unordered list markers
    text = re.sub(r'^\d+\.\s', '', text, flags=re.MULTILINE)    # ordered list markers
    return text.strip()

def load_chunk_lengths(batch_file, pipeline_label=""):
    """Load retrieved chunk informative lengths from a batch file."""
    with open(batch_file, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    lengths = []
    shallow = 0
    total_chunks = 0
    
    for r in results:
        chunks = r.get("retrieved_chunks", [])
        for c in chunks:
            raw_text = c.get("text", "")
            clean = strip_markdown(raw_text)
            info_len = len(clean)
            lengths.append(info_len)
            total_chunks += 1
            if info_len <= 200:
                shallow += 1
    
    return np.array(lengths), shallow, total_chunks

def figure3_shallow():
    # Load data from the most recent complete A and B batch runs
    file_a = os.path.join(LOGS_DIR, "batch_gemma26b_a_20260512_122008.json")
    file_b = os.path.join(LOGS_DIR, "batch_z_gemma26b_b_merged.json")
    
    lengths_a, shallow_a, total_a = load_chunk_lengths(file_a)
    lengths_b, shallow_b, total_b = load_chunk_lengths(file_b)
    
    pct_a = 100 * shallow_a / total_a if total_a else 0
    pct_b = 100 * shallow_b / total_b if total_b else 0
    
    print(f"  Pipeline A: {shallow_a}/{total_a} shallow ({pct_a:.1f}%)")
    print(f"  Pipeline B: {shallow_b}/{total_b} shallow ({pct_b:.1f}%)")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), sharey=True)
    
    bins = np.linspace(0, 8000, 50)
    
    # Pipeline A histogram
    ax1.hist(lengths_a, bins=bins, color=COLORS["a"], alpha=0.85, edgecolor="white", linewidth=0.3)
    ax1.axvline(x=200, color="red", linestyle="--", linewidth=1, label="Shallow threshold (≤200)")
    ax1.set_title(f"Pipeline A (Raw)\n{shallow_a}/{total_a} shallow = {pct_a:.1f}%", fontsize=10)
    ax1.set_xlabel("Informative chunk length (chars)")
    ax1.set_ylabel("Number of retrieved chunks")
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")
    
    # Pipeline B histogram - with inset for shallow zone
    ax2.hist(lengths_b, bins=bins, color=COLORS["b"], alpha=0.85, edgecolor="white", linewidth=0.3)
    ax2.axvline(x=200, color="red", linestyle="--", linewidth=1, label="Shallow threshold (≤200)")
    ax2.set_title(f"Pipeline B (Markdown)\n{shallow_b}/{total_b} shallow = {pct_b:.1f}%", fontsize=10)
    ax2.set_xlabel("Informative chunk length (chars)")
    ax2.legend(fontsize=8)
    ax2.grid(axis="y", alpha=0.3, linestyle="--")
    
    # Inset: zoom on 0-500 range for Pipeline B (top-right, clear of x-label)
    axins = ax2.inset_axes([0.50, 0.50, 0.48, 0.48])
    axins.hist(lengths_b[lengths_b <= 500], bins=20, range=(0, 500),
               color=COLORS["delta_neg"], alpha=0.85, edgecolor="white", linewidth=0.3)
    axins.set_xlim(0, 500)
    axins.set_title("Shallow zone (0-500)", fontsize=7)
    axins.tick_params(labelsize=6)
    axins.set_xlabel("")
    ax2.indicate_inset_zoom(axins, edgecolor="black")
    
    fig.subplots_adjust(bottom=0.16, wspace=0.35)
    fig.savefig(os.path.join(FIGURES_DIR, "figure3_shallow.png"), dpi=300)
    fig.savefig(os.path.join(FIGURES_DIR, "figure3_shallow.pdf"))
    plt.close(fig)
    print("  Figure 3 OK")


# ============================================================
# Figure 4 - Oracle test (paired bars)
# ============================================================

def figure4_oracle():
    conditions = ["Pipeline A\n(top-3 retrieval)", "Pipeline B\n(top-3 retrieval)",
                  "Oracle\n(full document, A)", "Oracle\n(full document, B)"]
    scores = [1.73, 1.58, 2.90, 2.93]
    
    colors_bar = [COLORS["a"], COLORS["b"], "#3A7A3A", "#AA6A3A"]
    improvements = [0, 0, 2.90 - 1.73, 2.93 - 1.58]
    
    x = np.arange(len(conditions))
    
    fig, ax = plt.subplots(figsize=(7, 4))
    
    bars = ax.bar(x, scores, width=0.55, color=colors_bar, edgecolor="white", linewidth=0.5)
    
    # Add value labels on bars
    for i, (bar, sc) in enumerate(zip(bars, scores)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06,
                f"{sc:.2f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    
    # Add improvement arrow and label for oracle bars
    for i in [2, 3]:
        anno = "+67%" if i == 2 else "+85%"
        ax.annotate(anno + " vs. retrieval",
                    xy=(x[i], scores[i] - 0.2), fontsize=8,
                    ha="center", color="darkgreen", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
    
    ax.set_ylabel("Mean Score (0–5)")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, 3.6)
    
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "figure4_oracle.png"), dpi=300)
    fig.savefig(os.path.join(FIGURES_DIR, "figure4_oracle.pdf"))
    plt.close(fig)
    print("  Figure 4 OK")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Generating figures...")
    figure1_scores()
    figure2_delta()
    figure3_shallow()
    figure4_oracle()
    print(f"\nAll figures saved to {FIGURES_DIR}/")
    print("Files: figure1_scores.{png,pdf}, figure2_delta.{png,pdf}, figure3_shallow.{png,pdf}, figure4_oracle.{png,pdf}")
