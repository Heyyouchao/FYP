import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(layout="wide")

# ============================================================
# LOAD STYLES
# ============================================================
from ui.styles import load_css
st.markdown(load_css(), unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
MODE_DEBUG = "Debug Mode"
MODE_LIVE = "Live Mode"

# ============================================================
# MAIN CONTAINER
# ============================================================
st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<h1 style="text-align:center; margin-bottom:5px; margin-top:20px; color:#e2e8f0; font-size:32px; font-weight:700;">
    Hierarchical Intrusion Detection System
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="text-align:center; color:#ffffff; font-size:24px;">
    Cyber-Physical Security Monitoring for Power Grid Systems
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SYSTEM STATUS (OPTIONAL BUT STRONG)
# ============================================================
st.markdown("""
<div style="
    text-align:center;
    margin-bottom:20px;
    font-size:20px;
    color:#ffffff;
">
    System Status: <span style="color:#22c55e;">READY</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""<h2 style="text-align:center;">Select System Mode</h2>""", unsafe_allow_html=True)

# =========================
# DEBUG MODE
# =========================
st.markdown("""
<div class="mode-box">
    <div class="mode-title">Debug Mode</div>
    <div class="mode-desc">
        Controlled simulation using labelled dataset scenarios.
        Ideal for testing, validation, and analysis.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])  # center button

with col2:
    if st.button("Start Debug Mode", use_container_width=True):
        st.session_state.mode = MODE_DEBUG
        st.switch_page("pages/Dashboard.py")


# =========================
# LIVE MODE
# =========================
st.markdown("""
<div class="mode-box live">
    <div class="mode-title">Live Mode</div>
    <div class="mode-desc">
        Real-time streaming with randomised events.
        Simulates live grid monitoring conditions.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    if st.button("Start Live Mode", use_container_width=True):
        st.session_state.mode = MODE_LIVE
        st.switch_page("pages/Dashboard.py")

# ============================================================
# FOOTER
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    font-size:12px;
    color:#64748b;
">
    Version 1.0 • Cyber-Physical IDS Research System
</div>
""", unsafe_allow_html=True)

# ============================================================
# CLOSE CONTAINER
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)