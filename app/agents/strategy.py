import json
from typing import List
from .base import BaseAgent, AgentContext
from ..schemas import BusinessProfile, GrowthGoal, FunnelInsight, GrowthExperiment
from ..logic import propose_experiments
from ..db_utils import get_business_strategy_memory, get_db_session, ensure_business_exists


class StrategyAgent(BaseAgent):
    """Proposes growth experiments based on bottlenecks, filtered by strategy memory"""
    
    def __init__(self):
        super().__init__("Strategy")
    
    async def process(
        self, 
        input_data: dict, 
        context: AgentContext
    ) -> List[GrowthExperiment]:
        """Generate context-aware experiments, filtered by strategy memory"""
        
        business = input_data['business']
        goal = input_data['goal']
        insight = input_data['insight']
        
        self.log_action(
            context,
            "Proposing experiments",
            f"For {insight.from_step}→{insight.to_step} bottleneck"
        )

        # Ensure business record exists in database
        ensure_business_exists(business)

        # Generate initial experiments using existing logic
        experiments = propose_experiments(business, goal, insight)
        
        # Retrieve strategy memory to filter out past failures
        try:
            memory_json = get_business_strategy_memory(business.business_id)
            if memory_json:
                memory = json.loads(memory_json)
                failed_experiments = memory.get('failed_experiments', [])
                
                if failed_experiments:
                    self.log_action(
                        context,
                        "Memory Check",
                        f"Found {len(failed_experiments)} past failed experiments to avoid"
                    )
                    
                    # Filter out failed experiments
                    filtered = [
                        exp for exp in experiments
                        if exp.name not in failed_experiments
                    ]
                    
                    if len(filtered) < len(experiments):
                        removed = len(experiments) - len(filtered)
                        self.log_action(
                            context,
                            "Memory Filter Applied",
                            f"Removed {removed} previously failed experiment(s)"
                        )
                        context.metadata['experiments_filtered_by_memory'] = removed
                    
                    # Use filtered list if we still have experiments
                    experiments = filtered if filtered else experiments
        
        except Exception as e:
            # Memory retrieval is optional - don't fail if it errors
            self.log_action(context, "Memory Warning", f"Could not retrieve memory: {str(e)[:50]}")
        
        self.log_action(
            context,
            "Experiments proposed",
            f"Generated {len(experiments)} filtered experiments"
        )
        
        # Store for later agents
        context.metadata['proposed_experiments'] = len(experiments)
        
        return experiments

