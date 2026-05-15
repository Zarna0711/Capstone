import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip
import os
import zipfile

DATA_DIR   = r"C:\capstone\data"
OUTPUT_DIR = r"C:\capstone\outputs"
MAPS_DIR   = r"C:\capstone\maps"
os.makedirs(MAPS_DIR, exist_ok=True)

# ── Load your scored + validated county data ───────────
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Validated.csv"))
print(f"County scores loaded: {len(county)} counties")

# ── Load shapefile ─────────────────────────────────────

shp_path = None

# Check which shapefile exists
candidates = [
    os.path.join(DATA_DIR, "tl_2025_us_county", "tl_2025_us_county.shp"),
    os.path.join(DATA_DIR, "tl_2022_51_county", "tl_2022_51_county.shp"),
]
for c in candidates:
    if os.path.exists(c):
        shp_path = c
        print(f"Shapefile found: {c}")
        break

# If ZIP not yet extracted, extract it automatically
if shp_path is None:
    zip_candidates = [
        os.path.join(DATA_DIR, "tl_2025_us_county.zip"),
        os.path.join(DATA_DIR, "tl_2022_51_county.zip"),
    ]
    for zp in zip_candidates:
        if os.path.exists(zp):
            extract_dir = zp.replace(".zip", "")
            os.makedirs(extract_dir, exist_ok=True)
            print(f"Extracting {zp}...")
            with zipfile.ZipFile(zp, "r") as z:
                z.extractall(extract_dir)
            for f in os.listdir(extract_dir):
                if f.endswith(".shp"):
                    shp_path = os.path.join(extract_dir, f)
                    print(f"Extracted: {shp_path}")
                    break
            if shp_path:
                break

if shp_path is None:
    print("ERROR: No shapefile found. Check C:\\capstone\\data\\")
    exit()

# ── Read and filter to Virginia ────────────────────────
print("Reading shapefile...")
gdf = gpd.read_file(shp_path)
print(f"Total counties in file: {len(gdf)}")
print(f"Columns: {list(gdf.columns)}")

# Virginia FIPS code is 51
if "STATEFP" in gdf.columns:
    gdf = gdf[gdf["STATEFP"] == "51"].copy()
elif "STUSPS" in gdf.columns:
    gdf = gdf[gdf["STUSPS"] == "VA"].copy()
print(f"Virginia counties in shapefile: {len(gdf)}")

# Convert to WGS84 for folium
gdf = gdf.to_crs(epsg=4326)

# ── Clean county names for merging ────────────────────
def clean_name(name):
    if pd.isna(name): return ""
    name = str(name).strip()
    for suffix in [" County"," city"," City"," (Independent City)",
                   " Town"," Independent City"]:
        name = name.replace(suffix, "")
    return name.strip()

gdf["name_clean"]    = gdf["NAME"].apply(clean_name)
county["name_clean"] = county["CountyName"].apply(clean_name)

# ── Merge scores into shapefile ────────────────────────
merged = gdf.merge(county, on="name_clean", how="left")
matched = merged["Healthcare_Desert_Score"].notna().sum()
print(f"Counties matched with scores: {matched}/{len(gdf)}")

if matched < 100:
    print("\nSample shapefile names:", list(gdf["NAME"].head(10)))
    print("Sample your names:", list(county["CountyName"].head(10)))

# Fill missing scores with state median for display
median_score = county["Healthcare_Desert_Score"].median()
merged["Healthcare_Desert_Score"] = merged["Healthcare_Desert_Score"].fillna(median_score)
merged["Risk_Tier"]  = merged["Risk_Tier"].fillna("UNKNOWN")
merged["Is_HPSA"]    = merged["Is_HPSA"].fillna(False)
merged["CountyName"] = merged["CountyName"].fillna(merged["NAME"])

# ── Build Folium map ───────────────────────────────────
print("\nBuilding interactive map...")
m = folium.Map(
    location=[37.5, -79.0],
    zoom_start=7,
    tiles="CartoDB positron",
    prefer_canvas=True
)

# Color scale — green (safe) to dark red (critical)
color_scale = folium.LinearColormap(
    colors=["#1D9E75","#F9CB42","#EF9F27","#D85A30","#A32D2D"],
    vmin=10,
    vmax=24,
    caption="Healthcare Desert Score (CDC PLACES 2025)"
)

def tier_color(score):
    if pd.isna(score): return "#cccccc"
    if score >= 22:    return "#A32D2D"
    if score >= 19:    return "#D85A30"
    if score >= 16:    return "#BA7517"
    return "#1D9E75"

# ── Choropleth layer ───────────────────────────────────
folium.GeoJson(
    merged,
    name="Healthcare Desert Score",
    style_function=lambda f: {
        "fillColor":   tier_color(f["properties"].get("Healthcare_Desert_Score")),
        "color":       "white",
        "weight":      0.8,
        "fillOpacity": 0.82,
    },
    highlight_function=lambda f: {
        "fillOpacity": 1.0,
        "weight":      2,
        "color":       "#333",
    },
    tooltip=GeoJsonTooltip(
        fields=["CountyName","Healthcare_Desert_Score","Risk_Tier",
                "Is_HPSA","Insurance_Gap","Food_Insecurity","Loneliness"],
        aliases=["County:","Desert Score:","Risk Tier:",
                 "HRSA Shortage:","Uninsured %:","Food Insecure %:","Lonely %:"],
        localize=True,
        sticky=True,
        style="""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 12px;
            font-family: sans-serif;
            font-size: 13px;
        """
    )
).add_to(m)

color_scale.add_to(m)

# ── Pin markers for top 5 critical/high counties ───────
top5 = county.head(5)
TIER_ICONS = {
    "CRITICAL": ("red",   "!!!"),
    "HIGH":     ("orange","!! "),
    "MODERATE": ("beige", " ! "),
    "LOW":      ("green", " OK"),
}

# Approximate centroids for top counties (lat/lon)
CENTROIDS = {
    "Hopewell":     (37.3043, -77.2872),
    "Petersburg":   (37.2279, -77.4019),
    "Emporia":      (36.6860, -77.5408),
    "Martinsville": (36.6918, -79.8728),
    "Danville":     (36.5860, -79.3950),
}

for _, row in top5.iterrows():
    cname = row["CountyName"]
    if cname in CENTROIDS:
        lat, lon = CENTROIDS[cname]
        tier = str(row["Risk_Tier"])
        icon_color, icon_text = TIER_ICONS.get(tier, ("gray","?"))
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<b>{cname}</b><br>"
                f"Score: {row['Healthcare_Desert_Score']:.2f}<br>"
                f"Tier: {tier}<br>"
                f"HRSA Confirmed: {row.get('Is_HPSA','?')}",
                max_width=200
            ),
            tooltip=f"{cname} — {tier}",
            icon=folium.Icon(color=icon_color, icon="info-sign")
        ).add_to(m)

# ── Legend panel ───────────────────────────────────────
legend_html = """
<div style="position:fixed;bottom:30px;left:30px;z-index:1000;
     background:white;padding:14px 18px;border-radius:10px;
     border:1px solid #ddd;font-family:sans-serif;font-size:13px;
     box-shadow:2px 2px 8px rgba(0,0,0,.12);">
  <div style="font-weight:bold;margin-bottom:8px;">Risk Tier</div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
    <div style="width:16px;height:16px;border-radius:3px;background:#A32D2D"></div>
    <span>CRITICAL (&ge; 22.0)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
    <div style="width:16px;height:16px;border-radius:3px;background:#D85A30"></div>
    <span>HIGH (19.0 – 21.9)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
    <div style="width:16px;height:16px;border-radius:3px;background:#BA7517"></div>
    <span>MODERATE (16.0 – 18.9)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
    <div style="width:16px;height:16px;border-radius:3px;background:#1D9E75"></div>
    <span>LOW (&lt; 16.0)</span>
  </div>
  <div style="margin-top:10px;font-size:11px;color:#888;">
    Source: CDC PLACES 2025 + HRSA Validation<br>
    Model: Gravity Project FHIR SDOH IG v2.3.0
  </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ── Title banner ───────────────────────────────────────
title_html = """
<div style="position:fixed;top:12px;left:50%;transform:translateX(-50%);
     z-index:1000;background:white;padding:10px 22px;border-radius:8px;
     border:1px solid #ddd;font-family:sans-serif;
     box-shadow:2px 2px 8px rgba(0,0,0,.12);text-align:center;">
  <div style="font-size:15px;font-weight:bold;color:#222;">
    Virginia Healthcare Desert Map
  </div>
  <div style="font-size:11px;color:#888;margin-top:2px;">
    CDC PLACES 2025 &nbsp;|&nbsp; HRSA Validated &nbsp;|&nbsp;
    Gravity Project FHIR &nbsp;|&nbsp; 2,166 census tracts
  </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# ── Save ───────────────────────────────────────────────
out = os.path.join(MAPS_DIR, "virginia_healthcare_deserts.html")
m.save(out)
print(f"\nMap saved: {out}")
print("Open this file in Chrome or Edge to view the interactive map.")
print("\nWhat you can do in the map:")
print("  - Hover over any county to see its score, tier, and SDOH indicators")
print("  - Click the red/orange pins for the top 5 worst counties")
print("  - Zoom in to see county boundaries clearly")
print("  - Screenshot it for your presentation slides")
print("\nScript 08 complete — all 8 scripts done!")
print("Your capstone pipeline is complete.")
