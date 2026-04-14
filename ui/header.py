import streamlit as st
from engine.utils import get_attack_type

def render_header(mode, df_debug, result=None,
                  final_relay="--", final_label="--"):

    # ============================================================
    # SAFE VALUES
    # ============================================================
    result = result or {}
    final_label = final_label or ""
    final_relay = final_relay or "--"

    running = st.session_state.get("running", False)
    awaiting_review = st.session_state.get("awaiting_review", False)

    # ============================================================
    # SCENARIO STATE INIT (DO THIS ONCE)
    # ============================================================
    if "scenario" not in st.session_state:
        markers = sorted(df_debug["marker"].unique())
        st.session_state.scenario = markers[0]

    # ============================================================
    # LAYOUT
    # ============================================================
    col_left, col_center, col_right = st.columns([3, 6, 2])

    # ============================================================
    # LEFT → MODE + SCENARIO + STATUS
    # ============================================================
    with col_left:

        c_mode, c_scenario, c_status = st.columns([1, 2, 3])

        # -------------------------
        # MODE
        # -------------------------
        with c_mode:
            if mode == "Debug Mode":
                st.badge("DEBUG", color="blue")
            else:
                st.badge("LIVE", color="red")

        # -------------------------
        # SCENARIO SELECTOR
        # -------------------------
        with c_scenario:
            if mode == "Debug Mode":

                markers = sorted(df_debug["marker"].unique())

                # safety check
                if st.session_state.scenario not in markers:
                    st.session_state.scenario = markers[0]

                selected = st.selectbox(
                    "",
                    markers,
                    index=markers.index(st.session_state.scenario),
                    key="header_scenario",
                    label_visibility="collapsed"
                )

                # 🔥 ONLY update scenario (NO RESET)
                if selected != st.session_state.scenario:
                    st.session_state.scenario = selected

            else:
                st.caption("Live Stream")

        # -------------------------
        # STATUS
        # PRIORITY: REVIEW > RUNNING > IDLE
        # -------------------------
        with c_status:

            c1, c2 = st.columns([1, 1])

            with c1:
                if awaiting_review:
                    st.badge("PAUSED", color="yellow")
                elif running:
                    st.badge("RUNNING", color="green")
                else:
                    st.badge("IDLE", color="gray")

            with c2:
                if awaiting_review:
                    st.badge("🚨 REVIEW", color="red")

    # ============================================================
    # CENTER → TITLE
    # ============================================================
    with col_center:
        st.markdown("""
        <div style='text-align:center; width:100%;'>
            <span style='font-size:26px; font-weight:700; color:#e2e8f0;'>
                ⚡ Hierarchical IDS Dashboard
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # RIGHT → ICON + RELAY + LABEL + SYSTEM STATE
    # ============================================================
    with col_right:

        c_icon, c_relay, c_label, c_system = st.columns([1, 1, 3, 2])

        label_raw = final_label.lower()

        # -------------------------
        # ICON
        # -------------------------
        with c_icon:

            if not result:
                st.badge("⚪", color="gray")

            elif result.get("Final_binary") == 1:
                st.badge("🔴", color="red")

            elif "fault" in label_raw:
                st.badge("🟡", color="yellow")

            elif "maintenance" in label_raw:
                st.badge("🔵", color="blue")

            else:
                st.badge("🟢", color="green")

        # -------------------------
        # RELAY
        # -------------------------
        with c_relay:
            st.badge(final_relay if final_relay != "--" else "--", color="blue")

        # -------------------------
        # LABEL
        # -------------------------
        with c_label:

            if not result:
                st.badge("Waiting", color="gray")

            elif result.get("Final_binary") == 1:
                try:
                    attack_type = get_attack_type(result.get("Final_class", 0))
                except:
                    attack_type = "Attack"

                st.badge(attack_type, color="red")

            else:
                if "maintenance" in label_raw:
                    st.badge(final_label, color="blue")
                elif "fault" in label_raw:
                    st.badge(final_label, color="yellow")
                elif "normal" in label_raw:
                    st.badge(final_label, color="green")
                else:
                    st.badge(final_label, color="gray")

        # -------------------------
        # SYSTEM STATE
        # -------------------------
        with c_system:

            if awaiting_review:
                st.badge("System Locked", color="red")
            elif running:
                st.badge("System Online", color="green")
            else:
                st.badge("System Idle", color="gray")

    return None