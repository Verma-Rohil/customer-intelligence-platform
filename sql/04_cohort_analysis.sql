-- Cohort Retention Analysis Matrix
-- Target: MySQL 8.x

USE customer_intelligence_db;

WITH customer_signup_cohort AS (
    -- Identifies the acquisition month for each customer
    SELECT 
        customer_id,
        DATE_FORMAT(signup_date, '%Y-%m-01') AS cohort_month
    FROM dim_customers
),
customer_monthly_activity AS (
    -- Collects months where the customer completed at least one transaction
    SELECT DISTINCT
        t.customer_id,
        DATE_FORMAT(d.full_date, '%Y-%m-01') AS activity_month
    FROM fact_transactions t
    JOIN dim_dates d ON t.date_id = d.date_id
),
cohort_intervals AS (
    -- Computes the month difference between signup and transaction activity
    SELECT 
        c.cohort_month,
        a.activity_month,
        TIMESTAMPDIFF(MONTH, STR_TO_DATE(c.cohort_month, '%Y-%m-%d'), STR_TO_DATE(a.activity_month, '%Y-%m-%d')) AS month_number
    FROM customer_signup_cohort c
    JOIN customer_monthly_activity a ON c.customer_id = a.customer_id
    WHERE STR_TO_DATE(a.activity_month, '%Y-%m-%d') >= STR_TO_DATE(c.cohort_month, '%Y-%m-%d')
),
cohort_sizes AS (
    -- Computes starting customer volume for each cohort
    SELECT 
        cohort_month, 
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_signup_cohort
    GROUP BY cohort_month
)
-- Renders the monthly cohort retention grid
SELECT 
    ci.cohort_month,
    cs.cohort_size,
    ci.month_number,
    COUNT(DISTINCT ci.activity_month) AS active_users,
    ROUND((COUNT(DISTINCT ci.activity_month) / cs.cohort_size) * 100, 2) AS retention_percent
FROM cohort_intervals ci
JOIN cohort_sizes cs ON ci.cohort_month = cs.cohort_month
GROUP BY ci.cohort_month, cs.cohort_size, ci.month_number
ORDER BY ci.cohort_month, ci.month_number;
