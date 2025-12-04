import os
from typing import List

from google import genai

from .schemas import GrowthPlan


# Environment variable name for your key
_API_ENV_VAR = "GOOGLE_API_KEY"

_api_key = os.getenv(_API_ENV_VAR)
_client = genai.Client(api_key=_api_key) if _api_key else None

_SYSTEM_PROMPT = """
You are a McKinsey-level growth strategist specializing in SME scale-up strategies. Your analyses have helped 200+ businesses achieve 3-5x revenue growth.

Write an executive strategic brief that a business owner can immediately implement. Be direct, specific, and results-focused.

STRUCTURE YOUR RESPONSE IN EXACTLY 3 SECTIONS:

---

**I. STRATEGIC DIAGNOSIS**

Begin: "Your growth is constrained by [specific bottleneck]."

Analyze the root cause using their actual data. Quantify the financial impact. Explain the market dynamics or operational factors creating this bottleneck. Reference their industry, geography, and competitive context.

Keep this section: 120-150 words.

---

**II. RECOMMENDED STRATEGY & RATIONALE**

Begin: "The highest-leverage intervention is [experiment name]."

Explain the strategic logic:
• Why this approach addresses the root cause (not just symptoms)
• How it aligns with their constraints (budget, time, resources)
• Why this outperforms alternative approaches in their specific context
• What business model dynamics make this scalable

Reference proven growth frameworks (viral coefficient, customer acquisition economics, retention cohorts) in plain language.

Keep this section: 150-180 words.

---

**III. 90-DAY EXECUTION BLUEPRINT**

Provide a tactical roadmap:

**Days 1-30 (Foundation):**
List 3-4 specific setup actions with exact channels, tools, or messaging.

**Days 31-60 (Optimization):**
Define key metrics to track. State decision criteria for pivots. Provide conservative vs. optimistic outcome ranges.

**Days 61-90 (Scale):**
Explain how to compound early wins. Include next-phase experiments to stack on this foundation.

End with: "Conservative outcome: [X]. Optimistic outcome: [Y]. Break-even point: [Z]."

Keep this section: 130-160 words.

---

TONE: Executive strategy memo, not marketing fluff. Data-driven, decisive, actionable.
TOTAL LENGTH: 400-490 words
FORMAT: Use markdown headers (##) and bullet points for readability.
""".strip()


def generate_strategy_commentary(plan: GrowthPlan) -> str:
    """
    Use Gemini to generate executive-level strategic commentary.
    Falls back to a simple deterministic explanation if no API key is set.
    """
    chosen = plan.chosen_experiment

    # Fallback message
    fallback_message = (
        f"## Strategic Recommendation\n\n"
        f"**Priority:** {chosen.experiment.name}\n\n"
        f"**Channel:** {chosen.experiment.channel}\n\n"
        f"**Rationale:** This experiment best addresses the '{plan.funnel_insight.from_step} → "
        f"{plan.funnel_insight.to_step}' bottleneck while aligning with your goal: {plan.goal.objective}.\n\n"
        f"**Hypothesis:** {chosen.experiment.hypothesis}\n\n"
        f"**Next Steps:** Implement this experiment within {plan.goal.horizon_weeks} weeks to unlock "
        f"the identified revenue opportunity."
    )

    # Fallback if no API key configured
    if _client is None:
        print("⚠️ No GOOGLE_API_KEY found - using fallback strategy")
        return fallback_message

    # Safe helper functions
    def safe_pct(numerator, denominator, default=0):
        """Safely calculate percentage, handling None and zero division."""
        if numerator is None or denominator is None or denominator == 0:
            return default
        return (numerator / denominator) * 100

    def safe_val(value, default=0):
        """Return value or default if None."""
        return value if value is not None else default

    # Build safe metrics
    visits = safe_val(plan.kpis.visits)
    leads = safe_val(plan.kpis.leads)
    signups = safe_val(plan.kpis.signups)
    purchases = safe_val(plan.kpis.purchases)
    revenue = safe_val(plan.kpis.revenue)
    retention_rate = safe_val(plan.kpis.retention_rate)

    lead_conversion = safe_pct(leads, visits)
    signup_conversion = safe_pct(signups, leads)
    purchase_conversion = safe_pct(purchases, signups)
    avg_customer_value = safe_val(revenue / purchases if purchases > 0 else 0)

    # Calculate revenue opportunity
    lost_customers = 0
    current_step = plan.funnel_insight.from_step.lower()
    next_step = plan.funnel_insight.to_step.lower()
    
    if current_step == "visits" and next_step == "leads":
        lost_customers = visits - leads
    elif current_step == "leads" and next_step == "signups":
        lost_customers = leads - signups
    elif current_step == "signups" and next_step == "purchases":
        lost_customers = signups - purchases
    
    revenue_opportunity = lost_customers * avg_customer_value

    experiments_summary = "\n".join(
        f"{i+1}. {se.experiment.name} ({se.experiment.channel}) - ICE Score: {se.priority_score:.1f} "
        f"(I:{se.impact}, C:{se.confidence}, E:{se.effort})"
        for i, se in enumerate(plan.experiments[:5])  # Top 5 only
    )

    prompt = f"""
BUSINESS CONTEXT:
Company: {plan.business_profile.name}
Industry: {plan.business_profile.industry}
Location: {plan.business_profile.region}
Primary Channels: {', '.join(plan.business_profile.main_channels)}
Target Market: {plan.business_profile.target_audience or 'General consumer market'}

CURRENT PERFORMANCE (30-DAY SNAPSHOT):
• Website Traffic: {visits:,} visitors
• Lead Capture: {leads:,} leads ({lead_conversion:.1f}% conversion rate)
• Account Signups: {signups:,} ({signup_conversion:.1f}% from leads)
• Completed Purchases: {purchases:,} ({purchase_conversion:.1f}% from signups)
• Total Revenue: ${revenue:,.2f}
• Average Order Value: ${avg_customer_value:.2f}
• Customer Retention: {retention_rate*100:.0f}%

CRITICAL BOTTLENECK IDENTIFIED:
Stage: {plan.funnel_insight.from_step} → {plan.funnel_insight.to_step}
Drop Rate: {plan.funnel_insight.drop_rate*100:.1f}%
Lost Customers: {lost_customers:,} potential buyers
Revenue at Stake: ${revenue_opportunity:,.2f}

Technical Finding: {plan.funnel_insight.comment}

BUSINESS OBJECTIVE:
{plan.goal.objective}
Timeline: {plan.goal.horizon_weeks} weeks
Constraints: {plan.goal.constraints or 'Standard operating budget and resources'}

PRIORITIZED EXPERIMENTS (ICE Framework):
{experiments_summary}

YOUR RECOMMENDED STRATEGY:
Experiment: {chosen.experiment.name}
Channel: {chosen.experiment.channel}
Hypothesis: {chosen.experiment.hypothesis}
Priority Score: {chosen.priority_score:.1f}/10
Expected Impact: {chosen.impact}/5 (High revenue potential)
Implementation Confidence: {chosen.confidence}/5
Resource Requirement: {chosen.effort}/5

---

Generate a 400-word executive strategic brief following the 3-section structure in your system prompt. Use their specific numbers. Be concrete, actionable, and professional.
""".strip()

    try:
        print(f"🤖 Calling Gemini API for strategy commentary...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        response = _client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 1024,
            }
        )
        
        text = (response.text or "").strip()
        
        # Enhanced logging
        if not text:
            print(f"⚠️ Gemini returned empty response")
            if hasattr(response, 'candidates'):
                print(f"Candidates: {response.candidates}")
            if hasattr(response, 'prompt_feedback'):
                print(f"Prompt feedback: {response.prompt_feedback}")
            return fallback_message
        
        print(f"✅ Gemini generated {len(text)} characters of strategy commentary")
        return text
        
    except Exception as e:
        # Detailed error logging
        print(f"❌ Gemini API error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return fallback_message