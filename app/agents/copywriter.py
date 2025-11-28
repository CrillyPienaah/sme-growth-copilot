from .base import BaseAgent, AgentContext
from ..schemas import BusinessProfile, GrowthGoal, ScoredExperiment
from ..logic import generate_copy


class CopywriterAgent(BaseAgent):
    """Generates marketing copy for experiments"""
    
    def __init__(self):
        super().__init__("Copywriter")
    
    async def process(
        self,
        input_data: dict,
        context: AgentContext
    ) -> str:
        """Generate campaign copy"""
        
        experiment = input_data['experiment']
        business = input_data['business']
        goal = input_data['goal']
        
        self.log_action(
            context,
            "Generating copy",
            f"For {experiment.experiment.name} on {experiment.experiment.channel}"
        )
        
        # Use existing copy generation logic
        copy = generate_copy(business, goal, experiment)
        
        # Log copy preview
        first_line = copy.split('\n')[0][:60]
        self.log_action(
            context,
            "Copy generated",
            f"Preview: {first_line}..."
        )
        
        # Store copy length for analytics
        context.metadata['copy_length'] = len(copy)
        
        return copy