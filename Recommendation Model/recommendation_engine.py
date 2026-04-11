"""
Rule-Based Recommendation Engine for Plant Disease Management
=============================================================

Provides diagnostic rules (symptom → disease mapping) and evidence-based
remedies for wheat and cotton diseases.  Each recommendation cites peer-
reviewed or institutional sources so downstream consumers can present
traceable advice.

Sources
-------
- Indian Council of Agricultural Research (ICAR)
- Punjab Agricultural University (PAU)
- International Maize and Wheat Improvement Center (CIMMYT)
- Food and Agriculture Organization (FAO)
- Central Institute for Cotton Research (CICR)
- Tamil Nadu Agricultural University (TNAU)
- United States Department of Agriculture (USDA)
- CABI – Centre for Agriculture and Bioscience International
- Ministry of Agriculture and Farmers Welfare, Government of India
- Directorate of Plant Protection, Quarantine and Storage (DPPQS)
- Murray T.D., Parry D.W., & Cattlin N.D. – *Compendium of Wheat Diseases and Pests* (APS Press)
- Agrios G.N. – *Plant Pathology* (Academic Press)
- Schumann G.L. & D'Arcy C.J. – *Essential Plant Pathology* / *Introduction to Plant Pathology*
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Wheat disease recommendations
# ---------------------------------------------------------------------------

WHEAT_RECOMMENDATIONS: dict[str, dict[str, Any]] = {
    "Black Rust(Stem Rust)": {
        "disease_name": "Black Rust (Stem Rust)",
        "rule": "IF reddish-brown elongated pustules on stem/leaves → THEN disease = Black Rust",
        "symptoms": [
            "Reddish-brown elongated pustules on stems and leaves",
            "Dark brown to black pustules at maturity",
            "Weakened stems susceptible to lodging",
        ],
        "remedies": [
            "Spray Propiconazole (0.1%) at first appearance of pustules",
            "Use stem-rust-resistant varieties (e.g., Sr31, Sr38 gene lines)",
            "Adopt early sowing to escape peak rust inoculum",
            "Eliminate alternate host (barberry) near fields",
            "Monitor fields weekly during tillering to heading stage",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Murray T.D. et al. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },
    "BlackPoint": {
        "disease_name": "Black Point",
        "rule": "IF black discoloration at grain embryo end → THEN disease = Black Point",
        "symptoms": [
            "Black or dark-brown discoloration at the embryo end of grains",
            "Reduced grain quality and test weight",
            "May lower germination in severe cases",
        ],
        "remedies": [
            "Treat seeds with Carbendazim (2 g/kg seed) before sowing",
            "Avoid excess humidity during grain storage",
            "Harvest at optimal moisture (< 14%) to prevent fungal colonisation",
            "Ensure proper drying and ventilated storage",
            "Avoid delayed harvesting in wet conditions",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Food and Agriculture Organization (FAO)",
            "Murray T.D. et al. – Compendium of Wheat Diseases and Pests (APS Press)",
        ],
    },
    "FusariumFootRot": {
        "disease_name": "Fusarium Foot Rot",
        "rule": "IF base stem browning + plant wilting → THEN disease = Fusarium Foot Rot",
        "symptoms": [
            "Brown lesions at the stem base",
            "Premature wilting and white-head symptoms",
            "Honey-brown discoloration of sub-crown internode",
        ],
        "remedies": [
            "Treat seeds with Carbendazim (2 g/kg seed)",
            "Practice crop rotation — avoid wheat-after-wheat for ≥ 2 seasons",
            "Avoid deep sowing; maintain optimum sowing depth (3–5 cm)",
            "Manage crop residue to reduce inoculum carry-over",
            "Use seed-treatment fungicides such as Fludioxonil where available",
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
        "rule": "No disease symptoms detected — plant appears healthy",
        "symptoms": [],
        "remedies": [
            "No treatment required",
            "Continue regular crop monitoring and scouting",
            "Maintain balanced fertilisation (N-P-K as per soil test)",
            "Follow recommended irrigation schedule",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
        ],
    },
    "LeafBlight": {
        "disease_name": "Leaf Blight",
        "rule": "IF yellow/brown lesions on leaves → THEN disease = Leaf Blight",
        "symptoms": [
            "Yellow to brown oval/elliptical lesions on leaves",
            "Lesions may coalesce causing extensive blighting",
            "Premature leaf drying and reduced photosynthesis",
        ],
        "remedies": [
            "Spray Mancozeb (0.25%) at first symptom appearance",
            "Ensure balanced fertilisation — avoid excess nitrogen",
            "Use resistant or tolerant varieties",
            "Remove and destroy infected crop debris after harvest",
            "Apply Propiconazole as follow-up spray if disease progresses",
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
        "rule": "IF white powder on leaves → THEN disease = Mildew",
        "symptoms": [
            "White to grey powdery fungal growth on leaf surfaces",
            "May also appear on stems and spikes",
            "Reduced photosynthesis and grain shrivelling",
        ],
        "remedies": [
            "Spray wettable Sulfur (0.3%) or Triadimefon",
            "Maintain proper plant spacing for air circulation",
            "Avoid excessive nitrogen fertilisation",
            "Use mildew-resistant varieties",
            "Apply fungicide at early boot stage if conditions are conducive",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Murray T.D. et al. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },
    "Smut": {
        "disease_name": "Smut (Loose Smut)",
        "rule": "IF grains replaced by black powder → THEN disease = Smut",
        "symptoms": [
            "Grain heads replaced by masses of dark-brown to black spores",
            "Infected heads emerge earlier than healthy ones",
            "Wind-dispersed spore mass visible at heading",
        ],
        "remedies": [
            "Treat seeds with Carbendazim or Carboxin + Thiram",
            "Use certified smut-free seeds from reliable sources",
            "Hot-water seed treatment (52 °C for 10 min) as traditional method",
            "Use systemic seed-treatment fungicides such as Tebuconazole",
        ],
        "sources": [
            "Indian Council of Agricultural Research (ICAR)",
            "Punjab Agricultural University (PAU)",
            "Murray T.D. et al. – Compendium of Wheat Diseases and Pests (APS Press)",
            "Directorate of Plant Protection, Quarantine and Storage (DPPQS)",
        ],
    },
    "WheatBlast": {
        "disease_name": "Wheat Blast",
        "rule": "IF spike bleaching + shrivelled grains → THEN disease = Wheat Blast",
        "symptoms": [
            "Bleached or white spikes (partial or complete)",
            "Shrivelled, light-weight grains",
            "Rapid spike death under warm, humid conditions",
        ],
        "remedies": [
            "Spray Trifloxystrobin + Tebuconazole combination at heading",
            "Avoid late sowing — adhere to recommended sowing window",
            "Use blast-resistant varieties where available",
            "Manage crop residue to lower inoculum",
            "Apply preventive strobilurin + triazole fungicides",
        ],
        "sources": [
            "International Maize and Wheat Improvement Center (CIMMYT)",
            "Food and Agriculture Organization (FAO)",
            "Agrios G.N. – Plant Pathology (Academic Press)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },
    "Yellow Rust(Leaf Rust)": {
        "disease_name": "Yellow Rust (Leaf Rust)",
        "rule": "IF yellow stripe pustules on leaves → THEN disease = Yellow Rust",
        "symptoms": [
            "Yellow-orange pustules arranged in stripes along leaf veins",
            "Favoured by cool, moist conditions",
            "Severe yield reduction when infection occurs before heading",
        ],
        "remedies": [
            "Spray Propiconazole (0.1%) at first appearance of stripes",
            "Use rust-resistant varieties (e.g., Yr gene lines)",
            "Monitor fields regularly during cool, wet weather",
            "Apply Tebuconazole as an alternate fungicide",
            "Remove volunteer wheat plants near fields",
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
# Cotton disease recommendations
# ---------------------------------------------------------------------------

COTTON_RECOMMENDATIONS: dict[str, dict[str, Any]] = {
    "Bacterial Blight": {
        "disease_name": "Bacterial Blight",
        "rule": "IF angular leaf spots + vein blackening → THEN disease = Bacterial Blight",
        "symptoms": [
            "Angular, water-soaked lesions on leaves",
            "Vein blackening (black-arm symptom)",
            "Lesions turn brown and necrotic; leaves may drop",
        ],
        "remedies": [
            "Spray Copper Oxychloride (0.3%) at symptom onset",
            "Use disease-free, resistant seed varieties",
            "Practice crop rotation with non-host crops",
            "Remove and destroy infected plant debris",
            "Avoid overhead irrigation to reduce splash dispersal",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "CABI – Centre for Agriculture and Bioscience International",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
        ],
    },
    "Curl Virus": {
        "disease_name": "Cotton Leaf Curl Virus",
        "rule": "IF leaf curling + stunted growth → THEN disease = Curl Virus",
        "symptoms": [
            "Upward or downward curling of leaves",
            "Vein thickening and enations on the underside",
            "Stunted plant growth and reduced boll formation",
        ],
        "remedies": [
            "Control whitefly vector (Bemisia tabaci) — spray Imidacloprid (0.3 mL/L)",
            "Remove and destroy infected plants early",
            "Use CLCuV-resistant/tolerant varieties",
            "Install yellow sticky traps around field margins",
            "Avoid late sowing which overlaps with high whitefly populations",
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
        "rule": "No disease symptoms detected — leaf appears healthy",
        "symptoms": [],
        "remedies": [
            "No treatment required",
            "Continue regular crop monitoring and scouting",
            "Maintain balanced fertilisation as per soil test",
            "Follow recommended irrigation and pest-management schedule",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
        ],
    },
    "Herbicide Growth Damage": {
        "disease_name": "Herbicide Growth Damage",
        "rule": "IF leaf deformation after spraying → THEN cause = Herbicide Damage",
        "symptoms": [
            "Abnormal leaf curling, cupping, or strapping",
            "Chlorosis or necrosis following herbicide application",
            "Deformed new growth",
        ],
        "remedies": [
            "Apply irrigation flush to leach residual herbicide from root zone",
            "Avoid herbicide overdose — follow label rates strictly",
            "Use buffer zones and drift-reduction nozzles during spraying",
            "Apply growth regulators or foliar nutrients to aid recovery",
            "Select herbicides with crop-safe profiles",
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
        "rule": "IF leaf yellowing + curling edges → THEN pest = Jassids",
        "symptoms": [
            "Yellowing and curling of leaf margins",
            "Hopper-burn: leaves show a burnt appearance in severe infestation",
            "Downward cupping of leaves",
        ],
        "remedies": [
            "Spray Imidacloprid (0.3 mL/L) or Thiamethoxam",
            "Apply Neem oil (5 mL/L) as a bio-pesticide alternative",
            "Use jassid-resistant varieties with hairy leaves",
            "Maintain proper plant spacing for air circulation",
            "Avoid excess nitrogen which promotes succulent growth",
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
        "rule": "IF leaves turn red/purple → THEN cause = Nutrient Deficiency (P or Mg)",
        "symptoms": [
            "Reddish-purple discoloration of leaves",
            "Starts from older leaves and progresses upward",
            "May be associated with waterlogging or pest-induced stress",
        ],
        "remedies": [
            "Apply DAP (Di-Ammonium Phosphate) for phosphorus correction",
            "Apply Magnesium Sulfate (MgSO₄) foliar spray (1%)",
            "Improve field drainage to prevent waterlogging",
            "Control sucking pests that may trigger reddening",
            "Conduct soil testing and apply deficient nutrients",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "Indian Council of Agricultural Research (ICAR)",
            "Schumann G.L. & D'Arcy C.J. – Essential Plant Pathology",
        ],
    },
    "Leaf Variegation": {
        "disease_name": "Leaf Variegation",
        "rule": "IF uneven yellow-green patches → THEN cause = Viral/Nutrient Issue",
        "symptoms": [
            "Irregular patches of light and dark green on leaves",
            "Mosaic-like pattern or sectoral chlorosis",
            "May be accompanied by leaf distortion",
        ],
        "remedies": [
            "Spray micronutrient mixture (Zn, Mn, Fe) as foliar application",
            "Remove and destroy infected/symptomatic plants",
            "Control insect vectors (whitefly, aphids) to limit viral spread",
            "Use virus-free planting material",
            "Submit samples for lab diagnosis if viral cause is suspected",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "CABI – Centre for Agriculture and Bioscience International",
            "Agrios G.N. – Plant Pathology (Academic Press)",
        ],
    },
    "fussarium_wilt": {
        "disease_name": "Fusarium Wilt",
        "rule": "IF plant wilting + vascular browning → THEN disease = Fusarium Wilt",
        "symptoms": [
            "Progressive wilting of plant starting from lower leaves",
            "Vascular browning visible on split stems",
            "Yellowing and eventual death of the plant",
        ],
        "remedies": [
            "Apply soil drenching with Carbendazim (0.1%)",
            "Practice crop rotation — rotate with non-host crops for 3+ years",
            "Use Fusarium-wilt-resistant cotton varieties",
            "Apply Trichoderma viride as a bio-control agent in soil",
            "Avoid waterlogged conditions which favour the pathogen",
        ],
        "sources": [
            "Central Institute for Cotton Research (CICR)",
            "Tamil Nadu Agricultural University (TNAU)",
            "Ministry of Agriculture and Farmers Welfare, Government of India",
            "Agrios G.N. – Plant Pathology (Academic Press)",
        ],
    },
}

# ---------------------------------------------------------------------------
# Unified lookup
# ---------------------------------------------------------------------------

_ALL_RECOMMENDATIONS: dict[str, dict[str, dict[str, Any]]] = {
    "wheat": WHEAT_RECOMMENDATIONS,
    "cotton": COTTON_RECOMMENDATIONS,
}

_GENERAL_SOURCES: list[str] = [
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
    "Schumann G.L. & D'Arcy C.J. – Introduction to Plant Pathology",
]


def get_recommendation(crop: str, class_name: str) -> dict[str, Any]:
    """Return the rule-based recommendation for a given crop + class_name.

    Returns a dict with keys:
        disease_name, rule, symptoms, remedies, sources

    If the class_name is not found, returns a sensible fallback.
    """
    crop_key = crop.strip().lower()
    crop_recs = _ALL_RECOMMENDATIONS.get(crop_key, {})
    rec = crop_recs.get(class_name)
    if rec is not None:
        return dict(rec)

    # Fallback for unknown class
    return {
        "disease_name": class_name,
        "rule": "",
        "symptoms": [],
        "remedies": ["Consult a local agricultural extension officer for diagnosis and treatment."],
        "sources": [],
    }


def get_all_recommendations(crop: str) -> dict[str, dict[str, Any]]:
    """Return all recommendations for a given crop."""
    crop_key = crop.strip().lower()
    return dict(_ALL_RECOMMENDATIONS.get(crop_key, {}))
