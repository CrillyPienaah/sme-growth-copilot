import uuid
from typing import Optional
from .agents.base import AgentContext
from .agents.intake import IntakeAgent
from .agents.analyst import AnalystAgent
from .schemas import PlanRequest, GrowthPlan, KpiSnapshot, FunnelInsight
from .logic import propose_experiments, score_experiments_ice, generate_copy
from .llm_strategy import generate_strategy_commentary


class GrowthCoPilotOrchestrator:
    """Coordinates multi-agent workflow"""
    
    def __init__(self):
        # Initialize agents
        self.intake = IntakeAgent()
        self.analyst = AnalystAgent()
        # TODO: Add other agents this weekend
        
    async def execute_plan(self, request: PlanRequest) -> GrowthPlan:
        """Execute multi-agent workflow"""
        
        # Create trace context
        trace_id = str(uuid.uuid4())[:8]  # Short trace ID for readability
        context = AgentContext(trace_id)
        
        try:
            # Stage 1: Intake - Validate request
            validated_request = await self.intake.process(request, context)
            
            # Stage 2: Analyst - Diagnose funnel
            insight = await self.analyst.process(validated_request.kpis, context)
            
            # Stage 3-6: Use existing logic for now (migrate this weekend)
            experiments = propose_experiments(
                validated_request.business_profile,
                validated_request.goal,
                insight
            )
            scored = score_experiments_ice(experiments)
            chosen = scored[0]
            copy = generate_copy(
                validated_request.business_profile,
                validated_request.goal,
                chosen
            )
            
            # Assemble plan
            plan = GrowthPlan(
                business_profile=validated_request.business_profile,
                kpis=validated_request.kpis,
                goal=validated_request.goal,
                funnel_insight=insight,
                experiments=scored,
                chosen_experiment=chosen,
                copy_suggestion=copy,
            )
            
            # Generate base commentary
            base_commentary = generate_strategy_commentary(plan)
            
            # Enhance with revenue opportunity from analyst
            if context.metadata.get('revenue_opportunity'):
                rev_opp = context.metadata['revenue_opportunity']
                base_commentary += f"\n\n💰 Revenue Opportunity: ${rev_opp:,.2f} if bottleneck is fixed"
            
            # Add trace ID for debugging
            base_commentary += f"\n[Trace: {trace_id}]"
            
            # Set final commentary
            plan.llm_strategy_commentary = base_commentary
            
            return plan
            
        except Exception as e:
            context.log_step("Orchestrator", "ERROR", str(e))
            raise
