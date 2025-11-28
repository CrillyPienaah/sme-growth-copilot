from typing import List
from .base import BaseAgent, AgentContext
from ..schemas import GrowthExperiment, ScoredExperiment
from ..logic import score_experiments_ice


class ScoringAgent(BaseAgent):
    """Scores experiments using ICE framework"""
    
    def __init__(self):
        super().__init__("Scoring")
    
    async def process(
        self,
        input_data: List[GrowthExperiment],
        context: AgentContext
    ) -> List[ScoredExperiment]:
        """Apply ICE scoring and rank by priority"""
        
        self.log_action(
            context,
            "Scoring experiments",
            f"{len(input_data)} experiments to score"
        )
        
        # Use existing ICE logic
        scored = score_experiments_ice(input_data)
        
        # Log top scores
        if scored:
            top = scored[0]
            self.log_action(
                context,
                "Scoring complete",
                f"Top: {top.experiment.name} (Priority: {top.priority_score:.1f})"
            )
            
            # Store scoring summary
            context.metadata['top_experiment'] = top.experiment.name
            context.metadata['top_priority_score'] = top.priority_score
        
        return scored