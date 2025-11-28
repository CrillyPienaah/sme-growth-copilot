from typing import Any
from .base import BaseAgent, AgentContext
from ..schemas import PlanRequest, KpiSnapshot


class IntakeAgent(BaseAgent):
    """Validates and structures incoming requests"""
    
    def __init__(self):
        super().__init__("Intake")
    
    async def process(self, input_data: PlanRequest, context: AgentContext) -> PlanRequest:
        """Validate and clean the request"""
        self.log_action(context, "Validating request", input_data.business_profile.business_id)
        
        # Validate KPIs
        validated_kpis = self._validate_kpis(input_data.kpis, context)
        
        # Update request with validated data
        validated_request = PlanRequest(
            business_profile=input_data.business_profile,
            kpis=validated_kpis,
            goal=input_data.goal
        )
        
        self.log_action(context, "Validation complete", "Request is valid")
        return validated_request
    
    def _validate_kpis(self, kpis: KpiSnapshot, context: AgentContext) -> KpiSnapshot:
        """Check KPI data quality"""
        warnings = []
        
        # Check for negative values
        if any([kpis.visits < 0, kpis.leads < 0, kpis.signups < 0, 
                kpis.purchases < 0, kpis.revenue < 0]):
            warnings.append("Negative values detected in KPIs")
        
        # Check for impossible ratios
        if kpis.purchases > kpis.signups:
            warnings.append(f"Impossible: {kpis.purchases} purchases > {kpis.signups} signups")
        
        if kpis.signups > kpis.leads:
            warnings.append(f"Impossible: {kpis.signups} signups > {kpis.leads} leads")
        
        if kpis.leads > kpis.visits:
            warnings.append(f"Impossible: {kpis.leads} leads > {kpis.visits} visits")
        
        # Log warnings
        if warnings:
            context.metadata['data_warnings'] = warnings
            self.logger.warning(f"[{context.trace_id}] Data quality issues: {warnings}")
        
        return kpis