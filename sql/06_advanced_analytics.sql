-- Advanced Customer Purchase Lead, Lag, and Running Totals
-- Target: MySQL 8.x

USE customer_intelligence_db;

WITH transaction_lead_lag AS (
    -- Tracks previous and subsequent purchase dates for each order
    SELECT 
        t.transaction_id,
        t.customer_id,
        d.full_date AS current_order_date,
        t.total_amount,
        LAG(d.full_date) OVER (PARTITION BY t.customer_id ORDER BY d.full_date) AS previous_order_date,
        LEAD(d.full_date) OVER (PARTITION BY t.customer_id ORDER BY d.full_date) AS next_order_date
    FROM fact_transactions t
    JOIN dim_dates d ON t.date_id = d.date_id
),
interval_calculations AS (
    -- Computes interval between transactions in days
    SELECT 
        customer_id,
        current_order_date,
        total_amount,
        DATEDIFF(current_order_date, previous_order_date) AS days_since_previous_order,
        DATEDIFF(next_order_date, current_order_date) AS days_until_next_order
    FROM transaction_lead_lag
)
-- Calculates cumulative spend and transaction metrics
SELECT 
    ic.customer_id,
    ic.current_order_date,
    ic.total_amount AS transaction_spend,
    ic.days_since_previous_order,
    ic.days_until_next_order,
    SUM(ic.total_amount) OVER (
        PARTITION BY ic.customer_id 
        ORDER BY ic.current_order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_spend,
    ROUND(AVG(ic.days_since_previous_order) OVER (
        PARTITION BY ic.customer_id 
        ORDER BY ic.current_order_date
    ), 1) AS moving_avg_purchase_interval
FROM interval_calculations ic
ORDER BY ic.customer_id, ic.current_order_date;
