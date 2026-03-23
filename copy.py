import streamlit as st
import pandas as pd
import datetime
import time
import random

# ============================================================
# IMPORT ENGINE + UTILS
# ============================================================
from engine.inference import predict_one, M1
from engine.utils import get_attack_type

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
df.columns = df.columns.str.strip()

FEATURE_COLS = M1.feature_names_in_

# ============================================================
# SESSION STATE INIT
# ============================================================
if "running" not in st.session_state:
    st.session_state.running = True

if "logs" not in st.session_state:
    st.session_state.logs = []

if "event_counter" not in st.session_state:
    st.session_state.event_counter = 1767

if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

# ============================================================
# TITLE
# ============================================================
st.title("⚡ Hierarchical IDS Dashboard")

# ============================================================
# SCENARIO SELECTION
# ============================================================
scenario = st.selectbox(
    "Select Scenario",
    sorted(df["marker"].unique())
)

df_s = df[df["marker"] == scenario].reset_index(drop=True)

# ============================================================
# CONTROLS
# ============================================================
col1, col2 = st.columns(2)

if col1.button("▶️ Start Stream"):
    st.session_state.running = True

if col2.button("⏸ Pause Stream"):
    st.session_state.running = False

# ============================================================
# STREAM LOGIC
# ============================================================
if st.session_state.running:
    idx = random.randint(0, len(df_s) - 1)
    st.session_state.current_idx = idx
else:
    idx = st.session_state.current_idx

# ============================================================
# GET ROW
# ============================================================
row = df_s.iloc[idx].copy()
y_true = row["marker"]

# ============================================================
# PREPARE INPUT
# ============================================================
row_model = row.drop(["marker", "label", "label_name"], errors="ignore")
row_model = row_model[FEATURE_COLS]

# ============================================================
# PREDICT
# ============================================================
result = predict_one(row_model, FEATURE_COLS)

# ============================================================
# LOCATION DETECTION
# ============================================================
def detect_location(row):
    for col in row.index:
        if col.startswith("R1"):
            return "R1"
        elif col.startswith("R2"):
            return "R2"
        elif col.startswith("R3"):
            return "R3"
        elif col.startswith("R4"):
            return "R4"
    return "Unknown"

location = detect_location(row_model)

# ============================================================
# 🚨 ALERT PANEL
# ============================================================
st.subheader("🚨 IDS Alert Output")

if result["Final_binary"] == 1:

    scenario_id = result["Final_class"]
    attack_type = get_attack_type(scenario_id)

    st.error("⚠️ Attack Detected")

    st.markdown(f"**Type:** {attack_type}")
    st.markdown(f"**Scenario:** `{scenario_id}` — {result['Final_label']}")
    st.markdown(f"**Path:** {result['Path']}")
    st.markdown(f"**Confidence:** {result['Final_conf']:.2%}")

else:
    st.success("✅ Non-Attack")

    st.markdown(f"**Condition:** {result['Final_label']}")
    st.markdown(f"**Path:** {result['Path']}")
    st.markdown(f"**Confidence:** {result['Final_conf']:.2%}")

# ============================================================
# 🔍 EXPLAINABILITY
# ============================================================
st.subheader("🔍 Contributing Factors")

if result["Contributing_Factors"]:
    for f in result["Contributing_Factors"]:
        st.markdown(f"- **{f}**")
else:
    st.write("No contributing factors")

# ============================================================
# 📋 EVENT LOG
# ============================================================
st.subheader("📋 Live Event Log")

event = {
    "ID": f"E-{st.session_state.event_counter}",
    "Time": datetime.datetime.now().strftime("%H:%M:%S"),
    "Source": "IDS",
    "Location": location,
    "Decision": "Attack" if result["Final_binary"] == 1 else "Normal",
    "Type": get_attack_type(result["Final_class"]) if result["Final_binary"] == 1 else result["Final_label"],
    "Confidence": f"{result['Final_conf']:.2%}",
    "Path": result["Path"]
}

st.session_state.logs.insert(0, event)
st.session_state.event_counter += 1

# ============================================================
# DISPLAY LOG TABLE + BUTTONS
# ============================================================
for i, log in enumerate(st.session_state.logs[:10]):  # show last 10

    cols = st.columns([1,1,1,1,1,1,1,1])

    cols[0].write(log["ID"])
    cols[1].write(log["Time"])
    cols[2].write(log["Source"])
    cols[3].write(log["Location"])

    if log["Decision"] == "Attack":
        cols[4].error("Attack")
    else:
        cols[4].success("Normal")

    cols[5].write(log["Type"])
    cols[6].write(log["Confidence"])

    if cols[7].button("Investigate", key=f"btn_{i}"):
        st.session_state.selected_event = log

# ============================================================
# 🔎 INVESTIGATION PANEL
# ============================================================
if "selected_event" in st.session_state:

    st.subheader("🔎 Event Investigation")

    e = st.session_state.selected_event

    st.write(f"**ID:** {e['ID']}")
    st.write(f"**Location:** {e['Location']}")
    st.write(f"**Type:** {e['Type']}")
    st.write(f"**Confidence:** {e['Confidence']}")
    st.write(f"**Path:** {e['Path']}")

# ============================================================
# AUTO REFRESH
# ============================================================
if st.session_state.running:
    time.sleep(1)
    st.rerun()