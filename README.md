# ♻️ Smart Waste Classification System (WasteAI)

An AI-powered computer vision and environmental analytics application that detects, classifies, and analyzes waste materials in real time. Built using Python, PyTorch, Streamlit, OpenCV, and Grad-CAM, the system combines deep learning models with a polished Forest Green + Electric Lime developer-brutalist theme to deliver interactive, explainable, and actionable waste management insights.

---

## 📌 Project Overview

Traditional waste classification systems struggle to address mixed-material waste and explain why classifications are made. **WasteAI** addresses these limitations by providing:
- **PyTorch Inference**: Dual-mode inference supporting a fine-tuned EfficientNet-B3 architecture and an intelligent color-space bias mock model.
- **Explainable AI (XAI)**: High-resolution Grad-CAM (Gradient-weighted Class Activation Mapping) overlays to visualize feature-level model attention for any detected class.
- **Ecological Impact Analysis**: Instant carbon footprint assessment, weighted recyclability scores (0–100%), and dynamic A–E grade assignments.
- **Session-scoped Tracking**: Locally cached database storing thumbnail-indexed scans with sorting, viewing, and clearing operations.
- **Exportable Analytics**: Matplotlib-based composition breakdown charts, historical recyclability trend visualizations, and direct CSV exporting.

---

## 🚀 Features

- **Multi-Label Inference**: Identifies multiple waste materials in a single image with confidence progress bars.
- **Taxonomy recommendations**: Outlines precise disposal methods, decomposition timelines, and carbon footprint levels for 9 categories.
- **Visual Attention (Grad-CAM)**: Dropdown class selector displays target feature heatmaps using `pytorch-grad-cam` to explain classification decisions.
- **Session Summary Metrics**: Real-time counters showing *Total Scans*, *Most Frequent Type*, and *Average Recyclability*.
- **Interactive Batch Reports**: Stacked composition bar charts and a line graph showing recyclability progress over time.
- **CSV Data Export**: Single-click downloads for comprehensive offline database analyses.

---

## 📂 Project Structure

```text
Smart-Waste-Classification-System/
├── .streamlit/
│   └── config.toml          # Custom theme configuration
├── app.py                   # Main Streamlit web application & UI layout
├── taxonomy.py              # Waste classes mapping & environmental metrics
├── waste_detector.py        # EfficientNet-B3 model and Grad-CAM engine
├── impact_calculator.py     # Weighted recyclability & carbon calculations
├── history_manager.py       # Session state scan database & statistics
├── report_generator.py      # Pandas dataframes & Matplotlib chart generators
├── requirements.txt         # Project package dependencies
└── README.md                # System documentation
```

---

## 🛠️ Tech Stack & Dependencies

- **Framework**: Streamlit (v1.32+)
- **Deep Learning**: PyTorch (v2.0+), torchvision
- **Explainability**: pytorch-grad-cam
- **Computer Vision**: OpenCV (headless), Pillow
- **Data & Charts**: Pandas, Matplotlib, NumPy

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SOUMYA0023/Smart-Waste-Classification-System.git
cd Smart-Waste-Classification-System
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 💡 Usage Guide

1. **Upload an Image**: Drag & drop or browse for a waste image in the sidebar file uploader.
2. **Review Predictions**: View classification confidences, decomposition timelines, and carbon footprint grades on the dashboard cards.
3. **Inspect Attention Maps**: Choose a class from the Grad-CAM dropdown selection to see exactly which features triggered the prediction.
4. **Track History**: Click past scans in the sidebar to review detailed results or clear the history at any time.
5. **Generate Batch Reports**: Click **Generate Batch Report** under the session stats panel to view aggregated analysis plots and click **Export Session Data (CSV)** to download the raw data.
