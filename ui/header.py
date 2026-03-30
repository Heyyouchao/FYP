import streamlit as st

def render_header(mode, running, result, final_relay, relay_disturbance):
    
    # =========================
    # FLAG
    # =========================
    flag_active = st.session_state.get("alert_active", False)

    # =========================
    # STATUS
    # =========================
    status = "🟢 RUNNING" if running else "🟡 PAUSED"
    mode_label = "🔴 LIVE MODE" if mode == "🔴 Live Mode" else "🧪 DEBUG MODE"

    # =========================
    # INSIGHT
    # =========================
    if result["Final_binary"] == 1:
        insight_text = f"🚨 {result['Final_label']} @ {final_relay}"
        insight_color = "#ff4d4d"

    elif relay_disturbance[final_relay] > 0.5:
        insight_text = f"⚠️ Disturbance @ {final_relay}"
        insight_color = "#f59e0b"

    else:
        insight_text = "✅ Normal"
        insight_color = "#22c55e"

    # =========================
    # RENDER
    # =========================
    st.markdown(f"""
    <div class="header-bar">
        
        <div class="header-left">
            {mode_label}
        </div>

        <div class="header-center">
            ⚡ Hierarchical IDS Dashboard
        </div>

        <div class="header-right">
            <span class="status">{status}</span>

            {"<span class='flag'>🚩 ALERT</span>" if flag_active else ""}

            <span class="insight" style="color:{insight_color}">
                {insight_text}
            </span>
        </div>

    </div>
    """, unsafe_allow_html=True)