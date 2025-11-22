from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from .schemas import PlanRequest, GrowthPlan

# Data folder (will sit next to your app/)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

LOG_FILE = DATA_DIR / "plan_log.jsonl"


def log_plan(request: PlanRequest, plan: GrowthPlan) -> None:
    """Append a single request/plan pair to a JSONL log file."""
    record: Dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "business_id": request.business_profile.business_id,
        "request": request.model_dump(),
        "plan": plan.model_dump(),
    }
    
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def load_plans_for_business(business_id: str) -> List[Dict[str, Any]]:
    """Return all logged plans for a given business_id."""
    if not LOG_FILE.exists():
        return []
    
    results: List[Dict[str, Any]] = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("business_id") == business_id:
                results.append(rec)
    
    return results