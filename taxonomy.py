"""
taxonomy.py — Waste Classification Taxonomy

Hardcoded dictionary mapping each waste class to its disposal method,
decomposition time, recyclability index, and carbon footprint category.
"""

# Ordered list of all 9 waste classes supported by the model
WASTE_CLASSES = [
    "Biodegradable",
    "Plastic",
    "Metal",
    "Glass",
    "E-Waste",
    "Pharmaceutical",
    "Hazardous",
    "Textile",
    "Construction Debris",
]

# Complete taxonomy mapping for each waste class
WASTE_TAXONOMY = {
    "Biodegradable": {
        "disposal_method": "Compost in a home or municipal composting facility. Separate food scraps from garden waste for optimal decomposition. Avoid mixing with non-organic materials.",
        "decomposition_time_years": 0.5,
        "recyclability_index": 0.85,
        "carbon_footprint_category": "low",
        "examples": ["food waste", "vegetable/fruit scraps", "garden waste", "paper"],
        "bin_color": "#4CAF50",
    },
    "Plastic": {
        "disposal_method": "Sort by resin code (PET #1, HDPE #2, etc.). Rinse containers before recycling. Film plastics go to dedicated collection points at grocery stores. Avoid contamination with food residue.",
        "decomposition_time_years": 450,
        "recyclability_index": 0.35,
        "carbon_footprint_category": "high",
        "examples": ["PET bottles", "HDPE containers", "polystyrene", "film plastic"],
        "bin_color": "#2196F3",
    },
    "Metal": {
        "disposal_method": "Rinse and place in metals recycling bin. Aluminium cans should be crushed to save space. Steel tins can be recycled indefinitely. Remove paper labels when possible.",
        "decomposition_time_years": 200,
        "recyclability_index": 0.92,
        "carbon_footprint_category": "medium",
        "examples": ["aluminium cans", "steel tins", "ferrous scrap"],
        "bin_color": "#9E9E9E",
    },
    "Glass": {
        "disposal_method": "Separate by colour (clear, green, brown) if required by local facility. Remove caps and lids. Do not mix with ceramics or heat-resistant glass. Broken glass should be wrapped safely.",
        "decomposition_time_years": 1000000,
        "recyclability_index": 0.90,
        "carbon_footprint_category": "medium",
        "examples": ["clear glass", "coloured glass", "broken glass"],
        "bin_color": "#00BCD4",
    },
    "E-Waste": {
        "disposal_method": "Take to a certified e-waste recycling centre. Never dispose in general waste. Remove batteries separately. Many electronics retailers offer take-back programmes.",
        "decomposition_time_years": 1000,
        "recyclability_index": 0.55,
        "carbon_footprint_category": "high",
        "examples": ["batteries", "circuit boards", "cables", "small electronics"],
        "bin_color": "#FF9800",
    },
    "Pharmaceutical": {
        "disposal_method": "Return to a pharmacy take-back programme. Do not flush medications or place in general waste. Blister packs may be recyclable at specialised facilities. Keep in original packaging for identification.",
        "decomposition_time_years": 100,
        "recyclability_index": 0.15,
        "carbon_footprint_category": "high",
        "examples": ["medicine packaging", "blister packs", "expired drugs"],
        "bin_color": "#E91E63",
    },
    "Hazardous": {
        "disposal_method": "Deliver to a hazardous waste collection event or permanent facility. Never pour down drains or place in regular bins. Store in original containers with labels intact. Contact local authority for pickup scheduling.",
        "decomposition_time_years": 500,
        "recyclability_index": 0.10,
        "carbon_footprint_category": "high",
        "examples": ["paint cans", "chemical containers", "aerosols"],
        "bin_color": "#F44336",
    },
    "Textile": {
        "disposal_method": "Donate wearable clothing to charity shops. Non-wearable textiles go to textile recycling bins. Some brands accept used clothing for recycling. Cut into rags for household use before discarding.",
        "decomposition_time_years": 40,
        "recyclability_index": 0.60,
        "carbon_footprint_category": "medium",
        "examples": ["fabric scraps", "clothing"],
        "bin_color": "#9C27B0",
    },
    "Construction Debris": {
        "disposal_method": "Separate into concrete, wood, metal, and mixed waste streams. Take to a construction and demolition recycling facility. Wood offcuts can be chipped for mulch. Tiles and concrete can be crushed for aggregate.",
        "decomposition_time_years": 100,
        "recyclability_index": 0.45,
        "carbon_footprint_category": "high",
        "examples": ["concrete", "wood offcuts", "tiles"],
        "bin_color": "#795548",
    },
}

# Carbon footprint badge colours for UI rendering
CARBON_COLORS = {
    "low": "#4CAF50",
    "medium": "#FF9800",
    "high": "#F44336",
}


def get_class_info(class_name: str) -> dict:
    """Return taxonomy info for a given waste class, or None if not found."""
    return WASTE_TAXONOMY.get(class_name)


def get_decomposition_display(years: float) -> str:
    """Format decomposition time as a human-readable string."""
    if years < 1:
        months = int(years * 12)
        return f"{months} months"
    elif years >= 1000000:
        return "~1 million years"
    elif years >= 1000:
        return f"~{int(years):,} years"
    else:
        return f"~{int(years)} years"
