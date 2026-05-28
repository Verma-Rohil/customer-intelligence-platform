"""
Machine Learning Pipeline Orchestrator and Retraining Script.
Author: Rohil Verma
"""

import os
import logging
import numpy as np
import pandas as pd
import joblib
from src import config
from src.clustering.rfm_scoring import apply_rfm_scoring
from src.clustering.kmeans_baseline import run_kmeans_clustering, preprocess_features
from src.models.label_generation import generate_churn_labels
from src.models.churn_prediction import train_xgboost_model
from src.models.autoencoder import train_autoencoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing complete machine learning retraining orchestration pipeline...")
    
    # 1. Load the calculated Olist customer feature matrix
    feature_matrix_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix.csv")
    if not os.path.exists(feature_matrix_path):
        raise FileNotFoundError(f"Feature matrix CSV missing at: {feature_matrix_path}. Run feature engineering first!")
        
    logger.info(f"Loading customer feature matrix from: {feature_matrix_path}")
    df = pd.read_csv(feature_matrix_path)
    logger.info(f"Successfully loaded feature matrix. Dimensions: {df.shape}")
    
    # 2. Run rule-based RFM scoring and segment labeling
    logger.info("Running Step 1: Rule-Based RFM Segmentation...")
    df_rfm = apply_rfm_scoring(df)
    
    # 3. Run unsupervised K-Means clustering (This fits and serializes 'preprocessor.joblib' and 'kmeans_model.joblib')
    logger.info("Running Step 2: Unsupervised K-Means Customer Clustering...")
    df_clustered = run_kmeans_clustering(df_rfm, n_clusters=5)
    
    # 4. Generate binary churn labels (60 days inactivity)
    logger.info("Running Step 3: Predictive Target Churn Labeling...")
    df_labeled = generate_churn_labels(df_clustered, churn_threshold_days=config.CHURN_THRESHOLD_DAYS)
    
    # 5. Train Supervised XGBoost Classifier (Using SMOTE for class imbalance, serializes 'xgb_churn_model.joblib')
    logger.info("Running Step 4: Supervised XGBoost Churn Prediction Classifier Training...")
    xgb_model, xgb_metrics, xgb_features = train_xgboost_model(df_labeled)
    logger.info(f"XGBoost Retraining Complete! ROC-AUC: {xgb_metrics['roc_auc']:.4f} | Recall: {xgb_metrics['recall']:.4f} | F1: {xgb_metrics['f1']:.4f}")
    
    # 6. Generate SHAP Summary Plot
    logger.info("Generating real-world SHAP summary plot artifact...")
    try:
        import shap
        import matplotlib.pyplot as plt
        
        # Preprocess features using the fitted preprocessor
        X_scaled, feature_names = preprocess_features(df_labeled, is_training=False)
        
        # Take a random sample of 500 users for quick SHAP calculation
        np.random.seed(config.RANDOM_SEED)
        sample_size = min(500, len(X_scaled))
        indices = np.random.choice(len(X_scaled), sample_size, replace=False)
        X_sample = X_scaled[indices]
        
        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Plot SHAP summary and customize color backgrounds
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
        plt.title("SHAP Feature Importance (Olist E-Commerce Churn)", fontsize=14, color="white", pad=15)
        plt.gcf().patch.set_facecolor('#0E1117')  # Streamlit dark bg color
        plt.gca().set_facecolor('#0E1117')
        
        os.makedirs(os.path.join(config.BASE_DIR, "plots", "modeling"), exist_ok=True)
        plot_path = os.path.join(config.BASE_DIR, "plots", "modeling", "shap_summary_plot.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight', facecolor='#0E1117')
        plt.close()
        logger.info(f"Successfully generated and saved SHAP summary plot: {plot_path}")
    except Exception as shap_err:
        logger.error(f"Failed to generate SHAP summary plot artifact: {shap_err}")
    
    # 7. Train PyTorch Autoencoder (Undercomplete bottleneck anomaly detector, serializes 'autoencoder.pth')
    logger.info("Running Step 5: PyTorch Deep Learning Autoencoder Anomaly Detector Training...")
    df_final = train_autoencoder(df_labeled, epochs=8, batch_size=256)
    
    # 8. Save the final enriched customer dataset containing clusters and anomaly scores
    final_output_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix_enriched.csv")
    df_final.to_csv(final_output_path, index=False)
    logger.info(f"Enriched feature matrix containing anomaly scores successfully written to: {final_output_path}")
    logger.info("Complete ML Retraining Pipeline executed successfully! All new models are live.")

if __name__ == "__main__":
    main()
