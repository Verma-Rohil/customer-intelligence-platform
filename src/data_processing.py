"""
ETL Pipeline & Ingestion Engine for Customer Intelligence Platform.
Supports database-agnostic operations (MySQL & SQLite fallback) and Olist ingestion.
Author: Rohil Verma
"""

import os
import logging
import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from src import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Creates and returns an active SQLAlchemy database engine.
    Attempts connection to MySQL first; if database doesn't exist, creates it.
    Falls back to local SQLite on server failure.
    """
    try:
        # Try connecting to MySQL directly
        engine = create_engine(config.DB_URL)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        logger.info("Database connection established: MySQL Server active.")
        return engine
    except Exception as e:
        # Check if the error is "Unknown database" (1049)
        if "1049" in str(e):
            logger.info("MySQL Database 'customer_intelligence_db' does not exist. Creating it now...")
            try:
                # Connect to server root (without the database name)
                base_url = config.DB_URL.rsplit("/", 1)[0] + "/"
                temp_engine = create_engine(base_url)
                with temp_engine.connect() as conn:
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME};"))
                    conn.commit()
                logger.info(f"MySQL Database '{config.DB_NAME}' created successfully.")
                
                # Now try connecting again with the database name
                engine = create_engine(config.DB_URL)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1;"))
                return engine
            except Exception as create_err:
                logger.error(f"Failed to create MySQL database dynamically: {create_err}")
                
        logger.warning(f"MySQL connection failed ({e}). Falling back to local SQLite database...")
        sqlite_path = os.path.join(config.DATA_DIR, "customer_intelligence.db")
        sqlite_url = f"sqlite:///{sqlite_path}"
        engine = create_engine(sqlite_url)
        return engine


def initialize_database():
    """
    Executes the DDL script to create the database schema and indexes.
    Transpiles MySQL DDL to SQLite DDL dynamically if running on SQLite fallback.
    """
    logger.info("Initializing database schema...")
    schema_file = os.path.join(config.BASE_DIR, "sql", "01_schema_creation.sql")
    if not os.path.exists(schema_file):
        logger.error(f"DDL schema file not found at: {schema_file}")
        return False
    
    try:
        engine = get_db_connection()
        is_sqlite = "sqlite" in str(engine.url)
        
        with open(schema_file, "r") as f:
            ddl_queries = f.read().split(";")
        
        with engine.connect() as conn:
            for query in ddl_queries:
                clean_query = query.strip()
                if not clean_query:
                    continue
                
                # Strip SQL Comments safely for parsing comparison
                lines = [line.split("--")[0].strip() for line in clean_query.split("\n")]
                clean_query_no_comments = " ".join([l for l in lines if l]).strip()
                
                if not clean_query_no_comments:
                    continue
                
                if is_sqlite:
                    # SQLite Compatibility Transpilation
                    if clean_query_no_comments.upper().startswith("CREATE DATABASE") or clean_query_no_comments.upper().startswith("USE "):
                        continue
                    
                    # Strip MySQL storage engine and collations
                    clean_query = clean_query.replace("ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci", "")
                    clean_query = clean_query.replace("AUTO_INCREMENT", "")
                    clean_query = clean_query.replace("ON UPDATE CURRENT_TIMESTAMP", "")
                
                conn.execute(text(clean_query))
            conn.commit()
        logger.info("Database schema initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Database schema initialization failed: {e}")
        return False


def populate_date_dimension(start_date: datetime.date, end_date: datetime.date):
    """
    Generates and populates the dim_dates dimension table dynamically.
    """
    logger.info(f"Populating dim_dates from {start_date} to {end_date}...")
    try:
        engine = get_db_connection()
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        dates_df = pd.DataFrame({
            'full_date': date_range.date
        })
        
        dates_df['date_id'] = dates_df['full_date'].apply(
            lambda x: int(x.strftime("%Y%m%d"))
        )
        dates_df['day_of_week'] = pd.to_datetime(dates_df['full_date']).dt.dayofweek + 1
        dates_df['month'] = pd.to_datetime(dates_df['full_date']).dt.month
        dates_df['quarter'] = pd.to_datetime(dates_df['full_date']).dt.quarter
        dates_df['is_weekend'] = dates_df['day_of_week'].apply(lambda x: x in [6, 7])
        dates_df['is_holiday'] = False
        
        # Prevent key errors on duplicate records by checking first or using append
        with engine.connect() as conn:
            existing_count = conn.execute(text("SELECT COUNT(*) FROM dim_dates;")).scalar()
            
        if existing_count == 0:
            dates_df.to_sql(
                name="dim_dates",
                con=engine,
                if_exists="append",
                index=False,
                method="multi"
            )
            logger.info(f"Successfully loaded {len(dates_df)} days into dim_dates.")
        else:
            logger.info("dim_dates records already exist. Skipping date loading.")
        return True
    except Exception as e:
        logger.warning(f"Error populating dim_dates: {e}")
        return False


def run_etl():
    """
    ETL Load Engine for Olist E-Commerce dataset.
    Loads raw relational CSVs, performs mappings, enriches attributes, and loads into DW.
    """
    logger.info("Starting Olist ETL ingestion sequence...")
    
    # 1. Initialize schema
    if not initialize_database():
        logger.error("ETL aborted due to schema initialization error.")
        return False
        
    try:
        engine = get_db_connection()
        
        # Define paths to raw CSV files
        raw_cust_path = os.path.join(config.RAW_DATA_DIR, "olist_customers_dataset.csv")
        raw_orders_path = os.path.join(config.RAW_DATA_DIR, "olist_orders_dataset.csv")
        raw_items_path = os.path.join(config.RAW_DATA_DIR, "olist_order_items_dataset.csv")
        raw_payments_path = os.path.join(config.RAW_DATA_DIR, "olist_order_payments_dataset.csv")
        raw_reviews_path = os.path.join(config.RAW_DATA_DIR, "olist_order_reviews_dataset.csv")
        raw_products_path = os.path.join(config.RAW_DATA_DIR, "olist_products_dataset.csv")
        raw_trans_path = os.path.join(config.RAW_DATA_DIR, "product_category_name_translation.csv")
        
        # Validate existence
        for path in [raw_cust_path, raw_orders_path, raw_items_path, raw_payments_path, raw_reviews_path, raw_products_path, raw_trans_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required Olist CSV missing at: {path}")
                
        # --- A. Load Raw Files into Memory ---
        logger.info("Loading Olist raw tables into Pandas DataFrames...")
        customers_raw = pd.read_csv(raw_cust_path)
        orders_raw = pd.read_csv(raw_orders_path)
        items_raw = pd.read_csv(raw_items_path)
        payments_raw = pd.read_csv(raw_payments_path)
        reviews_raw = pd.read_csv(raw_reviews_path)
        products_raw = pd.read_csv(raw_products_path)
        trans_raw = pd.read_csv(raw_trans_path)
        
        # Parse dates
        orders_raw['order_purchase_timestamp'] = pd.to_datetime(orders_raw['order_purchase_timestamp'])
        orders_raw['order_delivered_customer_date'] = pd.to_datetime(orders_raw['order_delivered_customer_date'])
        
        # --- B. Process dim_products ---
        logger.info("Processing dim_products...")
        # Merge products with English category name
        products_merged = pd.merge(products_raw, trans_raw, on='product_category_name', how='left')
        products_merged['category'] = products_merged['product_category_name_english'].fillna(
            products_merged['product_category_name'].fillna('Unknown')
        ).apply(lambda x: x.replace('_', ' ').title())
        
        # Map price range categories from order items price aggregates
        prod_prices = items_raw.groupby('product_id')['price'].mean().reset_index()
        def get_price_range(p):
            if p < 50.0:
                return 'Low'
            elif p <= 200.0:
                return 'Medium'
            else:
                return 'High'
        prod_prices['price_range'] = prod_prices['price'].apply(get_price_range)
        
        dim_products = pd.merge(products_merged[['product_id', 'category', 'product_category_name']], prod_prices, on='product_id', how='left')
        dim_products['subcategory'] = dim_products['product_category_name'].fillna('Miscellaneous').apply(lambda x: x.replace('_', ' ').title())
        dim_products['brand'] = 'Generic'
        dim_products['price_range'] = dim_products['price_range'].fillna('Medium')
        
        dim_products_final = dim_products[['product_id', 'category', 'subcategory', 'brand', 'price_range']].drop_duplicates(subset=['product_id'])
        
        # --- C. Process dim_customers ---
        logger.info("Processing dim_customers...")
        # Map transactional customer_id to customer_unique_id
        cust_order_link = pd.merge(orders_raw, customers_raw, on='customer_id', how='inner')
        
        # Calculate signup date (first purchase date) per customer_unique_id
        customer_signups = cust_order_link.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
        customer_signups.rename(columns={'order_purchase_timestamp': 'signup_date'}, inplace=True)
        customer_signups['signup_date'] = customer_signups['signup_date'].dt.date
        
        # Extract latest geographical state and city tier mapping
        latest_cust_loc = cust_order_link.sort_values(by='order_purchase_timestamp').groupby('customer_unique_id').last().reset_index()
        
        def map_city_tier(state):
            if state in ['SP', 'RJ', 'MG']:
                return 'Tier 1'
            elif state in ['PR', 'RS', 'SC', 'ES', 'DF']:
                return 'Tier 2'
            else:
                return 'Tier 3'
        latest_cust_loc['city_tier'] = latest_cust_loc['customer_state'].apply(map_city_tier)
        
        # Synthesize customer payment profiles by finding most common payment method
        customer_payment_modes = pd.merge(cust_order_link[['customer_unique_id', 'order_id']], payments_raw, on='order_id', how='inner')
        if not customer_payment_modes.empty:
            cust_fav_payment = customer_payment_modes.groupby(['customer_unique_id', 'payment_type']).size().reset_index(name='count')
            cust_fav_payment = cust_fav_payment.sort_values(by=['customer_unique_id', 'count'], ascending=[True, False]).groupby('customer_unique_id').first().reset_index()
            # Map payment modes to clean terminology
            payment_map = {
                'credit_card': 'Credit Card',
                'boleto': 'Boleto (Ticket)',
                'voucher': 'Voucher',
                'debit_card': 'Debit Card'
            }
            cust_fav_payment['payment_mode'] = cust_fav_payment['payment_type'].map(payment_map).fillna('Unknown')
        else:
            cust_fav_payment = pd.DataFrame(columns=['customer_unique_id', 'payment_mode'])
            
        # Merge all customer dimensions
        dim_customers = pd.merge(customer_signups, latest_cust_loc[['customer_unique_id', 'customer_city', 'customer_state', 'city_tier']], on='customer_unique_id', how='left')
        dim_customers = pd.merge(dim_customers, cust_fav_payment[['customer_unique_id', 'payment_mode']], on='customer_unique_id', how='left')
        dim_customers['payment_mode'] = dim_customers['payment_mode'].fillna('Unknown')
        
        # Inject seeded demographic distributions for ML pipelines
        np.random.seed(config.RANDOM_SEED)
        n_cust = len(dim_customers)
        dim_customers['gender'] = np.random.choice(['Male', 'Female', 'Other', 'Unknown'], size=n_cust, p=[0.48, 0.49, 0.02, 0.01])
        dim_customers['device_pref'] = np.random.choice(['Mobile', 'Web', 'Tablet', 'Unknown'], size=n_cust, p=[0.70, 0.22, 0.06, 0.02])
        dim_customers['marital_status'] = np.random.choice(['Single', 'Married', 'Unknown'], size=n_cust, p=[0.44, 0.54, 0.02])
        
        dim_customers.rename(columns={'customer_unique_id': 'customer_id'}, inplace=True)
        dim_customers_final = dim_customers[['customer_id', 'signup_date', 'city_tier', 'gender', 'device_pref', 'payment_mode', 'marital_status']].drop_duplicates(subset=['customer_id'])
        
        # --- D. Process dim_dates Calendar range ---
        min_date = orders_raw['order_purchase_timestamp'].min().date()
        max_date = orders_raw['order_purchase_timestamp'].max().date()
        populate_date_dimension(min_date, max_date)
        
        # --- E. Process fact_transactions ---
        logger.info("Processing fact_transactions...")
        # Link order items with purchase details
        trans_merged = pd.merge(items_raw, orders_raw, on='order_id', how='inner')
        trans_merged = pd.merge(trans_merged, customers_raw, on='customer_id', how='inner')
        
        # Format transaction attributes
        trans_merged['date_id'] = trans_merged['order_purchase_timestamp'].apply(lambda x: int(x.strftime("%Y%m%d")))
        trans_merged['quantity'] = 1
        trans_merged['unit_price'] = trans_merged['price']
        trans_merged['discount_applied'] = 0.0  # Olist baseline price
        trans_merged['total_amount'] = trans_merged['price']
        
        # Calculate actual delivery durations
        trans_merged['delivery_days'] = (trans_merged['order_delivered_customer_date'] - trans_merged['order_purchase_timestamp']).dt.days
        trans_merged['delivery_days'] = trans_merged['delivery_days'].apply(lambda x: x if x >= 0 else None)
        
        # Drop entries where customer_unique_id is missing (insignificant edge-cases in raw data)
        trans_merged = trans_merged[trans_merged['customer_unique_id'].notna()]
        
        # Select target columns matching database warehouse schema
        fact_transactions = trans_merged[[
            'customer_unique_id', 'product_id', 'date_id', 'quantity', 
            'unit_price', 'discount_applied', 'total_amount', 'delivery_days'
        ]]
        fact_transactions.rename(columns={'customer_unique_id': 'customer_id'}, inplace=True)
        
        # Clean up entries referencing keys missing from dimensions to preserve foreign key checks
        active_customer_ids = set(dim_customers_final['customer_id'])
        active_product_ids = set(dim_products_final['product_id'])
        
        fact_transactions_final = fact_transactions[
            fact_transactions['customer_id'].isin(active_customer_ids) & 
            fact_transactions['product_id'].isin(active_product_ids)
        ].copy()
        
        # --- F. DB Ingestion ---
        logger.info(f"Clearing old database records to enable clean Olist ingestion...")
        with engine.connect() as conn:
            # Dialect safe truncations
            if "sqlite" in str(engine.url):
                conn.execute(text("DELETE FROM fact_transactions;"))
                conn.execute(text("DELETE FROM dim_customers;"))
                conn.execute(text("DELETE FROM dim_products;"))
            else:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                conn.execute(text("TRUNCATE TABLE fact_transactions;"))
                conn.execute(text("TRUNCATE TABLE dim_customers;"))
                conn.execute(text("TRUNCATE TABLE dim_products;"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()
            
        logger.info(f"Loading {len(dim_customers_final)} unique customers into dim_customers...")
        dim_customers_final.to_sql(
            name="dim_customers",
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )
        
        logger.info(f"Loading {len(dim_products_final)} unique products into dim_products...")
        dim_products_final.to_sql(
            name="dim_products",
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )
        
        logger.info(f"Loading {len(fact_transactions_final)} order records into fact_transactions...")
        fact_transactions_final.to_sql(
            name="fact_transactions",
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )
        
        logger.info("Olist ETL Ingestion Engine completed execution successfully!")
        return True
        
    except Exception as e:
        logger.error(f"ETL pipeline run aborted due to errors: {e}")
        raise


def sanitize_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitizes transaction records by filtering out negative quantities
    and calculating the total amount spent after discounts.
    """
    # Filter out rows with negative/zero quantity
    clean_df = df[df['quantity'] > 0].copy()
    
    # Calculate custom total_amount: (quantity * unit_price) - discount_applied
    clean_df['total_amount'] = (clean_df['quantity'] * clean_df['unit_price']) - clean_df['discount_applied'].fillna(0.0)
    
    return clean_df


if __name__ == "__main__":
    run_etl()
