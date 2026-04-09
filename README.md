# ⚡ Hierarchical Intrusion Detection System (H-IDS)

## 📖 Overview

The Hierarchical Intrusion Detection System (H-IDS) is a cyber-physical monitoring platform designed for power grid systems.  
It integrates physical disturbance analysis, machine learning detection, and interactive operator control into a unified real-time dashboard.

This system is developed as part of a research project to simulate and analyse cyber-physical attacks in smart grids.

---

## 🎯 Key Objectives

- Detect abnormal behaviour in power grid data  
- Identify the most affected relay (physical impact)  
- Classify attack scenarios using machine learning  
- Provide real-time visualisation and explainability  
- Enable human-in-the-loop decision making  

---

## 🧩 System Components

### 1. Data Pipeline
- Handles Debug and Live modes  
- Loads and processes PMU-based datasets  
- Controls data streaming behaviour  

### 2. Physical Layer
- Computes disturbance scores for each relay  
- Simulates grid state (relay, breaker, line, bus, generator)  
- Provides explainable system behaviour  

### 3. Machine Learning Layer
- Performs attack detection and classification  
- Outputs confidence, scenario, and contributing factors  

Detailed ML explanation: ML_SYSTEM.md

---

### 4. Fusion Layer
- Determines the most affected relay using physical signals  
- Bridges system measurements with detection results  

---

### 5. Event System
- Tracks system activity as structured events:
  - Physical (P)
  - IDS/ML (M)
  - User actions (U)

---

### 6. User Interface
- Built with Streamlit  
- Provides interactive monitoring dashboard  

Full system design: SYSTEM_ARCHITECTURE.md

---

## 🧪 Operating Modes

### Debug Mode
- Uses labelled dataset  
- Sequential playback  
- Ideal for testing and validation  

### Live Mode
- Uses the same dataset but treats it as raw input  
- Bypasses pre-cleaned data  
- Passes data through a preprocessing pipeline (engine.preprocessing)  
- Simulates real-world streaming data ingestion  
- Produces non-deterministic behaviour via random sampling  

---

## 🚀 How to Run

### 1. Install dependencies
pip install -r requirements.txt

### 2. Start the application
streamlit run app.py

### 3. Select mode
- Debug Mode → controlled simulation  
- Live Mode → simulated real-time behaviour  

---

## 🖥 Key Features

- Interactive grid visualisation (relay, breaker, line, bus, generator)  
- Real-time PMU waveform plotting (Phase A, B, C)  

- Physical measurement panel (PMU-based):
  - Voltage, Current, Frequency  
  - Sequence component analysis (Positive, Negative, Zero)  
  - Impedance anomaly detection  

- Machine learning-based intrusion detection  
- IDS alert detection panel with confidence scoring  
- Event investigation modal (Physical + IDS + User layers)  
- Real-time event logging system  
- Operator control actions:
  - Isolate  
  - Lock  
  - Restore  

---

## 🔗 System Workflow

Input Data → Physical Layer → ML Detection → Fusion → Event → UI

---

## 📁 Project Structure

app.py  
pages/  
    Dashboard.py  

engine/
    __init__.py  
    inference.py  
    disturbance.py  
    scoring.py  
    physical_layer.py  
    explainer.py  
    preprocessing.py 
    measurements.py
    pmu_history.py
    utils.py
ui/  
    styles.py  
    header.py  
    event_modal.py  
    grid_diagram.py  

helpers/  
    event_helpers.py  

data/  
    merged/  

---

## ⚠️ Known Behaviour

- System pauses during investigation (by design)  
- Live mode may generate rapid event streams  
- Streamlit reruns may cause UI refresh behaviour  
- Import reload issues may occasionally appear during development  

---

## 📌 Notes

- Live Mode does NOT use true real-time data  
- Instead, it simulates real-world conditions by:
  - Using unprocessed dataset samples  
  - Passing them through a preprocessing pipeline  

- The system separates:
  - Detection (ML layer)  
  - Physical reasoning (disturbance analysis)  

- This improves:
  - Interpretability  
  - Reliability  
  - Debugging capability  

- This approach provides a balance between:
  - Reproducibility (Debug Mode)  
  - Realism (Live Mode simulation)  

---

## 📚 Documentation

- Machine Learning Module → ML_SYSTEM.md  
- System Architecture → SYSTEM_ARCHITECTURE.md  

---

## 👩‍💻 Author

Final Year Project — Cyber-Physical Intrusion Detection System  