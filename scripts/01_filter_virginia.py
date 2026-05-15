import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────
DATA_DIR   = r"C:\capstone\data"
OUTPUT_DIR = r"C:\capstone\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load the full CDC PLACES 2025 CSV ─────────────────

print("Loading CDC PLACES 2025... (this takes ~30 seconds)")
places_file = os.path.join(DATA_DIR, "PLACES_Census_Tract_2025.csv")
df = pd.read_csv(places_file, low_memory=False)
print(f"Loaded: {len(df):,} rows, {df.shape[1]} columns")

# ── Filter for Virginia ───────────────────────────────
va = df[df["StateAbbr"] == "VA"].copy()
va.reset_index(drop=True, inplace=True)
print(f"Virginia rows: {len(va):,}")
print(f"Virginia counties/cities: {va['CountyName'].nunique()}")

# ── Save ──────────────────────────────────────────────
out = os.path.join(OUTPUT_DIR, "Virginia_Full_Data.csv")
va.to_csv(out, index=False)
print(f"\nSaved: {out}")
print("Available measures:", va["Short_Question_Text"].unique()[:10])
