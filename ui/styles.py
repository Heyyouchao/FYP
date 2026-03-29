def load_css():
    return """
    <style>

    /* =========================
       GLOBAL
    ========================= */
    body {
        background-color: #0f172a;
    }

    /* =========================
    Title
    ========================= */
    .title {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 20px;
    }

    /* =========================
       BANNER
    ========================= */
    .banner {
        padding: 14px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .banner-error {
        background: #7f1d1d;
        border-left: 6px solid #ef4444;
    }

    .banner-warning {
        background: #78350f;
        border-left: 6px solid #f59e0b;
    }

    .banner-success {
        background: #064e3b;
        border-left: 6px solid #10b981;
    }

    .banner-info {
        background: #1e3a8a;
        border-left: 6px solid #3b82f6;
    }

    /* =========================
        BOTTOM CONTROLS (LEFT PANEL)
    ========================= */
    .bottom-controls {
        position: sticky;
        bottom: 0;
        background: #0f172a;
        padding: 12px;
        border-top: 1px solid #374151;
        border-radius: 12px 12px 0 0;
        z-index: 999;
    }

    /* optional: make buttons full width */
    .bottom-controls .stButton > button {
        width: 100%;
        border-radius: 8px;
    }

    /* =========================
    STREAMLIT CARD FIX
    ========================= */

    /* hidden anchor */
    .card-anchor {
        display: none;
    }

    /* turn Streamlit container INTO a card */
    div[data-testid="stVerticalBlock"]:has(.card-anchor) {
        background: #111827;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 12px;
    }

    /* alert card variant */
    .alert-anchor {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.alert-anchor) {
        background: #111827;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #374151;
        border-left: 4px solid #374151;
    }

    /* =========================
       METRICS
    ========================= */
    .metric-label {
        font-size: 13px;
        color: #9ca3af;
    }

    .metric-value {
        font-size: 22px;
        font-weight: bold;
    }

    /* =========================
       BUTTONS
    ========================= */
    .btn {
        border-radius: 8px;
        padding: 6px 12px;
        border: 1px solid #374151;
        background: #1f2937;
        color: white;
        text-align: center;
        cursor: pointer;
    }

    .btn:hover {
        background: #374151;
    }

    /* =========================
       ALERT CARD (RIGHT PANEL)
    ========================= */
    .alert-card {
        background: #111827;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #374151;
    }

    .alert-error {
        background: #7f1d1d;
        padding: 8px;
        border-radius: 8px;
    }

    .alert-success {
        background: #064e3b;
        padding: 8px;
        border-radius: 8px;
    }

    /* =========================
       FACTORS LIST
    ========================= */
    .factor {
        margin-bottom: 6px;
    }

    </style>
    """