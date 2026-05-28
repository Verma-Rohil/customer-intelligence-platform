-- Data Loading Queries & Bulk Ingestion Templates
-- Target: MySQL 8.x
-- Note: Replace '/path/to/' with actual absolute paths if running bulk loads via MySQL command line

USE customer_intelligence_db;

-- 1. Load Data into dim_customers (Template)
-- LOAD DATA INFILE '/path/to/raw_customers.csv'
-- INTO TABLE dim_customers
-- FIELDS TERMINATED BY ',' 
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (customer_id, signup_date, city_tier, gender, device_pref, payment_mode, marital_status);

-- 2. Load Data into dim_products (Template)
-- LOAD DATA INFILE '/path/to/raw_products.csv'
-- INTO TABLE dim_products
-- FIELDS TERMINATED BY ',' 
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (product_id, category, subcategory, brand, price_range);

-- 3. Load Data into fact_transactions (Template)
-- LOAD DATA INFILE '/path/to/raw_transactions.csv'
-- INTO TABLE fact_transactions
-- FIELDS TERMINATED BY ',' 
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (customer_id, product_id, date_id, quantity, unit_price, discount_applied, total_amount, delivery_days);

-- Standard SQL manual insert statements for baseline configurations
INSERT INTO dim_products (product_id, category, subcategory, brand, price_range)
VALUES ('DEFAULT_PROD', 'General', 'Miscellaneous', 'Generic', 'Medium')
ON DUPLICATE KEY UPDATE product_id=product_id;

INSERT INTO dim_customers (customer_id, signup_date, city_tier, gender, device_pref, payment_mode, marital_status)
VALUES ('DEFAULT_CUST', '2026-01-01', 'Tier 3', 'Unknown', 'Unknown', 'Unknown', 'Unknown')
ON DUPLICATE KEY UPDATE customer_id=customer_id;
