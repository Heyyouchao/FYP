import streamlit as st
import pandas as pd
import joblib

# -------------------------
# Load model
# -------------------------
model = joblib.load("models/M1.joblib")
feature_cols = joblib.load("models/feature_columns.pkl")  # 🔥 NEW

# -------------------------
# Load data
# -------------------------
df = pd.read_csv("data/merged/multi_class_dataset_clean_FULL.csv")
df.columns = df.columns.str.strip()

# -------------------------
# Title
# -------------------------
st.title("⚡ Simple IDS Dashboard")

# -------------------------
# Select scenario
# -------------------------
scenario = st.selectbox(
    "Select Scenario",
    sorted(df["marker"].unique())
)

df_s = df[df["marker"] == scenario].reset_index(drop=True)

# -------------------------
# Select row
# -------------------------
idx = st.slider("Row", 0, len(df_s)-1)

row = df_s.iloc[idx].copy()

# -------------------------
# Separate label
# -------------------------
y_true = row["marker"]
row = row.drop("marker")

# 🔥 CRITICAL FIX
row = row[feature_cols]

# -------------------------
# Predict
# -------------------------
pred = model.predict([row])[0]
prob = model.predict_proba([row])[0].max()

# -------------------------
# Display
# -------------------------
st.subheader("Prediction")

st.write(f"Prediction: {pred}")
st.write(f"Confidence: {prob:.2%}")
st.write(f"True label: {y_true}")