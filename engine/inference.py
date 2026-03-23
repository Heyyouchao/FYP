# ============================================================
# engine/inference.py
# ============================================================

import pandas as pd
import numpy as np
from tqdm import tqdm
import joblib

# ============================================================
# LOAD MODELS
# ============================================================
M1 = joblib.load("models/M1.joblib")
M2 = joblib.load("models/M2.joblib")
M3 = joblib.load("models/M3.joblib")
M4 = joblib.load("models/M4.joblib")
M5 = joblib.load("models/M5.joblib")
M6 = joblib.load("models/M6.joblib")

# ============================================================
# PARAMETERS
# ============================================================
TAU_GATE = 0.5311
CONF_FALLBACK = 0.8100
SAFE_MARGIN = 0.0750

ATTACK_LABEL_IDX = 0

# ============================================================
# LABELS
# ============================================================
M2_LABELS = {
    0: "SLG Faults",
    1: "Line Maintenance",
    2: "Normal Operation"
}

# ============================================================
# SCENARIO LOOKUP
# ============================================================
SCENARIO_LOOKUP = {

    # =========================
    # NATURAL EVENTS — SLG FAULTS
    # =========================
    1: "Fault from 10–19% on L1",
    2: "Fault from 20–79% on L1",
    3: "Fault from 80–90% on L1",
    4: "Fault from 10–19% on L2",
    5: "Fault from 20–79% on L2",
    6: "Fault from 80–90% on L2",

    # =========================
    # NATURAL EVENTS — MAINTENANCE
    # =========================
    13: "Line L1 maintenance",
    14: "Line L2 maintenance",

    # =========================
    # NO EVENT
    # =========================
    41: "Normal Operation (load changes)",

    # =========================
    # DATA INJECTION ATTACKS
    # =========================
    7:  "Fault 10–19% on L1 with tripping command",
    8:  "Fault 20–79% on L1 with tripping command",
    9:  "Fault 80–90% on L1 with tripping command",
    10: "Fault 10–19% on L2 with tripping command",
    11: "Fault 20–79% on L2 with tripping command",
    12: "Fault 80–90% on L2 with tripping command",

    # =========================
    # REMOTE TRIPPING — SINGLE RELAY
    # =========================
    15: "Command Injection to R1",
    16: "Command Injection to R2",
    17: "Command Injection to R3",
    18: "Command Injection to R4",

    # =========================
    # REMOTE TRIPPING — MULTI RELAY
    # =========================
    19: "Command Injection to R1 and R2",
    20: "Command Injection to R3 and R4",

    # =========================
    # RELAY SETTING CHANGE — SINGLE RELAY
    # =========================
    21: "Fault 10–19% on L1 with R1 disabled & fault",
    22: "Fault 20–90% on L1 with R1 disabled & fault",
    23: "Fault 10–49% on L1 with R2 disabled & fault",
    24: "Fault 50–79% on L1 with R2 disabled & fault",
    25: "Fault 80–90% on L1 with R2 disabled & fault",
    26: "Fault 10–19% on L2 with R3 disabled & fault",
    27: "Fault 20–49% on L2 with R3 disabled & fault",
    28: "Fault 50–90% on L2 with R3 disabled & fault",
    29: "Fault 10–79% on L2 with R4 disabled & fault",
    30: "Fault 80–90% on L2 with R4 disabled & fault",

    # =========================
    # RELAY SETTING CHANGE — TWO RELAYS + FAULT
    # =========================
    35: "Fault 10–49% on L1 with R1 and R2 disabled & fault",
    36: "Fault 50–90% on L1 with R1 and R2 disabled & fault",
    37: "Fault 10–49% on L1 with R3 and R4 disabled & fault",
    38: "Fault 50–90% on L1 with R3 and R4 disabled & fault",

    # =========================
    # RELAY SETTING CHANGE — MAINTENANCE
    # =========================
    39: "L1 maintenance with R1 and R2 disabled",
    40: "L1 maintenance with R1 and R2 disabled"
}

# ============================================================
# ATTACK GROUPS
# ============================================================
DI_IDS = [7,8,9,10,11,12]
RT_IDS = [15,16,17,18,19,20]
RSC_IDS = [21,22,23,24,25,26,27,28,29,30,35,36,37,38,39,40]

M4_INV_MAP = {i: k for i, k in enumerate(DI_IDS)}
M5_INV_MAP = {i: k for i, k in enumerate(RT_IDS)}
M6_INV_MAP = {i: k for i, k in enumerate(RSC_IDS)}

# ============================================================
# IMPORT UTILS
# ============================================================
from engine.utils import get_top_features

# ============================================================
# CORE HIERARCHICAL FUNCTION
# ============================================================
def predict_one(row, feature_cols):

    # Ensure correct format
    X = pd.DataFrame([row], columns=feature_cols)

    # ---------------- M1 ----------------
    p_attack = M1.predict_proba(X)[0][ATTACK_LABEL_IDX]

    result = {
        "M1_conf": p_attack,
        "M3_conf": None,
        "Leaf_conf": None,
        "Final_binary": None,
        "Final_class": None,
        "Final_label": None,
        "Final_conf": None,
        "Decision": None,
        "Path": None,
        "Contributing_Factors": None
    }

    # ---------------- M1 ROUTING ----------------
    if p_attack < TAU_GATE:

        m2_probs = M2.predict_proba(X)[0]
        m2_pred = int(np.argmax(m2_probs))
        m2_conf = float(m2_probs[m2_pred])

        result.update({
            "Final_binary": 0,
            "Final_label": M2_LABELS[m2_pred],
            "Final_conf": m2_conf,
            "Decision": "M2_DIRECT",
            "Path": "M1 → M2"
        })

    else:

        # ---------------- M3 ----------------
        m3_probs = M3.predict_proba(X)[0]
        m3_pred = int(np.argmax(m3_probs))
        m3_conf = float(m3_probs[m3_pred])

        result["M3_conf"] = m3_conf

        # ---------------- FALLBACK ----------------
        if (m3_conf < CONF_FALLBACK) and (p_attack < TAU_GATE + SAFE_MARGIN):

            m2_probs = M2.predict_proba(X)[0]
            m2_pred = int(np.argmax(m2_probs))
            m2_conf = float(m2_probs[m2_pred])

            result.update({
                "Final_binary": 0,
                "Final_label": M2_LABELS[m2_pred],
                "Final_conf": m2_conf,
                "Decision": "FALLBACK_TO_M2",
                "Path": "M1 → M3 → M2"
            })

        else:

            # ---------------- LEAF ----------------
            if m3_pred == 0:
                model = M4
                inv_map = M4_INV_MAP
                path = "M1 → M3 → M4"
            elif m3_pred == 1:
                model = M5
                inv_map = M5_INV_MAP
                path = "M1 → M3 → M5"
            else:
                model = M6
                inv_map = M6_INV_MAP
                path = "M1 → M3 → M6"

            probs = model.predict_proba(X)[0]
            pred = int(np.argmax(probs))
            conf = float(np.max(probs))

            result.update({
                "Final_binary": 1,
                "Final_class": inv_map[pred],
                "Final_label": SCENARIO_LOOKUP.get(inv_map[pred]),
                "Final_conf": conf,
                "Leaf_conf": conf,
                "Decision": "ATTACK_CONFIRMED",
                "Path": path
            })

    return result

# ============================================================
# FULL DATASET RUN
# ============================================================
def run_full_inference(X, y_true=None):

    results = hierarchical_predict(X, y_true_marker=y_true)

    return results