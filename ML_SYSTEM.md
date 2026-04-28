# 🧠 Machine Learning Module (ML System)

---

## 📖 Overview

The Machine Learning (ML) module is the **data-driven detection component**  
of the Hierarchical Intrusion Detection System (H-IDS).

It is responsible for:

- Detecting whether system behaviour is normal or anomalous  
- Classifying the type of disturbance or cyber-attack  
- Providing probabilistic confidence for decision-making  
- Supporting explainability through feature importance  

Unlike the physical layer, which relies on system rules and baseline comparison,  
the ML module **learns patterns directly from historical PMU data**.

---

## 📊 Dataset and Feature Space

The ML system is trained on a **multi-class PMU dataset** representing  
power grid behaviour under different conditions.

- Total samples: ~78,000  
- Features: ~130 electrical measurements  
- Scenarios: 37 distinct system conditions  

Note: Scenario IDs range from 1 to 41 but are **non-continuous**,  
resulting in 37 valid scenarios.

### 📌 Feature Types

The dataset includes measurements extracted from PMUs (Phasor Measurement Units), such as:

- Voltage magnitude (Phase A, B, C)  
- Current magnitude (Phase A, B, C)  
- Voltage angle  
- Current angle  
- Frequency and frequency deviation  
- Sequence components (Positive, Negative, Zero)  
- Impedance and impedance angle  
- Relay status indicators  

Each feature is tied to a specific relay (R1–R4), enabling spatial awareness  
and relay-level classification.

---

## 🧩 Hierarchical Learning Design

The ML system follows a **hierarchical classification architecture**,  
where multiple models (M1–M6) operate in stages.

This design decomposes a complex multi-class problem into smaller,  
specialised classification tasks.

### 🔷 Model Hierarchy

![Model Hierarchy](images/model_hierarchy.png)

- M1: Binary routing model (Attack vs Non-Attack)  
- M2: Non-attack category classifier  
- M3: Attack category classifier  
- M4–M6: Attack subtype classifiers  

This structure allows the system to progressively refine predictions  
from general detection to specific scenario identification.

---

## ⚙️ Model Roles and Responsibilities

### 🔹 M1 — Binary Detection Model

- Task: Distinguish between attack and non-attack samples  
- Output: Probability of attack (`p_attack`)  

M1 is optimised for **high recall**, ensuring that potential attacks  
are not missed during classification.

---

### 🔹 M2 — Non-Attack Classification

Classifies normal system behaviour into:

- SLG Faults  
- Line Maintenance  
- Normal Operation  

---

### 🔹 M3 — Attack Category Classification

Classifies detected attacks into:

- Data Injection  
- Remote Tripping  
- Relay Setting Change  

M3 identifies **which type of attack occurred**.

---

### 🔹 M4–M6 — Attack Subtype Classification

Each model specialises in a specific attack category:

| Model | Purpose |
|------|--------|
| M4 | Data Injection subtypes |
| M5 | Remote Tripping subtypes |
| M6 | Relay Setting Change subtypes |

These models determine the **exact scenario within each attack category**.

---

## 🧠 Training Strategy

All models are trained using the **same feature space**  
but with **different label mappings**.

### Key Principle

Instead of training a single multi-class model, the system:

- Decomposes the problem into smaller classification tasks  
- Uses specialised models at each stage  
- Improves interpretability and modularity  

---

## 📌 Label Transformation

The dataset is re-labelled differently for each model:

- M1 → Binary (Attack / Non-Attack)  
- M2 → Non-attack categories  
- M3 → Attack categories  
- M4–M6 → Scenario-level classification  

### 📌 Label Transformation Example

The hierarchical mapping depends on whether a sample is classified as attack or non-attack.

**Attack example (marker = 7):**
7 → Attack → Data Injection → DI subtype
**Non-attack example (marker = 41):**
41 → Non-Attack → Normal Operation

This demonstrates how samples follow different classification paths  
depending on the output of the M1 gating model.

---

## ⚙️ Threshold Design

The ML system uses thresholds to support hierarchical decision-making:

- `τ (tau)` → routing threshold for M1  
- Confidence threshold → used to evaluate prediction reliability  
- Safe margin → defines uncertainty region near the decision boundary  

These parameters are determined through validation experiments  
to balance detection performance and robustness.

## 🔁 Fallback Mechanism

The system incorporates a safety-first fallback mechanism to handle low-confidence predictions.

Since the framework prioritises high recall in M1, some samples may be routed to the attack branch even when classification confidence is uncertain.

When:
- M3 confidence falls below a defined threshold, and  
- M1 probability remains close to the routing boundary  

the system reverts to M2 instead of committing to

---

## 🧠 Explainability

The ML system provides interpretable outputs through:

- Feature importance  
- Contributing factors  

### 📌 Top Contributing Features

The most influential features typically include:

- Voltage magnitude  
- Current magnitude  
- Frequency deviation  
- Sequence components (positive, negative, zero)  
- Impedance-related measurements  

These features reflect electrical disturbances and are consistently  
important across multiple models.

---

## 📌 Key Strengths

- Hierarchical and modular architecture  
- High recall attack detection  
- Explainable outputs  
- Robust to noisy data  
- Scalable for real-time applications  

---

## ⚠️ Limitations

- Dependent on training data quality  
- Sensitive to feature mismatch  
- Cannot directly localise physical faults  
- Requires threshold tuning  

---

## 🔁 Reproducibility Overview

The ML models can be recreated using the following process:

1. Prepare and clean the dataset  
2. Ensure feature consistency and alignment  
3. Apply hierarchical label transformations  
4. Train models M1–M6 independently  
5. Tune routing and confidence thresholds  
6. Export trained models (`.joblib`)  
7. Save feature schema (`feature_columns.pkl`)  

---

## 📓 Development Notes

The development of the ML system was supported by notebooks used for:

- Data cleaning and preprocessing  
- Exploratory data analysis (EDA)  
- Hierarchical model training  
- Threshold selection and validation  
- Model evaluation  

---

## 📌 Summary

The Machine Learning module acts as the **intelligence layer** of the H-IDS.

It transforms raw electrical measurements into:

- Detection decisions  
- Attack classifications  
- Explainable insights  

through a hierarchical and interpretable learning framework.