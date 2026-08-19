import pandas as pd

df = pd.read_csv("employee_dataset.csv")

# --- 1. Standardise categoricals ---
df["Department"] = df["Department"].str.strip().str.lower()
df["Gender"] = df["Gender"].str.strip().str.lower()
df["Resigned"] = df["Resigned"].str.strip().str.lower()

dept_map = {"fin": "finance", "support": "customer support", "ops": "operations",
            "mktg": "marketing", "eng": "engineering"}
gender_map = {"m": "male", "f": "female"}
resigned_map = {"y": "yes", "n": "no", "0": "no", "1": "yes"}

df["Department"] = df["Department"].replace(dept_map)
df["Gender"] = df["Gender"].replace(gender_map)
df["Resigned"] = df["Resigned"].replace(resigned_map)
df["Resigned"] = df["Resigned"].fillna("no")

# Strip all string columns
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.strip()

# --- 2. Fix numeric anomalies ---
df["Salary"] = pd.to_numeric(df["Salary"].astype(str).str.replace(r"[\$,]", "", regex=True), errors="coerce")
df.loc[df["Age"] < 0, "Age"] = None
df.loc[df["Age"] > 100, "Age"] = None
df.loc[df["Overtime_Hours"] < 0, "Overtime_Hours"] = None
df.loc[df["Absence_Days"] > 365, "Absence_Days"] = None

# --- 3. Impute missing numeric values (median) ---
numeric_cols = ["Performance_Score", "Satisfaction_Score", "Training_Hours",
                "Remote_Work_Days", "Working_Hours", "Overtime_Hours"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# --- 4. Handle duplicate Employee_ID ---
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
        max_num = max(int(x.replace("EMP", "")) for x in df["Employee_ID"] if x.startswith("EMP"))
        for _, row in rows.iloc[1:].iterrows():
            max_num += 1
            row["Employee_ID"] = f"EMP{max_num}"
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

assert df["Employee_ID"].is_unique, "Duplicate IDs still exist!"

# --- 5. Save ---
df.to_csv("final_cleaned_employee_dataset.csv", index=False)
print("Cleaning complete. File saved as final_cleaned_employee_dataset.csv")
