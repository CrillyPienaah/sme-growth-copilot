from fastapi import FastAPI, UploadFile, File
from .schemas import PlanRequest, GrowthPlan
from .logic import build_growth_plan
from .storage import log_plan, load_plans_for_business
from .parsers import parse_csv_to_plan_request

app = FastAPI(
    title="SME Growth Co-Pilot",
    description="Enterprise agent that turns SME KPIs into a ranked growth plan.",
    version="0.1.0",
)


@app.post("/plan", response_model=GrowthPlan)
def create_plan(request: PlanRequest) -> GrowthPlan:
    """Create a growth plan and log it."""
    plan = build_growth_plan(
        business=request.business_profile,
        kpis=request.kpis,
        goal=request.goal,
    )
    log_plan(request, plan)
    return plan


@app.post("/plan/from-csv", response_model=GrowthPlan)
async def create_plan_from_csv(file: UploadFile = File(...)) -> GrowthPlan:
    """
    Upload a CSV file with business KPIs and get a growth plan.
    
    CSV should have columns like:
    - business_id, business_name, industry, region, channels
    - visits, leads, signups, purchases, revenue, retention_rate
    - goal, horizon_weeks, constraints
    
    See examples/sample_data.csv for reference format.
    """
    # Parse CSV to PlanRequest
    request = parse_csv_to_plan_request(file)
    
    # Generate plan (reuse existing logic)
    plan = build_growth_plan(
        business=request.business_profile,
        kpis=request.kpis,
        goal=request.goal,
    )
    
    # Log it
    log_plan(request, plan)
    
    return plan


@app.get("/plans/{business_id}")
def list_plans(business_id: str):
    """Return all historical plans for a business."""
    return load_plans_for_business(business_id)


@app.get("/health")
def health_check():
    return {"status": "ok"}