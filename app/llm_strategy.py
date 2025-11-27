import os
from typing import List

from google import genai

from .schemas import GrowthPlan


# Environment variable name for your key
_API_ENV_VAR = "GOOGLE_API_KEY"

_api_key = os.getenv(_API_ENV_VAR)
_client = genai.Client(api_key=_api_key) if _api_key else None

_SYSTEM_PROMPT = """
You are a senior growth strategist advising small business owners who need clear, actionable guidance.

Your task: Explain WHY the recommended experiment should be their #1 priority.

Structure your response in 3 short paragraphs (150-200 words total):

Paragraph 1 - THE PROBLEM:
Clearly state their biggest bottleneck and what it's costing them. Use specific numbers from their data.

Paragraph 2 - WHY THIS SOLUTION:
Explain why this specific experiment addresses their bottleneck better than alternatives. Connect it to their constraints and channels.

Paragraph 3 - WHAT TO EXPECT:
Describe the expected outcome, timeline, and first steps. Make it concrete and actionable.

Style guidelines:
- Write like you're talking to a busy business owner, not a marketer
- Use plain language - avoid jargon like "CAC" or "conversion funnel"
- Be specific with their business context (use their industry, region, channels)
- Sound confident but realistic - no hype
- Focus on the business logic, not the AI methodology
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

BUSINESS CONTEXT:
Name: {plan.business_profile.name}
Industry: {plan.business_profile.industry}
Location: {plan.business_profile.region}
Main channels: {', '.join(plan.business_profile.main_channels)}
Target audience: {plan.business_profile.target_audience or 'General customers'}
Current tone: {plan.business_profile.tone_of_voice or 'Professional'}

CURRENT SITUATION:
Period analyzed: {plan.kpis.period}
Traffic: {plan.kpis.visits:,} visits
Lead capture: {plan.kpis.leads:,} leads ({plan.kpis.leads/plan.kpis.visits*100:.1f}% conversion)
Signups: {plan.kpis.signups:,} ({plan.kpis.signups/plan.kpis.leads*100:.1f}% from leads)
Purchases: {plan.kpis.purchases:,} ({plan.kpis.purchases/plan.kpis.signups*100:.1f}% from signups)
Revenue: ${plan.kpis.revenue:,.2f}
Customer retention: {plan.kpis.retention_rate*100:.0f}%

BIGGEST PROBLEM:
{plan.funnel_insight.comment}
This means {int(plan.funnel_insight.drop_rate * 100)}% of potential customers are being lost at this stage.

BUSINESS GOAL:
{plan.goal.objective} within {plan.goal.horizon_weeks} weeks
Constraints: {plan.goal.constraints or 'None specified'}

ALL CANDIDATE EXPERIMENTS (ranked by priority):
{experiments_summary}

YOUR RECOMMENDED EXPERIMENT:
Name: {chosen.experiment.name}
Channel: {chosen.experiment.channel}
Hypothesis: {chosen.experiment.hypothesis}
Priority Score: {chosen.priority_score:.1f} (Impact: {chosen.impact}, Confidence: {chosen.confidence}, Effort: {chosen.effort})

Now explain to the business owner WHY this is their best first move.
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