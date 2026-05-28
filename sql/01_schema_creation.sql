-- DDL Schema Creation Script for Customer Intelligence Platform
-- Target: MySQL 8.x or compatible systems

CREATE DATABASE IF NOT EXISTS customer_intelligence_db;
USE customer_intelligence_db;

-- 1. Create dim_customers table
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    city_tier VARCHAR(10) DEFAULT 'Tier 3',
    gender VARCHAR(10) DEFAULT 'Unknown',
    device_pref VARCHAR(20) DEFAULT 'Unknown',
    payment_mode VARCHAR(30) DEFAULT 'Unknown',
    marital_status VARCHAR(20) DEFAULT 'Unknown',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    CONSTRAINT chk_city_tier CHECK (city_tier IN ('Tier 1', 'Tier 2', 'Tier 3')),
    CONSTRAINT chk_gender CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    CONSTRAINT chk_device CHECK (device_pref IN ('Mobile', 'Web', 'Tablet', 'Unknown')),
    CONSTRAINT chk_marital CHECK (marital_status IN ('Single', 'Married', 'Unknown'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create dim_products table
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    brand VARCHAR(50) DEFAULT 'Generic',
    price_range VARCHAR(20) DEFAULT 'Medium',
    PRIMARY KEY (product_id),
    CONSTRAINT chk_price_range CHECK (price_range IN ('Low', 'Medium', 'High'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Create dim_dates table
CREATE TABLE IF NOT EXISTS dim_dates (
    date_id INT NOT NULL,
    full_date DATE NOT NULL,
    day_of_week INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (date_id),
    UNIQUE KEY uq_full_date (full_date),
    CONSTRAINT chk_day CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_quarter CHECK (quarter BETWEEN 1 AND 4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Create fact_transactions table
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INT AUTO_INCREMENT NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    date_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_applied DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    delivery_days INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    CONSTRAINT fk_transaction_customer FOREIGN KEY (customer_id) 
        REFERENCES dim_customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transaction_product FOREIGN KEY (product_id) 
        REFERENCES dim_products(product_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transaction_date FOREIGN KEY (date_id) 
        REFERENCES dim_dates(date_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_price CHECK (unit_price >= 0.00),
    CONSTRAINT chk_discount CHECK (discount_applied >= 0.00),
    CONSTRAINT chk_delivery CHECK (delivery_days >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Create Indexes for Optimization
CREATE INDEX idx_transactions_customer_date ON fact_transactions(customer_id, date_id);
CREATE INDEX idx_transactions_product ON fact_transactions(product_id);
CREATE INDEX idx_customers_signup ON dim_customers(signup_date);
CREATE INDEX idx_products_category ON dim_products(category);
CREATE INDEX idx_dates_full ON dim_dates(full_date);
