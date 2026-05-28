"""
K-Means Clustering Baseline

Fits a K-Means model to the customer feature matrix and assigns cluster labels.
"""

import os
import logging
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib

from src import config

logger = logging.getLogger(__name__)


def preprocess_features(df: pd.DataFrame, is_training: bool = True) -> np.ndarray:
    """
    Imputes missing values and scales features.
    Saves the scaler during training to models/scaler.joblib.
    """
    # Select numeric columns for clustering (excluding IDs and raw dates)
    exclude_cols = ['customer_id', 'signup_date', 'city_tier', 'gender', 'device_pref', 'marital_status', 'rfm_segment', 'rfm_score_concat']
    numeric_features = [col for col in df.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
    
    X = df[numeric_features].copy()
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Identify skewed features for RobustScaler, others for StandardScaler
    skewed_features = ['monetary_value_total', 'avg_order_value', 'spend_last_30d', 'max_spend_single']
    skewed_features = [f for f in skewed_features if f in numeric_features]
    standard_features = [f for f in numeric_features if f not in skewed_features]
    
    if is_training:
        logger.info(f"Training preprocessor on {len(numeric_features)} features.")
        
        skewed_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', RobustScaler())
        ])
        
        standard_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('skewed', skewed_transformer, skewed_features),
                ('standard', standard_transformer, standard_features)
            ]
        )
        
        X_scaled = preprocessor.fit_transform(X)
        
        # Save preprocessor
        os.makedirs(os.path.join(config.BASE_DIR, "models"), exist_ok=True)
        joblib.dump(preprocessor, os.path.join(config.BASE_DIR, "models", "preprocessor.joblib"))
        
    else:
        # Load preprocessor
        preprocessor = joblib.load(os.path.join(config.BASE_DIR, "models", "preprocessor.joblib"))
        X_scaled = preprocessor.transform(X)
        
    return X_scaled, numeric_features

def run_kmeans_clustering(feature_matrix: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """
    Runs the K-Means clustering pipeline on the feature matrix.
    """
    logger.info(f"Running K-Means clustering with k={n_clusters}...")
    
    df = feature_matrix.copy()
    
    X_scaled, feature_names = preprocess_features(df, is_training=True)
    
    # Fit K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=config.RANDOM_SEED, n_init='auto')
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    df['cluster_id'] = cluster_labels
    
    # Save model
    joblib.dump(kmeans, os.path.join(config.BASE_DIR, "models", "kmeans_model.joblib"))
    
    logger.info(f"Clustering complete. Cluster sizes:\n{df['cluster_id'].value_counts()}")
    
    return df
