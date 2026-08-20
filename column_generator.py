import pandas as pd
import numpy as np

df = pd.read_csv("cleaned_employee_dataset.csv")

target_date = pd.to_datetime("2026-08-01")

df["Hire_Date"] = pd.to_datetime(df["Hire_Date"])
df["Last_Promotion_Date"] = pd.to_datetime(df["Last_Promotion_Date"])

df["Tenure_Years"] = np.floor((target_date - df["Hire_Date"]).dt.days / 365.25)

df["Never_Promoted"] = df["Last_Promotion_Date"].isna()

reference_date = df["Last_Promotion_Date"].fillna(df["Hire_Date"])
df["Promotion_Waiting_Time"] = np.floor((target_date - reference_date).dt.days / 365.25)

# Overtime Percentage (Handles division by zero perfectly)
total_hours = df["Working_Hours"] + df["Overtime_Hours"]
df["Overtime_Percentage"] = np.where(
    total_hours > 0, df["Overtime_Hours"] / total_hours, 0
)
df["Overtime_Percentage"] = np.floor(df["Overtime_Percentage"] * 100) / 100
# Age Group (Added <20 category for completeness)
bins = [
    18,
    20,
    30,
    40,
    50,
    65,
]  # Adjusted upper limit to 65 for age group categorization
labels = ["<20", "20s", "30s", "40s", "50s+"]
df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

# Total Workload
workload_cols = ["Working_Hours", "Overtime_Hours", "Training_Hours"]
df["Total_Workload"] = df[workload_cols].sum(axis=1)
df.to_csv("final_employee_dataset.csv", index=False)
print("Column generation complete. File saved as final_employee_dataset.csv")
# Group by Department and get the mean
avg_wait = df.groupby("Department")["Promotion_Waiting_Time"].mean()
print(avg_wait)
