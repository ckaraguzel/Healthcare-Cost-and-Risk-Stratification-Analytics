"""
01_data_prep.py
Healthcare Cost & Risk Stratification Analytics
------------------------------------------------
Loads the insurance CSV, cleans data, engineers features,
and loads everything into a local SQLite database so the
SQL queries in analysis_queries.sql can be run directly.
"""

import pandas as pd
import sqlite3
import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "insurance.csv")
DB_PATH   = os.path.join(BASE_DIR, "data", "healthcare.db")

# ── 1. Load CSV ─────────────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}\n")

# ── 2. Basic validation ─────────────────────────────────────────────────────
print("Null values per column:")
print(df.isnull().sum())
print()

assert df.isnull().sum().sum() == 0, "Dataset contains nulls — investigate!"

# ── 3. Feature Engineering ─────────────────────────────────────────────────
def age_group(age):
    if age < 30:   return "Under 30"
    elif age <= 50: return "30-50"
    else:           return "50+"

def bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal"
    elif bmi < 30: return "Overweight"
    else:          return "Obese"

df["age_group"]     = df["age"].apply(age_group)
df["bmi_category"]  = df["bmi"].apply(bmi_category)
df["high_risk_flag"] = ((df["smoker"] == "yes") & (df["bmi"] >= 30)).astype(int)

# Ordered categoricals for consistent chart sorting
age_order = ["Under 30", "30-50", "50+"]
bmi_order = ["Underweight", "Normal", "Overweight", "Obese"]
df["age_group"]    = pd.Categorical(df["age_group"],    categories=age_order, ordered=True)
df["bmi_category"] = pd.Categorical(df["bmi_category"], categories=bmi_order, ordered=True)

print("Derived columns added:")
print(df[["age", "age_group", "bmi", "bmi_category", "smoker", "high_risk_flag"]].head(10))
print()

# ── 4. Summary stats ────────────────────────────────────────────────────────
print("── Charges Summary ─────────────────────────────────────────")
print(df["charges"].describe().round(2))
print()

# ── 5. Write to SQLite ──────────────────────────────────────────────────────
print(f"Writing to SQLite: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)

# Write base table (matches the SQL schema)
df.to_sql("patients", conn, if_exists="replace", index=False)

# Verify row count
count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
print(f"  Rows written: {count}")
conn.close()

print("\nData preparation complete. Run 02_eda_visualizations.py next.")
