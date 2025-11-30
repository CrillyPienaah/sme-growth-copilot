import logging
import os
import uuid  # ADD THIS
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from .schemas import PlanRequest, GrowthPlan, ExperimentResultUpdate, WebhookKpiData, WebhookResponse, BusinessProfile, KpiSnapshot, GrowthGoal
from .logic import build_growth_plan
from .storage import log_plan, load_plans_for_business
from .parsers import parse_csv_to_plan_request
from .orchestrator import GrowthCoPilotOrchestrator
from .integrations.slack_notifier import slack_notifier
from .integrations.email_notifier import email_notifier

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
async def create_plan(
    request: PlanRequest,
    send_email: bool = False,
    recipient_emails: Optional[List[str]] = None
) -> GrowthPlan:
    """Create a growth plan and log it."""
    
    # Use multi-agent if enabled
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
        trace_id = str(uuid.uuid4())[:8]
    else:
        # Use monolithic logic (current system)
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
        trace_id = "monolithic"
    
    log_plan(request, plan)
    
    # Send Slack notification
    slack_notifier.send_plan_notification(plan, trace_id)
    
    # Send email notification if requested
    if send_email and recipient_emails:
        email_notifier.send_plan_email(plan, trace_id, recipient_emails)
    
    return plan


@app.post("/plan/from-csv", response_model=GrowthPlan)
async def create_plan_from_csv(file: UploadFile = File(...)) -> GrowthPlan:
    """Upload a CSV file with business KPIs and get a growth plan."""
    request = parse_csv_to_plan_request(file)
    
    # Use multi-agent if enabled
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
        trace_id = str(uuid.uuid4())[:8]
    else:
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
        trace_id = "csv-upload"
    
    log_plan(request, plan)
    
    # Send Slack notification
    slack_notifier.send_plan_notification(plan, trace_id)
    
    return plan

@app.get("/plans/{business_id}")
def list_plans(business_id: str):
    """Return all historical plans for a business."""
    return load_plans_for_business(business_id)


@app.post("/experiments/{experiment_id}/result")
def update_experiment(experiment_id: int, result: ExperimentResultUpdate):
    """Update experiment result and strategy memory if failed"""
    from .db_utils import update_experiment_result
    return update_experiment_result(experiment_id, result)

@app.post("/webhook/kpis", response_model=WebhookResponse)
async def webhook_kpis(webhook_data: WebhookKpiData):
    """
    Webhook endpoint for external systems to push KPI data and trigger plan generation.
    
    External systems can POST KPI data here to automatically generate growth plans.
    """
    try:
        # Check if business exists in database, create if needed
        from .db_utils import ensure_business_exists
        from . import models
        from .database import SessionLocal
        
        # Build business profile from webhook data
        db = SessionLocal()
        business = db.query(models.Business).filter(
            models.Business.business_id == webhook_data.business_id
        ).first()
        
        if business:
            # Use existing business data
            business_profile = BusinessProfile(
                business_id=business.business_id,
                name=business.name,
                industry=business.industry,
                region="Unknown",  # Not stored in current model
                main_channels=[],
                tone_of_voice=business.tone
            )
        elif webhook_data.business_name and webhook_data.industry:
            # Create new business from webhook data
            business_profile = BusinessProfile(
                business_id=webhook_data.business_id,
                name=webhook_data.business_name,
                industry=webhook_data.industry,
                region=webhook_data.region or "Unknown",
                main_channels=["Website"],
                tone_of_voice="professional"
            )
            ensure_business_exists(business_profile)
        else:
            db.close()
            return WebhookResponse(
                success=False,
                message="Business not found and insufficient data provided to create new business",
                errors=["Provide business_name and industry for new businesses"]
            )
        
        db.close()
        
        # Build KPI snapshot
        kpis = KpiSnapshot(
            period=webhook_data.period,
            visits=webhook_data.visits,
            leads=webhook_data.leads,
            signups=webhook_data.signups,
            purchases=webhook_data.purchases,
            revenue=webhook_data.revenue,
            retention_rate=webhook_data.retention_rate
        )
        
        # Build goal
        goal = GrowthGoal(
            objective=webhook_data.goal_objective or f"Optimize funnel for {webhook_data.business_id}",
            horizon_weeks=webhook_data.goal_horizon_weeks or 8
        )
        
        # Create plan request
        request = PlanRequest(
            business_profile=business_profile,
            kpis=kpis,
            goal=goal
        )
        
        # Generate plan
        if USE_MULTI_AGENT and orchestrator:
            plan = await orchestrator.execute_plan(request)
            trace_id = str(uuid.uuid4())[:8]
        else:
            plan = build_growth_plan(
                business=business_profile,
                kpis=kpis,
                goal=goal
            )
            trace_id = "webhook"
        
        # Log plan
        log_plan(request, plan)
        
        # Send Slack notification
        slack_notifier.send_plan_notification(plan, trace_id)
        
        return WebhookResponse(
            success=True,
            message="Growth plan generated successfully from webhook",
            plan_id=webhook_data.business_id,
            trace_id=trace_id
        )
        
    except Exception as e:
        return WebhookResponse(
            success=False,
            message="Failed to process webhook",
            errors=[str(e)]
        )

@app.post("/plan/with-email", response_model=GrowthPlan)
async def create_plan_with_email(
    request: PlanRequest,
    recipient_emails: List[str]
) -> GrowthPlan:
    """Create a growth plan and send via email."""
    
    # Use multi-agent if enabled
    if USE_MULTI_AGENT and orchestrator:
        plan = await orchestrator.execute_plan(request)
        trace_id = str(uuid.uuid4())[:8]
    else:
        plan = build_growth_plan(
            business=request.business_profile,
            kpis=request.kpis,
            goal=request.goal,
        )
        trace_id = "monolithic"
    
    log_plan(request, plan)
    
    # Send Slack notification
    slack_notifier.send_plan_notification(plan, trace_id)
    
    # Send email notification
    email_notifier.send_plan_email(plan, trace_id, recipient_emails)
    
    return plan

@app.get("/health")
def health_check():
    return {"status": "ok"}