from typing import List
import json
import asyncio # <-- NEW IMPORT
from .base import BaseAgent, AgentContext
from ..schemas import BusinessProfile, GrowthGoal, FunnelInsight, GrowthExperiment
from ..logic import propose_experiments
from ..db_utils import get_business_strategy_memory


class StrategyAgent(BaseAgent):
    """Proposes growth experiments based on bottlenecks and filters them using memory."""
    
    def __init__(self):
        super().__init__("Strategy")
    
    async def process(
        self, 
        input_data: dict, 
        context: AgentContext
    ) -> List[GrowthExperiment]:
        """Generate context-aware experiments and filter against memory."""
        
        business: BusinessProfile = input_data['business']
        goal: GrowthGoal = input_data['goal']
        insight: FunnelInsight = input_data['insight']
        
        business_id = business.business_id
        
        self.log_action(
            context,
            "Proposing experiments",
            f"For {insight.from_step}→{insight.to_step} bottleneck"
        )
        
        # 1. Retrieve Strategy Memory (CORRECTED ASYNC CALL)
        # Use asyncio.to_thread to run the synchronous DB function without blocking the event loop.
        try:
            strategy_memory_json = await asyncio.to_thread(get_business_strategy_memory, business_id)
        except Exception as e:
            self.log_action(context, "DB Error", f"Failed to retrieve memory: {e}. Proceeding without memory.")
            strategy_memory_json = None
            
        # Parse the JSONB data. Default to empty if none found.
        strategy_memory = json.loads(strategy_memory_json) if strategy_memory_json else {}
        failed_experiments = strategy_memory.get('failed_experiments', [])
        
        self.log_action(
            context,
            "Memory Check",
            f"Found {len(failed_experiments)} past failed experiments to avoid."
        )

        # 2. Use existing logic to generate the initial set of experiments
        initial_experiments = propose_experiments(business, goal, insight)
        
        # 3. Filter the experiments 
        # The logic here is perfect for removing experiments whose names match failed_experiments.
        filtered_experiments = [
            exp 
            for exp in initial_experiments 
            if exp.name not in failed_experiments
        ]
        
        # Log the result of filtering
        if len(initial_experiments) > len(filtered_experiments):
            self.log_action(
                context,
                "Memory Filter Applied",
                f"Removed {len(initial_experiments) - len(filtered_experiments)} experiment(s) due to past failure."
            )
        
        self.log_action(
            context,
            "Experiments proposed",
            f"Generated {len(filtered_experiments)} filtered experiments"
        )
        
        # Store for later agents
        context.metadata['proposed_experiments'] = len(filtered_experiments)
        
        return filtered_experiments