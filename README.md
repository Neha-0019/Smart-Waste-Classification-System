# ♻️ WasteVision-AI

### Smart Waste Classification for Smart Waste Management using Computer Vision and Deep Learning

![Python](https://img.shields.io/badge/Python-3.11-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Project Overview

WasteVision-AI is an AI-powered smart waste classification system designed to automate waste segregation using Computer Vision and Deep Learning.

The system classifies waste images into multiple categories and recommends the appropriate disposal method, helping improve recycling efficiency and sustainable waste management practices.

The project combines:

* Deep Learning
* Computer Vision
* Real-Time Webcam Detection
* Flask Web Application
* SQLite Database
* Waste Disposal Recommendation Engine

---

## 🚀 Features

### 🔍 Waste Classification

Classifies waste into 9 categories:

| Class        | Description                              |
| ------------ | ---------------------------------------- |
| Cardboard    | Packaging boxes and corrugated materials |
| Glass        | Bottles, jars, and glass waste           |
| Metal        | Cans, tins, and metallic waste           |
| Paper        | Newspapers, magazines, and office paper  |
| Plastic Hard | Bottles and rigid plastic containers     |
| Plastic Soft | Plastic bags, wrappers, and films        |
| Organic      | Food scraps and biodegradable waste      |
| E-Waste      | Electronics, batteries, and cables       |
| Textile      | Clothes, fabric scraps, and footwear     |

---

### ♻️ Disposal Recommendation System

After classification, the system recommends the correct disposal method.

Example:

| Waste Type   | Disposal Method             |
| ------------ | --------------------------- |
| Cardboard    | Recyclable Bin              |
| Glass        | Recyclable Bin              |
| Metal        | Recyclable Bin              |
| Paper        | Recyclable Bin              |
| Plastic Hard | Recyclable Bin              |
| Plastic Soft | Soft Plastic Collection Bin |
| Organic      | Compost Bin                 |
| E-Waste      | E-Waste Collection Point    |
| Textile      | Textile Recycling Bin       |

---

### 🌍 Environmental Impact Awareness

Each prediction includes environmental impact information to promote sustainable disposal practices.

Example:

> Soft plastics may take hundreds of years to decompose and should be recycled separately.

---

### 📷 Real-Time Webcam Detection

* Live waste classification
* Confidence score display
* FPS monitoring
* Disposal recommendation overlay
* Screenshot capture support

---

### 📊 Analytics Dashboard

* Prediction history
* Most common waste category
* Average confidence score
* Class distribution charts
* Dataset quality reports

---

## 🏗️ Project Architecture

```text
Image Input
      │
      ▼
Preprocessing
      │
      ▼
EfficientNetV2B0
      │
      ▼
Waste Classification
      │
      ▼
Disposal Recommendation
      │
      ▼
SQLite Database
      │
      ▼
Flask Dashboard
```

## 🧠 Model Architecture

### Backbone

* EfficientNetV2B0
* ImageNet Pretrained Weights

### Input

```python
224 x 224 x 3
```

### Classification Head

```python
GlobalAveragePooling2D()

BatchNormalization()

Dense(512, activation="relu")

Dropout(0.5)

Dense(256, activation="relu")

Dropout(0.4)

Dense(9, activation="softmax")
```

### Training Strategy

#### Phase A

* Freeze Backbone
* Train Classification Head

#### Phase B

* Unfreeze Last 50 Layers
* Fine Tune Model

#### Phase C

* Fine Tune Entire Network

---

## 📂 Project Structure

```text
WasteVision-AI/

├── dataset/
│   ├── raw/
│   └── processed/
│
├── models/
│
├── reports/
│
├── static/
│
├── templates/
│
├── config.py
├── database.py
├── data_prep.py
├── train.py
├── evaluate.py
├── predict.py
├── webcam_detection.py
├── app.py
├── requirements.txt
├── README.md
└── wastevision.db
```

---

## 📥 Dataset Setup

Create:

```text
dataset/raw/
```

Add the following folders:

```text
cardboard
glass
metal
paper
plastic_hard
plastic_soft
organic
e_waste
textile
```

### Dataset Sources

* Garbage Classification Dataset
* TACO Dataset
* Waste Classification Data
* E-Waste Images Dataset
* Textile Waste Image Dataset

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/WasteVision-AI.git

cd WasteVision-AI
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗂️ Prepare Dataset

```bash
python data_prep.py
```

This will:

* Validate images
* Remove duplicates
* Detect blurry images
* Create train/validation/test splits
* Generate dataset quality reports

---

## 🏋️ Train the Model

```bash
python train.py
```

Training stages:

* Phase A
* Phase B
* Phase C

Outputs:

```text
models/
reports/
```

---

## 📈 Evaluate the Model

```bash
python evaluate.py
```

Generated reports:

* Accuracy
* Precision
* Recall
* F1 Score
* Top-3 Accuracy
* Confusion Matrix
* Classification Report

---

## 🖼️ Single Image Prediction

```bash
python predict.py --image sample.jpg
```

Example Output:

```text
Predicted Class : Plastic Soft

Confidence      : 92.4%

Disposal Method : Soft Plastic Collection Bin
```

---

## 📷 Webcam Detection

```bash
python webcam_detection.py
```

Controls:

```text
Q -> Quit

S -> Save Screenshot
```

---

## 🌐 Run Flask Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Available Pages:

* Home
* Predict
* Classes
* History
* Analytics Dashboard

---

## 📊 Database

Database:

```text
wastevision.db
```

Stores:

* Prediction history
* Confidence scores
* Disposal recommendations
* Timestamps

---

## 📌 Future Enhancements

* TensorFlow Lite Deployment
* Mobile Application
* Smart IoT Waste Bin Integration
* YOLO-Based Waste Detection
* Multi-Object Waste Recognition
* Cloud Deployment

---

## 🎓 Academic Significance

This project demonstrates concepts from:

* Computer Vision
* Deep Learning
* Transfer Learning
* Image Classification
* Web Development
* Database Systems
* Sustainable Computing

---

## 👩‍💻 Author

**Neha Panbude**

B.Tech Computer Science Engineering
SRM Institute of Science and Technology

---

## 📜 License

This project is released under the MIT License.

---

## ⭐ If you found this project useful, consider giving it a star on GitHub!
