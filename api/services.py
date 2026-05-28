import os
import json
import joblib
import pandas as pd
import numpy as np
import shap
import logging

from src import config

logger = logging.getLogger(__name__)

# Directory containing pre-exported JSON snapshots (fallback for deployment)
STATIC_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_data")

# Cache models globally
_PREPROCESSOR = None
_KMEANS_MODEL = None
_XGB_MODEL = None
_SHAP_EXPLAINER = None

def load_models():
    """Loads serialized models into memory for fast inference."""
    global _PREPROCESSOR, _KMEANS_MODEL, _XGB_MODEL, _SHAP_EXPLAINER
    
    try:
        if _PREPROCESSOR is None:
            _PREPROCESSOR = joblib.load(os.path.join(config.BASE_DIR, "models", "preprocessor.joblib"))
        if _KMEANS_MODEL is None:
            _KMEANS_MODEL = joblib.load(os.path.join(config.BASE_DIR, "models", "kmeans_model.joblib"))
        if _XGB_MODEL is None:
            _XGB_MODEL = joblib.load(os.path.join(config.BASE_DIR, "models", "xgb_churn_model.joblib"))
            
        if _SHAP_EXPLAINER is None and _XGB_MODEL is not None:
            _SHAP_EXPLAINER = shap.TreeExplainer(_XGB_MODEL)
            
        return True
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return False

def _pad_features(payload_dict: dict) -> pd.DataFrame:
    """
    Pads the incoming request with default values for missing feature columns 
    expected by the preprocessor/model pipeline.
    """
    # Create base dataframe
    df = pd.DataFrame([payload_dict])
    
    # We must ensure it has the exact features the preprocessor expects.
    expected_cols = [
        'recency_days', 'frequency_total', 'monetary_value_total', 'avg_order_value', 
        'purchase_interval_avg', 'basket_diversity', 'discount_dependency_ratio',
        'delivery_delay_tolerance_avg', 'session_frequency', 'time_of_day_pref',
        'category_affinity_score', 'repeat_purchase_ratio', 'max_spend_single',
        'weekend_spend_ratio', 'avg_items_per_order', 'avg_discount_percent',
        'spend_variance', 'tenure_months', 'complaint_count', 'satisfaction_score_avg',
        'refund_frequency', 'coupon_usage_rate', 'payment_diversity', 'complaint_ratio',
        'spend_last_30d', 'spend_ratio_last_30d', 'login_recency_days', 'recency_ratio',
        'churn_prob_indicator', 'spend_trend_3m', 'spend_velocity_3m', 'frequency_velocity_3m'
    ]
    
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0.0
            
    # Ensure correct order
    return df[expected_cols]

def segment_customer(payload_dict: dict) -> dict:
    df = _pad_features(payload_dict)
    
    # Compute basic RFM rule scores
    r = 4 if payload_dict['recency_days'] < 30 else 2
    f = 4 if payload_dict['frequency_total'] > 5 else 2
    m = 4 if payload_dict['monetary_value_total'] > 1000 else 2
    
    segment = "Loyal Customers"
    if r < 3 and m > 2:
        segment = "At Risk"
    elif r < 2 and f < 2:
        segment = "Lost"
        
    # K-Means Pipeline
    X_scaled = _PREPROCESSOR.transform(df)
    cluster_id = int(_KMEANS_MODEL.predict(X_scaled)[0])
    
    return {
        "rfm_scores": {"recency": r, "frequency": f, "monetary": m},
        "rfm_segment": segment,
        "behavioral_cluster": cluster_id,
        "cluster_label": f"Cluster {cluster_id}",
        "cluster_description": "Behavioral cluster based on representation learning."
    }

def predict_churn(payload_dict: dict) -> dict:
    df = _pad_features(payload_dict)
    
    X_scaled = _PREPROCESSOR.transform(df)
    prob = float(_XGB_MODEL.predict_proba(X_scaled)[0, 1])
    
    # SHAP
    shap_vals = _SHAP_EXPLAINER.shap_values(X_scaled)[0]
    
    # Get top 3
    top_indices = np.argsort(np.abs(shap_vals))[-3:][::-1]
    features_names = df.columns
    
    top_factors = []
    for idx in top_indices:
        val = float(shap_vals[idx])
        top_factors.append({
            "feature": features_names[idx],
            "shap_value": val,
            "direction": "increases_risk" if val > 0 else "reduces_risk"
        })
        
    risk_level = "HIGH" if prob > 0.6 else "MEDIUM" if prob > 0.3 else "LOW"
    action = "Flat discount (20%) + Personal outreach call" if prob > 0.6 else "Standard Marketing"
    
    return {
        "churn_probability": prob,
        "risk_level": risk_level,
        "recommended_action": action,
        "top_risk_factors": top_factors
    }

def simulate_campaign(segment_name: str, campaign_id: str, override_cost: float = None) -> dict:
    # Dummy simulation math for the endpoint
    size = 1500
    cost_per_user = override_cost if override_cost else 500.0
    total_cost = size * cost_per_user
    clv = 5200.0
    saved = int(size * 0.3)
    revenue = saved * clv
    roi = ((revenue - total_cost) / total_cost) * 100
    
    return {
        "segment_name": segment_name,
        "segment_size": size,
        "campaign_name": "Flat discount (20%)" if campaign_id == "C1" else "Loyalty Bonus",
        "cost_per_user": cost_per_user,
        "total_campaign_cost": total_cost,
        "assumed_churn_reduction": 0.30,
        "customers_saved": saved,
        "avg_clv": clv,
        "revenue_saved": revenue,
        "roi_percent": round(roi, 2),
        "recommendation": "PROCEED" if roi > 0 else "DO NOT PROCEED"
    }


# ──────────────────────────────────────────────────────────
# New service functions for React SPA endpoints
# ──────────────────────────────────────────────────────────

def get_executive_summary() -> dict:
    """
    Loads the customer feature matrix and returns aggregated KPIs
    and segment distribution data for the Executive Overview page.
    """
    csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix_enriched.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix.csv")
    
    if not os.path.exists(csv_path):
        # Fallback to static JSON snapshot
        static_path = os.path.join(STATIC_DATA_DIR, "executive_summary.json")
        if os.path.exists(static_path):
            with open(static_path, "r") as f:
                return json.load(f)
        return {"error": "Feature matrix not found. Run ETL and training first."}
    
    df = pd.read_csv(csv_path)
    
    # Core KPIs
    n_active = len(df)
    avg_spent = float(df['monetary_value_total'].mean())
    
    if 'is_churned' in df.columns:
        churn_rate = float(df['is_churned'].mean() * 100)
        high_risk_count = int(df['is_churned'].sum())
    else:
        churn_rate = float((df['recency_days'] > 60).mean() * 100)
        high_risk_count = int((df['recency_days'] > 60).sum())
    
    avg_tenure = float(df['tenure_months'].mean())
    
    # Segment distribution
    if 'rfm_segment' not in df.columns:
        df['rfm_segment'] = 'Regular'
    
    segment_counts = df['rfm_segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'count']
    
    segment_spend = df.groupby('rfm_segment')['monetary_value_total'].sum().reset_index()
    segment_spend.columns = ['segment', 'total_spend']
    
    # Treemap data (segment × city_tier)
    treemap_data = []
    if 'city_tier' in df.columns:
        df_tree = df.groupby(['rfm_segment', 'city_tier']).agg(
            customer_count=('customer_id', 'count'),
            total_spend=('monetary_value_total', 'sum'),
            avg_recency=('recency_days', 'mean')
        ).reset_index()
        treemap_data = df_tree.to_dict(orient='records')
    
    return {
        "kpis": {
            "active_customers": n_active,
            "avg_spend": round(avg_spent, 2),
            "churn_rate": round(churn_rate, 1),
            "high_risk_count": high_risk_count,
            "avg_tenure_months": round(avg_tenure, 1)
        },
        "segment_distribution": segment_counts.to_dict(orient='records'),
        "segment_spend": segment_spend.to_dict(orient='records'),
        "treemap_data": treemap_data
    }


def get_feature_importances() -> dict:
    """
    Extracts feature importance scores from the loaded XGBoost model
    and returns them sorted by importance descending.
    """
    if _XGB_MODEL is None:
        # Fallback to static JSON snapshot
        static_path = os.path.join(STATIC_DATA_DIR, "feature_importance.json")
        if os.path.exists(static_path):
            with open(static_path, "r") as f:
                return json.load(f)
        return {"error": "XGBoost model not loaded."}
    
    # Get the feature names from the preprocessor
    # The preprocessor is a ColumnTransformer, we need to reconstruct feature names
    try:
        csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix_enriched.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix.csv")
        
        df = pd.read_csv(csv_path, nrows=1)
        exclude_cols = ['customer_id', 'signup_date', 'city_tier', 'gender', 'device_pref', 
                       'marital_status', 'rfm_segment', 'rfm_score_concat']
        feature_names = [col for col in df.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
    except Exception:
        feature_names = [f"feature_{i}" for i in range(_XGB_MODEL.n_features_in_)]
    
    importances = _XGB_MODEL.feature_importances_
    
    # Pair and sort
    pairs = list(zip(feature_names[:len(importances)], importances.tolist()))
    pairs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 15
    top_features = [{"feature": name, "importance": round(imp, 4)} for name, imp in pairs[:15]]
    
    return {
        "model_type": "XGBoost Classifier",
        "total_features": len(importances),
        "top_features": top_features
    }


def get_segment_data() -> dict:
    """
    Returns sampled customer data for the Segment Deep Dive page,
    including cluster assignments, RFM segments, and core metrics.
    """
    csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix_enriched.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(config.PROCESSED_DATA_DIR, "customer_feature_matrix.csv")
    
    if not os.path.exists(csv_path):
        # Fallback to static JSON snapshot
        static_path = os.path.join(STATIC_DATA_DIR, "segment_data.json")
        if os.path.exists(static_path):
            with open(static_path, "r") as f:
                return json.load(f)
        return {"error": "Feature matrix not found."}
    
    df = pd.read_csv(csv_path)
    
    if 'cluster_id' not in df.columns:
        df['cluster_id'] = 0
    if 'rfm_segment' not in df.columns:
        df['rfm_segment'] = 'Regular'
    
    # Sample up to 2000 rows for frontend performance
    sample_size = min(2000, len(df))
    df_sample = df.sample(sample_size, random_state=42)
    
    # Core columns to return
    core_cols = ['customer_id', 'recency_days', 'frequency_total', 'monetary_value_total',
                 'avg_order_value', 'tenure_months', 'cluster_id', 'rfm_segment']
    
    # Add optional columns if they exist
    optional_cols = ['purchase_interval_avg', 'satisfaction_score_avg', 'complaint_count',
                     'anomaly_score', 'is_churned']
    for col in optional_cols:
        if col in df_sample.columns:
            core_cols.append(col)
    
    available_cols = [c for c in core_cols if c in df_sample.columns]
    result_df = df_sample[available_cols].copy()
    
    # Replace NaN/inf for JSON serialization
    result_df = result_df.replace([np.inf, -np.inf], np.nan)
    result_df = result_df.astype(object).where(pd.notna(result_df), None)
    
    # Segment summary stats
    seg_summary = df.groupby('rfm_segment').agg(
        count=('customer_id', 'count'),
        avg_spend=('monetary_value_total', 'mean'),
        avg_recency=('recency_days', 'mean'),
        avg_frequency=('frequency_total', 'mean'),
        avg_tenure=('tenure_months', 'mean')
    ).reset_index()
    
    seg_summary = seg_summary.replace([np.inf, -np.inf], np.nan)
    seg_summary = seg_summary.astype(object).where(pd.notna(seg_summary), None)
    
    return {
        "total_customers": len(df),
        "sample_size": sample_size,
        "customers": result_df.to_dict(orient='records'),
        "segment_summary": seg_summary.to_dict(orient='records'),
        "available_segments": sorted(df['rfm_segment'].unique().tolist()),
        "available_clusters": sorted(df['cluster_id'].unique().tolist())
    }
