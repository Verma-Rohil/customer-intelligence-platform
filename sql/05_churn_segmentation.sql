-- Churn Rate Segmentation by Product Category and Demographics
-- Target: MySQL 8.x

USE customer_intelligence_db;

WITH latest_data_date AS (
    SELECT MAX(full_date) AS max_date FROM dim_dates
),
customer_churn_status AS (
    -- Defines active vs churned status based on 60 days inactivity window
    SELECT 
        c.customer_id,
        c.city_tier,
        c.gender,
        c.device_pref,
        DATEDIFF((SELECT max_date FROM latest_data_date), MAX(d.full_date)) AS days_inactive,
        CASE 
            WHEN DATEDIFF((SELECT max_date FROM latest_data_date), MAX(d.full_date)) > 60 THEN 1 
            ELSE 0 
        END AS is_churned
    FROM dim_customers c
    LEFT JOIN fact_transactions t ON c.customer_id = t.customer_id
    LEFT JOIN dim_dates d ON t.date_id = d.date_id
    GROUP BY c.customer_id, c.city_tier, c.gender, c.device_pref
),
product_affinities AS (
    -- Maps customers to their top category by spent amount
    SELECT 
        t.customer_id,
        p.category AS favorite_category,
        SUM(t.total_amount) AS category_spend,
        ROW_NUMBER() OVER (PARTITION BY t.customer_id ORDER BY SUM(t.total_amount) DESC) AS rank_order
    FROM fact_transactions t
    JOIN dim_products p ON t.product_id = p.product_id
    GROUP BY t.customer_id, p.category
)
-- Aggregates churn metric outputs grouped by category and city tier
SELECT 
    pa.favorite_category,
    cc.city_tier,
    COUNT(DISTINCT cc.customer_id) AS total_customers,
    SUM(cc.is_churned) AS churned_customers,
    ROUND((SUM(cc.is_churned) / COUNT(DISTINCT cc.customer_id)) * 100, 2) AS churn_rate_percent
FROM customer_churn_status cc
JOIN product_affinities pa ON cc.customer_id = pa.customer_id
WHERE pa.rank_order = 1
GROUP BY pa.favorite_category, cc.city_tier
ORDER BY total_customers DESC, churn_rate_percent DESC;
