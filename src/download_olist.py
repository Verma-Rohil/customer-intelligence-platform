"""
Automated Olist Dataset Downloader for Customer Intelligence Platform.
Downloads raw CSV files from a high-speed public mirror.
Author: Rohil Verma
"""

import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base Mirror URL
MIRROR_BASE_URL = "https://raw.githubusercontent.com/Mylinear/Brazilian_E_Commerce_-Public_Dataset_by_Olist/main/"

# Raw file list to download
FILES_TO_DOWNLOAD = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv"
]

# Destination path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_DIR = os.path.join(BASE_DIR, "data", "raw")

def download_dataset():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    logger.info("Initializing automated Olist dataset downloader...")
    
    success_count = 0
    for filename in FILES_TO_DOWNLOAD:
        # Source and Destination URLs
        source_url = f"{MIRROR_BASE_URL}{filename.replace(' ', '%20')}"
        dest_path = os.path.join(DEST_DIR, filename)
        
        # Check if file already exists
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            logger.info(f"File already exists (skipping): {filename}")
            success_count += 1
            continue
            
        logger.info(f"Downloading {filename} from mirror...")
        try:
            # Setup custom headers to prevent raw github connection blocks
            req = urllib.request.Request(
                source_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
            logger.info(f"Successfully downloaded: {filename}")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to download {filename} from {source_url}. Error: {e}")
            
    if success_count == len(FILES_TO_DOWNLOAD):
        logger.info("All Olist dataset files downloaded successfully!")
        return True
    else:
        logger.warning(f"Downloaded {success_count}/{len(FILES_TO_DOWNLOAD)} files. Some downloads failed.")
        return False

if __name__ == "__main__":
    download_dataset()
