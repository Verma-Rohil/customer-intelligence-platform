from pydantic import BaseModel, Field

class CustomerFeatures(BaseModel):
    """
    Standardized payload for all prediction endpoints.
    Requires minimum input validation.
    """
    recency_days: int = Field(..., ge=0, description="Days since last purchase")
    frequency_total: int = Field(..., ge=1, description="Total purchases completed")
    monetary_value_total: float = Field(..., ge=0.0, description="Total value spent")
    avg_order_value: float = Field(..., ge=0.0, description="Mean order spend")
    purchase_interval_avg: float | None = Field(..., description="Average days between purchases")
    basket_diversity: int = Field(..., ge=1, description="Unique categories purchased")
    discount_dependency_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of discounted orders")
    login_recency_days: int = Field(..., ge=0, description="Days since last login")
    complaint_count: int = Field(..., ge=0, description="Count of customer complaints")
    satisfaction_score_avg: float = Field(..., ge=1.0, le=5.0, description="Mean rating score")
    tenure_months: int = Field(..., ge=0, description="Customer lifespan in months")
    avg_discount_percent: float = Field(..., ge=0.0, le=100.0, description="Mean discount percentage")
    
    # We add placeholders for the rest of the features required by the pipeline for simplicity,
    # in a real scenario we might impute these or require them. 
    # For this demo, we can just pad the rest in services.py if needed, 
    # or require exactly what the models were trained on.
    
    class Config:
        json_schema_extra = {
            "example": {
                "recency_days": 14,
                "frequency_total": 9,
                "monetary_value_total": 4500.0,
                "avg_order_value": 500.0,
                "purchase_interval_avg": 18.5,
                "basket_diversity": 4,
                "discount_dependency_ratio": 0.22,
                "login_recency_days": 3,
                "complaint_count": 0,
                "satisfaction_score_avg": 4.5,
                "tenure_months": 12,
                "avg_discount_percent": 5.0
            }
        }

class CampaignSimulationRequest(BaseModel):
    segment_name: str = Field(..., description="Target segment (e.g., 'At Risk')")
    campaign_id: str = Field(..., description="ID of the campaign to simulate")
    custom_cost_override: float | None = Field(None, description="Optional override for cost per user")
