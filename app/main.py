from fastapi import FastAPI
from .schemas import PlanRequest, GrowthPlan
from .logic import build_growth_plan
from .storage import log_plan, load_plans_for_business

app = FastAPI(
    title="SME Growth Co-Pilot",
    description="Enterprise agent that turns SME KPIs into a ranked growth plan.",
    version="0.1.0",
)


@app.post("/plan", response_model=GrowthPlan)
def create_plan(request: PlanRequest) -> GrowthPlan:
    """Create a growth plan and log it."""
    plan = build_growth_plan(
        business=request.business_profile,  # ✅ this name must match PlanRequest
        kpis=request.kpis,
        goal=request.goal,
    )
    log_plan(request, plan)
    return plan


@app.get("/plans/{business_id}")
def list_plans(business_id: str):
    """Return all historical plans for a business."""
    return load_plans_for_business(business_id)


@app.get("/health")
def health_check():
    return {"status": "ok"}
