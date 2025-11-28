import logging
import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# --- New Imports for Database ---
from .database import engine, Base, get_db
from . import models # Import your ORM models
# ---------------------------------

# Existing Imports
from .schemas import PlanRequest, GrowthPlan as GrowthPlanSchema # Renamed for clarity
from .logic import build_growth_plan
# from .storage import log_plan, load_plans_for_business # <-- REMOVED
from .parsers import parse_csv_to_plan_request
from .orchestrator import GrowthCoPilotOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:      %(name)s - %(message)s'
)

# Feature flag for multi-agent
USE_MULTI_AGENT = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"
orchestrator = GrowthCoPilotOrchestrator() if USE_MULTI_AGENT else None


# --- DATABASE INITIALIZATION ---
# Create tables if they do not exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.error(f"Error connecting to or initializing database: {e}")
# -------------------------------


app = FastAPI(
    title="SME Growth Co-Pilot",
    description="Enterprise agent that turns SME KPIs into a ranked growth plan.",
    version="0.1.0",
)

# --- NEW UTILITY FUNCTION TO SAVE RESULTS ---

def save_plan_to_db(db: Session, request: PlanRequest, plan_result: GrowthPlanSchema):
    """Saves the generated plan and associated experiments to the PostgreSQL database."""
    
    # 1. Ensure Business Entry Exists
    business_profile = request.business_profile
    business_orm = db.query(models.Business).filter(models.Business.business_id == business_profile.business_id).first()
    
    if not business_orm:
        # Create a new business entry if it doesn't exist
        business_orm = models.Business(
            business_id=business_profile.business_id,
            name=business_profile.name,
            industry=business_profile.industry,
            tone="Professional" # Using a default, this should be part of PlanRequest eventually
        )
        db.add(business_orm)
        # db.commit() # Don't commit yet, we do it all at once later
        
    # 2. Create Growth Plan Entry
    new_plan = models.GrowthPlan(
        business_id=business_profile.business_id,
        trace_id=plan_result.trace_id,
        kpi_snapshot=plan_result.kpis.dict(), # Save Pydantic object as JSON
        revenue_opportunity=plan_result.funnel_analysis.revenue_opportunity,
        strategy_commentary=plan_result.strategy.commentary
    )
    db.add(new_plan)
    db.flush() # Flushes the plan to get the plan_id for experiments

    # 3. Create Experiment Entries
    for exp_data in plan_result.experiments:
        new_experiment = models.Experiment(
            plan_id=new_plan.plan_id,
            name=exp_data.name,
            priority_score=exp_data.priority_score,
            campaign_copy=exp_data.marketing_copy,
            status='PROPOSED'
        )
        db.add(new_experiment)
    
    # 4. Final Commit
    db.commit()
    db.refresh(new_plan)
    
    return plan_result

# --- UPDATED ENDPOINTS ---

@app.post("/plan", response_model=GrowthPlanSchema)
async def create_plan(
    request: PlanRequest, 
    db: Session = Depends(get_db) # New DB dependency
) -> GrowthPlanSchema:
    """Create a growth plan and log it to the database."""
    
    # 1. Execute Logic (Multi-agent or Monolithic)
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
    else:
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
    
    # 2. Save result to PostgreSQL
    return save_plan_to_db(db, request, plan)


@app.post("/plan/from-csv", response_model=GrowthPlanSchema)
async def create_plan_from_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) # New DB dependency
) -> GrowthPlanSchema:
    """Upload a CSV file with business KPIs and get a growth plan, logged to DB."""
    
    request = parse_csv_to_plan_request(file)
    
    # 1. Execute Logic (Multi-agent or Monolithic)
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
    else:
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
        
    # 2. Save result to PostgreSQL
    return save_plan_to_db(db, request, plan)


@app.get("/plans/{business_id}", response_model=List[GrowthPlanSchema])
def list_plans(business_id: str, db: Session = Depends(get_db)):
    """Return all historical plans for a business from the database."""
    
    # Retrieve all plans for the given business_id
    plans_orm = db.query(models.GrowthPlan).filter(
        models.GrowthPlan.business_id == business_id
    ).all()
    
    if not plans_orm:
        raise HTTPException(status_code=404, detail=f"No plans found for business ID: {business_id}")
    
    # Note: Converting ORM models back to your GrowthPlan Pydantic schema 
    # may require additional mapping logic depending on your schema structure.
    # For simplicity, we assume a direct conversion for now.
    # return [GrowthPlanSchema.from_orm(p) for p in plans_orm] # Use this if you set up from_orm=True on Pydantic models
    return plans_orm # Return ORM models directly (FastAPI will attempt to serialize)


@app.get("/health")
def health_check():
    return {"status": "ok"}