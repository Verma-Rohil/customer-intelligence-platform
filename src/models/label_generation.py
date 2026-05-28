"""
Label Generation Module

Appends the target variable (is_churned) based on the standard 60-day inactivity threshold.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def generate_churn_labels(feature_matrix: pd.DataFrame, churn_threshold_days: int = 60) -> pd.DataFrame:
    """
    Creates the binary `is_churned` target label based on recency.
    1 if recency_days > threshold, else 0.
    """
    logger.info(f"Generating churn labels with threshold > {churn_threshold_days} days.")
    
    df = feature_matrix.copy()
    
    if 'recency_days' not in df.columns:
        raise ValueError("Required column 'recency_days' missing for label generation.")
        
    df['is_churned'] = (df['recency_days'] > churn_threshold_days).astype(int)
    
    churn_rate = df['is_churned'].mean()
    logger.info(f"Label generation complete. Global Churn Rate: {churn_rate:.2%}")
    
    return df
