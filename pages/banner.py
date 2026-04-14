import streamlit as st

st.set_page_config(layout="wide")

# -------------------------
# INIT STATE
# -------------------------
if "show_banner" not in st.session_state:
    st.session_state.show_banner = False

# -------------------------
# TEST BUTTON
# -------------------------
if st.button("Toggle Banner"):
    st.session_state.show_banner = not st.session_state.show_banner

# -------------------------
# BANNER
# -------------------------
if st.session_state.show_banner:
    st.markdown("""
    <div style="
        width:100%;
        padding:16px;
        margin:15px 0;
        border-radius:10px;
        text-align:center;
        font-size:15px;
        font-weight:700;
        background:linear-gradient(90deg,#7f1d1d,#dc2626);
        color:white;
        border:2px solid #ef4444;
    ">
        🚨 TEST BANNER — WORKING
    </div>
    """, unsafe_allow_html=True)

st.write("Main app content here...")