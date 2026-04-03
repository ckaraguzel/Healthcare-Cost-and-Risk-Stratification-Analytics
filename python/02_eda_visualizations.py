"""
02_eda_visualizations.py
Healthcare Cost & Risk Stratification Analytics
------------------------------------------------
Exploratory Data Analysis — static charts saved to /outputs/figures/
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import sqlite3
import os

# ── Setup ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH    = os.path.join(BASE_DIR, "data", "healthcare.db")
FIG_DIR    = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Color palette (accessible, professional)
PALETTE    = {"yes": "#E05252", "no": "#4A90D9"}
AGE_COLORS = ["#4A90D9", "#F5A623", "#E05252"]
BMI_COLORS = ["#7ED6C8", "#4A90D9", "#F5A623", "#E05252"]

plt.rcParams.update({
    "font.family":    "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
})

# ── Load data ───────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df   = pd.read_sql("SELECT * FROM patients", conn)
conn.close()

age_order = ["Under 30", "30-50", "50+"]
bmi_order = ["Underweight", "Normal", "Overweight", "Obese"]
df["age_group"]    = pd.Categorical(df["age_group"],    categories=age_order, ordered=True)
df["bmi_category"] = pd.Categorical(df["bmi_category"], categories=bmi_order, ordered=True)

def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

fmt_dollar = mtick.FuncFormatter(lambda x, _: f"${x:,.0f}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: Distribution of Healthcare Charges (histogram)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(df["charges"], bins=50, color="#4A90D9", edgecolor="white", linewidth=0.5)
ax.axvline(df["charges"].mean(), color="#E05252", linestyle="--", linewidth=1.5,
           label=f"Mean  ${df['charges'].mean():,.0f}")
ax.axvline(df["charges"].median(), color="#F5A623", linestyle="--", linewidth=1.5,
           label=f"Median ${df['charges'].median():,.0f}")
ax.xaxis.set_major_formatter(fmt_dollar)
ax.set_title("Distribution of Annual Healthcare Charges")
ax.set_xlabel("Annual Charges ($)")
ax.set_ylabel("Patient Count")
ax.legend()
fig.tight_layout()
save(fig, "01_charge_distribution.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Average Cost — Smoker vs Non-Smoker
# ─────────────────────────────────────────────────────────────────────────────
smoke_avg = df.groupby("smoker")["charges"].mean().reset_index()
smoke_avg.columns = ["smoker", "avg_charges"]
smoke_avg["label"] = smoke_avg["smoker"].map({"yes": "Smoker", "no": "Non-Smoker"})

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(smoke_avg["label"], smoke_avg["avg_charges"],
              color=[PALETTE[s] for s in smoke_avg["smoker"]], width=0.5, edgecolor="white")
for bar, val in zip(bars, smoke_avg["avg_charges"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 300,
            f"${val:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=11)
ax.yaxis.set_major_formatter(fmt_dollar)
ax.set_title("Average Annual Cost: Smoker vs Non-Smoker")
ax.set_ylabel("Average Charges ($)")
ax.set_ylim(0, smoke_avg["avg_charges"].max() * 1.2)
fig.tight_layout()
save(fig, "02_cost_by_smoking.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Average Cost by Age Group
# ─────────────────────────────────────────────────────────────────────────────
age_avg = df.groupby("age_group", observed=True)["charges"].mean().reset_index()

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(age_avg["age_group"].astype(str), age_avg["charges"],
              color=AGE_COLORS, width=0.5, edgecolor="white")
for bar, val in zip(bars, age_avg["charges"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
            f"${val:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=11)
ax.yaxis.set_major_formatter(fmt_dollar)
ax.set_title("Average Annual Cost by Age Group")
ax.set_ylabel("Average Charges ($)")
ax.set_ylim(0, age_avg["charges"].max() * 1.2)
fig.tight_layout()
save(fig, "03_cost_by_age_group.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4: Average Cost by BMI Category
# ─────────────────────────────────────────────────────────────────────────────
bmi_avg = df.groupby("bmi_category", observed=True)["charges"].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(bmi_avg["bmi_category"].astype(str), bmi_avg["charges"],
              color=BMI_COLORS, width=0.5, edgecolor="white")
for bar, val in zip(bars, bmi_avg["charges"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
            f"${val:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=10)
ax.yaxis.set_major_formatter(fmt_dollar)
ax.set_title("Average Annual Cost by BMI Category")
ax.set_ylabel("Average Charges ($)")
ax.set_ylim(0, bmi_avg["charges"].max() * 1.2)
fig.tight_layout()
save(fig, "04_cost_by_bmi.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5: Scatter — Age vs Charges, colored by smoking status
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
for status, group in df.groupby("smoker"):
    label = "Smoker" if status == "yes" else "Non-Smoker"
    ax.scatter(group["age"], group["charges"], c=PALETTE[status],
               alpha=0.55, s=30, label=label, edgecolors="none")
ax.yaxis.set_major_formatter(fmt_dollar)
ax.set_title("Age vs Annual Healthcare Charges by Smoking Status")
ax.set_xlabel("Age")
ax.set_ylabel("Annual Charges ($)")
ax.legend(title="Smoking Status")
fig.tight_layout()
save(fig, "05_age_vs_charges_scatter.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6: Heatmap — Avg Cost by Smoking Status × BMI Category
# ─────────────────────────────────────────────────────────────────────────────
pivot = df.pivot_table(values="charges", index="smoker",
                       columns="bmi_category", aggfunc="mean", observed=True)
pivot.index = ["Non-Smoker", "Smoker"]

fig, ax = plt.subplots(figsize=(9, 4))
sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="YlOrRd",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Avg Charges ($)"})
ax.set_title("Average Cost Heatmap: Smoking Status × BMI Category")
ax.set_xlabel("BMI Category")
ax.set_ylabel("")
fig.tight_layout()
save(fig, "06_heatmap_smoking_bmi.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7: Box plot — Charges by Region
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
region_order = df.groupby("region")["charges"].median().sort_values(ascending=False).index
df_sorted = df.copy()
df_sorted["region"] = pd.Categorical(df["region"], categories=region_order, ordered=True)
sns.boxplot(data=df_sorted, x="region", y="charges", palette="Set2",
            order=region_order, ax=ax)
ax.yaxis.set_major_formatter(fmt_dollar)
ax.set_title("Healthcare Charges Distribution by Region")
ax.set_xlabel("Region")
ax.set_ylabel("Annual Charges ($)")
fig.tight_layout()
save(fig, "07_charges_by_region_boxplot.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8: High-Risk Patients — Population Share vs Cost Share
# ─────────────────────────────────────────────────────────────────────────────
hr        = df.groupby("high_risk_flag")["charges"].agg(["count", "sum"])
hr.index  = ["Standard Risk", "High Risk"]
pop_pct   = (hr["count"] / hr["count"].sum() * 100).round(1)
cost_pct  = (hr["sum"]   / hr["sum"].sum()   * 100).round(1)

x    = [0, 1]
w    = 0.35
fig, ax = plt.subplots(figsize=(8, 5))
b1 = ax.bar([i - w/2 for i in x], pop_pct,  width=w, label="% of Population",
            color="#4A90D9", edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], cost_pct, width=w, label="% of Total Cost",
            color="#E05252", edgecolor="white")
for bar, val in zip(list(b1) + list(b2), list(pop_pct) + list(cost_pct)):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", va="bottom", fontweight="bold", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(["Standard Risk", "High Risk"])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("High-Risk Patients: Population Share vs Cost Share")
ax.set_ylabel("Percentage (%)")
ax.legend()
fig.tight_layout()
save(fig, "08_high_risk_population_vs_cost.png")

print("\nAll EDA charts saved to outputs/figures/")
print("Run 03_risk_segmentation.py next.")
