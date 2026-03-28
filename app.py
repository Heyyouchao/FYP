import streamlit as st
import pandas as pd
import datetime
import time
import random
import numpy as np

# ============================================================
# IMPORT ENGINE + UTILS
# ============================================================
from engine.inference import predict_one, M1
from engine.utils import get_attack_type

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(layout="wide")

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
    st.session_state.running = False

if "started" not in st.session_state:
    st.session_state.started = False

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
# SCENARIO
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
    st.session_state.started = True

if col2.button("⏸ Pause Stream"):
    st.session_state.running = False

# ============================================================
# BEFORE START
# ============================================================
if not st.session_state.started:
    st.markdown("### 💤 System Idle")
    st.caption("Waiting for live stream...")
    st.subheader("📋 Live Event Log")
    st.write("No events yet.")
    st.stop()

# ============================================================
# STREAM LOGIC
# ============================================================
if st.session_state.running:
    st.session_state.current_idx += 1
    if st.session_state.current_idx >= len(df_s):
        st.session_state.current_idx = 0

idx = st.session_state.current_idx

# ============================================================
# GET DATA
# ============================================================
row = df_s.iloc[idx].copy()
row = row.drop(["marker", "label", "label_name"], errors="ignore")
row = row[FEATURE_COLS]

# ============================================================
# PREDICT
# ============================================================
result = predict_one(row, FEATURE_COLS)

# ============================================================
# 🧱 DASHBOARD (3 PANEL)
# ============================================================
col_left, col_mid, col_right = st.columns([1, 3, 1])

# ============================================================
# LEFT PANEL
# ============================================================
with col_left:
    st.subheader("⚙️ Measurements")

    st.metric("Voltage", f"{round(random.uniform(220, 240),1)} V")
    st.metric("Current", f"{round(random.uniform(100,130),1)} A")
    st.metric("Frequency", f"{round(random.uniform(49.8,50.2),2)} Hz")

    st.subheader("🔋 Sequence")
    st.write("Positive: 91%")
    st.write("Negative: 7%")
    st.write("Zero: 2%")

# ============================================================
# CENTER PANEL
# ============================================================
with col_mid:
    st.subheader("⚡ System State & Context")

    st.markdown("""
    <div style='background:#1E293B;padding:20px;border-radius:12px;text-align:center'>
    <b>Grid Layout</b><br><br>
    G1 → R1 → R2 → R3 → R4 → G2
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Live PMU Waveforms")

    chart_data = pd.DataFrame(
        np.random.randn(50, 3),
        columns=["Phase A", "Phase B", "Phase C"]
    )

    st.line_chart(chart_data)

# ============================================================
# RIGHT PANEL (ALERT)
# ============================================================
with col_right:
    st.subheader("🚨 IDS Alert")

    current_time = datetime.datetime.now().strftime("%I:%M %p")

    if result["Final_binary"] == 1:
        attack_type = get_attack_type(result["Final_class"])

        st.error(f"⚠️ Attack Detected {result['Final_conf']:.0%}")
        st.markdown(f"🕒 {current_time}")
        st.markdown(f"**Type:** {attack_type}")
        st.markdown(f"**Path:** {result['Path']}")

        st.markdown("### Factors")
        for f in result["Contributing_Factors"]:
            st.write(f"- {f}")

        # Buttons
        b1, b2 = st.columns(2)
        with b1:
            st.button("🔍 Investigate")
        with b2:
            st.button("🟡 Dismiss")

    else:
        st.success(f"✅ Normal {result['Final_conf']:.0%}")
        st.markdown(f"🕒 {current_time}")
        st.markdown(f"**Condition:** {result['Final_label']}")

# ============================================================
# 📋 EVENT LOG
# ============================================================
st.markdown("---")
st.subheader("📋 Live Event Log")

event_id = f"E-{st.session_state.event_counter}"
st.session_state.event_counter += 1

timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
location = random.choice(["R1", "R2", "R3", "R4"])

event = {
    "ID": event_id,
    "Timestamp": timestamp,
    "Source": "IDS",
    "Location": location,
    "Decision": "Attack" if result["Final_binary"] == 1 else "Normal",
    "Event Type": (
        get_attack_type(result["Final_class"])
        if result["Final_binary"] == 1
        else result["Final_label"]
    ),
    "Path": result["Path"],
    "Confidence": f"{result['Final_conf']:.0%}",
    "Factors": result["Contributing_Factors"],
    "Action": "Investigate" if result["Final_binary"] == 1 else "Log"
}

if st.session_state.running:
    st.session_state.logs.insert(0, event)

# 🔥 BIG BUFFER (SCROLLABLE)
MAX_LOGS = 500
st.session_state.logs = st.session_state.logs[:MAX_LOGS]

st.dataframe(
    pd.DataFrame(st.session_state.logs),
    height=400,
    width="stretch"
)

# ============================================================
# AUTO REFRESH
# ============================================================
if st.session_state.running:
    time.sleep(1)
    st.rerun()