-- RFM Customer Matrix Calculation
-- Target: MySQL 8.x

USE customer_intelligence_db;

WITH customer_aggregates AS (
    -- Aggregates raw transactional features per customer
    SELECT 
        t.customer_id,
        DATEDIFF(
            (SELECT MAX(d.full_date) FROM dim_dates d JOIN fact_transactions ft ON d.date_id = ft.date_id), 
            MAX(d.full_date)
        ) AS raw_recency,
        COUNT(t.transaction_id) AS raw_frequency,
        SUM(t.total_amount) AS raw_monetary
    FROM fact_transactions t
    JOIN dim_dates d ON t.date_id = d.date_id
    GROUP BY t.customer_id
),
rfm_scoring AS (
    -- Assigns 1-5 scores using quintile distribution (NTILE)
    SELECT 
        customer_id,
        raw_recency,
        raw_frequency,
        raw_monetary,
        NTILE(5) OVER (ORDER BY raw_recency DESC) AS r_score, -- 5 represents lowest recency value (most recent)
        NTILE(5) OVER (ORDER BY raw_frequency ASC) AS f_score,  -- 5 represents highest frequency count
        NTILE(5) OVER (ORDER BY raw_monetary ASC) AS m_score    -- 5 represents highest spend amount
    FROM customer_aggregates
)
SELECT 
    customer_id,
    raw_recency,
    raw_frequency,
    raw_monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score) AS rfm_score_composite,
    CASE 
        WHEN CONCAT(r_score, f_score, m_score) IN ('555', '554', '545', '455', '454') THEN 'Champions'
        WHEN f_score >= 4 AND m_score >= 4 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score = 1 AND f_score = 1 THEN 'Lost / Hibernating'
        ELSE 'Needs Attention'
    END AS business_segment
FROM rfm_scoring;
