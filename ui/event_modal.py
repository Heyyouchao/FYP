import streamlit as st
import pandas as pd


@st.dialog("🧾 Event Detail", width="large")
def show_event_detail(e):

    st.markdown(f"## 🧾 Event Detail — {e.get('Event ID')}")

    P_full = e.get("P_full", {})

    # =========================
    # ⚡ PHYSICAL (3 TABLES)
    # =========================
    st.markdown("## ⚡ Physical Snapshot")

    # 1️⃣ Measurements
    df_measure = pd.DataFrame(P_full.get("Measurements", []))
    if not df_measure.empty:
        df_measure = df_measure.rename(columns={
            "Voltage": "Voltage (kV)",
            "Current": "Current (A)",
            "Frequency": "Frequency (Hz)",
            "Pos": "Pos (%)",
            "Neg": "Neg (%)",
            "Zero": "Zero (%)"
        })
        st.dataframe(df_measure, use_container_width=True, hide_index=True)

    # 2️⃣ Relay Analysis
    df_relay = pd.DataFrame(P_full.get("Relay Analysis", []))
    if not df_relay.empty:
        df_relay = df_relay[
            ["Relay", "State", "Raw", "Norm", "Flag", "Affect", "Top Causes"]
        ]
        st.dataframe(df_relay, use_container_width=True, hide_index=True)

    # 3️⃣ System State
    df_system = pd.DataFrame(P_full.get("System State", []))
    if not df_system.empty:
        st.dataframe(df_system, use_container_width=True, hide_index=True)

    # =========================
    # 🛡 IDS
    # =========================
    st.markdown("## 🛡 IDS Details")

    if e.get("M"):
        st.dataframe(pd.DataFrame([e["M"]]), use_container_width=True, hide_index=True)
    else:
        st.warning("Awaiting IDS decision")

    # =========================
    # 👤 USER
    # =========================
    st.markdown("## 👤 User Actions")

    if e.get("U"):
        df_u = pd.DataFrame([
            {
                "Time": u.get("Timestamp"),
                "Action": u.get("Action"),
                "Location": u.get("Location")
            }
            for u in e["U"]
        ])
        st.dataframe(df_u, use_container_width=True, hide_index=True)
    else:
        st.info("No user actions")