from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# --- BUSINESS MODEL ---
class Business(Base):
    __tablename__ = "businesses"
    
    business_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=False)
    tone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    strategy_memory = Column(JSON) # JSONB in Postgres, mapped to JSON here

    # Relationship to Growth Plans
    plans = relationship("GrowthPlan", back_populates="business")

# --- GROWTH PLAN MODEL ---
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

# --- EXPERIMENT MODEL ---
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