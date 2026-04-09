import streamlit as st

def render_header(mode, running, df_debug, result=None):

    col_left, col_center, col_right = st.columns([2, 6, 2])

    # =========================
    # LEFT → MODE + SCENARIO
    # =========================
    with col_left:

        col1, col2 = st.columns([4, 2])

        with col1:

            if mode == "Debug Mode":

                col_mode, col_scenario = st.columns([1, 2])

                with col_mode:
                    st.markdown(" **DEBUG**")

                with col_scenario:
                    scenario = st.selectbox(
                        "",
                        sorted(df_debug["marker"].unique()),
                        key="header_scenario",
                        label_visibility="collapsed"
                    )

            else:
                scenario = None

                col_mode, col_scenario = st.columns([1, 2])

                with col_mode:
                    st.markdown("🔴 **LIVE**")

                with col_scenario:

                    # DEFAULT
                    label = "--"
                    border = "#6b7280"
                    bg = "rgba(107,114,128,0.12)"
                    text = "#e5e7eb"

                    if result is not None:
                        final_label = str(result.get("Final_label", "")).lower()
                        final_binary = result.get("Final_binary", 0)

                        if final_binary == 0 and "maintenance" not in final_label:
                            label = "Normal"
                            border = "#22c55e"
                            bg = "rgba(34,197,94,0.12)"
                            text = "#dcfce7"

                        elif "maintenance" in final_label:
                            label = "Maintenance"
                            border = "#3b82f6"
                            bg = "rgba(59,130,246,0.12)"
                            text = "#dbeafe"

                        elif final_binary == 1:
                            label = f"Attack {result.get('Final_class', '--')}"
                            border = "#ef4444"
                            bg = "rgba(239,68,68,0.12)"
                            text = "#fee2e2"

                    st.markdown(
                        f"""
                        <div style="
                            padding:6px 10px;
                            border-radius:8px;
                            border:2px solid {border};
                            background:{bg};
                            color:{text};
                            font-size:13px;
                            font-weight:700;
                            display:inline-block;
                        ">
                            {label}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # STATUS
        with col2:
            status = "🟢 RUNNING" if running else "🟡 PAUSED"

            st.markdown(
                f"<div class='status'>{status}</div>",
                unsafe_allow_html=True
            )

    # =========================
    # CENTER → TITLE
    # =========================
    with col_center:

        st.markdown("""
        <div style='text-align:center; width:100%; margin-top:-2px;'>
            <span style='font-size:26px; font-weight:700; color:#e2e8f0;'>
                ⚡ Hierarchical IDS Dashboard
            </span>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # RIGHT → INSIGHT
    # =========================
    with col_right:

        if result:
            if result["Final_binary"] == 1:
                insight = f"Attack {result.get('Final_class', '')}"
                color = "#ef4444"
            else:
                insight = "Normal"
                color = "#22c55e"
        else:
            insight = "System Idle"
            color = "#9ca3af"

        st.markdown(
            f"""
            <div style='text-align:right; margin-top:4px;'>
                <div style='font-size:14px; font-weight:600; color:{color}'>
                    {insight}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    return scenario