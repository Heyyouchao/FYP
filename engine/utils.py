# engine/utils.py

import numpy as np

# -------------------------
# Helper (in app.py)
# -------------------------
def get_attack_type(scenario_id):

    if scenario_id is None:
        return None

    if 7 <= scenario_id <= 12:
        return "Data Injection"

    elif 15 <= scenario_id <= 20:
        return "Remote Tripping"

    elif (21 <= scenario_id <= 30) or (35 <= scenario_id <= 40):
        return "Relay Setting Change"

    return None

# ============================================================
# Feature Name Mapping (FULL ROBUST VERSION)
# ============================================================
def readable_feature_full(name):
    # your current full version (with "Magnitude"):

    # 🔥 Robust relay extraction
    relay = name.split("-")[0].split(":")[0]

    # ---------------- Impedance Flag ----------------
    if "Z_inf_flag" in name:
        return f"{relay} Impedance Fault Indicator"

    # ---------------- Voltage Magnitude ----------------
    if "PM1:V" in name:
        return f"{relay} Phase A Voltage Magnitude"
    if "PM2:V" in name:
        return f"{relay} Phase B Voltage Magnitude"
    if "PM3:V" in name:
        return f"{relay} Phase C Voltage Magnitude"

    # ---------------- Current Magnitude ----------------
    if "PM4:I" in name:
        return f"{relay} Phase A Current Magnitude"
    if "PM5:I" in name:
        return f"{relay} Phase B Current Magnitude"
    if "PM6:I" in name:
        return f"{relay} Phase C Current Magnitude"

    # ---------------- Voltage Angle ----------------
    if "PA1:VH" in name:
        return f"{relay} Phase A Voltage Angle"
    if "PA2:VH" in name:
        return f"{relay} Phase B Voltage Angle"
    if "PA3:VH" in name:
        return f"{relay} Phase C Voltage Angle"

    # ---------------- Current Angle ----------------
    if "PA4:IH" in name:
        return f"{relay} Phase A Current Angle"
    if "PA5:IH" in name:
        return f"{relay} Phase B Current Angle"
    if "PA6:IH" in name:
        return f"{relay} Phase C Current Angle"

    # ---------------- Sequence Components ----------------
    if "PM7:V" in name:
        return f"{relay} Positive Sequence Voltage"
    if "PM8:V" in name:
        return f"{relay} Negative Sequence Voltage"
    if "PM9:V" in name:
        return f"{relay} Zero Sequence Voltage"

    if "PM10:I" in name:
        return f"{relay} Positive Sequence Current"
    if "PM11:I" in name:
        return f"{relay} Negative Sequence Current"
    if "PM12:I" in name:
        return f"{relay} Zero Sequence Current"

    # ---------------- Frequency ----------------
    if ":F" in name:
        return f"{relay} Frequency"
    if ":DF" in name:
        return f"{relay} Frequency Change Rate"

    # ---------------- Impedance ----------------
    if ":Z" in name:
        return f"{relay} Apparent Impedance"
    if ":ZH" in name:
        return f"{relay} Impedance Angle"

    # ---------------- Status ----------------
    if ":S" in name:
        return f"{relay} Relay Status"

    return name

# ============================================================
# Feature Name Mapping (SHORT UI VERSION)
# ============================================================
def readable_feature_short(name):

    # 🔥 Robust relay extraction
    relay = name.split("-")[0].split(":")[0]

    # ---------------- Impedance Flag ----------------
    if "Z_inf_flag" in name:
        return f"{relay} Impedance Fault"

    # ---------------- Voltage ----------------
    if "PM1:V" in name:
        return f"{relay} Phase A Voltage"
    if "PM2:V" in name:
        return f"{relay} Phase B Voltage"
    if "PM3:V" in name:
        return f"{relay} Phase C Voltage"

    # ---------------- Current ----------------
    if "PM4:I" in name:
        return f"{relay} Phase A Current"
    if "PM5:I" in name:
        return f"{relay} Phase B Current"
    if "PM6:I" in name:
        return f"{relay} Phase C Current"

    # ---------------- Voltage Angle ----------------
    if "PA1:VH" in name:
        return f"{relay} Phase A Voltage (Angle)"
    if "PA2:VH" in name:
        return f"{relay} Phase B Voltage (Angle)"
    if "PA3:VH" in name:
        return f"{relay} Phase C Voltage (Angle)"

    # ---------------- Current Angle ----------------
    if "PA4:IH" in name:
        return f"{relay} Phase A Current (Angle)"
    if "PA5:IH" in name:
        return f"{relay} Phase B Current (Angle)"
    if "PA6:IH" in name:
        return f"{relay} Phase C Current (Angle)"

    # ---------------- Sequence ----------------
    if "PM7:V" in name:
        return f"{relay} Positive Seq Voltage"
    if "PM8:V" in name:
        return f"{relay} Negative Seq Voltage"
    if "PM9:V" in name:
        return f"{relay} Zero Seq Voltage"

    if "PM10:I" in name:
        return f"{relay} Positive Seq Current"
    if "PM11:I" in name:
        return f"{relay} Negative Seq Current"
    if "PM12:I" in name:
        return f"{relay} Zero Seq Current"

    # ---------------- Frequency ----------------
    if ":F" in name:
        return f"{relay} Frequency"
    if ":DF" in name:
        return f"{relay} ΔFrequency"

    # ---------------- Impedance ----------------
    if ":Z" in name:
        return f"{relay} Impedance"
    if ":ZH" in name:
        return f"{relay} Impedance (Angle)"

    # ---------------- Status ----------------
    if ":S" in name:
        return f"{relay} Relay Status"

    return name

def readable_feature_pop(name):

    relay = name.split("-")[0].split(":")[0]

    # ---------------- Voltage ----------------
    if "PM1:V" in name:
        return f"{relay} Phase A (V)"
    if "PM2:V" in name:
        return f"{relay} Phase B (V)"
    if "PM3:V" in name:
        return f"{relay} Phase C (V)"

    # ---------------- Current ----------------
    if "PM4:I" in name:
        return f"{relay} Phase A (I)"
    if "PM5:I" in name:
        return f"{relay} Phase B (I)"
    if "PM6:I" in name:
        return f"{relay} Phase C (I)"

    # ---------------- Sequence ----------------
    if "PM10:I" in name:
        return f"{relay} Positive Seq (I)"
    if "PM11:I" in name:
        return f"{relay} Negative Seq (I)"
    if "PM12:I" in name:
        return f"{relay} Zero Seq (I)"

    if "PM7:V" in name:
        return f"{relay} Positive Seq (V)"
    if "PM8:V" in name:
        return f"{relay} Negative Seq (V)"
    if "PM9:V" in name:
        return f"{relay} Zero Seq (V)"
    
    if ":F" in name:
        return f"{relay} Frequency"
    if ":DF" in name:
        return f"{relay} ΔFrequency"
    
    if ":Z" in name:
        return f"{relay} Impedance"
    if ":ZH" in name:
        return f"{relay} Impedance (Angle)"     
    return name


# ============================================================
# 🔥 FEATURE IMPORTANCE (WITH %)
# ============================================================
def get_top_features(model, feature_names, k=3, mode="short"):

    # ---------------- Get importance ----------------
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_

    elif hasattr(model, "coef_"):
        importance = np.abs(model.coef_).mean(axis=0)

    else:
        return ["N/A"]

    # ---------------- Normalize to % ----------------
    total = np.sum(importance)
    if total > 0:
        importance = importance / total * 100

    # ---------------- Get top k ----------------
    idx = np.argsort(importance)[::-1][:k]

    results = []

    for i in idx:

        raw_name = feature_names[i]

        # 🔥 Choose naming style
        if mode == "short":
            name = readable_feature_short(raw_name)
        else:
            name = readable_feature_full(raw_name)

        value = importance[i]

        results.append(f"{value:.1f}% — {name}")

    return results