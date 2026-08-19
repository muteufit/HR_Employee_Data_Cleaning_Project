import pandas as pd

# Mapping dictionaries
dept_map = {
    "fin": "finance",
    "support": "customer support",
    "ops": "operations",
    "mktg": "marketing",
    "eng": "engineering",
}
gender_map = {"m": "male", "f": "female"}
resigned_map = {"y": "yes", "n": "no", "0": "no", "1": "yes"}

# Load data
df = pd.read_csv("employee_dataset.csv")

# Clean text columns: strip whitespace and lowercase
df["Department"] = df["Department"].str.strip().str.lower()
df["Gender"] = df["Gender"].str.strip().str.lower()
df["Resigned"] = df["Resigned"].str.strip().str.lower()

# Apply mappings
df["Department"] = df["Department"].replace(dept_map)
df["Gender"] = df["Gender"].replace(gender_map)
df["Resigned"] = df["Resigned"].replace(resigned_map)

# Save cleaned data
df.to_csv("fully_cleaned_employee_dataset.csv", index=False)
