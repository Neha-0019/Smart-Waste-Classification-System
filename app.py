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
from taxonomy import WASTE_TAXONOMY, CARBON_COLORS, get_decomposition_display
from impact_calculator import compute_full_analysis
from report_generator import (
    generate_summary_dataframe,
    generate_detailed_dataframe,
    generate_composition_chart,
    generate_recyclability_trend,
)
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
.stButton > button, .stDownloadButton > button {
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

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--accent-lime);
    color: var(--accent-lime);
    background-color: rgba(181, 255, 77, 0.05);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: var(--bg-deep);
}
::-webkit-scrollbar-thumb {
    background: var(--border-sage);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--accent-lime);
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
# MAIN PANEL — Hero when no image, Results when image present
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

else:
    # ── Determine active image and predictions ──
    active_image = None
    active_predictions = None
    active_filtered = None
    active_analysis = None

    if "selected_scan_idx" in st.session_state:
        scan = get_scan_by_index(st.session_state["selected_scan_idx"])
        if scan:
            from history_manager import base64_to_image
            active_image = base64_to_image(scan["thumbnail_b64"])
            # Re-open at full resolution if we have the uploaded file
            if uploaded_file is not None:
                active_image = Image.open(uploaded_file)
            active_predictions = scan["predictions"]
            active_filtered = scan["filtered_predictions"]
            active_analysis = scan["analysis"]

    if active_image is None and uploaded_file is not None:
        active_image = Image.open(uploaded_file)
        raw_predictions = detector.predict(active_image)
        active_filtered = detector.filter_predictions(raw_predictions)
        active_predictions = raw_predictions
        active_analysis = compute_full_analysis(active_filtered)

        # Add to history
        if "last_uploaded_name" not in st.session_state or st.session_state["last_uploaded_name"] != uploaded_file.name:
            add_scan(active_image, active_predictions, active_filtered)
            st.session_state["last_uploaded_name"] = uploaded_file.name

    if active_image and active_analysis:
        composition = active_analysis["composition"]
        recyclability = active_analysis["recyclability_score"]
        impact_letter, impact_desc, impact_color = active_analysis["impact_rating"]
        disposal_instructions = active_analysis["disposal_instructions"]

        # ── Three-column layout: Main (60%) + Right panel (240px) ──
        main_col, spacer, right_col = st.columns([3, 0.1, 1])

        with main_col:
            # ── TOP ROW: Original + Grad-CAM ──
            st.markdown('<div class="section-label">Image Analysis</div>', unsafe_allow_html=True)
            img_left, img_right = st.columns(2)

            with img_left:
                st.markdown('<p style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px;">ORIGINAL</p>', unsafe_allow_html=True)
                st.image(active_image, use_container_width=True)

            with img_right:
                detected_classes = list(active_filtered.keys())
                gradcam_target = st.selectbox(
                    "Visualize attention for:",
                    options=detected_classes,
                    index=0,
                    key="gradcam_class_selector",
                    label_visibility="collapsed",
                )
                st.markdown(f'<p style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px;">GRAD-CAM — {gradcam_target}</p>', unsafe_allow_html=True)
                gradcam_overlay = detector.get_gradcam(active_image, gradcam_target)
                st.image(gradcam_overlay, use_container_width=True)

            # ── DETECTION RESULTS ──
            st.markdown('<div class="section-label">Detection Results</div>', unsafe_allow_html=True)

            for class_name, confidence in active_filtered.items():
                pct = composition.get(class_name, 0)
                info = WASTE_TAXONOMY.get(class_name, {})
                rec_idx = info.get("recyclability_index", 0)
                decomp = info.get("decomposition_time_years", 0)
                carbon = info.get("carbon_footprint_category", "medium")
                carbon_color = CARBON_COLORS.get(carbon, "#FF9800")
                bin_color = info.get("bin_color", "#8AA88C")
                bar_width = int(confidence * 100)
                decomp_display = get_decomposition_display(decomp)

                # SVG circular arc for recyclability
                arc_radius = 20
                arc_circumference = 2 * 3.14159 * arc_radius
                arc_filled = arc_circumference * rec_idx
                arc_empty = arc_circumference - arc_filled

                st.markdown(f"""
                <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                            padding: 0; margin-bottom: 8px; display: flex; overflow: hidden;">
                    <div style="width: 4px; background: {bin_color}; flex-shrink: 0;"></div>
                    <div style="padding: 16px; flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span style="font-family: var(--font-display); font-weight: 700; font-size: 1rem;">
                                    {class_name}
                                </span>
                                <span style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);
                                             margin-left: 8px;">{pct}% of waste</span>
                            </div>
                            <span style="font-family: var(--font-mono); font-size: 0.9rem; color: var(--accent-lime);
                                         font-weight: 600;">
                                {confidence:.1%}
                            </span>
                        </div>
                        <div style="background: rgba(181, 255, 77, 0.08); height: 6px; width: 100%; margin-bottom: 14px;">
                            <div style="background: linear-gradient(90deg, var(--accent-lime), #8FCC3D);
                                        height: 100%; width: {bar_width}%; transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);"></div>
                        </div>
                        <div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <svg width="48" height="48" viewBox="0 0 48 48">
                                    <circle cx="24" cy="24" r="{arc_radius}" fill="none" stroke="rgba(181,255,77,0.1)"
                                            stroke-width="3" transform="rotate(-90 24 24)"/>
                                    <circle cx="24" cy="24" r="{arc_radius}" fill="none" stroke="#B5FF4D"
                                            stroke-width="3" stroke-dasharray="{arc_filled:.1f} {arc_empty:.1f}"
                                            stroke-linecap="round" transform="rotate(-90 24 24)"
                                            style="transition: stroke-dasharray 0.8s ease;"/>
                                    <text x="24" y="26" text-anchor="middle" fill="#F0F4EE"
                                          font-family="JetBrains Mono" font-size="9" font-weight="600">
                                        {rec_idx:.0%}
                                    </text>
                                </svg>
                                <span style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);">
                                    Recyclability
                                </span>
                            </div>
                            <div style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-secondary);">
                                ⏱ <span style="color: var(--text-primary); font-weight: 500;">{decomp_display}</span>
                            </div>
                            <div style="font-family: var(--font-mono); font-size: 0.7rem; display: flex; align-items: center; gap: 4px;">
                                <span style="display: inline-block; width: 8px; height: 8px; background: {carbon_color};"></span>
                                <span style="color: {carbon_color}; font-weight: 600;">{carbon.upper()}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


            # ── COMPOSITION PIE CHART ──
            st.markdown('<div class="section-label">Composition Breakdown</div>', unsafe_allow_html=True)

            import matplotlib.pyplot as plt
            import matplotlib

            matplotlib.rcParams["font.family"] = "sans-serif"

            fig, ax = plt.subplots(figsize=(6, 4), facecolor="#0D1F0F")
            ax.set_facecolor("#0D1F0F")

            labels = list(composition.keys())
            sizes = list(composition.values())
            colors = [WASTE_TAXONOMY.get(c, {}).get("bin_color", "#8AA88C") for c in labels]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=None,
                colors=colors,
                autopct="%1.1f%%",
                startangle=90,
                pctdistance=0.78,
                wedgeprops={"linewidth": 1.5, "edgecolor": "#0D1F0F"},
            )

            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_color("#F0F4EE")
                autotext.set_fontfamily("monospace")
                autotext.set_fontweight("bold")

            # Draw centre circle for donut effect
            centre_circle = plt.Circle((0, 0), 0.55, fc="#0D1F0F")
            ax.add_artist(centre_circle)

            # Legend
            legend = ax.legend(
                wedges,
                [f"{label} ({size}%)" for label, size in zip(labels, sizes)],
                loc="center left",
                bbox_to_anchor=(1, 0.5),
                fontsize=7,
                frameon=False,
                labelcolor="#F0F4EE",
            )

            ax.set_aspect("equal")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            # ── DISPOSAL INSTRUCTIONS ──
            st.markdown('<div class="section-label">Disposal Instructions</div>', unsafe_allow_html=True)
            for i, instruction in enumerate(disposal_instructions, 1):
                st.markdown(f"""
                <div style="display: flex; gap: 12px; margin-bottom: 10px; padding: 10px;
                            background: var(--bg-surface); border: 1px solid var(--border-sage);">
                    <span style="font-family: var(--font-display); font-weight: 700; font-size: 1.1rem;
                                 color: var(--accent-lime); min-width: 24px;">{i}</span>
                    <span style="font-family: var(--font-body); font-size: 0.85rem; color: var(--text-primary);
                                 line-height: 1.5;">{instruction}</span>
                </div>
                """, unsafe_allow_html=True)

            # ── ENVIRONMENTAL IMPACT SCORE ──
            st.markdown('<div class="section-label">Environmental Impact Score</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                        padding: 24px; text-align: center;">
                <div style="font-family: var(--font-display); font-weight: 800; font-size: 4rem;
                            color: {impact_color}; line-height: 1;">{impact_letter}</div>
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-secondary);
                            margin-top: 8px; max-width: 400px; margin-left: auto; margin-right: auto;">
                    {impact_desc}
                </div>
                <div style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-secondary);
                            margin-top: 12px;">
                    Weighted Recyclability Score:
                    <span style="color: var(--accent-lime); font-weight: 600;">{recyclability:.1%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── RIGHT PANEL ──
        with right_col:
            stats = get_session_stats()

            st.markdown('<div class="section-label">Session Summary</div>', unsafe_allow_html=True)

            # Stat cards
            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                        padding: 14px; margin-bottom: 8px;">
                <div style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);
                            text-transform: uppercase; letter-spacing: 1px;">Total Scans</div>
                <div style="font-family: var(--font-display); font-weight: 700; font-size: 1.8rem;
                            color: var(--accent-lime); margin-top: 4px;">{stats['total_scans']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                        padding: 14px; margin-bottom: 8px;">
                <div style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);
                            text-transform: uppercase; letter-spacing: 1px;">Most Frequent</div>
                <div style="font-family: var(--font-display); font-weight: 700; font-size: 1rem;
                            color: var(--text-primary); margin-top: 4px;">{stats['most_frequent_type']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                        padding: 14px; margin-bottom: 8px;">
                <div style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);
                            text-transform: uppercase; letter-spacing: 1px;">Avg Recyclability</div>
                <div style="font-family: var(--font-display); font-weight: 700; font-size: 1.8rem;
                            color: var(--accent-lime); margin-top: 4px;">{stats['avg_recyclability']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-sage);
                        padding: 14px; margin-bottom: 8px;">
                <div style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary);
                            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Grade Distribution</div>
                <div style="display: flex; gap: 6px; justify-content: space-between;">
                    <div style="text-align: center; flex: 1; padding: 4px 2px; background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 4px;">
                        <div style="font-family: var(--font-mono); font-size: 0.7rem; color: #4CAF50; font-weight: bold;">A</div>
                        <div style="font-family: var(--font-display); font-size: 0.85rem; color: var(--text-primary); font-weight: 700; margin-top: 2px;">{stats['impact_distribution'].get('A', 0)}</div>
                    </div>
                    <div style="text-align: center; flex: 1; padding: 4px 2px; background: rgba(139, 195, 74, 0.1); border: 1px solid #8BC34A; border-radius: 4px;">
                        <div style="font-family: var(--font-mono); font-size: 0.7rem; color: #8BC34A; font-weight: bold;">B</div>
                        <div style="font-family: var(--font-display); font-size: 0.85rem; color: var(--text-primary); font-weight: 700; margin-top: 2px;">{stats['impact_distribution'].get('B', 0)}</div>
                    </div>
                    <div style="text-align: center; flex: 1; padding: 4px 2px; background: rgba(255, 152, 0, 0.1); border: 1px solid #FF9800; border-radius: 4px;">
                        <div style="font-family: var(--font-mono); font-size: 0.7rem; color: #FF9800; font-weight: bold;">C</div>
                        <div style="font-family: var(--font-display); font-size: 0.85rem; color: var(--text-primary); font-weight: 700; margin-top: 2px;">{stats['impact_distribution'].get('C', 0)}</div>
                    </div>
                    <div style="text-align: center; flex: 1; padding: 4px 2px; background: rgba(255, 87, 34, 0.1); border: 1px solid #FF5722; border-radius: 4px;">
                        <div style="font-family: var(--font-mono); font-size: 0.7rem; color: #FF5722; font-weight: bold;">D</div>
                        <div style="font-family: var(--font-display); font-size: 0.85rem; color: var(--text-primary); font-weight: 700; margin-top: 2px;">{stats['impact_distribution'].get('D', 0)}</div>
                    </div>
                    <div style="text-align: center; flex: 1; padding: 4px 2px; background: rgba(244, 67, 54, 0.1); border: 1px solid #F44336; border-radius: 4px;">
                        <div style="font-family: var(--font-mono); font-size: 0.7rem; color: #F44336; font-weight: bold;">E</div>
                        <div style="font-family: var(--font-display); font-size: 0.85rem; color: var(--text-primary); font-weight: 700; margin-top: 2px;">{stats['impact_distribution'].get('E', 0)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Batch report
            st.markdown('<div class="section-label">Reports</div>', unsafe_allow_html=True)

            if stats["total_scans"] >= 1:
                if st.button("Generate Batch Report", key="batch_report_btn", use_container_width=True):
                    st.session_state["show_batch_report"] = True

                if st.session_state.get("show_batch_report", False):
                    current_history = get_history()
                    summary_df = generate_summary_dataframe(current_history)

                    if not summary_df.empty:
                        st.markdown('<p style="font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-secondary); margin-top: 10px;">SESSION SUMMARY</p>', unsafe_allow_html=True)
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)

                    comp_chart = generate_composition_chart(current_history)
                    if comp_chart:
                        st.pyplot(comp_chart, use_container_width=True)
                        plt.close(comp_chart)

                    trend_chart = generate_recyclability_trend(current_history)
                    if trend_chart:
                        st.pyplot(trend_chart, use_container_width=True)
                        plt.close(trend_chart)

                    detailed_df = generate_detailed_dataframe(current_history)
                    if not detailed_df.empty:
                        csv_data = detailed_df.to_csv(index=False).encode('utf-8')
                        st.markdown('<div style="margin-top: 14px;"></div>', unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Export Session Data (CSV)",
                            data=csv_data,
                            file_name="waste_analysis_session_report.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="export_csv_btn",
                        )
            else:
                st.markdown(
                    '<p style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-secondary); text-align: center; padding: 12px;">'
                    'Scan at least one image to generate reports.</p>',
                    unsafe_allow_html=True,
                )

