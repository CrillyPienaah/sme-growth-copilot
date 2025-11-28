import uuid
from typing import Optional
from .agents.base import AgentContext
from .agents.intake import IntakeAgent
from .agents.analyst import AnalystAgent
from .agents.strategy import StrategyAgent
from .agents.scoring import ScoringAgent
from .agents.copywriter import CopywriterAgent
from .agents.judge import JudgeAgent
from .schemas import PlanRequest, GrowthPlan


class GrowthCoPilotOrchestrator:
    """Coordinates multi-agent workflow"""
    
    def __init__(self):
        # Initialize all 6 agents
        self.intake = IntakeAgent()
        self.analyst = AnalystAgent()
        self.strategist = StrategyAgent()
        self.scorer = ScoringAgent()
        self.copywriter = CopywriterAgent()
        self.judge = JudgeAgent()
        
    async def execute_plan(self, request: PlanRequest) -> GrowthPlan:
        """Execute complete multi-agent workflow"""
        
        # Create trace context
        trace_id = str(uuid.uuid4())[:8]
        context = AgentContext(trace_id)
        
        try:
            # Stage 1: Intake - Validate request
            validated_request = await self.intake.process(request, context)
            
            # Stage 2: Analyst - Diagnose funnel
            insight = await self.analyst.process(validated_request.kpis, context)
            
            # Stage 3: Strategist - Propose experiments
            experiments = await self.strategist.process({
                'business': validated_request.business_profile,
                'goal': validated_request.goal,
                'insight': insight
            }, context)
            
            # Stage 4: Scorer - Apply ICE framework
            scored = await self.scorer.process(experiments, context)
            
            # Stage 5: Judge - Select winner
            winner = await self.judge.select_winner(scored, context)
            
            # Stage 6: Copywriter - Generate copy
            copy = await self.copywriter.process({
                'experiment': winner,
                'business': validated_request.business_profile,
                'goal': validated_request.goal
            }, context)
            
            # Assemble plan
            plan = GrowthPlan(
                business_profile=validated_request.business_profile,
                kpis=validated_request.kpis,
                goal=validated_request.goal,
                funnel_insight=insight,
                experiments=scored,
                chosen_experiment=winner,
                copy_suggestion=copy,
            )
            
            # Stage 7: Judge - Generate strategy commentary
            plan.llm_strategy_commentary = await self.judge.generate_commentary(plan, context)
            
            return plan
            
        except Exception as e:
            context.log_step("Orchestrator", "ERROR", str(e))
            raise