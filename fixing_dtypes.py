import pandas as pd

df = pd.read_csv("final_cleaned_employee_dataset.csv")

# Fill empty Resigned with 'no'
df["Resigned"] = df["Resigned"].fillna("no")

# Strip whitespace from all string columns
# Fix the select_dtypes warning by including "string"
str_cols = df.select_dtypes(include=["object", "string"]).columns
for col in str_cols:
    df[col] = df[col].str.strip()

# ----------------------------
# 2. Fix numeric anomalies
# ----------------------------
# Convert Salary to numeric – use raw string for regex
df["Salary"] = df["Salary"].astype(str).str.replace(r"[\$,]", "", regex=True)
df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

# Age: negative → NaN, >100 → NaN
df.loc[df["Age"] < 0, "Age"] = None
df.loc[df["Age"] > 100, "Age"] = None

# Overtime_Hours: negative → NaN
df.loc[df["Overtime_Hours"] < 0, "Overtime_Hours"] = None

# Absence_Days: >365 → NaN
df.loc[df["Absence_Days"] > 365, "Absence_Days"] = None

# ----------------------------
# 3. Impute missing numeric values (optional)
# ----------------------------
numeric_cols = [
    "Performance_Score",
    "Satisfaction_Score",
    "Training_Hours",
    "Remote_Work_Days",
    "Working_Hours",
    "Overtime_Hours",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# ----------------------------
# 4. Handle duplicate Employee_ID
# ----------------------------
df = df.drop_duplicates()

dup_ids = df[df.duplicated("Employee_ID", keep=False)]["Employee_ID"].unique()
for emp_id in dup_ids:
    rows = df[df["Employee_ID"] == emp_id]
    if rows["Name"].nunique() == 1:
        keep_row = rows.loc[rows.isnull().sum(axis=1).idxmin()]
        df = df[df["Employee_ID"] != emp_id]
        df = pd.concat([df, pd.DataFrame([keep_row])], ignore_index=True)
    else:
        keep_row = rows.iloc[0]
        df = df[df["Employee_ID"] != emp_id]
        df = pd.concat([df, pd.DataFrame([keep_row])], ignore_index=True)
        max_num = max(
            [
                int(x.replace("EMP", ""))
                for x in df["Employee_ID"]
                if x.startswith("EMP")
            ]
        )
        for _, row in rows.iloc[1:].iterrows():
            max_num += 1
            row["Employee_ID"] = f"EMP{max_num}"
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

assert df["Employee_ID"].is_unique, "Duplicate IDs still exist!"

# ----------------------------
# 5. Save final cleaned file
# ----------------------------
df.to_csv("fully_final_cleaned_employee_dataset.csv", index=False)
print("Cleaning complete. File saved.")
