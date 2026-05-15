import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import os

OUTPUT_DIR = r"C:\capstone\outputs"

# ── Load data ──────────────────────────────────────────
master = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Master_Scored.csv"))
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Validated.csv"))
print(f"Tracts loaded: {len(master):,}")
print(f"Counties loaded: {len(county)}")

# ── Split tracts by risk ───────────────────────────────
high_risk = master[master["Risk_Tier"].isin(["HIGH","CRITICAL"])].copy()
mod_risk  = master[master["Risk_Tier"] == "MODERATE"].copy()
low_risk  = master[master["Risk_Tier"] == "LOW"].copy()

print(f"\nTract breakdown:")
print(f"  HIGH/CRITICAL: {len(high_risk):,} tracts")
print(f"  MODERATE:      {len(mod_risk):,} tracts")
print(f"  LOW:           {len(low_risk):,} tracts")

# ── SDOH comparison by tier ───────────────────────────
indicators = [
    ("Insurance_Gap",    "Uninsured (%)"),
    ("Food_Insecurity",  "Food Insecurity (%)"),
    ("Housing_Insecure", "Housing Instability (%)"),
    ("Loneliness",       "Social Isolation (%)"),
    ("Transport_Barriers","Transport Barriers (%)"),
    ("Utility_Threat",   "Utility Threat (%)"),
]

print("\n── SDOH Burden by Risk Tier ──────────────────────────")
print(f"{'Indicator':<25} {'HIGH/CRIT':>10} {'MODERATE':>10} {'LOW':>10}")
print("-" * 58)
for col, label in indicators:
    if col in master.columns:
        h = high_risk[col].mean()
        m = mod_risk[col].mean()
        l = low_risk[col].mean()
        print(f"  {label:<23} {h:>9.1f}% {m:>9.1f}% {l:>9.1f}%")

# ── Figure: 3-panel equity chart ──────────────────────
fig = plt.figure(figsize=(16, 6))
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35)

COLORS = {
    "CRITICAL": "#A32D2D",
    "HIGH":     "#D85A30",
    "MODERATE": "#BA7517",
    "LOW":      "#1D9E75",
}

# Panel 1 — SDOH bar comparison
ax1 = fig.add_subplot(gs[0])
cols_exist = [c for c, _ in indicators if c in master.columns]
labels_exist = [l for c, l in indicators if c in master.columns]
hr_vals = [high_risk[c].mean() for c in cols_exist]
lr_vals = [low_risk[c].mean()  for c in cols_exist]

x = range(len(cols_exist))
ax1.barh([i + 0.2 for i in x], hr_vals, 0.35,
         label="HIGH / CRITICAL", color="#D85A30", alpha=0.9)
ax1.barh([i - 0.2 for i in x], lr_vals, 0.35,
         label="LOW risk", color="#1D9E75", alpha=0.9)
ax1.set_yticks(list(x))
ax1.set_yticklabels(labels_exist, fontsize=9)
ax1.set_xlabel("Population (%)", fontsize=9)
ax1.set_title("SDOH Burden by Desert Status", fontsize=11, fontweight="bold")
ax1.legend(fontsize=8)
ax1.grid(axis="x", alpha=0.3)
ax1.invert_yaxis()

# Panel 2 — Top 20 counties ranked
ax2 = fig.add_subplot(gs[1])
top20 = county.head(20)
bar_colors = [COLORS.get(str(t), "#888") for t in top20["Risk_Tier"]]
bars = ax2.barh(
    top20["CountyName"][::-1],
    top20["Healthcare_Desert_Score"][::-1],
    color=bar_colors[::-1], alpha=0.9
)
ax2.axvline(x=22, color="#A32D2D", linestyle="--", linewidth=0.8, alpha=0.7)
ax2.axvline(x=19, color="#D85A30", linestyle="--", linewidth=0.8, alpha=0.7)
ax2.axvline(x=16, color="#BA7517", linestyle="--", linewidth=0.8, alpha=0.7)
ax2.set_xlabel("Healthcare Desert Score", fontsize=9)
ax2.set_title("Top 20 High-Risk Jurisdictions", fontsize=11, fontweight="bold")
patches = [mpatches.Patch(color=v, label=k) for k, v in COLORS.items()]
ax2.legend(handles=patches, fontsize=7, loc="lower right")
ax2.grid(axis="x", alpha=0.3)

# Panel 3 — Risk tier donut chart
ax3 = fig.add_subplot(gs[2])
tier_order  = ["CRITICAL","HIGH","MODERATE","LOW"]
tier_counts = [master["Risk_Tier"].value_counts().get(t, 0) for t in tier_order]
tier_colors = [COLORS[t] for t in tier_order]
wedges, texts, autotexts = ax3.pie(
    tier_counts,
    labels=tier_order,
    colors=tier_colors,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.75,
    wedgeprops=dict(width=0.5)
)
for at in autotexts:
    at.set_fontsize(8)
for t in texts:
    t.set_fontsize(9)
ax3.set_title("Tract Risk Distribution\n(2,166 Virginia census tracts)",
              fontsize=11, fontweight="bold")

# Add total population at risk
pop_at_risk = master[master["Risk_Tier"].isin(["HIGH","CRITICAL"])]["TotalPopulation"].sum()
fig.text(0.99, 0.02,
         f"Population in HIGH/CRITICAL tracts: {pop_at_risk:,.0f}",
         ha="right", fontsize=8, color="#555")

plt.suptitle("Virginia Healthcare Desert Analysis — CDC PLACES 2025 + HRSA Validation",
             fontsize=13, fontweight="bold", y=1.01)

out = os.path.join(OUTPUT_DIR, "equity_analysis.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
print("Opening chart...")
plt.show()
print("\nScript 06 complete. Ready for Script 07 (CDS Trigger).")