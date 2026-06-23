"""
impact_calculator.py — Environmental Impact Analysis

Computes composition percentages, weighted recyclability scores,
overall impact ratings (A–E), and disposal instructions from
detected waste classes and their confidence scores.
"""

from taxonomy import WASTE_TAXONOMY, get_decomposition_display


def compute_composition(predictions: dict) -> dict:
    """
    Normalize prediction confidences to composition percentages
    that sum to 100%.

    Args:
        predictions: Dict of {class_name: confidence_score} (filtered).

    Returns:
        Dict of {class_name: percentage} summing to 100.
    """
    total = sum(predictions.values())
    if total == 0:
        total = 1.0

    composition = {}
    for class_name, confidence in predictions.items():
        composition[class_name] = round((confidence / total) * 100, 1)

    return dict(sorted(composition.items(), key=lambda x: x[1], reverse=True))


def compute_recyclability_score(composition: dict) -> float:
    """
    Compute weighted average recyclability score based on
    composition percentages and per-class recyclability indices.

    Args:
        composition: Dict of {class_name: percentage}.

    Returns:
        Float between 0 and 1 representing overall recyclability.
    """
    if not composition:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for class_name, percentage in composition.items():
        if class_name in WASTE_TAXONOMY:
            recyclability = WASTE_TAXONOMY[class_name]["recyclability_index"]
            weighted_sum += recyclability * percentage
            total_weight += percentage

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 3)


def compute_impact_rating(recyclability_score: float) -> tuple:
    """
    Map recyclability score to an A–E impact rating.

    Args:
        recyclability_score: Float between 0 and 1.

    Returns:
        Tuple of (letter_grade, description, color_hex).
    """
    if recyclability_score >= 0.80:
        return (
            "A",
            "Excellent — Highly recyclable waste with minimal environmental burden. Most materials can be recovered and reprocessed.",
            "#4CAF50",
        )
    elif recyclability_score >= 0.60:
        return (
            "B",
            "Good — Majority of waste is recyclable. Some materials require specialised handling but overall impact is manageable.",
            "#8BC34A",
        )
    elif recyclability_score >= 0.45:
        return (
            "C",
            "Moderate — Mixed recyclability. Consider separating materials more carefully to improve recovery rates.",
            "#FF9800",
        )
    elif recyclability_score >= 0.25:
        return (
            "D",
            "Poor — Low recyclability detected. Most materials require special disposal. Seek alternative products where possible.",
            "#FF5722",
        )
    else:
        return (
            "E",
            "Critical — Very low recyclability. Materials pose significant environmental risk. Professional disposal required.",
            "#F44336",
        )


def generate_disposal_instructions(composition: dict) -> list:
    """
    Generate ordered disposal action steps based on detected
    waste composition.

    Args:
        composition: Dict of {class_name: percentage}.

    Returns:
        List of instruction strings, ordered by composition percentage.
    """
    instructions = []

    for class_name, percentage in composition.items():
        if class_name not in WASTE_TAXONOMY:
            continue

        info = WASTE_TAXONOMY[class_name]
        decomp_display = get_decomposition_display(info["decomposition_time_years"])

        instruction = (
            f"{class_name} ({percentage}% of detected waste): "
            f"{info['disposal_method']} "
            f"Decomposition time: {decomp_display}."
        )
        instructions.append(instruction)

    if not instructions:
        instructions.append(
            "No specific waste detected. Please upload a clearer image for accurate classification."
        )

    return instructions


def compute_carbon_summary(composition: dict) -> dict:
    """
    Summarize carbon footprint categories across detected waste.

    Returns:
        Dict with keys 'low', 'medium', 'high' mapping to
        total percentage of waste in each category.
    """
    summary = {"low": 0.0, "medium": 0.0, "high": 0.0}

    for class_name, percentage in composition.items():
        if class_name in WASTE_TAXONOMY:
            category = WASTE_TAXONOMY[class_name]["carbon_footprint_category"]
            summary[category] += percentage

    # Round values
    return {k: round(v, 1) for k, v in summary.items()}


def compute_full_analysis(predictions: dict) -> dict:
    """
    Orchestrate complete environmental impact analysis.

    Args:
        predictions: Dict of {class_name: confidence_score} (filtered).

    Returns:
        Dict containing all computed metrics:
        - composition: percentage breakdown
        - recyclability_score: weighted score (0–1)
        - impact_rating: (letter, description, color)
        - disposal_instructions: ordered list of actions
        - carbon_summary: breakdown by footprint category
    """
    composition = compute_composition(predictions)
    recyclability_score = compute_recyclability_score(composition)
    impact_rating = compute_impact_rating(recyclability_score)
    disposal_instructions = generate_disposal_instructions(composition)
    carbon_summary = compute_carbon_summary(composition)

    return {
        "composition": composition,
        "recyclability_score": recyclability_score,
        "impact_rating": impact_rating,
        "disposal_instructions": disposal_instructions,
        "carbon_summary": carbon_summary,
    }
