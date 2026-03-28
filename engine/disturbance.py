import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

VALID_SUFFIXES = (":V", ":I", ":VH", ":IH", ":Z", ":ZH", ":F", ":DF")
pmu_suffixes = [":VH",":IH",":V",":I",":F",":DF"]

# ------------------------------------------------------------
# BUILD FEATURE GROUPS
# ------------------------------------------------------------
def build_feature_groups(df):

    relay_groups = {
        r: [c for c in df.columns if c.startswith(r) and c.endswith(VALID_SUFFIXES)]
        for r in ["R1","R2","R3","R4"]
    }

    pmu_cols = [
        c for c in df.columns
        if any(c.endswith(s) for s in pmu_suffixes)
    ]

    return relay_groups, pmu_cols


# ------------------------------------------------------------
# STANDARDIZE
# ------------------------------------------------------------
def standardize(df, relay_groups, pmu_cols):

    scaler = StandardScaler()

    all_cols = sum(relay_groups.values(), []) + pmu_cols

    df_scaled = df.copy()
    df_scaled[all_cols] = scaler.fit_transform(df[all_cols])

    return df_scaled


# ------------------------------------------------------------
# BASELINE
# ------------------------------------------------------------
def compute_baseline(df_scaled, relay_groups, pmu_cols, normal_marker=41):

    relay_mean = df_scaled.groupby("marker")[sum(relay_groups.values(), [])].mean()
    pmu_mean = df_scaled.groupby("marker")[pmu_cols].mean()

    relay_baseline = relay_mean.loc[normal_marker]
    pmu_baseline = pmu_mean.loc[normal_marker]

    return relay_baseline, pmu_baseline


# ------------------------------------------------------------
# REAL-TIME DISTURBANCE
# ------------------------------------------------------------
def compute_row_disturbance(row, relay_groups, relay_baseline):

    relay_scores = {}

    for r, cols in relay_groups.items():
        diff = np.abs(row[cols] - relay_baseline[cols])
        relay_scores[r] = diff.mean()

    return relay_scores