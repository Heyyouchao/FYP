def load_css():
    return """
    <style>

/* =========================
   GLOBAL BACKGROUND
========================= */
body {
    background: radial-gradient(circle at top, #0b1a2a, #020617);
    color: #e5e7eb;
}

/* =========================
   HEADER
========================= */
.header-container {
    position: relative;
    background: linear-gradient(90deg, #0f172a, #1e293b);
    padding: 12px 20px;              /* 🔥 reduced height */
    border-radius: 12px;
    margin-bottom: -10px;              /* 🔥 remove space below */
    border-bottom: 1px solid rgba(148,163,184,0.15);  /* subtle separator */
}

.header-title-center {
    position: absolute;
    left: 50%;
    top: 50%;                        /* 🔥 vertical centering */
    transform: translate(-50%, -50%);
    font-size: 28px;                 /* 🔥 better proportion */
    font-weight: 700;
    color: #e2e8f0;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    height: 100%;                    /* 🔥 align vertically */
}

.header-right {
    position: absolute;
    right: 20px;
    top: 50%;                        /* 🔥 vertical centering */
    transform: translateY(-50%);
}



/* remove extra vertical spacing between blocks */
div[data-testid="stVerticalBlock"] {
    gap: 0.3rem !important;
}

/* kill invisible spacer */
div[data-testid="stMarkdownContainer"] {
    margin-bottom: 0 !important;
}


/* =========================
   MODE / STATUS
========================= */
.mode-active {
    padding: 6px 12px;
    border-radius: 8px;
    background: #3b82f6;
    color: white;
    font-weight: 600;
}

.mode-active.live {
    background: #ef4444;
}

.status {
    font-size: 20px;
    font-weight: 600;
}

.status.running {
    color: #22c55e;
}

.status.paused {
    color: #eab308;
}

.status.running::before {
    content: "";
    width: 6px;
    height: 6px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    animation: pulse 1.2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    100% { opacity: 0.3; transform: scale(1.6); }
}

/* =========================
   TYPOGRAPHY
========================= */
h1, h2 {
    font-size: 26px !important;
}

h3 {
    font-size: 24px !important;
    font-weight: 700 !important;
}

div[data-testid="stMarkdownContainer"] p {
    font-size: 15px !important;
    line-height: 1.5;
}

.subheader {
    font-size: 24px !important;
    font-weight: 600 !important;
}

.markdown-text {
    font-size: 18px;
}
/* =========================
   CARD SYSTEM
========================= */
.card-anchor {
    display: none;
}

div[data-testid="stVerticalBlock"]:has(.card-anchor) {
    background: linear-gradient(145deg, #0b1a2a, #0f2236);
    padding: 14px;
    border-radius: 12px;

    border: 1px solid rgba(59, 130, 246, 0.2);

    box-shadow:
        0 0 0 1px rgba(59, 130, 246, 0.08),
        0 8px 25px rgba(0, 0, 0, 0.5);

    margin-bottom: 8px;
}

.card-text{
    font-size: 16px;
    }

div[data-testid="stVerticalBlock"] {
    align-items: flex-start !important;
}

/* =========================
   ALERT PANEL
========================= */
.alert-anchor {
    display: none;
}

div[data-testid="stVerticalBlock"]:has(.alert-anchor) {
    background: linear-gradient(145deg, #0b1a2a, #0f2236);
    padding: 14px;
    border-radius: 12px;

    border: 1px solid rgba(239, 68, 68, 0.4);

    box-shadow:
        0 0 20px rgba(239, 68, 68, 0.2);
}

/* ALERT TEXT */
.alert-text {
    font-size: 24px;
}

.alert-title {
    font-size: 18px;
    font-weight: 700;
}

/* =========================
   IDS HEADER (TITLE + FLAG)
========================= */
.ids-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(145deg, #0b1a2a, #0f2236);
    padding: 14px 20px;
    margin-bottom: 8px;

}

/* LEFT TITLE */
.ids-title {
    font-size: 20px;
    font-weight: 700;
    color: #e5e7eb;
}

/* RIGHT FLAG CONTAINER */
.ids-flag-wrapper {
    display: flex;
    align-items: center;
}

/* =========================
   IDS FLAG BADGE (RED ALERT)
========================= */
.ids-badge {
    display: inline-block;
    padding: 5px 12px;

    border-radius: 999px;

    background: linear-gradient(135deg, #ef4444, #b91c1c);
    color: white;

    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;

    border: 1px solid rgba(255, 255, 255, 0.15);

    box-shadow:
        0 0 10px rgba(239, 68, 68, 0.5),
        inset 0 0 6px rgba(255, 255, 255, 0.1);
}

/* OPTIONAL: stronger glow when active */
.ids-badge.active {
    animation: pulse-red 1.2s infinite;
}

@keyframes pulse-red {
    0% { box-shadow: 0 0 10px rgba(239,68,68,0.5); }
    100% { box-shadow: 0 0 20px rgba(239,68,68,0.9); }
}

.normal-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: #16833E;
    border-left: 4px solid #22c55e;

    padding: 10px 14px;
    border-radius: 8px;

    margin: 10px 0;

    font-weight: 600;
}

/* LEFT TEXT */
.normal-bar-left {
    font-size: 16px;
}

/* RIGHT % */
.normal-bar-right {
    font-size: 26px;
    font-weight: 800;
    color: #black;
}


.impedance-error-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: #7f1d1d;
    border-left: 4px solid #ef4444;

    padding: 10px 14px;
    border-radius: 8px;

    margin: 10px 0;

    font-weight: 600;
}

/* LEFT TEXT */
.impedance-error-bar-left {
    font-size: 20px;
}


.impedance-normal-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: #16833E;
    border-left: 4px solid #22c55e;

    padding: 10px 14px;
    border-radius: 8px;

    margin: 10px 0;

    font-weight: 600;
}

/* LEFT TEXT */
.impedance-normal-bar-left {
    font-size: 20px;
}

/* =========================
   CONTROL ROOM ROWS
========================= */

.control-row {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: rgba(15, 23, 42, 0.6);
    border-radius: 10px;

    padding: 10px 14px;
    margin-bottom: 8px;

    border: 1px solid rgba(148, 163, 184, 0.2);
}

.control-left {
    color: #ffffff;
    font-weight: 600;
    font-size: 14px;
}

.control-status {
    color: #e2e8f0;
    font-size: 13px;
}

.control-right {
    color: #94a3b8;
    font-size: 12px;
    font-family: monospace;
}


/* =========================
   MINI BOX (STATE / MODEL)
========================= */
.mini-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.6);
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 8px;

    border: 1px solid rgba(148, 163, 184, 0.2);
}

.mini-label-left {
    font-size: 12px;
    color: #94a3b8;
}

.mini-value-right {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

/* =========================
   CHAIN BOX
========================= */
.chain-box {
    margin-top: 8px;
    padding: 10px;

    border-radius: 8px;
    background: rgba(30, 41, 59, 0.6);

    border-left: 3px solid #3b82f6;

    font-size: 14px;
}


/* =========================
   IDS ALERT BAR (CUSTOM)
========================= */
.alert-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: #7f1d1d;
    border-left: 4px solid #ef4444;

    padding: 10px 14px;
    border-radius: 8px;

    margin: 10px 0;

    font-weight: 600;
}

/* LEFT TEXT */
.alert-bar-left {
    font-size: 16px;
}

/* RIGHT % */
.alert-bar-right {
    font-size: 26px;
    font-weight: 800;
    color: #fecaca;
}

/* FLAG STYLE */
.alert-flag {
    margin-left: 10px;
    padding: 2px 8px;
    border-radius: 6px;
    background: #dc2626;
    color: white;
    font-size: 12px;
    font-weight: 700;
}

/* =========================
   BANNERS
========================= */
.banner {
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    margin-bottom: 10px;
}

.banner-error {
    background: #7f1d1d;
    border-left: 4px solid #ef4444;
}

.banner-warning {
    background: #78350f;
    border-left: 4px solid #f59e0b;
}

.banner-success {
    background: #064e3b;
    border-left: 4px solid #10b981;
}

.banner-info {
    background: #1e3a8a;
    border-left: 4px solid #3b82f6;
}

/* =========================
   METRICS → FORCE HORIZONTAL
========================= */

div[data-testid="stMetric"] {
    display: flex !important;
    justify-content: space-between;
    align-items: center;

    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;

    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* 🔥 THIS IS THE KEY FIX */
div[data-testid="stMetric"] > div {
    display: flex !important;
    width: 100%;
    justify-content: space-between;
    align-items: center;
}

/* label */
div[data-testid="stMetricLabel"] {
    font-size: 24px !important;
    color: #94a3b8 !important;
}

/* value */
div[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
}

/* =========================
   CUSTOM METRIC BOX
========================= */
.metric-box {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;

    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* LEFT LABEL */
.metric-box-left {
    font-size: 24px;
    color: #ffffff;
}

/* RIGHT VALUE */
.metric-box-right {
    font-size: 20px;
    font-weight: 600;
    color: #e2e8f0;
}

/* 🔴 ALERT (NEGATIVE / CRITICAL) */
.metric-box.alert {
    background: rgba(127, 29, 29, 0.4);
    border: 1px solid rgba(239, 68, 68, 0.5);
}

/* 🟡 WARNING */
.metric-box.warning {
    background: rgba(120, 53, 15, 0.4);
    border: 1px solid rgba(245, 158, 11, 0.5);
}

/* =========================
   BUTTONS
========================= */
.stButton > button {
    border-radius: 8px;
    background: #1f2937;
    border: 1px solid #374151;
    color: #e5e7eb;
    font-weight: 600;
    font-size: 19px;
    padding: 6px 8px;
}

.stButton > button:hover {
    background: #374151;
    border: 1px solid #4b5563;
}

/* =========================
   CONTROL ROOM TEXT
========================= */
.status-green { color: #22c55e; }
.status-yellow { color: #f59e0b; }
.status-gray { color: #9ca3af; }

.select_grid{
margin-top: 10px;
    font-size: 16px;
    text-align: center;
}

/* =========================
   EVENT LOG
========================= */
div[data-testid="stDataFrame"] {
    font-size: 13px !important;
    border-radius: 8px;
    overflow: hidden;
}

/* =========================
   SCROLLBAR
========================= */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: rgba(59, 130, 246, 0.3);
    border-radius: 4px;
}

/* =========================
   EVENT LOG SCROLL CONTAINER
========================= */
.event-log-wrapper {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 6px;
    border-radius: 10px;
}

/* smoother scroll */
.event-log-wrapper::-webkit-scrollbar {
    width: 6px;
}
.event-log-wrapper::-webkit-scrollbar-thumb {
    background: rgba(59, 130, 246, 0.4);
    border-radius: 4px;
}

/* =========================
   HOVER EFFECT
========================= */
div[data-testid="stVerticalBlock"]:has(.card-anchor):hover {
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow:
        0 0 0 1px rgba(59, 130, 246, 0.15),
        0 10px 30px rgba(0, 0, 0, 0.6);
}

div[data-testid="stModal"] > div {
    width: 100vw !important;
    height: 100vh !important;

    margin: 0 !important;
    border-radius: 0 !important;
}

/* ========================================
   🔥 FORCE OVERLAY ABOVE STREAMLIT
======================================== */

/* allow overlay to escape layout */
[data-testid="stAppViewContainer"] {
    overflow: visible !important;
}

/* prevent clipping */
.block-container {
    overflow: visible !important;
    position: relative;
    z-index: 0;
}

/* ========================================
   🔥 TRUE FULLSCREEN MODAL
======================================== */
.overlay-bg {
    position: centered;
    inset: 0;
    background: rgba(2, 6, 23, 0.92);
    backdrop-filter: blur(6px);
    z-index: 999999;
}

/* MAIN MODAL */
.overlay-box {
    position: fixed;
    justify-content: center;
    align-items: center;
    width: 100vw;
    height: 100vh;
    inset: 0;

    display: flex;
    flex-direction: column;

    padding: 20px;

    z-index: 1000000;
}

/* HEADER */
.overlay-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 12px 16px;
    margin-bottom: 10px;

    background: linear-gradient(90deg,#0f172a,#1e293b);
    border-radius: 10px;
}

/* 3-COLUMN LAYOUT */
.overlay-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;

    height: 180px;
    margin-bottom: 15px;
}

/* EACH COLUMN */
.overlay-col {
    background: rgba(15,23,42,0.7);
    border-radius: 10px;
    padding: 12px;
}

/* COLORS */
.overlay-col.physical { border-left: 4px solid #3b82f6; }
.overlay-col.ids { border-left: 4px solid #ef4444; }
.overlay-col.user { border-left: 4px solid #f59e0b; }

/* SCROLL CONTENT */
.overlay-content {
    overflow-y: auto;
    flex-grow: 1;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translate(-50%, -60%); }
    to { opacity: 1; transform: translate(-50%, -50%); }
}


/* ========================================
   🔥 STREAMLIT DIALOG FULL WIDTH FIX
======================================== */
/* =========================
   修正 Streamlit Dialog (彈窗) 寬度與定位
========================= */

/* 1. 強制 Dialog 變得更寬 */
div[data-testid="stDialog"] div[role="dialog"] {
    width: 90vw !important;       /* 佔用螢幕 90% 寬度 */
    max-width: 2400px !important;  /* 最大寬度，可根據需求調整 */
    min-width: 1600px !important;   /* 確保不會太窄 */
}

/* 2. 確保 Dialog 內容區塊自動填滿 */
div[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
    width: 100% !important;
}

/* 3. (選配) 讓表格 (Dataframe) 高度固定避免撐開太長 */
div[data-testid="stDialog"] .stDataFrame {
    max-height: 300px;
    overflow-y: auto;
}

/* 4. 修改 Dialog 的背景顏色以符合你的深色主題 */
div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #0b1a2a !important; 
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.7) !important;
}




    </style>
    """