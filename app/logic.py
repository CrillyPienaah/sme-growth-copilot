from typing import List

from .schemas import (
    BusinessProfile,
    GrowthGoal,
    KpiSnapshot,
    FunnelInsight,
    GrowthExperiment,
    ScoredExperiment,
    GrowthPlan,
)
from .llm_strategy import generate_strategy_commentary


def _conversion(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / float(denominator)


def diagnose_funnel(kpis: KpiSnapshot) -> FunnelInsight:
    """Find the biggest drop-off in the simple visits→leads→signups→purchases funnel."""

    visit_to_lead = _conversion(kpis.leads, kpis.visits)
    lead_to_signup = _conversion(kpis.signups, kpis.leads)
    signup_to_purchase = _conversion(kpis.purchases, kpis.signups)

    steps = [
        ("visits", "leads", visit_to_lead),
        ("leads", "signups", lead_to_signup),
        ("signups", "purchases", signup_to_purchase),
    ]

    from_step, to_step, conversion = min(steps, key=lambda x: x[2])
    drop_rate = 1.0 - conversion

    comment = (
        f"Biggest drop is from {from_step} to {to_step}: "
        f"conversion={conversion:.1%}, drop={drop_rate:.1%}."
    )

    return FunnelInsight(
        from_step=from_step,
        to_step=to_step,
        drop_rate=drop_rate,
        comment=comment,
    )


def propose_experiments(
    business: BusinessProfile,
    goal: GrowthGoal,
    insight: FunnelInsight,
) -> List[GrowthExperiment]:
    """Very simple rule-based experiment generator.

    Later we can let a Gemini agent propose experiments, but this keeps
    the system deterministic and easy to test.
    """
    exps: List[GrowthExperiment] = []

    bottleneck = (insight.from_step, insight.to_step)

    if bottleneck == ("visits", "leads"):
        exps.append(
            GrowthExperiment(
                name="Lead Magnet Landing Page",
                channel="website",
                hypothesis=(
                    "A focused landing page with a clear lead magnet will "
                    "convert more visitors into captured leads."
                ),
                description=(
                    "Launch a simple landing page offering a freebie or "
                    "discount in exchange for email sign-up."
                ),
            )
        )
        exps.append(
            GrowthExperiment(
                name="Referral Program",
                channel="email",
                hypothesis=(
                    "Existing customers will refer similar customers when given "
                    "a clear, simple reward."
                ),
                description=(
                    "Introduce a 'Give $5, Get $5' referral link in receipts "
                    "and follow-up emails."
                ),
            )
        )

    elif bottleneck == ("leads", "signups"):
        exps.append(
            GrowthExperiment(
                name="Onboarding Nurture Sequence",
                channel="email",
                hypothesis=(
                    "A short, value-packed email sequence will turn more leads "
                    "into account signups."
                ),
            )
        )
        exps.append(
            GrowthExperiment(
                name="Live Demo / Taster Session",
                channel="events",
                hypothesis=(
                    "Low-friction live demos reduce uncertainty and increase "
                    "signup conversions."
                ),
            )
        )

    else:  # ("signups", "purchases") or anything else
        exps.append(
            GrowthExperiment(
                name="Loyalty Punch Card",
                channel="in-store",
                hypothesis=(
                    "Rewarding repeat visits with a punch card will increase "
                    "purchase frequency."
                ),
            )
        )
        exps.append(
            GrowthExperiment(
                name="Win-Back Campaign",
                channel="email",
                hypothesis=(
                    "Targeted offers to lapsed customers will reactivate a "
                    "portion of them."
                ),
            )
        )

    if not exps:
        # Fallback safety net
        exps.append(
            GrowthExperiment(
                name="Customer Feedback Survey",
                channel="email",
                hypothesis=(
                    "Understanding customer friction points will reveal the "
                    "highest-leverage growth opportunities."
                ),
            )
        )

    return exps


def score_experiments_ice(experiments: List[GrowthExperiment]) -> List[ScoredExperiment]:
    """Assign simple ICE scores (Impact, Confidence, Effort)."""

    scored: List[ScoredExperiment] = []

    for exp in experiments:
        name = exp.name.lower()
        channel = exp.channel.lower()

        # Default scores for unmatched experiments
        impact = 4
        confidence = 3

        # Adjust scores based on experiment type
        if "referral" in name:
            impact, confidence = 5, 3
        elif "loyalty" in name or "punch card" in name:
            impact, confidence = 4, 4
        elif "win-back" in name or "winback" in name:
            impact, confidence = 4, 3
        elif "onboarding" in name or "nurture" in name:
            impact, confidence = 5, 4
        elif "demo" in name or "live" in name:
            impact, confidence = 4, 3
        elif "lead magnet" in name or "landing page" in name:
            impact, confidence = 5, 4
        elif "feedback" in name or "survey" in name:
            impact, confidence = 3, 5

        # Effort heuristic: email < website < in-store/events
        if channel == "email":
            effort = 2
        elif channel in {"website", "online"}:
            effort = 3
        else:
            effort = 4

        priority_score = (impact * confidence) / float(effort)

        scored.append(
            ScoredExperiment(
                experiment=exp,
                impact=impact,
                confidence=confidence,
                effort=effort,
                priority_score=priority_score,
            )
        )

    scored.sort(key=lambda s: s.priority_score, reverse=True)
    return scored


def generate_copy(
    business: BusinessProfile,
    goal: GrowthGoal,
    experiment: ScoredExperiment,
) -> str:
    """Deterministic copy stub (we'll swap to Gemini later)."""
    exp = experiment.experiment

    if exp.channel == "email":
        return (
            f"Subject: A thank-you from {business.name}\n\n"
            f"Hi there,\n\n"
            f"We're testing a new campaign called '{exp.name}' to help us "
            f"{goal.objective}. We'd love for you to be part of it.\n\n"
            f"Thanks for being part of the {business.name} community,\n"
            f"{business.name}"
        )

    return (
        f"{exp.name} – a {exp.channel} experiment designed to help "
        f"{business.name} {goal.objective}."
    )


def build_growth_plan(
    business: BusinessProfile,
    kpis: KpiSnapshot,
    goal: GrowthGoal,
) -> GrowthPlan:
    """Top-level orchestration for the non-LLM version of the agent."""
    funnel_insight = diagnose_funnel(kpis)
    experiments = propose_experiments(business, goal, funnel_insight)
    scored = score_experiments_ice(experiments)
    chosen = scored[0]
    copy = generate_copy(business, goal, chosen)

    plan = GrowthPlan(
        business_profile=business,
        kpis=kpis,
        goal=goal,  # 👈 ADDED THIS
        funnel_insight=funnel_insight,
        experiments=scored,
        chosen_experiment=chosen,
        copy_suggestion=copy,
    )
    
    # Ask the LLM to add a strategy commentary
    plan.llm_strategy_commentary = generate_strategy_commentary(plan)
    
    return plan