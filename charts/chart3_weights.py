"""
CHART 3 — Indicator Weights Pie Chart (Final Clean Version)
- Labels on slices (no legend)
- Reduced title spacing
- Times New Roman, bold styling
- Poster-ready (36x48 inches, 300 DPI)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Output path ────────────────────────────────────────
OUTPUT = r"C:\capstone\outputs\chart3_weights_pie_final.png"

# ── Font setup ─────────────────────────────────────────
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 32,
    "font.weight": "bold",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# ── Data ───────────────────────────────────────────────
indicators = [
    ("Insurance Gap",       0.25),
    ("Low Checkups",        0.20),
    ("Food Insecurity",     0.15),
    ("Housing Instability", 0.12),
    ("Loneliness",          0.10),
    ("Transport Barriers",  0.08),
    ("Utility Threat",      0.05),
    ("Food Stamps",         0.05),
]

labels  = [x[0] for x in indicators]
weights = [x[1] for x in indicators]

# ── Colors ─────────────────────────────────────────────
colors = [
    "#004d26",
    "#006633",
    "#1a7a45",
    "#2e8b57",
    "#d4a010",
    "#c8600a",
    "#b03020",
    "#8b2015",
]

# ── Figure ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 16))

wedges, texts, autotexts = ax.pie(
    weights,
    labels=labels,          # ✔ labels directly on slices
    colors=colors,
    autopct='%1.0f%%',
    startangle=140,
    labeldistance=1.05,     # pushes labels slightly outside pie
    pctdistance=0.75,
    textprops={
        "fontsize": 28,
        "fontweight": "bold",
        "fontfamily": "Times New Roman"
    }
)

# ── Style percentages ──────────────────────────────────
for t in autotexts:
    t.set_color("white")
    t.set_fontsize(28)
    t.set_fontweight("bold")

# ── Title (REDUCED GAP HERE) ───────────────────────────
ax.set_title(
    "Healthcare Desert Score -Indicator Weights",
    fontsize=36,
    fontweight="bold",
    fontfamily="Times New Roman",
    color="#004d26",
    pad=10   
)

# ── Keep circle shape ──────────────────────────────────
ax.axis("equal")

# ── Layout tightening ──────────────────────────────────
plt.tight_layout()

# ── Save ───────────────────────────────────────────────
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {OUTPUT}")
print("Final pie chart complete.")