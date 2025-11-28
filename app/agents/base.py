from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AgentContext:
    """Context passed between agents"""
    
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def log_step(self, agent_name: str, action: str, data: Any):
        """Log what each agent did"""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': action,
            'data': str(data)[:200]  # Truncate for logging
        })


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def process(self, input_data: Any, context: AgentContext) -> Any:
        """Each agent must implement this"""
        pass
    
    def log_action(self, context: AgentContext, action: str, data: Any):
        """Convenience logging method"""
        self.logger.info(f"[{context.trace_id}] {self.name}: {action}")
        context.log_step(self.name, action, data)