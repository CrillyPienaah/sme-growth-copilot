import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import LLMModel

Base.metadata.create_all(bind=engine)

def seed_llm_models():
    db = SessionLocal()
    
    models_to_add = [
        LLMModel(
            model_name="gemini-2.0-flash-exp",
            provider="GOOGLE",
            agent_type="JudgeAgent",
            traffic_weight=1.0,
            is_active=True
        ),
        LLMModel(
            model_name="gpt-4",
            provider="OPENAI",
            agent_type="JudgeAgent",
            traffic_weight=0.0,
            is_active=False
        ),
    ]
    
    try:
        for model in models_to_add:
            existing = db.query(LLMModel).filter(
                LLMModel.model_name == model.model_name,
                LLMModel.agent_type == model.agent_type
            ).first()
            
            if not existing:
                db.add(model)
                print(f"Added: {model.model_name} for {model.agent_type}")
        
        db.commit()
        print("LLM Models seeded!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_llm_models()
