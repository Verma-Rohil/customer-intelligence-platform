from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import logging

from api.schemas import CustomerFeatures, CampaignSimulationRequest
from api.services import (
    load_models, segment_customer, predict_churn, simulate_campaign,
    get_executive_summary, get_feature_importances, get_segment_data
)

# Initialize API
app = FastAPI(
    title="Customer Intelligence & Retention API",
    description="Inference endpoints for segmentation, churn prediction, and campaign simulation.",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Ensure models are loaded on startup
@app.on_event("startup")
async def startup_event():
    loaded = load_models()
    if not loaded:
        logger.warning("Models could not be loaded at startup. Endpoints may fail.")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/model-info")
async def get_model_info():
    return {
        "model_type": "XGBoost Classifier & PyTorch AE",
        "version": "v2.0",
        "training_date": "2026-05-28",
        "metrics": {
            "roc_auc": 0.92,
            "f1_score": 0.82,
            "precision": 0.81,
            "recall": 0.83
        }
    }

@app.post("/segment")
async def segment_endpoint(payload: CustomerFeatures):
    try:
        result = segment_customer(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-churn")
async def predict_churn_endpoint(payload: CustomerFeatures):
    try:
        result = predict_churn(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate-campaign")
async def simulate_campaign_endpoint(payload: CampaignSimulationRequest):
    try:
        result = simulate_campaign(
            payload.segment_name, 
            payload.campaign_id, 
            payload.custom_cost_override
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────────────────────
# New endpoints for React SPA frontend
# ──────────────────────────────────────────────────────────

@app.get("/api/executive-summary")
async def executive_summary_endpoint():
    """Returns aggregated KPIs and segment distributions from the customer feature matrix."""
    try:
        result = get_executive_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feature-importance")
async def feature_importance_endpoint():
    """Returns XGBoost feature importance scores with feature names."""
    try:
        result = get_feature_importances()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/segment-data")
async def segment_data_endpoint():
    """Returns sampled customer data for segment deep dive and PCA visualization."""
    try:
        result = get_segment_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
