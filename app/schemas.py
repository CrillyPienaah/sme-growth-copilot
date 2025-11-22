from typing import List, Optional
from pydantic import BaseModel, Field


class BusinessProfile(BaseModel):
    business_id: str
    name: str
    industry: str
    region: str
    main_channels: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    tone_of_voice: Optional[str] = None


class GrowthGoal(BaseModel):
    objective: str
    horizon_weeks: int = 8
    constraints: Optional[str] = None


class KpiSnapshot(BaseModel):
    period: str = "last_30_days"
    visits: int
    leads: int
    signups: int
    purchases: int
    revenue: float
    retention_rate: Optional[float] = None


class FunnelInsight(BaseModel):
    from_step: str
    to_step: str
    drop_rate: float
    comment: str


class GrowthExperiment(BaseModel):
    name: str
    channel: str
    hypothesis: str
    description: Optional[str] = None


class ScoredExperiment(BaseModel):
    experiment: GrowthExperiment
    impact: int
    confidence: int
    effort: int
    priority_score: float


class GrowthPlan(BaseModel):
    business_profile: BusinessProfile
    kpis: KpiSnapshot
    goal: GrowthGoal  # 👈 ADDED THIS FIELD
    funnel_insight: FunnelInsight
    experiments: List[ScoredExperiment]
    chosen_experiment: ScoredExperiment
    copy_suggestion: Optional[str] = None
    llm_strategy_commentary: Optional[str] = None


class PlanRequest(BaseModel):
    """Request body for the /plan endpoint."""
    business_profile: BusinessProfile
    kpis: KpiSnapshot
    goal: GrowthGoal