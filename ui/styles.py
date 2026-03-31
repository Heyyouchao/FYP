def load_css():
    return """
    <style>

    /* =========================
       GLOBAL BACKGROUND
    ========================= */
    body {
        background: radial-gradient(circle at top, #0b1a2a, #020617);
    }

    .header-container {
        position: relative;
        background: linear-gradient(90deg, #0f172a, #1e293b);
        padding: 18px 20px;
        border-radius: 12px;
        margin-bottom: 5px;
    }

    .header-title-center {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 54px;
        font-weight: 700;
        color: #e2e8f0;
    }

    /* LEFT SIDE (mode + scenario) */
    .header-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* RIGHT SIDE (status) */
    .header-right {
        position: absolute;
        right: 20px;
        top: 14px;
    }
    /* MODE ACTIVE */
    .mode-active {
        padding: 6px 12px;
        border-radius: 8px;
        background: #3b82f6;
        color: white;
        text-align: center;
        font-weight: 600;
    }

    .mode-active.live {
        background: #ef4444;
    }

    /* LIVE LABEL */
    .live-label {
        font-size: 13px;
        color: #ef4444;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    /* STATUS */
    .status {
        font-size: 13px;
        font-weight: 600;
        text-align: right;
    }

    .status.running {
        color: #22c55e;
    }

    .status.paused {
        color: #eab308;
    }

    /* BLINKING EFFECT */
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

    .live-label {
        font-size: 12px;
        color: #ef4444;
        font-weight: 600;
    }

    .insight-box {
        font-size: 13px;
        font-weight: 600;
        text-align: right;
    }
    /* =========================
       TITLE
    ========================= */
    .title {
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        color: #e5e7eb;
        margin-bottom: 15px;
    }

    /* =========================
       CARD SYSTEM (MAIN)
    ========================= */
    .card-anchor {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.card-anchor) {
        background: linear-gradient(145deg, #0b1a2a, #0f2236);
        padding: 16px;
        border-radius: 14px;

        border: 1px solid rgba(59, 130, 246, 0.2);

        box-shadow:
            0 0 0 1px rgba(59, 130, 246, 0.08),
            0 10px 30px rgba(0, 0, 0, 0.5);

        margin-bottom: 10px;

        /* 🔥 FIX: REMOVE EMPTY SPACE */
        height: auto !important;
        min-height: unset !important;
        padding-bottom: 12px !important;
    }

    /* 🔥 PREVENT STRETCHING */
    div[data-testid="stVerticalBlock"] {
        align-items: flex-start !important;
    }

    /* =========================
       ALERT CARD (RIGHT PANEL)
    ========================= */
    .alert-anchor {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.alert-anchor) {
        background: linear-gradient(145deg, #0b1a2a, #0f2236);
        padding: 16px;
        border-radius: 14px;

        border: 1px solid rgba(239, 68, 68, 0.3);

        box-shadow:
            0 0 25px rgba(239, 68, 68, 0.15);
    }

    /* =========================
       BANNER
    ========================= */
    .banner {
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .banner-error {
        background: #7f1d1d;
        border-left: 5px solid #ef4444;
    }

    .banner-warning {
        background: #78350f;
        border-left: 5px solid #f59e0b;
    }

    .banner-success {
        background: #064e3b;
        border-left: 5px solid #10b981;
    }

    .banner-info {
        background: #1e3a8a;
        border-left: 5px solid #3b82f6;
    }

    /* =========================
       METRICS
    ========================= */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(59, 130, 246, 0.1);
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
    }

    .stButton > button:hover {
        background: #374151;
        border: 1px solid #4b5563;
    }

    /* =========================
       CONTROL ROOM TEXT
    ========================= */
    .status-green {
        color: #22c55e;
    }

    .status-yellow {
        color: #f59e0b;
    }

    .status-gray {
        color: #9ca3af;
    }

    /* =========================
       EVENT LOG TABLE
    ========================= */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* =========================
       SCROLLBAR
    ========================= */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.5);
    }

    /* =========================
       BOTTOM CONTROLS
    ========================= */
    .bottom-controls {
        position: sticky;
        bottom: 0;
        background: #020617;
        padding: 12px;
        border-top: 1px solid #1e293b;
        border-radius: 12px 12px 0 0;
    }

    /* =========================
       OPTIONAL HOVER GLOW
    ========================= */
    div[data-testid="stVerticalBlock"]:has(.card-anchor):hover {
        border: 1px solid rgba(59, 130, 246, 0.35);
        box-shadow:
            0 0 0 1px rgba(59, 130, 246, 0.15),
            0 15px 40px rgba(0, 0, 0, 0.6);
    }

    </style>
    """