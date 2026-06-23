"""
history_manager.py — Session Scan History

Manages a session-scoped scan history list stored in st.session_state.
Provides add_scan(), get_history(), clear_history(), and get_session_stats().
Each entry stores timestamp, image thumbnail as base64, top detected
classes, overall impact rating, and full prediction data.
"""

import io
import base64
from datetime import datetime
from collections import Counter

from PIL import Image
import streamlit as st

from impact_calculator import compute_full_analysis

THUMBNAIL_SIZE = (80, 80)
HISTORY_KEY = "scan_history"


def _init_history():
    """Ensure scan_history exists in session state."""
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []


def _image_to_base64(image_pil: Image.Image) -> str:
    """Convert a PIL image to a base64-encoded JPEG string."""
    thumb = image_pil.copy()
    thumb.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
    buffer = io.BytesIO()
    thumb.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def base64_to_image(b64_string: str) -> Image.Image:
    """Convert a base64 JPEG string back to a PIL image."""
    raw = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(raw))


def add_scan(
    image_pil: Image.Image,
    predictions: dict,
    filtered_predictions: dict,
) -> dict:
    """
    Add a new scan entry to session history.

    Args:
        image_pil: Original uploaded image.
        predictions: Full prediction dict (all 9 classes).
        filtered_predictions: Predictions above confidence threshold.

    Returns:
        The scan entry dict that was added.
    """
    _init_history()

    analysis = compute_full_analysis(filtered_predictions)

    # Get top 3 classes by confidence
    sorted_preds = sorted(
        filtered_predictions.items(), key=lambda x: x[1], reverse=True
    )
    top_classes = [cls for cls, _ in sorted_preds[:3]]

    entry = {
        "timestamp": datetime.now().isoformat(),
        "timestamp_display": datetime.now().strftime("%H:%M:%S"),
        "thumbnail_b64": _image_to_base64(image_pil),
        "top_classes": top_classes,
        "impact_rating": analysis["impact_rating"][0],  # letter grade
        "impact_color": analysis["impact_rating"][2],  # color hex
        "predictions": predictions,
        "filtered_predictions": filtered_predictions,
        "composition": analysis["composition"],
        "recyclability_score": analysis["recyclability_score"],
        "analysis": analysis,
    }

    st.session_state[HISTORY_KEY].append(entry)
    return entry


def get_history() -> list:
    """
    Return the full scan history list.

    Returns:
        List of scan entry dicts, ordered by time (oldest first).
    """
    _init_history()
    return st.session_state[HISTORY_KEY]


def get_scan_by_index(index: int) -> dict | None:
    """
    Retrieve a specific scan entry by index.

    Args:
        index: Position in history list.

    Returns:
        Scan entry dict, or None if index is out of range.
    """
    _init_history()
    history = st.session_state[HISTORY_KEY]
    if 0 <= index < len(history):
        return history[index]
    return None


def clear_history():
    """Clear all scan history from the session."""
    st.session_state[HISTORY_KEY] = []


def get_session_stats() -> dict:
    """
    Compute live session summary statistics.

    Returns:
        Dict containing:
        - total_scans: int
        - most_frequent_type: str or "—"
        - avg_recyclability: float
        - impact_distribution: dict of {grade: count}
    """
    _init_history()
    history = st.session_state[HISTORY_KEY]

    if not history:
        return {
            "total_scans": 0,
            "most_frequent_type": "—",
            "avg_recyclability": 0.0,
            "impact_distribution": {},
        }

    # Count most frequent top-1 class across all scans
    top1_classes = [entry["top_classes"][0] for entry in history if entry["top_classes"]]
    class_counts = Counter(top1_classes)
    most_frequent = class_counts.most_common(1)[0][0] if class_counts else "—"

    # Average recyclability score
    recyclability_scores = [
        entry["recyclability_score"] for entry in history
    ]
    avg_recyclability = round(
        sum(recyclability_scores) / len(recyclability_scores), 3
    )

    # Impact grade distribution
    impact_grades = [entry["impact_rating"] for entry in history]
    impact_distribution = dict(Counter(impact_grades))

    return {
        "total_scans": len(history),
        "most_frequent_type": most_frequent,
        "avg_recyclability": avg_recyclability,
        "impact_distribution": impact_distribution,
    }
