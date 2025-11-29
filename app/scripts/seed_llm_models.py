import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import LLMModel

# Create tables
Base.metadata.create_all(bind=engine)

def seed_llm_models():
    """Seed the database with available LLM models for each agent"""
    
    db = SessionLocal()
    
    models_to_add = [
        # JudgeAgent models (for strategy commentary)
        LLMModel(
            model_name="gemini-2.0-flash-exp",
            provider="GOOGLE",
            agent_type="JudgeAgent",
            traffic_weight=1.0,  # 100% traffic
            is_active=True
        ),
        LLMModel(
            model_name="gpt-4",
            provider="OPENAI",
            agent_type="JudgeAgent",
            traffic_weight=0.0,  # 0% traffic (disabled for now)
            is_active=False
        ),
        LLMModel(
            model_name="claude-3-5-sonnet-20241022",
            provider="ANTHROPIC",
            agent_type="JudgeAgent",
            traffic_weight=0.0,
            is_active=False
        ),
        
        # StrategyAgent models (for experiment generation)
        LLMModel(
            model_name="gemini-2.0-flash-exp",
            provider="GOOGLE",
            agent_type="StrategyAgent",
            traffic_weight=1.0,
            is_active=False  # Currently using deterministic logic
        ),
        
        # CopywriterAgent models (for marketing copy)
        LLMModel(
            model_name="gpt-4",
            provider="OPENAI",
            agent_type="CopywriterAgent",
            traffic_weight=1.0,
            is_active=False  # Currently using templates
        ),
    ]
    
    try:
        for model in models_to_add:
            # Check if exists
            existing = db.query(LLMModel).filter(
                LLMModel.model_name == model.model_name,
                LLMModel.agent_type == model.agent_type
            ).first()
            
            if not existing:
                db.add(model)
                print(f"✅ Added: {model.model_name} for {model.agent_type} ({model.provider})")
            else:
                print(f"⏭️  Exists: {model.model_name} for {model.agent_type}")
        
        db.commit()
        print(f"\n🎉 LLM Models seeded successfully!")
        print(f"=" * 60)
        print(f"Total models configured: {len(models_to_add)}")
        print(f"\nTo enable different models, update is_active and traffic_weight in database")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_llm_models()