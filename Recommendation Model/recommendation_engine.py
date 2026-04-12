"""
Rule-Based Plant Disease Recommendation Engine
================================================

Takes four inputs:
  1. Disease      – class predicted by the image classification model
  2. Crop         – cotton or wheat
  3. Growth Stage – current growth stage of the crop
  4. Severity     – Mild | Moderate | Severe

Returns evidence-based remedies tailored to the specific growth stage and
severity level, drawn exclusively from peer-reviewed and institutional sources.

Knowledge Sources
-----------------
- ICAR   – Indian Council of Agricultural Research
- PAU    – Punjab Agricultural University
- CIMMYT – International Maize and Wheat Improvement Center
- FAO    – Food and Agriculture Organization
- CICR   – Central Institute for Cotton Research
- TNAU   – Tamil Nadu Agricultural University
- USDA   – United States Department of Agriculture
- CABI   – Centre for Agriculture and Bioscience International
- MoAFW  – Ministry of Agriculture and Farmers Welfare, Government of India
- DPPQS  – Directorate of Plant Protection, Quarantine and Storage
- Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)
- Agrios G.N. – Plant Pathology (Academic Press)
- Schumann G.L. & D'Arcy C.J. – Essential Plant Pathology / Introduction to Plant Pathology
"""

from __future__ import annotations

import re
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Knowledge base sources
# ---------------------------------------------------------------------------

KNOWLEDGE_SOURCES: list[str] = [
    "Indian Council of Agricultural Research (ICAR)",
    "Punjab Agricultural University (PAU)",
    "International Maize and Wheat Improvement Center (CIMMYT)",
    "Food and Agriculture Organization (FAO)",
    "Central Institute for Cotton Research (CICR)",
    "Tamil Nadu Agricultural University (TNAU)",
    "United States Department of Agriculture (USDA)",
    "CABI – Centre for Agriculture and Bioscience International",
    "Ministry of Agriculture and Farmers Welfare, Government of India",
    "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
    "Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)",
    "Agrios G.N. – Plant Pathology (Academic Press)",
    "Schumann G.L. & D'Arcy C.J. – Essential Plant Pathology / Introduction to Plant Pathology",
]

# Alias kept for any external code that references the old name
_GENERAL_SOURCES = KNOWLEDGE_SOURCES

# ---------------------------------------------------------------------------
# Supported growth stages
# ---------------------------------------------------------------------------

COTTON_STAGES: list[str] = [
    "Small Plant",
    "Leaf Growth",
    "Bud Formation",
    "Flowering",
    "Boll Starting",
    "Boll Maturity",
]

WHEAT_STAGES: list[str] = [
    "Small Plant",
    "Tillering",
    "Stem Growth",
    "Booting",
    "Ear Formation / Flowering",
    "Grain Filling",
    "Harvest Ready",
]

# ---------------------------------------------------------------------------
# Stage normalization helpers
# ---------------------------------------------------------------------------

_COTTON_STAGE_MAP: dict[str, str] = {
    "small plant": "small_plant",
    "small_plant": "small_plant",
    "leaf growth": "leaf_growth",
    "leaf_growth": "leaf_growth",
    "bud formation": "bud_formation",
    "bud_formation": "bud_formation",
    "flowering": "flowering",
    "boll starting": "boll_starting",
    "boll_starting": "boll_starting",
    "boll maturity": "boll_maturity",
    "boll_maturity": "boll_maturity",
}

_WHEAT_STAGE_MAP: dict[str, str] = {
    "small plant": "small_plant",
    "small_plant": "small_plant",
    "tillering": "tillering",
    "stem growth": "stem_growth",
    "stem_growth": "stem_growth",
    "booting": "booting",
    "ear formation flowering": "ear_formation_flowering",
    "ear formation": "ear_formation_flowering",
    "ear_formation_flowering": "ear_formation_flowering",
    "flowering": "ear_formation_flowering",
    "grain filling": "grain_filling",
    "grain_filling": "grain_filling",
    "harvest ready": "harvest_ready",
    "harvest_ready": "harvest_ready",
}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def _normalize_stage_text(stage: str) -> str:
    text = str(stage).strip().lower()
    text = re.sub(r"[/_\\-]+", " ", text)
    return re.sub(r"\s+", " ", text)


def _stage_key(crop: str, stage: str) -> str:
    if not stage or stage == "Unknown":
        return "unknown"
    norm = _normalize_stage_text(stage)
    if crop == "cotton":
        return _COTTON_STAGE_MAP.get(norm, "unknown")
    if crop == "wheat":
        return _WHEAT_STAGE_MAP.get(norm, "unknown")
    return "unknown"


def _severity_key(severity: str) -> str:
    if not severity or severity == "Unknown":
        return "unknown"
    return str(severity).strip().lower()


# ---------------------------------------------------------------------------
# Wheat disease knowledge base
# Rules drawn from ICAR, PAU, CIMMYT, FAO, DPPQS, Murray et al., Agrios,
# MoAFW, and Schumann & D'Arcy.
# ---------------------------------------------------------------------------

WHEAT_DISEASES: dict[str, dict[str, Any]] = {

    "Black Rust(Stem Rust)": {
        "disease_name": "Black Rust (Stem Rust)",
        "causal_organism": "Puccinia graminis f. sp. tritici",
        "symptoms": [
            "Reddish-brown elongated pustules on stems and leaves",
            "Pustules turn dark brown to black at maturity",
            "Weakened, lodge-prone stems",
            "Severe infections lead to shrivelled grains and heavy yield loss",
        ],
        # Base remedies: always recommended regardless of stage or severity
        "base_remedies": [
            "Spray Propiconazole 25 EC (0.1%) at first appearance of pustules",
            "Alternatively apply Tebuconazole 25.9 EC at the recommended label dose",
            "Use stem-rust-resistant varieties (Sr31, Sr38, Sr24 gene lines per CIMMYT)",
            "Eliminate barberry (Berberis spp.) alternate hosts from field borders",
            "Monitor fields weekly from tillering to heading stage",
        ],
        # Stage-specific additions: keyed by normalised stage identifier
        "stage_remedies": {
            "small_plant": [
                "At small plant stage, scout lower leaves and stem bases for early rust pustules.",
                "If a few pustules are detected, apply Propiconazole at 50% label dose as an early preventive measure.",
            ],
            "tillering": [
                "Tillering is the optimal first spray window — apply Propiconazole (0.1%) immediately at first pustule sighting.",
                "A well-timed spray at tillering gives the highest return on investment for rust control (ICAR).",
            ],
            "stem_growth": [
                "At stem growth, inspect leaf sheaths and stem nodes for expanding pustule colonies.",
                "Apply a second Propiconazole or Tebuconazole spray if the first was applied at tillering and disease is progressing.",
            ],
            "booting": [
                "Booting is a critical stage — flag leaf loss at this point directly reduces grain filling.",
                "Use Azoxystrobin + Propiconazole (strobilurin + triazole mix) for extended protection if disease pressure is high.",
            ],
            "ear_formation_flowering": [
                "At ear formation and flowering, focus on protecting the spike from stem rust spread.",
                "Apply Tebuconazole as a late spray only if active pustules are visible on the upper two leaves.",
            ],
            "grain_filling": [
                "At grain filling, active pustules still threaten grain weight — treat if infection is spreading.",
                "Economic threshold at this stage: treat only if flag leaf > 10% pustule coverage.",
            ],
            "harvest_ready": [
                "At harvest-ready stage, chemical treatment is not economically justified.",
                "Remove and plough under infected crop residue immediately after harvest to reduce next-season inoculum.",
                "Plan to sow rust-resistant varieties next season.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild infection: a single well-timed Propiconazole spray is usually sufficient.",
                "Re-scout after 7 days to confirm the spread is contained.",
            ],
            "moderate": [
                "Moderate infection: schedule two sprays 10–14 days apart.",
                "Remove and destroy the most heavily infected tillers where practical.",
            ],
            "severe": [
                "URGENT — severe stem rust spreads very rapidly; begin treatment immediately.",
                "Apply a high-efficacy triazole + strobilurin combination fungicide and repeat in 10 days.",
                "Notify the local agricultural officer — severe outbreaks may require coordinated regional management.",
                "Destroy heavily infected plant debris immediately to limit further spread.",
            ],
        },
        "preventive_measures": [
            "Grow Sr-gene-resistant varieties as the single most cost-effective prevention (CIMMYT/ICAR).",
            "Follow early sowing calendar to avoid peak rust inoculum period for your region.",
            "Apply a prophylactic Propiconazole spray at tillering in historically high-risk years.",
            "Eradicate Berberis (barberry) plants within 1 km of the field.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },

    "BlackPoint": {
        "disease_name": "Black Point",
        "causal_organism": "Bipolaris sorokiniana / Alternaria alternata",
        "symptoms": [
            "Black or dark-brown discoloration at the embryo end of wheat grains",
            "Reduced grain test weight and commercial quality",
            "Can lower germination percentage when severely affected grain is used as seed",
        ],
        "base_remedies": [
            "Treat seeds with Carbendazim 50 WP (2 g/kg seed) or Thiram 75 WS before sowing",
            "Harvest at optimal grain moisture — below 14% — to prevent post-harvest fungal colonisation",
            "Dry grain promptly and store in well-ventilated conditions",
            "Avoid delayed harvesting in wet or humid weather",
        ],
        "stage_remedies": {
            "ear_formation_flowering": [
                "At flowering, apply preventive Mancozeb 75 WP (0.25%) spray if wet, humid conditions are forecast.",
                "Avoid overhead irrigation during and immediately after anthesis.",
            ],
            "grain_filling": [
                "At grain filling, maintain canopy airflow by avoiding excess irrigation.",
                "If black point incidence exceeds 5% on sampled grains, apply Mancozeb (0.25%) foliar spray.",
            ],
            "harvest_ready": [
                "Harvest promptly — delayed harvest under humid conditions accelerates fungal colonisation of grains.",
                "Dry harvested grain to below 14% moisture immediately.",
                "Store grain in cool, ventilated facilities to prevent further fungal development.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild incidence: no immediate field spray needed; focus on timely harvest and storage management.",
                "Apply seed treatment at next sowing to prevent inoculum carry-over.",
            ],
            "moderate": [
                "Moderate incidence: apply Mancozeb 75 WP (0.25%) at late grain filling stage.",
                "Plan seed lot replacement even if the crop appears partially recoverable.",
            ],
            "severe": [
                "URGENT — high black point incidence severely downgrades grain quality.",
                "Harvest unaffected field sections first to salvage quality grain.",
                "Bag and separate affected grain batches to prevent contaminating sound stock.",
                "Do not use grain from severely affected lots as seed without laboratory testing.",
            ],
        },
        "preventive_measures": [
            "Always use certified, treated seed; seed treatment is the most effective preventive option (PAU).",
            "Adopt timely sowing per ICAR/PAU regional calendar.",
            "Avoid excess irrigation during grain filling and maturity stages.",
            "Destroy infected crop residues after harvest to reduce soil inoculum.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Food and Agriculture Organization (FAO)",
            "Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)",
        ],
    },

    "FusariumFootRot": {
        "disease_name": "Fusarium Foot Rot",
        "causal_organism": "Fusarium graminearum / F. culmorum",
        "symptoms": [
            "Brown lesions at the stem base (crown and sub-crown internode)",
            "Premature wilting and white-head symptoms on individual tillers",
            "Honey-brown discoloration at the sub-crown internode on split stems",
            "Reduced tiller count and stand thinning in affected patches",
        ],
        "base_remedies": [
            "Treat seeds with Carbendazim 50 WP (2 g/kg seed) or Fludioxonil-based seed treatment before sowing",
            "Practice crop rotation — do not sow wheat after wheat for at least 2 consecutive seasons",
            "Maintain optimum sowing depth of 3–5 cm; avoid deep sowing",
            "Manage crop residue — incorporate or remove infected debris to reduce soil inoculum",
        ],
        "stage_remedies": {
            "small_plant": [
                "At small plant stage, examine stem bases for brown discoloration (crown rot).",
                "Remove and destroy infected seedlings where stand loss exceeds 10% per patch.",
                "Improve field drainage to reduce the moisture conditions that favour Fusarium.",
            ],
            "tillering": [
                "At tillering, scout for premature whitening of individual tillers (white-head symptom).",
                "Apply Carbendazim 50 WP soil drench (0.1% solution) around affected plant bases in mild outbreak patches.",
                "Avoid waterlogging — switch to furrow irrigation if overhead irrigation is currently being used.",
            ],
            "stem_growth": [
                "At stem growth, inspect lower internodes for spreading discoloration.",
                "Apply Trichoderma viride (talc formulation, 5 g per litre water) as a soil drench bio-control option.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild foot rot: targeted Carbendazim drench in affected patches, plus drainage improvement.",
            ],
            "moderate": [
                "Moderate: Carbendazim (0.1%) or Hexaconazole soil drench around plant bases.",
                "Remove and destroy affected plants to limit build-up of soil inoculum.",
                "Avoid overhead irrigation — switch to furrow or drip irrigation.",
            ],
            "severe": [
                "URGENT — severe foot rot may require complete patch removal and fungicide-treated re-sowing.",
                "Drench the entire affected section with Carbendazim (0.1%).",
                "Inform the local agricultural authority; high-inoculum fields threaten future wheat crops.",
                "Do not use grain from severely affected plants as seed.",
            ],
        },
        "preventive_measures": [
            "Systemic seed treatment with Fludioxonil or Carboxin + Thiram is the single most effective preventive step (ICAR, PAU).",
            "Rotate with non-cereal crops — pulses, oilseeds — for at least two seasons.",
            "Avoid excessive nitrogen fertilisation which creates lush but pathogen-susceptible growth.",
            "Thoroughly plough and incorporate infected crop residue after harvest.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Agrios G.N. – Plant Pathology (Academic Press)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },

    "HealthyPlant": {
        "disease_name": "Healthy Plant",
        "causal_organism": "None",
        "symptoms": [],
        "base_remedies": [
            "No disease treatment required at this time.",
            "Continue regular crop scouting every 7–10 days.",
            "Maintain balanced fertilisation (N-P-K as per soil test recommendations from ICAR/PAU).",
            "Follow the recommended irrigation schedule for the current growth stage.",
        ],
        "stage_remedies": {},
        "severity_remedies": {},
        "preventive_measures": [
            "Keep the field free of weeds that can harbour pest and disease vectors.",
            "Use certified disease-free seed every season.",
            "Maintain field records for early detection of any emerging disease pressure.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
        ],
    },

    "LeafBlight": {
        "disease_name": "Leaf Blight (Spot Blotch)",
        "causal_organism": "Bipolaris sorokiniana",
        "symptoms": [
            "Yellow to dark-brown oval or elliptical lesions on leaves",
            "Lesions may coalesce, causing extensive leaf blighting",
            "Premature leaf drying and reduced photosynthesis",
            "Olive-green to black sporulation visible on lesions under humid conditions",
        ],
        "base_remedies": [
            "Spray Mancozeb 75 WP (0.25%) at first symptom appearance",
            "Follow up with Propiconazole 25 EC (0.1%) if disease progresses beyond mild stage",
            "Ensure balanced fertilisation — avoid excess nitrogen that produces susceptible leaf tissue",
            "Remove and destroy infected crop debris after harvest",
        ],
        "stage_remedies": {
            "small_plant": [
                "Leaf blight can establish early in warm, humid conditions at the small plant stage.",
                "A preventive Mancozeb spray (0.25%) at this stage gives good protection where weather risk is high.",
            ],
            "tillering": [
                "Tillering is the most economically important spray window for leaf blight (ICAR/PAU).",
                "Apply Mancozeb at the first sign of lesions — protecting leaf area here secures final yield.",
            ],
            "stem_growth": [
                "At stem growth, apply a second Mancozeb spray if lesion density is increasing on lower and middle leaves.",
                "Ensure full canopy coverage during spray application.",
            ],
            "booting": [
                "At booting, switch to Propiconazole (0.1%) for better systemic protection of the flag leaf.",
                "Flag leaf protection at booting is critical — a healthy flag leaf is responsible for 30–40% of grain filling.",
            ],
            "ear_formation_flowering": [
                "At ear formation/flowering, Propiconazole spray protects emerging ear and upper leaves.",
                "Avoid spraying at peak anthesis to prevent interference with pollination.",
            ],
            "grain_filling": [
                "At grain filling, apply a final fungicide spray if the flag leaf is still under active infection.",
                "Focus on limiting spread to upper canopy — complete canopy coverage is essential.",
            ],
            "harvest_ready": [
                "At harvest-ready stage, further sprays are not economically justified.",
                "Plough under infected debris after harvest to reduce next-season soil inoculum.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild infection: a single Mancozeb spray is usually sufficient; scout again in 7 days.",
            ],
            "moderate": [
                "Moderate infection: two-spray programme with Mancozeb, followed by Propiconazole 14 days later.",
                "Remove badly affected lower leaves where practical to reduce local inoculum.",
            ],
            "severe": [
                "URGENT — severe leaf blight spreads rapidly under warm, humid conditions.",
                "Begin immediate Propiconazole spray; repeat in 10–12 days.",
                "Remove and burn heavily blighted leaves and infected plant debris.",
                "Review variety selection for next season and use spot-blotch-tolerant lines (ICAR recommendations).",
            ],
        },
        "preventive_measures": [
            "Use tolerant or resistant varieties per ICAR/PAU recommendations for your region.",
            "Maintain recommended plant spacing to ensure good air circulation within the canopy.",
            "Rotate with non-cereal crops to break the soil inoculum cycle.",
            "Apply Carbendazim seed treatment to reduce seedling leaf blight infection.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Food and Agriculture Organization (FAO)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },

    "Mildew": {
        "disease_name": "Powdery Mildew",
        "causal_organism": "Blumeria graminis f. sp. tritici",
        "symptoms": [
            "White to grey powdery fungal growth on leaf surfaces and sheaths",
            "May extend to stems and glumes under heavy pressure",
            "Reduced photosynthesis and grain shrivelling in severe cases",
            "Favoured by cool (10–20 °C), humid weather with moderate rainfall",
        ],
        "base_remedies": [
            "Spray wettable Sulfur 80 WP (0.3%) or Triadimefon 25 WP at first symptom appearance",
            "Use mildew-resistant/tolerant varieties as the primary management tool (CIMMYT/ICAR)",
            "Avoid excessive nitrogen fertilisation that promotes dense, susceptible leaf growth",
            "Maintain recommended plant spacing to maximise air circulation within the canopy",
        ],
        "stage_remedies": {
            "tillering": [
                "Tillering is a key early window — apply wettable Sulfur (0.3%) at the first sign of white powdery patches.",
                "Early control at tillering prevents rapid spread to upper leaves and the ear.",
            ],
            "stem_growth": [
                "At stem growth, mildew can move from lower to upper leaves rapidly under cool, humid conditions.",
                "Apply a second spray — Triadimefon or Propiconazole — if weather remains conducive and disease is spreading.",
            ],
            "booting": [
                "At booting, apply Triadimefon (0.1%) to protect the flag leaf — mildew on the flag leaf reduces grain filling.",
                "Do not delay spray beyond early booting if white powder is spreading upward through the canopy.",
            ],
            "ear_formation_flowering": [
                "At ear formation, mildew on spikes and glumes reduces grain quality.",
                "Apply Propiconazole (0.1%) if ear infection is developing; avoid spraying at peak anthesis.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild mildew: wettable sulfur spray combined with improved spacing and air circulation is usually sufficient.",
            ],
            "moderate": [
                "Moderate infection: apply Triadimefon or Propiconazole and repeat in 14 days.",
                "Remove heavily infected lower leaves to reduce local inoculum load.",
            ],
            "severe": [
                "URGENT — severe mildew at booting or heading can cause major yield reductions.",
                "Apply Propiconazole (0.1%) immediately; repeat in 10 days.",
                "Consider a strobilurin + triazole combination (Azoxystrobin + Propiconazole) for severe infection.",
                "Replace planted variety with mildew-resistant lines next season.",
            ],
        },
        "preventive_measures": [
            "Grow mildew-resistant varieties — the most cost-effective and sustainable prevention (CIMMYT, ICAR).",
            "Follow recommended sowing dates to avoid the highest-risk cool/humid periods.",
            "Apply a preventive wettable sulfur spray at early tillering in historically endemic locations.",
            "Maintain balanced N-P-K fertilisation; excess nitrogen increases susceptibility to mildew.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },

    "Smut": {
        "disease_name": "Loose Smut",
        "causal_organism": "Ustilago tritici",
        "symptoms": [
            "Grain heads replaced by masses of dark brown to black spores at heading",
            "Infected heads emerge slightly earlier than healthy heads",
            "Wind-dispersed black spore mass visible during head emergence",
            "After spore dispersal, a bare rachis remains on the infected plant",
        ],
        "base_remedies": [
            "Treat seeds with Carboxin 37.5% + Thiram 37.5% WS (2 g/kg seed) before sowing — systemic treatment penetrates the embryo",
            "Alternatively use Tebuconazole 2 DS (1.5 g/kg seed) as a highly effective systemic seed treatment",
            "Hot-water seed treatment (52 °C for exactly 10 minutes, then immediate cooling in cold water) as a chemical-free option",
            "Use certified smut-free seed from verified and reputable suppliers only",
        ],
        "stage_remedies": {
            "small_plant": [
                "At small plant stage, loose smut infection is already internal (seed-borne) — no effective field treatment exists at this point.",
                "Record the number of infected-looking seedlings and report to the seed supplier if certified seeds were used.",
            ],
            "ear_formation_flowering": [
                "At ear formation, smutted heads become visible — hand roguing is the only available field action.",
                "Remove smutted heads by hand into sealed polythene bags before wind disperses the spores to healthy flowering heads.",
                "Do not shake or disturb smutted heads during removal — spores will contaminate adjacent plants.",
            ],
            "harvest_ready": [
                "At harvest, separate any smutted grain lots from healthy grain — never use affected grain as seed.",
                "Clean and disinfect threshing equipment thoroughly before processing certified seed lots.",
                "The primary control for next season is systemic seed treatment — plan seed procurement accordingly.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild incidence (below 5% plants affected): rogue all visible smutted heads and plan seed treatment for next sowing.",
            ],
            "moderate": [
                "Moderate incidence: systematic roguing of all visible smutted heads before spore release.",
                "Replace seed stock entirely — source certified, systemically treated seed for the next season.",
            ],
            "severe": [
                "URGENT — severe loose smut represents seed stock failure and continued use will propagate the problem.",
                "Collect and destroy all smutted heads before any wind dispersal of spores.",
                "Report to the local agricultural extension office for variety replacement and recovery advice.",
                "Do not use any grain from this field as seed stock.",
            ],
        },
        "preventive_measures": [
            "Systemic seed treatment (Carboxin + Thiram or Tebuconazole) is the single most effective and economical preventive action (ICAR, PAU).",
            "Never use home-saved seed without fungicide treatment — loose smut is seed-borne.",
            "Purchase seed only from reputable certified sources.",
            "Keep seasonal field records of smut incidence to identify consistently high-risk plots.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Murray T.D., Parry D.W., & Cattlin N.D. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },

    "WheatBlast": {
        "disease_name": "Wheat Blast",
        "causal_organism": "Magnaporthe oryzae pathotype Triticum (MoT)",
        "symptoms": [
            "Bleached or white spikes — partial or complete head blanching",
            "Shrivelled, light-weight grains with poor milling and flour quality",
            "Rapid spike death progressing upward from an infected node",
            "Characteristic bleaching begins from the rachis node under warm, humid conditions",
        ],
        "base_remedies": [
            "Apply Trifloxystrobin 25% + Tebuconazole 50% SC (200 mL/ha) at flag leaf and heading stage",
            "Alternatively use Azoxystrobin + Propiconazole SC as a preventive spray at booting",
            "Adhere strictly to the recommended sowing window for your region — late sowing dramatically increases blast risk",
            "Remove infected crop residues immediately after harvest to reduce pathogen inoculum carry-over",
        ],
        "stage_remedies": {
            "booting": [
                "CRITICAL — booting is the most important preventive spray window for wheat blast (CIMMYT/FAO).",
                "Apply Trifloxystrobin + Tebuconazole at early booting before the flag leaf fully emerges.",
                "A missed booting spray cannot be fully compensated by later applications.",
            ],
            "ear_formation_flowering": [
                "At ear formation/flowering, blast can rapidly move into the spike.",
                "Apply the scheduled fungicide immediately if the booting spray was missed.",
                "Inspect spikes for bleaching from the base node upward — this is the characteristic blast symptom.",
                "Emergency spray: Tebuconazole 25.9 EC (0.1%) if spikes are actively bleaching.",
            ],
            "grain_filling": [
                "At grain filling, blast damage to affected spikes is irreversible.",
                "Focus on limiting spread to uninfected plants and plan early harvest if infection is widespread.",
            ],
            "harvest_ready": [
                "Harvest promptly — delayed harvest under humid conditions worsens grain quality loss.",
                "Burn or deeply plough all infected residue immediately after harvest.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild blast detected at booting: immediate preventive spray can still meaningfully limit spike infection.",
                "Scout all spikes carefully every 2–3 days — blast escalates extremely rapidly under warm, humid weather.",
            ],
            "moderate": [
                "Moderate blast: apply emergency Tebuconazole spray and assess harvested grain quality.",
                "Consider early harvest of sound sections to salvage grain quality.",
            ],
            "severe": [
                "URGENT — severe wheat blast has no curative option once extensive spike bleaching is present.",
                "Harvest all recoverable sections immediately; accept yield loss in badly blighted patches.",
                "Report the outbreak to local plant protection authorities (DPPQS) — blast is a notifiable disease in several regions.",
                "Do not use grain from affected areas as seed — Magnaporthe oryzae MoT is seed-transmissible.",
            ],
        },
        "preventive_measures": [
            "Use blast-resistant varieties where commercially available (consult CIMMYT/ICAR regional advisories).",
            "Follow the recommended sowing window strictly — late sowing is the strongest agronomic risk factor for wheat blast.",
            "Apply preventive strobilurin + triazole spray at late booting every season in blast-prone environments.",
            "Deep-plough or remove wheat residue after harvest to reduce volunteer-plant inoculum sources.",
            "Avoid late-season irrigation that raises canopy humidity during the heading and grain-filling stages.",
        ],
        "sources": [
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Food and Agriculture Organization (FAO)",
            "Agrios G.N. – Plant Pathology (Academic Press)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },

    "Yellow Rust(Leaf Rust)": {
        "disease_name": "Yellow Rust (Stripe Rust)",
        "causal_organism": "Puccinia striiformis f. sp. tritici",
        "symptoms": [
            "Yellow-orange pustules arranged in distinctive stripes along leaf veins",
            "Favoured by cool (8–15 °C), moist weather conditions",
            "Severe pre-heading infection causes 40–70% yield reduction",
            "Pustules extend to leaf sheaths and glumes under high epidemic pressure",
        ],
        "base_remedies": [
            "Spray Propiconazole 25 EC (0.1%) at the first clear appearance of yellow stripe pustules",
            "Apply Tebuconazole 25.9 EC as an alternative or follow-up fungicide",
            "Use stripe-rust-resistant varieties (Yr gene lines per CIMMYT/ICAR recommendations)",
            "Remove volunteer wheat plants near fields that carry over-season inoculum",
        ],
        "stage_remedies": {
            "small_plant": [
                "Yellow rust is uncommon at the small plant stage but can appear under cool, wet conditions.",
                "Scout lower leaf surfaces carefully for faint yellow stripe pustules in conducive weather.",
            ],
            "tillering": [
                "Tillering is the optimal first spray window — apply Propiconazole at the first clear stripe symptom (ICAR).",
                "Early control at tillering prevents exponential spread under cool morning dew conditions.",
            ],
            "stem_growth": [
                "Yellow rust can spread very rapidly at stem growth under cool weather.",
                "Apply a second spray (Propiconazole or Tebuconazole) if stripes are spreading from lower to upper leaves.",
            ],
            "booting": [
                "At booting, protect the flag leaf — yellow rust on the flag leaf is the highest single yield-loss risk.",
                "Apply Tebuconazole (0.1%) for deep systemic protection of the flag leaf and emerging ear.",
            ],
            "ear_formation_flowering": [
                "At ear formation, yellow rust on glumes reduces grain quality and filling.",
                "Late spray is justified only if active pustules are visible on the top two leaves.",
            ],
            "grain_filling": [
                "Yellow rust at grain filling still reduces final grain weight if upper leaves remain green and infected.",
                "Economic threshold: treat if > 5% of flag leaf area is covered by active pustules.",
            ],
            "harvest_ready": [
                "At harvest-ready stage, spray treatment is not economical.",
                "Plan variety replacement and a next-season preventive spray programme based on this season's outbreak severity.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild stripe rust: a single Propiconazole spray followed by scouting in 7 days is usually sufficient.",
            ],
            "moderate": [
                "Moderate infection: two-spray programme — Propiconazole followed by Tebuconazole 14 days later.",
                "Increase monitoring frequency to every 3–4 days in cool, moist weather periods.",
            ],
            "severe": [
                "URGENT — severe yellow rust can cause 40–70% yield loss if left uncontrolled (CIMMYT).",
                "Apply immediate systemic fungicide (Tebuconazole or Propiconazole + Azoxystrobin combination).",
                "Schedule the follow-up second spray within 10–12 days.",
                "Notify the local agricultural extension office for regional epidemic assessment.",
                "Plan an immediate switch to Yr-gene-resistant varieties for the coming season.",
            ],
        },
        "preventive_measures": [
            "Grow Yr-gene-resistant varieties — the most economical long-term solution (CIMMYT, ICAR).",
            "Apply prophylactic fungicide in endemic zones at early tillering stage.",
            "Monitor fields regularly during cool, moist periods — yellow rust is a weather-driven epidemic disease.",
            "Destroy volunteer wheat plants and susceptible grass hosts along field borders.",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Punjab Agricultural University (PAU)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },
}


# ---------------------------------------------------------------------------
# Cotton disease knowledge base
# Rules drawn from CICR, TNAU, USDA, CABI, MoAFW, DPPQS,
# Agrios, and Schumann & D'Arcy.
# ---------------------------------------------------------------------------

COTTON_DISEASES: dict[str, dict[str, Any]] = {

    "Bacterial Blight": {
        "disease_name": "Bacterial Blight",
        "causal_organism": "Xanthomonas citri subsp. malvacearum",
        "symptoms": [
            "Angular, water-soaked lesions on leaves bounded by veins",
            "Vein blackening — the 'black-arm' symptom on petioles and stems",
            "Lesions turn brown and necrotic; premature leaf drop in severe cases",
            "Circular water-soaked spots on bolls that turn dark and sunken",
        ],
        "base_remedies": [
            "Spray Copper Oxychloride 50 WP (0.3%) at first symptom appearance",
            "Use disease-free, certified resistant cotton seed varieties",
            "Practice crop rotation with non-host crops (cereals, legumes)",
            "Remove and destroy infected plant debris immediately",
            "Avoid overhead irrigation — use drip or furrow system to reduce bacterial splash dispersal",
        ],
        "stage_remedies": {
            "small_plant": [
                "Small plants are highly susceptible — scout cotyledons and first true leaves for water-soaked angular spots.",
                "Remove and destroy infected seedlings immediately to contain early-season spread.",
                "Apply protective Copper Oxychloride (0.3%) spray at first symptom appearance in the seedling field.",
            ],
            "leaf_growth": [
                "At leaf growth, apply Copper Oxychloride (0.3%) spray immediately at first lesion sighting.",
                "The first spray at leaf growth stage gives the best protection of young developing leaf area (CICR).",
            ],
            "bud_formation": [
                "Bacterial blight on upper stems and petioles at bud formation can cause boll shedding.",
                "Apply Copper Oxychloride and follow up with a second spray 10 days later if lesions are spreading.",
            ],
            "flowering": [
                "At flowering, protect bolls from bacterial infection — apply Copper Oxychloride carefully.",
                "Spray during cooler morning hours to avoid heat and spray stress on open flowers.",
            ],
            "boll_starting": [
                "Small developing bolls are susceptible to bacterial black-spot infection.",
                "Apply protective copper-based spray and continue monitoring boll surfaces for sunken dark spots.",
            ],
            "boll_maturity": [
                "At boll maturity, focus on limiting quality loss and preventing spread to remaining sound bolls.",
                "Avoid unnecessary plant manipulation that creates wounds through which bacteria enter.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild blight: a single Copper Oxychloride spray and removal of heavily spotted leaves usually controls early spread.",
            ],
            "moderate": [
                "Moderate blight: repeat copper spray at 10-day intervals — 2 to 3 total sprays.",
                "Remove and burn all defoliated infected leaves from the field.",
            ],
            "severe": [
                "URGENT — severe bacterial blight can cause total defoliation and complete boll loss.",
                "Apply Copper Oxychloride every 7–10 days until symptoms stabilise.",
                "Destroy heavily infected plants to reduce the bacterial reservoir in the field.",
                "Conduct strict seed health testing before the next sowing season (CICR, CABI).",
            ],
        },
        "preventive_measures": [
            "Always use disease-free, certified seed and bacterial-blight-resistant varieties (CICR recommendation).",
            "Treat seeds by soaking in Streptocycline solution (100 ppm for 30 minutes) before sowing.",
            "Rotate with non-host crops for at least one season.",
            "Do not work in the field when foliage is wet — workers spread the bacteria mechanically.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "CABI – Centre for Agriculture and Bioscience International",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },

    "Curl Virus": {
        "disease_name": "Cotton Leaf Curl Virus (CLCuV)",
        "causal_organism": "Cotton Leaf Curl Virus (Begomovirus); vector: Bemisia tabaci (whitefly)",
        "symptoms": [
            "Upward or downward curling of leaves",
            "Vein thickening and enations (raised outgrowths) on the underside of leaves",
            "Stunted plant growth and drastically reduced boll formation",
            "Yellowing between veins in severe or long-standing infections",
        ],
        "base_remedies": [
            "Control whitefly vector (Bemisia tabaci) with Imidacloprid 17.8 SL (0.3 mL/L water)",
            "Remove and destroy infected plants as soon as symptoms are confirmed",
            "Use CLCuV-resistant or tolerant cotton varieties — the most effective long-term measure",
            "Install yellow sticky traps (25–30 per hectare) around field margins to monitor and suppress whitefly",
            "Avoid late sowing, which coincides with peak whitefly population cycles",
        ],
        "stage_remedies": {
            "small_plant": [
                "CRITICAL — small plants are the most susceptible; infection at this stage severely stunts the entire crop.",
                "Scout every 3–5 days for early leaf curling and whitefly presence on lower leaf undersides.",
                "Apply Imidacloprid at the first detection of whiteflies — early nymphal control is essential.",
                "Uproot and destroy infected seedlings immediately; do not attempt recovery treatment.",
            ],
            "leaf_growth": [
                "At leaf growth, apply insecticide spray if whitefly population exceeds 1 adult per leaf.",
                "Remove visibly infected plants to reduce the virus source for remaining healthy plants.",
                "Monitor yellow sticky trap catch counts to track whitefly population trends.",
            ],
            "bud_formation": [
                "At bud formation, CLCuV infection causes bud shedding and distorted new growth.",
                "Apply Neem-based insecticide (Azadirachtin 0.03%) as a bio-pesticide first option.",
                "If whitefly pressure remains high despite neem application, use Thiamethoxam at the recommended dose.",
            ],
            "flowering": [
                "At flowering, whitefly populations often peak — intensify scouting frequency to every 3 days.",
                "Rotate insecticide classes (e.g., alternate neonicotinoids with spiromesifen) to prevent resistance.",
                "Spray during early morning or evening to protect pollinating insects.",
            ],
            "boll_starting": [
                "At boll starting, new CLCuV infections will reduce boll retention.",
                "Continue the whitefly control programme; bolls remain at risk until they mature.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild CLCuV: rogue infected plants, apply Imidacloprid spray, and increase scouting to every 3 days.",
                "Install or check yellow sticky trap catch counts.",
            ],
            "moderate": [
                "Moderate CLCuV: immediate infected-plant removal plus a weekly whitefly spray protocol.",
                "Apply Spiromesifen (0.5 mL/L) as an effective alternative for populations showing neonicotinoid resistance.",
            ],
            "severe": [
                "URGENT — severe CLCuV with high whitefly pressure can destroy the entire crop.",
                "Apply emergency Imidacloprid 17.8 SL spray immediately.",
                "Destroy all infected plants within the outbreak zone without delay.",
                "Consult the local agricultural extension officer for regional outbreak assessment.",
                "In future seasons: adopt CLCuV-resistant hybrids as the primary prevention strategy (CICR, DPPQS).",
            ],
        },
        "preventive_measures": [
            "Sow CLCuV-resistant or tolerant varieties — host-plant resistance is the most sustainable long-term strategy (CICR).",
            "Apply seed treatment with Imidacloprid (7 g/kg seed) for 4–6 weeks of systemic seedling protection against whitefly.",
            "Install yellow sticky traps from crop emergence onward.",
            "Remove and destroy volunteer cotton plants and weed hosts such as Malvastrum spp. near fields.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "United States Department of Agriculture (USDA)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },

    "Healthy Leaf": {
        "disease_name": "Healthy Leaf",
        "causal_organism": "None",
        "symptoms": [],
        "base_remedies": [
            "No disease treatment required at this time.",
            "Continue regular crop scouting every 7–10 days.",
            "Maintain balanced fertilisation as per soil test (CICR recommendations).",
            "Follow the recommended irrigation and integrated pest management schedule.",
        ],
        "stage_remedies": {},
        "severity_remedies": {},
        "preventive_measures": [
            "Maintain field hygiene to prevent disease introduction.",
            "Use certified disease-free seeds every season.",
            "Keep surrounding weeds and volunteer plants removed from field margins.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
        ],
    },

    "Herbicide Growth Damage": {
        "disease_name": "Herbicide Growth Damage",
        "causal_organism": "Abiotic – Herbicide Phytotoxicity",
        "symptoms": [
            "Abnormal leaf curling, cupping, or strap-leafing following herbicide application",
            "Chlorosis or tissue necrosis associated with spray timing",
            "Deformed new growth — twisted or elongated leaves",
            "No pustules, lesions, or associated insect vectors (distinct from biotic diseases)",
        ],
        "base_remedies": [
            "Apply thorough irrigation immediately to leach residual herbicide from the root zone",
            "Follow herbicide label rates strictly — overdose is the primary cause of phytotoxicity",
            "Use drift-reduction spray nozzles during all herbicide applications",
            "Apply foliar micronutrient mixture (Zn + Fe + B) to accelerate recovery of damaged tissue",
            "Select only crop-safe herbicide formulations registered for cotton",
        ],
        "stage_remedies": {
            "small_plant": [
                "Herbicide damage at small plant stage is most severe — young plants have very limited detoxification capacity.",
                "Apply an irrigation flush immediately upon recognising damage symptoms.",
                "Severely damaged seedlings may not recover; be prepared for gap-filling or partial re-sowing if stand loss exceeds 15%.",
            ],
            "leaf_growth": [
                "At leaf growth, recovery from herbicide damage is faster than at the small plant stage.",
                "Apply foliar potassium nitrate (1%) plus a micronutrient mix to stimulate new growth.",
                "Avoid spraying any additional chemicals while plants are under herbicide stress.",
            ],
            "bud_formation": [
                "At bud formation, herbicide stress causes bud abortion and poor flower set.",
                "Cytokinin or gibberellin-based growth regulator foliar spray may aid recovery at this stage (consult agronomist).",
            ],
            "flowering": [
                "At flowering, avoid all unnecessary sprays — concentrate on irrigation management to flush root-zone herbicide.",
                "Flowers may abscise due to residual stress; the subsequent flush of flowers may be normal.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild damage: irrigation and time are usually sufficient for recovery — no chemical intervention needed.",
            ],
            "moderate": [
                "Moderate damage: irrigation flush + foliar micronutrient spray + growth regulator application.",
                "Monitor for recovery over 10–14 days; consult an agronomist if recovery is not visible after 2 weeks.",
            ],
            "severe": [
                "URGENT — severe phytotoxicity may require partial re-sowing to restore acceptable plant stand.",
                "Apply a heavy irrigation flush to leach the root zone.",
                "Contact the herbicide manufacturer and local agricultural extension officer for guidance.",
                "Assess economic viability of re-sowing versus allowing stressed plants to recover.",
            ],
        },
        "preventive_measures": [
            "Always follow label rate, timing, and weather-window guidelines for all herbicide applications.",
            "Use low-drift nozzles and maintain appropriate buffer distances to protect adjacent crop rows.",
            "Keep detailed records of herbicide applications: product name, dose, date, wind speed, and temperature.",
            "Test herbicide tolerance of new varieties on a small plot before full-field application.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "United States Department of Agriculture (USDA)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
            "CABI – Centre for Agriculture and Bioscience International",
        ],
    },

    "Leaf Hopper Jassids": {
        "disease_name": "Leaf Hopper (Jassids)",
        "causal_organism": "Amrasca biguttula biguttula (Ishida)",
        "symptoms": [
            "Yellowing and downward curling of leaf margins progressing toward the midrib",
            "Hopper burn — leaves show a characteristic bronzed or burnt appearance in heavy infestations",
            "Downward cupping of leaves",
            "Severe infestations cause premature leaf drop and a substantial reduction in leaf area index",
        ],
        "base_remedies": [
            "Spray Imidacloprid 17.8 SL (0.3 mL/L) or Thiamethoxam 25 WG at the recommended label dose",
            "Apply Neem oil (5 mL/L) or Neem-based Azadirachtin (0.03%) as a bio-pesticide alternative",
            "Use jassid-resistant varieties with hairy (pubescent) leaves — host-plant resistance is the most sustainable option",
            "Avoid excess nitrogen fertilisation, which promotes succulent, highly susceptible leaf tissue",
        ],
        "stage_remedies": {
            "small_plant": [
                "Jassid infestation at small plant stage is highly damaging — plants have very limited recovery capacity.",
                "Scout every 3–5 days; if jassid population exceeds 1 per leaf, apply insecticide immediately (CICR threshold).",
                "Seed treatment with Imidacloprid (7 g/kg seed) provides systemic 4–6 week protection.",
            ],
            "leaf_growth": [
                "At leaf growth, jassids multiply rapidly on young developing leaves.",
                "Economic threshold: 2–3 jassids per leaf — trigger insecticide spray immediately if exceeded (TNAU).",
                "Apply spray to the abaxial (lower) leaf surface for best contact with nymphs and adults.",
            ],
            "bud_formation": [
                "At bud formation, jassid feeding stress can cause bud abortion and impact yield.",
                "Rotate between insecticide classes (neonicotinoids vs. organophosphates) to prevent resistance development.",
                "Neem-based sprays are preferred at bud stage to protect beneficial insects and natural enemies.",
            ],
            "flowering": [
                "At flowering, use only selective insecticides to protect beneficial pollinators.",
                "Apply sprays in early morning or evening to minimise harm to bees and other pollinators.",
            ],
            "boll_starting": [
                "At boll starting, jassid infestation is less yield-impacting than at earlier stages but should be managed.",
                "Maintain scouting; treat only if population exceeds the economic threshold.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild jassid infestation: Neem oil spray (5 mL/L) and improved plant spacing for air circulation are usually sufficient.",
            ],
            "moderate": [
                "Moderate infestation: apply Imidacloprid or Thiamethoxam and repeat in 10–12 days.",
                "Check for natural enemies (parasitic wasps, spiders, ladybird beetles) before switching to broad-spectrum insecticides.",
            ],
            "severe": [
                "URGENT — severe jassid infestation causes hopper burn and heavy defoliation.",
                "Apply immediate emergency Imidacloprid 17.8 SL spray.",
                "Follow up in 7–10 days with an alternate class insecticide (Spinosad or Spiromesifen) to prevent resistance.",
                "Assess crop for need of gap-filling if stand has been severely damaged.",
            ],
        },
        "preventive_measures": [
            "Use jassid-resistant pubescent varieties as the primary host-plant resistance measure (CICR, TNAU).",
            "Seed treatment with Imidacloprid provides early-season vector protection.",
            "Install yellow sticky traps around field margins for early population monitoring.",
            "Avoid over-application of nitrogen — balanced N-P-K reduces susceptibility.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },

    "Leaf Redding": {
        "disease_name": "Leaf Reddening",
        "causal_organism": "Physiological disorder — Phosphorus or Magnesium deficiency, or root stress",
        "symptoms": [
            "Reddish-purple discoloration of leaves, starting from older (lower) leaves and progressing upward",
            "Whole-leaf intense reddening visible across the canopy in severe cases",
            "May be associated with waterlogging, drought, or sucking-pest feeding stress",
            "No pustules, lesions, vein thickening, or pest insects present (distinct from viral diseases)",
        ],
        "base_remedies": [
            "Apply Di-Ammonium Phosphate (DAP) as a corrective phosphorus dose based on soil test results",
            "Foliar spray of Magnesium Sulfate (MgSO4) 1% solution for rapid visible response",
            "Improve field drainage to prevent waterlogging, which blocks phosphorus and magnesium uptake",
            "Control sucking pests (whiteflies, jassids) that trigger secondary physiological stress and reddening",
            "Conduct soil testing to identify and correct all deficient nutrients (CICR, ICAR)",
        ],
        "stage_remedies": {
            "small_plant": [
                "At small plant stage, reddening indicates severe early nutrient stress — act quickly.",
                "Apply immediate basal DAP dose if phosphorus was withheld at planting, or apply liquid phosphorus fertiliser.",
            ],
            "leaf_growth": [
                "At leaf growth, foliar Magnesium Sulfate (1%) spray produces a rapid canopy colour response within 7–10 days.",
                "Check root-zone moisture carefully — both drought and waterlogging lock out phosphorus.",
            ],
            "bud_formation": [
                "At bud formation, leaf reddening impairs carbohydrate supply to developing buds and reduces boll set.",
                "Apply foliar micronutrient mix (ZnSO4 0.5%, MnSO4 0.3%, FeSO4 0.2%) alongside the Mg sulfate spray.",
            ],
            "flowering": [
                "At flowering, severe leaf reddening impairs photosynthate supply to bolls.",
                "Apply combined potassium nitrate (1%) + MgSO4 (1%) foliar spray for fastest recovery.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild reddening: a single Mg sulfate foliar spray (1%) usually reverses visible symptoms within 10–14 days.",
            ],
            "moderate": [
                "Moderate reddening: apply DAP soil correction + Mg sulfate foliar spray; improve drainage.",
                "Repeat foliar spray in 7 days if visible colour recovery has not started.",
            ],
            "severe": [
                "URGENT — severe reddening across the whole field indicates systemic nutrient or root stress.",
                "Conduct emergency soil and leaf tissue tests to pinpoint the primary deficiency.",
                "Apply DAP soil correction + Mg sulfate foliar spray + full micronutrient cocktail in sequence.",
                "Resolve irrigation management first — waterlogging or drought must be corrected before nutrient sprays become effective.",
            ],
        },
        "preventive_measures": [
            "Conduct soil nutrient testing before each crop season; apply phosphorus and magnesium per test results (CICR, ICAR).",
            "Ensure adequate basal phosphorus application — correcting phosphorus deficiency after establishment is difficult.",
            "Maintain well-functioning field drainage infrastructure.",
            "Manage sucking pest populations early to prevent secondary stress-triggered reddening.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "Indian Council of Agricultural Research (ICAR)",
            "Schumann G.L. & D'Arcy C.J. – Essential Plant Pathology / Introduction to Plant Pathology",
        ],
    },

    "Leaf Variegation": {
        "disease_name": "Leaf Variegation",
        "causal_organism": "Viral infection (mosaic begomovirus) or micronutrient deficiency",
        "symptoms": [
            "Irregular patches of light and dark green on leaves (mosaic pattern)",
            "Sectoral chlorosis or yellowing between veins",
            "May be accompanied by mild leaf distortion in viral cases",
            "Distinct from bacterial blight — no water-soaking, angular lesions, or vein blackening",
        ],
        "base_remedies": [
            "Apply foliar micronutrient mixture (Zinc Sulfate 0.5% + Manganese Sulfate 0.3% + Ferrous Sulfate 0.2%)",
            "Remove and destroy plants with clear mosaic or distortion symptoms to reduce virus source",
            "Control insect vectors (whiteflies, aphids) with Imidacloprid 17.8 SL (0.3 mL/L) or Thiamethoxam",
            "Use only virus-free certified planting material",
            "Submit representative leaf samples for laboratory diagnosis if viral aetiology is strongly suspected",
        ],
        "stage_remedies": {
            "small_plant": [
                "Variegation at small plant stage may indicate systemic virus infection via infected seed or early insect feeding.",
                "Remove and destroy affected plants immediately — viral spread at this stage will be extensive if unchecked.",
                "Apply Imidacloprid at once for vector insect control.",
            ],
            "leaf_growth": [
                "At leaf growth, apply micronutrient foliar spray to distinguish nutrient deficiency from viral cause.",
                "If symptoms persist or worsen after nutrient spray within 10 days, viral infection is the likely cause.",
                "Continue vector insect monitoring and control throughout leaf growth.",
            ],
            "bud_formation": [
                "Leaf variegation at bud formation reduces photosynthesis during a critical energy-demand stage.",
                "Continue micronutrient supplementation and vector insect control.",
            ],
        },
        "severity_remedies": {
            "mild": [
                "Mild variegation: apply micronutrient spray and monitor closely for recovery over 10 days.",
                "Control vector insects as a precaution regardless of suspected cause.",
            ],
            "moderate": [
                "Moderate variegation: vector insect control + micronutrient spray + removal of symptomatic plants in outbreak patches.",
                "Isolate visibly infected sections to limit virus spread to healthy sections.",
            ],
            "severe": [
                "URGENT — widespread leaf variegation with distortion indicates systemic viral spread.",
                "Remove and destroy all clearly infected plants without delay.",
                "Apply emergency Imidacloprid 17.8 SL vector control spray immediately.",
                "Send samples to an agricultural diagnostic laboratory for virus identification to guide further management.",
            ],
        },
        "preventive_measures": [
            "Use only certified, disease-tested planting material (CICR recommendation).",
            "Control vector insects (whiteflies, aphids, thrips) from crop emergence onward.",
            "Conduct pre-sowing soil micronutrient analysis and correct any deficiencies before sowing.",
            "Maintain barrier crops (maize, sorghum rows) at field margins as buffer zones against insect vector migration.",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "CABI – Centre for Agriculture and Bioscience International",
            "Agrios G.N. – Plant Pathology (Academic Press)",
        ],
    },
}


# ---------------------------------------------------------------------------
# Disease registry
# ---------------------------------------------------------------------------

_DISEASE_REGISTRY: dict[str, dict[str, dict[str, Any]]] = {
    "wheat": WHEAT_DISEASES,
    "cotton": COTTON_DISEASES,
}


# ---------------------------------------------------------------------------
# Core recommendation function
# ---------------------------------------------------------------------------

def get_recommendation(
    disease: str,
    crop: str,
    growth_stage: str = "Unknown",
    severity_level: str = "Unknown",
) -> dict[str, Any]:
    """Return a complete, context-aware remedy recommendation.

    Args:
        disease:       Disease class name as predicted by the image model.
        crop:          "cotton" or "wheat".
        growth_stage:  Current crop growth stage.
                       Call get_supported_growth_stages(crop) for valid values.
        severity_level: "Mild", "Moderate", or "Severe".

    Returns:
        dict with keys:
            disease_name        – human-readable disease name
            causal_organism     – causal pathogen or abiotic cause
            symptoms            – observed symptoms list
            remedies            – combined remedy list (base + stage-specific +
                                  severity-specific, deduplicated, ordered)
            stage_specific      – stage-specific remedy additions
            severity_specific   – severity-specific remedy additions
            preventive_measures – preventive measures for future seasons
            sources             – knowledge base sources cited
            growth_stage        – echoed input
            severity_level      – echoed input
    """
    crop_key = str(crop).strip().lower()
    crop_db = _DISEASE_REGISTRY.get(crop_key, {})

    # Locate disease record — exact key match first, then normalised match
    record: dict[str, Any] | None = crop_db.get(disease)
    if record is None:
        target = _normalize(disease)
        for key, val in crop_db.items():
            if _normalize(key) == target:
                record = val
                break

    # Fallback for unrecognised disease
    if record is None:
        return {
            "disease_name": disease,
            "causal_organism": "Unknown",
            "symptoms": [],
            "remedies": [
                "Consult a local agricultural extension officer for correct diagnosis and treatment.",
            ],
            "stage_specific": [],
            "severity_specific": [],
            "preventive_measures": [],
            "sources": [],
            "growth_stage": growth_stage,
            "severity_level": severity_level,
        }

    stage_key = _stage_key(crop_key, growth_stage)
    sev_key = _severity_key(severity_level)

    stage_actions: list[str] = list(
        record.get("stage_remedies", {}).get(stage_key, [])
    )
    severity_actions: list[str] = list(
        record.get("severity_remedies", {}).get(sev_key, [])
    )

    # Build deduplicated combined remedy list:
    # base remedies first, then stage-specific, then severity-specific
    seen: set[str] = set()
    combined: list[str] = []
    for item in list(record.get("base_remedies", [])) + stage_actions + severity_actions:
        norm = item.strip().lower()
        if norm and norm not in seen:
            seen.add(norm)
            combined.append(item)

    return {
        "disease_name": record["disease_name"],
        "causal_organism": record.get("causal_organism", ""),
        "symptoms": list(record.get("symptoms", [])),
        "remedies": combined,
        "stage_specific": stage_actions,
        "severity_specific": severity_actions,
        "preventive_measures": list(record.get("preventive_measures", [])),
        "sources": list(record.get("sources", [])),
        "growth_stage": growth_stage,
        "severity_level": severity_level,
    }


# ---------------------------------------------------------------------------
# Public utility functions
# ---------------------------------------------------------------------------

def get_supported_growth_stages(crop: str) -> list[str]:
    """Return the list of supported growth stage display names for a crop."""
    key = str(crop).strip().lower()
    if key == "cotton":
        return list(COTTON_STAGES)
    if key == "wheat":
        return list(WHEAT_STAGES)
    return []


def get_all_recommendations(crop: str) -> dict[str, dict[str, Any]]:
    """Return base recommendation records for every disease of a given crop."""
    crop_key = str(crop).strip().lower()
    result: dict[str, dict[str, Any]] = {}
    for disease_key, record in _DISEASE_REGISTRY.get(crop_key, {}).items():
        result[disease_key] = {
            "disease_name": record["disease_name"],
            "causal_organism": record.get("causal_organism", ""),
            "symptoms": list(record.get("symptoms", [])),
            "base_remedies": list(record.get("base_remedies", [])),
            "preventive_measures": list(record.get("preventive_measures", [])),
            "sources": list(record.get("sources", [])),
        }
    return result


# ---------------------------------------------------------------------------
# Backward-compatible wrapper (used by app/main.py)
# ---------------------------------------------------------------------------

def get_enhanced_recommendation(
    crop: str,
    class_name: str,
    growth_stage: str = "Unknown",
    severity_level: str = "Unknown",
    farm_size: Any = None,  # accepted for API compatibility; handled by LLM layer
) -> dict[str, Any]:
    """Backward-compatible wrapper around get_recommendation().

    The farm_size parameter is accepted to maintain API compatibility with
    app/main.py but is NOT used by the rule-based engine — farm-size-specific
    cost analysis is handled exclusively by the LLM advisory layer in
    Recommendation Model/LLM_Model.py.
    """
    return get_recommendation(
        disease=class_name,
        crop=crop,
        growth_stage=growth_stage,
        severity_level=severity_level,
    )
