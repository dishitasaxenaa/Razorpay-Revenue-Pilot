from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Goal, MerchantPolicy, AuditLog
from app.schemas import GoalCreate, GoalResponse, PolicyResponse, PolicyUpdate
from app.services.policy_engine import PolicyEngine

router = APIRouter(prefix="/goals", tags=["Goals & Policies"])

@router.get("/active", response_model=GoalResponse)
def get_active_goal(db: Session = Depends(get_db)):
    """Retrieves current active merchant revenue goal."""
    goal = db.query(Goal).filter(Goal.status == "ACTIVE").order_by(Goal.id.desc()).first()
    if not goal:
        # Fallback to last created goal or create default
        goal = Goal(
            prompt="Help me generate ₹1,00,000 additional revenue.",
            target_amount=100000.0,
            realized_amount=0.0,
            projected_amount=0.0,
            status="ACTIVE"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal

@router.post("", response_model=GoalResponse)
def set_revenue_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    """Creates a new merchant revenue goal."""
    # Extract target amount from prompt if not explicitly given
    target = payload.target_amount
    if not target:
        # Simple extraction heuristic for Indian rupee formats e.g. 1,00,000 or 50000
        cleaned = payload.prompt.replace("₹", "").replace(",", "").replace("INR", "").strip()
        import re
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            target = float(numbers[0])
        else:
            target = 100000.0

    goal = Goal(
        prompt=payload.prompt,
        target_amount=target,
        realized_amount=0.0,
        projected_amount=0.0,
        status="ACTIVE"
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    # Log in audit trail
    audit = AuditLog(
        timestamp=datetime.utcnow(),
        goal_id=goal.id,
        event_type="GOAL_SET",
        agent_recommendation=f"Merchant initialized revenue target of ₹{goal.target_amount:,.2f}.",
        reason=f"Goal prompt: '{goal.prompt}'",
        proposed_amount=goal.target_amount,
        proposed_discount=None,
        applicable_policy="Merchant Growth Directive",
        policy_result="ACCEPTED",
        human_approval="MERCHANT_INITIATED",
        razorpay_action=None,
        final_outcome=f"Target ₹{goal.target_amount:,.2f} recorded. Ready for data analysis.",
        metadata_json=None
    )
    db.add(audit)
    db.commit()

    return goal

@router.get("/policy", response_model=PolicyResponse)
def get_merchant_policy(db: Session = Depends(get_db)):
    """Fetches active merchant policy guardrails."""
    return PolicyEngine.get_active_policy(db)

@router.put("/policy", response_model=PolicyResponse)
def update_merchant_policy(payload: PolicyUpdate, db: Session = Depends(get_db)):
    """Updates merchant guardrail rules."""
    policy = PolicyEngine.get_active_policy(db)
    if payload.max_autonomous_discount_pct is not None:
        policy.max_autonomous_discount_pct = payload.max_autonomous_discount_pct
    if payload.max_campaign_budget is not None:
        policy.max_campaign_budget = payload.max_campaign_budget
    if payload.require_human_approval_over_discount is not None:
        policy.require_human_approval_over_discount = payload.require_human_approval_over_discount
    
    db.commit()
    db.refresh(policy)

    # Record policy update in audit trail
    audit = AuditLog(
        timestamp=datetime.utcnow(),
        event_type="POLICY_UPDATED",
        agent_recommendation=f"Merchant updated guardrails: Max Autonomous Discount = {policy.max_autonomous_discount_pct}%",
        reason="Manual merchant policy configuration adjustment",
        proposed_amount=None,
        proposed_discount=policy.max_autonomous_discount_pct,
        applicable_policy="Guardrail Modification",
        policy_result="APPLIED",
        human_approval="MERCHANT_MODIFIED",
        razorpay_action=None,
        final_outcome="Subsequent agent proposals will adhere to new guardrails.",
        metadata_json=None
    )
    db.add(audit)
    db.commit()

    return policy
