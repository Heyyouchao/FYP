# ui/event_modal.py

import streamlit as st
import pandas as pd
import time
from helpers.event_helpers import add_log_row, add_user_action


# ============================================================
# 🔥 FIX: LOCAL HELPER (REQUIRED)
# ============================================================
def is_current_event(event_id):
    return event_id == st.session_state.get("current_event_id")


@st.dialog("Event Detail", width="large")
def show_event_detail(e):
    st.markdown('<div class="dialog-big"></div>', unsafe_allow_html=True)
    # ============================================================
    # HEADER
    # ============================================================
    st.markdown(f"""
        <div style='text-align:center; width:100%; margin-top:10px; margin-bottom:10px'>
            <span style='font-size:40px; font-weight:700;'>
                Event Detail
            </span>
        </div>
    """, unsafe_allow_html=True)

    # hide default close button
    st.markdown("""
    <style>
    button[aria-label="Close"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # DATA
    # ============================================================
    p_data = e.get("P") or {}
    m_data = e.get("M") or {}
    u_list = e.get("U") or []
    P_full = e.get("P_full") or {}

    event_id = e.get("Event ID", "UNKNOWN")
    relay = p_data.get("Main Relay", "--")

    p_time = p_data.get("Timestamp", "--")
    m_time = m_data.get("Timestamp", "--")
    u_time = u_list[-1].get("Timestamp", "--") if u_list else "--"

    def extract_time(ts):
        if not ts or ts == "--":
            return "-"
        ts = str(ts)
        if ":" in ts and ("AM" in ts or "PM" in ts) and len(ts.split()) <= 2:
            return ts
        parts = ts.split()
        if len(parts) >= 2:
            return " ".join(parts[-2:])
        return ts

    p_time_only = extract_time(p_time)
    ids_time_only = extract_time(m_time)
    user_time_only = extract_time(u_time)

    # ============================================================
    # HEADER UI
    # ============================================================
    col_header, col_tip = st.columns([3, 2])
    with col_header:
        st.markdown(f"""
        <div style="
            padding:12px 16px;
            border-radius:10px;
            background:linear-gradient(90deg,#0f172a,#1e293b);
            border:1px solid rgba(148,163,184,0.2);
            margin-bottom:10px;
        ">
            <b style="font-size:24px;">Event ID:</b> <b style="font-size:24px; color: #ffffff;"> {event_id}</b>
            <span style="float:right; font-size:24px;">
                ⚡ Relay: <b>{relay}</b>
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_tip:
        st.markdown("""
        <div style="
            margin: 10px 0 18px 0;
            padding: 12px 18px;
            border-radius: 12px;
            background: linear-gradient(145deg, rgba(30,41,59,0.7), rgba(15,23,42,0.7));
            border: 1px solid rgba(148,163,184,0.3);
            font-size: 24px;
            font-weight: 500;
            color: #fffffff;
            text-align: center;
        ">
            💡 Tip: If the popup does not close, click outside the window to exit.
        </div>
        """, unsafe_allow_html=True)
   
    st.markdown("## ⏱ Event Flow")

    flow_cols = st.columns([1.25, 0.08, 1, 0.08, 1])

    with flow_cols[0]:
        st.markdown(f"### ⚡ Physical ({p_time_only})")
    with flow_cols[2]:
        st.markdown(f"### 🛡 IDS ({ids_time_only})")
    with flow_cols[4]:
        st.markdown(f"### 👤 User ({user_time_only})")

    col1, _, col2, _, col3 = st.columns([1.25, 0.08, 1, 0.08, 1])

    # ============================================================
    # PHYSICAL
    # ============================================================
    with col1:
        if P_full:
            st.markdown("#### Measurements")
            st.dataframe(pd.DataFrame(P_full.get("Measurements", [])), use_container_width=True, hide_index=True)

            st.markdown("#### Relay Analysis")
            st.dataframe(pd.DataFrame(P_full.get("Relay Analysis", [])), use_container_width=True, hide_index=True)

            st.markdown("#### System State")
            st.dataframe(pd.DataFrame(P_full.get("System State", [])), use_container_width=True, hide_index=True)
        else:
            st.info("No physical data")

    # ============================================================
    # IDS
    # ============================================================
    with col2:
        st.markdown(" ")
        st.markdown(" ")

        if m_data:
            for key, value in m_data.items():
                st.markdown(f"""
                <div style="
                    font-size:20px;
                    font-weight:bold;
                    color:#ffffff;
                    margin-top:8px;
                    margin-bottom:10px;
                ">
                    {key}: {value}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Awaiting IDS decision")

    # ============================================================
    # USER + ACTIONS
    # ============================================================
    with col3:

        if u_list:
            st.dataframe(pd.DataFrame(u_list), use_container_width=True, hide_index=True)
        else:
            st.info("No user actions")

        st.markdown("### ⚡ Operator Actions")

        # init per-event state
        if "actions" not in e:
            e["actions"] = {
                "isolated": set(),
                "locked": set()
            }

        # =========================
        # 🔌 ISOLATE
        # =========================
        if st.button("🔌 Isolate", use_container_width=True, type="primary"):
            if relay != "--":

                if is_current_event(event_id):
                    st.session_state.control_state["isolated"].add(relay)

                e["actions"]["isolated"].add(relay)

                add_user_action("Isolate", relay, event_id=event_id)
                st.success(f"Isolated {relay}")

        # =========================
        # 🔒 LOCK
        # =========================
        if st.button("🔒 Lock", use_container_width=True, type="primary"):
            if relay != "--":

                if is_current_event(event_id):
                    st.session_state.control_state["locked"].add(relay)

                e["actions"]["locked"].add(relay)

                add_user_action("Lock", relay, event_id=event_id)
                st.success(f"Locked {relay}")

        # =========================
        # 🛠 RESTORE
        # =========================
        if st.button("🛠 Restore", use_container_width=True, type="primary"):
            if relay != "--":

                if is_current_event(event_id):
                    st.session_state.control_state["isolated"].discard(relay)
                    st.session_state.control_state["locked"].discard(relay)

                e["actions"]["isolated"].discard(relay)
                e["actions"]["locked"].discard(relay)

                add_user_action("Restore", relay, event_id=event_id)
                st.success(f"Restored {relay}")

        # =========================
        # 🟡 ACK
        # =========================
        if st.button("🟡 Ack", use_container_width=True, type="primary"):

            if is_current_event(event_id):
                st.session_state.awaiting_review = False

            add_user_action("Acknowledge", relay, event_id=event_id)
            st.success(f"Acknowledged event {event_id}")

        # =========================
        # ⛔ IGNORE (with confirm)
        # =========================
        if st.button("⛔ Ignore", use_container_width=True, type="primary"):
            if is_current_event(event_id):
                if st.session_state.get("confirm_ignore") == event_id:
                    # Confirmed — proceed
                    st.session_state.awaiting_review = False
                    st.session_state.running = True
                    add_user_action("Ignore", relay, event_id=event_id)
                    st.session_state.confirm_ignore = None
                    st.success(f"Ignored event {event_id}")
                else:
                    # First click — ask for confirmation
                    st.session_state.confirm_ignore = event_id

        if st.session_state.get("confirm_ignore") == event_id:
            st.warning("Are you sure you want to ignore this event?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, ignore", use_container_width=True, type="primary"):
                    st.session_state.awaiting_review = False
                    st.session_state.running = True
                    add_user_action("Ignore", relay, event_id=event_id)
                    st.session_state.confirm_ignore = None
                    st.success(f"Ignored event {event_id}")
                    st.rerun()
            with col2:
                if st.button("↩️ Cancel", use_container_width=True):
                    st.session_state.confirm_ignore = None
                    st.rerun()
    # ============================================================
    # CLOSE
    # ============================================================
    st.markdown(" ")

    if st.button("Close", use_container_width=True):

        if st.session_state.get("modal_mode") == "investigate":

            e_pending = st.session_state.get("pending_action")

            if e_pending and e_pending.get("M"):
                add_log_row(
                    e_pending["Event ID"],
                    source="IDS",
                    data=e_pending["M"]
                )

            st.session_state.awaiting_review = False
            st.session_state.running = True

        # =========================
        # 📋 REVIEW → NO LOG
        # =========================
        elif st.session_state.get("modal_mode") == "review":
            pass 

        # DO NOT TOUCH CURRENT EVENT
        st.session_state.pending_action = None
        st.session_state.modal_mode = None
        st.session_state.selected_event = None
        st.session_state.modal_opened= False
        st.session_state.actions_clicked = False

        st.rerun()
