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

# 🔥 Use model's feature names (CORRECT WAY)
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
row = row.drop(["marker", "label", "label_name"], errors="ignore")

# 🔥 ALIGN FEATURES (CRITICAL)
row = row[FEATURE_COLS]

# ============================================================
# RUN PREDICTION
# ============================================================
result = predict_one(row, FEATURE_COLS)

# ============================================================
# 🚨 ALERT OUTPUT
# ============================================================
st.subheader("Hierarchical IDS Alert Output")

if result["Final_binary"] == 1:

    scenario_id = result["Final_class"]
    attack_type = get_attack_type(scenario_id)

    st.error(f"⚠️ Attack Detected {result['Final_conf']:.2%}")

    st.markdown(f"**Type:** {attack_type}")
    st.markdown(f"**Scenario:** `{scenario_id}` — {result['Final_label']}")
    st.markdown(f"**Path:** {result['Path']}  **({result['Decision']})**")

else:
    st.success(f"✅ Non-Attack {result['Final_conf']:.2%}")

    st.markdown(f"**Condition:** {result['Final_label']}")
    st.markdown(f"**Path:** {result['Path']}  **({result['Decision']})**")

# ============================================================
# 🔍 EXPLAINABILITY
# ============================================================
st.subheader("🔍 Contributing Factors")

if result["Contributing_Factors"]:
    for f in result["Contributing_Factors"]:
        st.markdown(f"- **{f}**")
else:
    st.write("No contributing factors available")

# ============================================================
# 📋 LIVE EVENT LOG
# ============================================================
st.subheader("📋 Live Event Log")

if "logs" not in st.session_state:
    st.session_state.logs = []

event = {
    "Time": datetime.datetime.now().strftime("%H:%M:%S"),
    "Decision": "Attack" if result["Final_binary"] == 1 else "Non-Attack",
    "Type": get_attack_type(result["Final_class"]) if result["Final_binary"] == 1 else result["Final_label"],
    "Confidence": f"{result['Final_conf']:.2%}",
    "Path": result["Path"]
}

st.session_state.logs.insert(0, event)

st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)