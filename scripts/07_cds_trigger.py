import pandas as pd
import json
import os
from datetime import datetime, timedelta

OUTPUT_DIR = r"C:\capstone\outputs"

master = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Master_Scored.csv"))
county = pd.read_csv(os.path.join(OUTPUT_DIR, "Virginia_Validated.csv"))
print(f"Loaded {len(master):,} tracts | {len(county)} counties")

# ── Find best Fairfax hidden desert tract automatically ─
fairfax = master[master["CountyName"].str.contains("Fairfax", na=False)].copy()
fairfax = fairfax.sort_values("Healthcare_Desert_Score", ascending=False)
if len(fairfax) > 0:
    best_fairfax_tract = str(fairfax.iloc[0]["LocationID"])
    best_fairfax_score = fairfax.iloc[0]["Healthcare_Desert_Score"]
    fairfax_county_mean = fairfax["Healthcare_Desert_Score"].mean()
    print(f"Fairfax county mean score:      {fairfax_county_mean:.2f} (LOW)")
    print(f"Highest Fairfax tract:          {best_fairfax_tract}")
    print(f"Highest Fairfax tract score:    {best_fairfax_score:.2f}")
    print(f"Hidden desert gap:              {best_fairfax_score - fairfax_county_mean:.2f} points")
else:
    best_fairfax_tract = None
    best_fairfax_score = 0
    fairfax_county_mean = 0
    print("WARNING: No Fairfax tracts found in master data")

# ══════════════════════════════════════════════════════
# GRAVITY PROJECT SDOH VALUE SETS
# Source: HL7 FHIR SDOH Clinical Care IG v2.3.0
# https://hl7.org/fhir/us/sdoh-clinicalcare/
# ══════════════════════════════════════════════════════

LOINC_CODES = {
    "prapare_panel":       "71802-3",
    "food_insecurity":     "88122-7",
    "housing_instability": "71802-3",
    "transport_need":      "93030-5",
    "utility_need":        "93038-8",
    "social_isolation":    "93029-7",
    "sdoh_assessment":     "96777-8",
}

SNOMED_CODES = {
    "food_insecurity":      "733423003",
    "housing_instability":  "32911000",
    "transport_problem":    "160695008",
    "social_isolation":     "422650009",
    "financial_insecurity": "454061000124102",
    "utility_insecurity":   "1148525003",
}

ICD10_ZCODES = {
    "food_insecurity":    "Z59.41",
    "housing_instability":"Z59.10",
    "transport_problems": "Z59.82",
    "utility_problems":   "Z59.89",
    "social_isolation":   "Z60.4",
    "lack_of_support":    "Z63.9",
}

GRAVITY_PROFILES = {
    "observation": "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-ObservationScreeningResponse",
    "condition":   "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition",
    "service_req": "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-ServiceRequest",
    "goal":        "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Goal",
    "task":        "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Task",
}

# ══════════════════════════════════════════════════════
# TIERED CLINICAL RESPONSE
# ══════════════════════════════════════════════════════

TIERS = {
    "CRITICAL": {
        "range":        (22.0, float("inf")),
        "icon":         "[!!!]",
        "cds_hook":     "patient-view",
        "action":       "Automated Social Work Referral. Mandatory PRAPARE. Document all Z-codes.",
        "gravity_step": ["Screen", "Assess", "Refer", "Goal"],
        "loinc":        [LOINC_CODES["prapare_panel"], LOINC_CODES["sdoh_assessment"]],
        "snomed":       [SNOMED_CODES["food_insecurity"], SNOMED_CODES["housing_instability"],
                         SNOMED_CODES["transport_problem"]],
        "icd10":        [ICD10_ZCODES["food_insecurity"], ICD10_ZCODES["housing_instability"],
                         ICD10_ZCODES["transport_problems"], ICD10_ZCODES["social_isolation"]],
        "fhir_resources": ["SDOHCCObservation", "SDOHCCCondition",
                           "SDOHCCServiceRequest", "SDOHCCGoal", "SDOHCCTask"],
        "cbo_referral": True,
    },
    "HIGH": {
        "range":        (19.0, 21.99),
        "icon":         "[!! ]",
        "cds_hook":     "patient-view",
        "action":       "CDS Alert: Initiate PRAPARE (LOINC 71802-3). Review and add Z-codes.",
        "gravity_step": ["Screen", "Assess"],
        "loinc":        [LOINC_CODES["prapare_panel"]],
        "snomed":       [SNOMED_CODES["food_insecurity"], SNOMED_CODES["housing_instability"]],
        "icd10":        [ICD10_ZCODES["food_insecurity"], ICD10_ZCODES["housing_instability"]],
        "fhir_resources": ["SDOHCCObservation", "SDOHCCCondition"],
        "cbo_referral": False,
    },
    "MODERATE": {
        "range":        (16.0, 18.99),
        "icon":         "[ ! ]",
        "cds_hook":     "patient-view",
        "action":       "Warning: Review social history. Consider Z-code documentation.",
        "gravity_step": ["Screen"],
        "loinc":        [LOINC_CODES["prapare_panel"]],
        "snomed":       [],
        "icd10":        [],
        "fhir_resources": ["SDOHCCObservation"],
        "cbo_referral": False,
    },
    "LOW": {
        "range":        (0, 15.99),
        "icon":         "[ OK]",
        "cds_hook":     None,
        "action":       "Standard care. No SDOH trigger required.",
        "gravity_step": [],
        "loinc":        [],
        "snomed":       [],
        "icd10":        [],
        "fhir_resources": [],
        "cbo_referral": False,
    },
}

# ══════════════════════════════════════════════════════
# LONGITUDINAL OVERRIDE — Professor Refinement #2
# If patient is LOW by geography but has not had an SDOH
# screen in over 12 months, override to trigger screening.
# In production: last_sdoh_screen_date queried from EHR
# via SMART on FHIR — Observation resources LOINC 71802-3
# ══════════════════════════════════════════════════════

def apply_longitudinal_override(summary, last_sdoh_screen_date=None):
    SCREEN_INTERVAL_DAYS = 365

    if summary.get("tier") not in ["LOW"]:
        return summary

    if last_sdoh_screen_date is None:
        days_since = float("inf")
    else:
        last = datetime.strptime(last_sdoh_screen_date, "%Y-%m-%d")
        days_since = (datetime.now() - last).days

    if days_since > SCREEN_INTERVAL_DAYS:
        days_str = "never" if days_since == float("inf") else f"{int(days_since)} days"
        summary["tier"]              = "LOW+OVERRIDE"
        summary["icon"]              = "[CLK]"
        summary["action"]            = (
            f"Standard care area — but last SDOH screen was "
            f"{days_str} ago (>{SCREEN_INTERVAL_DAYS} day threshold). "
            f"Trigger PRAPARE screening (LOINC 71802-3) to capture "
            f"individual-level risk not reflected in community score."
        )
        summary["loinc"]             = ["71802-3"]
        summary["override_reason"]   = "time_based_screening_override"
        summary["days_since_screen"] = days_str
        summary["fhir_resources"]    = ["SDOHCCObservation"]
        summary["gravity_steps"]     = ["Screen"]
    return summary


# ══════════════════════════════════════════════════════
# LOOKUP FUNCTIONS
# ══════════════════════════════════════════════════════

def get_county_score(county_name):
    """County-level score lookup — fallback method."""
    match = county[county["CountyName"].str.lower() == county_name.lower()]
    if len(match) == 0:
        return None, None
    row = match.iloc[0]
    return row["Healthcare_Desert_Score"], row.get("Is_HPSA", False)


def get_score_by_tract_or_county(county_name, tract_id=None):
    """
    MICRO-DESERT RESOLUTION — Professor Refinement #3

    Priority order:
    1. If tract_id provided — use exact census tract score (most precise)
    2. If only county_name — fall back to county mean

    This exposes Hidden Deserts inside low-risk counties.
    Example: Fairfax County mean = 13.11 (LOW)
             But a specific tract in Herndon may score HIGH.
             A patient there deserves a HIGH alert, not LOW.

    In production: tract_id comes from geocoding the patient
    address via the US Census Geocoder API, which returns a
    Census FIPS tract code from any street address in the US.
    API: https://geocoding.geo.census.gov/geocoder/
    """
    county_score, county_hpsa = get_county_score(county_name)

    # ── Try tract-level first ──────────────────────────
    if tract_id is not None:
        tract_match = master[
            master["LocationID"].astype(str) == str(tract_id)
        ]
        if len(tract_match) > 0:
            row = tract_match.iloc[0]
            tract_score = row["Healthcare_Desert_Score"]
            is_hpsa     = row.get("Is_HPSA", county_hpsa)
            return tract_score, is_hpsa, "tract", county_score
        else:
            print(f"  [TRACT LOOKUP] Tract {tract_id} not found "
                  f"— falling back to county mean")

    # ── Fallback to county mean ────────────────────────
    return county_score, county_hpsa, "county", county_score


def get_tier(score):
    for name, t in TIERS.items():
        lo, hi = t["range"]
        if lo <= score < hi:
            return name, t
    return "LOW", TIERS["LOW"]


# ══════════════════════════════════════════════════════
# FHIR BUNDLE BUILDER — Gravity Project Compliant
# ══════════════════════════════════════════════════════

def build_gravity_fhir_bundle(patient, address, county_name,
                               score, tier_name, tier, is_hpsa,
                               lookup_level, county_mean_score):
    now         = datetime.now().isoformat()
    patient_ref = f"Patient/{patient.replace(' ', '_')}"

    bundle = {
        "resourceType": "Bundle",
        "id": (f"sdoh-cds-{county_name.lower().replace(' ','-')}"
               f"-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
        "type":      "collection",
        "timestamp": now,
        "meta": {
            "profile": [
                "http://hl7.org/fhir/us/sdoh-clinicalcare/"
                "StructureDefinition/SDOHCC-Bundle"
            ]
        },
        "entry": []
    }

    # Resource 1: Screening Observation
    if LOINC_CODES["prapare_panel"] in tier["loinc"]:
        precision_note = (
            f"Tract-level precision lookup. "
            f"Tract score: {score} vs county mean: {county_mean_score:.2f}. "
            if lookup_level == "tract"
            else f"County-level lookup. County mean score: {score}. "
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [GRAVITY_PROFILES["observation"]]},
            "status": "preliminary",
            "category": [{
                "coding": [{
                    "system":  "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code":    "social-history",
                    "display": "Social History"
                }]
            }],
            "code": {
                "coding": [{
                    "system":  "http://loinc.org",
                    "code":    LOINC_CODES["prapare_panel"],
                    "display": "PRAPARE"
                }]
            },
            "subject":           {"reference": patient_ref},
            "effectiveDateTime": now,
            "valueQuantity": {
                "value":  score,
                "unit":   "Healthcare Desert Score",
                "system": "http://capstone.nhit.va/scoring",
            },
            "note": [{
                "text": (
                    f"Geospatial CDS trigger. County: {county_name}. "
                    f"Lookup level: {lookup_level}. "
                    f"{precision_note}"
                    f"HRSA HPSA confirmed: {is_hpsa}. "
                    f"Source: CDC PLACES 2025 + HRSA validation."
                )
            }]
        }
        bundle["entry"].append({"resource": observation})

    # Resource 2: SDOH Conditions (ICD-10 + SNOMED)
    for i, icd in enumerate(tier["icd10"]):
        snomed = tier["snomed"][i] if i < len(tier["snomed"]) else None
        condition_coding = [{
            "system":  "http://hl7.org/fhir/sid/icd-10-cm",
            "code":    icd,
            "display": icd
        }]
        if snomed:
            condition_coding.append({
                "system":  "http://snomed.info/sct",
                "code":    snomed,
                "display": f"SNOMED-CT {snomed}"
            })
        condition = {
            "resourceType": "Condition",
            "meta": {"profile": [GRAVITY_PROFILES["condition"]]},
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code":   "active"
                }]
            },
            "category": [{
                "coding": [{
                    "system":  "http://hl7.org/fhir/us/core/CodeSystem/condition-category",
                    "code":    "health-concern",
                    "display": "Health Concern"
                }]
            }],
            "code":    {"coding": condition_coding},
            "subject": {"reference": patient_ref},
            "onsetDateTime": now,
        }
        bundle["entry"].append({"resource": condition})

    # Resource 3: ServiceRequest → CBO (CRITICAL only)
    if tier["cbo_referral"]:
        service_request = {
            "resourceType": "ServiceRequest",
            "meta": {"profile": [GRAVITY_PROFILES["service_req"]]},
            "status": "active",
            "intent": "order",
            "category": [{
                "coding": [{
                    "system":  "http://snomed.info/sct",
                    "code":    "410606002",
                    "display": "Social service procedure"
                }]
            }],
            "code": {
                "coding": [{
                    "system":  "http://snomed.info/sct",
                    "code":    "410606002",
                    "display": "Referral to social worker"
                }]
            },
            "subject":    {"reference": patient_ref},
            "authoredOn": now,
            "note": [{"text": (
                f"CRITICAL desert referral. Score {score}. "
                f"County: {county_name}. "
                f"Refer to Community Based Organization for "
                f"food, housing, transport assistance."
            )}]
        }
        bundle["entry"].append({"resource": service_request})

    # Resource 4: Goal (CRITICAL + HIGH)
    if tier_name in ["CRITICAL", "HIGH"]:
        goal = {
            "resourceType": "Goal",
            "meta": {"profile": [GRAVITY_PROFILES["goal"]]},
            "lifecycleStatus": "active",
            "description": {
                "coding": [{
                    "system":  "http://snomed.info/sct",
                    "code":    "1078229009",
                    "display": "Improve access to healthcare services"
                }]
            },
            "subject":   {"reference": patient_ref},
            "startDate": datetime.now().strftime("%Y-%m-%d"),
            "note": [{"text": (
                f"SDOH goal: reduce healthcare desert burden. "
                f"Current score: {score}. Target: below 16.0."
            )}]
        }
        bundle["entry"].append({"resource": goal})

    # Resource 5: Task — Closed Loop 7-day verification (CRITICAL only)
    if tier["cbo_referral"]:
        deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        task = {
            "resourceType": "Task",
            "meta": {"profile": [GRAVITY_PROFILES["task"]]},
            "status":   "requested",
            "intent":   "order",
            "priority": "routine",
            "code": {
                "coding": [{
                    "system":  "http://hl7.org/fhir/CodeSystem/task-code",
                    "code":    "fulfill",
                    "display": "Fulfill the focal request"
                }]
            },
            "for":        {"reference": patient_ref},
            "authoredOn": now,
            "restriction": {
                "repetitions": 1,
                "period": {"end": deadline}
            },
            "businessStatus": {
                "coding": [{
                    "system":  (
                        "http://hl7.org/fhir/us/sdoh-clinicalcare/"
                        "CodeSystem/SDOHCC-CodeSystemTemporaryCodes"
                    ),
                    "code":    "waiting-for-response",
                    "display": "Waiting for CBO response"
                }]
            },
            "note": [{"text": (
                f"7-day follow-up rule: if Task status remains "
                f"'requested' after {deadline}, fire escalation "
                f"alert to Social Work team via CDS Hooks. "
                f"CBO platforms: findhelp.org, Unite Us, NowPow."
            )}]
        }
        bundle["entry"].append({"resource": task})

    return bundle


# ══════════════════════════════════════════════════════
# MAIN EVALUATION FUNCTION
# ══════════════════════════════════════════════════════

def evaluate_patient(patient_name, address, county_name,
                     last_screen_date=None, tract_id=None):

    score, is_hpsa, lookup_level, county_mean = get_score_by_tract_or_county(
        county_name, tract_id
    )

    if score is None:
        return None, {"error": f"County not found: {county_name}"}

    tier_name, tier = get_tier(score)

    fhir_bundle = build_gravity_fhir_bundle(
        patient_name, address, county_name,
        score, tier_name, tier, is_hpsa,
        lookup_level, county_mean
    )

    summary = {
        "patient":          patient_name,
        "county":           county_name,
        "score":            round(score, 2),
        "county_mean":      round(county_mean, 2) if county_mean else None,
        "lookup_level":     lookup_level,
        "tract_id":         tract_id,
        "tier":             tier_name,
        "icon":             tier["icon"],
        "action":           tier["action"],
        "gravity_steps":    tier["gravity_step"],
        "loinc":            tier["loinc"],
        "icd10":            tier["icd10"],
        "snomed":           tier["snomed"],
        "cbo_referral":     tier["cbo_referral"],
        "fhir_resources":   tier["fhir_resources"],
        "hrsa_confirmed":   bool(is_hpsa),
        "fhir_bundle_size": len(fhir_bundle["entry"]),
        "last_screen_date": last_screen_date,
    }

    # ── Longitudinal override — Professor Refinement #2 ─
    summary = apply_longitudinal_override(summary, last_screen_date)

    # ── Rebuild bundle if override fired ──────────────
    if summary.get("override_reason") == "time_based_screening_override":
        fhir_bundle["entry"].append({
            "resource": {
                "resourceType": "Observation",
                "meta": {"profile": [GRAVITY_PROFILES["observation"]]},
                "status": "preliminary",
                "code": {"coding": [{
                    "system":  "http://loinc.org",
                    "code":    "71802-3",
                    "display": "PRAPARE — longitudinal override triggered"
                }]},
                "subject": {
                    "reference": f"Patient/{patient_name.replace(' ','_')}"
                },
                "effectiveDateTime": datetime.now().isoformat(),
                "note": [{"text": (
                    f"Longitudinal override: patient in LOW-risk area "
                    f"({county_name}, score {score}) but last SDOH "
                    f"screen was {summary['days_since_screen']} ago. "
                    f"PRAPARE triggered per 12-month screening policy."
                )}]
            }
        })
        summary["fhir_bundle_size"] = len(fhir_bundle["entry"])

    return fhir_bundle, summary


# ══════════════════════════════════════════════════════
# TEST PATIENTS
# (name, address, county, last_screen_date, tract_id)
# tract_id=None  → county-level mean (fallback)
# tract_id=FIPS  → tract-level precision (micro-desert)
# ══════════════════════════════════════════════════════

test_patients = [
    ("James R.",  "412 N 2nd St",          "Hopewell",     None,         None),
    ("Maria L.",  "87 Old Town Rd",         "Petersburg",   None,         None),
    ("David K.",  "234 Main St",            "Harrisonburg", "2024-11-01", None),
    ("Sarah M.",  "1100 Wilson Blvd",       "Arlington",    "2023-03-15", None),
    ("Thomas B.", "55 County Road",         "Buchanan",     "2025-01-10", None),
    # ── Micro-Desert demo — Professor Refinement #3 ───
    # Fairfax county mean is LOW (~13) but specific tracts
    # in Herndon, Route 1 corridor score much higher.
    # tract_id auto-selected as highest-scoring Fairfax tract.
    ("Carlos V.", "13045 Elden St Herndon", "Fairfax",      None,
     best_fairfax_tract),
]

print("\n" + "="*65)
print("  VIRGINIA SDOH CDS — GRAVITY PROJECT FHIR R4 PROTOTYPE")
print("  HL7 SDOH Clinical Care IG v2.3.0 | CDS Hooks | LOINC")
print("  ICD-10-CM Z-codes | SNOMED-CT | Gravity Value Sets")
print("  + Longitudinal Override     (Prof. Refinement #2)")
print("  + Micro-Desert Tract Lookup (Prof. Refinement #3)")
print("  + Closed-Loop Task Resource (Prof. Refinement #4)")
print("="*65)

all_bundles   = []
all_summaries = []

for name, address, cty, last_screen, tract_id in test_patients:
    bundle, summary = evaluate_patient(
        name, address, cty,
        last_screen_date=last_screen,
        tract_id=tract_id
    )
    if bundle is None:
        print(f"\n  ERROR: {summary['error']}")
        continue

    all_bundles.append(bundle)
    all_summaries.append(summary)

    print(f"\n  {'─'*62}")
    print(f"  Patient:         {summary['patient']}")
    print(f"  Address:         {address}, {cty}, VA")
    print(f"  Desert Score:    {summary['score']:.2f}  "
          f"[{summary['lookup_level'].upper()} level]", end="")

    # Show hidden desert gap for tract-level lookups
    if (summary["lookup_level"] == "tract"
            and summary["county_mean"] is not None):
        gap = summary["score"] - summary["county_mean"]
        print(f"  ← county mean: {summary['county_mean']:.2f} "
              f"(hidden desert gap: +{gap:.2f})")
    else:
        print()

    print(f"  Last Screen:     {summary['last_screen_date'] or 'Never recorded'}")
    print(f"  {summary['icon']}  {summary['tier']} RISK")
    print(f"  Action:          {summary['action']}")

    if summary.get("gravity_steps"):
        print(f"  Gravity Steps:   {' → '.join(summary['gravity_steps'])}")
    if summary.get("loinc"):
        print(f"  LOINC:           {', '.join(summary['loinc'])}")
    if summary.get("icd10"):
        print(f"  ICD-10 Z-codes:  {', '.join(summary['icd10'])}")
    if summary.get("snomed"):
        print(f"  SNOMED-CT:       {', '.join(summary['snomed'])}")
    if summary.get("fhir_resources"):
        print(f"  FHIR Resources:  {', '.join(summary['fhir_resources'])}")
    if summary.get("override_reason"):
        print(f"  Override Reason: {summary['override_reason']}")
        print(f"  Days Since Screen:{summary['days_since_screen']}")

    print(f"  CBO Referral:    "
          f"{'YES — Social Work referral + 7-day Task created' if summary['cbo_referral'] else 'No'}")
    print(f"  HRSA Confirmed:  "
          f"{'YES — federally designated shortage area' if summary['hrsa_confirmed'] else 'No'}")
    print(f"  FHIR Bundle:     {summary['fhir_bundle_size']} resource(s) generated")

print(f"\n  {'─'*62}")
print(f"\n  BATCH SUMMARY — {len(all_summaries)} patients evaluated")
for tier in ["CRITICAL", "HIGH", "MODERATE", "LOW+OVERRIDE", "LOW"]:
    n    = sum(1 for s in all_summaries if s["tier"] == tier)
    icon = TIERS.get(tier, {}).get("icon", "[CLK]")
    if n > 0:
        print(f"  {icon}  {tier}: {n} patient(s)")

# ── Micro-desert summary ───────────────────────────────
carlos = next((s for s in all_summaries if s["patient"] == "Carlos V."), None)
if carlos and carlos["lookup_level"] == "tract":
    print(f"\n  MICRO-DESERT DEMONSTRATION:")
    print(f"  Carlos V. lives in Fairfax (county mean: "
          f"{carlos['county_mean']:.2f} — LOW)")
    print(f"  His specific tract scores: {carlos['score']:.2f} "
          f"— {carlos['tier']}")
    gap = carlos["score"] - carlos["county_mean"]
    print(f"  Hidden desert gap: +{gap:.2f} points")
    print(f"  Without tract-level lookup: would receive LOW alert")
    print(f"  With tract-level lookup:    receives {carlos['tier']} alert")
    print(f"  This is the Hidden Desert problem county models cannot solve.")

# ── Save FHIR bundles ──────────────────────────────────
output = {
    "meta": {
        "ig":        "HL7 FHIR SDOH Clinical Care IG v2.3.0",
        "gravity":   "https://hl7.org/fhir/us/sdoh-clinicalcare/",
        "generated": datetime.now().isoformat(),
        "patients":  len(all_summaries),
        "refinements": [
            "Gravity Project FHIR profiles (Point 1)",
            "Longitudinal 12-month screening override (Point 2)",
            "Tract-level micro-desert precision lookup (Point 3)",
            "7-day closed-loop SDOHCCTask resource (Point 4)",
        ]
    },
    "bundles": all_bundles
}

json_out = os.path.join(OUTPUT_DIR, "cds_gravity_fhir_bundles.json")
with open(json_out, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n  Gravity FHIR bundles saved: {json_out}")
print("  Script 07 complete — all professor refinements implemented.")