import pandas as pd
import os

OUTPUT_DIR = r"C:\capstone\outputs"
DATA_DIR   = r"C:\capstone\data"

TRIAL_DIR = r"C:\capstone\outputs\trial_threshold_sweep"
os.makedirs(TRIAL_DIR, exist_ok=True)

print("=" * 65)
print("THRESHOLD SWEEP: Testing multiple score cutoffs side by side")
print(f"Results saved to: {TRIAL_DIR}")
print("=" * 65)

# ── Load data ──────────────────────────────────────────────────────────
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Healthcare_Deserts.csv"))
print(f"\nScored counties loaded: {len(county)}")

hrsa = pd.read_csv(
    os.path.join(DATA_DIR, "BCD_HPSA_FCT_DET_PC.csv"),
    low_memory=False, encoding="latin-1"
)
va_hpsa = hrsa[
    (hrsa["Common State Name"].str.strip() == "Virginia") &
    (hrsa["HPSA Status"].str.strip() == "Designated") &
    (hrsa["HPSA Discipline Class"].str.strip() == "Primary Care")
].copy()

# ── Clean & match counties ─────────────────────────────────────────────
def clean_county(name):
    if pd.isna(name): return ""
    name = str(name).strip()
    for suffix in [" County", " city", " City", " (Independent City)",
                   " Town", " town"]:
        name = name.replace(suffix, "")
    return name.strip().lower()

county_col = None
for col in ["County Equivalent Name", "County Name", "Common County Name",
            "HPSA County Name", "county_name"]:
    if col in va_hpsa.columns:
        county_col = col
        break

va_hpsa["county_clean"] = va_hpsa[county_col].apply(clean_county)
county["county_clean"]  = county["CountyName"].apply(clean_county)
hpsa_counties           = set(va_hpsa["county_clean"].unique())
county["Is_HPSA"]       = county["county_clean"].isin(hpsa_counties)
hrsa_pos                = county["Is_HPSA"]

print(f"HRSA-designated counties matched: {hrsa_pos.sum()}")
print(f"Score range in your data: {county['Healthcare_Desert_Score'].min():.2f} "
      f"— {county['Healthcare_Desert_Score'].max():.2f}")

# ── Define thresholds to test ──────────────────────────────────────────
# Each entry: (label, minimum score to flag as a desert)
thresholds = [
    ("Original  (tiers HIGH+CRIT only)", None, ["HIGH", "CRITICAL"]),
    ("Trial 1   (tiers HIGH+CRIT+MOD)",  None, ["HIGH", "CRITICAL", "MODERATE"]),
    ("Cutoff 15.5  (score >= 15.5)",     15.5, None),
    ("Cutoff 15.0  (score >= 15.0)",     15.0, None),
    ("Cutoff 14.5  (score >= 14.5)",     14.5, None),
    ("Cutoff 14.0  (score >= 14.0)",     14.0, None),
    ("Cutoff 13.5  (score >= 13.5)",     13.5, None),
]

# ── Run sweep ──────────────────────────────────────────────────────────
records = []

for label, cutoff, tiers in thresholds:
    if tiers is not None:
        flagged = county["Risk_Tier"].isin(tiers)
    else:
        flagged = county["Healthcare_Desert_Score"] >= cutoff

    tp = int((flagged  &  hrsa_pos).sum())
    fp = int((flagged  & ~hrsa_pos).sum())
    fn = int((~flagged &  hrsa_pos).sum())
    tn = int((~flagged & ~hrsa_pos).sum())

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv         = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1          = (2 * ppv * sensitivity / (ppv + sensitivity)
                   if (ppv + sensitivity) > 0 else 0)

    records.append(dict(
        label=label, cutoff=cutoff,
        flagged=int(flagged.sum()),
        tp=tp, fp=fp, fn=fn, tn=tn,
        sensitivity=sensitivity,
        specificity=specificity,
        ppv=ppv,
        f1=f1,
    ))

results = pd.DataFrame(records)

# ── Print comparison table ─────────────────────────────────────────────
print("\n" + "=" * 90)
print("THRESHOLD SWEEP RESULTS")
print("=" * 90)
print(f"{'Threshold':<38} {'Flagged':>7} {'TP':>4} {'FP':>4} {'FN':>4} "
      f"{'Sens':>7} {'Spec':>7} {'Prec':>7} {'F1':>7}")
print("-" * 90)

for _, r in results.iterrows():
    print(f"{r['label']:<38} {r['flagged']:>7} {r['tp']:>4} {r['fp']:>4} {r['fn']:>4} "
          f"{r['sensitivity']:>6.1%} {r['specificity']:>6.1%} "
          f"{r['ppv']:>6.1%} {r['f1']:>6.1%}")

print("=" * 90)

# ── Find the sweet spot automatically ─────────────────────────────────
# Best F1 score balances sensitivity and precision
best_row = results.loc[results["f1"].idxmax()]
print(f"\n★  BEST F1 SCORE: '{best_row['label']}' — F1={best_row['f1']:.1%}, "
      f"Sensitivity={best_row['sensitivity']:.1%}, Precision={best_row['ppv']:.1%}")

# Best sensitivity without dropping precision below 80%
good_prec = results[results["ppv"] >= 0.80]
if len(good_prec) > 0:
    best_sens_row = good_prec.loc[good_prec["sensitivity"].idxmax()]
    print(f"★  BEST SENSITIVITY (Precision ≥ 80%): '{best_sens_row['label']}' — "
          f"Sensitivity={best_sens_row['sensitivity']:.1%}, "
          f"Precision={best_sens_row['ppv']:.1%}")

# ── Detailed breakdown for each score cutoff ───────────────────────────
print("\n" + "=" * 65)
print("DETAILED BREAKDOWN — Counties newly caught at each cutoff")
print("=" * 65)

score_cutoffs = [r for r in records if r["cutoff"] is not None]
prev_flagged  = county["Risk_Tier"].isin(["HIGH", "CRITICAL", "MODERATE"])

for r in score_cutoffs:
    cutoff  = r["cutoff"]
    flagged = county["Healthcare_Desert_Score"] >= cutoff
    newly_caught = county[flagged & ~prev_flagged & hrsa_pos]

    print(f"\n── Score >= {cutoff} — {r['flagged']} counties flagged "
          f"(Sensitivity {r['sensitivity']:.1%}, Precision {r['ppv']:.1%}) ──")

    if len(newly_caught) > 0:
        print(f"  Newly caught vs previous cutoff ({newly_caught.shape[0]} counties):")
        for _, row in newly_caught.iterrows():
            print(f"    {row['CountyName']:<22} score={row['Healthcare_Desert_Score']:.2f}  "
                  f"tier={row['Risk_Tier']}")
    else:
        print("  No new HRSA counties caught vs previous cutoff.")

    # Show false positives introduced
    new_fp = county[flagged & ~prev_flagged & ~hrsa_pos]
    if len(new_fp) > 0:
        print(f"  ⚠ New false positives introduced ({len(new_fp)}):")
        for _, row in new_fp.iterrows():
            print(f"    {row['CountyName']:<22} score={row['Healthcare_Desert_Score']:.2f}  "
                  f"tier={row['Risk_Tier']}")

    prev_flagged = flagged

# ── Save full sweep results table ──────────────────────────────────────
sweep_path = os.path.join(TRIAL_DIR, "threshold_sweep_summary.csv")
results.to_csv(sweep_path, index=False)
print(f"\nSweep summary saved to: {sweep_path}")

# ── Save county-level file with a column per cutoff ───────────────────
county_out = county.drop("county_clean", axis=1).copy()
county_out["Flagged_HighCrit"]     = county["Risk_Tier"].isin(["HIGH","CRITICAL"])
county_out["Flagged_HighCritMod"]  = county["Risk_Tier"].isin(["HIGH","CRITICAL","MODERATE"])
for cutoff in [15.5, 15.0, 14.5, 14.0, 13.5]:
    col = f"Flagged_{str(cutoff).replace('.','_')}"
    county_out[col] = county["Healthcare_Desert_Score"] >= cutoff

county_path = os.path.join(TRIAL_DIR, "Virginia_Threshold_Sweep.csv")
county_out.to_csv(county_path, index=False)
print(f"County-level sweep file saved to: {county_path}")
print("\nScript complete. Review the table above to pick your final cutoff.")
