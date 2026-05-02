import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
df.columns = df.columns.str.strip()

print("✅ Dataset loaded:", df.shape)

# ============================================================
# FEATURE GROUPS
# ============================================================
VALID_SUFFIXES = (":V", ":I", ":VH", ":IH", ":Z", ":ZH", ":F", ":DF")

relay_groups = {
    r: [c for c in df.columns if c.startswith(r) and c.endswith(VALID_SUFFIXES)]
    for r in ["R1", "R2", "R3", "R4"]
}

all_cols = list(set(sum(relay_groups.values(), [])))

# ============================================================
# SCALE
# ============================================================
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[all_cols] = scaler.fit_transform(df[all_cols])

print("✅ Scaling complete")

# ============================================================
# BASELINE (marker = 41)
# ============================================================
baseline_rows = df_scaled[df["marker"] == 41].reset_index(drop=True)

baseline_mean = baseline_rows[all_cols].mean()
baseline_std  = baseline_rows[all_cols].std().replace(0, 1e-6)

print("✅ Baseline computed")

# ============================================================
# SCORE FUNCTION (SAME AS YOUR DEBUG)
# ============================================================
def compute_row_score(row):

    scores = {}

    for r, cols in relay_groups.items():

        z = (row[cols] - baseline_mean[cols]) / baseline_std[cols]

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
# BASELINE DISTRIBUTION
# ============================================================
baseline_scores = baseline_rows.apply(
    lambda row: compute_row_score(row), axis=1
)

baseline_df = pd.DataFrame(list(baseline_scores))

# ============================================================
# CLEAN BASELINE (REMOVE OUTLIERS)
# ============================================================
row_mean = baseline_df.mean(axis=1)
clean_mask = row_mean < row_mean.quantile(0.95)

baseline_clean = baseline_df[clean_mask]

print("✅ Clean baseline size:", baseline_clean.shape)

# ============================================================
# THRESHOLDS
# ============================================================
green_thr  = baseline_clean.quantile(0.95)
yellow_thr = green_thr * 1.4

# ============================================================
# DISTRIBUTION (FOR EXPLAINABILITY)
# ============================================================
distribution = {}

for r in ["R1","R2","R3","R4"]:
    vals = baseline_df[r]
    distribution[r] = {
        "mean": float(vals.mean()),
        "p95": float(vals.quantile(0.95)),
        "p99": float(vals.quantile(0.99)),
        "max": float(vals.max())
    }

# ============================================================
# SAVE MODEL
# ============================================================
model = {
    "scaler": scaler,
    "relay_groups": relay_groups,

    "baseline_mean": baseline_mean,
    "baseline_std": baseline_std,

    "green_thr": green_thr,
    "yellow_thr": yellow_thr,

    "distribution": distribution,
    "clean_size": int(len(baseline_clean)),

    "version": "v1_physical"
}

joblib.dump(model, "models/physical_baseline.pkl")

print("\n✅ Baseline model saved to models/physical_baseline.pkl")

# ============================================================
# BASELINE STATISTICS TABLE (FOR FIGURE B.10)
# ============================================================

# Create summary table
baseline_stats = baseline_rows[all_cols].describe().T

# Optional: select top features to keep it readable
baseline_stats = baseline_stats[["mean", "std", "min", "max"]]
baseline_stats = baseline_stats.head(20)  # keep first 20 features only

# ============================================================
# SAVE AS IMAGE
# ============================================================

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

table = ax.table(
    cellText=baseline_stats.round(3).values,
    colLabels=baseline_stats.columns,
    rowLabels=baseline_stats.index,
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(8)

plt.savefig("baseline_stats.png", bbox_inches='tight')
plt.close()

print("✅ Baseline statistics image saved as baseline_stats.png")