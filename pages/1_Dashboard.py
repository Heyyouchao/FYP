import streamlit as st
import pandas as pd
import datetime
import time
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ============================================================
st.set_page_config(layout="wide")

# ============================================================
# UI STYLES
# ============================================================
from ui.styles import load_css
st.markdown(load_css(), unsafe_allow_html=True)

# ============================================================
# IMPORT ENGINE + UTILS
# ============================================================
from engine.inference import predict_one, M1
from engine.utils import get_attack_type
from engine.scoring import get_most_affected_relay
from engine.measurements import get_measurements
from engine.pmu_history import update_pmu_history
from engine.physical_layer import process_event
from ui.grid_diagram import draw_grid
from engine.disturbance import (
    build_feature_groups,
    standardize,
    compute_baseline,
    compute_row_disturbance
)

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
df.columns = df.columns.str.strip()

FEATURE_COLS = M1.feature_names_in_

# ============================================================
# INIT DISTURBANCE ENGINE
# ============================================================
relay_groups, pmu_cols = build_feature_groups(df)
df_scaled = standardize(df, relay_groups, pmu_cols)
relay_baseline, _ = compute_baseline(df_scaled, relay_groups, pmu_cols)

# ============================================================
# SESSION STATE
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

if "pmu_history" not in st.session_state:
    st.session_state.pmu_history = []

# ============================================================
# HELPERS
# ============================================================
def get_model_input(row_clean, feature_cols):
    return row_clean.drop(
        ["marker", "label", "label_name"],
        errors="ignore"
    )[feature_cols]


def add_log_event(source, location, decision, event_type, path, confidence, action):
    event_id = f"E-{st.session_state.event_counter}"
    st.session_state.event_counter += 1

    event = {
        "ID": event_id,
        "Timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
        "Source": source,
        "Location": location,
        "Decision": decision,
        "Event Type": event_type,
        "Path": path,
        "Confidence": confidence,
        "Action": action
    }

    st.session_state.logs.insert(0, event)
    st.session_state.logs = st.session_state.logs[:500]


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="title">⚡ Hierarchical IDS Dashboard</div>',
    unsafe_allow_html=True
)

# ============================================================
# TOP CONTROLS (ONLY BEFORE START)
# ============================================================
if not st.session_state.started:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🎮 Controls")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("▶️ Start Stream", key="top_start"):
            st.session_state.running = True
            st.session_state.started = True
            st.rerun()

    with c2:
        st.button("⏸ Pause Stream", key="top_pause_disabled", disabled=True)

    st.markdown('</div>', unsafe_allow_html=True)

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
# PHYSICAL LAYER FOR GRID
# ============================================================
physical_layer = process_event(scores)

# ============================================================
# RELAY SELECTION
# ============================================================
if st.session_state.selected_relay == "AUTO":
    selected_relay = final_relay
else:
    selected_relay = st.session_state.selected_relay

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1, 3, 1])

# ============================================================
# LEFT PANEL
# ============================================================
with col_left:

    # st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    with st.container():
        # st.markdown('<div class="card"></div>', unsafe_allow_html=True)
        # TOP CONTENT
        st.subheader("🔀 Relay Selection")

        # buttons...
        b0, b1, b2, b3, b4 = st.columns(5)

        with b0:
            if st.button("Auto", key="relay_auto"):
                st.session_state.selected_relay = "AUTO"
        with b1:
            if st.button("R1", key="relay_r1"):
                st.session_state.selected_relay = "R1"
        with b2:
            if st.button("R2", key="relay_r2"):
                st.session_state.selected_relay = "R2"
        with b3:
            if st.button("R3", key="relay_r3"):
                st.session_state.selected_relay = "R3"
        with b4:
            if st.button("R4", key="relay_r4"):
                st.session_state.selected_relay = "R4"

        current_display_relay = final_relay if st.session_state.selected_relay == "AUTO" else st.session_state.selected_relay
        st.write(f"Current: {current_display_relay}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

        st.subheader(f"⚙️ Measurements — {selected_relay}")
        # metrics...
        data = get_measurements(row_clean, current_display_relay)

        if "error" in data:
            st.error(f"Measurement error: {data['error']}")
        else:
            st.metric("Voltage", f"{data['voltage']:.1f} kV")
            st.metric("Current", f"{data['current']:.1f} A")
            st.metric("Frequency", f"{data['frequency']:.2f} Hz")

            st.subheader("🔋 Sequence")
            st.write(f"Positive: {data['pos']:.1f}%")

            if data["neg"] > 5:
                st.error(f"Negative: {data['neg']:.1f}%")
            else:
                st.write(f"Negative: {data['neg']:.1f}%")

            st.write(f"Zero: {data['zero']:.1f}%")

            st.subheader("⚡ Relay Insight")
            st.write(f"Physical Relay: {physical_relay}")
            st.write(f"Final Relay: {final_relay}")
            st.write(f"Disturbance: {relay_disturbance[current_display_relay]:.2f}")

            if data.get("impedance_flag", 0) == 1:
                st.error("⚠️ Impedance anomaly detected")
            else:
                st.success("✅ Impedance normal")

    # st.markdown('</div>', unsafe_allow_html=True)
# ============================================================
# CENTER PANEL
# ============================================================
with col_center:
    # st.markdown('<div class="main-content">', unsafe_allow_html=True)
    with st.container():
        st.subheader("⚡ System State & Context")
        
        col_grid, col_table = st.columns([3, 1]) # grid bigger

        # =========================
        # GRID
        # =========================
        with col_grid:
            # with st.container():
            st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

            # fig_grid = draw_grid(physical_layer)
            # st.plotly_chart(fig_grid, use_container_width=True)

                # st.markdown('</div>', unsafe_allow_html=True)


    # with col_grid:
    #     st.subheader("⚡ System State & Context")

    #     st.markdown('<div class="card card-glow">', unsafe_allow_html=True)

    #     fig_grid = draw_grid(physical_layer)

        # st.plotly_chart(
        #     fig_grid,
        #     use_container_width=True,
        #     key="grid_chart"
        # )

        # st.markdown('</div>', unsafe_allow_html=True)


        # =========================
        # CONTROL ROOM TABLE
        # =========================
        with col_table:
            st.markdown('<div class="card-anchor">', unsafe_allow_html=True)
            st.subheader("🖥️ Control Room")

            def status_icon(status):
                if "Active" in status or "Connected" in status:
                    return "🟢"
                elif "Monitoring" in status:
                    return "🟡"
                else:
                    return "⚪"

            components = [
                ("Substation Switch", "Active", final_relay),
                ("PDC", "Connected", selected_relay),
                ("Snort", "Monitoring" if result["Final_binary"] else "Idle", result["Path"]),
                ("Syslog", "Logging", "Event Log")
            ]

            for name, status, signal in components:
                c1, c2, c3 = st.columns([2, 1.5, 2])

                with c1:
                    st.markdown(f"**{name}**")

                with c2:
                    st.markdown(f"{status_icon(status)} {status}")

                with c3:
                    st.markdown(f"`{signal}`")

    st.markdown('</div>', unsafe_allow_html=True)
   
    with st.container():
        st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)
        st.subheader("📊 Live PMU Waveforms")

        chart_data = update_pmu_history(
            st.session_state,
            row_clean,
            current_display_relay,
            result
        )

        x_vals = list(range(len(chart_data)))

        fig_pmu = go.Figure()
        fig_pmu.add_trace(go.Scatter(x=x_vals, y=chart_data["Phase A"], mode="lines", name="Phase A"))
        fig_pmu.add_trace(go.Scatter(x=x_vals, y=chart_data["Phase B"], mode="lines", name="Phase B"))
        fig_pmu.add_trace(go.Scatter(x=x_vals, y=chart_data["Phase C"], mode="lines", name="Phase C"))

        min_y = chart_data.min().min()
        max_y = chart_data.max().max()

        window = 50
        start = max(0, len(x_vals) - window)
        end = len(x_vals)

        fig_pmu.update_layout(
            template="plotly_dark",
            height=300,
            dragmode="pan",
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(
                range=[start, end],
                rangeslider=dict(visible=True)
            ),
            yaxis=dict(range=[min_y - 2, max_y + 2])
        )

        st.plotly_chart(fig_pmu, use_container_width=True)



# ============================================================
# RIGHT PANEL
# ============================================================
with col_right:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
    
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

            b1, b2, b3 = st.columns(3)

            with b1:
                if st.button("🔍 Investigate", key="investigate_btn"):
                    add_log_event(
                        source="User",
                        location=final_relay,
                        decision="Investigate",
                        event_type=result["Final_label"],
                        path=result["Path"],
                        confidence=f"{result['Final_conf']:.0%}",
                        action="Investigate"
                    )

            with b2:
                if st.button("🟡 Ack", key="ack_btn"):
                    add_log_event(
                        source="User",
                        location=final_relay,
                        decision="Acknowledge",
                        event_type=result["Final_label"],
                        path=result["Path"],
                        confidence=f"{result['Final_conf']:.0%}",
                        action="Acknowledge"
                    )

            with b3:
                if st.button("⛔ Ignore", key="ignore_btn"):
                    add_log_event(
                        source="User",
                        location=final_relay,
                        decision="Ignore",
                        event_type=result["Final_label"],
                        path=result["Path"],
                        confidence=f"{result['Final_conf']:.0%}",
                        action="Ignore"
                    )

        else:
            st.markdown(f"🕒 {current_time}")
            st.success(f"✅ Normal {result['Final_conf']:.0%}")
            st.markdown(f"**Condition:** {result['Final_label']}")
            st.markdown(f"**Path:** {result['Path']}")

            st.markdown("### Factors")
            for f in result["Contributing_Factors"]:
                st.write(f"- {f}")
    st.markdown('</div>', unsafe_allow_html=True)
                
# ============================================================
# AUTO SYSTEM LOG
# ============================================================
system_event = {
    "ID": f"E-{st.session_state.event_counter}",
    "Timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
    "Source": "IDS",
    "Location": final_relay,
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
    st.session_state.logs.insert(0, system_event)
    st.session_state.event_counter += 1
    st.session_state.logs = st.session_state.logs[:500]

# ============================================================
# EVENT LOG (UNDER MID + RIGHT)
# ============================================================
# st.markdown("---")
col_left, col_main = st.columns([1, 4])

with col_left:
    # BOTTOM CONTROLS
    st.markdown('<div class="bottom-controls">', unsafe_allow_html=True)
    if st.button("▶️ Start", use_container_width=True):
        st.session_state.running = True
        st.session_state.started = True
    if st.button("⏸ Pause", use_container_width=True):
        st.session_state.running = False
    
with col_main:
    # PUSH DOWN
    st.subheader("📋 Live Event Log")
    st.dataframe(
        pd.DataFrame(st.session_state.logs),
        height=400,
        width="stretch"
    )

# # ============================================================
# # BOTTOM CONTROL BAR
# # ============================================================
# if st.session_state.started:
#     st.markdown('<div class="bottom-controls">', unsafe_allow_html=True)

#     c1, c2, c3 = st.columns([2, 2, 6])

#     with c1:
#         if st.button("⏸ Pause", key="bottom_pause"):
#             st.session_state.running = False
#             st.rerun()

#     with c2:
#         if st.session_state.running:
#             st.success("🟢 Running")
#         else:
#             st.warning("🟡 Paused")

#     with c3:
#         st.write("")

#     st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# AUTO REFRESH
# ============================================================
if st.session_state.running:
    time.sleep(1)
    st.rerun()