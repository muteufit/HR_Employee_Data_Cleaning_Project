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
never_promoted_count = df[df["Never_Promoted"]].groupby("Department").size()
# print(avg_wait)
# print(never_promoted_count)
cs = df[df["Department"] == "customer support"]["Promotion_Waiting_Time"]
# print(cs.std())
# print(cs.mean())
never_promoted_rate = df.groupby("Department")["Hire_Date"].mean()  # * 100
# print(never_promoted_rate.sort_values(ascending=False))

summary = df.groupby("Department").agg(
    avg_salary=("Salary", "mean"),
    avg_satisfaction=("Satisfaction_Score", "mean"),
    avg_performance=("Performance_Score", "mean"),
    employee_count=("Employee_ID", "count"),  # Counts non-null Employee_IDs per dept
)
# print(summary)

EMP1076 = df[df["Employee_ID"] == "EMP1076"]

print("Tenure_Years: " + str(EMP1076["Tenure_Years"].iloc[0]))
print("Years_Experience: " + str(EMP1076["Years_Experience"].iloc[0]))
print("Performance_Score: " + str(EMP1076["Performance_Score"].iloc[0]))
print("Working_Hours: " + str(EMP1076["Working_Hours"].iloc[0]))
print("Overtime_Hours: " + str(EMP1076["Overtime_Hours"].iloc[0]))
print("Projects_Completed: " + str(EMP1076["Projects_Completed"].iloc[0]))
print("Remote_Work_Days: " + str(EMP1076["Remote_Work_Days"].iloc[0]))

customer_support_employees_without_EMP1076 = df[
    (df["Department"] == "customer support") & (df["Employee_ID"] != "EMP1076")
]

print(
    "Customer Support - Tenure_Years: "
    + str(customer_support_employees_without_EMP1076["Tenure_Years"].mean())
)
print(
    "Customer Support - Years_Experience: "
    + str(customer_support_employees_without_EMP1076["Years_Experience"].mean())
)
print(
    "Customer Support - Performance_Score: "
    + str(customer_support_employees_without_EMP1076["Performance_Score"].mean())
)
print(
    "Customer Support - Working_Hours: "
    + str(customer_support_employees_without_EMP1076["Working_Hours"].mean())
)
print(
    "Customer Support - Overtime_Hours: "
    + str(customer_support_employees_without_EMP1076["Overtime_Hours"].mean())
)
print(
    "Customer Support - Projects_Completed: "
    + str(customer_support_employees_without_EMP1076["Projects_Completed"].mean())
)
print(
    "Customer Support - Remote_Work_Days: "
    + str(customer_support_employees_without_EMP1076["Remote_Work_Days"].mean())
)
print(
    "Customer Support - Average Salary: "
    + str(customer_support_employees_without_EMP1076["Salary"].mean())
)
