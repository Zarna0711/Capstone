# Closing the Loop: Automated SDOH Screening via Geospatial Healthcare Desert Scores and FHIR Alerts

**Author:** Zarna Patel  
**Program:** MS Health Informatics — George Mason University  
**Preceptor:** Luis Belen, CEO | NHIT  

---

## Project Overview

Medical care accounts for only 10–20% of modifiable health outcomes — the remaining 80–90% are driven by social conditions like food insecurity, housing instability, and lack of insurance (Magnan, 2017). Yet most EHR systems treat a patient's home address as nothing more than a mailing label.

In Virginia, wealthy Northern Virginia suburbs sit alongside persistently underserved Southside and Appalachian communities. These disparities are often invisible to county-level data but become clear at the census tract level. CMS 2025 HRSN screening mandates now require healthcare organizations to screen for social needs — yet no automated tool exists to trigger that screening at the point of care.

This capstone closes that gap. A weighted Healthcare Desert Score built from CDC PLACES 2025 data across Virginia's 2,166 census tracts triggers real-time CDS Hooks alerts at patient intake — auto-generating ICD-10 Z-codes and FHIR referrals, reaching 1,148,341 Virginians with zero additional clinician burden.

---

## Repository Structure

```
capstone/
├── scripts/          # All Python scripts 
│   ├── 01_load_data.py
│   ├── 02_extract_sdoh.py
│   ├── 03_master_table.py
│   ├── 04_risk_score.py
│   ├── 05_hrsa_validate.py
│   ├── 06_equity_analysis.py
│   └── 07_cds_trigger.py
├── charts/           # Generated poster visualizations (PNG)
├── maps/             # Interactive choropleth map outputs
├── outputs/          # Scored CSV outputs
└── data/             # NOT INCLUDED — see Data Sources below
```

---

## Data Sources

The `data/` folder is not included in this repository due to file size. Download the required files from these free public sources and place them in a folder called `data/` in the root of this project.

| File | Source | Direct Link |
|---|---|---|
| CDC PLACES 2025 Census Tract Data | CDC | https://chronicdata.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-Census-Tract-D/cwsq-ngmh |
| HRSA HPSA Primary Care (BCD_HPSA_FCT_DET_PC.csv) | HRSA Data Warehouse | https://data.hrsa.gov/data/download |
| US Census TIGER/Line Shapefiles 2025 | Census Bureau | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html |

---

## How to Run

### Requirements

```
pip install pandas numpy matplotlib folium geopandas requests
```

### Run Scripts in Order

```
python scripts/01_load_data.py
python scripts/02_extract_sdoh.py
python scripts/03_master_table.py
python scripts/04_risk_score.py
python scripts/05_hrsa_validate.py
python scripts/06_equity_analysis.py
python scripts/07_cds_trigger.py
```

Each script saves its output to the `outputs/` folder and the next script reads from it. Run them in order for the pipeline to work correctly.

---

## Pipeline Overview

```
CDC PLACES 2025
      ↓
SDOH Extraction (8 measures)
      ↓
Master Table (2,166 census tracts)
      ↓
Weighted Healthcare Desert Score
      ↓
HRSA HPSA Validation
      ↓
Equity Analysis
      ↓
FHIR CDS Trigger + SDOH Alerts
```

---

## Key Results

| Metric | Result |
|---|---|
| Census tracts scored | 2,166 |
| Virginia counties ranked | 129 |
| CRITICAL deserts identified | 146 tracts |
| HIGH risk tracts | 167 tracts |
| Population in HIGH/CRITICAL tracts | 1,148,341 |
| HRSA Validation Specificity | 100% |
| HRSA Validation PPV | 100% |
| Sensitivity | 8.7% (threshold conservative) |
| Weighted vs equal-weight correlation | r = 0.991 |

---

## Indicator Weights

Weights assigned based on published literature (AHRQ 2023, Gravity Project, CDC HRSN 2025).

| Indicator | Weight | Source |
|---|---|---|
| Insurance Gap | 25% | AHRQ 2023 — strongest predictor of preventive care avoidance |
| Low Checkups | 20% | Direct outcome measure of access failure |
| Food Insecurity | 15% | Gravity Project — economic stability domain |
| Housing Instability | 12% | Gravity Project — neighborhood environment domain |
| Loneliness | 10% | CDC HRSN 2025 — social isolation |
| Transport Barriers | 8% | CDC HRSN 2025 — new 2025 variable |
| Utility Threat | 5% | CDC HRSN 2025 — new 2025 variable |
| Food Stamps | 5% | Proxy measure for economic need |

---

## Risk Tier Thresholds

| Tier | Score Range | Tracts | Action |
|---|---|---|---|
| CRITICAL | ≥ 22.0 | 146 | Automated social work referral + 7-day FHIR Task |
| HIGH | 19.0 – 21.9 | 167 | CDS alert — initiate PRAPARE screening |
| MODERATE | 16.0 – 18.9 | 391 | Warning — review social history |
| LOW | < 16.0 | 1,462 | Standard care |

---

## Standards Used

- HL7 FHIR R4 — Gravity Project SDOH Clinical Care IG v2.3.0
- CDS Hooks — patient-view trigger
- ICD-10-CM Z-codes — social determinant documentation
- SNOMED-CT — condition coding
- LOINC 71802-3 — PRAPARE screening panel
- CDC PLACES 2025 HRSN variables

---

## Limitations

- CDC PLACES values are model-estimated prevalences, not direct survey counts
- County-level HRSA matching may miss sub-county population HPSAs
- Sensitivity of 8.7% reflects a conservative HIGH threshold — MODERATE counties scoring 16–19 are also federally confirmed shortage areas
- Prototype only — not yet deployed in a production EHR environment

---

## References

1. Magnan S. Social determinants of health 101 for health care: Five plus five. NAM Perspectives. 2017. doi:10.31478/201710c
2. World Health Organization. Social determinants of health. https://www.who.int/health-topics/social-determinants-of-health. Accessed April 2025.
3. Office of Disease Prevention and Health Promotion. Healthy People 2030: Social determinants of health. U.S. Department of Health and Human Services. 2025.
4. Agency for Healthcare Research and Quality. Medical Expenditure Panel Survey. 2023.
5. HL7 Gravity Project. SDOH Clinical Care Implementation Guide v2.3.0. 2024. https://hl7.org/fhir/us/sdoh-clinicalcare/

---

## Acknowledgements

I sincerely thank my professor, Dr. Eman Elashkar, and my preceptor Luis Belen and team NHIT for constant guidance, support and encouragement throughout this project.

---

## Contact

**Zarna Patel**  
MS Health Informatics — George Mason University  
Email: zpatel3@gmu.edu
