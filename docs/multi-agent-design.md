# Multi-Agent Architecture Design

**Version:** 0.2.0 (Planned)  
**Author:** Christopher Crilly Pienaah  
**Date:** November 27, 2025  
**Status:** Design Phase

---

## 🎯 Vision

Transform the current monolithic `build_growth_plan()` function into a **collaborative multi-agent system** where specialized AI agents work together, each handling one aspect of growth strategy generation.

**Current Architecture:** Single function with sequential logic  
**Target Architecture:** Orchestrated agents with clear separation of concerns

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│                  POST /plan, POST /plan/from-csv             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              GrowthCoPilotOrchestrator                       │
│         (Coordinates agent communication)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ IntakeAgent  │  │AnalystAgent  │  │StrategyAgent │
│ Validates &  │  │ Diagnoses    │  │ Proposes     │
│ Structures   │  │ Funnel       │  │ Experiments  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ScoringAgent │  │CopywriterAgent│ │  JudgeAgent  │
│ ICE Scores   │  │ Generates    │  │ Selects Best │
│ Experiments  │  │ Copy         │  │ & Explains   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  GrowthPlan     │
                 │  (Final Output) │
                 └─────────────────┘
```

---

## 🤖 Agent Specifications

### 1. IntakeAgent
**Responsibility:** Validate and structure incoming requests

**Inputs:**
- `PlanRequest` (from JSON or CSV)

**Outputs:**
- `ValidatedRequest` with sanitized data
- List of warnings/data quality issues

**Key Functions:**
```python
class IntakeAgent:
    def validate_kpis(self, kpis: KpiSnapshot) -> ValidationResult:
        """Check for data quality issues"""
        - Ensure no negative values
        - Check for impossible ratios (e.g., purchases > signups)
        - Validate date ranges
        - Flag missing optional fields
    
    def extract_constraints(self, goal: GrowthGoal) -> List[Constraint]:
        """Parse constraint text into structured rules"""
        - Parse "no paid ads" → budget_constraint
        - Parse "focus on email" → channel_preference
        - Parse time constraints
    
    def assess_data_completeness(self) -> QualityScore:
        """Rate data quality 1-10"""
        - High quality: all fields, recent data
        - Low quality: missing fields, old data
```

**Error Handling:**
- Invalid data → Return structured error with suggested fixes
- Missing fields → Use defaults, warn user
- Impossible values → Reject with clear message

---

### 2. AnalystAgent (Data Scientist)
**Responsibility:** Diagnose funnel bottlenecks and calculate metrics

**Inputs:**
- `ValidatedRequest`

**Outputs:**
- `FunnelInsight` (current)
- `DetailedAnalytics` (new - extended metrics)

**Key Functions:**
```python
class AnalystAgent:
    def analyze_funnel(self, kpis: KpiSnapshot) -> FunnelInsight:
        """Identify biggest drop-off (current logic)"""
        
    def calculate_conversion_rates(self) -> Dict[str, float]:
        """All stage conversions"""
        return {
            'visit_to_lead': 0.175,
            'lead_to_signup': 0.571,
            'signup_to_purchase': 0.40
        }
    
    def estimate_revenue_opportunity(self, drop_rate: float) -> float:
        """Calculate $ value of fixing bottleneck"""
        lost_customers = visits * drop_rate
        potential_revenue = lost_customers * avg_purchase_value
        return potential_revenue
    
    def compare_to_benchmarks(self, industry: str) -> BenchmarkComparison:
        """Compare to industry standards (future)"""
        # E.g., "Your 17.5% visit-to-lead is below F&B average of 25%"
```

**Error Handling:**
- Zero division → Return 0% conversion with warning
- All zeros → Flag "no data" issue
- Negative values → Already caught by IntakeAgent

---

### 3. StrategyAgent (Growth Marketer)
**Responsibility:** Propose experiments based on bottlenecks

**Inputs:**
- `FunnelInsight`
- `BusinessProfile`
- `GrowthGoal`

**Outputs:**
- `List[GrowthExperiment]` (2-6 experiments)

**Key Functions:**
```python
class StrategyAgent:
    def propose_experiments(
        self, 
        bottleneck: FunnelInsight,
        business: BusinessProfile,
        constraints: List[Constraint]
    ) -> List[GrowthExperiment]:
        """Generate context-aware experiments (current logic)"""
        
    def filter_by_constraints(self, experiments, constraints):
        """Remove experiments that violate constraints"""
        # E.g., if "no paid ads" → exclude paid campaigns
        
    def adapt_to_industry(self, experiments, industry: str):
        """Customize experiments for industry"""
        # E.g., F&B → in-store tactics
        # E.g., SaaS → product-led growth
    
    def explain_hypothesis(self, experiment: GrowthExperiment) -> str:
        """Detailed reasoning for each experiment"""
```

**Future Enhancement:**
- Use Gemini to GENERATE experiments (not just explain)
- Learn from historical success rates
- Industry-specific templates

---

### 4. ScoringAgent (Analyst)
**Responsibility:** Score experiments using ICE framework

**Inputs:**
- `List[GrowthExperiment]`
- `BusinessProfile` (for context)

**Outputs:**
- `List[ScoredExperiment]` (sorted by priority)

**Key Functions:**
```python
class ScoringAgent:
    def score_ice(self, experiments: List[GrowthExperiment]) -> List[ScoredExperiment]:
        """Apply ICE scoring (current logic)"""
        
    def adjust_for_business_context(self, score, business):
        """Modify scores based on business specifics"""
        # E.g., local business → boost in-store tactics
        # E.g., online-only → boost digital tactics
    
    def explain_scoring_rationale(self, experiment) -> str:
        """Why did this get this ICE score?"""
        return f"Impact {score.impact} because..."
```

**Scoring Intelligence:**
- Channel availability → Adjust effort scores
- Past success data → Adjust confidence
- Business size → Adjust impact estimates

---

### 5. CopywriterAgent (Content Creator)
**Responsibility:** Generate marketing copy

**Inputs:**
- `ScoredExperiment` (the chosen one)
- `BusinessProfile` (for tone/voice)
- `GrowthGoal`

**Outputs:**
- `MarketingCopy` (email, social, etc.)

**Key Functions:**
```python
class CopywriterAgent:
    def generate_copy(
        self,
        experiment: ScoredExperiment,
        tone_of_voice: str,
        channel: str
    ) -> str:
        """Generate channel-specific copy"""
        
    def adapt_tone(self, copy: str, tone: str) -> str:
        """Match business voice"""
        # Use Gemini to rewrite in specific tone
        
    def create_multi_channel_copy(self) -> Dict[str, str]:
        """Generate for multiple channels"""
        return {
            'email': email_copy,
            'social': social_post,
            'in_store': poster_text
        }
```

**Enhancement:**
- Use Gemini to generate creative, on-brand copy
- A/B test variant generation
- Subject line testing

---

### 6. JudgeAgent (Executive Decision Maker)
**Responsibility:** Select best experiment and explain why

**Inputs:**
- `List[ScoredExperiment]`
- Full business context

**Outputs:**
- `ScoredExperiment` (the chosen one)
- `StrategyCommentary` (the WHY)

**Key Functions:**
```python
class JudgeAgent:
    def select_winner(
        self,
        scored_experiments: List[ScoredExperiment],
        business_context: BusinessContext
    ) -> ScoredExperiment:
        """Choose #1 experiment (may disagree with scores!)"""
        # Usually picks highest score
        # But can override based on business specifics
        
    def generate_strategy_commentary(
        self,
        winner: ScoredExperiment,
        alternatives: List[ScoredExperiment]
    ) -> str:
        """Comprehensive WHY explanation (uses enhanced prompt)"""
        # Uses Gemini with structured 3-paragraph format
        # Explains: Problem → Why This → Expected Outcome
        
    def provide_implementation_guidance(self) -> ActionPlan:
        """Next steps for business owner"""
        return {
            'week_1': ['Draft email', 'Design reward'],
            'week_2': ['Test with 50 customers'],
            'week_3': ['Launch to full list']
        }
```

---

## 🔄 Agent Communication Protocol

### Message Format
```python
class AgentMessage:
    sender: str          # Which agent sent this
    recipient: str       # Which agent receives it
    message_type: str    # 'request', 'response', 'error'
    payload: Any         # The actual data
    timestamp: datetime
    trace_id: str        # For debugging
```

### Communication Flow
```python
1. Orchestrator → IntakeAgent: "Validate this request"
2. IntakeAgent → Orchestrator: "Validated, here's clean data"
3. Orchestrator → AnalystAgent: "Analyze this funnel"
4. AnalystAgent → Orchestrator: "Bottleneck is visits→leads"
5. Orchestrator → StrategyAgent: "Propose experiments for this bottleneck"
6. StrategyAgent → Orchestrator: "Here are 2 experiments"
7. Orchestrator → ScoringAgent: "Score these"
8. ScoringAgent → Orchestrator: "Scored and ranked"
9. Orchestrator → JudgeAgent: "Pick the winner"
10. JudgeAgent → Orchestrator: "Here's #1 with reasoning"
11. Orchestrator → CopywriterAgent: "Generate copy for this"
12. CopywriterAgent → Orchestrator: "Copy ready"
13. Orchestrator → API: "Complete plan assembled"
```

---

## 🛠️ Implementation Strategy

### Phase A: Create Agent Classes (2 hours)
**File structure:**
```
app/agents/
├── __init__.py
├── base.py              # BaseAgent class
├── intake.py            # IntakeAgent
├── analyst.py           # AnalystAgent
├── strategy.py          # StrategyAgent
├── scoring.py           # ScoringAgent
├── copywriter.py        # CopywriterAgent
└── judge.py             # JudgeAgent
```

**Base Agent:**
```python
class BaseAgent:
    """All agents inherit from this"""
    
    def __init__(self, name: str):
        self.name = name
        self.history = []
    
    def process(self, input_data: Any) -> Any:
        """Override in each agent"""
        raise NotImplementedError
    
    def log_action(self, action: str, data: Any):
        """Track what this agent did"""
        self.history.append({
            'timestamp': datetime.now(),
            'action': action,
            'data': data
        })
```

### Phase B: Build Orchestrator (2 hours)
**File:** `app/orchestrator.py`
```python
class GrowthCoPilotOrchestrator:
    """Coordinates multi-agent workflow"""
    
    def __init__(self):
        self.intake = IntakeAgent("Intake")
        self.analyst = AnalystAgent("Analyst")
        self.strategist = StrategyAgent("Strategist")
        self.scorer = ScoringAgent("Scorer")
        self.copywriter = CopywriterAgent("Copywriter")
        self.judge = JudgeAgent("Judge")
    
    async def execute_plan(self, request: PlanRequest) -> GrowthPlan:
        """Sequential agent workflow"""
        
        # Stage 1: Validate
        validated = await self.intake.process(request)
        
        # Stage 2: Analyze
        insight = await self.analyst.process(validated.kpis)
        
        # Stage 3: Strategize
        experiments = await self.strategist.process({
            'insight': insight,
            'business': validated.business_profile,
            'goal': validated.goal
        })
        
        # Stage 4: Score
        scored = await self.scorer.process(experiments)
        
        # Stage 5: Judge
        winner = await self.judge.select_winner(scored)
        
        # Stage 6: Generate Copy
        copy = await self.copywriter.process({
            'experiment': winner,
            'business': validated.business_profile,
            'tone': validated.business_profile.tone_of_voice
        })
        
        # Stage 7: Strategy Commentary
        commentary = await self.judge.generate_commentary({
            'winner': winner,
            'alternatives': scored[1:],
            'business': validated.business_profile,
            'insight': insight
        })
        
        # Assemble final plan
        return GrowthPlan(...)
```

### Phase C: Migration Strategy (1 hour)
**How to move from monolithic → multi-agent WITHOUT breaking existing API**

**Option 1: Feature Flag**
```python
USE_MULTI_AGENT = os.getenv("USE_MULTI_AGENT", "false") == "true"

@app.post("/plan")
def create_plan(request: PlanRequest):
    if USE_MULTI_AGENT:
        plan = orchestrator.execute_plan(request)
    else:
        plan = build_growth_plan(...)  # Legacy
```

**Option 2: Gradual Migration**
```python
# Week 1: Move IntakeAgent only
# Week 2: Add AnalystAgent
# Week 3: Add rest of agents
```

**Option 3: New Endpoint**
```python
@app.post("/plan/v2")  # Multi-agent version
@app.post("/plan")     # Keep monolithic for compatibility
```

---

## 🧪 Testing Strategy

### Unit Tests (Each Agent)
```python
# tests/agents/test_intake_agent.py
def test_intake_validates_negative_kpis()
def test_intake_parses_constraints()

# tests/agents/test_analyst_agent.py
def test_analyst_handles_zero_division()
def test_analyst_identifies_correct_bottleneck()

# etc. for each agent
```

### Integration Tests (Agent Communication)
```python
# tests/test_orchestrator.py
def test_orchestrator_full_workflow()
def test_orchestrator_handles_agent_failure()
def test_orchestrator_maintains_trace_id()
```

### Performance Tests
```python
def test_multi_agent_latency_acceptable():
    """Ensure multi-agent isn't slower than monolithic"""
    # Target: <1 second total (excluding LLM)
```

---

## 📊 Data Flow Specification

### Input → Validated Data
```python
PlanRequest → IntakeAgent → ValidatedRequest
{
    'business': BusinessProfile,
    'kpis': KpiSnapshot (validated),
    'goal': GrowthGoal,
    'constraints': List[Constraint],  # NEW - structured
    'quality_score': float,            # NEW - data quality
    'warnings': List[str]              # NEW - data issues
}
```

### Validated Data → Funnel Analysis
```python
ValidatedRequest → AnalystAgent → AnalysisResult
{
    'insight': FunnelInsight,
    'conversion_rates': Dict[str, float],
    'revenue_opportunity': float,       # NEW
    'benchmark_comparison': Dict,        # NEW (future)
    'confidence_level': float            # NEW
}
```

### Analysis → Experiments
```python
AnalysisResult → StrategyAgent → ExperimentProposal
{
    'experiments': List[GrowthExperiment],
    'filtered_count': int,              # How many were rejected
    'reasoning': Dict[str, str]         # Why each was proposed
}
```

### Experiments → Scored
```python
ExperimentProposal → ScoringAgent → ScoredExperiments
{
    'scored': List[ScoredExperiment],
    'scoring_rationale': Dict,          # Why these scores
    'confidence': float                  # How sure are the scores
}
```

### Scored → Decision
```python
ScoredExperiments → JudgeAgent → Decision
{
    'chosen': ScoredExperiment,
    'reasoning': str,                    # Why this one
    'runner_up': ScoredExperiment,       # Close second
    'consideration_factors': List[str]   # What influenced decision
}
```

---

## 🚨 Error Handling & Resilience

### Agent Failure Scenarios

**If IntakeAgent fails:**
- Fallback: Use basic validation, warn user
- Continue: Yes, with warnings

**If AnalystAgent fails:**
- Fallback: Use simple heuristic (pick first stage)
- Continue: Yes, degraded mode

**If StrategyAgent fails:**
- Fallback: Use rule-based generation (current logic)
- Continue: Yes, deterministic mode

**If ScoringAgent fails:**
- Fallback: Use default scores (4,3,3)
- Continue: Yes, equal ranking

**If CopywriterAgent fails:**
- Fallback: Use template-based generation (current logic)
- Continue: Yes, basic copy

**If JudgeAgent fails:**
- Fallback: Pick highest scoring experiment
- Continue: Yes, no commentary

**CRITICAL RULE:** System MUST always return a valid GrowthPlan, even if all LLMs fail!

---

## 🔍 Observability & Debugging

### Trace ID System
```python
class TraceContext:
    trace_id: str       # UUID for this request
    agent_trail: List   # Which agents ran
    timing: Dict        # How long each took
    errors: List        # Any errors encountered
```

### Logging
```python
# Each agent logs:
logger.info(f"[{trace_id}] IntakeAgent: Validating request for {business_id}")
logger.info(f"[{trace_id}] AnalystAgent: Detected bottleneck visits→leads (82.5%)")
logger.error(f"[{trace_id}] JudgeAgent: Gemini call failed, using fallback")
```

### Metrics to Track
- Agent execution time (each agent)
- Agent success/failure rates
- LLM call success rates
- End-to-end latency
- Most common bottlenecks detected
- Most commonly chosen experiments

---

## 📈 Performance Targets

| Metric | Current (Monolithic) | Target (Multi-Agent) |
|--------|---------------------|---------------------|
| **Total latency** | <500ms | <800ms |
| **LLM calls** | 1 per request | 1-2 per request |
| **Memory usage** | ~50MB | ~80MB |
| **Testability** | 69% coverage | 85% coverage |
| **Maintainability** | Medium | High |

---

## 🎯 Success Criteria

**Multi-agent architecture is successful if:**

1. ✅ Each agent has <100 lines of focused code
2. ✅ Agents can be tested independently
3. ✅ New experiments can be added without touching other agents
4. ✅ Agent failures don't crash the system
5. ✅ Response time < 1 second (excl. LLM)
6. ✅ Code is more maintainable than monolithic version
7. ✅ Can swap out individual agents (e.g., replace Gemini with GPT-4)

---

## 🚀 Implementation Timeline

### Saturday (4 hours)
- 09:00-10:00: Create agent base classes
- 10:00-11:00: Implement IntakeAgent, AnalystAgent
- 11:00-12:00: Implement StrategyAgent, ScoringAgent
- 12:00-13:00: Implement CopywriterAgent, JudgeAgent

### Sunday (3 hours)
- 09:00-10:00: Build orchestrator
- 10:00-11:00: Write integration tests
- 11:00-12:00: Update documentation, test, push

### Monday (Polish)
- Test extensively
- Fix any bugs
- Performance optimization
- Update README with architecture diagram

---

## 🤔 Open Questions to Resolve

1. **Should agents use Gemini or stay deterministic?**
   - Pro: More intelligent, adaptive
   - Con: More LLM calls, higher latency
   - **Decision:** Keep AnalystAgent & ScoringAgent deterministic, use LLM for JudgeAgent only

2. **How to handle agent-to-agent data validation?**
   - Use Pydantic models for all inter-agent messages
   - Each agent validates its inputs

3. **Should we add agent retry logic?**
   - Yes, but with exponential backoff
   - Max 2 retries per agent

4. **How to visualize agent workflow for debugging?**
   - Add `/debug/{trace_id}` endpoint
   - Returns agent execution timeline

---

## 📝 Migration Checklist

**Before starting:**
- [ ] All current tests passing
- [ ] Current system documented
- [ ] Performance baseline recorded

**During migration:**
- [ ] Keep monolithic version working
- [ ] Add agents incrementally
- [ ] Test after each agent addition
- [ ] Maintain API compatibility

**After completion:**
- [ ] All tests passing
- [ ] Performance within targets
- [ ] Documentation updated
- [ ] Deprecation plan for monolithic version

---

## 🎓 Learning Resources

- **Agent Development Kit (ADK) docs:** Review Google's patterns
- **FastAPI async patterns:** For efficient agent coordination
- **Pydantic validation:** For inter-agent contracts
- **Structured outputs:** For reliable agent communication

---

## 🏁 Next Steps

1. **Review this design** with fresh eyes (tomorrow)
2. **Get feedback** from peers/mentors
3. **Refine** agent responsibilities
4. **Start implementation** this weekend
5. **Iterate** based on testing

---

**Status:** Ready for implementation  
**Risk Level:** Medium (well-planned but significant refactor)  
**Expected Value:** High (better architecture, easier to extend, impressive for portfolio)

---

*This design document will guide the transformation from monolithic function to collaborative multi-agent system while maintaining production stability.*