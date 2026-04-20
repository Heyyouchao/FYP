import streamlit as st
import pandas as pd
import datetime
import time
import plotly.graph_objects as go
import numpy as np
# ============================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ============================================================
st.set_page_config(layout="wide")

# ============================================================
# UI STYLES
# ============================================================
from ui.styles import load_css
from ui.header import render_header
from ui.event_modal import show_event_detail
from streamlit_plotly_events import plotly_events
from ui.confirm_ignore import confirm_ignore_dialog

st.markdown(load_css(), unsafe_allow_html=True)


# ============================================================
# IMPORT ENGINE + UTILS
# ============================================================
from engine.inference import predict_one, M1, FEATURE_COLS
from engine.utils import get_attack_type, readable_feature_pop, readable_feature_full
from engine.disturbance import classify_relay_scores
from engine.scoring import compute_fusion_scores, get_most_affected_relay
from engine.measurements import get_measurements
from engine.pmu_history import update_pmu_history
from engine.physical_layer import process_event
from engine.explainer import(
    get_relay_flow,
    get_breaker_flow, 
    get_line_flow, 
    get_bus_flow, 
    get_generator_flow, 
    get_cyber_logs
)
from ui.grid_diagram import draw_grid
from helpers.event_helpers import add_log_row, get_current_event, add_user_action, now_full, create_event, build_M

# ============================================================
# LOAD DATA (SAFE)
# ============================================================
@st.cache_data
def load_data():
    df_debug = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
    df_debug.columns = df_debug.columns.str.strip()

    df_live = pd.read_csv("data/merged/multi_class_dataset.csv")
    df_live.columns = df_live.columns.str.strip()

    return df_debug, df_live

df_debug, df_live_raw = load_data()

# ============================================================
# MODE
# ============================================================
mode = st.session_state.get("mode", "Debug Mode")

# ============================================================
# SESSION STATE (SAFE INIT)
# ============================================================
defaults = {
    "running": False,
    "started": False,
    "alert_status": "active",
    "current_alert_signature": None,
    "logs": [],
    "log_rows": [],
    "event_counter": 1567,
    "current_idx": 0,
    "selected_relay": "AUTO",
    "pmu_history": [],
    "selected_component": None,
    "selected_event": None,
    "awaiting_review": False,
    "current_event": None,
    "current_event_id": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "last_idx" not in st.session_state:
    st.session_state.last_idx = -1

# ============================================================
# SCENARIO INIT (SAFE + VALIDATED)
# ============================================================
markers = sorted(df_debug["marker"].unique())

if "scenario" not in st.session_state or st.session_state.scenario not in markers:
    st.session_state.scenario = markers[0]

system_started = st.session_state.get("started", False)
system_running = st.session_state.get("running", False)

# =========================
# 🔥 CONTROL STATE INIT (ROBUST)
# =========================
if "control_state" not in st.session_state:
    st.session_state.control_state = {}

if "isolated" not in st.session_state.control_state:
    st.session_state.control_state["isolated"] = set()

if "locked" not in st.session_state.control_state:
    st.session_state.control_state["locked"] = set()

if "control_target" not in st.session_state:
    st.session_state.control_target = None

if "just_resumed" not in st.session_state:
    st.session_state.just_resumed = False

if st.session_state.get("closing_modal"):
    st.session_state.closing_modal = False

# ============================================================
# 🔒 SYSTEM FREEZE (CRITICAL FIX)
# ============================================================
def system_frozen():
    return (
        st.session_state.get("selected_event") is not None
        or st.session_state.get("selected_component") is not None
    )

def modal_just_closed():
    t = st.session_state.get("modal_closed_time", 0)
    return time.time() - t < 2

def get_active_event():
    return st.session_state.get("current_event")

# ============================================================
# HELPERS
# ============================================================
def all_green(physical_layer):

    # relays

    for r in physical_layer["relay"].values():

        if r["color"] != "🟢":

            return False

    # other components

    for group in ["line", "breaker", "bus", "generator"]:

        for val in physical_layer[group].values():

            if val != "🟢":

                return False

    return True
def get_model_input(row_clean, feature_cols):
    return row_clean.drop(
        ["marker", "label", "label_name"],
        errors="ignore"
    )[feature_cols]

def metric_row(label, value, unit="", level=None):
    cls = "metric-box"

    if level == "alert":
        cls += " alert"
    elif level == "warning":
        cls += " warning"

    st.markdown(f"""
    <div class="{cls}">
        <div class="metric-box-left">{label}</div>
        <div class="metric-box-right">{value} {unit}</div>
    </div>
    """, unsafe_allow_html=True)

def apply_user_controls(physical_layer):
    current_event = st.session_state.get("current_event")

    # no active event or no actions -> return physical model as-is
    if not current_event or "actions" not in current_event:
        return physical_layer

    control = current_event["actions"]

    relay_state = physical_layer.get("relay", {})
    breaker = physical_layer.get("breaker", {})
    line = physical_layer.get("line", {})
    bus = physical_layer.get("bus", {})

    # ============================================================
    # APPLY OVERRIDES ONLY
    # physical_layer already contains the base physical state
    # so we only override when user actions exist
    # ============================================================

    # -------------------------
    # ISOLATE
    # -------------------------
    for relay in control.get("isolated", set()):

        flow = get_relay_flow(relay)
        affected_line = flow.get("affects_on")

        # relay degraded
        if relay in relay_state:
            relay_state[relay]["color"] = "🟡"

        # trip breaker
        for br in breaker:
            br_flow = get_breaker_flow(br)
            if relay in br_flow.get("affected_by", ""):
                breaker[br] = "🔴"

        # disconnect line
        if affected_line in line:
            line[affected_line] = "⚪"

        # degrade bus
        for b in bus:
            b_flow = get_bus_flow(b)
            if affected_line in b_flow.get("affected_by", ""):
                bus[b] = "🟡"

    # -------------------------
    # LOCK
    # -------------------------
    for relay in control.get("locked", set()):

        flow = get_relay_flow(relay)
        affected_line = flow.get("affects_on")

        # relay fault persists
        if relay in relay_state:
            relay_state[relay]["color"] = "🔴"

        # line fault persists
        if affected_line in line:
            line[affected_line] = "🔴"

    return physical_layer

# ============================================================
# PHYSICAL SNAPSHOT (P_full)
# ============================================================
def build_physical_snapshot(row_clean, raw_scores, norm_scores,fusion_scores, physical_layer):

    # -------------------------
    # 1. MEASUREMENTS
    # -------------------------
    measurements = []

    for r in ["R1","R2","R3","R4"]:
        data = get_measurements(row_clean, r)

        if "error" not in data:
            measurements.append({
                "Relay": r,
                "Voltage": round(data["voltage"], 1),
                "Current": round(data["current"], 1),
                "Frequency": round(data["frequency"], 2),
                "Pos": round(data["pos"], 1),
                "Neg": round(data["neg"], 1),
                "Zero": round(data["zero"], 1),
            })

    # -------------------------
    # 2. RELAY ANALYSIS
    # -------------------------
    relay_analysis = []

    for r in ["R1","R2","R3","R4"]:

        r_data = physical_layer.get("relay", {}).get(r, {})
        raw = raw_scores.get(r, 0)
        norm = norm_scores.get(r, 0)
        fusion = fusion_scores.get(r, 0)

        flag = "⚠️" if row_clean.get(f"{r}-PA:Z_inf_flag", 0) == 1 else "--"
        flow = get_relay_flow(r)

        causes = []
        for f in r_data.get("top_features", [])[:2]:
            name = readable_feature_full(f)
            name = name.split(" ", 1)[1] if " " in name else name
            causes.append(name)

        relay_analysis.append({
            "Relay": r,
            "State": r_data.get("color", "⚪"),
            "Raw": round(raw, 2),
            "Norm": round(norm, 2),
            "Fusion": round(fusion, 2),
            "Flag": flag,
            "Affect": flow.get("affects_on", "--"),
            "Top Causes": ", ".join(causes) if causes else "Stable"
        })

    relay_analysis = sorted(relay_analysis, key=lambda x: x["Raw"], reverse=True)

    # -------------------------
    # 3. SYSTEM STATE
    # -------------------------
    system_state = []

    breaker = physical_layer.get("breaker", {})
    bus = physical_layer.get("bus", {})
    generator = physical_layer.get("generator", {})
    line_state = physical_layer.get("line", {})
    line_model = physical_layer.get("line_model", {})

    for br in ["BR1","BR2","BR3","BR4"]:
        flow = get_breaker_flow(br)
        system_state.append({
            "Component": br,
            "Type": "Breaker",
            "State": breaker.get(br, "N/A"),
            "Affected By": flow.get("affected_by", "--"),
            "Affects On": flow.get("affects_on", "--")
        })

    for line in ["L1","L2"]:
        flow = get_line_flow(line)
        actual = line_state.get(line, "N/A")
        model = line_model.get(line, "N/A")

        affects = flow.get("affects_on", "--")
        if model != "N/A" and actual != model:
            affects = f"{affects} ⚠️ Override"

        system_state.append({
            "Component": line,
            "Type": "Line",
            "State": actual,
            "Affected By": flow.get("affected_by", "--"),
            "Affects On": affects
        })

    for b in ["B1","B2","B3"]:
        flow = get_bus_flow(b)
        system_state.append({
            "Component": b,
            "Type": "Bus",
            "State": bus.get(b, "N/A"),
            "Affected By": flow.get("affected_by", "--"),
            "Affects On": flow.get("affects_on", "--")
        })

    for g in ["G1","G2"]:
        flow = get_generator_flow(g)
        system_state.append({
            "Component": g,
            "Type": "Generator",
            "State": generator.get(g, "N/A"),
            "Affected By": flow.get("affected_by", "--"),
            "Affects On": flow.get("affects_on", "--")
        })

    return {
        "Measurements": measurements,
        "Relay Analysis": relay_analysis,
        "System State": system_state
    }



# ============================================================
# FLAGGED RELAYS
# ============================================================
def get_flagged_relays(row):
    flagged = []

    for i in range(1, 5):
        col = f"R{i}-PA:Z_inf_flag"
        if col in row and row[col] == 1:
            flagged.append(f"R{i}")

    return flagged

# =========================
# INIT STATE (SAFE)
# =========================
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

if "scenario" not in st.session_state:
    st.session_state.scenario = df_debug["marker"].iloc[0]

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_relay" not in st.session_state:
    st.session_state.last_relay = "--"

# =========================
# DATA PIPELINE
# =========================
if mode == "Debug Mode":

    # 🔒 SINGLE SOURCE OF TRUTH
    scenario = st.session_state.scenario

    # 🔒 STRICT FILTER
    df_active = df_debug[df_debug["marker"] == scenario].reset_index(drop=True)

    # 🚨 HARD CHECK
    if df_active.empty:
        st.error(f"❌ No data for scenario: {scenario}")
        st.stop()

    # -------------------------
    # STREAM (SEQUENTIAL)
    # -------------------------
    if st.session_state.running and not system_frozen():

        # 🔥 PREVENT EVENT SKIP AFTER USER ACTION
        if st.session_state.get("just_resumed", False):
            st.session_state.just_resumed = False
        else:
            st.session_state.current_idx += 1

        if st.session_state.current_idx >= len(df_active):
            st.session_state.current_idx = 0

    idx = min(st.session_state.current_idx, len(df_active) - 1)
    st.session_state.current_idx = idx

    # -------------------------
    # GET ROW
    # -------------------------
    row_clean = df_active.iloc[idx]


# ============================================================
# LIVE MODE (REAL RANDOM STREAM - FIXED)
# ============================================================
else:

    df_active = df_live_raw.copy().reset_index(drop=True)

    if not system_frozen():

        # 🔥 PREVENT JUMP AFTER RESUME
        if st.session_state.get("just_resumed", False):
            idx = st.session_state.get("current_idx", 0)
            st.session_state.just_resumed = False
        else:
            idx = np.random.randint(0, len(df_active))
            st.session_state.current_idx = idx   # 🔥 CRITICAL

    else:
        idx = st.session_state.get("current_idx", 0)

    # -------------------------
    # SAFE INDEX
    # -------------------------
    if df_active.empty:
        st.error("❌ No live data available.")
        st.stop()

    idx = min(idx, len(df_active) - 1)
    st.session_state.current_idx = idx

    # -------------------------
    # GET ROW
    # -------------------------
    row_raw = df_active.iloc[idx].copy()

    import engine.preprocessing
    row_clean = engine.preprocessing.clean_live_row(row_raw, df_debug)

    st.caption(f"Live sample from scenario: {row_raw['marker']}")


# ============================================================
# MODEL + RESULT
# ============================================================
if not system_started:

    final_relay = "--"
    physical_relay = "--"

    raw_scores = {f"R{i}": 0 for i in range(1, 5)}
    norm_scores = {f"R{i}": 0 for i in range(1, 5)}
    top_features = {}

    result = {
        "Final_binary": 0,
        "Final_label": "Waiting to start",
        "Final_class": "--",
        "Final_conf": 0,
        "Decision": "--",
        "Path": "--",
        "Contributing_Factors": []
    }

else:
    raw_scores, norm_scores, state, top_features = classify_relay_scores(row_clean)

    physical_relay = max(raw_scores, key=raw_scores.get)

    row_model = get_model_input(row_clean, FEATURE_COLS)
    result = predict_one(row_model, FEATURE_COLS)

    final_relay, scores = get_most_affected_relay(row_clean, raw_scores)

    # 🔥 SAVE FOR HEADER (CRITICAL FIX)
    st.session_state.last_result = result
    st.session_state.last_relay = final_relay

if system_started:
    fusion_scores = compute_fusion_scores(row_clean, raw_scores)
else:
    fusion_scores = {f"R{i}": 0 for i in range(1,5)}

# ============================================================
# 🔥 SCENARIO (CORRECT PLACE)
# ============================================================
scenario = (
    st.session_state.scenario
    if mode == "Debug Mode"
    else result.get("Final_class", "--")
)

header_result = st.session_state.get("last_result", None)
header_relay = st.session_state.get("last_relay", "--")

header_label = (
    header_result.get("Final_label", "--")
    if header_result else "--"
)

selected_scenario = render_header(
    mode,
    df_debug,
    result=header_result,
    final_relay=header_relay,
    final_label=header_label
)

# ============================================================
# 🔥 SCENARIO SYNC (NO INDEX RESET)
# ============================================================
if selected_scenario is not None:
    if selected_scenario != st.session_state.scenario:

        st.session_state.scenario = selected_scenario

        # ❌ DO NOT TOUCH current_idx
        # ❌ DO NOT TOUCH pmu_history
        # ❌ DO NOT TOUCH logs

        st.rerun()


# ============================================================
# 4. GRID
# ============================================================
if system_started:
    physical_layer = process_event(
        norm_scores,
        row_clean,        # or your current row
        top_features
    )

    physical_layer = apply_user_controls(physical_layer)
else:
    physical_layer = {
        "relay": {f"R{i}": {"color": "🟢"} for i in range(1,5)},
        "breaker": {f"BR{i}": "🟢" for i in range(1,5)},
        "line": {f"L{i}": "🟢" for i in range(1,3)},
        "bus": {f"B{i}": "🟢" for i in range(1,4)},
        "generator": {f"G{i}": "🟢" for i in range(1,3)},
    }
# ============================================================
# AUTO CREATE PHYSICAL EVENT (FIXED - NO OVERWRITE)
# ============================================================
if system_started:

    # 🔒 DO NOT CREATE NEW EVENT DURING REVIEW
    if (
        not system_frozen() 
        and not st.session_state.get("awaiting_review", False)
    ):

        fusion_scores = compute_fusion_scores(row_clean, raw_scores)

        event = create_event(
            row_clean,
            raw_scores,
            norm_scores,
            fusion_scores,
            physical_layer,
            final_relay,
            build_physical_snapshot
        )

        # 🔥 ONLY CREATE IF NO ACTIVE EVENT
        if st.session_state.get("current_event") is None:
            st.session_state.current_event = event
            st.session_state.current_event_id = event["Event ID"]

# ============================================================
# RELAY SELECTION
# ============================================================
selected_relay = (
    final_relay
    if st.session_state.selected_relay == "AUTO"
    else st.session_state.selected_relay
)

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 4])

# ============================================================
# LEFT PANEL
# ============================================================
with col_left:
    with st.container():
        st.markdown('<div class="card-anchor "></div>', unsafe_allow_html=True)
        # TOP CONTENT
        st.subheader("Relay Selection")

        # buttons...
        b0, b1, b2, b3, b4 = st.columns(5)

        with b0:
            if st.button("Auto", key="relay_auto", type="secondary"):
                st.session_state.selected_relay = "AUTO"
        with b1:
            if st.button("R1", key="relay_r1", type="secondary"):
                st.session_state.selected_relay = "R1"
        with b2:
            if st.button("R2", key="relay_r2", type="secondary"):
                st.session_state.selected_relay = "R2"
        with b3:
            if st.button("R3", key="relay_r3", type="secondary"):
                st.session_state.selected_relay = "R3"
        with b4:
            if st.button("R4", key="relay_r4", type="secondary"):
                st.session_state.selected_relay = "R4"

        current_display_relay = (
            final_relay 
            if st.session_state.selected_relay == "AUTO" 
            else st.session_state.selected_relay
        )
        st.write(f"Current: {current_display_relay}")
    
    with st.container():
        st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

        st.subheader(f"Measurements — {selected_relay}")

        if not system_started:
            st.info("Waiting to start ...")
        else:
            # metrics...
            data = get_measurements(row_clean, current_display_relay)

            if "error" in data:
                st.error(f"Measurement error: {data['error']}")
            else:
                st.metric("Voltage", f"{data['voltage']:.1f} kV")
                st.metric("Current", f"{data['current']:.1f} A")
                st.metric("Frequency", f"{data['frequency']:.2f} Hz")

                st.subheader("Sequence (I)")
                metric_row("Positive", f"{data['pos']:.1f}%", level="normal")

                neg_level="alert" if data["neg"] > 5 else None
                metric_row("Negative", f"{data['neg']:.1f}%", level=neg_level)

                metric_row("Zero", f"{data['zero']:.1f}%", level="normal")

                st.subheader("Relay Insight")
                metric_row("Physical Relay", physical_relay)
                metric_row("Final Relay", final_relay)
                # -------------------------
                # SCORES
                # -------------------------

                # Physical score (raw)
                physical_score = raw_scores[current_display_relay]

                # Fusion score (final)
                fusion_score = fusion_scores[current_display_relay]  # 👈 assumes you already have fusion scores

                # Optional: show physical score (recommended for clarity)
                phys_level = "alert" if physical_score > 1.5 else "warning" if physical_score > 1.0 else None
                metric_row("Physical Score", f"{physical_score:.2f}", level=phys_level)

                # Fusion score (main decision metric)
                fusion_level = "alert" if fusion_score > 1.5 else "warning" if fusion_score > 1.0 else None
                metric_row("Fusion Score", f"{fusion_score:.2f}", level=fusion_level)

                if data.get("impedance_flag", 0) == 1:
                    st.markdown(
                        f"""
                        <div class="impedance-error-bar">
                            <div class="impedance-error-bar-left">
                                ⚠️ Impedance anomaly detected
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="impedance-normal-bar">
                            <div class="impedance-normal-bar-left">
                                ✅ Impedance normal
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    with st.container():
        st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)
        # 🔥 FIX: DISABLE WHEN SYSTEM FROZEN
        disabled_controls = system_frozen()

        # =========================
        # ▶ START / RESUME BUTTON
        # =========================
        label = "▶ Start" if not st.session_state.started else "▶ Resume"

        if st.button(label, use_container_width=True, type="primary"):

            # 🔥 always resume system
            st.session_state.running = True
            st.session_state.started = True

            # 🔥 clear stuck states (important for Resume)
            st.session_state.awaiting_review = False
            st.session_state.selected_event = None
            st.session_state.modal_mode = None
            st.session_state.modal_opened = False
            st.session_state.pending_action = None
            st.session_state.actions_clicked = False

            st.rerun()
        if st.button("⏸ Pause", use_container_width=True, type="primary"):
            st.session_state.started = True
            st.session_state.running = False
            st.rerun()
        
# ============================================================
# CENTER PANEL
# ============================================================
with col_right:
    col_centre, col_alert = st.columns([2.75, 1])
    with col_centre:
        with st.container():
            st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

            # ============================================================
            # 🟢 NORMAL STATE MESSAGE (BASED ON GRID COLOURS)
            # ============================================================
            if (
                system_started
                and all_green(physical_layer)
                and not st.session_state.get("awaiting_review", False)
                and st.session_state.get("selected_component") is None
            ):
                caption = "✔ All components operating normally — inspection optional"
            else:
                caption = ""
           
            st.markdown(f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:10px;
            ">
                <h3 style="margin:0;">System State & Context</h3>
                <span style="color:#ffffff; font-size:24px;">{caption}</span>
            </div>
            """, unsafe_allow_html=True)
            
            col_grid, col_table = st.columns([2, 1]) # grid bigger

            # =========================
            # GRID
            # =========================
            with col_grid:
                # with st.container():
                st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

                fig_grid = draw_grid(
                    physical_layer,
                    selected=st.session_state.get("selected_component")
                )

                selected_points = plotly_events(
                    fig_grid, 
                    click_event=True,
                    hover_event=False,
                    select_event=False,
                    override_height=420,
                )

                if selected_points:

                    point = selected_points[0]
                    idx = point["pointIndex"]

                    clickable_trace = fig_grid.data[-1]
                    selected_name = clickable_trace["text"][idx]


                    if st.session_state.selected_component == selected_name:
                        st.session_state.selected_component = None
                    else:
                        st.session_state.selected_component = selected_name
                    st.session_state.running = False

                    st.rerun()


        # =========================
        # CONTROL ROOM TABLE
        # =========================
            with col_table:
                st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)
                st.subheader("Control Room")

                def status_icon(status):
                    if "Active" in status or "Connected" in status:
                        return "🟢"
                    elif "Monitoring" in status:
                        return "🟡"
                    elif "Alert" in status:
                        return "🔴"
                    else:
                        return "⚪"
                
                if not system_started:
                    components = [
                        ("Switch", "Idle", "--"),
                        ("PDC", "Idle", "--"),
                        ("IDS", "Waiting", "--"),
                        ("Syslog", "Stopped", "--")
                    ]
                else:
                    components = [
                        ("Switch", "Active", final_relay),
                        ("PDC", "Connected", selected_relay),
                        ("IDS", "Alert" if result["Final_binary"] == 1 else "Monitoring", "--"),
                        ("Syslog", "Logging", "Event Log")
                    ]
                
                st.markdown('<div class="control-grid">', unsafe_allow_html=True)

                for name, status, signal in components:

                    st.markdown(f"""
                    <div class="control-row">
                        <div class="control-left">{name}</div>
                        <div class="control-status">{status_icon(status)} {status}</div>
                        <div class="control-right">{signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


                selected = st.session_state.get("selected_component")

                if not selected:
                    st.markdown("""
                    <div style="
                        margin: 30px auto;
                        padding: 16px 20px;
                        width: 65%;
                        border-radius: 14px;
                        background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(15,23,42,0.6));
                        border: 1px solid rgba(148,163,184,0.2);
                        text-align: center;
                        color: #cbd5f5;
                        font-size: 14px;
                        font-weight: 500;
                        backdrop-filter: blur(6px);
                    ">
                        Click a component in the grid
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    breaker = physical_layer.get("breaker", {})
                    line_status = physical_layer.get("line", {})
                    line_model = physical_layer.get("line_model", {})
                    bus = physical_layer.get("bus", {})
                    generator = physical_layer.get("generator", {})

                    # =========================
                    # RELAY
                    # =========================
                    if selected.startswith("R"):

                        r_data = physical_layer["relay"][selected]

                        raw = raw_scores[selected]
                        norm = norm_scores[selected]
                        fusion_score = fusion_scores[selected]

                        # 🔥 HEADER
                        control = st.session_state.control_state
                        if selected in control["isolated"]:
                            relay_color = "⚪️"
                            status = "Isolated"
                        elif selected in control["locked"]:
                            relay_color = "🟣"
                            status = "Locked"
                        else:
                            relay_color = r_data["color"]
                            status = "Normal" if relay_color == "🟢" else "Alert"

                        st.markdown(f"### Selected - {selected} {relay_color}({status}) - Fusion Score: {fusion_score:.2f}")

                        # ROW: score + chain
                        flow = get_relay_flow(selected)

                        c1, c2 = st.columns([1.5, 1])
                        with c1:
                            st.markdown(f"Raw: {raw:.2f} | Norm: {norm:.2f}")
                        with c2:
                            st.markdown(f" Event Chain: {flow['affected_by']} → {flow['affects_on']}")

                        # =========================
                        # CAUSE (INLINE)
                        # =========================
                        if "top_features" in r_data:

                            causes = []

                            for f in r_data["top_features"][:3]:
                                name = readable_feature_pop(f)
                                name = name.split(" ", 1)[1] if " " in name else name
                                causes.append(name)

                            st.markdown(f"**Cause:** {' | '.join(causes)}")

                        # =========================
                        # CYBER (INLINE)
                        # =========================
                        logs = get_cyber_logs(row_clean, selected)

                        st.markdown(f"**Cyber:** {' | '.join(logs)}")

                    # =========================
                    # NON-RELAY (IMPROVED)
                    # =========================
                    else:
                        
                        # =========================
                        # SELECTED HEADER (ONLY G + B COLORED)
                        # =========================
                        if selected.startswith("G") or (selected.startswith("B") and not selected.startswith("BR")):

                            # get correct state
                            if selected.startswith("B"):
                                state = bus.get(selected, "⚪")
                            else:  # G
                                state = generator.get(selected, "⚪")

                            # map emoji → color
                            color_map = {
                                "🟢": "#22c55e",
                                "🔴": "#ef4444",
                                "🟡": "#f59e0b",
                                "⚪": "#9ca3af"
                            }

                            dot_color = color_map.get(state, "#9ca3af")

                            st.markdown(f"""
                            <h3>
                            Selected — {selected}
                            <span style="
                                display:inline-block;
                                width:10px;
                                height:10px;
                                border-radius:50%;
                                background:{dot_color};
                                margin-left:8px;
                            "></span>
                            </h3>
                            """, unsafe_allow_html=True)

                        else:
                            # normal (no color)
                            st.markdown(f"### Selected — `{selected}`")

                        # =========================
                        # BREAKER
                        # =========================
                        if selected.startswith("BR"):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"**Status:** {status}")

                            flow = get_breaker_flow(selected)

                            with c2:
                                st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                            st.caption("Protection switch controlling line flow")

                        # =========================
                        # GENERATOR
                        # =========================
                        elif selected.startswith("G"):

                            flow = get_generator_flow(selected)

                            st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                            st.caption("Power source supplying the grid")

                        # =========================
                        # BUS
                        # =========================
                        elif selected.startswith("B"):

                            flow = get_bus_flow(selected)

                            st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                            st.caption("Connection node distributing power")

                        # =========================
                        # LINE
                        # =========================

                        elif selected.startswith("L"):
                            actual = physical_layer["line"].get(selected, "N/A")
                            model = physical_layer["line_model"].get(selected, "N/A")

                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"""
                                <div class="mini-box">
                                    <div class="mini-label">State</div>
                                    <div class="mini-value">{actual}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with c2:
                                st.markdown(f"""
                                <div class="mini-box">
                                    <div class="mini-label">Model</div>
                                    <div class="mini-value">{model}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            # =========================
                            # FLOW / CHAIN
                            # =========================
                            flow = get_line_flow(selected)

                            st.markdown(f"""
                            <div class="chain-box">
                                <b>Chain:</b> {flow['affected_by']} → {flow['affects_on']}
                            </div>
                            """, unsafe_allow_html=True)

                            st.caption("Transmission path between buses")


                    # =========================
                    # CLEAR
                    # =========================
                    if st.button("Clear", use_container_width=True, type="tertiary"):

                        # 🔥 remove selection (exit inspection mode)
                        st.session_state.selected_component = None

                        # 🔥 RESUME system IF not in review
                        if not st.session_state.get("awaiting_review", False):
                            st.session_state.running = True

                        st.rerun()


            with st.container():
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.subheader("Live PMU Waveforms")

                if not system_started:
                    st.info("Waiting to start...")

                else:
                    relay_for_pmu = final_relay if final_relay != "--" else "R1"

                    # 🔥 FIX: freeze PMU when popup/review is active
                    if system_frozen():
                        chart_data = pd.DataFrame(st.session_state.get("pmu_history", []))
                    else:
                        chart_data = update_pmu_history(
                            st.session_state,
                            row_clean,
                            relay_for_pmu,
                            result,
                            idx
                        )

                    if chart_data is not None and len(chart_data) > 0:

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

                    else:
                        st.info("PMU initializing...")

                st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RIGHT PANEL
# ============================================================
    with col_alert:
        with st.container():

            st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)

            flagged_relays = get_flagged_relays(row_clean)
            has_flag = len(flagged_relays) > 0

            if flagged_relays:
                flag_text = " | ".join(flagged_relays)

                st.markdown(
                    f"""
                    <div class="ids-header">
                        <div class="ids-title">🚨 IDS Alert</div>
                        <div class="ids-flag-wrapper">
                            <span class="ids-badge active">FLAG IN {flag_text}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div class="ids-header">
                        <div class="ids-title">🚨 IDS Alert</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            current_time = datetime.datetime.now().strftime("%I:%M %p")

            should_freeze = (
                result["Final_binary"] == 1
                or has_flag
                or st.session_state.awaiting_review
            )
            event_id = st.session_state.get("current_event_id") or "--"

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    font-size:18px;
                    font-weight:600;
                    color:#ffffff;
                ">
                    <span>{current_time}</span>
                    <span>{event_id}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            if result["Final_binary"] == 1:
                st.markdown(
                    f"""
                    <div class="alert-bar">
                        <div class="alert-bar-left">
                            ⚠️ Attack Detected
                        </div>
                        <div class="alert-bar-right">
                            {result['Final_conf']:.1%}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:        
                st.markdown(
                    f"""
                    <div class="normal-bar">
                        <div class="normal-bar-left">
                            ✅ Normal
                        </div>
                        <div class="normal-bar-right">
                            {result['Final_conf']:.1%}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            if should_freeze and not modal_just_closed():

                scenario_id = result["Final_class"]
                attack_type = get_attack_type(result["Final_class"])

                # st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"**Type:** {attack_type}")
                st.markdown(f"**Scenario:** `{scenario_id}` — {result['Final_label']}")
                st.markdown(f"**Path:** '{result['Path']}' [{result['Decision']}]")
                                
                st.markdown("### Factors")
                for f in result["Contributing_Factors"]:
                    st.write(f"- {f}")


                if not st.session_state.awaiting_review:
                    # 🔥 這裡最重要：存下當前的 Index
                    st.session_state.locked_idx = st.session_state.current_idx
                    st.session_state.locked_event_id = st.session_state.current_event_id
                    # 🔥 STEP 1: show banner FIRST
                    st.session_state.awaiting_review = True

                    # ============================================================
                    # 🚨 ONLY FROZEN WARNING
                    # ============================================================
                    if st.session_state.get("awaiting_review"):

                        reason = []

                        if result["Final_binary"] == 1:
                            reason.append("Attack Detected")

                        if has_flag:
                            reason.append("Flag Detected")
                        
                        # 🔥 ADD THIS
                        if not reason:
                            reason.append("Manual Review — Press Resume to continue")

                        reason_text = " & ".join(reason) if reason else "Manual Review"

                        st.markdown(f"""
                        <div style="
                            width:100%;
                            padding:16px 18px;
                            margin-bottom:12px;
                            border-radius:10px;
                            background:linear-gradient(90deg,#7f1d1d,#dc2626);
                            color:white;
                            font-weight:700;
                            font-size:15px;
                            border:2px solid #ef4444;
                            text-align:center;
                        ">
                            🚨 SYSTEM FROZEN — Awaiting Analyst Review ({reason_text})
                        </div>
                        """, unsafe_allow_html=True)

                    st.session_state.running = False

                b1, b2, b3 = st.columns([1.5,1,1])

                with b1:
                    if st.button("🔍 Investigate", key="investigate_btn", use_container_width=True, type="secondary"):

                        e = st.session_state.current_event

                        if e:
                            # ✅ IDS LOG (M)
                            e["M"] = build_M(
                                result,
                                final_relay,
                                scenario,
                                mode,
                                action="Investigate"
                            )

                            # 🔥 mark modal mode
                            st.session_state.modal_mode = "investigate"

                            st.session_state.show_banner = False

                            # 🔥 store pending action
                            st.session_state.pending_action = e

                            st.session_state.modal_opened = True

                            # 🔥 open modal
                            st.session_state.selected_event = e


                with b2:
                    if st.button("🟡 Ack", key="ack_btn", use_container_width=True, type="secondary"):

                        e = st.session_state.current_event

                        if e:
                            e["M"] = build_M(
                                result,
                                final_relay,
                                scenario,
                                mode,
                                action="Acknowledge"
                            )

                            m_data = e["M"]

                            # guarantee Action exists
                            m_data["Action"] = m_data.get("Action", "Acknowledge")

                            add_log_row(
                                event_id=st.session_state.current_event_id,
                                source="IDS",
                                data=m_data
                            )
                            
                            st.session_state.awaiting_review = False
                            st.session_state.running = True


                with b3:
                    if st.button("⛔ Ignore", key="ignore_btn", use_container_width=True, type="secondary"):
                        st.session_state.confirm_ignore = st.session_state.current_event_id
                        st.rerun()

            else:
                st.markdown(f"**Condition:** {result['Final_label']}")
                st.markdown(f"**Path:** {result['Path']}")

                st.markdown("### Factors")
                for f in result["Contributing_Factors"]:
                    st.write(f"- {f}")
                
                # ============================================================
                # 🔥 AUTO LOG NORMAL (ONLY ONCE)
                # ============================================================
                e = get_current_event()

                if e and e.get("M") is None:
                    e["M"] = build_M(
                        result,
                        final_relay,
                        scenario,
                        mode,
                        action="Auto Log"
                    )

                    add_log_row(
                        event_id=e["Event ID"],
                        source="IDS",
                        data=e["M"]
                    )

                # =========================
                # REVIEW BUTTON ONLY
                # =========================
                if st.button("Review", key="view_logs_btn", use_container_width=True, type="secondary"):
                    if e:
                        st.session_state.modal_mode = "review"
                        st.session_state.selected_event = e
                        st.session_state.running = False
                        st.session_state.awaiting_review = True
        #=========================
        # ⚡ ACTIONS
        # =========================
        st.markdown("### ⚡ Actions")

        def get_target_relay():
            selected = st.session_state.get("selected_component")

            if selected and str(selected).startswith("R"):
                return selected

            selected_relay = st.session_state.get("selected_relay", "AUTO")
            if selected_relay != "AUTO":
                return selected_relay

            return st.session_state.get("control_target") or final_relay

        # 🔌 ISOLATE
        if st.button("🔌 Isolate", width="stretch", type="primary"):

            relay = get_target_relay()

            st.session_state.control_state["isolated"].add(relay)
            st.session_state.control_target = relay

            add_user_action("Isolate", relay)

            st.session_state.actions_clicked = True
            st.rerun()

        # 🔒 LOCK
        if st.button("🔒 Lock", width="stretch", type="primary"):

            relay = get_target_relay()

            st.session_state.control_state["locked"].add(relay)
            st.session_state.control_target = relay

            add_user_action("Lock", relay)

            st.session_state.actions_clicked = True
            st.rerun()

        # 🛠 RESTORE
        if st.button("🛠 Restore", width="stretch", type="primary"):

            relay = get_target_relay()

            if relay:
                st.session_state.control_state["isolated"].discard(relay)
                st.session_state.control_state["locked"].discard(relay)

                # clear saved target if it matches restored relay
                if st.session_state.get("control_target") == relay:
                    st.session_state.control_target = None

                add_user_action("Restore", relay)

            st.session_state.actions_clicked = True
            st.rerun()

    # ============================================================
    # 📋 EVENT LOG (FINAL VERSION)
    # ============================================================
    st.subheader("📋 Live Event Log")

    # =========================
    # BASE HEADERS
    # =========================
    headers = [
        "Event ID", "Timestamp", "Source", "Location",
        "Event Type", "Decision", "Confidence",
        "Path", "Scenario", "Original Scenario", "Action"
    ]

    # 🔥 REMOVE in LIVE MODE
    if mode != "Debug Mode":
        display_columns = [c for c in headers if c != "Original Scenario"]
    else:
        display_columns = headers

    # ➕ ADD VIEW COLUMN
    display_columns_with_view = display_columns + ["View"]

    # =========================
    # COLUMN WIDTHS
    # =========================
    column_widths = {
        "Event ID": 1,
        "Timestamp": 1.1,
        "Source": 1,
        "Location": 0.9,
        "Event Type": 2,
        "Decision": 1.5,
        "Confidence": 1,
        "Path": 1.2,
        "Scenario": 1,
        "Original Scenario": 1.5,
        "Action": 1,
        "View": 1
    }

    widths = [column_widths[c] for c in display_columns_with_view]

    # =========================
    # HEADER
    # =========================
    cols = st.columns(widths)

    for i, h in enumerate(display_columns_with_view):
        with cols[i]:
             st.markdown(f"""
            <div style="
                padding-left:20px;   /* 8px + 3px border alignment */
                font-size:16px;
                color:#ffffff;
                font-weight:600;
            ">
                {h}
            </div>
            """, unsafe_allow_html=True)

    
    # 🔥 OPEN SCROLL CONTAINER HERE
    with st.container(height=300):

        if not st.session_state.log_rows:
            st.info("Waiting for events...")
        else:
            # =========================
            # EVENT MAP (FAST LOOKUP)
            # =========================
            event_map = {e["Event ID"]: e for e in st.session_state.logs}

            # =========================
            # ROW RENDER FUNCTION
            # =========================
            def render_row(row, color, idx):

                cols = st.columns(widths)

                for i, key in enumerate(display_columns_with_view):
                    with cols[i]:

                        # 🔍 VIEW BUTTON
                        if key == "View":
                            if st.button(
                                "🔍",
                                key=f"view_{idx}", type="secondary", use_container_width=True
                            ):

                                event_id = row.get("Event ID")
                                e = event_map.get(event_id)

                                if e:
                                    # =========================
                                    # 👁 OPEN POPUP (VIEW ONLY)
                                    # =========================
                                    st.session_state.modal_mode = "view"
                                    st.session_state.selected_event = e
                        else:
                            val = row.get(key, "--")

                            st.markdown(f"""
                            <div style="
                                padding:6px 8px;
                                border-left:3px solid {color};
                                background:rgba(15,23,42,0.6);
                                border-radius:6px;
                                font-size:12px;
                                color:white;
                                white-space:nowrap;
                                overflow:hidden;
                                text-overflow:ellipsis;
                            ">
                                {val}
                            </div>
                            """, unsafe_allow_html=True)

            # =========================
            # GROUP LOGS BY EVENT ID
            # =========================
            from collections import defaultdict

            grouped = defaultdict(list)

            for row in st.session_state.log_rows:
                grouped[row["Event ID"]].append(row)

            # =========================
            # RENDER EVENTS
            # =========================
            row_counter = 0

            for event_id, rows in grouped.items():

                # sort by time
                rows = sorted(rows, key=lambda x: x["Timestamp"])

                for row in rows:

                    source = row.get("Source", "")

                    # 🎨 COLOR BY SOURCE
                    if source == "Physical":
                        color = "#3b82f6"   # blue
                    elif source == "IDS":
                        color = "#ef4444"   # red
                    elif source == "User":
                        color = "#f59e0b"   # yellow
                    else:
                        color = "#64748b"

                    render_row(row, color, row_counter)
                    row_counter += 1

                # 🔥 EVENT SEPARATOR
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)


if st.session_state.get("confirm_ignore"):
    confirm_ignore_dialog(
        result=result,
        final_relay=final_relay,
        scenario=scenario,
        mode=mode
    )

# ============================================================
# 🧾 EVENT POPUP VIEW (FINAL - 3 COLUMN LAYOUT)
# ============================================================
if st.session_state.get("selected_event"):
    show_event_detail(st.session_state.selected_event)


# ============================================================
# 🔥 CLOSE MAIN CONTENT (VERY IMPORTANT)
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# AUTO REFRESH
# ============================================================
if (
    st.session_state.running
    and not st.session_state.awaiting_review
    and st.session_state.get("selected_component") is None
    and st.session_state.get("selected_event") is None  # ✅ ADD THIS  # ✅ ADD THIS
):
    time.sleep(1)
    st.rerun()
