-- ============================================================
-- Healthcare Cost & Risk Stratification Analysis
-- Central California Alliance for Health - Portfolio Project
-- ============================================================

-- ----------------------------------------------------------------
-- STEP 1: Create the base table (run in SQLite or any SQL engine)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    age         INTEGER,
    sex         TEXT,
    bmi         REAL,
    children    INTEGER,
    smoker      TEXT,
    region      TEXT,
    charges     REAL
);

-- ----------------------------------------------------------------
-- STEP 2: Add derived columns (as a view for portability)
-- ----------------------------------------------------------------
CREATE VIEW IF NOT EXISTS patients_enriched AS
SELECT
    age,
    sex,
    bmi,
    children,
    smoker,
    region,
    charges,

    -- Age group segmentation
    CASE
        WHEN age < 30 THEN 'Under 30'
        WHEN age BETWEEN 30 AND 50 THEN '30-50'
        ELSE '50+'
    END AS age_group,

    -- BMI category (WHO classification)
    CASE
        WHEN bmi < 18.5 THEN 'Underweight'
        WHEN bmi < 25.0 THEN 'Normal'
        WHEN bmi < 30.0 THEN 'Overweight'
        ELSE 'Obese'
    END AS bmi_category,

    -- High-risk flag: smoker AND obese
    CASE
        WHEN smoker = 'yes' AND bmi >= 30.0 THEN 1
        ELSE 0
    END AS high_risk_flag

FROM patients;

-- ----------------------------------------------------------------
-- STEP 3: KPI Summary
-- ----------------------------------------------------------------
SELECT
    COUNT(*)                        AS total_patients,
    ROUND(AVG(charges), 2)          AS avg_annual_cost,
    ROUND(SUM(charges), 2)          AS total_cost,
    ROUND(MAX(charges), 2)          AS max_cost,
    ROUND(MIN(charges), 2)          AS min_cost
FROM patients;

-- ----------------------------------------------------------------
-- STEP 4: Cost by Smoking Status
-- ----------------------------------------------------------------
SELECT
    smoker,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost,
    ROUND(MAX(charges), 2)          AS max_cost
FROM patients
GROUP BY smoker
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 5: Cost by Age Group
-- ----------------------------------------------------------------
SELECT
    age_group,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost
FROM patients_enriched
GROUP BY age_group
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 6: Cost by BMI Category
-- ----------------------------------------------------------------
SELECT
    bmi_category,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost
FROM patients_enriched
GROUP BY bmi_category
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 7: Cost by Region
-- ----------------------------------------------------------------
SELECT
    region,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost
FROM patients
GROUP BY region
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 8: High-Risk Patient Segment Analysis
-- ----------------------------------------------------------------
SELECT
    high_risk_flag,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients), 1) AS pct_of_population
FROM patients_enriched
GROUP BY high_risk_flag;

-- ----------------------------------------------------------------
-- STEP 9: Combined Risk Factor Matrix (Smoker x BMI)
-- ----------------------------------------------------------------
SELECT
    smoker,
    bmi_category,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost
FROM patients_enriched
GROUP BY smoker, bmi_category
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 10: Top 10% Cost Outliers
-- ----------------------------------------------------------------
SELECT
    age,
    sex,
    bmi,
    smoker,
    region,
    ROUND(charges, 2)               AS charges,
    age_group,
    bmi_category,
    high_risk_flag
FROM patients_enriched
WHERE charges >= (
    SELECT PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY charges) FROM patients
    -- Note: for SQLite use: SELECT charges FROM patients ORDER BY charges DESC LIMIT 134
)
ORDER BY charges DESC;

-- ----------------------------------------------------------------
-- STEP 11: Sex-based cost comparison
-- ----------------------------------------------------------------
SELECT
    sex,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost,
    ROUND(SUM(charges), 2)          AS total_cost
FROM patients
GROUP BY sex
ORDER BY avg_cost DESC;

-- ----------------------------------------------------------------
-- STEP 12: Cost by number of dependents
-- ----------------------------------------------------------------
SELECT
    children                        AS num_dependents,
    COUNT(*)                        AS patient_count,
    ROUND(AVG(charges), 2)          AS avg_cost
FROM patients
GROUP BY children
ORDER BY children;
