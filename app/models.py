from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Date, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# --- LLM MODEL FOR A/B TESTING (NEW ADDITION) ---
class LLMModel(Base):
    __tablename__ = "llm_models"

    model_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False) # e.g., 'gemini-2.5-flash', 'gpt-4o'
    provider = Column(String(50), nullable=False) # 'GOOGLE', 'OPENAI', etc.
    agent_type = Column(String(50), nullable=False) # Which agent uses it: 'JudgeAgent', 'StrategyAgent', 'CopywriterAgent'
    traffic_weight = Column(Numeric(4, 2), default=1.00, nullable=False) # e.g., 0.80 for 80% traffic
    is_active = Column(Boolean, default=True, nullable=False)
# ----------------------------------------------------


# --- API KEY MODEL (EXISTING) ---
class ApiKey(Base):
    __tablename__ = "api_keys"

    key_id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64), unique=True, nullable=False) # The actual key string (should be hashed in production)
    business_id = Column(String(50), ForeignKey("businesses.business_id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    rate_limit_per_min = Column(Integer, default=5, nullable=False) # Default rate limit (e.g., 5 plans/minute)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship to Business
    business = relationship("Business", back_populates="api_keys")

# --- BUSINESS MODEL (EXISTING) ---
class Business(Base):
    __tablename__ = "businesses"
    
    business_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=False)
    tone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    strategy_memory = Column(JSON) 

    # Relationship to Growth Plans (existing)
    plans = relationship("GrowthPlan", back_populates="business")
    
    # Relationship to API Keys (existing)
    api_keys = relationship("ApiKey", back_populates="business")

# --- GROWTH PLAN MODEL (EXISTING) ---
class GrowthPlan(Base):
    __tablename__ = "growth_plans"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(50), ForeignKey("businesses.business_id"), nullable=False)
    trace_id = Column(String(100), unique=True, nullable=False)
    kpi_snapshot = Column(JSON, nullable=False)
    revenue_opportunity = Column(Numeric(10, 2), nullable=False)
    strategy_commentary = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="plans")
    experiments = relationship("Experiment", back_populates="plan")

# --- EXPERIMENT MODEL (EXISTING) ---
class Experiment(Base):
    __tablename__ = "experiments"
    
    experiment_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("growth_plans.plan_id"), nullable=False)
    name = Column(String(255), nullable=False)
    priority_score = Column(Numeric(4, 2), nullable=False)
    campaign_copy = Column(Text)
    status = Column(String(50), default='PROPOSED', nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    observed_result = Column(JSON)
    
    # Relationship
    plan = relationship("GrowthPlan", back_populates="experiments")