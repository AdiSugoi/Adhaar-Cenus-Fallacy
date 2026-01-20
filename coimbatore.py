import pandas as pd
import numpy as np

# 1. LOAD CSV FILES

demo = pd.read_csv("coimbatore_datasets/demographic.csv")
enroll = pd.read_csv("coimbatore_datasets/Monthly_enrollment.csv")
bio = pd.read_csv("coimbatore_datasets/biometric.csv")

# 2. STANDARDIZE COLUMN NAMES

demo = demo.rename(columns={
    "demo_age_5_17": "age_5_17",
    "demo_age_17_": "age_17_plus"
})

enroll = enroll.rename(columns={
    "age_18_greater": "age_17_plus"
})

bio = bio.rename(columns={
    "bio_age_5_17": "age_5_17",
    "bio_age_17_": "age_17_plus"
})

# 3. FIX DATE TYPES
for df in [demo, enroll, bio]:
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)

# 4. AGGREGATE DATA 
group_cols = ["date", "state", "district", "pincode"]
demo_agg = demo.groupby(group_cols, as_index=False).sum()
enroll_agg = enroll.groupby(group_cols, as_index=False).sum()
bio_agg = bio.groupby(group_cols, as_index=False).sum()

# 5. MERGE DATASETS
merged = demo_agg.merge(
    enroll_agg,
    on=group_cols,
    how="left",
    suffixes=("_demo", "_enroll")
)

merged = merged.merge(
    bio_agg,
    on=group_cols,
    how="left",
    suffixes=("", "_bio")
)

merged = merged.fillna(0)

# CREATE CORE METRICS

# Enrollment penetration
merged["enroll_rate_5_17"] = np.where(
    merged["age_5_17_demo"] > 0,
    merged["age_5_17_enroll"] / merged["age_5_17_demo"],
    0
)

merged["enroll_rate_17_plus"] = np.where(
    merged["age_17_plus_demo"] > 0,
    merged["age_17_plus_enroll"] / merged["age_17_plus_demo"],
    0
)

# Biometric completion
merged["bio_completion_5_17"] = np.where(
    merged["age_5_17_enroll"] > 0,
    merged["age_5_17"] / merged["age_5_17_enroll"],
    0
)

merged["bio_completion_17_plus"] = np.where(
    merged["age_17_plus_enroll"] > 0,
    merged["age_17_plus"] / merged["age_17_plus_enroll"],
    0
)

# FLAG ANOMALIES

merged["low_enrollment_flag"] = merged["enroll_rate_5_17"] < 0.05
merged["biometric_gap_flag"] = merged["bio_completion_5_17"] < 0.6

# PRIORITY SCORE (DECISION READY)

merged["priority_score"] = (
    (1 - merged["enroll_rate_5_17"]) * 0.6 +
    (1 - merged["bio_completion_5_17"]) * 0.4
)

# OUTPUT RESULTS

# Full analytical output
merged.to_csv("aadhaar_analysis_output.csv", index=False)

# high-risk pincodes
top_risk = merged.sort_values("priority_score", ascending=False).head(10)
top_risk.to_csv("aadhaar_high_risk_pincodes.csv", index=False)

print("Analysis complete.")
print("Files generated:")
print("- aadhaar_analysis_output.csv")
print("- aadhaar_high_risk_pincodes.csv")
