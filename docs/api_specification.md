# API Specification Document
## Customer Intelligence & Retention Platform

| Field | Value |
| :--- | :--- |
| **Document Owner** | Rohil Verma |
| **Version** | 1.0 |
| **Created** | 2026-05-27 |
| **Status** | Approved for Development |
| **Framework** | FastAPI 0.110+ |
| **Base URL** | `http://localhost:8000` |

---

## Table of Contents
1. [API Architecture & Conventions](#1-api-architecture--conventions)
2. [Pydantic Validation Schemas](#2-pydantic-validation-schemas)
3. [Endpoint Specifications](#3-endpoint-specifications)
4. [Error Handling & Response Codes](#4-error-handling--response-codes)
5. [Inference Latency & Testing Commands](#5-inference-latency--testing-commands)

---

# 1. API Architecture & Conventions

The platform uses a RESTful API built with FastAPI. It handles prediction requests, calculates SHAP explainability, runs campaign simulations, and serves metrics.

```
       [Client (Streamlit / cURL)]
                    |
                    v  JSON Payloads via HTTP
       +----------------------------+
       |       FastAPI Server       |
       +----------------------------+
         /health          (Get status)
         /model-info      (Get model details)
         /segment         (Layer 1 & 2 predictions)
         /predict-churn   (Layer 3 prediction + SHAP)
         /simulate-campaign(ROI calculations)
```

### Protocol Conventions
*   **Format**: Requests and responses use standard JSON (`application/json`).
*   **Status Codes**:
    - `200 OK`: Successful request.
    - `400 Bad Request`: Validation failure or malformed payload.
    - `422 Unprocessable Entity`: Request body parser validation failure (Pydantic level).
    - `500 Internal Server Error`: Server-side model error.

---

# 2. Pydantic Validation Schemas

To ensure type safety and data integrity, all endpoints validate inputs using Pydantic models.

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class CustomerFeatures(BaseModel):
    recency_days: int = Field(..., ge=0, description="Days since last purchase")
    frequency_total: int = Field(..., ge=1, description="Total purchases completed")
    monetary_value_total: float = Field(..., ge=0.0, description="Total value spent")
    avg_order_value: float = Field(..., ge=0.0, description="Mean order spend")
    purchase_interval_days: float = Field(..., ge=0.0, description="Average days between purchases")
    basket_diversity: int = Field(..., ge=1, description="Unique categories purchased")
    discount_dependency_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of discounted orders")
    login_recency_days: int = Field(..., ge=0, description="Days since last login")
    complaint_count: int = Field(..., ge=0, description="Count of customer complaints")
    satisfaction_score_avg: float = Field(..., ge=1.0, le=5.0, description="Mean rating score")
    tenure_months: int = Field(..., ge=0, description="Customer lifespan in months")
    avg_discount_percent: float = Field(..., ge=0.0, le=100.0, description="Mean discount percentage")

    @field_validator('avg_order_value')
    def validate_aov(cls, v, values):
        # Business logic validation
        return v
```

---

# 3. Endpoint Specifications

### 3.1 `GET /health`
*   **Description**: Checks if the API service is active and the serialized model weights are successfully loaded into memory.
*   **Response (200 OK)**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-05-27T16:27:51Z"
}
```

### 3.2 `GET /model-info`
*   **Description**: Exposes metadata about the loaded churn classifier, including performance metrics recorded during training.
*   **Response (200 OK)**:
```json
{
  "model_type": "XGBoost Classifier",
  "version": "v1.0",
  "training_date": "2026-05-20",
  "training_samples": 85000,
  "metrics": {
    "roc_auc": 0.92,
    "f1_score": 0.82,
    "precision": 0.81,
    "recall": 0.83
  }
}
```

### 3.3 `POST /segment`
*   **Description**: Assigns a customer profile to an RFM segment and a behavioral cluster.
*   **Request Body**:
```json
{
  "recency_days": 14,
  "frequency_total": 9,
  "monetary_value_total": 4500.0,
  "avg_order_value": 500.0,
  "purchase_interval_days": 18.5,
  "basket_diversity": 4,
  "discount_dependency_ratio": 0.22,
  "login_recency_days": 3,
  "complaint_count": 0,
  "satisfaction_score_avg": 4.5,
  "tenure_months": 12,
  "avg_discount_percent": 5.0
}
```
*   **Response (200 OK)**:
```json
{
  "rfm_scores": {
    "recency": 4,
    "frequency": 4,
    "monetary": 3
  },
  "rfm_segment": "Loyal Customers",
  "behavioral_cluster": 2,
  "cluster_label": "High-Value Frequent Shoppers",
  "cluster_description": "Frequent buyers with low discount sensitivity and high average spend."
}
```

### 3.4 `POST /predict-churn`
*   **Description**: Calculates the churn probability for a customer profile and returns local SHAP explainability values and a recommended business action.
*   **Request Body**: (Same feature payload as `/segment`)
*   **Response (200 OK)**:
```json
{
  "churn_probability": 0.78,
  "risk_level": "HIGH",
  "recommended_action": "Flat discount (20%) + Personal outreach call",
  "top_risk_factors": [
    {
      "feature": "login_recency_days",
      "shap_value": 0.24,
      "direction": "increases_risk"
    },
    {
      "feature": "complaint_count",
      "shap_value": 0.18,
      "direction": "increases_risk"
    },
    {
      "feature": "satisfaction_score_avg",
      "shap_value": -0.12,
      "direction": "reduces_risk"
    }
  ]
}
```

### 3.5 `POST /simulate-campaign`
*   **Description**: Estimates campaign ROI for a targeted customer segment.
*   **Request Body**:
```json
{
  "segment_name": "At Risk",
  "campaign_id": "C1",
  "custom_cost_override": null
}
```
*   **Response (200 OK)**:
```json
{
  "segment_name": "At Risk",
  "segment_size": 1500,
  "campaign_name": "Flat discount (20%)",
  "cost_per_user": 500.0,
  "total_campaign_cost": 750000.0,
  "assumed_churn_reduction": 0.30,
  "customers_saved": 450,
  "avg_clv": 5200.0,
  "revenue_saved": 2340000.0,
  "roi_percent": 212.00,
  "recommendation": "PROCEED — Strong positive ROI projected."
}
```

---

# 4. Error Handling & Response Codes

The API returns standardized JSON responses when error states or validation failures occur.

### 4.1 Schema Validation Failure (HTTP 422)
Returned when a request payload fails Pydantic type checks.
*   **Response**:
```json
{
  "detail": [
    {
      "loc": ["body", "discount_dependency_ratio"],
      "msg": "Input should be less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### 4.2 Resource Exception (HTTP 400)
Returned when invalid parameters are passed to the endpoints (e.g., an unsupported campaign ID).
*   **Response**:
```json
{
  "detail": "Campaign ID 'C99' is not supported in the database."
}
```

---

# 5. Inference Latency & Testing Commands

To comply with our non-functional requirements, single-record classification requests must complete in under **500 milliseconds**.

### Performance Optimization Actions
1.  **Explainer Optimization**: We pass a pre-calculated background dataset of 100 centroids to the `SHAP TreeExplainer` on startup. This prevents the API from recalculating the background dataset during inference.
2.  **Thread Pool Isolation**: We use asynchronous endpoint definitions (`async def`) for database read/write actions, and offload CPU-bound inference calculations (XGBoost and PyTorch evaluations) to executor threads.

### cURL Verification Commands
Use these commands to test endpoint health and responses:

```bash
# Verify Service Health
curl -X GET http://localhost:8000/health

# Test Churn Prediction
curl -X POST http://localhost:8000/predict-churn \
  -H "Content-Type: application/json" \
  -d '{
    "recency_days": 45,
    "frequency_total": 2,
    "monetary_value_total": 1000.00,
    "avg_order_value": 500.00,
    "purchase_interval_days": 12.0,
    "basket_diversity": 1,
    "discount_dependency_ratio": 0.90,
    "login_recency_days": 25,
    "complaint_count": 2,
    "satisfaction_score_avg": 2.1,
    "tenure_months": 3,
    "avg_discount_percent": 20.0
  }'
```
---
> [!IMPORTANT]
> The automated Swagger documentation is available locally at `http://localhost:8000/docs`. All Pydantic request models and schemas are auto-synchronized with the Swagger page on start.
