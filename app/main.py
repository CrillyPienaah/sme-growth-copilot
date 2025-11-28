import logging
import os
from fastapi import FastAPI, UploadFile, File
from .schemas import PlanRequest, GrowthPlan
from .logic import build_growth_plan
from .storage import log_plan, load_plans_for_business
from .parsers import parse_csv_to_plan_request
from .orchestrator import GrowthCoPilotOrchestrator

# Configure logging to show agent activity
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:     %(name)s - %(message)s'
)

# Feature flag for multi-agent
USE_MULTI_AGENT = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"
orchestrator = GrowthCoPilotOrchestrator() if USE_MULTI_AGENT else None


app = FastAPI(
    title="SME Growth Co-Pilot",
    description="Enterprise agent that turns SME KPIs into a ranked growth plan.",
    version="0.1.0",
)


@app.post("/plan", response_model=GrowthPlan)
async def create_plan(request: PlanRequest) -> GrowthPlan:
    """Create a growth plan and log it."""
    
    # Use multi-agent if enabled
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
    else:
        # Use monolithic logic (current system)
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
    
    log_plan(request, plan)
    return plan


@app.post("/plan/from-csv", response_model=GrowthPlan)
async def create_plan_from_csv(file: UploadFile = File(...)) -> GrowthPlan:
    """Upload a CSV file with business KPIs and get a growth plan."""
    request = parse_csv_to_plan_request(file)
    
    # Use multi-agent if enabled
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
    else:
        plan = build_growth_plan(
            business=request.business_profile,
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