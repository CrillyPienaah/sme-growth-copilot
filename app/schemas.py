from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Utility Configuration for ORM Conversion (Pydantic V2) ---
# Define the common settings dictionary
COMMON_MODEL_CONFIG = {
    "from_attributes": True 
}
# -------------------------------------------------------------

# --- Input Schemas ---

class BusinessProfile(BaseModel):
    business_id: str
    name: str
    industry: str
    region: str
    main_channels: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    tone_of_voice: Optional[str] = None
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


class GrowthGoal(BaseModel):
    objective: str
    horizon_weeks: int = 8
    constraints: Optional[str] = None
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


class KpiSnapshot(BaseModel):
    period: str = "last_30_days"
    visits: int
    leads: int
    signups: int
    purchases: int
    revenue: float
    retention_rate: Optional[float] = None
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


class PlanRequest(BaseModel):
    """Request body for the /plan endpoint."""
    business_profile: BusinessProfile
    kpis: KpiSnapshot
    goal: GrowthGoal


# --- Core Component Schemas ---

class FunnelInsight(BaseModel):
    from_step: str
    to_step: str
    drop_rate: float
    comment: str
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


class GrowthExperiment(BaseModel):
    name: str
    channel: str
    hypothesis: str
    description: Optional[str] = None
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


class ScoredExperiment(BaseModel):
    experiment: GrowthExperiment
    impact: int
    confidence: int
    effort: int
    priority_score: float
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


# --- Output Schema ---

class GrowthPlan(BaseModel):
    business_profile: BusinessProfile
    kpis: KpiSnapshot
    goal: GrowthGoal
    funnel_insight: FunnelInsight
    experiments: List[ScoredExperiment]
    chosen_experiment: ScoredExperiment
    copy_suggestion: Optional[str] = None
    llm_strategy_commentary: Optional[str] = None
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG


# --- NEW Feedback Loop Schema (Phase 3) ---

class ExperimentResultUpdate(BaseModel):
    """Schema for reporting the outcome of a completed experiment."""
    experiment_id: int = Field(..., description="The ID of the experiment to update (from the 'experiments' table).")
    status: str = Field(
        ..., 
        description="The final status (e.g., 'COMPLETED', 'FAILED', 'CANCELED_LOW_IMPACT')."
    )
    end_date: Optional[str] = Field(None, description="The date the experiment concluded (YYYY-MM-DD).")
    observed_result: Dict[str, Any] = Field(
        ...,
        description="The observed metrics and outcomes (e.g., {'metric': 'leads_to_signups_cr', 'change': 0.15})."
    )
    
    # CORRECT: Use model_config dictionary
    model_config = COMMON_MODEL_CONFIG