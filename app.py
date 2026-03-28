import streamlit as st
import pandas as pd
import datetime
import time
import random
import numpy as np
import plotly.graph_objects as go

# ============================================================
# IMPORT ENGINE + UTILS
# ============================================================
from engine.inference import predict_one, M1
from engine.utils import get_attack_type
from engine.scoring import get_most_affected_relay
from engine.measurements import get_measurements
from engine.pmu_history import update_pmu_history
from engine.disturbance import (
    build_feature_groups,
    standardize,
    compute_baseline,
    compute_row_disturbance
)

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
# INIT DISTURBANCE ENGINE (RUN ONCE)
# ============================================================
relay_groups, pmu_cols = build_feature_groups(df)
df_scaled = standardize(df, relay_groups, pmu_cols)
relay_baseline, _ = compute_baseline(df_scaled, relay_groups, pmu_cols)

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

if "selected_relay" not in st.session_state:
    st.session_state.selected_relay = "AUTO"

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
df_scaled_s = df_scaled[df["marker"] == scenario].reset_index(drop=True)

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

row_clean = df_s.iloc[idx]
row_scaled = df_scaled_s.iloc[idx]

# ============================================================
# GET DATA
# ============================================================
def get_model_input(row_clean, FEATURE_COLS):
    return row_clean.drop(
        ["marker","label","label_name"], errors="ignore"
    )[FEATURE_COLS]

# ============================================================
# PREDICT
# ============================================================
row_model = get_model_input(row_clean, FEATURE_COLS)
result = predict_one(row_model, FEATURE_COLS)

# ============================================================
# DISTURBANCE (PHYSICAL)
# ============================================================
relay_disturbance = compute_row_disturbance(
    row_scaled,
    relay_groups,
    relay_baseline
)

physical_relay = max(relay_disturbance, key=relay_disturbance.get)

# ============================================================
# FUSION SCORING
# ============================================================
final_relay, scores = get_most_affected_relay(
    row_clean,
    relay_disturbance
)

# ============================================================
# RELAY SELECTION
# ============================================================
if st.session_state.selected_relay == "AUTO":
    selected_relay = final_relay
else:
    selected_relay = st.session_state.selected_relay

# ============================================================
# 🧱 DASHBOARD (3 PANEL)
# ============================================================
col_left, col_mid, col_right = st.columns([1, 3, 1])

# ============================================================
# LEFT PANEL — FIXED MEASUREMENTS (REAL DATA)
# ============================================================
with col_left:

    st.subheader("🔀 Relay Selection")

    c0,c1,c2,c3,c4 = st.columns(5)

    if c0.button("Auto"):
        st.session_state.selected_relay = "AUTO"
    if c1.button("R1"):
        st.session_state.selected_relay = "R1"
    if c2.button("R2"):
        st.session_state.selected_relay = "R2"
    if c3.button("R3"):
        st.session_state.selected_relay = "R3"
    if c4.button("R4"):
        st.session_state.selected_relay = "R4"

    st.write(f"Current: {selected_relay}")

    st.subheader(f"⚙️ Measurements — {selected_relay}")

    # ✅ USE ENGINE FUNCTION
    data = get_measurements(row_clean, selected_relay)

    if "error" in data:
        st.error(f"Measurement error: {data['error']}")
    else:
        st.metric("Voltage", f"{data['voltage']:.1f} kV")
        st.metric("Current", f"{data['current']:.1f} A")
        st.metric("Frequency", f"{data['frequency']:.2f} Hz")

        st.subheader("🔋 Sequence")

        # 🔥 add smart coloring
        if data["neg"] > 5:
            st.error(f"Negative: {data['neg']:.1f}% ⚠️")
        else:
            st.write(f"Negative: {data['neg']:.1f}%")

        st.write(f"Positive: {data['pos']:.1f}%")
        st.write(f"Zero: {data['zero']:.1f}%")

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

    # ============================================================
    # PMU WAVEFORM (REAL + SMOOTH VARIATION)
    # ============================================================

    # 🔥 get PMU data from engine
    chart_data = update_pmu_history(
        st.session_state,
        row_clean,
        selected_relay,
        result
    )

    # ---------------- Plot ----------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=chart_data["Phase A"],
        mode='lines',
        name='Phase A'
    ))

    fig.add_trace(go.Scatter(
        y=chart_data["Phase B"],
        mode='lines',
        name='Phase B'
    ))

    fig.add_trace(go.Scatter(
        y=chart_data["Phase C"],
        mode='lines',
        name='Phase C'
    ))

    # 🔥 zoom nicely
    min_y = chart_data.min().min()
    max_y = chart_data.max().max()

    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(range=[min_y - 2, max_y + 2]),
        height=300,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
# ============================================================
# RIGHT PANEL (ALERT)
# ============================================================
with col_right:
    st.subheader("🚨 IDS Alert")

    current_time = datetime.datetime.now().strftime("%I:%M %p")

    if result["Final_binary"] == 1:
        scenario_id = result["Final_class"]
        attack_type = get_attack_type(result["Final_class"])

        st.markdown(f"🕒 {current_time}")
        st.error(f"⚠️ Attack Detected {result['Final_conf']:.1%}")
        st.markdown(f"**Type:** {attack_type}")
        st.markdown(f"**Scenario:** `{scenario_id}` — {result['Final_label']}")
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
        st.markdown(f"🕒 {current_time}")
        st.success(f"✅ Normal {result['Final_conf']:.0%}")
        st.markdown(f"**Condition:** {result['Final_label']}")
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

# ============================================================
# 📋 EVENT LOG
# ============================================================
st.markdown("---")
_, col_main = st.columns([1, 4])  # skip left

with col_main:
    st.subheader("📋 Live Event Log")

    event_id = f"E-{st.session_state.event_counter}"
    st.session_state.event_counter += 1

    timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
    location = final_relay

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