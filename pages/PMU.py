import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 🔥 USE YOUR REAL FUNCTION
from engine.pmu_history import update_pmu_history

st.set_page_config(layout="wide")
st.title("🧪 PMU Debug (Real Function)")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load():
    df = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
    df.columns = df.columns.str.strip()
    return df

df = load()

# -------------------------
# SESSION STATE
# -------------------------
if "idx" not in st.session_state:
    st.session_state.idx = 0

if "pmu_history" not in st.session_state:
    st.session_state.pmu_history = []

if "last_idx" not in st.session_state:
    st.session_state.last_idx = -1

# -------------------------
# CONTROL
# -------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Pause"):
        st.session_state.running = False

running = st.session_state.get("running", False)

# -------------------------
# STREAM (PHYSICAL SIMULATION)
# -------------------------
if running:
    st.session_state.idx += 1
    if st.session_state.idx >= len(df):
        st.session_state.idx = 0

idx = st.session_state.idx
row = df.iloc[idx]

# -------------------------
# FAKE RESULT (for testing)
# -------------------------
result = {
    "Final_binary": 0,
    "Final_conf": 0
}

# -------------------------
# DEBUG PANEL
# -------------------------
st.write({
    "idx": idx,
    "last_idx": st.session_state.get("last_idx"),
    "pmu_len": len(st.session_state.get("pmu_history", [])),
    "running": running
})

# -------------------------
# RUN PMU (REAL FUNCTION)
# -------------------------
chart_data = update_pmu_history(
    st.session_state,
    row,
    "R1",     # fixed relay for testing
    result,
    idx       # 🔥 CRITICAL
)

# -------------------------
# SHOW RAW DATA
# -------------------------
st.write("Last 3 points:", chart_data.tail(3) if len(chart_data) > 0 else "Empty")

# -------------------------
# PLOT
# -------------------------
if chart_data is not None and len(chart_data) > 0:

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=chart_data["Phase A"], name="A"))
    fig.add_trace(go.Scatter(y=chart_data["Phase B"], name="B"))
    fig.add_trace(go.Scatter(y=chart_data["Phase C"], name="C"))

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("PMU empty")

# -------------------------
# LOOP
# -------------------------
if running:
    time.sleep(1)
    st.rerun()