import os
import json
from typing import Optional
from ..schemas import GrowthPlan

class SlackNotifier:
    """Sends growth plan notifications to Slack"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.test_mode = os.getenv("SLACK_TEST_MODE", "true").lower() == "true"
        
        # Only import and create client if not in test mode
        if not self.test_mode and self.webhook_url:
            try:
                from slack_sdk.webhook import WebhookClient
                self.client = WebhookClient(self.webhook_url)
            except ImportError:
                print("⚠️ slack-sdk not installed, using test mode")
                self.test_mode = True
                self.client = None
        else:
            self.client = None
    
    def send_plan_notification(self, plan: GrowthPlan, trace_id: str) -> bool:
        """
        Send a formatted growth plan notification to Slack
        
        Args:
            plan: The generated growth plan
            trace_id: Unique trace ID for this plan
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        # Build the message
        blocks = self._build_message_blocks(plan, trace_id)
        
        # Test mode - just print to console
        if self.test_mode:
            print("\n" + "="*60)
            print("📢 SLACK NOTIFICATION (TEST MODE)")
            print("="*60)
            print(f"🏢 Business: {plan.business_profile.name}")
            print(f"🎯 Goal: {plan.goal.objective}")
            print(f"🔍 Bottleneck: {plan.funnel_insight.from_step} → {plan.funnel_insight.to_step}")
            print(f"📉 Drop Rate: {plan.funnel_insight.drop_rate*100:.1f}%")
            
            # Calculate revenue opportunity
            revenue_opp = plan.kpis.revenue * (1 / (1 - plan.funnel_insight.drop_rate) - 1)
            print(f"💰 Revenue Opportunity: ${revenue_opp:,.2f}")
            
            print(f"\n🎯 Top Experiment: {plan.chosen_experiment.experiment.name}")
            print(f"   Priority Score: {plan.chosen_experiment.priority_score:.1f}")
            print(f"   Impact: {plan.chosen_experiment.impact} | Confidence: {plan.chosen_experiment.confidence} | Effort: {plan.chosen_experiment.effort}")
            
            print(f"\n📊 All Experiments ({len(plan.experiments)}):")
            for i, exp in enumerate(plan.experiments[:5], 1):
                print(f"   {i}. {exp.experiment.name} (Score: {exp.priority_score:.1f})")
            
            if plan.llm_strategy_commentary:
                print(f"\n🤖 AI Commentary:")
                print(f"   {plan.llm_strategy_commentary[:200]}...")
            
            print(f"\n🔗 Trace ID: {trace_id}")
            print("="*60)
            print("✅ Slack notification sent (test mode)\n")
            return True
        
        # Real mode - send to Slack
        try:
            response = self.client.send(
                text=f"🚀 New Growth Plan for {plan.business_profile.name}",
                blocks=blocks
            )
            
            if response.status_code == 200:
                print(f"✅ Slack notification sent for trace {trace_id}")
                return True
            else:
                print(f"⚠️ Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Slack notification error: {e}")
            return False
    
    def _build_message_blocks(self, plan: GrowthPlan, trace_id: str) -> list:
        """Build Slack Block Kit message"""
        
        # Calculate revenue opportunity
        revenue_opp = plan.kpis.revenue * (1 / (1 - plan.funnel_insight.drop_rate) - 1)
        
        # Get top experiment
        top_exp = plan.chosen_experiment
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 New Growth Plan: {plan.business_profile.name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Industry:*\n{plan.business_profile.industry}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Region:*\n{plan.business_profile.region}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Goal:*\n{plan.goal.objective}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Timeframe:*\n{plan.goal.horizon_weeks} weeks"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔍 Funnel Bottleneck Identified*\n"
                            f"Biggest drop: *{plan.funnel_insight.from_step}* → *{plan.funnel_insight.to_step}*\n"
                            f"Drop rate: *{plan.funnel_insight.drop_rate*100:.1f}%*\n"
                            f"💰 Revenue Opportunity: *${revenue_opp:,.2f}*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎯 Recommended Experiment*\n"
                            f"*{top_exp.experiment.name}*\n"
                            f"Channel: {top_exp.experiment.channel}\n"
                            f"Priority Score: {top_exp.priority_score:.1f} (I:{top_exp.impact} C:{top_exp.confidence} E:{top_exp.effort})"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 All Experiments Evaluated:*\n" + 
                            "\n".join([f"• {exp.experiment.name} (Score: {exp.priority_score:.1f})" 
                                     for exp in plan.experiments[:5]])
                }
            }
        ]
        
        # Add strategy commentary if available
        if plan.llm_strategy_commentary:
            blocks.append({
                "type": "divider"
            })
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 AI Strategy Commentary*\n{plan.llm_strategy_commentary[:500]}..."
                }
            })
        
        # Add trace ID
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Trace ID: `{trace_id}` | Generated by SME Growth Co-Pilot"
                }
            ]
        })
        
        return blocks


# Singleton instance
slack_notifier = SlackNotifier()