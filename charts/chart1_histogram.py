"""
CHART 1 — Healthcare Desert Score Distribution Histogram
Font: Times New Roman, 36pt, Bold throughout
Print size: 36x48 inches poster ready (300 DPI)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────
INPUT  = r"C:\capstone\outputs\Virginia_Master_Scored.csv"
OUTPUT = r"C:\capstone\outputs\chart1_histogram.png"

# ── Font setup — Times New Roman 36pt Bold everywhere ──
plt.rcParams.update({
    "font.family":        "Times New Roman",
    "font.size":          36,
    "font.weight":        "bold",
    "axes.titlesize":     36,
    "axes.titleweight":   "bold",
    "axes.labelsize":     36,
    "axes.labelweight":   "bold",
    "xtick.labelsize":    36,
    "ytick.labelsize":    36,
    "legend.fontsize":    34,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
})

# ── Colors matching your tier system ───────────────────
COL_LOW      = "#006633"   # GMU green
COL_MODERATE = "#d4a010"   # amber
COL_HIGH     = "#c8600a"   # orange
COL_CRITICAL = "#b03020"   # red
COL_DARK     = "#004d26"
COL_GRAY     = "#444444"
COL_LGRAY    = "#cccccc"

# ── Load real data ─────────────────────────────────────
scores = pd.read_csv(INPUT)["Healthcare_Desert_Score"].dropna().values
print(f"Loaded {len(scores):,} tract scores")
print(f"Mean={scores.mean():.2f}  Median={np.median(scores):.2f}  "
      f"SD={scores.std():.2f}  Skew={float(np.mean(((scores-scores.mean())/scores.std())**3)):.3f}")

# ── Figure — large enough for 36x48 poster ─────────────
fig, ax = plt.subplots(figsize=(22, 14))

# ── Draw histogram ─────────────────────────────────────
n, bins, patches = ax.hist(scores, bins=40,
                            edgecolor="white", linewidth=0.8, zorder=3)

# Color each bar by tier threshold
for patch, left in zip(patches, bins[:-1]):
    if   left >= 22: patch.set_facecolor(COL_CRITICAL)
    elif left >= 19: patch.set_facecolor(COL_HIGH)
    elif left >= 16: patch.set_facecolor(COL_MODERATE)
    else:            patch.set_facecolor(COL_LOW)

ylim = ax.get_ylim()[1]

# ── Threshold dashed lines ─────────────────────────────
thresholds = [
    (16, COL_MODERATE),
    (19, COL_HIGH),
    (22, COL_CRITICAL),
]

for thresh, col in thresholds:
    ax.axvline(thresh, color=col, lw=3.0, ls="--", zorder=4)

# ── Mean and Median lines ──────────────────────────────
ax.axvline(scores.mean(),      color=COL_DARK, lw=2.5, ls="-",  zorder=4)
ax.axvline(np.median(scores),  color=COL_GRAY, lw=2.5, ls=":",  zorder=4)

# ── Stats box top-left ─────────────────────────────────
skew = float(np.mean(((scores - scores.mean()) / scores.std()) ** 3))
stats_text = (
    f"Mean      = {scores.mean():.2f}\n"
    f"Median  = {np.median(scores):.2f}\n"
    f"SD          = {scores.std():.2f}\n"
    f"Skewness = {skew:.3f}\n"
    f"(right-skewed)"
)
ax.text(0.02, 0.97, stats_text,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=30, color=COL_DARK,
        fontfamily="Times New Roman",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5",
                  fc="#e8f5ee", ec=COL_LOW, lw=1.5))

# ── Legend ─────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=COL_LOW,      label="LOW  (< 16.0)"),
    mpatches.Patch(color=COL_MODERATE, label="MODERATE (16.0–18.9)"),
    mpatches.Patch(color=COL_HIGH,     label="HIGH (19.0–21.9)"),
    mpatches.Patch(color=COL_CRITICAL, label="CRITICAL (≥ 22.0)"),
    plt.Line2D([0],[0], color=COL_DARK, lw=2.5, ls="-",
               label=f"Mean = {scores.mean():.2f}"),
    plt.Line2D([0],[0], color=COL_GRAY, lw=2.5, ls=":",
               label=f"Median = {np.median(scores):.2f}"),
]
ax.legend(handles=legend_patches,
          fontsize=30, loc="upper right",
          framealpha=0.9, edgecolor=COL_LGRAY,
          prop={"family": "Times New Roman",
                "size": 30, "weight": "bold"})

# ── Axis labels and title ──────────────────────────────
ax.set_xlabel("Healthcare Desert Score",
              color=COL_GRAY, fontsize=36, fontweight="bold",
              fontfamily="Times New Roman")
ax.set_ylabel("Number of Census Tracts",
              color=COL_GRAY, fontsize=36, fontweight="bold",
              fontfamily="Times New Roman")
ax.set_title(
    "Healthcare Desert Score Distribution (2,166 Virginia Census Tracts)\n"
    "Right-skewed",
    fontsize=36, fontweight="bold",
    fontfamily="Times New Roman",
    color=COL_DARK, pad=20
)

ax.tick_params(colors=COL_GRAY, width=1.5, length=6,
               labelsize=36)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_fontfamily("Times New Roman")
    lbl.set_fontweight("bold")

ax.spines["left"].set_color(COL_LGRAY)
ax.spines["bottom"].set_color(COL_LGRAY)

fig.tight_layout(pad=2.0)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {OUTPUT}")
print("Chart 1 complete.")
