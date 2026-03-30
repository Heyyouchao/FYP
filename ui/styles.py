def load_css():
    return """
    <style>

    .home-card {
        padding: 30px 25px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.2);
        background-color: rgba(128,128,128,0.05);
        text-align: center;
    }
    /* =========================
       GLOBAL
    ========================== */
    .title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* =========================
       HEADER BAR
    ========================== */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;

        padding: 14px 20px;
        margin-bottom: 12px;

        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.2);

        background-color: rgba(128,128,128,0.05);
    }

    /* LEFT (MODE) */
    .header-left {
        font-size: 13px;
        font-weight: 600;
    }

    .header-left.live {
        color: #ff4d4d;
    }

    /* CENTER */
    .header-center {
        font-size: 16px;
        font-weight: 700;
        text-align: center;
        flex-grow: 1;
    }

    /* RIGHT */
    .header-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* STATUS */
    .status {
        font-size: 13px;
        opacity: 0.8;
    }

    /* =========================
       🚩 FLAG
    ========================== */
    .flag {
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;

        background-color: rgba(255, 0, 0, 0.1);
        color: #ff4d4d;
        border: 1px solid rgba(255, 0, 0, 0.3);
    }

    /* =========================
       🧠 INSIGHT
    ========================== */
    .insight {
        font-size: 12px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
    }

    /* ATTACK */
    .insight.attack {
        color: #ff4d4d;
        background: rgba(255, 0, 0, 0.08);
        border: 1px solid rgba(255, 0, 0, 0.3);
    }

    /* DISTURBANCE */
    .insight.disturbance {
        color: #f59e0b;
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* NORMAL */
    .insight.normal {
        color: #22c55e;
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    /* =========================
       CARDS / PANELS
    ========================== */
    .card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;

        border: 1px solid rgba(128,128,128,0.15);
        background-color: rgba(128,128,128,0.04);
    }

    .card-anchor {
        margin-bottom: 10px;
    }

    .left-panel {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    /* =========================
       MAIN CONTENT
    ========================== */
    .main-content {
        padding-top: 5px;
    }

    /* =========================
       BUTTONS
    ========================== */
    button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* =========================
       METRICS
    ========================== */
    div[data-testid="stMetric"] {
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.15);
        background-color: rgba(128,128,128,0.05);
    }

    /* =========================
       TABLE
    ========================== */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* =========================
       SCROLLBAR
    ========================== */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(128,128,128,0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(128,128,128,0.5);
    }

    </style>
    """