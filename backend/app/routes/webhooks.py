import json
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import ActionProposal
from app.schemas import SimulatePaymentRequest
from app.services.razorpay_service import RazorpayService

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Payment Simulation"])

@router.post("/razorpay")
async def razorpay_webhook_receiver(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Real Razorpay Test Mode Webhook Endpoint.
    Captures 'payment_link.paid' and 'payment.captured' events.
    Verifies HMAC signature.
    """
    raw_body = await request.body()

    # Verify signature if header present
    if x_razorpay_signature:
        is_valid = RazorpayService.verify_webhook_signature(raw_body, x_razorpay_signature)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid Razorpay webhook signature.")

    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed webhook JSON payload.")

    event = data.get("event")
    payload = data.get("payload", {})

    action_id = None
    payment_id = None

    if event == "payment_link.paid":
        plink_entity = payload.get("payment_link", {}).get("entity", {})
        notes = plink_entity.get("notes", {})
        action_id = notes.get("action_id")
        payment_id = payload.get("payment", {}).get("entity", {}).get("id")

        if not action_id:
            # Try to match by razorpay_link_id
            link_id = plink_entity.get("id")
            action = db.query(ActionProposal).filter(ActionProposal.razorpay_link_id == link_id).first()
            if action:
                action_id = action.id

    elif event == "payment.captured":
        payment_entity = payload.get("payment", {}).get("entity", {})
        notes = payment_entity.get("notes", {})
        action_id = notes.get("action_id")
        payment_id = payment_entity.get("id")

    if action_id:
        result = RazorpayService.record_payment_outcome(
            db=db,
            action_id=int(action_id),
            is_simulated_demo=False,
            payment_id=payment_id
        )
        return {"status": "PROCESSED", "result": result}

    return {"status": "IGNORED", "event": event, "reason": "No matching ActionProposal found in notes."}

@router.post("/simulate")
def simulate_payment_demo(
    payload: SimulatePaymentRequest,
    db: Session = Depends(get_db)
):
    """
    =======================================================
    DEMO / TESTING UTILITY ONLY
    =======================================================
    This endpoint simulates the arrival of a successful customer 
    payment for hackathon live judging presentations.
    It is explicitly tagged as simulated in the database and audit trail.
    """
    action = db.query(ActionProposal).filter(ActionProposal.id == payload.action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="ActionProposal not found.")

    if not action.razorpay_link_id:
        raise HTTPException(
            status_code=400,
            detail="Action has not been executed yet. A Razorpay test link must be generated before payment can be received or simulated."
        )

    result = RazorpayService.record_payment_outcome(
        db=db,
        action_id=action.id,
        is_simulated_demo=True, # Explicitly flagged as demo simulation!
        payment_id=f"pay_sim_{action.id}"
    )

    return {
        "status": "SIMULATED_SUCCESS",
        "notice": "DEMO / TESTING UTILITY: Payment outcome simulated for evaluation purposes.",
        "details": result
    }
