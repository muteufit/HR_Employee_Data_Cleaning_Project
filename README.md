# HR Employee Data Cleaning Project

This repository contains a set of Python scripts to clean and prepare the `employee_dataset.csv` file for HR analytics. The raw data has inconsistencies in categorical values, missing entries, duplicate records, and erroneous numeric fields. The scripts standardise, impute, and deduplicate the data to produce a reliable dataset.

## Files in this repository

| File                          | Description |
|-------------------------------|-------------|
| `employee_dataset.csv`        | Raw input file (provided). |
| `cleaning.py`                 | Basic cleaning: standardises Department, Gender, and Resigned columns to lowercase and maps abbreviations (e.g., `fin` → `finance`, `M` → `male`, `Y` → `yes`). Saves output as `fully_cleaned_employee_dataset.csv`. |
| `fixing_IDs.py`               | Handles duplicate `Employee_ID` entries by removing exact duplicate rows and assigning new IDs to conflicting records (different employees sharing the same ID). Reads `fully_cleaned_employee_dataset.csv` and writes `final_cleaned_employee_dataset.csv`. |
| `fixing_dtypes.py`            | Comprehensive cleaning: converts salary to numeric, fixes invalid ages, negative overtime, extreme absence days, imputes missing numeric values, and resolves duplicate IDs. Reads `final_cleaned_employee_dataset.csv` and outputs `fully_final_cleaned_employee_dataset.csv`. |
| (optional) `clean_employee_data.py` | **Recommended:** a single script that combines all steps (see below). |

## Data issues addressed

- **Inconsistent categorical values** – Department names (e.g., `FIN`, `Eng`), Gender (`M`, `F`), Resigned (`Y`, `N`, `1`, `0`).
- **Salary stored as string** with `$` and commas (e.g., `"$72,800"`).
- **Invalid ages** – negative values (e.g., `-5`) and unrealistic ages > 100.
- **Negative overtime hours** – e.g., `-5.0`.
- **Extreme absence days** – values over 365 (e.g., `400`) treated as errors.
- **Missing values** in numeric columns (`Performance_Score`, `Satisfaction_Score`, `Training_Hours`, etc.) – imputed with median.
- **Duplicate Employee_IDs** – exact duplicate rows removed; different employees with the same ID are assigned new unique IDs.

## How to use

### Option 1: Run the separate scripts in order

1. **Clean categoricals**  
   `python cleaning.py`  
   → produces `fully_cleaned_employee_dataset.csv`

2. **Fix duplicate IDs**  
   `python fixing_IDs.py`  
   → produces `final_cleaned_employee_dataset.csv`

3. **Fix data types and numeric anomalies**  
   `python fixing_dtypes.py`  
   → produces `fully_final_cleaned_employee_dataset.csv`

### Option 2: Use the unified script (recommended)

Create a single file (e.g., `clean_employee_data.py`) with the following content – it combines all steps and reads the original `employee_dataset.csv` directly.

```python
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
