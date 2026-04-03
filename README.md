# Healthcare Cost & Risk Stratification Analytics

## Overview
This project analyzes healthcare cost drivers and patient risk factors using SQL, Python, and Tableau. The objective is to identify high-cost populations and uncover patterns that can support data-driven decision-making in healthcare systems.

## Business Problem
Healthcare organizations must understand which patient groups contribute most to overall costs in order to design targeted interventions, improve outcomes, and optimize resource allocation.

## Dataset
- Source: Medical Cost Personal Dataset (Kaggle)
- Size: ~1,300 patient records
- Features:
  - Age
  - Sex
  - BMI (Body Mass Index)
  - Smoking status
  - Number of dependents
  - Region
  - Healthcare charges

## Tools & Technologies
- SQL (data querying, aggregation, segmentation)
- Python (pandas, matplotlib)
- Tableau (interactive dashboard visualization)

## Data Preparation
- Cleaned and validated dataset
- Created derived features:
  - Age groups (Under 30, 30–50, 50+)
  - BMI categories (Normal, Overweight, Obese)
  - High-risk flag (smoker + obese)

## Key Analysis
- Cost comparison across demographic groups
- Identification of high-risk patient segments
- Combined risk factor analysis (smoking + BMI)
- Exploration of cost distribution and outliers

## Key Insights
- Smoking is the strongest predictor of high healthcare costs, with smokers incurring significantly higher expenses
- Obesity is associated with increased costs, especially when combined with smoking
- Patients aged 50+ represent the highest average cost group
- A small subset of high-risk patients contributes disproportionately to total healthcare spending

## Dashboard
The Tableau dashboard provides:
- KPI summary (average cost, total patients)
- Cost breakdown by smoking status, age group, and BMI
- Scatter plot of age vs healthcare costs
- Interactive filters for demographic exploration
