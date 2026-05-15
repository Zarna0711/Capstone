"""
CHART 6 — HRSA Validation Results Stat Callout
Three large numbers: 100% Specificity, 100% PPV, 8.7% Sensitivity
Font: Times New Roman, 36pt, Bold throughout
Print size: 36x48 inches poster ready (300 DPI)
Real values from Script 05 output
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as FancyBboxPatch
import numpy as np
import os

# ── Path ───────────────────────────────────────────────
OUTPUT = r"C:\capstone\outputs\chart6_validation.png"

# ── Font setup ─────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "Times New Roman",
    "font.size":        36,
    "font.weight":      "bold",
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
})

# ── Real validation results from Script 05 ─────────────
# TP=9, FP=0, FN=95, TN=25
# Sensitivity = 9/(9+95) = 8.7%
# Specificity = 25/(25+0) = 100%
# PPV         = 9/(9+0)  = 100%

stats = [
    {
        "value":    "100%",
        "metric":   "Specificity",
        "sub1":     "Zero false alarms",
        "sub2":     "TN = 25  |  FP = 0",
        "bg":       "#e8f5ee",
        "border":   "#006633",
        "vcol":     "#004d26",
    },
    {
        "value":    "100%",
        "metric":   "PPV",
        "sub1":     "Every flag confirmed",
        "sub2":     "TP = 9  |  FP = 0",
        "bg":       "#e8f5ee",
        "border":   "#006633",
        "vcol":     "#004d26",
    },
    {
        "value":    "8.7%",
        "metric":   "Sensitivity",
        "sub1":     "Threshold conservative",
        "sub2":     "TP = 9  |  FN = 95",
        "bg":       "#fff3e0",
        "border":   "#c8600a",
        "vcol":     "#b03020",
    },
]

# ── Figure — wide horizontal layout ────────────────────
fig, axes = plt.subplots(1, 3, figsize=(26, 10))

for ax, s in zip(axes, stats):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Background box
    from matplotlib.patches import FancyBboxPatch as FBP
    box = FBP((0.04, 0.04), 0.92, 0.92,
              boxstyle="round,pad=0.04",
              linewidth=3,
              edgecolor=s["border"],
              facecolor=s["bg"])
    ax.add_patch(box)

    # Large value number
    ax.text(0.5, 0.70, s["value"],
            ha="center", va="center",
            fontsize=88, fontweight="bold",
            fontfamily="Times New Roman",
            color=s["vcol"],
            transform=ax.transAxes)

    # Metric name
    ax.text(0.5, 0.46, s["metric"],
            ha="center", va="center",
            fontsize=44, fontweight="bold",
            fontfamily="Times New Roman",
            color="#222222",
            transform=ax.transAxes)

    # Sub line 1
    ax.text(0.5, 0.30, s["sub1"],
            ha="center", va="center",
            fontsize=32, fontweight="bold",
            fontfamily="Times New Roman",
            color="#555555",
            transform=ax.transAxes)

    # Sub line 2 — confusion matrix counts
    ax.text(0.5, 0.14, s["sub2"],
            ha="center", va="center",
            fontsize=28, fontweight="bold",
            fontfamily="Times New Roman",
            color="#777777",
            transform=ax.transAxes)

# ── Overall title ──────────────────────────────────────
fig.suptitle(
    "HRSA Validation Results — Healthcare Desert Score vs. Federal HPSA Designations\n"
    "104 Virginia HRSA-designated shortage counties  |  100% precision, zero false alarms",
    fontsize=34, fontweight="bold",
    fontfamily="Times New Roman",
    color="#004d26", y=1.02
)

fig.tight_layout(pad=1.5)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {OUTPUT}")
print("Chart 6 complete.")
