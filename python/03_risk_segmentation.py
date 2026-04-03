"""
03_risk_segmentation.py
Healthcare Cost & Risk Stratification Analytics
------------------------------------------------
Patient risk segmentation — identifies cost tiers and
produces a summary report printed to console + CSV.
"""

import pandas as pd
import sqlite3
import os

# ── Setup ───────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "data", "healthcare.db")
OUT_DIR   = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
df   = pd.read_sql("SELECT * FROM patients", conn)
conn.close()

age_order = ["Under 30", "30-50", "50+"]
bmi_order = ["Underweight", "Normal", "Overweight", "Obese"]
df["age_group"]    = pd.Categorical(df["age_group"],    categories=age_order, ordered=True)
df["bmi_category"] = pd.Categorical(df["bmi_category"], categories=bmi_order, ordered=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Cost Tier Segmentation (quartile-based)
# ─────────────────────────────────────────────────────────────────────────────
q25  = df["charges"].quantile(0.25)
q50  = df["charges"].quantile(0.50)
q75  = df["charges"].quantile(0.75)
q90  = df["charges"].quantile(0.90)

def cost_tier(c):
    if c <= q25:  return "Tier 1 – Low Cost"
    elif c <= q50: return "Tier 2 – Below Average"
    elif c <= q75: return "Tier 3 – Above Average"
    elif c <= q90: return "Tier 4 – High Cost"
    else:          return "Tier 5 – Very High Cost"

df["cost_tier"] = df["charges"].apply(cost_tier)

tier_summary = df.groupby("cost_tier").agg(
    patient_count=("charges", "count"),
    avg_charges=("charges", "mean"),
    total_charges=("charges", "sum"),
    pct_smoker=("smoker", lambda x: (x == "yes").mean() * 100),
    pct_obese=("bmi_category", lambda x: (x == "Obese").mean() * 100),
    pct_high_risk=("high_risk_flag", "mean")
).round(2)
tier_summary["total_charges"]  = tier_summary["total_charges"].round(0)
tier_summary["pct_high_risk"]  = (tier_summary["pct_high_risk"] * 100).round(1)

print("=" * 65)
print("COST TIER SEGMENTATION SUMMARY")
print("=" * 65)
print(tier_summary.to_string())
print()

# ─────────────────────────────────────────────────────────────────────────────
# 2. High-Risk Cohort Deep Dive
# ─────────────────────────────────────────────────────────────────────────────
high_risk = df[df["high_risk_flag"] == 1]
pop_total  = len(df)
cost_total = df["charges"].sum()

print("=" * 65)
print("HIGH-RISK COHORT (Smoker + Obese)")
print("=" * 65)
print(f"  Patients     : {len(high_risk):,}  ({len(high_risk)/pop_total*100:.1f}% of total)")
print(f"  Avg Cost     : ${high_risk['charges'].mean():,.2f}")
print(f"  Total Cost   : ${high_risk['charges'].sum():,.2f}  ({high_risk['charges'].sum()/cost_total*100:.1f}% of total)")
print(f"  Max Cost     : ${high_risk['charges'].max():,.2f}")
print()

# Breakdown of high-risk by age group
hr_age = high_risk.groupby("age_group", observed=True)["charges"].agg(["count", "mean"]).round(2)
hr_age.columns = ["count", "avg_charges"]
print("High-Risk by Age Group:")
print(hr_age.to_string())
print()

# ─────────────────────────────────────────────────────────────────────────────
# 3. Top 10% Cost Outliers profile
# ─────────────────────────────────────────────────────────────────────────────
outliers = df[df["charges"] >= q90].copy()

print("=" * 65)
print(f"TOP 10% COST OUTLIERS (charges ≥ ${q90:,.0f})")
print("=" * 65)
print(f"  Patient count  : {len(outliers):,}")
print(f"  Avg cost       : ${outliers['charges'].mean():,.2f}")
print(f"  % smokers      : {(outliers['smoker']=='yes').mean()*100:.1f}%")
print(f"  % obese        : {(outliers['bmi_category']=='Obese').mean()*100:.1f}%")
print(f"  % high-risk    : {outliers['high_risk_flag'].mean()*100:.1f}%")
print(f"  % age 50+      : {(outliers['age_group']=='50+').mean()*100:.1f}%")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 4. Key Findings Summary (mirrors Tableau KPI cards)
# ─────────────────────────────────────────────────────────────────────────────
smoker_avg     = df[df["smoker"] == "yes"]["charges"].mean()
nonsmoker_avg  = df[df["smoker"] == "no"]["charges"].mean()
smoking_mult   = smoker_avg / nonsmoker_avg
age50_avg      = df[df["age_group"] == "50+"]["charges"].mean()
overall_avg    = df["charges"].mean()

print("=" * 65)
print("KEY FINDINGS")
print("=" * 65)
print(f"  Overall avg annual cost      : ${overall_avg:,.2f}")
print(f"  Smoker avg cost              : ${smoker_avg:,.2f}")
print(f"  Non-smoker avg cost          : ${nonsmoker_avg:,.2f}")
print(f"  Smokers cost {smoking_mult:.1f}x more than non-smokers")
print(f"  Age 50+ avg cost             : ${age50_avg:,.2f}  ({age50_avg/overall_avg*100-100:.0f}% above avg)")
print(f"  High-risk patients           : {len(high_risk)/pop_total*100:.1f}% of pop → {high_risk['charges'].sum()/cost_total*100:.1f}% of cost")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 5. Export enriched dataset
# ─────────────────────────────────────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "patients_enriched.csv")
df.to_csv(out_path, index=False)
print(f"Enriched dataset exported to: {out_path}")
print("\nRun 04_dashboard.py to launch the interactive dashboard.")
