import pandas as pd
import os

OUTPUT_DIR = r"C:\capstone\outputs"

# ── Load Virginia data from Step 1 ────────────────────
print("Loading Virginia data...")
va = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Full_Data.csv"),
                 low_memory=False)
print(f"Loaded: {len(va):,} rows")

# ── FIRST: Print ALL measures to see what exists ──
print("\n" + "="*55)
print("ALL MEASURES IN DATA:")
print("="*55)
all_measures = sorted(va["Short_Question_Text"].dropna().unique())
for m in all_measures:
    print(f"  {m}")
print(f"\nTotal measures: {len(all_measures)}")
print("="*55 + "\n")

# ── SDOH Measure Mapping ──────────────────────────────

MEASURE_MAP = {
    "Checkups":           "Annual Checkup",
    "Insurance_Gap":      "Health Insurance",
    "Depression":         "Depression",
    "Food_Insecurity":    "Food Insecurity",
    "Food_Stamps":        "Food Stamps",
    "Housing_Insecure":   "Housing Insecurity",
    "Loneliness":         "Loneliness",
    "Transport_Barriers": "Transportation Barriers",
    "Utility_Threat":     "Utility Services Threat",
    "Disability":         "Any Disability",
}

# ── Extract each measure ──────────────────────────────
rows = []
print("Extracting SDOH measures:")
print("-" * 40)

for measure_name, keyword in MEASURE_MAP.items():
    subset = va[
        va["Short_Question_Text"].str.contains(
            keyword, case=False, na=False
        )
    ].copy()
    subset["Measure_Name"] = measure_name

    if len(subset) == 0:
        print(f"  WARNING: '{measure_name}' not found (keyword: '{keyword}')")
        print(f"           Check the measure list above and update the keyword")
    else:
        print(f"  OK: {measure_name:20s} — {len(subset):,} rows found")
        rows.append(subset)

# ── Combine and save ──────────────────────────────────
if len(rows) == 0:
    print("\nERROR: No measures found at all. Check keyword spelling.")
else:
    sdoh = pd.concat(rows, ignore_index=True)

    key_cols = [
        "CountyName", "LocationID", "TotalPopulation",
        "Short_Question_Text", "Data_Value", "Measure_Name"
    ]
    # Only keep columns that actually exist
    key_cols = [c for c in key_cols if c in sdoh.columns]
    sdoh = sdoh[key_cols]

    out = os.path.join(OUTPUT_DIR, "Virginia_SDOH_Selected.csv")
    sdoh.to_csv(out, index=False)

    print(f"\nTotal SDOH rows extracted: {len(sdoh):,}")
    print(f"Measures successfully extracted: {sdoh['Measure_Name'].nunique()}")
    print(f"Unique tracts covered: {sdoh['LocationID'].nunique():,}")
    print(f"\nSaved: {out}")
    print("\nMeasure breakdown:")
    print(sdoh.groupby("Measure_Name")["Data_Value"]
              .agg(["count","mean","min","max"])
              .round(1).to_string())
