# 🛡️ Globot Shield: Securing Global Lifelines (v2.2.20260201)

> **Google Gemini 3 Hackathon Entry - Powered by Gemini 2.0**

![Globot Dashboard](ai-sales-mvp/frontend/src/assets/dashboard_preview.png)

## 📖 Project Overview

**Globot** represents a paradigm shift in global trade risk management. Unlike traditional static dashboards, Globot is an **Agentic AI system** capable of real-time proactive monitoring, analysis, and mitigation of supply chain risks.

> 💡 *"We are not just optimizing spreadsheets; we are securing the lifelines of the global economy."*

### 🌍 Social Impact (Potential Impact)

When Globot helps Maersk quickly reroute during the Red Sea crisis, it means:
- 🌾 **Kenya's grain** won't be cut off
- 🔥 **Europe's natural gas** will last through the winter
- 🏥 **Hospital emergency equipment** won't be stuck at the port

This version (**v2.1.20260131**) is a specifically built **"High-Fidelity Mock"** version designed to ensure absolute stability and high impact during the demonstration. It simulates a realistic "4:55 PM Crisis Scenario" (Hormuz Strait geopolitical crisis) and fully demonstrates the **AI Chain-of-Thought (CoT)** and **Human-in-the-Loop** decision-making process.

## 🌟 Core Features (v2.1 Upgrade)

### 1. 🧠 Visualized AI Chain-of-Thought (CoT)

- **Real-time Reasoning Display**: Line-by-line display of the AI's thinking process like a "typewriter", no longer a black box.
- **Multi-Agent Debate**: Side-by-side adversarial debate (Red Team vs. Blue Team) to ensure decision robustness.
- **Citation Traceability**: Each reasoning step is linked to specific RAG knowledge base documents or real-time news sources.

### 2. 🤖 Multi-Agent Collaboration Engine (5-Agent Reasoning Engine)

Showcases a team of 5 specialized AI Agents working together:

- **🔭 Market Sentinel**: Monitors Reuters/Bloomberg for geopolitical signals (Mock API supports multiple scenarios: Red Sea crisis, port congestion, etc.).
- **🛡️ Financial Hedge Agent**: Provides real-time analysis of fuel prices, exchange rates, and freight risks. Offers intelligent hedging strategies (futures, options, forwards) for both normal and crisis modes. Dynamically calculates reroute fuel costs (+$180K) and freight fluctuations.
- **🚢 Logistics Orchestrator**: Replans routes to avoid conflict zones.
- **📋 Compliance Manager**: Uses **Gemini 2M Token Context Window** to analyze 500-page insurance terms and sanction lists.
- **⚖️ Adversarial Debate**: Red-team tests decisions to prevent hallucinations.

### 3. 📸 Visual Risk Intelligence (Satellite Image Analysis) - NEW

Leverages **Gemini Vision** multimodal capabilities:

- **Satellite Image Analysis**: Real-time detection of port congestion, canal blockages, and container pile-ups.
- **Suez Canal Scenario**: Early warning for Ever Given-type events (6 hours before official announcements).
- **Visual Evidence**: Embeds satellite screenshots into decisions as reasoning evidence.

### 4. 📄 Long Document Compliance Analysis - NEW

Showcases the advantage of the Gemini long context window:

- **500 Pages of Maritime Insurance Terms**: Automatic parsing and route compliance verification.
- **OFAC/UN Sanctions Lists**: Real-time cross-checking (2M tokens context).
- **MLC 2006 Convention**: Automatic verification of crew qualifications.

### 5. � Aviation-Grade Logistics Holographic Map (Deck.gl)

- **Routes and Ports**: Visualizes major global shipping lanes and core ports like Shanghai, Rotterdam, and Los Angeles.
- **Interactive Vessels**: Click on yellow ship icons on the map to view detailed cargo manifests and voyage status.
- **Dynamic Risk**: Affected areas highlight and pulse with alerts when a crisis occurs.

### 👨‍✈️ 6. Human-in-the-Loop

- **Decision Confirmation**: After the AI makes a recommendation, a human must click **"Approve & Execute"** for it to take effect, reflecting responsible AI principles.
- **Multiple Options**: Provides "Details" and "Override" (manual intervention) options.

### 🔒 7. Enterprise-Grade Authentication & Security

- **Multi-Channel Login**: Integrated with Clerk, supporting Google, Facebook, LinkedIn social logins, and email/SMS verification codes.
- **Admin Console**: A visualized dashboard designed specifically for administrators to monitor global system KPIs.
- **Security Whitelist**: An email whitelist system based on environment variables to ensure the privacy and security of management permissions.

### 🔌 Pluggable Architecture (Pluggable Data Sources)

The **Reasoning Engine** in this project is generic. The current use of Mock data is a Hackathon limitation. For production, it can directly connect to:

| Data Source | Purpose | Replacement Method |
| :--- | :--- | :--- |
| Bloomberg Terminal API | Real-time market data, geopolitical events | Replace `mock_knowledge_base.py` |
| MarineTraffic API | Real-time AIS vessel positioning | Replace `demo/cot_data.py` |
| Sentinel-2 Satellite API | Port/canal satellite imagery | Replace `visual_risk_service.py` |
| Reuters/Bing News API | Real-time news feeds | Replace Market Sentinel data source |

## 🎯 Target Customers

| Industry | Example Companies | User Roles |
| :--- | :--- | :--- |
| Shipping & Logistics | Maersk, COSCO | NOC Manager, Control Tower Lead |
| High-End Manufacturing | Tesla, Apple | Global Supply Manager, Resiliency PM |
| Commodity Trading | Cargill, Glencore | Commodity Logistics Risk Lead |
| Freight Forwarding | Flexport | Trade Compliance Officer |

## 🚀 Quick Start

### 1. Start Backend

#### Prerequisites
- Python 3.11

#### Installation Steps

```bash
# Enter backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
 venv\Scripts\activate.bat
# macOS/Linux:
 source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create a .env file in the backend directory, refer to core configuration:
# CLERK_ISSUER_URL=...
# ADMIN_WHITELIST=...

# Start server
python start_server.py
```
_Backend runs at `http://localhost:8000`_

### 2. Start Frontend

```bash
cd frontend
npm install

# Configure environment variables
# Create a .env file in the frontend directory:
# VITE_CLERK_PUBLISHABLE_KEY=...
# VITE_ADMIN_WHITELIST=...

npm run dev
```
_Frontend runs at `http://localhost:5173`_

### 3. Demo Path

1. Open browser and visit: `http://localhost:5173/pay`
2. Click **"Watch Demo"**, redirecting to route selection (`/port`).
3. Confirm route (default Shanghai -> Rotterdam), click **"Start Simulation"** to enter the demo (`/demo`).
4. Observe the AI reasoning process and click confirm when the "Approve & Execute" button appears.

## 📂 Key Files Description

- `updates/README.md`: Detailed step-by-step demonstration instructions (must-read for new users).
- `task.md`: Project development task checklist.
- `updates/README.md`: Service startup and troubleshooting cheat sheet.

## 💰 Financial Hedging System (NEW)

Globot now includes a comprehensive financial risk hedging system for managing:

### Risk Categories
- **Fuel Price Risk**: Hedging bunker fuel price fluctuations using futures, options, and swaps.
- **Currency Risk**: Locking in exchange rates through forward contracts and currency swaps.
- **Freight Rate Risk**: A combination strategy of long-term charter contracts and spot markets.

### Features
- ✅ AI-powered risk assessment with Value at Risk (VaR) calculations
- ✅ Automated hedging strategy recommendations (normal & crisis modes)
- ✅ Real-time market data simulation
- ✅ Crisis detection and emergency hedging protocols
- ✅ Multi-instrument portfolio optimization

### API Endpoints
```bash
# Health check
GET http://localhost:8000/api/hedge/health

# Get market data
GET http://localhost:8000/api/hedge/market-data

# Assess risk exposure
POST http://localhost:8000/api/hedge/assess-risk

# Get hedging recommendations
POST http://localhost:8000/api/hedge/recommend

# Activate crisis hedging
POST http://localhost:8000/api/hedge/crisis-activate

# Generate executive report
POST http://localhost:8000/api/hedge/report
```

### Documentation
- **API Documentation**: `backend/docs/HEDGING_API.md`
- **Strategy Guide**: `backend/docs/HEDGING_STRATEGY_GUIDE.md`
- **Claude Skill**: `backend/claude_skill/financial_hedging/SKILL.md`

### Quick Test
```bash
cd backend
python test_hedging_system.py
```

---

**Maintainer**: Vector897
**License**: MIT
