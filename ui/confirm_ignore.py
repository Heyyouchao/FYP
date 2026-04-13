import streamlit as st
from helpers.event_helpers import add_user_action, add_log_row, build_M


@st.dialog("Confirm Ignore")
def confirm_ignore_dialog(result, final_relay, scenario, mode):
    st.markdown('<div class="dialog-small"></div>', unsafe_allow_html=True)
    event_id = st.session_state.get("confirm_ignore")
    relay    = (st.session_state.get("current_event") or {}).get("P", {}).get("Main Relay", "--")

    st.markdown(f"""
        <div style="text-align:center; padding: 10px 0 20px;">
            <div style="
                width: 56px; height: 56px; border-radius: 50%;
                background: #FCEBEB; border: 2px solid #A32D2D;
                display: flex; align-items: center; justify-content: center;
                margin: 0 auto 16px; font-size: 24px;
            ">⚠️</div>
            <p style="font-size:17px; font-weight:500; color:var(--color-text-primary); margin:0 0 8px;">
                Ignore event <code style="font-size:14px;">{event_id}</code>?
            </p>
            <p style="font-size:13px; color:#791F1F; line-height:1.6; margin:0;
                background:#FCEBEB; border-radius:8px; padding:10px 14px;
                border: 0.5px solid #A32D2D;">
                This event will be dismissed without further investigation.
                No isolate or lock actions will be applied.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.confirm_ignore = None
            st.rerun()

    with c2:
        if st.button("Ignore event", use_container_width=True, type="primary"):
            st.session_state.selected_event  = None
            e = st.session_state.current_event
            if e:
                e["M"] = build_M(result, final_relay, scenario, mode, action="Ignore")
                e["M"]["Action"] = e["M"].get("Action", "Ignore")
                add_log_row(e["Event ID"], source="IDS", data=e["M"])

            st.session_state.awaiting_review = False
            st.session_state.running         = True
            st.session_state.confirm_ignore  = None
            st.rerun()