import os
from typing import Optional
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models


def select_model_for_agent(agent_type: str) -> models.LLMModel:
    """
    Selects which LLM model to use for a given agent type.
    Uses traffic_weight for A/B testing between models.
    
    Args:
        agent_type: 'JudgeAgent', 'StrategyAgent', 'CopywriterAgent', etc.
    
    Returns:
        LLMModel configuration with provider and model_name
    
    Raises:
        ValueError: If no active model found for agent_type
    """
    db = SessionLocal()
    
    try:
        # Get all active models for this agent type
        active_models = db.query(models.LLMModel).filter(
            models.LLMModel.agent_type == agent_type,
            models.LLMModel.is_active == True
        ).order_by(models.LLMModel.traffic_weight.desc()).all()
        
        if not active_models:
            raise ValueError(f"No active LLM model configured for {agent_type}")
        
        # For now, return the model with highest traffic weight
        # TODO: Implement weighted random selection for true A/B testing
        selected = active_models[0]
        
        return selected
        
    finally:
        db.close()


def get_llm_client(llm_model: models.LLMModel):
    """
    Returns the appropriate LLM client based on provider.
    
    Args:
        llm_model: LLMModel configuration from database
    
    Returns:
        Initialized client (Gemini, OpenAI, or Anthropic)
    """
    provider = llm_model.provider.upper()
    
    if provider == "GOOGLE":
        from google import genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        return genai.Client(api_key=api_key)
    
    elif provider == "OPENAI":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAI(api_key=api_key)
    
    elif provider == "ANTHROPIC":
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return Anthropic(api_key=api_key)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def call_llm(llm_model: models.LLMModel, prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Universal LLM calling function that works across providers.
    
    Args:
        llm_model: LLMModel configuration
        prompt: User prompt
        system_prompt: Optional system instructions
    
    Returns:
        LLM response text
    """
    client = get_llm_client(llm_model)
    provider = llm_model.provider.upper()
    
    try:
        if provider == "GOOGLE":
            # Gemini API
            response = client.models.generate_content(
                model=llm_model.model_name,
                contents=prompt
            )
            return (response.text or "").strip()
        
        elif provider == "OPENAI":
            # OpenAI API
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=llm_model.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        elif provider == "ANTHROPIC":
            # Claude API
            response = client.messages.create(
                model=llm_model.model_name,
                max_tokens=1024,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    except Exception as e:
        # Log error and re-raise
        print(f"LLM call failed for {llm_model.model_name}: {e}")
        raise