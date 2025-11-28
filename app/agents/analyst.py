from .base import BaseAgent, AgentContext
from ..schemas import KpiSnapshot, FunnelInsight
from ..logic import diagnose_funnel


class AnalystAgent(BaseAgent):
    """Diagnoses funnel bottlenecks"""
    
    def __init__(self):
        super().__init__("Analyst")
    
    async def process(self, input_data: KpiSnapshot, context: AgentContext) -> FunnelInsight:
        """Analyze funnel and find biggest bottleneck"""
        self.log_action(context, "Analyzing funnel", f"{input_data.visits} visits")
        
        # Use existing logic
        insight = diagnose_funnel(input_data)
        
        # Calculate additional metrics
        revenue_opportunity = self._estimate_revenue_opportunity(input_data, insight, context)
        context.metadata['revenue_opportunity'] = revenue_opportunity
        
        self.log_action(
            context, 
            "Bottleneck identified", 
            f"{insight.from_step}→{insight.to_step}: {insight.drop_rate*100:.1f}% drop"
        )
        
        return insight
    
    def _estimate_revenue_opportunity(
        self, 
        kpis: KpiSnapshot, 
        insight: FunnelInsight,
        context: AgentContext
    ) -> float:
        """Calculate potential revenue from fixing bottleneck"""
        if kpis.visits == 0:
            return 0.0
        
        # Estimate average revenue per visitor
        avg_revenue_per_visitor = kpis.revenue / kpis.visits if kpis.visits > 0 else 0
        
        # Calculate lost opportunities
        lost_customers = kpis.visits * insight.drop_rate
        
        # Potential revenue if we fix this bottleneck
        potential_revenue = lost_customers * avg_revenue_per_visitor
        
        # Log the revenue opportunity
        self.logger.info(
            f"[{context.trace_id}] Revenue opportunity: ${potential_revenue:,.2f}"
        )
        
        return round(potential_revenue, 2)