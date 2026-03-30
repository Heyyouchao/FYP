import streamlit as st

st.set_page_config(layout="wide")

from ui.styles import load_css
st.markdown(load_css(), unsafe_allow_html=True)

st.markdown('<div class="home-card">', unsafe_allow_html=True)

st.markdown("## ⚡ Hierarchical IDS System")
st.caption("Cyber-Physical Intrusion Detection System")

st.markdown("<br>", unsafe_allow_html=True)

# Buttons stacked (simple)
if st.button("🧪 Debug Mode", use_container_width=True):
    st.session_state.mode = "🧪 Debug Mode"
    st.switch_page("1_Dashboard")

if st.button("🔴 Live Mode", use_container_width=True):
    st.session_state.mode = "🔴 Live Mode"
    st.switch_page("1_Dashboard")

st.markdown('</div>', unsafe_allow_html=True)