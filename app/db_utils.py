from sqlalchemy.orm import Session
from typing import List, Optional
import json
from .database import SessionLocal
from . import models
from .schemas import ExperimentResultUpdate


def get_business_strategy_memory(business_id: str) -> Optional[str]:
    """
    Retrieves the strategy_memory JSON for a business.
    
    Returns:
        JSON string of strategy memory or None
    """
    db = SessionLocal()
    try:
        business = db.query(models.Business).filter(
            models.Business.business_id == business_id
        ).first()
        
        if business and business.strategy_memory:
            return json.dumps(business.strategy_memory)
        
        return None
        
    finally:
        db.close()


def update_business_strategy_memory(
    business_id: str,
    failed_experiment_name: str
) -> dict:
    """
    Adds a failed experiment to the business's strategy memory.
    
    Args:
        business_id: Business identifier
        failed_experiment_name: Name of experiment that failed
    
    Returns:
        Updated strategy memory dict
    """
    db = SessionLocal()
    try:
        business = db.query(models.Business).filter(
            models.Business.business_id == business_id
        ).first()
        
        if not business:
            raise ValueError(f"Business {business_id} not found")
        
        # Initialize or load existing memory
        memory = business.strategy_memory or {}
        
        # Initialize failed_experiments list if needed
        if 'failed_experiments' not in memory:
            memory['failed_experiments'] = []
        
        # Add to failed list (avoid duplicates)
        if failed_experiment_name not in memory['failed_experiments']:
            memory['failed_experiments'].append(failed_experiment_name)
        
        # Update database
        business.strategy_memory = memory
        db.commit()
        
        print(f"📝 Added '{failed_experiment_name}' to failed experiments for {business_id}")
        
        return memory
        
    finally:
        db.close()


def update_experiment_result(
    experiment_id: int,
    result: ExperimentResultUpdate
) -> dict:
    """
    Records the outcome of an experiment and updates strategy memory if failed.
    
    Args:
        experiment_id: Database ID of experiment
        result: Result data (success/failure, metrics)
    
    Returns:
        Response dict
    """
    db = SessionLocal()
    try:
        # Find the experiment
        experiment = db.query(models.Experiment).filter(
            models.Experiment.experiment_id == experiment_id
        ).first()
        
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Update experiment record
        experiment.status = result.status
        experiment.observed_result = result.metrics
        
        # If experiment FAILED, add to strategy memory
        if result.status == "FAILED":
            plan = experiment.plan
            business_id = plan.business_id
            
            # Update strategy memory
            update_business_strategy_memory(business_id, experiment.name)
        
        db.commit()
        
        return {
            "experiment_id": experiment_id,
            "status": result.status,
            "message": f"Experiment result recorded. Strategy memory updated." if result.status == "FAILED" else "Experiment result recorded."
        }
        
    finally:
        db.close()
def get_db_session():
    """
    Provides a database session context manager.
    Usage:
        with get_db_session() as db:
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






def ensure_business_exists(business_profile) -> None:
    """
    Creates a business record if it doesn't exist.
    Args:
        business_profile: BusinessProfile schema object
    """
    db = SessionLocal()
    try:
        from . import models
        
        # Check if business exists
        existing = db.query(models.Business).filter(
            models.Business.business_id == business_profile.business_id
        ).first()
        
        if not existing:
            # Create new business record
            new_business = models.Business(
                business_id=business_profile.business_id,
                name=business_profile.name,
                industry=business_profile.industry,
                tone=business_profile.tone_of_voice or 'professional'
            )
            db.add(new_business)
            db.commit()
            print(f"? Created business record for {business_profile.business_id}")
    except Exception as e:
        db.rollback()
        print(f"?? Error creating business: {e}")
    finally:
        db.close()
