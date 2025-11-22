import os
from typing import List

from google import genai

from .schemas import GrowthPlan


# Environment variable name for your key
_API_ENV_VAR = "GOOGLE_API_KEY"

_api_key = os.getenv(_API_ENV_VAR)
_client = genai.Client(api_key=_api_key) if _api_key else None

_SYSTEM_PROMPT = """
You are a senior growth strategist for small and medium businesses.
Given a business description, funnel bottleneck, and candidate experiments,
choose ONE experiment to prioritize first and justify it clearly.
Explain the reasoning in business terms (impact, risk, effort) and, if
you disagree with the heuristic ordering, briefly highlight why.
Keep the answer under 200 words in 2–3 short paragraphs.
""".strip()


def generate_strategy_commentary(plan: GrowthPlan) -> str:
    """
    Use Gemini to add a strategy commentary to the chosen experiment.
    Falls back to a simple deterministic explanation if no API key is set.
    """
    chosen = plan.chosen_experiment

    # Fallback message
    fallback_message = (
        f"Strategy note (no LLM): prioritize '{chosen.experiment.name}' on "
        f"{chosen.experiment.channel} because it best aligns with the goal "
        f"'{plan.goal.objective}' and addresses the "
        f"'{plan.funnel_insight.from_step} to {plan.funnel_insight.to_step}' bottleneck."
    )

    # Fallback if no API key configured
    if _client is None:
        return fallback_message

    experiments_summary = "\n".join(
        f"- {se.experiment.name} ({se.experiment.channel}) | Priority={se.priority_score:.1f}"
        for se in plan.experiments
    )

    prompt = f"""
{_SYSTEM_PROMPT}

Business: {plan.business_profile.name} ({plan.business_profile.industry}, {plan.business_profile.region})
Goal: {plan.goal.objective} over {plan.goal.horizon_weeks} weeks
Bottleneck: {plan.funnel_insight.from_step} to {plan.funnel_insight.to_step}
Insight: {plan.funnel_insight.comment}

Candidate experiments:
{experiments_summary}

Heuristic top experiment: {chosen.experiment.name} ({chosen.experiment.channel})
""".strip()

    try:
        response = _client.models.generate_content(  # 🔧 FIX: Proper indentation
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        
        text = (response.text or "").strip()
        if not text:
            return fallback_message
            
        return text
        
    except Exception as e:  # 🔧 FIX: Added error handling
        # Log the error and return fallback instead of crashing
        print(f"Gemini API error: {e}")
        return fallback_message