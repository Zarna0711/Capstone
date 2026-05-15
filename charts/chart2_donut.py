"""
CHART 2 — Risk Tier Distribution Donut Chart
Font: Times New Roman, 36pt, Bold throughout
Print size: 36x48 inches poster ready (300 DPI)
Real data: 2166 tracts — LOW=1462, MODERATE=391, HIGH=167, CRITICAL=146
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────
INPUT  = r"C:\capstone\outputs\Virginia_Master_Scored.csv"
OUTPUT = r"C:\capstone\outputs\chart2_donut.png"

# ── Font setup ─────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "Times New Roman",
    "font.size":        36,
    "font.weight":      "bold",
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
})

# ── Colors ─────────────────────────────────────────────
COL_LOW      = "#006633"
COL_MODERATE = "#d4a010"
COL_HIGH     = "#c8600a"
COL_CRITICAL = "#b03020"
COL_DARK     = "#004d26"

# ── Load real data and count tiers ─────────────────────
df = pd.read_csv(INPUT)

def assign_tier(score):
    if   score >= 22: return "CRITICAL"
    elif score >= 19: return "HIGH"
    elif score >= 16: return "MODERATE"
    else:             return "LOW"

df["Risk_Tier"] = df["Healthcare_Desert_Score"].apply(assign_tier)
counts = df["Risk_Tier"].value_counts()

# Ordered slices
tiers  = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
colors = [COL_LOW, COL_MODERATE, COL_HIGH, COL_CRITICAL]
sizes  = [counts.get(t, 0) for t in tiers]
total  = sum(sizes)

print("Tier counts:")
for t, s in zip(tiers, sizes):
    print(f"  {t:10s}: {s:4d} tracts ({s/total*100:.1f}%)")

# ── Figure ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 18))

# Draw donut — wedgeprops width makes the hole
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=None,
    colors=colors,
    autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct/100*total)):,})",
    startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.52, edgecolor="white", linewidth=3),
)

# Style autotext (percentages inside slices)
for at in autotexts:
    at.set_fontsize(32)
    at.set_fontweight("bold")
    at.set_fontfamily("Times New Roman")
    at.set_color("white")

# ── Center label ───────────────────────────────────────
ax.text(0, 0.08, f"{total:,}",
        ha="center", va="center",
        fontsize=54, fontweight="bold",
        fontfamily="Times New Roman",
        color=COL_DARK)
ax.text(0, -0.18, "census tracts",
        ha="center", va="center",
        fontsize=34, fontweight="bold",
        fontfamily="Times New Roman",
        color="#555555")
ax.text(0, -0.38, "Virginia",
        ha="center", va="center",
        fontsize=32, fontweight="bold",
        fontfamily="Times New Roman",
        color="#555555")

# ── Custom legend outside the donut ───────────────────
legend_labels = [
    "LOW  < 16.0",
    "MODERATE  16.0–18.9",
    "HIGH  19.0–21.9",
    "CRITICAL  ≥ 22.0"
]
import matplotlib.patches as mpatches

# ── Title (Standardized padding to 20) ───────────────────
ax.set_title(
    "Risk Tier Distribution Across Virginia Census Tracts\n"
    "CDC PLACES 2025  |  Healthcare Desert Score",
    fontsize=36, 
    fontweight="bold",
    fontfamily="Times New Roman",
    color=COL_DARK, 
    pad=20  # Changed from 24 to 20 for uniformity
)

# ── Layout and Save ──────────────────────────────────────
# Using a consistent pad here ensures no labels are clipped
fig.tight_layout(pad=2.0)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {OUTPUT}")
print("Chart 2 complete.")
