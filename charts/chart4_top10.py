"""
CHART 4 — Top 10 Virginia Healthcare Desert Communities
Font: Times New Roman, 36pt, Bold throughout
Print size: 36x48 inches poster ready (300 DPI)
Reads from Virginia_Healthcare_Deserts.csv (Script 04 output)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────
INPUT  = r"C:\capstone\outputs\Virginia_Healthcare_Deserts.csv"
OUTPUT = r"C:\capstone\outputs\chart4.png"

# ── Font setup ─────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "Times New Roman",
    "font.size":        36,
    "font.weight":      "bold",
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
})

# ── Colors ─────────────────────────────────────────────
COL_CRITICAL = "#b03020"
COL_HIGH     = "#c8600a"
COL_DARK     = "#004d26"
COL_GRAY     = "#444444"

# ── Load real county data ──────────────────────────────
county = pd.read_csv(INPUT)
county = county.sort_values("Healthcare_Desert_Score",
                             ascending=False).reset_index(drop=True)
top10  = county.head(10).copy()

print("Top 10 counties:")
for _, row in top10.iterrows():
    print(f"  {row['CountyName']:25s} {row['Healthcare_Desert_Score']:.2f}  [{row['Risk_Tier']}]")

# ── Assign bar color by tier ───────────────────────────
def bar_color(tier):
    return COL_CRITICAL if tier == "CRITICAL" else COL_HIGH

top10["color"] = top10["Risk_Tier"].apply(bar_color)

# ── Figure ─────────────────────────────────────────────
# Height scaled so each bar has plenty of room
fig, ax = plt.subplots(figsize=(22, 16))

y_pos = np.arange(len(top10))

# Plot bars reversed so highest is at top
bars = ax.barh(
    y_pos,
    top10["Healthcare_Desert_Score"].values[::-1],
    color=top10["color"].values[::-1],
    edgecolor="white", linewidth=1.0,
    height=0.65
)

# ── Score labels at end of each bar ───────────────────
for bar, (_, row) in zip(bars, top10.iloc[::-1].iterrows()):
    score = row["Healthcare_Desert_Score"]
    tier  = row["Risk_Tier"]
    ax.text(score + 0.12,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center", ha="left",
            fontsize=32, fontweight="bold",
            fontfamily="Times New Roman",
            color=bar_color(tier))

# ── Y axis — county names ──────────────────────────────
ax.set_yticks(y_pos)
ax.set_yticklabels(
    top10["CountyName"].values[::-1],
    fontsize=36, fontweight="bold",
    fontfamily="Times New Roman"
)
ax.tick_params(axis="y", length=0, pad=10)

# ── X axis ─────────────────────────────────────────────
ax.set_xlim(0, 28)
ax.set_xticks([14, 16, 18, 20, 22, 24])
ax.set_xticklabels(["14", "16", "18", "20", "22", "24"],
                   fontsize=34, fontweight="bold",
                   fontfamily="Times New Roman")
ax.set_xlabel("Healthcare Desert Score",
              fontsize=36, fontweight="bold",
              fontfamily="Times New Roman",
              color=COL_GRAY)
ax.tick_params(axis="x", colors=COL_GRAY, width=1.5, length=6)
ax.spines["bottom"].set_color("#cccccc")

# ── Threshold lines ────────────────────────────────────
ax.axvline(22, color=COL_CRITICAL, lw=2.5, ls="--",
           label="CRITICAL threshold (≥ 22.0)", zorder=4)
ax.axvline(19, color=COL_HIGH,     lw=2.5, ls="--",
           label="HIGH threshold (19.0–21.9)", zorder=4)

# ── Legend ─────────────────────────────────────────────
patches = [
    mpatches.Patch(color=COL_CRITICAL,
                   label="CRITICAL tier (score ≥ 22.0)"),
    mpatches.Patch(color=COL_HIGH,
                   label="HIGH tier (score 19.0–21.9)"),
]
ax.legend(handles=patches,
          fontsize=30, loc="lower left",
          bbox_to_anchor=(-0.20, -0.20),
          framealpha=0.9, edgecolor="#cccccc",
          prop={"family": "Times New Roman",
                "size": 30, "weight": "bold"})

# ── Grid ───────────────────────────────────────────────
ax.xaxis.grid(True, color="#dddddd", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)

ax.set_title(
    "Top 10 Virginia Healthcare Desert Communities\n"
    " HRSA HPSA Validation  |  CDC PLACES 2025",
    fontsize=36, fontweight="bold",
    fontfamily="Times New Roman",
    color=COL_DARK, pad=22
)

fig.tight_layout(pad=2.0)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {OUTPUT}")
print("Chart 4 complete.")
