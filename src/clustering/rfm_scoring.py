"""
Rule-Based RFM Scoring Module

Assigns deterministic labels based on Recency, Frequency, and Monetary (RFM) quantiles.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def compute_rfm_quantiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes quantile scores (1-4) for Recency, Frequency, and Monetary metrics.
    1 is worst, 4 is best.
    """
    # Recency: Lower is better (1 is highest recency days, 4 is lowest)
    # Using rank to handle identical values
    df['r_quartile'] = pd.qcut(df['recency_days'].rank(method='first'), 4, labels=[4, 3, 2, 1])
    
    # Frequency: Higher is better
    df['f_quartile'] = pd.qcut(df['frequency_total'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    
    # Monetary: Higher is better
    df['m_quartile'] = pd.qcut(df['monetary_value_total'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    
    return df

def assign_rfm_segment(row: pd.Series) -> str:
    """
    Rule-based mapping from RFM quantiles to customer segment.
    """
    # Convert categorical to int for easy boolean logic
    r = int(row['r_quartile'])
    f = int(row['f_quartile'])
    m = int(row['m_quartile'])
    
    # Champions: High Recency, High Frequency, High Monetary
    if r >= 3 and f >= 3 and m >= 3:
        return 'Champions'
        
    # Loyal Customers: Good Recency, High Frequency
    if r >= 2 and f >= 3:
        return 'Loyal Customers'
        
    # At Risk: Low Recency, High Frequency/Monetary (Lost good customers)
    if r <= 2 and (f >= 3 or m >= 3):
        return 'At Risk'
        
    # New Customers: High Recency, Low Frequency
    if r >= 3 and f <= 2:
        return 'New Customers'
        
    # Lost: Low Recency, Low Frequency, Low Monetary
    if r <= 2 and f <= 2 and m <= 2:
        return 'Lost'
        
    # Default for anything in the middle
    return 'Regular'

def apply_rfm_scoring(feature_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Applies RFM quantile scoring and segmentation to the feature matrix.
    """
    logger.info("Applying rule-based RFM scoring...")
    
    df = feature_matrix.copy()
    
    # Ensure RFM features exist
    required_cols = ['recency_days', 'frequency_total', 'monetary_value_total']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Required column {col} not found in feature matrix.")
            
    df = compute_rfm_quantiles(df)
    
    df['rfm_segment'] = df.apply(assign_rfm_segment, axis=1)
    
    # Calculate RFM Score by concatenating
    df['rfm_score_concat'] = df['r_quartile'].astype(str) + df['f_quartile'].astype(str) + df['m_quartile'].astype(str)
    
    logger.info(f"RFM Segmentation complete. Segment distribution:\n{df['rfm_segment'].value_counts()}")
    
    return df
