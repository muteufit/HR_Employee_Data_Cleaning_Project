import pandas as pd

df = pd.read_csv("employee_dataset.csv")

# --- 1. Standardise categoricals ---
df["Department"] = df["Department"].str.strip().str.lower()
df["Gender"] = df["Gender"].str.strip().str.lower()
df["Resigned"] = df["Resigned"].str.strip().str.lower()

dept_map = {
    "fin": "finance",
    "support": "customer support",
    "ops": "operations",
    "mktg": "marketing",
    "eng": "engineering",
}
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
df["Salary"] = pd.to_numeric(
    df["Salary"].astype(str).str.replace(r"[\$,]", "", regex=True), errors="coerce"
)
df.loc[(df["Age"] < 18) | (df["Age"] > 65), "Age"] = None
df.loc[
    (df["Overtime_Hours"] < 0) | (df["Overtime_Hours"].isnull()), "Overtime_Hours"
] = 0
df.loc[(df["Absence_Days"] > 365), "Absence_Days"] = None
df.loc[(df["Working_Hours"] < 0), "Working_Hours"] = None
df.loc[(df["Training_Hours"] < 0), "Training_Hours"] = None

# fix date columns
df["Hire_Date"] = pd.to_datetime(df["Hire_Date"])
df["Last_Promotion_Date"] = pd.to_datetime(df["Last_Promotion_Date"])


# --- 3. Impute missing numeric values (median) ---
df["Satisfaction_Score"] = df.groupby("Department")["Satisfaction_Score"].transform(
    lambda x: x.fillna(x.median())
)
df["Performance_Score"] = df.groupby("Department")["Performance_Score"].transform(
    lambda x: x.fillna(x.median())
)
df["Training_Hours"] = df.groupby("Department")["Training_Hours"].transform(
    lambda x: x.fillna(x.median())
)
df["Working_Hours"] = df.groupby("Department")["Working_Hours"].transform(
    lambda x: x.fillna(x.median())
)
df["Absence_Days"] = df.groupby("Department")["Absence_Days"].transform(
    lambda x: x.fillna(x.median())
)


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
        max_num = max(
            int(x.replace("EMP", "")) for x in df["Employee_ID"] if x.startswith("EMP")
        )
        for _, row in rows.iloc[1:].iterrows():
            max_num += 1
            row["Employee_ID"] = f"EMP{max_num}"
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

assert df["Employee_ID"].is_unique, "Duplicate IDs still exist!"


# --- 5. Save ---
df.to_csv("final_cleaned_employee_dataset.csv", index=False)
print("Cleaning complete. File saved as final_cleaned_employee_dataset.csv")
