import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(
    page_title="IDS Alert Beacon",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
    section[data-testid="stMain"] { padding: 0 !important; overflow: hidden !important; }
    div[data-testid="stVerticalBlock"] { gap: 0 !important; }
    iframe { display: block; width: 100vw !important; height: 100vh !important; border: none; position: fixed; top: 0; left: 0; }
    .stApp { background: #0e1117; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SHARED STATE
# ============================================================
@st.cache_resource
def get_global_alert_state():
    return {
        "is_attack":       False,
        "has_flag":        False,
        "started":         False,
        "awaiting_review": False,
        "investigating":   False,
        "paused":          False,
    }

s = get_global_alert_state()

# ============================================================
# STATE LOGIC
# ============================================================
if not s["started"]:
    state = "IDLE"
elif s.get("paused", False):
    state = "PAUSED"
elif s.get("investigating", False):
    state = "INVESTIGATING"
elif s["is_attack"] and s["has_flag"]:
    state = "BOTH"
elif s["is_attack"]:
    state = "ATTACK"
elif s["has_flag"]:
    state = "FLAG"
elif s["awaiting_review"]:
    state = "PAUSED"
else:
    state = "RUNNING"

# ============================================================
# STATE 1 — IDLE
# ============================================================
if state == "IDLE":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes breathe { 0%,100%{opacity:0.5} 50%{opacity:0.15} }
body {
  width:100vw; height:100vh; background:#060d1a;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.ring {
  width:120px; height:120px;
  border:8px solid #334155;
  border-radius:50%; margin-bottom:52px;
  animation:breathe 2.5s ease-in-out infinite;
  box-shadow:0 0 40px #33415544;
}
.title {
  color:#475569;
  font-size:96px;
  font-weight:900;
  letter-spacing:12px;
  text-align:center;
  line-height:1.0;
  animation:breathe 2.5s ease-in-out infinite;
  font-family:Arial Black,Arial,sans-serif;
}
.sub {
  color:#1e293b;
  font-size:24px;
  font-weight:700;
  margin-top:28px;
  letter-spacing:6px;
  text-transform:uppercase;
}
</style></head><body>
  <div class="ring"></div>
  <div class="title">SYSTEM<br>IDLE</div>
  <div class="sub">Press Start on Dashboard</div>
</body></html>
""", height=1000)

# ============================================================
# STATE 2 — RUNNING
# ============================================================
elif state == "RUNNING":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes breathe { 0%,100%{opacity:1} 50%{opacity:0.65} }
@keyframes dot-pulse {
  0%,100% { transform:scale(1); opacity:1; }
  50% { transform:scale(1.4); opacity:0.6; }
}
body {
  width:100vw; height:100vh; background:#060d1a;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.dot {
  width:52px; height:52px; background:#22c55e;
  border-radius:50%; margin-bottom:40px;
  animation:dot-pulse 2s ease-in-out infinite;
  box-shadow:0 0 40px #22c55e99;
}
.title {
  color:#22c55e;
  font-size:96px;
  font-weight:900;
  text-align:center;
  letter-spacing:6px;
  line-height:1.0;
  animation:breathe 3s ease-in-out infinite;
  font-family:Arial Black,Arial,sans-serif;
}
.sub {
  color:#475569;
  font-size:24px;
  font-weight:700;
  text-align:center;
  margin-top:24px;
  letter-spacing:4px;
  text-transform:uppercase;
}
.stats { display:flex; gap:48px; margin-top:52px; }
.stat { text-align:center; }
.stat-val { color:#22c55e; font-size:36px; font-weight:900; }
.stat-lbl { color:#334155; font-size:13px; font-weight:700; letter-spacing:3px; text-transform:uppercase; margin-top:6px; }
</style></head><body>
  <div class="dot"></div>
  <div class="title">SYSTEM<br>ONLINE</div>
  <div class="sub">Monitoring Power Grid...</div>
  <div class="stats">
    <div class="stat"><div class="stat-val">94.6%</div><div class="stat-lbl">Recall</div></div>
    <div class="stat"><div class="stat-val">R1–R4</div><div class="stat-lbl">Relays</div></div>
    <div class="stat"><div class="stat-val">Live</div><div class="stat-lbl">Stream</div></div>
  </div>
</body></html>
""", height=1000)

# ============================================================
# STATE 3 — INVESTIGATING
# ============================================================
elif state == "INVESTIGATING":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes breathe { 0%,100%{opacity:1} 50%{opacity:0.55} }
@keyframes dot-pulse {
  0%,100% { transform:scale(1); opacity:1; }
  50% { transform:scale(1.4); opacity:0.6; }
}
body {
  width:100vw; height:100vh; background:#060d1a;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.dot {
  width:52px; height:52px; background:#A78BFA;
  border-radius:50%; margin-bottom:40px;
  animation:dot-pulse 1.5s ease-in-out infinite;
  box-shadow:0 0 40px #A78BFA99;
}
.icon {
  font-size:100px; margin-bottom:16px;
  animation:breathe 1.5s ease-in-out infinite;
}
.title {
  color:#A78BFA;
  font-size:88px;
  font-weight:900;
  text-align:center;
  letter-spacing:6px;
  line-height:1.0;
  animation:breathe 1.5s ease-in-out infinite;
  font-family:Arial Black,Arial,sans-serif;
}
.sub {
  color:#6D28D9;
  font-size:26px;
  font-weight:700;
  text-align:center;
  margin-top:24px;
  letter-spacing:4px;
  text-transform:uppercase;
}
.badge {
  margin-top:36px;
  padding:16px 52px;
  background:linear-gradient(90deg,#2e1065,#4c1d95,#2e1065);
  border:2px solid #7C3AED;
  border-radius:40px;
  color:#A78BFA;
  font-size:20px;
  font-weight:900;
  letter-spacing:4px;
  text-transform:uppercase;
  animation:breathe 1.5s ease-in-out infinite;
}
</style></head><body>
  <div class="icon">🔍</div>
  <div class="title">UNDER<br>INVESTIGATION</div>
  <div class="sub">Analyst reviewing event details</div>
  <div class="badge">🔒 System Frozen</div>
</body></html>
""", height=1000)

# ============================================================
# STATE 4 — ATTACK
# ============================================================
elif state == "ATTACK":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes flash { 0%,49%{background:#cc0000;} 50%,100%{background:#000000;} }
@keyframes pulse-text { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.85;transform:scale(1.03);} }
body {
  width:100vw; height:100vh;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  animation:flash 0.6s steps(1) infinite;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.icon { font-size:120px; line-height:1; animation:pulse-text 0.6s ease-in-out infinite; margin-bottom:20px; }
.title {
  color:white; font-size:100px; font-weight:900;
  text-align:center; line-height:1.0; letter-spacing:4px;
  animation:pulse-text 0.6s ease-in-out infinite;
  text-shadow:0 0 60px rgba(255,255,255,0.5);
  font-family:Arial Black,Arial,sans-serif;
}
.subtitle {
  color:#ffaaaa; font-size:28px; font-weight:700;
  text-align:center; margin-top:20px;
  letter-spacing:5px; text-transform:uppercase;
}
.reason {
  color:#ff6666; font-size:20px; font-weight:700;
  text-align:center; margin-top:14px; letter-spacing:3px;
}
</style></head><body>
  <div class="icon">&#x26A0;&#xFE0F;</div>
  <div class="title">INTRUSION<br>DETECTED</div>
  <div class="subtitle">System Frozen — Awaiting Analyst</div>
  <div class="reason">Frozen: Attack Detected by IDS</div>
</body></html>
""", height=1000)

# ============================================================
# STATE 5 — FLAG
# ============================================================
elif state == "FLAG":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes flash { 0%,49%{background:#78350f;} 50%,100%{background:#000000;} }
@keyframes pulse-text { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.85;transform:scale(1.03);} }
body {
  width:100vw; height:100vh;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  animation:flash 0.7s steps(1) infinite;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.icon { font-size:120px; line-height:1; animation:pulse-text 0.7s ease-in-out infinite; margin-bottom:20px; }
.title {
  color:white; font-size:100px; font-weight:900;
  text-align:center; line-height:1.0; letter-spacing:4px;
  animation:pulse-text 0.7s ease-in-out infinite;
  text-shadow:0 0 60px rgba(255,255,255,0.5);
  font-family:Arial Black,Arial,sans-serif;
}
.subtitle {
  color:#fde68a; font-size:28px; font-weight:700;
  text-align:center; margin-top:20px;
  letter-spacing:5px; text-transform:uppercase;
}
.reason {
  color:#fcd34d; font-size:20px; font-weight:700;
  text-align:center; margin-top:14px; letter-spacing:3px;
}
</style></head><body>
  <div class="icon">&#x26A0;&#xFE0F;</div>
  <div class="title">IMPEDANCE<br>FLAG</div>
  <div class="subtitle">System Frozen — Awaiting Analyst</div>
  <div class="reason">Frozen: Impedance Anomaly Detected</div>
</body></html>
""", height=1000)

# ============================================================
# STATE 6 — BOTH
# ============================================================
elif state == "BOTH":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes flash {
  0%,32%{background:#cc0000;}
  33%,65%{background:#000000;}
  66%,99%{background:#78350f;}
  100%{background:#000000;}
}
@keyframes pulse-text { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.85;transform:scale(1.03);} }
body {
  width:100vw; height:100vh;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  animation:flash 0.9s steps(1) infinite;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.icon { font-size:100px; line-height:1; animation:pulse-text 0.9s ease-in-out infinite; margin-bottom:16px; }
.title {
  color:white; font-size:88px; font-weight:900;
  text-align:center; line-height:1.0; letter-spacing:3px;
  animation:pulse-text 0.9s ease-in-out infinite;
  text-shadow:0 0 60px rgba(255,255,255,0.5);
  font-family:Arial Black,Arial,sans-serif;
}
.badges { display:flex; gap:16px; margin-top:20px; justify-content:center; flex-wrap:wrap; }
.badge-red { background:rgba(220,38,38,0.3); border:2px solid #ef4444; border-radius:30px; padding:10px 24px; color:#fca5a5; font-size:16px; font-weight:900; letter-spacing:3px; }
.badge-amber { background:rgba(217,119,6,0.3); border:2px solid #f59e0b; border-radius:30px; padding:10px 24px; color:#fcd34d; font-size:16px; font-weight:900; letter-spacing:3px; }
.reason { color:#ff9999; font-size:20px; font-weight:700; text-align:center; margin-top:16px; letter-spacing:3px; }
</style></head><body>
  <div class="icon">&#x1F6A8;</div>
  <div class="title">ATTACK &amp;<br>FLAG DETECTED</div>
  <div class="badges">
    <div class="badge-red">&#x26A1; INTRUSION CONFIRMED</div>
    <div class="badge-amber">&#x26A0;&#xFE0F; IMPEDANCE FLAG</div>
  </div>
  <div class="reason">Frozen: Attack Detected + Impedance Flag</div>
</body></html>
""", height=1000)

# ============================================================
# STATE 7 — PAUSED
# ============================================================
elif state == "PAUSED":
    components.html("""
<!DOCTYPE html><html><head><style>
* { margin:0; padding:0; box-sizing:border-box; }
@keyframes breathe { 0%,100%{opacity:1} 50%{opacity:0.5} }
@keyframes dot-pulse {
  0%,100% { transform:scale(1); opacity:1; }
  50% { transform:scale(1.4); opacity:0.6; }
}
body {
  width:100vw; height:100vh; background:#060d1a;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  font-family:Arial Black,Arial,sans-serif; overflow:hidden;
}
.dot {
  width:52px; height:52px; background:#3B9EDD;
  border-radius:50%; margin-bottom:40px;
  animation:dot-pulse 1.5s ease-in-out infinite;
  box-shadow:0 0 40px #3B9EDD99;
}
.title {
  color:#3B9EDD;
  font-size:96px;
  font-weight:900;
  text-align:center;
  letter-spacing:6px;
  line-height:1.0;
  animation:breathe 1.5s ease-in-out infinite;
  font-family:Arial Black,Arial,sans-serif;
}
.sub {
  color:#475569;
  font-size:24px;
  font-weight:700;
  text-align:center;
  margin-top:24px;
  letter-spacing:4px;
  text-transform:uppercase;
}
.reason {
  color:#1e3a5f;
  font-size:20px;
  font-weight:700;
  text-align:center;
  margin-top:14px;
  letter-spacing:3px;
}
</style></head><body>
  <div class="dot"></div>
  <div class="title">SYSTEM<br>HOLD</div>
  <div class="sub">Paused — Awaiting Analyst Review</div>
  <div class="reason">Frozen: Operator reviewing event</div>
</body></html>
""", height=1000)

# ============================================================
# AUTO REFRESH — every 1 second
# ============================================================
time.sleep(1)
st.rerun()