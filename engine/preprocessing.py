# ============================================================
# engine/processing.py
# ============================================================

import pandas as pd
import numpy as np
import joblib

# ============================================================
# LOAD FEATURE SCHEMA (CRITICAL)
# ============================================================
FEATURE_COLS = joblib.load("models/feature_columns.pkl")

# ============================================================
# CLEAN LIVE ROW (MAIN FUNCTION)
# ============================================================
def clean_live_row(row_raw, df_reference):
    """
    Convert raw row → clean row aligned with training pipeline
    """

    # -------------------------
    # 1. Ensure Series
    # -------------------------
    if not isinstance(row_raw, pd.Series):
        row_raw = pd.Series(row_raw)

    row = row_raw.copy()

    # -------------------------
    # 2. STRIP COLUMN NAMES
    # -------------------------
    row.index = row.index.str.strip()

    # -------------------------
    # 3. ADD MISSING FEATURES
    # -------------------------
    for col in FEATURE_COLS:
        if col not in row:
            row[col] = 0

    # -------------------------
    # 4. KEEP ONLY TRAINED FEATURES (ORDER MATTERS)
    # -------------------------
    row = row[FEATURE_COLS]

    # -------------------------
    # 5. CONVERT TO NUMERIC
    # -------------------------
    row = row.apply(pd.to_numeric, errors="coerce")

    # -------------------------
    # 6. HANDLE INF VALUES
    # -------------------------
    inf_mask = np.isinf(row)
    row[inf_mask] = np.nan

    # -------------------------
    # 7. ADD IMPEDANCE FLAGS (IMPORTANT)
    # -------------------------
    Z_COLS = ["R1-PA:Z", "R2-PA:Z", "R3-PA:Z", "R4-PA:Z"]

    for z in Z_COLS:
        flag_col = z + "_inf_flag"

        if z in row.index:
            row[flag_col] = int(np.isinf(row[z]))
        else:
            row[flag_col] = 0

    # -------------------------
    # 8. FILL NaN (MATCH TRAINING)
    # -------------------------
    medians = df_reference[FEATURE_COLS].median()
    row = row.fillna(medians)

    # -------------------------
    # 9. OUTLIER CLIPPING (OPTIONAL BUT CONSISTENT)
    # -------------------------
    for col in FEATURE_COLS:

        if "log" in col.lower() or "flag" in col.lower() or col == "marker":
            continue

        Q1 = df_reference[col].quantile(0.25)
        Q3 = df_reference[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        row[col] = np.clip(row[col], lower, upper)

    # -------------------------
    # 10. FINAL TYPE SAFETY
    # -------------------------
    row = row.astype(float)

    return row