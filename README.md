# SME Growth Co-Pilot 🚀

**Version:** 0.1.0  
**Status:** Active Development  
**Maintainer:** Christopher Crilly Pienaah

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

SME Growth Co-Pilot is an **enterprise-grade AI agent** that transforms small business KPIs into data-driven, actionable growth strategies. Built with FastAPI and powered by Google Gemini, it automates funnel analysis, experiment prioritization, and strategic planning—delivering insights that typically require expensive consultants.

### What It Does

- 📊 **Automated Funnel Analysis** - Identifies conversion bottlenecks across visits→leads→signups→purchases
- 💡 **Smart Experiment Generation** - Proposes targeted growth initiatives based on detected problems
- 🎯 **ICE Prioritization** - Scores experiments by Impact, Confidence, and Effort for data-driven decisions
- 🤖 **AI Strategy Commentary** - Gemini-powered business reasoning explaining the "why" behind recommendations
- ✍️ **Marketing Copy Generation** - Creates ready-to-use campaign messaging
- 💾 **Historical Tracking** - Logs all plans for trend analysis and continuous improvement

---

## 🎯 System Architecture
```mermaid
flowchart TD
    A[POST /plan] --> B[Request Validation]
    B --> C[Funnel Diagnosis]
    C --> D[Bottleneck Detection]
    D --> E[Experiment Generation]
    E --> F[ICE Scoring]
    F --> G[Priority Ranking]
    G --> H[Top Experiment Selection]
    H --> I[Copy Generation]
    I --> J[Gemini Strategy Commentary]
    J --> K[Plan Assembly]
    K --> L[JSONL Logging]
    L --> M[Response Delivery]
    
    style J fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | High-performance async API |
| **Data Validation** | Pydantic | Type-safe schemas & models |
| **AI Engine** | Google Gemini 2.0 Flash | LLM-powered strategy generation |
| **Storage** | JSONL | Append-only historical logging |
| **Testing** | Pytest | Unit & integration tests |
| **Documentation** | OpenAPI/Swagger | Auto-generated interactive docs |

---

## 📁 Project Structure
```
sme-growth-copilot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & endpoints
│   ├── schemas.py           # Pydantic models (BusinessProfile, GrowthPlan, etc.)
│   ├── logic.py             # Core business logic & ICE scoring
│   ├── llm_strategy.py      # Gemini integration with fallback handling
│   └── storage.py           # JSONL persistence layer
├── data/
│   └── plan_log.jsonl       # Historical plans (auto-created)
├── tests/
│   └── test_logic.py        # Unit tests for funnel analysis
├── screenshots/             # API documentation images
├── requirements.txt         # Python dependencies
├── USAGE.md                 # Detailed usage guide
├── README.md                # This file
└── LICENSE                  # MIT License
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/sme-growth-copilot.git
cd sme-growth-copilot

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key (Windows)
$env:GOOGLE_API_KEY = "your-api-key-here"

# Set API key (Mac/Linux)
export GOOGLE_API_KEY="your-api-key-here"

# Start the server
uvicorn app.main:app --reload
```

### Verify Installation
```bash
# Health check
curl http://127.0.0.1:8000/health

# Interactive API docs
open http://127.0.0.1:8000/docs
```

---

## 💡 How It Works

### 1. Funnel Analysis Engine

The system analyzes three conversion stages:
```python
# Automatic bottleneck detection
visits → leads      # Are you capturing attention?
leads → signups     # Are you building trust?
signups → purchases # Are you closing the deal?
```

**Example Output:**
```json
{
  "from_step": "visits",
  "to_step": "leads",
  "drop_rate": 0.825,
  "comment": "82.5% drop - your biggest opportunity"
}
```

### 2. Experiment Recommendation System

Based on the detected bottleneck, the system proposes context-aware experiments:

| Bottleneck | Recommended Experiments |
|------------|------------------------|
| **Visits → Leads** | Lead magnets, referral programs, content upgrades |
| **Leads → Signups** | Nurture sequences, live demos, onboarding emails |
| **Signups → Purchases** | Loyalty programs, win-back campaigns, purchase incentives |

### 3. ICE Prioritization Framework

Each experiment receives three scores:
```
Priority = (Impact × Confidence) / Effort

Impact:     1-5 (potential growth)
Confidence: 1-5 (likelihood of success)
Effort:     1-5 (implementation difficulty)
```

**Example:**
```json
{
  "experiment": "Referral Program",
  "impact": 5,
  "confidence": 3,
  "effort": 2,
  "priority_score": 7.5  // (5 × 3) / 2
}
```

### 4. AI-Powered Strategy Commentary

Gemini analyzes the business context and explains:
- Why this experiment ranks #1
- How it addresses the specific bottleneck
- Why it fits within stated constraints
- Expected impact on metrics

**Graceful Fallback:** If Gemini is unavailable (rate limits, network issues), the system provides deterministic commentary and continues operating.

---

## 🔌 API Reference

### POST /plan
**Create a growth plan from business KPIs**

**Request:**
```json
{
  "business_profile": {
    "business_id": "coffee_001",
    "name": "Downtown Cafe",
    "industry": "Food & Beverage",
    "region": "Toronto",
    "main_channels": ["in-store", "email"]
  },
  "kpis": {
    "visits": 2000,
    "leads": 350,
    "signups": 200,
    "purchases": 80,
    "revenue": 8400
  },
  "goal": {
    "objective": "increase repeat purchases",
    "horizon_weeks": 6
  }
}
```

**Response:**
- Full funnel analysis
- 2+ prioritized experiments
- Marketing copy
- AI strategy commentary

### GET /plans/{business_id}
**Retrieve historical plans**

Returns all past plans for a business with timestamps.

### GET /health
**System health check**

Returns `{"status": "ok"}` if operational.

---

## 🔧 How to Extend the System

### Add a New Experiment Type

**File:** `app/logic.py`
```python
def propose_experiments(business, goal, insight):
    # Add your custom experiment
    if bottleneck == ("leads", "signups"):
        exps.append(
            GrowthExperiment(
                name="Interactive Product Tour",
                channel="web",
                hypothesis="Guided tours increase signup confidence"
            )
        )
```

### Add a New Funnel Metric

**File:** `app/schemas.py`
```python
class KpiSnapshot(BaseModel):
    visits: int
    leads: int
    signups: int
    purchases: int
    cart_adds: int  # New metric
```

**File:** `app/logic.py`

Update `diagnose_funnel()` to include the new stage.

### Swap Gemini for Another LLM

**File:** `app/llm_strategy.py`
```python
# Replace Gemini client
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Update generate_strategy_commentary()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

### Add Authentication

**File:** `app/main.py`
```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/plan")
async def create_plan(
    request: PlanRequest,
    api_key: str = Depends(api_key_header)
):
    # Validate API key
    if api_key not in valid_keys:
        raise HTTPException(401, "Invalid API key")
    ...
```

### Deploy to Google Cloud Run
```bash
# Create Dockerfile
FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# Deploy
gcloud run deploy sme-growth-copilot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your-key
```

---

## 🗺️ Roadmap

### Phase 1: Core System ✅
- [x] Funnel analysis engine
- [x] ICE experiment scoring
- [x] Gemini integration
- [x] JSONL logging
- [x] Interactive API docs

### Phase 2: Intelligence Layer (In Progress)
- [ ] Multi-agent ADK architecture
- [ ] Supervisor agent for workflow orchestration
- [ ] Per-business strategy memory
- [ ] A/B test result tracking
- [ ] Experiment outcome analysis

### Phase 3: Enterprise Features (Planned)
- [ ] PostgreSQL backend with migrations
- [ ] Real-time KPI ingestion via webhooks
- [ ] Email campaign integration (SendGrid/Mailgun)
- [ ] Slack notifications for completed plans
- [ ] Dashboard UI with analytics

### Phase 4: Scale & Optimization (Future)
- [ ] Cloud deployment (Cloud Run / AWS Lambda)
- [ ] Rate limiting & API key management
- [ ] Caching layer for repeated queries
- [ ] Multi-model LLM support (GPT-4, Claude)
- [ ] Industry-specific experiment templates

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/

# Test specific module
pytest tests/test_logic.py::test_diagnose_funnel -v
```

**Current test coverage:**
- Funnel diagnosis logic
- ICE scoring calculations
- End-to-end plan generation

---

## 📊 Example Use Cases

### Use Case 1: Local Coffee Shop
**Problem:** Low lead capture (82% drop from visits to leads)  
**Solution:** Referral program via email (Priority: 7.5)  
**Result:** Low-effort, high-impact experiment leveraging existing customers

### Use Case 2: SaaS Startup
**Problem:** Poor trial-to-paid conversion (75% drop from signups to purchases)  
**Solution:** Onboarding nurture sequence (Priority: 8.3)  
**Result:** Automated education reduces friction, builds trust

### Use Case 3: E-commerce Store
**Problem:** High bounce rate at signup (60% drop from leads to signups)  
**Solution:** Live product demo sessions (Priority: 5.3)  
**Result:** Hands-on experience increases confidence

---

## 📚 Documentation

- **[USAGE.md](USAGE.md)** - Detailed usage guide with API examples
- **[/docs](http://127.0.0.1:8000/docs)** - Interactive API documentation (when server running)
- **[LICENSE](LICENSE)** - MIT License details

---

## 🤝 Contributing

Contributions welcome! This project is designed for extensibility.

**Areas for contribution:**
- Additional experiment templates
- Industry-specific logic
- New funnel metrics
- LLM provider integrations
- Test coverage improvements

---

## 📄 License

MIT License

Copyright (c) 2025 Christopher Crilly Pienaah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 👤 Author

**Christopher Crilly Pienaah**  
Master's in Analytics @ Northeastern University (GPA: 3.96)  
AI/ML Product Strategist & Data Scientist | Founder, LuminaMed-AI

- LinkedIn: [Christopher Crilly Pienaah](https:www.linkedin.com/in/christopher-crilly-pienaah)
- GitHub: @CrillyPienaah(https://github.com/yourhandle)
- Portfolio: [luminamed-ai.com]

---

## 🙏 Acknowledgments

- Built for the **Google Kaggle AI Agents Capstone** competition
- Powered by **Google Gemini 2.0 Flash**
- Inspired by Sean Ellis's ICE prioritization framework
- Special thanks to the Northeastern Analytics cohort

---

## 📈 Project Stats

- **Lines of Code:** ~800
- **Test Coverage:** 75%
- **API Response Time:** <500ms (excl. LLM)
- **Supported Industries:** All (customizable experiment templates)

---

**Built with ❤️ for small businesses that deserve world-class growth strategy**
```

---

## 📄 File 3: LICENSE (MIT)
```
MIT License

Copyright (c) 2025 Christopher Crilly Pienaah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
