from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import ActionProposal, Customer, Opportunity, AuditLog
from app.schemas import ActionProposalResponse, ActionApproveRequest
from app.services.razorpay_service import RazorpayService, RazorpayExecutionError
from app.services.policy_engine import PolicyEngine
from app.config import settings

router = APIRouter(prefix="/actions", tags=["Actions & HITL"])

@router.get("", response_model=List[ActionProposalResponse])
def list_actions(goal_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lists action proposals and their execution/policy status."""
    query = db.query(ActionProposal)
    if goal_id:
        query = query.filter(ActionProposal.goal_id == goal_id)
    actions = query.order_by(ActionProposal.id.desc()).all()

    results = []
    for act in actions:
        customer_name = act.customer.name if act.customer else None
        results.append(ActionProposalResponse(
            id=act.id,
            opportunity_id=act.opportunity_id,
            goal_id=act.goal_id,
            action_type=act.action_type,
            target_customer_id=act.target_customer_id,
            target_customer_name=customer_name,
            original_price=act.original_price,
            proposed_discount_pct=act.proposed_discount_pct,
            final_price=act.final_price,
            status=act.status,
            policy_check_result=act.policy_check_result,
            rejection_reason=act.rejection_reason,
            alternative_proposal=act.alternative_proposal,
            approved_by_merchant=act.approved_by_merchant,
            razorpay_link_id=act.razorpay_link_id,
            razorpay_short_url=act.razorpay_short_url,
            payment_status=act.payment_status,
            is_simulated=act.is_simulated,
            created_at=act.created_at,
            executed_at=act.executed_at
        ))
    return results

@router.post("/approve", response_model=ActionProposalResponse)
def approve_action(payload: ActionApproveRequest, db: Session = Depends(get_db)):
    """
    Human-in-the-Loop Merchant Approval:
    - Accepts compliant alternative (e.g. 10% cap) OR overrides policy with merchant sign-off.
    - Transitions action from BLOCKED/REQUIRES_APPROVAL to APPROVED.
    - Does not execute a Razorpay action; execution is separately human-triggered.
    """
    action = db.query(ActionProposal).filter(ActionProposal.id == payload.action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action proposal not found.")
    if action.status == "EXECUTED":
        raise HTTPException(status_code=400, detail="Executed actions cannot be approved again.")
    if action.status == "APPROVED":
        raise HTTPException(status_code=400, detail="Action is already approved. Generate the Razorpay Test Link to execute it.")
    if action.status not in ["BLOCKED", "REQUIRES_APPROVAL"]:
        raise HTTPException(status_code=400, detail=f"Action cannot be approved from status: {action.status}.")

    previous_status = action.status
    previous_discount = action.proposed_discount_pct

    # If merchant applied alternative or override discount
    if payload.override_discount_pct is not None:
        action.proposed_discount_pct = payload.override_discount_pct
        action.final_price = round(action.original_price * (1.0 - (payload.override_discount_pct / 100.0)), 2)

    action.approved_by_merchant = True
    action.status = "APPROVED"

    # Record Merchant Approval in Audit Log
    audit = AuditLog(
        timestamp=datetime.utcnow(),
        goal_id=action.goal_id,
        opportunity_id=action.opportunity_id,
        action_id=action.id,
        event_type="MERCHANT_APPROVAL_GRANTED",
        agent_recommendation=f"Execute action at {action.proposed_discount_pct}% discount (Final Price: ₹{action.final_price:,.2f}).",
        reason=payload.merchant_notes or f"Merchant resolved previous status '{previous_status}' and signed off.",
        proposed_amount=action.final_price,
        proposed_discount=action.proposed_discount_pct,
        applicable_policy=f"Previous proposed: {previous_discount}%. Approved: {action.proposed_discount_pct}%",
        policy_result="MERCHANT_OVERRIDE_APPROVED",
        human_approval="APPROVED_BY_MERCHANT",
        razorpay_action="READY_FOR_MERCHANT_EXECUTION",
        final_outcome="Approved with no payment link. Merchant must explicitly generate the Razorpay test link.",
        metadata_json=f'{{"override_discount": {payload.override_discount_pct}, "notes": "{payload.merchant_notes}"}}'
    )
    db.add(audit)
    db.commit()

    db.refresh(action)

    customer_name = action.customer.name if action.customer else None
    return ActionProposalResponse(
        id=action.id,
        opportunity_id=action.opportunity_id,
        goal_id=action.goal_id,
        action_type=action.action_type,
        target_customer_id=action.target_customer_id,
        target_customer_name=customer_name,
        original_price=action.original_price,
        proposed_discount_pct=action.proposed_discount_pct,
        final_price=action.final_price,
        status=action.status,
        policy_check_result=action.policy_check_result,
        rejection_reason=action.rejection_reason,
        alternative_proposal=action.alternative_proposal,
        approved_by_merchant=action.approved_by_merchant,
        razorpay_link_id=action.razorpay_link_id,
        razorpay_short_url=action.razorpay_short_url,
        payment_status=action.payment_status,
        is_simulated=action.is_simulated,
        created_at=action.created_at,
        executed_at=action.executed_at
    )

@router.post("/{action_id}/execute", response_model=ActionProposalResponse)
def execute_action(action_id: int, demo_failure: bool = False, db: Session = Depends(get_db)):
    """Directly executes an already APPROVED action."""
    action = db.query(ActionProposal).filter(ActionProposal.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action proposal not found.")

    if action.status not in ["APPROVED"]:
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be executed. Current status: {action.status}. Merchant approval required."
        )

    if action.action_type == "REFUND" and not settings.AUTONOMOUS_REFUNDS_ENABLED:
        audit = AuditLog(
            timestamp=datetime.utcnow(), goal_id=action.goal_id, opportunity_id=action.opportunity_id,
            action_id=action.id, event_type="POLICY_BLOCKED",
            agent_recommendation="Attempted refund action.",
            reason="Autonomous refunds are disabled by server-side merchant policy.",
            proposed_amount=action.final_price, proposed_discount=action.proposed_discount_pct,
            applicable_policy="Refunds Disabled", policy_result="VIOLATION_BLOCKED",
            human_approval="NOT_PERMITTED", razorpay_action="REFUND_PREVENTED",
            final_outcome="No refund or Razorpay action was executed.", metadata_json=None
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=403, detail="Refunds are disabled by server-side policy.")

    customer = db.query(Customer).filter(Customer.id == action.target_customer_id).first()
    if not customer:
        customer = db.query(Customer).first()

    opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
    desc = f"{opportunity.title if opportunity else 'Exclusive Offer'} - Personalized Special"

    try:
        RazorpayService.create_payment_link(
            db=db, action=action, customer=customer, description=desc,
            force_demo_failure=demo_failure
        )
    except RazorpayExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    db.refresh(action)
    customer_name = action.customer.name if action.customer else None
    return ActionProposalResponse(
        id=action.id,
        opportunity_id=action.opportunity_id,
        goal_id=action.goal_id,
        action_type=action.action_type,
        target_customer_id=action.target_customer_id,
        target_customer_name=customer_name,
        original_price=action.original_price,
        proposed_discount_pct=action.proposed_discount_pct,
        final_price=action.final_price,
        status=action.status,
        policy_check_result=action.policy_check_result,
        rejection_reason=action.rejection_reason,
        alternative_proposal=action.alternative_proposal,
        approved_by_merchant=action.approved_by_merchant,
        razorpay_link_id=action.razorpay_link_id,
        razorpay_short_url=action.razorpay_short_url,
        payment_status=action.payment_status,
        is_simulated=action.is_simulated,
        created_at=action.created_at,
        executed_at=action.executed_at
    )
