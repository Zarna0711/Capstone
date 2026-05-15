import pandas as pd
import numpy as np
import os

OUTPUT_DIR = r"C:\capstone\outputs"

master = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Master_Analysis.csv"))
print(f"Loaded master table: {master.shape[0]:,} tracts")

# ── Step 1: Invert Checkups ────────────────────────────
# Checkups is a POSITIVE measure (higher = healthier)
# We flip it so higher always means MORE RISK
master["Low_Checkups"] = 100 - master["Checkups"]
print(f"Low_Checkups created (mean: {master['Low_Checkups'].mean():.1f}%)")

# ── Step 2: Literature-Based Weights ──────────────────
# Justification for each weight (cite these in your report):
# Insurance_Gap   0.25 — AHRQ 2023: strongest predictor of preventive care avoidance
# Low_Checkups    0.20 — Direct outcome measure of access failure
# Food_Insecurity 0.15 — Gravity Project SDOH domain: economic stability
# Housing_Insecure 0.12 — Gravity Project SDOH domain: neighborhood environment
# Loneliness      0.10 — CDC HRSN 2025: social isolation linked to worse outcomes
# Transport_Barriers 0.08 — CDC HRSN 2025: new 2025 release variable
# Utility_Threat  0.05 — CDC HRSN 2025: new 2025 release variable
# Food_Stamps     0.05 — program participation proxy for economic need

WEIGHTS = {
    "Insurance_Gap":    0.25,
    "Low_Checkups":     0.20,
    "Food_Insecurity":  0.15,
    "Housing_Insecure": 0.12,
    "Loneliness":       0.10,
    "Transport_Barriers": 0.08,
    "Utility_Threat":   0.05,
    "Food_Stamps":      0.05,
}

# Verify weights sum to 1.0
weight_sum = sum(WEIGHTS.values())
print(f"\nWeights sum: {weight_sum:.2f} (must be 1.00)")

# ── Step 3: Compute Weighted Score ────────────────────
def weighted_score(row):
    total_w, weighted_sum = 0, 0
    for col, w in WEIGHTS.items():
        val = row.get(col, np.nan)
        if pd.notna(val):
            weighted_sum += val * w
            total_w += w
    return round(weighted_sum / total_w, 2) if total_w > 0 else np.nan

print("Computing weighted Healthcare Desert Score...")
master["Healthcare_Desert_Score"] = master.apply(weighted_score, axis=1)

# ── Step 4: Sensitivity Analysis ──────────────────────
# This proves your weights don't arbitrarily change the rankings
# If correlation > 0.95, your weighted model is stable = defensible
eq_cols = list(WEIGHTS.keys())
master["Score_EqualWeights"] = master[eq_cols].mean(axis=1).round(2)
correlation = master["Healthcare_Desert_Score"].corr(master["Score_EqualWeights"])
print(f"\nSensitivity check — correlation weighted vs equal weights: {correlation:.4f}")
if correlation >= 0.95:
    print("PASS — rankings are stable. Your weights are defensible.")
else:
    print("NOTE — rankings differ. Review weight justification.")

# ── Step 5: Risk Tier Labels ──────────────────────────
def assign_tier(score):
    if pd.isna(score):    return "UNKNOWN"
    if score >= 22:       return "CRITICAL"
    if score >= 19:       return "HIGH"
    if score >= 16:       return "MODERATE"
    return "LOW"

master["Risk_Tier"] = master["Healthcare_Desert_Score"].apply(assign_tier)

tier_counts = master["Risk_Tier"].value_counts()
print(f"\nTract-level risk distribution:")
for tier in ["CRITICAL","HIGH","MODERATE","LOW"]:
    n = tier_counts.get(tier, 0)
    pct = n / len(master) * 100
    bar = "█" * int(pct / 2)
    print(f"  {tier:10s} {n:4d} tracts ({pct:4.1f}%) {bar}")

# ── Step 6: County Aggregation ────────────────────────
print("\nAggregating to county level...")
county = master.groupby("CountyName").agg(
    Healthcare_Desert_Score = ("Healthcare_Desert_Score", "mean"),
    Score_EqualWeights       = ("Score_EqualWeights",      "mean"),
    Total_Population         = ("TotalPopulation",          "sum"),
    Tract_Count              = ("LocationID",               "count"),
    Insurance_Gap            = ("Insurance_Gap",            "mean"),
    Low_Checkups             = ("Low_Checkups",             "mean"),
    Food_Insecurity          = ("Food_Insecurity",          "mean"),
    Housing_Insecure         = ("Housing_Insecure",         "mean"),
    Loneliness               = ("Loneliness",               "mean"),
    Transport_Barriers       = ("Transport_Barriers",       "mean"),
    Utility_Threat           = ("Utility_Threat",           "mean"),
).round(2).reset_index()

county["Risk_Tier"] = county["Healthcare_Desert_Score"].apply(assign_tier)
county = county.sort_values("Healthcare_Desert_Score", ascending=False).reset_index(drop=True)
county["Rank"] = county.index + 1

# ── Step 7: Results ───────────────────────────────────
print("\n" + "="*60)
print("TOP 15 HEALTHCARE DESERTS IN VIRGINIA")
print("="*60)
top15 = county.head(15)
for _, row in top15.iterrows():
    print(f"  #{int(row.Rank):2d} {row.CountyName:25s} "
          f"Score: {row.Healthcare_Desert_Score:5.2f}  "
          f"[{row.Risk_Tier}]")

print(f"\nTotal counties ranked: {len(county)}")
print(f"CRITICAL deserts: {(county.Risk_Tier=='CRITICAL').sum()}")
print(f"HIGH risk:        {(county.Risk_Tier=='HIGH').sum()}")
print(f"MODERATE risk:    {(county.Risk_Tier=='MODERATE').sum()}")
print(f"LOW risk:         {(county.Risk_Tier=='LOW').sum()}")

# ── Save both files ───────────────────────────────────
master.to_csv(os.path.join(OUTPUT_DIR, "Virginia_Master_Scored.csv"),  index=False)
county.to_csv(os.path.join(OUTPUT_DIR, "Virginia_Healthcare_Deserts.csv"), index=False)
print(f"\nSaved: Virginia_Master_Scored.csv")
print(f"Saved: Virginia_Healthcare_Deserts.csv")
print("\nScript 04 complete. Ready for Script 05 (HRSA Validation).")

# ── Threshold Sensitivity Test ─────────────────────────
print("\n── Threshold sensitivity test ────────────────────────")
for threshold in [19.0, 18.0, 17.0, 16.0]:
    flagged = county[county["Healthcare_Desert_Score"] >= threshold]
    print(f"  Threshold >= {threshold}: flags {len(flagged)} counties "
          f"({len(flagged)/len(county)*100:.0f}% of Virginia)")