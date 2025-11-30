import time
from typing import Optional
from contextlib import contextmanager
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from .. import models


class PerformanceTracker:
    """Track and analyze agent performance metrics"""
    
    @staticmethod
    @contextmanager
    def track_agent(
        agent_name: str,
        trace_id: str,
        business_id: Optional[str] = None
    ):
        """
        Context manager to track agent execution time and status
        
        Usage:
            with PerformanceTracker.track_agent("StrategyAgent", trace_id):
                # agent code here
                pass
        """
        start_time = time.time()
        error_msg = None
        status = "SUCCESS"
        
        try:
            yield
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)
            raise  # Re-raise the exception
        finally:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Save to database
            try:
                PerformanceTracker._save_metric(
                    agent_name=agent_name,
                    trace_id=trace_id,
                    execution_time_ms=execution_time_ms,
                    status=status,
                    error_message=error_msg,
                    business_id=business_id
                )
            except Exception as db_error:
                print(f"⚠️ Failed to save performance metric: {db_error}")
    
    @staticmethod
    def _save_metric(
        agent_name: str,
        trace_id: str,
        execution_time_ms: int,
        status: str,
        error_message: Optional[str],
        business_id: Optional[str]
    ):
        """Save performance metric to database"""
        db = SessionLocal()
        try:
            metric = models.AgentPerformance(
                trace_id=trace_id,
                agent_name=agent_name,
                execution_time_ms=execution_time_ms,
                status=status,
                error_message=error_message,
                business_id=business_id
            )
            db.add(metric)
            db.commit()
            
            # Log in test mode
            print(f"📊 {agent_name}: {execution_time_ms}ms ({status})")
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_agent_stats(agent_name: Optional[str] = None, days: int = 7) -> dict:
        """
        Get performance statistics for agents
        
        Args:
            agent_name: Specific agent name, or None for all agents
            days: Number of days to look back
            
        Returns:
            Dictionary with performance stats
        """
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = db.query(models.AgentPerformance).filter(
                models.AgentPerformance.created_at >= cutoff_date
            )
            
            if agent_name:
                query = query.filter(models.AgentPerformance.agent_name == agent_name)
            
            metrics = query.all()
            
            if not metrics:
                return {
                    "agent_name": agent_name or "all",
                    "total_executions": 0,
                    "success_rate": 0.0,
                    "avg_execution_time_ms": 0,
                    "min_execution_time_ms": 0,
                    "max_execution_time_ms": 0
                }
            
            total = len(metrics)
            successes = sum(1 for m in metrics if m.status == "SUCCESS")
            execution_times = [m.execution_time_ms for m in metrics]
            
            return {
                "agent_name": agent_name or "all",
                "total_executions": total,
                "success_rate": round((successes / total) * 100, 2),
                "avg_execution_time_ms": int(sum(execution_times) / len(execution_times)),
                "min_execution_time_ms": min(execution_times),
                "max_execution_time_ms": max(execution_times),
                "period_days": days
            }
            
        finally:
            db.close()
    
    @staticmethod
    def get_all_agents_summary(days: int = 7) -> list:
        """Get performance summary for all agents"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get distinct agent names
            agent_names = db.query(models.AgentPerformance.agent_name).filter(
                models.AgentPerformance.created_at >= cutoff_date
            ).distinct().all()
            
            summaries = []
            for (agent_name,) in agent_names:
                stats = PerformanceTracker.get_agent_stats(agent_name, days)
                summaries.append(stats)
            
            # Sort by total executions (most active first)
            summaries.sort(key=lambda x: x['total_executions'], reverse=True)
            
            return summaries
            
        finally:
            db.close()


# Singleton instance
performance_tracker = PerformanceTracker()