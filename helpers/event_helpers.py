# helpers/event_helpers.py

import streamlit as st
import pandas as pd
import datetime

from engine.utils import get_attack_type


def now():
    return datetime.datetime.now().strftime("%I:%M:%S %p")

def now_full():
    return datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

def get_current_event():
    return st.session_state.get("current_event", None)

def add_user_action(action, final_relay, event_id=None):
    
    # ============================================================
    # 🔥 FIX: ALWAYS RESOLVE EVENT BY ID (NO GUESSING)
    # ============================================================
    if event_id:
        event = next(
            (e for e in st.session_state.logs if e["Event ID"] == event_id),
            None
        )
    else:
        event = st.session_state.get("selected_event") or get_current_event()

    if not event:
        return

    # ============================================================
    # ✅ SAFE APPEND
    # ============================================================
    event["U"].append({
        "Timestamp": now(),
        "Action": action,
        "Location": final_relay
    })

    # ============================================================
    # ✅ LOG (CORRECT EVENT)
    # ============================================================
    add_log_row(
        event["Event ID"],
        "User",
        {
            "Location": final_relay,
            "Model Decision": "Manual",
            "Event Type": "Countermeasure",
            "Decision": action,
            "Confidence": "--",
            "Path": "Grid",
            "Scenario": "--",
            "Original Scenario": "--",
            "Action": action
        }
    )

def create_event(row_clean, raw_scores, norm_scores, physical_layer, final_relay, build_physical_snapshot):
    event_id = f"E-{st.session_state.event_counter}"
    st.session_state.event_counter += 1

    physical_snapshot = build_physical_snapshot(
        row_clean,
        raw_scores,
        norm_scores,
        physical_layer
    )

    event = {
        "Event ID": event_id,
        "P": {
            "Timestamp": now(),
            "Main Relay": final_relay,
        },
        "P_full": physical_snapshot,
        "M": None,
        "U": []
    }

    st.session_state.logs.insert(0, event)
    st.session_state.logs = st.session_state.logs[:500]

    st.session_state.current_event = event
    st.session_state.current_event_id = event_id

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

def build_M(result, final_relay, scenario, mode, action):
    return {
        "Timestamp": now_full(),
        "Source": "IDS",
        "Location": final_relay,
        "Model Decision": "Attack" if result["Final_binary"] == 1 else "Normal",
        "Event Type": (
            get_attack_type(result["Final_class"])
            if result["Final_binary"] == 1
            else result["Final_label"]
        ),
        "Decision": result["Decision"],
        "Confidence": f"{result['Final_conf']:.0%}",
        "Path": result["Path"],
        "Scenario": result["Final_class"] if result["Final_binary"] == 1 else "--",
        "Original Scenario": scenario if mode == "🧪 Debug Mode" else "--",
        "Action": action
    }

def add_log_row(event_id, source, data):
    row = {
        "Event ID": event_id,
        "Timestamp": now(),
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
    st.session_state.log_rows = st.session_state.log_rows[:500]