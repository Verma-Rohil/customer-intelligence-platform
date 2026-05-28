"""
Churn Prediction Pipeline using XGBoost
"""

import os
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold
from imblearn.over_sampling import SMOTE
from sklearn.metrics import roc_auc_score, recall_score, f1_score

from src import config
from src.clustering.kmeans_baseline import preprocess_features

logger = logging.getLogger(__name__)

def train_xgboost_model(feature_matrix: pd.DataFrame):
    """
    Trains XGBoost Churn Prediction Model using SMOTE for class imbalance.
    Returns the trained model and test set metrics.
    """
    logger.info("Starting XGBoost Churn Prediction training pipeline...")
    
    df = feature_matrix.copy()
    
    if 'is_churned' not in df.columns:
        raise ValueError("Missing 'is_churned' target column. Run label generation first.")
        
    # Scale Features
    X_scaled, feature_names = preprocess_features(df, is_training=False) # Assumes preprocessor exists
    y = df['is_churned'].values
    
    # Train-Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.20, stratify=y, random_state=config.RANDOM_SEED
    )
    
    logger.info(f"Training distribution before SMOTE: 0: {(y_train==0).sum()}, 1: {(y_train==1).sum()}")
    
    # Apply SMOTE to Training set ONLY
    smote = SMOTE(random_state=config.RANDOM_SEED)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
    
    logger.info(f"Training distribution after SMOTE: 0: {(y_train_sm==0).sum()}, 1: {(y_train_sm==1).sum()}")
    
    # Calculate scale_pos_weight based on original distribution
    scale_pos_weight = (y_train == 0).sum() / max(1, (y_train == 1).sum())
    
    # Initialize Model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=scale_pos_weight,
        random_state=config.RANDOM_SEED,
        eval_metric='auc',
        use_label_encoder=False
    )
    
    # Train
    model.fit(X_train_sm, y_train_sm)
    
    # Evaluate on Hold-out Test
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'roc_auc': roc_auc_score(y_test, y_proba),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred)
    }
    
    logger.info(f"Test Set Metrics: ROC-AUC={metrics['roc_auc']:.4f}, Recall={metrics['recall']:.4f}, F1={metrics['f1']:.4f}")
    
    # Save Model
    os.makedirs(os.path.join(config.BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model, os.path.join(config.BASE_DIR, "models", "xgb_churn_model.joblib"))
    
    return model, metrics, feature_names
