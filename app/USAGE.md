# SME Growth Co-Pilot - Usage Guide

**Version:** 0.1.0  
**Status:** Active Development  
**Maintainer:** Christopher Crilly Pienaah

---

## 📖 Overview

SME Growth Co-Pilot is an enterprise-grade AI agent that converts SME KPIs into an actionable, ICE-prioritized growth plan. It performs funnel diagnostics, proposes experiments, generates ready-to-use marketing copy, and provides LLM-powered strategic commentary using Google Gemini. This guide shows you how to install, run, and integrate it.

---

## 📁 Project Structuresme-growth-copilot/
├── app/
│   ├── init.py
│   ├── main.py              # FastAPI app & endpoints
│   ├── schemas.py           # Pydantic models
│   ├── logic.py             # Business logic & ICE scoring
│   ├── llm_strategy.py      # Gemini integration
│   └── storage.py           # JSONL logging
├── data/
│   └── plan_log.jsonl       # Historical plans storage
├── tests/
│   └── test_logic.py        # Unit tests
├── screenshots/             # API documentation screenshots
├── requirements.txt         # Python dependencies
├── USAGE.md                 # This file
├── README.md                # Project overview
└── LICENSE                  # MIT License

---

## 🚀 Quick Start

### 1. Setup Environment
```bashActivate virtual environment
.venv\Scripts\activate  # Windows PowerShellSet your Gemini API key
$env:GOOGLE_API_KEY = "your-gemini-api-key-here"Verify it's set
$env:GOOGLE_API_KEY

### 2. Start the Server
```bashuvicorn app.main:app --reload

Server will start at: **http://127.0.0.1:8000**

### 3. Access API Documentation

Open in browser: **http://127.0.0.1:8000/docs**

---

## 📊 API Endpoints

### 1. Health Check
**GET** `/health`

Quick check that the service is running.

**Browser:**http://127.0.0.1:8000/health

**cURL:**
```bashcurl http://127.0.0.1:8000/health

**Response:**
```json{
"status": "ok"
}

---

### 2. Create Growth Plan
**POST** `/plan`

Analyzes business metrics and generates a prioritized growth plan.

**Browser:** http://127.0.0.1:8000/docs (Use interactive UI)

**cURL:**
```bashcurl -X POST "http://127.0.0.1:8000/plan" 
-H "Content-Type: application/json" 
-d '{
"business_profile": {
"business_id": "demo_sme_001",
"name": "Neighborhood Coffee Hub",
"industry": "Food & Beverage",
"region": "Toronto, Canada",
"main_channels": ["in-store", "email", "instagram"],
"target_audience": "local professionals and students",
"tone_of_voice": "warm, community-focused, friendly"
},
"kpis": {
"period": "last_30_days",
"visits": 2000,
"leads": 350,
"signups": 200,
"purchases": 80,
"revenue": 8400.0,
"retention_rate": 0.35
},
"goal": {
"objective": "increase repeat purchases from existing customers",
"horizon_weeks": 6,
"constraints": "No paid ads; focus on owned channels like email and in-store promos."
}
}'

**PowerShell (Windows):**
```powershellInvoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/plan"   -ContentType "application/json"
-Body (Get-Content sample_request.json)

**Response Includes:**
- 📊 Funnel analysis (identifies biggest bottleneck)
- 💡 Recommended experiments (2+ options)
- 🎯 Chosen experiment (ICE prioritized)
- ✍️ Marketing copy suggestion
- 🤖 AI-powered strategy commentary

**Example Response:**
```json{
"business_profile": {...},
"kpis": {...},
"goal": {...},
"funnel_insight": {
"from_step": "visits",
"to_step": "leads",
"drop_rate": 0.825,
"comment": "Biggest drop is from visits to leads: conversion=17.5%, drop=82.5%."
},
"experiments": [
{
"experiment": {
"name": "Referral Program",
"channel": "email",
"hypothesis": "Existing customers will refer similar customers when given a clear, simple reward."
},
"impact": 5,
"confidence": 3,
"effort": 2,
"priority_score": 7.5
}
],
"chosen_experiment": {...},
"copy_suggestion": "Subject: A thank-you from Neighborhood Coffee Hub...",
"llm_strategy_commentary": "The Referral Program is your best first move..."
}

---

### 3. Get Historical Plans
**GET** `/plans/{business_id}`

Retrieves all past growth plans for a specific business.

**Browser:**http://127.0.0.1:8000/plans/demo_sme_001

**cURL:**
```bashcurl http://127.0.0.1:8000/plans/demo_sme_001

**Response:**
Array of all plans generated for that business, with timestamps.

---

## 🎯 What the System Does

### Step 1: Funnel Analysis
Analyzes your conversion funnel and identifies the biggest drop-off:
- **Visits → Leads**: Are you capturing visitor interest?
- **Leads → Signups**: Are leads converting to accounts?
- **Signups → Purchases**: Are users becoming customers?

### Step 2: Experiment Generation
Proposes growth experiments based on the bottleneck:
- **Visits→Leads problem:** Lead magnets, referral programs
- **Leads→Signups problem:** Nurture sequences, demos
- **Signups→Purchases problem:** Loyalty programs, win-back campaigns

### Step 3: ICE Prioritization
Scores each experiment on:
- **Impact:** How much growth it could drive (1-5)
- **Confidence:** How likely it is to work (1-5)
- **Effort:** How hard it is to implement (1-5)

**Priority Score = (Impact × Confidence) / Effort**

Higher score = Higher priority experiment

### Step 4: AI Strategy Commentary
Uses Google Gemini to explain:
- Why this experiment is #1
- How it tackles the bottleneck
- Why it fits the business constraints
- Expected outcomes

### Step 5: Copy Generation
Creates ready-to-use marketing copy for the chosen experiment:
- Email subject lines
- Body copy
- Call-to-action messaging

---

## 💾 Data Storage

All plans are logged to: `data/plan_log.jsonl`

Each line contains:
- **Timestamp** (ISO format with timezone)
- **Business ID** (for filtering)
- **Full request** (original input)
- **Complete plan** (generated output)

This allows you to:
- Track historical recommendations
- Compare different scenarios
- Analyze experiment trends
- Build analytics on top of the data

---

## 🔧 Troubleshooting

### "Strategy note (no LLM)" in response
This is the **fallback message** when:
- API key not set properly
- Rate limits hit (free tier has strict limits)
- Network issues with Gemini API

**The system still works!** You get:
- Full funnel analysis
- Experiment recommendations
- ICE prioritization
- Marketing copy
- Basic strategy reasoning

**Solution:** 
- Check API key is set: `$env:GOOGLE_API_KEY`
- Wait 1-2 minutes between requests
- Free tier has very low limits on experimental models

### Server won't start
Check that:
- Virtual environment is activated (see `(.venv)` in terminal)
- All dependencies installed: `pip install -r requirements.txt`
- Port 8000 is available (no other services using it)

### Rate limit errors in terminal
Free tier of Gemini has strict limits:
- `gemini-2.0-flash-exp` model has very low quotas
- Wait several minutes between requests
- System gracefully falls back to deterministic commentary

### Import errors
Verify folder structure matches the layout above and all `__init__.py` files exist.

---

## 📈 Example Business Scenarios

### Scenario 1: Coffee Shop (Visits→Leads problem)
**Input:**
- 2000 visits, only 350 leads captured (82.5% drop)
- Goal: Increase repeat purchases

**Output:**
- Recommendation: **Referral Program**
- Priority Score: 7.5
- Why: Low effort (email), high impact, uses existing customers

### Scenario 2: SaaS Product (Leads→Signups problem)  
**Input:**
- Good lead generation, poor signup conversion
- Goal: Increase trial-to-paid conversion

**Output:**
- Recommendation: **Onboarding nurture sequence**
- Why: Reduces friction, builds trust, automates education

### Scenario 3: E-commerce (Signups→Purchases problem)
**Input:**
- Many signups, few purchases
- Goal: Increase first-time buyers

**Output:**
- Recommendation: **Loyalty punch card**
- Why: Encourages repeat visits, tangible rewards, community building

---

## 🎓 Understanding the Output

### Funnel Insight Breakdown
```json{
"from_step": "visits",
"to_step": "leads",
"drop_rate": 0.825,
"comment": "Biggest drop is from visits to leads: conversion=17.5%, drop=82.5%."
}

- **from_step/to_step:** Which funnel stage has the problem
- **drop_rate:** Percentage of users lost (0-1 scale)
- **comment:** Human-readable explanation

### ICE Scoring Breakdown
```json{
"impact": 5,
"confidence": 3,
"effort": 2,
"priority_score": 7.5
}

- **Impact (1-5):** Potential growth impact
  - 5 = Game-changer
  - 3 = Moderate improvement
  - 1 = Minimal effect
  
- **Confidence (1-5):** Likelihood of success
  - 5 = Proven strategy
  - 3 = Good evidence
  - 1 = Experimental
  
- **Effort (1-5):** Implementation difficulty
  - 1 = Quick win
  - 3 = Moderate work
  - 5 = Major project
  
- **Priority Score:** (Impact × Confidence) / Effort
  - Higher = Do this first
  - Lower = Save for later

---

## 🛠️ Advanced Usage

### Testing Different KPI Scenarios

Test how recommendations change with different metrics:
```bashScenario A: Lead generation problem
{
"kpis": {
"visits": 2000,
"leads": 200,    # Only 10% conversion
"signups": 150,
"purchases": 100
}
}Scenario B: Conversion problem
{
"kpis": {
"visits": 2000,
"leads": 1000,   # Good lead capture
"signups": 800,
"purchases": 50   # Poor purchase conversion
}
}

### Comparing Different Goals

See how goal changes affect recommendations:
```json// Growth goal
{"objective": "increase customer acquisition"}// Retention goal
{"objective": "improve customer lifetime value"}// Efficiency goal
{"objective": "reduce customer acquisition cost"}

### Channel-Specific Constraints

Test how constraints influence experiment selection:
```json{
"constraints": "No paid ads; focus on owned channels"
}
// vs
{
"constraints": "Limited budget; quick wins only"
}
// vs
{
"constraints": "No technical resources; manual tactics only"
}

---

## 📞 Support

### Getting Help
- Review the main **README.md**
- Check API docs at `/docs` endpoint
- Examine server logs in terminal

### Reporting Issues
If you encounter bugs:
1. Check the terminal for error messages
2. Verify all endpoints work individually
3. Test with the provided example data first

---

## 🎯 Quick Reference

**Start Server:**
```bashuvicorn app.main:app --reload

**Test Endpoints:**
- Health: `http://127.0.0.1:8000/health`
- Docs: `http://127.0.0.1:8000/docs`
- Plans: `http://127.0.0.1:8000/plans/demo_sme_001`

**Set API Key:**
```powershell$env:GOOGLE_API_KEY = "your-key-here"

**Common Commands:**
```bashInstall dependencies
pip install -r requirements.txtRun tests
pytest tests/ -vCheck code
python -m app.main

---

**Built by Christopher Crilly Pienaah**  
*Master's in Analytics @ Northeastern University*  
*AI/ML Product Strategy & Data Scientist*