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

from PIL import Image
from waste_detector import WasteDetector
from history_manager import (
    add_scan,
    get_history,
    clear_history,
    get_scan_by_index,
    get_session_stats,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — Custom theme injection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg-deep: #0D1F0F;
    --bg-surface: #162A18;
    --border-sage: #3D6142;
    --accent-lime: #B5FF4D;
    --text-primary: #F0F4EE;
    --text-secondary: #8AA88C;
    --font-display: 'Syne', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Global body */
.stApp {
    background-color: var(--bg-deep);
    font-family: var(--font-body);
    color: var(--text-primary);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: var(--bg-surface);
    border-right: 1px solid var(--border-sage);
    width: 280px !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary);
    font-family: var(--font-body);
    font-size: 0.85rem;
}

/* Wordmark styling */
.wordmark {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 1.8rem;
    color: var(--accent-lime);
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
    padding: 0;
}

.wordmark-icon {
    width: 28px;
    height: 28px;
}

.wordmark-sub {
    font-family: var(--font-body);
    font-weight: 400;
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: -4px;
    margin-bottom: 20px;
}

/* Upload area */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border: 1px dashed var(--border-sage);
    border-radius: 0;
    padding: 8px;
    background: rgba(61, 97, 66, 0.1);
}

/* Sidebar thumbnail */
.sidebar-thumbnail {
    border: 1px solid var(--border-sage);
    margin: 10px 0;
}

/* History entry */
.history-entry {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    border: 1px solid var(--border-sage);
    background: var(--bg-deep);
    margin-bottom: 6px;
    cursor: pointer;
    transition: border-color 0.2s ease;
}

.history-entry:hover {
    border-color: var(--accent-lime);
}

.history-thumb {
    width: 40px;
    height: 40px;
    object-fit: cover;
    flex-shrink: 0;
}

.history-info {
    flex: 1;
    min-width: 0;
}

.history-class {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.history-time {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--text-secondary);
}

.history-badge {
    font-family: var(--font-mono);
    font-weight: 600;
    font-size: 0.75rem;
    padding: 2px 6px;
    border: 1px solid;
    flex-shrink: 0;
}

/* Section labels */
.section-label {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-sage);
}

/* Hero section */
.hero-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    text-align: center;
    padding: 40px 20px;
}

.hero-tagline {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 3.2rem;
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 16px;
    letter-spacing: -1px;
}

.hero-tagline span {
    color: var(--accent-lime);
}

.hero-subtitle {
    font-family: var(--font-body);
    font-weight: 300;
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 440px;
    line-height: 1.5;
}

/* Button overrides */
.stButton > button {
    background-color: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-sage);
    border-radius: 0;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s ease;
    width: 100%;
}

.stButton > button:hover {
    border-color: var(--accent-lime);
    color: var(--accent-lime);
    background-color: rgba(181, 255, 77, 0.05);
}

/* Divider */
.sidebar-divider {
    height: 1px;
    background: var(--border-sage);
    margin: 16px 0;
    opacity: 0.5;
}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Initialize detector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_resource
def load_detector():
    """Load and cache the WasteDetector instance."""
    return WasteDetector()


detector = load_detector()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div class="wordmark">
        <svg class="wordmark-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L8.5 8.5L2 12L8.5 15.5L12 22L15.5 15.5L22 12L15.5 8.5L12 2Z" 
                  fill="#B5FF4D" opacity="0.2"/>
            <path d="M7.5 7.5C9.5 5.5 12 4.5 12 4.5C12 4.5 14.5 5.5 16.5 7.5C18.5 9.5 19.5 12 19.5 12C19.5 12 18.5 14.5 16.5 16.5C14.5 18.5 12 19.5 12 19.5C12 19.5 9.5 18.5 7.5 16.5C5.5 14.5 4.5 12 4.5 12C4.5 12 5.5 9.5 7.5 7.5Z" 
                  stroke="#B5FF4D" stroke-width="1.5" fill="none"/>
            <path d="M12 8V12L14.5 14.5" stroke="#B5FF4D" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="12" cy="12" r="1.5" fill="#B5FF4D"/>
        </svg>
        WasteAI
    </div>
    <div class="wordmark-sub">Smart Waste Classification System</div>
    """, unsafe_allow_html=True)

    # Upload control
    st.markdown('<div class="section-label">Upload Image</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a waste image for classification",
        type=["jpg", "jpeg", "png", "webp"],
        key="waste_upload",
        label_visibility="collapsed",
    )

    # Thumbnail preview
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

    # Scan History
    st.markdown('<div class="section-label">Scan History</div>', unsafe_allow_html=True)
    history = get_history()

    if history:
        for idx, entry in enumerate(reversed(history)):
            real_idx = len(history) - 1 - idx
            top_class = entry["top_classes"][0] if entry["top_classes"] else "Unknown"
            badge_color = entry.get("impact_color", "#8AA88C")

            st.markdown(f"""
            <div class="history-entry" id="history-{real_idx}">
                <img class="history-thumb" src="data:image/jpeg;base64,{entry['thumbnail_b64']}" alt="scan {real_idx + 1}"/>
                <div class="history-info">
                    <div class="history-class">{top_class}</div>
                    <div class="history-time">{entry['timestamp_display']}</div>
                </div>
                <div class="history-badge" style="color: {badge_color}; border-color: {badge_color};">{entry['impact_rating']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Clickable button to reload this scan
            if st.button(f"View scan #{real_idx + 1}", key=f"hist_{real_idx}", use_container_width=True):
                st.session_state["selected_scan_idx"] = real_idx
                st.rerun()
    else:
        st.markdown(
            '<p style="font-size: 0.8rem; color: var(--text-secondary); text-align: center; padding: 20px 0;">'
            'No scans yet. Upload an image to begin.</p>',
            unsafe_allow_html=True,
        )

    # Clear History
    if history:
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        if st.button("Clear History", key="clear_history"):
            clear_history()
            if "selected_scan_idx" in st.session_state:
                del st.session_state["selected_scan_idx"]
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN PANEL — Hero when no image
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if uploaded_file is None and "selected_scan_idx" not in st.session_state:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-tagline">See What<br/>Others <span>Miss.</span></div>
        <div class="hero-subtitle">
            Upload a waste image to identify materials, assess environmental impact,
            and receive actionable disposal guidance powered by deep learning.
        </div>
    </div>
    """, unsafe_allow_html=True)
