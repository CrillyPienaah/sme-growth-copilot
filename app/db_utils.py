from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from typing import Optional
import json

# Assuming app.database and app.models are importable from here
from .database import SessionLocal 
from . import models
from .schemas import ExperimentResultUpdate # <-- NEW IMPORT


def get_business_strategy_memory(business_id: str) -> Optional[str]:
    """
    Retrieves the strategy_memory JSON string for a given business ID.
    (Used by StrategyAgent to filter failed experiments).
    """
    db: Session = SessionLocal()
    
    try:
        # Query the businesses table for the specific ID
        business_record = db.query(models.Business.strategy_memory).filter(
            models.Business.business_id == business_id
        ).one_or_none()
        
        if business_record and business_record.strategy_memory is not None:
            # SQLAlchemy handles JSONB mapping, returning a Python dictionary.
            # Convert Python dictionary back to JSON string for the agent to parse.
            return json.dumps(business_record.strategy_memory)
            
        return None
            
    except NoResultFound:
        return None
        
    finally:
        db.close()


def update_experiment_result(experiment_id: int, update_data: ExperimentResultUpdate):
    """
    Updates an experiment record and, if the result is a failure, updates 
    the business's strategy_memory to close the feedback loop.
    """
    db: Session = SessionLocal()
    try:
        # 1. Find the Experiment
        experiment = db.query(models.Experiment).filter(
            models.Experiment.experiment_id == experiment_id
        ).one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail=f"Experiment ID {experiment_id} not found.")

        # 2. Update Experiment Details
        experiment.status = update_data.status
        experiment.end_date = update_data.end_date
        # Store the observed result dictionary directly into the JSONB column
        experiment.observed_result = update_data.observed_result
        
        # 3. Conditional Strategy Update (The Learning Step)
        # Check for failure statuses (e.g., failed, or canceled due to zero impact)
        if update_data.status.upper() in ["FAILED", "CANCELED_LOW_IMPACT", "NO_IMPACT"]:
            
            # --- Get the Business ID via the GrowthPlan ---
            plan = db.query(models.GrowthPlan).filter(
                models.GrowthPlan.plan_id == experiment.plan_id
            ).one()
            
            business = db.query(models.Business).filter(
                models.Business.business_id == plan.business_id
            ).one()
            
            # --- Update Strategy Memory (Add failed experiment name) ---
            current_memory = business.strategy_memory if business.strategy_memory else {}
            failed_exps = current_memory.get('failed_experiments', [])
            
            # Prevent duplicate entries in the memory list
            if experiment.name not in failed_exps:
                failed_exps.append(experiment.name)
                current_memory['failed_experiments'] = failed_exps
                business.strategy_memory = current_memory # Saves the updated dictionary
                
        db.commit()
        return {"status": "success", "message": f"Experiment {experiment_id} status updated to {update_data.status}."}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {e}")
    finally:
        db.close()