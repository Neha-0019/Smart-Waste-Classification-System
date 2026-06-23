"""
report_generator.py — Session Report Generation

Takes a list of scan history entries and produces a pandas DataFrame
summary and matplotlib figures for session-level analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from collections import Counter

from taxonomy import WASTE_TAXONOMY

matplotlib.rcParams["font.family"] = "sans-serif"

# Theme colours
BG_DEEP = "#0D1F0F"
TEXT_PRIMARY = "#F0F4EE"
TEXT_SECONDARY = "#8AA88C"
ACCENT_LIME = "#B5FF4D"
BORDER_SAGE = "#3D6142"


def generate_summary_dataframe(history: list) -> pd.DataFrame:
    """
    Generate a pandas DataFrame summarizing all scans in the session.

    Args:
        history: List of scan entry dicts from history_manager.

    Returns:
        DataFrame with columns: Scan#, Time, Top Class, Confidence,
        Impact Rating, Recyclability Score.
    """
    if not history:
        return pd.DataFrame()

    rows = []
    for i, entry in enumerate(history, 1):
        top_class = entry["top_classes"][0] if entry["top_classes"] else "Unknown"
        top_confidence = entry["filtered_predictions"].get(top_class, 0)

        rows.append({
            "Scan": f"#{i}",
            "Time": entry["timestamp_display"],
            "Top Class": top_class,
            "Confidence": f"{top_confidence:.1%}",
            "Impact": entry["impact_rating"],
            "Recyclability": f"{entry['recyclability_score']:.1%}",
        })

    return pd.DataFrame(rows)


def generate_detailed_dataframe(history: list) -> pd.DataFrame:
    """
    Generate a detailed DataFrame with all detected classes per scan.

    Suitable for CSV export.
    """
    if not history:
        return pd.DataFrame()

    rows = []
    for i, entry in enumerate(history, 1):
        for class_name, confidence in entry["filtered_predictions"].items():
            pct = entry["composition"].get(class_name, 0)
            info = WASTE_TAXONOMY.get(class_name, {})

            rows.append({
                "Scan Number": i,
                "Timestamp": entry["timestamp_display"],
                "Waste Class": class_name,
                "Confidence": round(confidence, 4),
                "Composition %": pct,
                "Recyclability Index": info.get("recyclability_index", 0),
                "Decomposition Years": info.get("decomposition_time_years", 0),
                "Carbon Footprint": info.get("carbon_footprint_category", ""),
                "Disposal Method": info.get("disposal_method", ""),
                "Impact Rating": entry["impact_rating"],
                "Overall Recyclability": entry["recyclability_score"],
            })

    return pd.DataFrame(rows)


def generate_composition_chart(history: list) -> plt.Figure:
    """
    Generate a stacked bar chart showing waste composition
    across all scans in the session.

    Args:
        history: List of scan entry dicts.

    Returns:
        matplotlib Figure object.
    """
    if not history:
        return None

    # Collect all unique classes
    all_classes = set()
    for entry in history:
        all_classes.update(entry["composition"].keys())
    all_classes = sorted(all_classes)

    # Build data matrix
    scan_labels = [f"#{i+1}" for i in range(len(history))]
    data = {cls: [] for cls in all_classes}

    for entry in history:
        for cls in all_classes:
            data[cls].append(entry["composition"].get(cls, 0))

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG_DEEP)
    ax.set_facecolor(BG_DEEP)

    # Stacked bar chart
    x = np.arange(len(scan_labels))
    bar_width = 0.6
    bottom = np.zeros(len(scan_labels))

    colors = [WASTE_TAXONOMY.get(cls, {}).get("bin_color", "#8AA88C") for cls in all_classes]

    for cls, color in zip(all_classes, colors):
        values = data[cls]
        ax.bar(x, values, bar_width, bottom=bottom, label=cls, color=color,
               edgecolor=BG_DEEP, linewidth=0.5)
        bottom += np.array(values)

    ax.set_xlabel("Scan", color=TEXT_SECONDARY, fontsize=8, fontfamily="monospace")
    ax.set_ylabel("Composition %", color=TEXT_SECONDARY, fontsize=8, fontfamily="monospace")
    ax.set_xticks(x)
    ax.set_xticklabels(scan_labels, color=TEXT_PRIMARY, fontsize=7, fontfamily="monospace")
    ax.tick_params(axis="y", colors=TEXT_SECONDARY, labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(BORDER_SAGE)
    ax.spines["left"].set_color(BORDER_SAGE)

    legend = ax.legend(
        loc="upper right",
        fontsize=6,
        frameon=False,
        labelcolor=TEXT_PRIMARY,
    )

    plt.tight_layout()
    return fig


def generate_recyclability_trend(history: list) -> plt.Figure:
    """
    Generate a line chart showing recyclability score trend
    across scans.
    """
    if not history or len(history) < 2:
        return None

    fig, ax = plt.subplots(figsize=(8, 3), facecolor=BG_DEEP)
    ax.set_facecolor(BG_DEEP)

    scores = [entry["recyclability_score"] for entry in history]
    x = range(1, len(scores) + 1)

    ax.plot(x, scores, color=ACCENT_LIME, linewidth=2, marker="o",
            markersize=5, markerfacecolor=ACCENT_LIME, markeredgecolor=BG_DEEP,
            markeredgewidth=1.5)

    # Fill under line
    ax.fill_between(x, scores, alpha=0.15, color=ACCENT_LIME)

    ax.set_xlabel("Scan #", color=TEXT_SECONDARY, fontsize=8, fontfamily="monospace")
    ax.set_ylabel("Recyclability", color=TEXT_SECONDARY, fontsize=8, fontfamily="monospace")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="both", colors=TEXT_SECONDARY, labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(BORDER_SAGE)
    ax.spines["left"].set_color(BORDER_SAGE)

    # Add horizontal grid lines
    ax.yaxis.grid(True, color=BORDER_SAGE, alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig
