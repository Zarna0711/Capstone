import pandas as pd
import os

OUTPUT_DIR = r"C:\capstone\outputs"
DATA_DIR   = r"C:\capstone\data"

# ── TRIAL: Results go to a separate folder so originals are untouched ──
TRIAL_DIR = r"C:\capstone\outputs\trial_moderate_threshold"
os.makedirs(TRIAL_DIR, exist_ok=True)
print("=" * 60)
print("TRIAL RUN: Sensitivity threshold expanded to include MODERATE")
print(f"Results will be saved to: {TRIAL_DIR}")
print("=" * 60)

# ── Load your scored counties ──────────────────────────────────────────
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Healthcare_Deserts.csv"))
print(f"\nYour scored counties: {len(county)}")

# ── Load HRSA Primary Care HPSA data ──────────────────────────────────
print("Loading HRSA HPSA data...")
hrsa = pd.read_csv(
    os.path.join(DATA_DIR, "BCD_HPSA_FCT_DET_PC.csv"),
    low_memory=False, encoding="latin-1"
)
print(f"HRSA HPSA total rows: {len(hrsa):,}")

# ── Filter for Virginia, active, Primary Care ──────────────────────────
va_hpsa = hrsa[
    (hrsa["Common State Name"].str.strip() == "Virginia") &
    (hrsa["HPSA Status"].str.strip() == "Designated") &
    (hrsa["HPSA Discipline Class"].str.strip() == "Primary Care")
].copy()
print(f"Virginia active Primary Care HPSAs: {len(va_hpsa)}")

# ── Find county column ─────────────────────────────────────────────────
print("\nHRSA columns available:")
print([c for c in hrsa.columns if "county" in c.lower() or "name" in c.lower()])

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

    county["Is_HPSA"] = county["county_clean"].isin(hpsa_counties)
    print(f"\nYour counties matched as HPSA: {county['Is_HPSA'].sum()}")

    # ── Show tier distribution so you can see what changed ────────────
    print("\n── Risk Tier Distribution ───────────────────────────────────")
    print(county["Risk_Tier"].value_counts().to_string())

    # ────────────────────────────────────────────────────────────────────
    # RUN BOTH THRESHOLDS SIDE BY SIDE FOR COMPARISON
    # ────────────────────────────────────────────────────────────────────

    thresholds = {
        "ORIGINAL  (HIGH + CRITICAL only)":
            county["Risk_Tier"].isin(["HIGH", "CRITICAL"]),
        "TRIAL     (HIGH + CRITICAL + MODERATE)":
            county["Risk_Tier"].isin(["HIGH", "CRITICAL", "MODERATE"]),
    }

    hrsa_pos = county["Is_HPSA"]
    results  = {}

    for label, your_high in thresholds.items():
        tp = int((your_high  &  hrsa_pos).sum())
        fp = int((your_high  & ~hrsa_pos).sum())
        fn = int((~your_high &  hrsa_pos).sum())
        tn = int((~your_high & ~hrsa_pos).sum())

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv         = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1          = (2 * ppv * sensitivity / (ppv + sensitivity)
                       if (ppv + sensitivity) > 0 else 0)

        results[label] = dict(
            tp=tp, fp=fp, fn=fn, tn=tn,
            sensitivity=sensitivity,
            specificity=specificity,
            ppv=ppv,
            f1=f1,
            flagged=int(your_high.sum()),
        )

    # ── Print comparison table ─────────────────────────────────────────
    print("\n" + "=" * 65)
    print("THRESHOLD COMPARISON")
    print("=" * 65)
    header = f"{'Metric':<32} {'ORIGINAL':>14} {'TRIAL':>14}"
    print(header)
    print("-" * 65)

    orig  = results["ORIGINAL  (HIGH + CRITICAL only)"]
    trial = results["TRIAL     (HIGH + CRITICAL + MODERATE)"]

    rows = [
        ("Counties flagged",      orig["flagged"],      trial["flagged"]),
        ("True Positives  (TP)",  orig["tp"],           trial["tp"]),
        ("False Positives (FP)",  orig["fp"],           trial["fp"]),
        ("False Negatives (FN)",  orig["fn"],           trial["fn"]),
        ("True Negatives  (TN)",  orig["tn"],           trial["tn"]),
        ("Sensitivity (Recall)",  orig["sensitivity"],  trial["sensitivity"]),
        ("Specificity",           orig["specificity"],  trial["specificity"]),
        ("Precision (PPV)",       orig["ppv"],          trial["ppv"]),
        ("F1 Score",              orig["f1"],           trial["f1"]),
    ]

    for name, o_val, t_val in rows:
        if isinstance(o_val, float):
            print(f"{name:<32} {o_val:>13.1%} {t_val:>13.1%}")
        else:
            print(f"{name:<32} {o_val:>14} {t_val:>14}")

    print("=" * 65)

    # ── Interpretation ─────────────────────────────────────────────────
    sens_gain = trial["sensitivity"] - orig["sensitivity"]
    ppv_loss  = orig["ppv"] - trial["ppv"]

    print("\n── INTERPRETATION ───────────────────────────────────────────")
    print(f"  Sensitivity gain from adding MODERATE: +{sens_gain:.1%}")
    print(f"  Precision loss  from adding MODERATE: -{ppv_loss:.1%}")

    if sens_gain > 0.10 and ppv_loss < 0.20:
        print("\n  GOOD TRADE-OFF — meaningful sensitivity gain with")
        print("  acceptable precision loss. Consider keeping MODERATE.")
    elif sens_gain > 0.10 and ppv_loss >= 0.20:
        print("\n  MIXED TRADE-OFF — sensitivity improved significantly")
        print("  but precision dropped hard. May need score sub-filtering.")
    elif sens_gain <= 0.10:
        print("\n  MINIMAL GAIN — adding MODERATE barely moves sensitivity.")
        print("  The missed HRSA counties may score consistently LOW.")
        print("  Consider reviewing those counties' raw feature values.")

    # ── Detailed county tables (TRIAL threshold) ───────────────────────
    trial_high = county["Risk_Tier"].isin(["HIGH", "CRITICAL", "MODERATE"])

    print("\n── [TRIAL] Counties flagged HIGH / CRITICAL / MODERATE ──────")
    caught = county[trial_high][["CountyName", "Healthcare_Desert_Score",
                                  "Risk_Tier", "Is_HPSA"]].copy()
    caught = caught.rename(columns={"Is_HPSA": "HRSA_Confirmed"})
    caught = caught.sort_values("Healthcare_Desert_Score", ascending=False)
    print(caught.to_string(index=False))

    print("\n── [TRIAL] HRSA-designated areas still MISSED ───────────────")
    still_missed = county[~trial_high & hrsa_pos][
        ["CountyName", "Healthcare_Desert_Score", "Risk_Tier"]]
    if len(still_missed) == 0:
        print("  None — perfect recall with MODERATE threshold!")
    else:
        print(still_missed.to_string(index=False))
        print("\n  These counties score LOW despite HRSA designation.")
        print("  Check their raw feature values for data anomalies.")

    # ── Save trial output (separate file, originals untouched) ─────────
    trial_out = county.drop("county_clean", axis=1).copy()
    trial_out["Trial_Flagged"] = trial_high.values

    out_path = os.path.join(TRIAL_DIR, "Virginia_Validated_TRIAL_moderate.csv")
    trial_out.to_csv(out_path, index=False)
    print(f"\nSaved trial results to: {out_path}")
    print("\nYour original Virginia_Healthcare_Deserts.csv is UNCHANGED.")
    print("\nScript 05 TRIAL complete.")
    print("If the trade-off looks good, update Script 05 permanently.")
    print("Otherwise, Script 06 (Equity Analysis) can proceed with either file.")
