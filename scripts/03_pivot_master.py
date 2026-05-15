import pandas as pd
import os

OUTPUT_DIR = r"C:\capstone\outputs"

print("Loading SDOH selected data...")
sdoh = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_SDOH_Selected.csv"))
print(f"Loaded: {len(sdoh):,} rows, {sdoh['Measure_Name'].nunique()} measures")

# ── Pivot: long → wide ─────────────────────────────────
print("\nPivoting to wide format...")
master = sdoh.pivot_table(
    index=["CountyName", "LocationID", "TotalPopulation"],
    columns="Measure_Name",
    values="Data_Value",
    aggfunc="mean"
).reset_index()
master.columns.name = None

# ── Define SDOH columns AFTER pivot ───────────────────

sdoh_cols = [
    c for c in master.columns
    if c not in ["CountyName", "LocationID", "TotalPopulation"]
]
print(f"\nSDOH columns found after pivot: {sdoh_cols}")

# ── Formal Missing Value Analysis ─────────────────────
print("\n" + "="*55)
print("MISSING VALUE ANALYSIS")
print("="*55)

total_cells    = master.shape[0] * len(sdoh_cols)
missing_counts = master[sdoh_cols].isnull().sum()
missing_pct    = (missing_counts / len(master) * 100).round(2)

print(f"Total tracts:       {len(master):,}")
print(f"Total SDOH columns: {len(sdoh_cols)}")
print(f"Total data cells:   {total_cells:,}")
print(f"Missing cells:      {missing_counts.sum()}")
completeness = (1 - missing_counts.sum() / total_cells) * 100
print(f"Completeness rate:  {completeness:.2f}%\n")

if missing_counts.sum() == 0:
    print("Result: Dataset is 100% complete.")
    print("Reason: CDC PLACES uses model-based estimation,")
    print("        producing values for every qualifying tract.")
    print("        Tracts below 50 adult residents are excluded")
    print("        entirely rather than appearing as nulls.")
    print("        This means every row that exists has complete data.")
else:
    print("Missing values detected — breakdown by column:")
    for col in sdoh_cols:
        if missing_counts[col] > 0:
            print(f"  {col:<25} {missing_counts[col]:4d} tracts "
                  f"({missing_pct[col]:.1f}%)")

    print("\nMissing Value Strategy:")
    print("  Method: Available case analysis in weighted scoring.")
    print("  Logic:  Missing measures are excluded from the")
    print("          weighted calculation. Remaining weights")
    print("          renormalize to sum to 1.0 automatically.")
    print("  Flag:   Tracts with fewer than 3 valid measures")
    print("          are flagged as INSUFFICIENT_DATA and")
    print("          excluded from risk tier assignment.")

    # Count valid measures per tract
    master["Valid_Measure_Count"] = master[sdoh_cols].notna().sum(axis=1)

    # Flag insufficient tracts
    insufficient = master[master["Valid_Measure_Count"] < 3]
    if len(insufficient) > 0:
        print(f"\nWARNING: {len(insufficient)} tracts have fewer "
              f"than 3 valid measures — flagged as INSUFFICIENT_DATA")
        master.loc[
            master["Valid_Measure_Count"] < 3, "Risk_Tier"
        ] = "INSUFFICIENT_DATA"
    else:
        print("\n  No tracts flagged — all have sufficient data.")

    # Remove helper column before saving
    master.drop("Valid_Measure_Count", axis=1,
                errors="ignore", inplace=True)

# ── Report shape ───────────────────────────────────────
print(f"\nMaster table shape: {master.shape}")
print(f"Tracts (rows):      {len(master):,}")
print(f"Columns:            {list(master.columns)}")

# ── Final missing value check ──────────────────────────
print("\nFinal missing values per column:")
missing = master.isnull().sum()
if missing.sum() == 0:
    print("  None — all columns complete!")
else:
    print(missing[missing > 0])

# ── Save ───────────────────────────────────────────────
out = os.path.join(OUTPUT_DIR, "Virginia_Master_Analysis.csv")
master.to_csv(out, index=False)
print(f"\nSaved: {out}")

# ── Preview ────────────────────────────────────────────
print("\nFirst 3 tracts (preview):")
print(master[["CountyName", "Insurance_Gap", "Food_Insecurity",
              "Loneliness", "Transport_Barriers"]].head(3).to_string(index=False))
