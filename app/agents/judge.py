from typing import List
from .base import BaseAgent, AgentContext
from ..schemas import ScoredExperiment, GrowthPlan
from ..llm_strategy import generate_strategy_commentary


class JudgeAgent(BaseAgent):
    """Selects best experiment and explains why"""
    
    def __init__(self):
        super().__init__("Judge")
    
    async def process(
        self,
        input_data: List[ScoredExperiment],
        context: AgentContext
    ) -> ScoredExperiment:
        """Main process method - selects winner (satisfies ABC requirement)"""
        return await self.select_winner(input_data, context)
    
    async def select_winner(
        self,
        scored_experiments: List[ScoredExperiment],
        context: AgentContext
    ) -> ScoredExperiment:
        """Choose the #1 experiment to prioritize"""
        
        self.log_action(
            context,
            "Evaluating experiments",
            f"{len(scored_experiments)} candidates"
        )
        
        # Pick the highest scoring
        winner = scored_experiments[0]
        
        self.log_action(
            context,
            "Winner selected",
            f"{winner.experiment.name} (Priority: {winner.priority_score:.1f})"
        )
        
        # Store decision rationale
        context.metadata['chosen_experiment'] = winner.experiment.name
        context.metadata['selection_method'] = 'highest_ice_score'
        
        return winner
    
    async def generate_commentary(
        self,
        plan: GrowthPlan,
        context: AgentContext
    ) -> str:
        """Generate AI-powered strategy explanation"""
        
        self.log_action(
            context,
            "Generating strategy commentary",
            f"For {plan.chosen_experiment.experiment.name}"
        )
        
        # For now, use standard Gemini (multi-model support coming in Phase 4.2)
        base_commentary = generate_strategy_commentary(plan)
        context.metadata['llm_model_used'] = "GOOGLE/gemini-2.0-flash-exp"
        
        # Enhance with revenue opportunity
        if context.metadata.get('revenue_opportunity'):
            rev_opp = context.metadata['revenue_opportunity']
            base_commentary += f"\n\n💰 Revenue Opportunity: ${rev_opp:,.2f} if bottleneck is fixed"
        
        # Add data warnings
        if context.metadata.get('data_warnings'):
            warnings = context.metadata['data_warnings']
            base_commentary += f"\n\n⚠️ Data Quality Notes: {'; '.join(warnings)}"
        
        # Add trace
        base_commentary += f"\n[Trace: {context.trace_id}]"
        
        # Add model info
        if context.metadata.get('llm_model_used'):
            base_commentary += f" | Model: {context.metadata['llm_model_used']}"
        
        self.log_action(
            context,
            "Commentary complete",
            f"{len(base_commentary)} characters"
        )
        
        return base_commentary