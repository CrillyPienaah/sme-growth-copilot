from typing import List
from .base import BaseAgent, AgentContext
from ..schemas import BusinessProfile, GrowthGoal, FunnelInsight, GrowthExperiment
from ..logic import propose_experiments


class StrategyAgent(BaseAgent):
    """Proposes growth experiments based on bottlenecks"""
    
    def __init__(self):
        super().__init__("Strategy")
    
    async def process(
        self, 
        input_data: dict, 
        context: AgentContext
    ) -> List[GrowthExperiment]:
        """Generate context-aware experiments"""
        
        business = input_data['business']
        goal = input_data['goal']
        insight = input_data['insight']
        
        self.log_action(
            context,
            "Proposing experiments",
            f"For {insight.from_step}→{insight.to_step} bottleneck"
        )
        
        # Use existing logic
        experiments = propose_experiments(business, goal, insight)
        
        self.log_action(
            context,
            "Experiments proposed",
            f"Generated {len(experiments)} experiments"
        )
        
        # Store for later agents
        context.metadata['proposed_experiments'] = len(experiments)
        
        return experiments