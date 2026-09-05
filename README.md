# Revenue Pilot

### AI that finds, plans, and executes your next revenue opportunity.

Revenue Pilot is an AI-powered revenue growth agent for merchants. It analyzes customer, product, and transaction data to identify high-value revenue opportunities, proposes targeted actions, applies merchant-defined guardrails, and executes approved actions through Razorpay Test Mode.

**🚀 Live Demo:** [Open Revenue Pilot](https://razorpay-revenue-pilot-sage.vercel.app/)
**📐 Architecture:** [View Architecture](./architecture/architecture.md)

> **The agent proposes. The policy engine bounds. The approval gate controls. Razorpay executes. The audit trail records.**

---

## Overview

Merchants often have valuable revenue opportunities hidden in their existing customer and transaction data — customers at risk of churning, customers ready for an upsell, or customers who purchased a product but not its complementary products.

Revenue Pilot turns these signals into **actionable and controlled revenue opportunities**.

A merchant can define a revenue goal such as:

> **"Help me generate ₹1,00,000 in additional revenue."**

Revenue Pilot analyzes the available business data, identifies opportunities, estimates potential revenue and ROI, proposes an action, checks it against merchant policies, and routes the approved action to Razorpay.

Every important decision and outcome is recorded in the audit trail.

---

## How It Works

```text
Merchant Goal
     ↓
Analyze Customer + Product + Transaction Data
     ↓
Identify Revenue Opportunities
     ↓
Create Action Proposal
     ↓
Check Merchant Guardrails
     ↓
Auto-Approve OR Request Merchant Approval
     ↓
Execute Approved Action
     ↓
Create Razorpay Test Mode Payment Link
     ↓
Payment / Webhook Outcome
     ↓
Update Revenue + Goal Progress
     ↓
Audit Trail
```

The core operating loop is:

**Analyze → Reason → Plan → Policy Check → Approval → Execute → Observe → Recover → Audit**

---

## Key Features

### 🎯 Revenue Opportunity Detection

Revenue Pilot identifies revenue opportunities across four use cases:

- **VIP Churn Win-Back** — target high-value customers who have become inactive.
- **Cross-Sell** — identify customers who own a product but are missing complementary products.
- **VIP Upsell** — target high-value active customers with relevant higher-value offers.
- **Replenishment** — identify customers likely to need a repeat purchase.

Each opportunity includes:

- Target customer cohort
- Proposed offer
- Projected revenue
- Estimated conversion rate
- Projected ROI
- AI-generated reasoning/explanation

### 🛡️ Merchant Guardrails

Merchants define limits that the system must respect before an action can be executed.

### 👤 Approval-Gated Execution

Actions outside autonomous limits are blocked and routed to the merchant for review.

The merchant can review the proposed action and approve the compliant alternative before execution.

### 💳 Razorpay Payment Links

Approved actions can create **Razorpay Test Mode Payment Links** directly from Revenue Pilot.

### 🔔 Webhook-Based Payment Updates

Revenue Pilot receives Razorpay payment events and updates the corresponding action and revenue state.

### 📋 Explainable Audit Trail

The system records the lifecycle of important actions:

```text
Opportunity
    ↓
Policy Check
    ↓
Approval
    ↓
Razorpay Action
    ↓
Payment
    ↓
Revenue Update
```

This makes it possible to understand **why an action was proposed, what policy decision was made, what happened during execution, and what payment outcome followed**.

### 🚨 Graceful Failure Handling

If Razorpay Test Mode fails while creating a Payment Link:

- No fake payment is recorded.
- The failure is recorded in the audit trail.
- The approved action remains recoverable.
- The merchant can retry the action.

### 🔄 Recovery Protocol

Revenue Pilot also includes a demo recovery flow that responds to a simulated sales drop by selecting a compliant, high-ROI opportunity and routing it through the existing approval and Razorpay execution flow.

---

# Guardrails

Revenue Pilot uses explicit merchant-defined policies to bound revenue actions.

| Guardrail | Current Limit |
|---|---:|
| Maximum autonomous discount | **10%** |
| Maximum campaign budget | **₹20,000** |
| Maximum autonomous transaction | **₹5,000** |
| Refunds | **Disabled** |
| Human approval above discount limit | **Enabled** |

### Example

If the system proposes a **15% discount**:

```text
Proposed:       15%
Merchant Limit: 10%
                  ↓
           POLICY BLOCKED
                  ↓
       Compliant Alternative
                  ↓
                10%
                  ↓
        Merchant Approval
```

The system does not bypass the merchant's policy to execute the original proposal.

---

# Razorpay Integration

Revenue Pilot uses the **Razorpay Payment Links API** to turn approved revenue opportunities into payment actions.

The integration follows this flow:

```text
Approved Action
      ↓
Revenue Pilot Backend
      ↓
Razorpay Payment Links API
      ↓
Razorpay Test Mode Payment Link
      ↓
Test Checkout
      ↓
Payment
      ↓
Razorpay Webhook
      ↓
Revenue Pilot
      ↓
Update Payment + Revenue + Audit
```

The Payment Links API allows Revenue Pilot to connect a revenue decision directly to a payment action.

### Webhooks

Revenue Pilot exposes:

```text
POST /api/webhooks/razorpay
```

The webhook receiver:

1. Reads the raw request body.
2. Validates the Razorpay webhook signature when configured.
3. Processes the Payment Link payment event.
4. Matches the event to the corresponding Revenue Pilot action.
5. Records the payment outcome.
6. Updates application state and audit data.

The implementation uses Razorpay's HMAC-SHA256 webhook signature mechanism.

### Test Mode

All payment execution in this project uses **Razorpay Test Mode**.

**No real money is processed.**

The application also contains a clearly labelled:

> **DEMO / TESTING UTILITY**

for simulating a successful payment outcome during demonstrations.

---

# Failure Handling

Revenue Pilot explicitly handles payment execution failure.

```text
Approved Action
      ↓
Razorpay Execution
      ↓
     FAIL
      ↓
No Payment Link Created
      ↓
Failure Recorded
      ↓
Action Remains Recoverable
```

The system does **not** convert an execution failure into a successful payment or fake revenue.

This demonstrates the principle that money actions must be **bounded, explainable, and auditable**.

---

# Recovery Protocol

Revenue Pilot includes a demo recovery protocol for an unexpected sales drop.

```text
Simulated Sales Drop
        ↓
Recovery Protocol Activated
        ↓
Analyze Existing Opportunities
        ↓
Select Highest-ROI Compliant Opportunity
        ↓
Policy Check
        ↓
Approval / Existing Execution Flow
        ↓
Razorpay Test Mode
        ↓
Revenue + Audit Update
```

The recovery protocol does not bypass the existing guardrails or approval flow.

---

# Architecture

See the detailed architecture:

**[`architecture/architecture.md`](./architecture/architecture.md)**

The system consists of:

- React + Vite frontend
- FastAPI backend
- Revenue analysis and opportunity engine
- Merchant policy engine
- Approval gate
- Razorpay Payment Link executor
- Razorpay webhook receiver
- SQLite application database
- Audit trail

---

# Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- SQLAlchemy

### Database
- SQLite

### Payments
- Razorpay Payment Links API
- Razorpay Test Mode
- Razorpay Webhooks

### Deployment
- **Vercel** — Frontend
- **Render** — Backend

---

# Project Structure

```text
Revenue Pilot/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── api.js
│   └── package.json
│
├── architecture/
│   ├── architecture.md
│   └── architecture.png
│
├── README.md
└── .gitignore
```

---

# Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/dishitasaxenaa/Razorpay-Revenue-Pilot.git
cd Razorpay-Revenue-Pilot
```

## 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will run locally on:

```text
http://127.0.0.1:8000
```

## 3. Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will provide the local frontend URL.

---

# Environment Variables

Create a `.env` file inside `backend/`:

```env
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

DEFAULT_MAX_AUTONOMOUS_DISCOUNT=10
DEFAULT_MAX_CAMPAIGN_BUDGET=20000
```

**Never commit real Razorpay credentials or webhook secrets to the repository.**

---

# Demo Flow

For a quick demonstration:

### 1. Set a revenue goal

Example:

```text
Help me generate ₹1,00,000 in additional revenue.
```

### 2. Run AI Growth Analysis

Revenue Pilot analyzes the merchant's data and generates revenue opportunities.

### 3. Review Opportunities

Explore:

- Target customers
- Offer
- Projected revenue
- ROI
- AI reasoning
- Policy status

### 4. Demonstrate the Guardrail

Open the VIP Churn Win-Back opportunity.

The system proposes **15%**, while the merchant's autonomous limit is **10%**.

Revenue Pilot blocks the original action and proposes a compliant **10% alternative**.

### 5. Approve an Action

Approve the compliant action.

### 6. Generate Razorpay Test Link

Revenue Pilot creates a Razorpay **Test Mode Payment Link**.

### 7. Complete Test Payment

Open the test link and complete the payment using Razorpay's Test Mode payment flow.

### 8. Verify the Result

Return to Revenue Pilot and view:

- Payment status
- Updated revenue
- Goal progress
- Audit Trail

### 9. Demonstrate Failure Handling

Use the demo failure utility to simulate a Razorpay execution failure and show that:

- No fake payment is created.
- The failure is recorded.
- The action remains recoverable.

---

# Test Mode Notice

This project is built using **Razorpay Test Mode**.
Payment Links and checkout transactions shown in the demo are for testing and evaluation only.
The application's payment simulator is explicitly labelled **DEMO / TESTING UTILITY** and should not be interpreted as a real payment.

---

# Razorpay Buildathon — Track 01

Revenue Pilot is built for **AI Growth & Agentic Commerce**.
The project focuses on the merchant-side revenue growth problem:
> **Identify a revenue opportunity → make a bounded decision → get approval where required → execute through Razorpay → observe the outcome.**

The implementation specifically demonstrates:

- Revenue opportunity discovery
- Controlled agent actions
- Merchant-defined guardrails
- Human approval for bounded actions
- Razorpay payment execution
- Payment event handling
- Explainable decisions
- Auditability
- Graceful failure and recovery

---

# Design Principle

> **The agent proposes.**  
> **The policy engine bounds.**  
> **The approval gate controls.**  
> **Razorpay executes.**  
> **The audit trail records.**
