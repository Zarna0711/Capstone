import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

OUT = r"C:\capstone\outputs\fig10_score_distribution_fixed.png"
DPI = 300

# ── Colors ────────────────────────────────────────────
GMU_GREEN  = "#006633"
DARK_GREEN = "#004d26"
LIGHT_GRAY = "#e8e8e8"
GRAY       = "#555555"
AMBER      = "#d4a010"
ORANGE     = "#c8600a"
RED        = "#b03020"

# ── Global style ──────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "font.family":        "Times New Roman",
    "axes.titlepad":      14,
})

# ── Simulate realistic right-skewed score distribution
# matching your real stats: mean=15.04, median=14.23, SD=4.12
scores = pd.read_csv(r"C:\capstone\outputs\Virginia_Master_Scored.csv")["Healthcare_Desert_Score"].dropna().values

# ── Plot ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))

n, bins, patches = ax.hist(scores, bins=40,
                            edgecolor="white", linewidth=0.5, zorder=3)

# Color each bar by tier
for patch, left in zip(patches, bins[:-1]):
    if left >= 22:   patch.set_facecolor(RED)
    elif left >= 19: patch.set_facecolor(ORANGE)
    elif left >= 16: patch.set_facecolor(AMBER)
    else:            patch.set_facecolor(GMU_GREEN)

ylim = ax.get_ylim()[1]

# ── Threshold lines ────────────────────────────────────
thresholds = [
    (16, AMBER,  "MODERATE ", 0.90),
    (19, ORANGE, "HIGH ",     0.76),
    (22, RED,    "CRITICAL", 0.62),
]
for thresh, col, lbl, y_frac in thresholds:
    ax.axvline(thresh, color=col, lw=1.8, ls="--", zorder=4)
    ax.text(thresh + 0.3, ylim * y_frac, lbl,
            fontsize=9.5, color=col, va="top",
            fontweight="bold", zorder=5)

# ── Mean and median lines ──────────────────────────────
ax.axvline(scores.mean(),   color=DARK_GREEN, lw=1.5, ls="-",
           label=f"Mean = {scores.mean():.2f}", zorder=4)
ax.axvline(np.median(scores), color=GRAY, lw=1.5, ls=":",
           label=f"Median = {np.median(scores):.2f}", zorder=4)

# ── FIX 1: Stats box moved to TOP-LEFT ─────────────────
# was top-right and hidden behind legend
stats_text = (
    f"Mean      = {scores.mean():.2f}\n"
    f"Median  = {np.median(scores):.2f}\n"
    f"SD          = {scores.std():.2f}\n"
    f"Skewness = {float(np.mean(((scores - scores.mean())/scores.std())**3)):.3f}\n"
    f"(right-skewed)"
)
ax.text(0.02, 0.97, stats_text,
        transform=ax.transAxes,
        ha="left", va="top",           # FIX: was ha="right"
        fontsize=10, color=DARK_GREEN,
        bbox=dict(boxstyle="round,pad=0.45",
                  fc="#e8f5ee", ec=GMU_GREEN, lw=0.8))

# ── Legend ─────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=GMU_GREEN, label="LOW  (< 16.0)"),
    mpatches.Patch(color=AMBER,     label="MODERATE (16.0–18.9)"),
    mpatches.Patch(color=ORANGE,    label="HIGH (19.0–21.9)"),
    mpatches.Patch(color=RED,       label="CRITICAL (≥ 22.0)"),
]
ax.legend(handles=legend_patches,
          fontsize=10, loc="upper right",   # legend stays top-right
          framealpha=0.9, edgecolor=LIGHT_GRAY)

# ── FIX 3: Lighter, smaller title ─────────────────────
# was large bold green — now quieter so it doesn't
# compete with the poster section header
ax.set_title(
    "Healthcare Desert Score Distribution (2,166 Virginia Census Tracts)\n"
    "Right-skewed distribution",
    fontsize=20,              # FIX: was 14
    fontweight="bold",      # FIX: was "bold"
    color=DARK_GREEN
)

ax.set_xlabel("Healthcare Desert Score", color=GRAY, fontsize=11, fontweight="bold")
ax.set_ylabel("Number of Census Tracts", color=GRAY, fontsize=11,fontweight="bold")
ax.tick_params(colors=GRAY)
ax.spines["left"].set_color(LIGHT_GRAY)
ax.spines["bottom"].set_color(LIGHT_GRAY)

fig.tight_layout()
fig.savefig(OUT, dpi=DPI, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {OUT}")
