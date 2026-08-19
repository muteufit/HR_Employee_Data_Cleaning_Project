import pandas as pd

# Load the data
df = pd.read_csv("fully_cleaned_employee_dataset.csv")

# 1. Drop rows that are exact duplicates (all columns identical)
df = df.drop_duplicates()

# 2. Handle duplicate Employee_IDs
dup_ids = df[df.duplicated("Employee_ID", keep=False)]["Employee_ID"].unique()

for emp_id in dup_ids:
    rows = df[df["Employee_ID"] == emp_id]

    if rows["Name"].nunique() == 1:
        # Same person – keep the row with the fewest missing values
        keep_row = rows.loc[rows.isnull().sum(axis=1).idxmin()]
        df = df[df["Employee_ID"] != emp_id]
        df = pd.concat([df, pd.DataFrame([keep_row])], ignore_index=True)
    else:
        # Different people – keep the first row, assign new IDs to the rest
        keep_row = rows.iloc[0]
        df = df[df["Employee_ID"] != emp_id]
        df = pd.concat([df, pd.DataFrame([keep_row])], ignore_index=True)

        # Generate new IDs for the remaining rows
        max_num = max(
            int(x.replace("EMP", "")) for x in df["Employee_ID"] if x.startswith("EMP")
        )
        for _, row in rows.iloc[1:].iterrows():
            max_num += 1
            row["Employee_ID"] = f"EMP{max_num}"
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

# 3. Check that all IDs are now unique
assert df["Employee_ID"].is_unique, "Duplicate IDs still exist!"

# 4. Save the result
df.to_csv("final_cleaned_employee_dataset.csv", index=False)
print("Done! Cleaned file saved.")
