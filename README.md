# RevenueSystem — AI Revenue Growth Agent for Merchants

**Track**: Razorpay AI Buildathon 2026 — Track 01: "AI Growth & Agentic Commerce"  
**Project**: RevenueSystem  
**Store Profile**: *Aura Living* (D2C Lifestyle, Wellness & Fragrance Brand)

---

## 🎯 Executive Summary & Core Idea

Most e-commerce merchants are overwhelmed by passive analytics dashboards that state problems without taking action (*"Your churn is 14%"*).

**RevenueSystem** transforms analytics into **Agentic Commerce**:
1. The merchant provides a high-level financial directive:  
   👉 **`"Help me generate ₹1,00,000 additional revenue."`**
2. The agent analyzes historical store transactions, customer RFM segments, and product affinity patterns using **deterministic Python analytics**.
3. It decomposes the revenue goal into **quantified, ranked growth opportunities** (Win-Back, Cross-Sell, VIP Upsell, Consumable Replenishment).
4. It enforces **strict merchant guardrails** (e.g. maximum autonomous discount limit of 10%).
5. **The agent NEVER directly executes money-related actions autonomously without policy clearance.**
6. When an action complies or is approved via Human-in-the-Loop (HITL), it **executes real Razorpay Test-Mode Payment Links** (`https://rzp.io/i/...`).
7. Incoming test payments or simulated webhooks update the merchant's revenue goal in real time and trigger **lightweight learning** across customer profiles.
8. A **first-class Audit Trail** logs every decision, reason, policy check, human sign-off, and payment receipt for complete explainability.

---

## 🛡️ Demonstrable Failure Scenario (Strict Guardrail Enforcement)

As mandated by safe agentic principles:
- **Default Policy**: Maximum autonomous discount capped at **`10.0%`**.
- **Agent Proposal**: For the *VIP Churn Win-Back Campaign*, the AI reasoning layer targets a **`15.0%`** discount on a ₹4,999 luxury hamper to maximize dormant reactivation.
- **Policy Engine Interception**: The Policy Engine intercepts the action and marks it as **`VIOLATION_BLOCKED`**.
- **Explainability**: The agent explains why 15% was proposed, cites the violated 10% policy, and automatically formulates an allowed **`10.0%` compliant alternative** (Price: ₹4,499.10).
- **Human-in-the-Loop**: The merchant reviews the proposal in the HITL Modal, signs off on the compliant alternative (or provides an explicit override), triggering Razorpay test link execution.
- **Audit Log**: The entire chain of events (`POLICY_BLOCKED` → `MERCHANT_APPROVAL_GRANTED` → `RAZORPAY_LINK_CREATED`) is immutably recorded in SQLite.

---

## 🏗️ Architecture & Tech Stack

```
RevenueSystem/
├── backend/                  # FastAPI + SQLite + Razorpay Python SDK
│   ├── app/
│   │   ├── main.py           # FastAPI entry point, CORS & Lifespan
│   │   ├── config.py         # App configuration & guardrail defaults
│   │   ├── database.py       # SQLite engine (revenue_system.db)
│   │   ├── models.py         # Customer, Product, Order, Goal, Opportunity, ActionProposal, AuditLog
│   │   ├── schemas.py        # Pydantic validation schemas
│   │   ├── seed_data.py      # 60 realistic customers, 12 products, 210 historical orders
│   │   ├── services/
│   │   │   ├── analyzer.py   # Deterministic Python calculations (AOV, RFM, affinity, ROI)
│   │   │   ├── agent.py      # Claude reasoning layer (strategy synthesis & campaign copy)
│   │   │   ├── policy_engine.py # Deterministic guardrail validation & failure handling
│   │   │   └── razorpay_service.py # Razorpay Test-Mode SDK & Webhook processor
│   │   └── routes/           # /goals, /opportunities, /actions, /webhooks, /audit, /analytics
│   ├── test_app.py           # Comprehensive end-to-end test suite
│   ├── requirements.txt
│   └── .env
├── frontend/                 # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Store metrics pill & demo reset button
│   │   │   ├── GoalHero.jsx          # Dynamic multi-tier revenue progress bar
│   │   │   ├── OpportunityPipeline.jsx # AI Growth Cards with policy badges
│   │   │   ├── ApprovalModal.jsx     # HITL sign-off & demonstrable failure resolver
│   │   │   ├── RazorpayLivePanel.jsx # Test checkout table with Payment Simulator
│   │   │   ├── AuditTimeline.jsx     # First-class explainability log
│   │   │   └── PolicyModal.jsx       # Guardrail settings configurator
│   │   ├── api.js            # API client
│   │   ├── App.jsx           # Main merchant dashboard
│   │   └── main.jsx
│   └── package.json
├── run_backend.bat           # One-click Windows backend runner
├── run_frontend.bat          # One-click Windows frontend runner
└── README.md
```

---

## ⚡ Quickstart & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Start Backend Server
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend automatically seeds the SQLite database (`revenue_system.db`) with 60 customer profiles, 12 products, and 210 historical orders on first startup.*

### 2. Start Frontend Dashboard
```powershell
cd frontend
npm run dev
```
Open **http://localhost:5173** in your browser.

*(On Windows, you can also simply double-click `run_backend.bat` and `run_frontend.bat`).*

---

## 🧪 Running Automated Verification Tests

The test suite validates the entire deterministic mathematics, policy guardrails, demonstrable failure interception, and Razorpay test payment flow:

```powershell
cd backend
python -u test_app.py
```

All 8 assertion steps pass out of the box.

---

## 💳 Razorpay Test-Mode Integration

| Component | Test Mode Behavior |
| :--- | :--- |
| **Payment Links API** | Generates real test checkout URLs (`https://rzp.io/i/...`) for approved merchant opportunities. |
| **Webhooks** | Listens to `payment_link.paid` and `payment.captured` with HMAC SHA256 verification. |
| **Payment Simulator** | Clearly labeled in the UI as **`[DEMO / TESTING UTILITY]`** to trigger instant payments during hackathon judging presentations without manual test card entry. |
| **Lightweight Learning** | Upon payment capture, increments customer spend, advances orders count, transitions dormant VIPs to `REACTIVATED_VIP`, and appends a verified purchase order. |

---

## 📜 Audit Trail First-Class Features

Every single money-related event logs:
- `timestamp`: Exact UTC time of the event
- `goal`: Active merchant target (e.g. ₹1,00,000)
- `opportunity`: Specific growth campaign
- `agent_recommendation`: What the AI proposed
- `reason`: Full natural-language decision explainability
- `proposed_amount / proposed_discount`: Numerical values
- `applicable_policy`: Active merchant policy rule evaluated
- `policy_result`: `VIOLATION_BLOCKED`, `PASSED`, `MERCHANT_OVERRIDE_APPROVED`
- `human_approval`: `NOT_REQUIRED`, `PENDING`, `APPROVED_BY_MERCHANT`
- `razorpay_action`: Test link ID and checkout URL
- `final_outcome`: Realized outcome or reason for block
