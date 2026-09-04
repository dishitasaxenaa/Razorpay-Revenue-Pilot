from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import ActionProposal, Customer, Opportunity, AuditLog
from app.schemas import ActionProposalResponse, ActionApproveRequest
from app.services.razorpay_service import RazorpayService, RazorpayExecutionError
from app.services.policy_engine import PolicyEngine

router = APIRouter(prefix="/actions", tags=["Actions & HITL"])


def _to_response(act: ActionProposal) -> ActionProposalResponse:
    customer_name = act.customer.name if act.customer else None
    return ActionProposalResponse(
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
    )


@router.get("", response_model=List[ActionProposalResponse])
def list_actions(goal_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lists action proposals and their execution/policy status."""
    query = db.query(ActionProposal)
    if goal_id:
        query = query.filter(ActionProposal.goal_id == goal_id)
    actions = query.order_by(ActionProposal.id.desc()).all()
    return [_to_response(act) for act in actions]


@router.post("/demo/force-next-execution-failure")
def arm_demo_execution_failure():
    """
    =======================================================
    DEMO / TESTING UTILITY ONLY
    =======================================================
    Arms the next Razorpay execute call to fail deterministically.
    Does not contact Razorpay. Does not affect subsequent retries after that one failure.
    """
    RazorpayService.arm_next_execution_failure()
    return {
        "status": "ARMED",
        "notice": (
            "DEMO / TESTING UTILITY: The next Generate Razorpay Test Link attempt will fail on purpose. "
            "No payment link will be created. The action will stay APPROVED so you can retry."
        ),
        "armed": True,
    }


@router.get("/demo/failure-status")
def demo_failure_status():
    armed = RazorpayService.is_next_execution_failure_armed()
    return {
        "armed": armed,
        "notice": "DEMO / TESTING UTILITY" if armed else "Normal Razorpay TEST MODE execution.",
    }


@router.post("/approve", response_model=ActionProposalResponse)
def approve_action(payload: ActionApproveRequest, db: Session = Depends(get_db)):
    """
    Human-in-the-Loop Merchant Approval:
    - Accepts compliant alternative (e.g. 10% cap) OR overrides policy with merchant sign-off.
    - Transitions action from BLOCKED/REQUIRES_APPROVAL to APPROVED.
    - Does NOT create a Razorpay Payment Link.
    """
    action = db.query(ActionProposal).filter(ActionProposal.id == payload.action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action proposal not found.")

    if action.status == "EXECUTED":
        raise HTTPException(status_code=400, detail="This action has already been executed.")

    if "REFUND" in (action.action_type or "").upper():
        raise HTTPException(status_code=403, detail="Refunds are disabled by merchant policy.")

    previous_status = action.status
    previous_discount = action.proposed_discount_pct

    if payload.override_discount_pct is not None:
        action.proposed_discount_pct = payload.override_discount_pct
        action.final_price = round(action.original_price * (1.0 - (payload.override_discount_pct / 100.0)), 2)

    action.approved_by_merchant = True
    action.status = "APPROVED"

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
        razorpay_action="NOT_EXECUTED",
        final_outcome="Approved. Awaiting explicit merchant action to generate Razorpay TEST MODE payment link.",
        metadata_json=f'{{"override_discount": {payload.override_discount_pct}, "notes": "{payload.merchant_notes}"}}'
    )
    db.add(audit)
    db.commit()
    db.refresh(action)
    return _to_response(action)


@router.post("/{action_id}/execute", response_model=ActionProposalResponse)
def execute_action(action_id: int, db: Session = Depends(get_db)):
    """Creates a Razorpay TEST MODE Payment Link for an already APPROVED action."""
    action = db.query(ActionProposal).filter(ActionProposal.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action proposal not found.")

    if action.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be executed. Current status: {action.status}. Merchant approval required."
        )

    if action.razorpay_link_id:
        raise HTTPException(
            status_code=400,
            detail="A Razorpay payment link already exists for this action."
        )

    try:
        PolicyEngine.assert_can_execute(db, action)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    customer = db.query(Customer).filter(Customer.id == action.target_customer_id).first()
    if not customer:
        customer = db.query(Customer).first()

    opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
    desc = f"{opportunity.title if opportunity else 'Exclusive Offer'} - Personalized Special"

    try:
        RazorpayService.create_payment_link(
            db=db,
            action=action,
            customer=customer,
            description=desc
        )
    except RazorpayExecutionError as exc:
        db.refresh(action)
        raise HTTPException(status_code=502, detail=exc.merchant_message)

    db.refresh(action)
    return _to_response(action)
