import pandas as pd
import os

OUTPUT_DIR = r"C:\capstone\outputs"
DATA_DIR   = r"C:\capstone\data"

# ── Load your scored counties ──────────────────────────
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Healthcare_Deserts.csv"))
print(f"Your scored counties: {len(county)}")

# ── Load HRSA Primary Care HPSA data ──────────────────
print("Loading HRSA HPSA data...")
hrsa = pd.read_csv(
    os.path.join(DATA_DIR, "BCD_HPSA_FCT_DET_PC.csv"),
    low_memory=False, encoding="latin-1"
)
print(f"HRSA HPSA total rows: {len(hrsa):,}")

# ── Filter for Virginia, active, Primary Care ─────────
va_hpsa = hrsa[
    (hrsa["Common State Name"].str.strip() == "Virginia") &
    (hrsa["HPSA Status"].str.strip() == "Designated") &
    (hrsa["HPSA Discipline Class"].str.strip() == "Primary Care")
].copy()
print(f"Virginia active Primary Care HPSAs: {len(va_hpsa)}")

# ── Print HPSA column names so we can find county field ─
print("\nHRSA columns available:")
print([c for c in hrsa.columns if "county" in c.lower() or "name" in c.lower()])

# ── Clean county names for matching ───────────────────
def clean_county(name):
    if pd.isna(name): return ""
    name = str(name).strip()
    for suffix in [" County"," city"," City"," (Independent City)",
                   " Town"," town"]:
        name = name.replace(suffix, "")
    return name.strip().lower()

# Try the most common HRSA county column names
county_col = None
for col in ["County Equivalent Name","County Name","Common County Name",
            "HPSA County Name","county_name"]:
    if col in va_hpsa.columns:
        county_col = col
        break

if county_col is None:
    print("\nCould not auto-detect county column.")
    print("All HRSA columns:", list(va_hpsa.columns))
else:
    print(f"\nUsing HRSA county column: '{county_col}'")

    va_hpsa["county_clean"] = va_hpsa[county_col].apply(clean_county)
    county["county_clean"]  = county["CountyName"].apply(clean_county)

    hpsa_counties = set(va_hpsa["county_clean"].unique())
    print(f"Unique HPSA-designated counties: {len(hpsa_counties)}")
    print(f"Sample HPSA counties: {list(hpsa_counties)[:8]}")

    # ── Match ──────────────────────────────────────────
    county["Is_HPSA"] = county["county_clean"].isin(hpsa_counties)
    print(f"\nYour counties matched as HPSA: {county['Is_HPSA'].sum()}")

    # ── Confusion Matrix ───────────────────────────────
    your_high = county["Risk_Tier"].isin(["HIGH","CRITICAL"])
    hrsa_pos  = county["Is_HPSA"]

    tp = int((your_high  & hrsa_pos).sum())   # you said HIGH, HRSA agrees
    fp = int((your_high  & ~hrsa_pos).sum())  # you said HIGH, HRSA disagrees
    fn = int((~your_high & hrsa_pos).sum())   # you said LOW/MOD, HRSA says shortage
    tn = int((~your_high & ~hrsa_pos).sum())  # both agree: not a desert

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv         = tp / (tp + fp) if (tp + fp) > 0 else 0

    print("\n" + "="*55)
    print("HRSA VALIDATION RESULTS")
    print("="*55)
    print(f"  True Positives  (you=HIGH,  HRSA=shortage): {tp}")
    print(f"  False Positives (you=HIGH,  HRSA=ok):       {fp}")
    print(f"  False Negatives (you=LOW,   HRSA=shortage): {fn}")
    print(f"  True Negatives  (you=LOW,   HRSA=ok):       {tn}")
    print(f"\n  Sensitivity (recall):          {sensitivity:.1%}")
    print(f"  Specificity:                   {specificity:.1%}")
    print(f"  Positive Predictive Value:     {ppv:.1%}")

    if sensitivity >= 0.70:
        print("\n  STRONG RESULT — your model catches 70%+ of federal deserts")
    elif sensitivity >= 0.50:
        print("\n  MODERATE RESULT — your model catches majority of federal deserts")
    else:
        print("\n  NOTE — lower sensitivity. See false negatives below.")

    # ── Show what your model caught vs missed ──────────
    print("\n── Counties YOUR model flagged HIGH/CRITICAL ────────")
    caught = county[your_high][["CountyName","Healthcare_Desert_Score",
                                 "Risk_Tier","Is_HPSA"]]
    caught = caught.rename(columns={"Is_HPSA":"HRSA_Confirmed"})
    print(caught.to_string(index=False))

    print("\n── HRSA-designated areas your model MISSED ──────────")
    missed = county[~your_high & hrsa_pos][["CountyName",
                    "Healthcare_Desert_Score","Risk_Tier"]]
    if len(missed) == 0:
        print("  None — perfect recall!")
    else:
        print(missed.to_string(index=False))
        print("\n  (These are candidates to review your threshold settings)")

    # ── Save validated file ────────────────────────────
    county.drop("county_clean", axis=1).to_csv(
        os.path.join(OUTPUT_DIR, "Virginia_Validated.csv"), index=False
    )
    print(f"\nSaved: Virginia_Validated.csv")
    print("Script 05 complete. Ready for Script 06 (Equity Analysis).")