# ui/event_modal.py

import streamlit as st
import pandas as pd

from helpers.event_helpers import add_log_row, add_user_action


# ============================================================
# 🔥 FIX: LOCAL HELPER (REQUIRED)
# ============================================================
def is_current_event(event_id):
    return event_id == st.session_state.get("current_event_id")


@st.dialog(" ", width="large")
def show_event_detail(e):

    # ============================================================
    # HEADER
    # ============================================================
    st.markdown("""
        <div style='text-align:center; width:100%; margin-top:-15px;'>
            <span style='font-size:36px; font-weight:700; color:#e2e8f0;'>
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
    st.markdown(f"""
    <div style="
        padding:12px 16px;
        border-radius:10px;
        background:linear-gradient(90deg,#0f172a,#1e293b);
        border:1px solid rgba(148,163,184,0.2);
        margin-bottom:10px;
    ">
        <b style="font-size:24px;">Event ID:</b> {event_id}
        <span style="float:right; font-size:24px;">
            ⚡ Relay: <b>{relay}</b>
        </span>
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
        if st.button("🔌 Isolate", use_container_width=True):
            if relay != "--":

                if is_current_event(event_id):
                    st.session_state.control_state["isolated"].add(relay)

                e["actions"]["isolated"].add(relay)

                add_user_action("Isolate", relay, event_id=event_id)
                st.success(f"Isolated {relay}")

        # =========================
        # 🔒 LOCK
        # =========================
        if st.button("🔒 Lock", use_container_width=True):
            if relay != "--":

                if is_current_event(event_id):
                    st.session_state.control_state["locked"].add(relay)

                e["actions"]["locked"].add(relay)

                add_user_action("Lock", relay, event_id=event_id)
                st.success(f"Locked {relay}")

        # =========================
        # 🛠 RESTORE
        # =========================
        if st.button("🛠 Restore", use_container_width=True):
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
        if st.button("🟡 Ack", use_container_width=True):

            if is_current_event(event_id):
                st.session_state.awaiting_review = False

            add_user_action("Acknowledge", relay, event_id=event_id)
            st.success(f"Acknowledged event {event_id}")

        # =========================
        # ⛔ IGNORE
        # =========================
        if st.button("⛔ Ignore", use_container_width=True):

            if is_current_event(event_id):
                st.session_state.awaiting_review = False
                st.session_state.running = True

            add_user_action("Ignore", relay, event_id=event_id)
            st.success(f"Ignored event {event_id}")

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

        # DO NOT TOUCH CURRENT EVENT

        st.session_state.closing_modal = True
        st.session_state.pending_action = None
        st.session_state.modal_mode = None
        st.session_state.selected_event = None
        st.session_state.actions_clicked = False

        st.rerun()