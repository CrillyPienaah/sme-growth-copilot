# SME Growth Co-Pilot 🚀

**🌐 Live Demo:** https://web-production-a0573.up.railway.app/  
**📚 API Docs:** https://web-production-a0573.up.railway.app/docs

**Version:** 0.2.0  
**Status:** ✅ DEPLOYED - Multi-Agent System with Enterprise Features Active  
**Maintainer:** Christopher Crilly Pienaah

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.0-orange.svg)](https://ai.google.dev/gemini-api)
[![Kaggle](https://img.shields.io/badge/Kaggle-AI%20Agents%20Capstone-20BEFF.svg)](https://www.kaggle.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

SME Growth Co-Pilot is an **enterprise-grade AI agent system** that transforms small business KPIs into data-driven, actionable growth strategies. Built with FastAPI and powered by Google Gemini, it features intelligent learning, real-time notifications, and comprehensive monitoring—delivering insights that typically require expensive consultants.

### What It Does

- 📊 **Automated Funnel Analysis** - Identifies conversion bottlenecks across visits→leads→signups→purchases
- 💡 **Smart Experiment Generation** - Proposes targeted growth initiatives based on detected problems
- 🎯 **ICE Prioritization** - Scores experiments by Impact, Confidence, and Effort
- 🧠 **Strategy Memory** - Learns from failed experiments and avoids repeating them
- 🤖 **AI Strategy Commentary** - Gemini-powered business reasoning
- ✍️ **Marketing Copy Generation** - Ready-to-use campaign messaging
- 📁 **Flexible Input** - JSON API, CSV upload, or webhook integration
- 🔔 **Real-Time Notifications** - Slack and email delivery
- 📈 **Performance Dashboard** - Beautiful web UI with live metrics
- 💰 **Revenue Opportunity Analysis** - Calculates potential revenue from fixes

---

## 🎯 System Architecture

### Multi-Agent Workflow

The system uses **6 specialized AI agents** working collaboratively:
```
┌─────────────────────────────────────────────────────────────┐
│                   GROWTH CO-PILOT ORCHESTRATOR              │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐   ┌──────────┐
     │  Intake  │    │ Analyst  │   │ Strategy │
     │  Agent   │───▶│  Agent   │──▶│  Agent   │
     └──────────┘    └──────────┘   └──────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐   ┌──────────┐
     │ Scoring  │    │   Judge  │   │Copywriter│
     │  Agent   │───▶│  Agent   │──▶│  Agent   │
     └──────────┘    └──────────┘   └──────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │   Growth Plan     │
                  │  • Slack          │
                  │  • Email          │
                  │  • Dashboard      │
                  │  • Database       │
                  └───────────────────┘
```

### The 6 AI Agents

1. **Intake Agent** - Validates business data and KPIs
2. **Analyst Agent** - Diagnoses funnel bottlenecks and calculates revenue opportunity
3. **Strategy Agent** - Proposes experiments, **filtered by strategy memory**
4. **Scoring Agent** - Applies ICE framework to rank experiments
5. **Judge Agent** - Selects the winning experiment and provides commentary
6. **Copywriter Agent** - Generates campaign copy for the chosen experiment

---

## ⭐ New Enterprise Features

### 🧠 Strategy Memory System

The system **learns from failures** and gets smarter over time:

**How it works:**
1. Business runs an experiment
2. Mark it as FAILED via API
3. System stores it in strategy_memory
4. **Future plans automatically exclude that experiment**
5. System recommends fresh alternatives
```bash
# Mark experiment as failed
POST /experiments/{experiment_id}/result
{
  "status": "FAILED",
  "observed_result": {"conversion_rate": -0.05}
}

# Next plan request automatically filters it out!
```

### 🔔 Slack Notifications

Real-time growth plan delivery to your Slack workspace:

**Features:**
- Beautiful formatted messages with Slack Block Kit
- Shows funnel analysis, revenue opportunity, experiments
- Includes AI commentary and trace IDs
- Production-ready with real webhooks

**Setup:**
```bash
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_WEBHOOK_URL=your_webhook_url
SLACK_TEST_MODE=false
```

### 📧 Email Integration

Send growth plans via email to stakeholders:

**Features:**
- Beautiful HTML email templates
- Plain text fallback
- Multiple recipients support
- SendGrid integration
```bash
POST /plan/with-email
{
  "request": { /* plan request */ },
  "recipient_emails": ["owner@business.com", "manager@business.com"]
}
```

### 🔌 Webhook Integration

External systems can push KPIs automatically:
```bash
POST /webhook/kpis
{
  "business_id": "shop_001",
  "visits": 10000,
  "leads": 1000,
  "signups": 500,
  "purchases": 250,
  "revenue": 25000.0
}
```

Triggers automatic plan generation + Slack/email notifications!

### 📊 Performance Monitoring

Track agent execution metrics in real-time:
```bash
GET /monitoring/agents

# Returns:
{
  "agents": [
    {
      "agent_name": "Strategy",
      "total_executions": 45,
      "success_rate": 100.0,
      "avg_execution_time_ms": 5
    }
  ]
}
```

### 🎨 Web Dashboard

Beautiful real-time dashboard at `http://localhost:8000/`

**Features:**
- Live agent performance charts
- Success rate tracking
- Response time monitoring
- Auto-refresh every 30 seconds
- Mobile-responsive design

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Optional: Slack webhook, SendGrid API key

### Installation
```bash
# Clone the repository
git clone https://github.com/CrillyPienaah/sme-growth-copilot.git
cd sme-growth-copilot

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```bash
# Core Settings
USE_MULTI_AGENT=true
GOOGLE_API_KEY=your_gemini_api_key

# Slack Integration (optional)
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_TEST_MODE=false
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Email Integration (optional)
EMAIL_NOTIFICATIONS_ENABLED=true
EMAIL_TEST_MODE=true
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=noreply@yourcompany.com

# Database
DATABASE_URL=sqlite:///./sme_growth_copilot.db
```

### Run the Application
```bash
# Start the server
uvicorn app.main:app --reload

# Access the dashboard
open http://localhost:8000

# API Documentation
open http://localhost:8000/docs
```

---

## 💡 How It Works

### 1. Funnel Analysis Engine

Analyzes three conversion stages:
```
visits → leads      # Capturing attention?
leads → signups     # Building trust?
signups → purchases # Closing the deal?
```

### 2. Experiment Recommendation

Context-aware experiments based on bottleneck:

| Bottleneck | Experiments |
|------------|-------------|
| **Visits → Leads** | Lead magnets, referral programs, content upgrades |
| **Leads → Signups** | Nurture sequences, demos, onboarding emails |
| **Signups → Purchases** | Loyalty programs, win-back campaigns, incentives |

### 3. ICE Prioritization
```
Priority = (Impact × Confidence) / Effort

Impact:     1-5 (growth potential)
Confidence: 1-5 (success likelihood)
Effort:     1-5 (implementation difficulty)
```

### 4. Strategy Memory

**Learns from failures:**
- Failed experiments stored in database
- Future plans automatically exclude them
- System recommends fresh alternatives
- Gets smarter with every iteration

---

## 🔌 API Reference

### Core Endpoints
```bash
POST   /plan                    # Generate plan from JSON
POST   /plan/from-csv           # Generate plan from CSV
POST   /plan/with-email         # Generate plan + send email
POST   /webhook/kpis            # Accept KPIs from external systems
GET    /plans/{business_id}     # Get historical plans
POST   /experiments/{id}/result # Update experiment results
GET    /monitoring/agents       # Agent performance metrics
GET    /monitoring/agents/{name} # Specific agent stats
GET    /                        # Web dashboard
GET    /health                  # Health check
```

### Example: Generate Plan
```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile": {
      "business_id": "shop_001",
      "name": "My Shop",
      "industry": "E-commerce",
      "region": "North America",
      "main_channels": ["Website"]
    },
    "kpis": {
      "visits": 10000,
      "leads": 1000,
      "signups": 500,
      "purchases": 250,
      "revenue": 25000.0
    },
    "goal": {
      "objective": "Increase revenue by 50%",
      "horizon_weeks": 12
    }
  }'
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, SQLAlchemy, Pydantic |
| **AI Engine** | Google Gemini 2.0 Flash |
| **Database** | PostgreSQL / SQLite |
| **Notifications** | Slack SDK, SendGrid |
| **Frontend** | Tailwind CSS, Chart.js |
| **Testing** | Pytest |
| **Deployment** | Railway |

---

## 🗺️ Roadmap

### Phase 1: Core System ✅ COMPLETE
- [x] Funnel analysis engine
- [x] ICE experiment scoring
- [x] Gemini integration
- [x] JSONL logging
- [x] Interactive API docs
- [x] CSV upload capability

### Phase 2: Multi-Agent Architecture ✅ COMPLETE
- [x] 6 specialized AI agents
- [x] Orchestrator workflow
- [x] Agent communication
- [x] Trace ID system
- [x] Revenue calculations

### Phase 3: Enterprise Features ✅ COMPLETE
- [x] Cloud deployment (Railway)
- [x] PostgreSQL backend
- [x] **Webhook integration**
- [x] **Email notifications**
- [x] **Slack notifications**
- [x] **Web dashboard**
- [x] **Performance monitoring**

### Phase 4: Scale & Optimization ✅ COMPLETE
- [x] Rate limiting structure
- [x] Multi-model LLM support (structure)
- [x] **Strategy memory system**
- [x] **Agent performance tracking**
- [ ] Caching layer
- [ ] Industry templates

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=app tests/

# Specific tests
pytest tests/test_logic.py -v
```

**Test Coverage:** 18 passing tests across funnel analysis, ICE scoring, CSV parsing, and end-to-end workflows.

---

## 📊 Example Use Cases

### Coffee Shop (Low Lead Capture)
- **Problem:** 82% drop visits→leads
- **Solution:** Referral program via email (Priority: 7.5)
- **Delivery:** Slack + Email notification
- **Tracking:** Dashboard shows performance

### SaaS Startup (Poor Trial Conversion)
- **Problem:** 75% drop signups→purchases
- **Solution:** Onboarding nurture sequence (Priority: 8.3)
- **Integration:** Webhook from CRM
- **Memory:** Avoids previously failed experiments

### E-commerce (High Signup Bounce)
- **Problem:** 60% drop leads→signups
- **Solution:** Live product demos (Priority: 5.3)
- **Input:** CSV from Shopify
- **Monitor:** Real-time agent metrics

---

## 📁 Project Structure
```
sme-growth-copilot/
├── app/
│   ├── agents/                 # 6 specialized AI agents
│   ├── integrations/           # Slack & Email notifiers
│   ├── monitoring/             # Performance tracking
│   ├── static/                 # Dashboard assets
│   ├── templates/              # HTML templates
│   ├── main.py                 # FastAPI app
│   ├── orchestrator.py         # Multi-agent coordinator
│   ├── schemas.py              # Pydantic models
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # Database config
│   ├── db_utils.py             # Database helpers
│   ├── logic.py                # Business logic
│   └── storage.py              # JSONL persistence
├── tests/                      # Unit & integration tests
├── data/                       # Historical logs
├── examples/                   # Sample files
└── README.md                   # This file
```

---

## 🤝 Contributing

Contributions welcome! Areas for contribution:
- Additional experiment templates
- Industry-specific logic
- LLM provider integrations
- Test coverage improvements

---

## 📄 License

MIT License - Copyright (c) 2025 Christopher Crilly Pienaah

---

## 👤 Author

**Christopher Crilly Pienaah**  
Master's in Analytics @ Northeastern University (GPA: 3.96)  
AI/ML Product Strategist | Data Scientist | Founder, LuminaMed-AI

- LinkedIn: [Christopher Crilly Pienaah](https://www.linkedin.com/in/christopher-crilly-pienaah)
- GitHub: [@CrillyPienaah](https://github.com/CrillyPienaah)

---

## 🙏 Acknowledgments

- Built for the **Google Kaggle AI Agents Capstone** competition
- Powered by **Google Gemini 2.0 Flash**
- Inspired by Sean Ellis's ICE framework

---

## 📈 Project Stats

- **Lines of Code:** 5,000+
- **Agents:** 6 specialized AI agents
- **Features:** 9 enterprise features
- **Tests:** 18 unit tests passing
- **API Endpoints:** 10+
- **Development Time:** 18+ hours intensive coding
- **Status:** Production-ready

---

**Built with ❤️ and ☕ for SMEs that deserve world-class growth strategy**
