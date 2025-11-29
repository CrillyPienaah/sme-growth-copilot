from sqlalchemy.orm import Session
from .database import SessionLocal 
from . import models
import random
from typing import List

def select_model_for_agent(agent_name: str) -> models.LLMModel:
    """Selects an LLM model based on active traffic weights."""
    db: Session = SessionLocal()
    try:
        # 1. Fetch all active models for this agent
        active_models = db.query(models.LLMModel).filter(
            models.LLMModel.agent_type == agent_name,
            models.LLMModel.is_active == True
        ).all()
        
        if not active_models:
            raise ValueError(f"No active LLM models configured for {agent_name}.")

        # 2. Build lists for random choice weighted selection
        models_list: List[models.LLMModel] = [m for m in active_models]
        weights = [float(m.traffic_weight) for m in active_models] # Convert Decimal/Numeric to float for random.choices

        # 3. Use weighted random choice (k=1 selects one element)
        # Note: random.choices returns a list, so we take the first element [0]
        selected_model = random.choices(models_list, weights=weights, k=1)[0]
        return selected_model
        
    finally:
        db.close()