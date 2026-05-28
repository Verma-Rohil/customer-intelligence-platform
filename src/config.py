import os
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Global Random Seed
RANDOM_SEED = 42

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# Ensure critical directories exist
for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, PLOTS_DIR,
               os.path.join(PLOTS_DIR, "eda"),
               os.path.join(PLOTS_DIR, "clustering"),
               os.path.join(PLOTS_DIR, "shap"),
               os.path.join(PLOTS_DIR, "campaign")]:
    os.makedirs(folder, exist_ok=True)

# Database Credentials
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "customer_intelligence_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Database connection URL
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Churn Target and Thresholds
CHURN_THRESHOLD_DAYS = 60
PROBABILITY_HIGH_RISK = 0.70
PROBABILITY_MEDIUM_RISK = 0.30

# Feature definitions
RFM_FEATURES = ["recency_days", "frequency_total", "monetary_value_total"]
