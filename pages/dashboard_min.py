import streamlit as st
import pandas as pd
import datetime
import time

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(layout="wide")

# 👉 make dialog wider
st.markdown("""
<style>
div[role="dialog"] {
    width: 90vw !important;
    max-width: 1400px !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "logs" not in st.session_state:
    st.session_state.logs = []

if "log_rows" not in st.session_state:
    st.session_state.log_rows = []

if "event_counter" not in st.session_state:
    st.session_state.event_counter = 1000

if "awaiting_review" not in st.session_state:
    st.session_state.awaiting_review = False

if "current_event" not in st.session_state:
    st.session_state.current_event = None

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# ============================================================
# TIME
# ============================================================
def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

def now_full():
    return datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

# ============================================================
# LOGGING
# ============================================================
def add_log_row(event_id, source, data):

    row = {
        "Event ID": event_id,
        "Timestamp": now_full(),
        "Source": source,
        "Location": data.get("Location", "--"),
        "Model Decision": data.get("Model Decision", "--"),
        "Event Type": data.get("Event Type", "--"),
        "Decision": data.get("Decision", "--"),
        "Confidence": data.get("Confidence", "--"),
        "Path": data.get("Path", "--"),
        "Scenario": data.get("Scenario", "--"),
        "Original Scenario": data.get("Original Scenario", "--"),
        "Action": data.get("Action", "--"),
    }

    st.session_state.log_rows.insert(0, row)

# ============================================================
# CREATE EVENT
# ============================================================
def create_event(final_relay):

    event_id = f"E-{st.session_state.event_counter}"
    st.session_state.event_counter += 1

    event = {
        "Event ID": event_id,
        "P": {
            "Timestamp": now(),
            "Main Relay": final_relay
        },
        "P_full": {},
        "M": None,
        "U": []
    }

    st.session_state.logs.insert(0, event)
    st.session_state.current_event = event

    add_log_row(
        event_id,
        "Physical",
        {
            "Location": final_relay,
            "Event Type": "Physical Disturbance",
            "Action": "Auto Detected"
        }
    )

    return event

# ============================================================
# IDS BUILD
# ============================================================
def build_M(action, final_relay):

    return {
        "Timestamp": now_full(),
        "Source": "IDS",
        "Location": final_relay,
        "Model Decision": "Attack",
        "Event Type": "Cyber Attack",
        "Decision": "Alert",
        "Confidence": "95%",
        "Path": "Grid",
        "Scenario": "SC-1",
        "Original Scenario": "--",
        "Action": action
    }

# ============================================================
# MODAL (NATIVE)
# ============================================================
@st.dialog("🧾 Event Detail", width="large")
def show_event_detail(e):

    st.markdown(f"## Event Detail — {e.get('Event ID')}")

    # -------------------------
    # PHYSICAL
    # -------------------------
    st.markdown("### ⚡ Physical Snapshot")

    P_full = e.get("P_full", {})

    if P_full:
        st.dataframe(pd.DataFrame(P_full.get("Measurements", [])), use_container_width=True)
        st.dataframe(pd.DataFrame(P_full.get("Relay Analysis", [])), use_container_width=True)
        st.dataframe(pd.DataFrame(P_full.get("System State", [])), use_container_width=True)
    else:
        st.info("No physical data")

    # -------------------------
    # IDS
    # -------------------------
    st.markdown("### 🛡 IDS Details")

    if e.get("M"):
        st.dataframe(pd.DataFrame([e["M"]]), use_container_width=True)
    else:
        st.warning("Awaiting IDS decision")

    # -------------------------
    # USER
    # -------------------------
    st.markdown("### 👤 User Actions")

    if e.get("U"):
        st.dataframe(pd.DataFrame(e["U"]), use_container_width=True)
    else:
        st.info("No user actions")

    # CLOSE
    if st.button("Close", use_container_width=True):
        st.session_state.selected_event = None
        st.rerun()

# ============================================================
# SIMULATION
# ============================================================
if st.button("⚡ Simulate Attack") and not st.session_state.awaiting_review:
    create_event("R2")
    st.session_state.awaiting_review = True

# ============================================================
# IDS PANEL
# ============================================================
st.subheader("🚨 IDS Panel")

if st.session_state.awaiting_review:

    st.error("⚠️ Attack Detected")

    e = st.session_state.current_event

    c1, c2, c3 = st.columns(3)

    # INVESTIGATE
    with c1:
        if st.button("🔍 Investigate"):
            if e and not e.get("M"):
                e["M"] = build_M("Investigate", "R2")
                add_log_row(e["Event ID"], "IDS", e["M"])

            st.session_state.selected_event = e
            st.rerun()

    # ACK
    with c2:
        if st.button("🟡 Ack"):
            if e and not e.get("M"):
                e["M"] = build_M("Acknowledge", "R2")
                add_log_row(e["Event ID"], "IDS", e["M"])

            st.session_state.awaiting_review = False

    # IGNORE
    with c3:
        if st.button("⛔ Ignore"):
            if e and not e.get("M"):
                e["M"] = build_M("Ignore", "R2")
                add_log_row(e["Event ID"], "IDS", e["M"])

            st.session_state.awaiting_review = False

# ============================================================
# USER ACTIONS
# ============================================================
st.subheader("⚡ Actions")

if st.button("Isolate"):
    e = st.session_state.current_event
    if e:
        e["U"].append({
            "Timestamp": now(),
            "Action": "Isolate",
            "Location": "R2"
        })

        add_log_row(
            e["Event ID"],
            "User",
            {
                "Location": "R2",
                "Event Type": "Control Action",
                "Action": "Isolate"
            }
        )

# ============================================================
# EVENT LOG (CLICKABLE)
# ============================================================
st.subheader("📋 Live Event Log")

if st.session_state.log_rows:

    df_logs = pd.DataFrame(st.session_state.log_rows)

    for i, row in df_logs.iterrows():

        cols = st.columns([1,2,2,2,1])

        cols[0].write(row["Event ID"])
        cols[1].write(row["Timestamp"])
        cols[2].write(row["Source"])
        cols[3].write(row["Event Type"])

        if cols[4].button("View", key=f"view_{i}"):

            for e in st.session_state.logs:
                if e["Event ID"] == row["Event ID"]:
                    st.session_state.selected_event = e
                    st.rerun()
                    break

# ============================================================
# TRIGGER MODAL
# ============================================================
if st.session_state.get("selected_event"):
    show_event_detail(st.session_state.selected_event)

# ============================================================
# AUTO REFRESH
# ============================================================
if (
    st.session_state.awaiting_review
    and st.session_state.get("selected_event") is None
):
    time.sleep(1)
    st.rerun()