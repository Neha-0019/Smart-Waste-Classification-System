"""
app.py — WasteAI Streamlit Application

Main entry point for the Smart Waste Detection System.
Provides a three-panel interface for waste classification,
Grad-CAM visualization, and environmental impact analysis.
"""

import streamlit as st

st.set_page_config(
    page_title="WasteAI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)
