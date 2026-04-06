# ============================================================
# engine/disturbance.py
# ============================================================

import numpy as np
import pandas as pd
import joblib

# ============================================================
# LOAD BASELINE MODEL (ONCE)
# ============================================================
model = joblib.load("models/physical_baseline.pkl")

scaler = model["scaler"]
relay_groups = model["relay_groups"]
baseline_mean = model["baseline_mean"]
baseline_std  = model["baseline_std"]
green_thr = model["green_thr"]

# 🔥 IMPORTANT: build feature list ONCE
feature_cols = model["scaler"].feature_names_in_.tolist()

# ============================================================
# COMPUTE RELAY SCORES (WITH SCALING)
# ============================================================
def compute_relay_scores(row):

    # 👉 ensure DataFrame format (for sklearn)
    if isinstance(row, pd.Series):
        row_df = row.reindex(feature_cols).to_frame().T
    else:
        row_df = row[feature_cols]

    # 👉 apply SAME scaler from baseline
    row_scaled_vals = scaler.transform(row_df)[0]
    row_scaled = pd.Series(row_scaled_vals, index=feature_cols)

    scores = {}

    for r, cols in relay_groups.items():

        z = (row_scaled[cols] - baseline_mean[cols]) / baseline_std[cols]

        abs_part = np.abs(z)
        dir_part = np.zeros(len(cols))

        for i, c in enumerate(cols):

            if ":V" in c or ":VH" in c:
                dir_part[i] = max(-z.iloc[i], 0)

            elif ":I" in c or ":IH" in c:
                dir_part[i] = max(z.iloc[i], 0)

            elif ":Z" in c or ":ZH" in c:
                dir_part[i] = max(-z.iloc[i], 0)

            else:
                dir_part[i] = abs_part.iloc[i]

        adj = abs_part + 0.3 * dir_part
        scores[r] = float(np.mean(adj))

    return scores


# ============================================================
# CLASSIFICATION
# ============================================================
def classify_relay_scores(row):

    # -------------------------
    # Compute base scores
    # -------------------------
    if isinstance(row, pd.Series):
        row_df = row.reindex(feature_cols).to_frame().T
    else:
        row_df = row[feature_cols]

    row_scaled_vals = scaler.transform(row_df)[0]
    row_scaled = pd.Series(row_scaled_vals, index=feature_cols)

    scores = {}
    norm_scores = {}
    state = {}
    top_features = {}   # 🔥 NEW

    # -------------------------
    # Per relay
    # -------------------------
    for r, cols in relay_groups.items():

        z = (row_scaled[cols] - baseline_mean[cols]) / baseline_std[cols]

        abs_part = np.abs(z)
        dir_part = np.zeros(len(cols))

        for i, c in enumerate(cols):

            if ":V" in c or ":VH" in c:
                dir_part[i] = max(-z.iloc[i], 0)

            elif ":I" in c or ":IH" in c:
                dir_part[i] = max(z.iloc[i], 0)

            elif ":Z" in c or ":ZH" in c:
                dir_part[i] = max(-z.iloc[i], 0)

            else:
                dir_part[i] = abs_part.iloc[i]

        adj = abs_part + 0.3 * dir_part

        # -------------------------
        # Score
        # -------------------------
        score = float(np.mean(adj))
        scores[r] = score

        # -------------------------
        # Normalised score
        # -------------------------
        norm = score / green_thr[r]
        norm_scores[r] = norm

        # -------------------------
        # State
        # -------------------------
        if norm <= 1.0:
            state[r] = "GREEN"
        elif norm <= 1.4:
            state[r] = "YELLOW"
        else:
            state[r] = "RED"

        # -------------------------
        # 🔥 TOP 3 FEATURES
        # -------------------------
        sorted_idx = np.argsort(adj.values)[::-1][:3]
        top_features[r] = [cols[i] for i in sorted_idx]

    return scores, norm_scores, state, top_features