"""
CHART 5 — Health Equity Disparities: HIGH/CRITICAL vs LOW Tracts
Font: Times New Roman, 36pt, Bold throughout
Print size: 36x48 inches poster ready (300 DPI)
Real values from Script 06 EDA output
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
OUTPUT = r"C:\capstone\outputs\chart5_equity.png"

# ── Font setup ─────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "Times New Roman",
    "font.size":        36,
    "font.weight":      "bold",
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ── Colors ─────────────────────────────────────────────
COL_HIGH = "#b03020"    # red for HIGH/CRITICAL
COL_LOW  = "#006633"    # green for LOW
COL_DARK = "#004d26"
COL_GRAY = "#444444"

# ── Load real data ─────────────────────────────────────
df = pd.read_csv(INPUT)

def assign_tier(score):
    if   score >= 22: return "CRITICAL"
    elif score >= 19: return "HIGH"
    elif score >= 16: return "MODERATE"
    else:             return "LOW"

df["Risk_Tier"] = df["Healthcare_Desert_Score"].apply(assign_tier)

high_risk = df[df["Risk_Tier"].isin(["HIGH", "CRITICAL"])]
low_risk  = df[df["Risk_Tier"] == "LOW"]

# ── SDOH indicators — using real column names from your data
indicators = [
    ("Food_Insecurity",    "Food\nInsecurity"),
    ("Utility_Threat",     "Utility\nThreat"),
    ("Transport_Barriers", "Transport\nBarriers"),
    ("Insurance_Gap",      "Uninsured\nRate"),
    ("Housing_Insecure",   "Housing\nInsecure"),
    ("Loneliness",         "Loneliness"),
]

cols_exist = [c for c, _ in indicators if c in df.columns]
labels     = [l for c, l in indicators if c in df.columns]

high_vals  = [high_risk[c].mean() for c in cols_exist]
low_vals   = [low_risk[c].mean()  for c in cols_exist]
multipliers = [h/l if l > 0 else 0
               for h, l in zip(high_vals, low_vals)]

print("SDOH values:")
for c, h, l, m in zip(cols_exist, high_vals, low_vals, multipliers):
    print(f"  {c:20s}  HIGH={h:.1f}%  LOW={l:.1f}%  mult={m:.1f}x")

# ── Figure ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(22, 14))

x      = np.arange(len(cols_exist))
width  = 0.36

bars_h = ax.bar(x - width/2, high_vals, width,
                color=COL_HIGH, label="HIGH / CRITICAL tracts",
                edgecolor="white", linewidth=1.0)
bars_l = ax.bar(x + width/2, low_vals, width,
                color=COL_LOW,  label="LOW risk tracts",
                edgecolor="white", linewidth=1.0)

# ── Value labels on each bar ───────────────────────────
for bar, val in zip(bars_h, high_vals):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.6,
            f"{val:.1f}%",
            ha="center", va="bottom",
            fontsize=28, fontweight="bold",
            fontfamily="Times New Roman",
            color=COL_HIGH)

for bar, val in zip(bars_l, low_vals):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.6,
            f"{val:.1f}%",
            ha="center", va="bottom",
            fontsize=28, fontweight="bold",
            fontfamily="Times New Roman",
            color=COL_LOW)



# ── Axes ───────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(labels,
                   fontsize=34, fontweight="bold",
                   fontfamily="Times New Roman")
ax.set_ylabel("Prevalence (%)",
              fontsize=36, fontweight="bold",
              fontfamily="Times New Roman",
              color=COL_GRAY)
ax.tick_params(axis="x", length=0, pad=10)
ax.tick_params(axis="y", colors=COL_GRAY, width=1.5,
               length=6, labelsize=34)
for lbl in ax.get_yticklabels():
    lbl.set_fontfamily("Times New Roman")
    lbl.set_fontweight("bold")

ax.spines["left"].set_color("#cccccc")
ax.spines["bottom"].set_color("#cccccc")
ax.yaxis.grid(True, color="#dddddd", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)

# ── Legend ─────────────────────────────────────────────
patches = [
    mpatches.Patch(color=COL_HIGH, label="HIGH / CRITICAL desert tracts"),
    mpatches.Patch(color=COL_LOW,  label="LOW risk tracts"),
]
ax.legend(handles=patches,
          fontsize=20, loc="upper left",
          framealpha=0.9, edgecolor="#cccccc",
          prop={"family": "Times New Roman",
                "size": 30, "weight": "bold"})

ax.set_title(
    "Health Equity Disparities: Healthcare Desert vs. Low-Risk Tracts\n"
  ,
    fontsize=36, fontweight="bold",
    fontfamily="Times New Roman",
    color=COL_DARK, pad=22
)

fig.tight_layout(pad=2.0)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {OUTPUT}")
print("Chart 5 complete.")
