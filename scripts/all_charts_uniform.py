"""
Virginia Healthcare Desert — All 5 Poster Charts
=================================================
Poster size : 36 × 48 inches (portrait)
Font        : Times New Roman, Bold, everywhere
DPI         : 300 (print-ready)

UNIFORM STYLE GUIDE — change values here, ALL charts update:
  BASE_FS   = 36   base font size
  FIG_W     = 22   figure width  (inches) — keeps aspect ratio
  FIG_H     = 14   figure height (inches)
  TITLE_PAD = 28   gap between chart and title

Outputs: C:\\capstone\\outputs\\poster_charts\\
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

# ════════════════════════════════════════════════════════════════
# ①  MASTER STYLE  — edit here only, every chart inherits this
# ════════════════════════════════════════════════════════════════
FONT        = "Times New Roman"
BASE_FS     = 36          # base font size (pt)
DPI         = 300         # print resolution

# Derived sizes — proportional to BASE_FS
FS_TITLE    = BASE_FS                    # 36 — chart title
FS_AXIS_LBL = BASE_FS                    # 36 — x/y axis labels
FS_TICK     = int(BASE_FS * 0.83)        # 30 — tick mark numbers
FS_BAR_LBL  = int(BASE_FS * 0.83)        # 30 — numbers on bars/slices
FS_LEGEND   = int(BASE_FS * 0.83)        # 30 — legend text
FS_STATS    = int(BASE_FS * 0.75)        # 27 — stats annotation box
FS_CAPTION  = int(BASE_FS * 0.67)        # 24 — small caption text
TITLE_PAD   = 28

# Figure dimensions — designed for 36×48 poster column
# Rectangular charts (bar, histogram, equity)
FIG_W_RECT  = 22          # inches wide
FIG_H_RECT  = 14          # inches tall

# Square-ish charts (pie, donut)
FIG_W_CIRC  = 18          # inches wide
FIG_H_CIRC  = 18          # inches tall

# Apply to matplotlib globally
matplotlib.rcParams.update({
    "font.family":        FONT,
    "font.weight":        "bold",
    "font.size":          BASE_FS,
    "axes.titlesize":     FS_TITLE,
    "axes.titleweight":   "bold",
    "axes.titlepad":      TITLE_PAD,
    "axes.labelsize":     FS_AXIS_LBL,
    "axes.labelweight":   "bold",
    "xtick.labelsize":    FS_TICK,
    "ytick.labelsize":    FS_TICK,
    "legend.fontsize":    FS_LEGEND,
    "legend.title_fontsize": FS_LEGEND,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
})

# Font kwargs helper — use in every ax.text() and ax.annotate()
def FP(size=None):
    """Return font properties dict for ax.text() calls."""
    return {"fontfamily": FONT,
            "fontweight": "bold",
            "fontsize":   size if size else BASE_FS}

def LP():
    """Return prop dict for ax.legend()."""
    return {"family": FONT, "weight": "bold", "size": FS_LEGEND}

# ════════════════════════════════════════════════════════════════
# ②  COLOR PALETTE
# ════════════════════════════════════════════════════════════════
GMU_GREEN    = "#006633"
DARK_GREEN   = "#004d26"
MID_GREEN    = "#4a9e6e"
LIGHT_GREEN  = "#a8d5b5"
RED          = "#b03020"
ORANGE       = "#c8600a"
AMBER        = "#d4a010"
GRAY         = "#444444"
LIGHT_GRAY   = "#dddddd"
PIE_COLORS   = ["#004d26","#006633","#1a7a45","#2e8b57",
                "#d4a010","#c8600a","#b03020","#8b2015"]

# ════════════════════════════════════════════════════════════════
# ③  PATHS
# ════════════════════════════════════════════════════════════════
OUTPUT_DIR = r"C:\capstone\outputs"
SAVE_DIR   = os.path.join(OUTPUT_DIR, "poster_charts")
os.makedirs(SAVE_DIR, exist_ok=True)

SCORED_CSV    = os.path.join(OUTPUT_DIR, "Virginia_Master_Scored.csv")
DESERTS_CSV   = os.path.join(OUTPUT_DIR, "Virginia_Healthcare_Deserts.csv")

def save(fig, name):
    path = os.path.join(SAVE_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓  {name}")

# ════════════════════════════════════════════════════════════════
# ④  LOAD DATA
# ════════════════════════════════════════════════════════════════
print("Loading data …")
df      = pd.read_csv(SCORED_CSV)
county  = pd.read_csv(DESERTS_CSV)

# Make sure Risk_Tier column exists
def tier(s):
    if s >= 22: return "CRITICAL"
    if s >= 19: return "HIGH"
    if s >= 16: return "MODERATE"
    return "LOW"

if "Risk_Tier" not in df.columns:
    df["Risk_Tier"] = df["Healthcare_Desert_Score"].apply(tier)
if "Risk_Tier" not in county.columns:
    county["Risk_Tier"] = county["Healthcare_Desert_Score"].apply(tier)

scores = df["Healthcare_Desert_Score"].dropna()
print(f"  Tracts  : {len(df):,}")
print(f"  Counties: {len(county)}")

# Tier counts
TIER_ORDER  = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
TIER_COLORS = [GMU_GREEN, AMBER, ORANGE, RED]
counts = [int(df["Risk_Tier"].value_counts().get(t, 0))
          for t in TIER_ORDER]
total  = sum(counts)
pcts   = [c / total * 100 for c in counts]


# ════════════════════════════════════════════════════════════════
# CHART 1 — Score distribution histogram
# ════════════════════════════════════════════════════════════════
print("\nChart 1 — Score distribution histogram")
fig, ax = plt.subplots(figsize=(FIG_W_RECT, FIG_H_RECT))

n, bins, patches = ax.hist(scores, bins=40,
                            edgecolor="white", linewidth=1.5, zorder=3)

# Colour each bar by tier
for patch, left in zip(patches, bins[:-1]):
    if   left >= 22: patch.set_facecolor(RED)
    elif left >= 19: patch.set_facecolor(ORANGE)
    elif left >= 16: patch.set_facecolor(AMBER)
    else:            patch.set_facecolor(GMU_GREEN)

ylim = ax.get_ylim()[1]

# Staggered threshold labels — no overlap
for thresh, col, lbl, yf in [
    (16, AMBER,  "MODERATE", 0.90),
    (19, ORANGE, "HIGH",     0.75),
    (22, RED,    "CRITICAL", 0.60),
]:
    ax.axvline(thresh, color=col, lw=3, ls="--", zorder=4)
    ax.text(thresh + 0.4, ylim * yf, lbl,
            va="top", color=col, zorder=5, **FP(FS_BAR_LBL))

# Mean / median lines
ax.axvline(scores.mean(),   color=DARK_GREEN, lw=2.5, ls="-",  zorder=4)
ax.axvline(scores.median(), color=GRAY,       lw=2.5, ls=":",  zorder=4)

# Stats box — top-left, clear of legend
stats = (f"Mean       = {scores.mean():.2f}\n"
         f"Median   = {scores.median():.2f}\n"
         f"SD           = {scores.std():.2f}\n"
         f"Skewness = {scores.skew():.3f}\n"
         f"(right-skewed)")
ax.text(0.02, 0.97, stats, transform=ax.transAxes,
        ha="left", va="top", color=DARK_GREEN,
        bbox=dict(boxstyle="round,pad=0.6",
                  fc="#e8f5ee", ec=GMU_GREEN, lw=2.5),
        **FP(FS_STATS))

# Legend — top-right, inside axes
leg_patches = [
    mpatches.Patch(color=GMU_GREEN, label="LOW  (< 16.0)"),
    mpatches.Patch(color=AMBER,     label="MODERATE (16–18.9)"),
    mpatches.Patch(color=ORANGE,    label="HIGH (19–21.9)"),
    mpatches.Patch(color=RED,       label="CRITICAL (≥ 22.0)"),
]
ax.legend(handles=leg_patches, loc="upper right",
          framealpha=0.95, edgecolor=LIGHT_GRAY,
          prop=LP())

ax.set_title("Healthcare Desert Score Distribution\n"
             "2,166 Virginia Census Tracts  |  CDC PLACES 2025",
             color=DARK_GREEN)
ax.set_xlabel("Healthcare Desert Score", color=GRAY)
ax.set_ylabel("Number of Census Tracts",  color=GRAY)
ax.tick_params(colors=GRAY, width=2, length=8)
ax.spines["left"].set_color(LIGHT_GRAY)
ax.spines["bottom"].set_color(LIGHT_GRAY)

fig.tight_layout(pad=2.0)
save(fig, "chart1_histogram.png")


# ════════════════════════════════════════════════════════════════
# CHART 2 — Risk tier donut chart
# ════════════════════════════════════════════════════════════════
print("Chart 2 — Risk tier donut")
fig, ax = plt.subplots(figsize=(FIG_W_CIRC, FIG_H_CIRC))

wedges, _, autotexts = ax.pie(
    counts,
    labels=None,
    colors=TIER_COLORS,
    autopct=lambda p: f"{p:.1f}%\n({int(round(p/100*total)):,})",
    startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.52, edgecolor="white", linewidth=3),
)

for at in autotexts:
    at.set_fontsize(FS_BAR_LBL)
    at.set_fontweight("bold")
    at.set_fontfamily(FONT)
    at.set_color("white")

# Centre text
ax.text(0,  0.10, f"{total:,}", ha="center", va="center",
        color=DARK_GREEN, **FP(54))
ax.text(0, -0.16, "census tracts", ha="center", va="center",
        color=GRAY, **FP(FS_STATS))
ax.text(0, -0.38, "Virginia", ha="center", va="center",
        color=GRAY, **FP(FS_STATS))
# Standardized Title with 28pt padding (matching your master guide)
ax.set_title("Risk Tier Distribution Across Virginia Census Tracts\n"
             "CDC PLACES 2025  |  Healthcare Desert Score",
             color=DARK_GREEN, pad=TITLE_PAD)


fig.tight_layout(pad=2.0)
save(fig, "chart2_donut.png")


# ════════════════════════════════════════════════════════════════
# CHART 3 — Indicator weights pie chart
# ════════════════════════════════════════════════════════════════
print("Chart 3 — Indicator weights pie")
indicators_w = [
    ("Insurance Gap",       0.25),
    ("Low Checkups",        0.20),
    ("Food Insecurity",     0.15),
    ("Housing Instability", 0.12),
    ("Loneliness",          0.10),
    ("Transport Barriers",  0.08),
    ("Utility Threat",      0.05),
    ("Food Stamps",         0.05),
]
labels_w  = [x[0] for x in indicators_w]
weights_w = [x[1] for x in indicators_w]

fig, ax = plt.subplots(figsize=(FIG_W_CIRC, FIG_H_CIRC))

# startangle=140 separates the two 5% wedges cleanly
wedges, texts, autotexts = ax.pie(
    weights_w,
    labels=None,
    colors=PIE_COLORS,
    autopct="%1.0f%%",
    startangle=140,
    counterclock=False,
    pctdistance=0.78,
    wedgeprops=dict(edgecolor="white", linewidth=3),
)

# Percentage labels inside slices
for at in autotexts:
    at.set_fontsize(FS_BAR_LBL)
    at.set_fontweight("bold")
    at.set_fontfamily(FONT)
    at.set_color("white")

# Leader-line labels outside — small wedges pushed further out
for i, (wedge, lbl, col) in enumerate(
        zip(wedges, labels_w, PIE_COLORS)):
    angle = (wedge.theta2 + wedge.theta1) / 2
    rad   = np.radians(angle)
    dist  = 1.22 if weights_w[i] >= 0.10 else 1.42
    xo = dist * np.cos(rad)
    yo = dist * np.sin(rad)
    xi = 0.72 * np.cos(rad)
    yi = 0.72 * np.sin(rad)
    ha = "left" if xo > 0 else "right"
    ax.annotate(
        lbl,
        xy=(xi, yi), xytext=(xo, yo),
        arrowprops=dict(arrowstyle="-", color=col,
                        lw=2, shrinkA=0, shrinkB=0),
        ha=ha, va="center", color=col,
        linespacing=1.4, **FP(FS_BAR_LBL))

ax.set_title("Healthcare Desert Score - Indicator Weights\n",
             color=DARK_GREEN)

ax.axis("equal")
fig.tight_layout(pad=2.5)
save(fig, "chart3_weights_pie.png")


# ════════════════════════════════════════════════════════════════
# CHART 4 — Top 10 healthcare desert communities
# ════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════
# CHART 4 — Top 10 healthcare desert communities (Corrected)
# ════════════════════════════════════════════════════════════════
print("Chart 4 — Top 10 counties")

# ... (data processing stays the same) ...

fig, ax = plt.subplots(figsize=(FIG_W_RECT, FIG_H_RECT))

# Highest score at top → reverse
y = np.arange(len(top10))
ax.barh(y, top10["Healthcare_Desert_Score"].values[::-1],
        color=bar_colors[::-1], height=0.62,
        edgecolor="white", linewidth=1.0)

# Score labels ONLY (No brackets)
for i, (_, row) in enumerate(top10.iloc[::-1].iterrows()):
    ax.text(row["Healthcare_Desert_Score"] + 0.12, i,
            f"{row['Healthcare_Desert_Score']:.2f}",
            va="center", ha="left",
            color=RED if row["Risk_Tier"] == "CRITICAL" else ORANGE,
            **FP(FS_BAR_LBL))

ax.set_yticks(y)
ax.set_yticklabels(top10["CountyName"].values[::-1])

# Threshold lines
ax.axvline(19, color=ORANGE, lw=2.5, ls="--", zorder=4)
ax.axvline(22, color=RED,    lw=2.5, ls="--", zorder=4)

# Legend — Moved to LOWER RIGHT to avoid overlapping bars
ax.legend(handles=leg_patches, 
          loc="lower right", 
          framealpha=0.95, 
          edgecolor=LIGHT_GRAY,
          prop=LP())

ax.set_xlim(0, top10["Healthcare_Desert_Score"].max() + 5)
ax.set_xlabel("Healthcare Desert Score", color=GRAY)

# Standardized Title (Using TITLE_PAD for uniformity)
ax.set_title("Top 10 Virginia Healthcare Desert Communities\n"
             "HRSA HPSA Validated",
             color=DARK_GREEN, 
             pad=TITLE_PAD)

ax.tick_params(axis="y", length=0, pad=10)
ax.tick_params(axis="x", colors=GRAY, width=2, length=8)
ax.spines["left"].set_color(LIGHT_GRAY)
ax.spines["bottom"].set_color(LIGHT_GRAY)
ax.xaxis.grid(True, color=LIGHT_GRAY, lw=1, zorder=0)
ax.set_axisbelow(True)

fig.tight_layout(pad=2.0)
save(fig, "chart4_top10.png")

# ════════════════════════════════════════════════════════════════
# CHART 5 — Health equity disparities
# ════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════
# CHART 5 — Health equity disparities (Multiplier logic removed)
# ════════════════════════════════════════════════════════════════
print("Chart 5 — Health equity disparities")

high_risk = df[df["Risk_Tier"].isin(["HIGH", "CRITICAL"])]
low_risk  = df[df["Risk_Tier"] == "LOW"]

sdoh_map = [
    ("Food_Insecurity",    "Food\nInsecurity"),
    ("Utility_Threat",     "Utility\nThreat"),
    ("Transport_Barriers", "Transport\nBarriers"),
    ("Insurance_Gap",      "Uninsured\nRate"),
    ("Housing_Insecure",   "Housing\nInsecure"),
    ("Loneliness",         "Loneliness"),
]
exist    = [(c, l) for c, l in sdoh_map if c in df.columns]
cols_e   = [c for c, _ in exist]
labels_e = [l for _, l in exist]

high_v   = [high_risk[c].mean() for c in cols_e]
low_v    = [low_risk[c].mean()  for c in cols_e]

# Removed mults calculation to clean up the script

fig, ax = plt.subplots(figsize=(FIG_W_RECT, FIG_H_RECT))

x     = np.arange(len(cols_e))
width = 0.36

bh = ax.bar(x - width / 2, high_v, width,
            color=RED, label="HIGH / CRITICAL desert tracts",
            edgecolor="white", linewidth=1.5)
bl = ax.bar(x + width / 2, low_v,  width,
            color=GMU_GREEN, label="LOW risk tracts",
            edgecolor="white", linewidth=1.5)

# Value labels on bars - Numbers only
for bar, val in zip(bh, high_v):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", va="bottom",
            color=RED, **FP(FS_BAR_LBL))

for bar, val in zip(bl, low_v):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", va="bottom",
            color=DARK_GREEN, **FP(FS_BAR_LBL))

ax.set_xticks(x)
ax.set_xticklabels(labels_e)
ax.set_ylabel("Prevalence (%)", color=GRAY)
ax.set_ylim(0, max(high_v) * 1.30)

# Standardized Title (Using TITLE_PAD for uniformity)
ax.set_title("Health Equity Disparities: Desert vs. Low-Risk Tracts",
             color=DARK_GREEN, 
             pad=TITLE_PAD) # <── Verified: Using global pad

leg_patches = [
    mpatches.Patch(color=RED,       label="HIGH / CRITICAL desert tracts"),
    mpatches.Patch(color=GMU_GREEN, label="LOW risk tracts"),
]
ax.legend(handles=leg_patches, loc="upper right",
          framealpha=0.95, edgecolor=LIGHT_GRAY,
          prop=LP())

ax.tick_params(axis="x", length=0, pad=12)
ax.tick_params(axis="y", colors=GRAY, width=2, length=8)
ax.spines["left"].set_color(LIGHT_GRAY)
ax.spines["bottom"].set_color(LIGHT_GRAY)
ax.yaxis.grid(True, color=LIGHT_GRAY, lw=1, zorder=0)
ax.set_axisbelow(True)

fig.tight_layout(pad=2.0)
save(fig, "chart5_equity.png")

# ════════════════════════════════════════════════════════════════
print(f"""
All 5 charts saved to:
  {SAVE_DIR}

  chart1_histogram.png
  chart2_donut.png
  chart3_weights_pie.png
  chart4_top10.png
  chart5_equity.png

All charts use:
  Font       : Times New Roman
  Weight     : Bold (title, labels, ticks, legend, annotations)
  Base size  : {BASE_FS}pt
  Tick size  : {FS_TICK}pt
  Legend     : {FS_LEGEND}pt
  Bar labels : {FS_BAR_LBL}pt
  DPI        : {DPI}
""")
