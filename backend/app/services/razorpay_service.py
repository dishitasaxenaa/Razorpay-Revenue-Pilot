import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional
import razorpay
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ActionProposal, Customer, Order, Goal, AuditLog, Opportunity


MERCHANT_EXECUTION_FAILURE_MESSAGE = (
    "Razorpay payment link creation failed. No payment action was executed. You can retry."
)
DEMO_EXECUTION_FAILURE_MESSAGE = (
    "[DEMO / TESTING UTILITY] Razorpay payment link creation failed. "
    "No payment action was executed. You can retry."
)


class RazorpayExecutionError(Exception):
    """Raised when a Razorpay TEST MODE payment link is not created. Action stays retryable."""

    def __init__(self, merchant_message: str, is_demo: bool = False):
        self.merchant_message = merchant_message
        self.is_demo = is_demo
        super().__init__(merchant_message)


class RazorpayService:
    """
    Razorpay Test Mode Integration Service.
    - Operates STRICTLY in TEST MODE.
    - Generates Razorpay Test Payment Links.
    - Verifies Webhooks.
    - Dispatches clearly labeled DEMO/TESTING simulated payments.
    - Implements lightweight learning by updating customer & order records.
    """

    _force_next_execution_failure = False

    @classmethod
    def arm_next_execution_failure(cls) -> None:
        """DEMO / TESTING UTILITY: next create_payment_link call fails without contacting Razorpay."""
        cls._force_next_execution_failure = True

    @classmethod
    def is_next_execution_failure_armed(cls) -> bool:
        return cls._force_next_execution_failure

    @classmethod
    def consume_demo_failure_flag(cls) -> bool:
        armed = cls._force_next_execution_failure
        cls._force_next_execution_failure = False
        return armed

    @classmethod
    def get_client(cls) -> Optional[razorpay.Client]:
        """Initializes Razorpay Python SDK Client in Test Mode."""
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET

        if not key_id or "placeholder" in key_id.lower() or "yourtestkey" in key_id.lower():
            return None

        # Guardrail: Ensure strictly test key
        if not key_id.startswith("rzp_test_"):
            raise ValueError("SECURITY ALERT: Razorpay client must be configured with a TEST key starting with 'rzp_test_'!")

        return razorpay.Client(auth=(key_id, key_secret))

    @classmethod
    def _record_execution_failure(
        cls,
        db: Session,
        action: ActionProposal,
        customer: Optional[Customer],
        is_demo: bool,
    ) -> None:
        """Persist a failure audit event. Does not mark EXECUTED or store a payment link."""
        customer_label = customer.name if customer else "target customer"
        event_type = "DEMO_RAZORPAY_EXECUTION_FAILED" if is_demo else "RAZORPAY_EXECUTION_FAILED"
        reason = (
            "[DEMO / TESTING UTILITY] Intentional execution failure for hackathon judging. "
            "No Razorpay Payment Link was created. Action remains APPROVED and retryable."
            if is_demo
            else (
                f"Razorpay TEST MODE did not create a payment link for {customer_label}. "
                "No money action was executed. Action remains APPROVED and retryable."
            )
        )
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type=event_type,
            agent_recommendation=f"Create Razorpay TEST MODE payment link for ₹{action.final_price:,.2f}.",
            reason=reason,
            proposed_amount=action.final_price,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy="Razorpay TEST MODE execution; no silent fallback links",
            policy_result="EXECUTION_FAILED",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action="PAYMENT_LINK_NOT_CREATED",
            final_outcome="Execution failed. Status remains APPROVED. Merchant can retry.",
            metadata_json='{"executed": false, "razorpay_link_id": null}',
        )
        db.add(audit_log)
        db.commit()

    @classmethod
    def create_payment_link(
        cls,
        db: Session,
        action: ActionProposal,
        customer: Customer,
        description: str
    ) -> Dict[str, Any]:
        """
        Creates a TEST MODE payment link via the real Razorpay API.
        On failure: no fake link, action stays APPROVED, explicit audit + error.
        """
        attempt_audit = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type="RAZORPAY_EXECUTION_ATTEMPTED",
            agent_recommendation=f"Execute payment link for ₹{action.final_price:,.2f} ({action.proposed_discount_pct}% discount).",
            reason=f"Merchant triggered Razorpay TEST MODE link creation for {customer.name}.",
            proposed_amount=action.final_price,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy="Approved action only; TEST MODE credentials required (rzp_test_)",
            policy_result="EXECUTION_IN_PROGRESS",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action="CREATE_PAYMENT_LINK",
            final_outcome="Calling Razorpay TEST MODE Payment Links API.",
            metadata_json=None,
        )
        db.add(attempt_audit)
        db.commit()

        if cls.consume_demo_failure_flag():
            cls._record_execution_failure(db, action, customer, is_demo=True)
            raise RazorpayExecutionError(DEMO_EXECUTION_FAILURE_MESSAGE, is_demo=True)

        try:
            client = cls.get_client()
        except ValueError:
            cls._record_execution_failure(db, action, customer, is_demo=False)
            raise RazorpayExecutionError(MERCHANT_EXECUTION_FAILURE_MESSAGE)

        if not client:
            cls._record_execution_failure(db, action, customer, is_demo=False)
            raise RazorpayExecutionError(MERCHANT_EXECUTION_FAILURE_MESSAGE)

        amount_in_paise = int(round(action.final_price * 100))
        ref_id = f"REV_ACT_{action.id}_{int(time.time())}"

        try:
            payload = {
                "amount": amount_in_paise,
                "currency": "INR",
                "accept_partial": False,
                "reference_id": ref_id,
                "description": description,
                "customer": {
                    "name": customer.name,
                    "email": customer.email,
                    "contact": customer.phone
                },
                "notify": {
                    "sms": False,
                    "email": False
                },
                "reminder_enable": False,
                "notes": {
                    "goal_id": str(action.goal_id),
                    "opportunity_id": str(action.opportunity_id),
                    "action_id": str(action.id),
                    "discount_pct": str(action.proposed_discount_pct)
                }
            }
            response = client.payment_link.create(payload)
            link_id = response.get("id")
            short_url = response.get("short_url")
            if not link_id or not short_url:
                raise RazorpayExecutionError(MERCHANT_EXECUTION_FAILURE_MESSAGE)
        except RazorpayExecutionError:
            cls._record_execution_failure(db, action, customer, is_demo=False)
            raise
        except Exception:
            cls._record_execution_failure(db, action, customer, is_demo=False)
            raise RazorpayExecutionError(MERCHANT_EXECUTION_FAILURE_MESSAGE)

        action.razorpay_link_id = link_id
        action.razorpay_short_url = short_url
        action.status = "EXECUTED"
        action.executed_at = datetime.utcnow()
        action.is_simulated = False
        if not action.payment_status:
            action.payment_status = "PENDING"

        opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
        if opportunity:
            opportunity.status = "IN_PROGRESS"

        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type="RAZORPAY_LINK_CREATED",
            agent_recommendation=f"Execute payment link for ₹{action.final_price:,.2f} ({action.proposed_discount_pct}% discount).",
            reason=f"Policy approved. Created Razorpay test payment link for customer {customer.name}.",
            proposed_amount=action.final_price,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy=f"Approved with discount {action.proposed_discount_pct}%",
            policy_result="EXECUTED",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action=f"Created Payment Link {link_id} ({short_url}) via TEST_API",
            final_outcome="Payment link active. Awaiting customer payment.",
            metadata_json=f'{{"razorpay_link_id": "{link_id}", "short_url": "{short_url}", "mode": "TEST_API"}}'
        )
        db.add(audit_log)
        db.commit()
        db.refresh(action)

        return {
            "link_id": link_id,
            "short_url": short_url,
            "amount": action.final_price,
            "mode": "TEST_API"
        }

    @classmethod
    def record_payment_outcome(
        cls,
        db: Session,
        action_id: int,
        is_simulated_demo: bool = False,
        payment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a successful payment outcome (via Webhook or Demo Simulator).
        Implements lightweight learning:
        - Updates Goal realized amount.
        - Creates new completed Order.
        - Updates Customer total_spent, orders_count, and last_order_date.
        - Records transparent audit log with clear simulated vs test-API label.
        """
        action = db.query(ActionProposal).filter(ActionProposal.id == action_id).first()
        if not action:
            raise ValueError(f"ActionProposal {action_id} not found.")

        if action.payment_status == "PAID":
            return {"status": "ALREADY_PAID", "action_id": action_id}

        now = datetime.utcnow()
        action.payment_status = "PAID"
        action.is_simulated = is_simulated_demo

        paid_amount = action.final_price

        goal = db.query(Goal).filter(Goal.id == action.goal_id).first()
        if goal:
            goal.realized_amount = round(goal.realized_amount + paid_amount, 2)
            if goal.realized_amount >= goal.target_amount:
                goal.status = "COMPLETED"

        customer = db.query(Customer).filter(Customer.id == action.target_customer_id).first()
        opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
        product_id = opportunity.suggested_product_id if opportunity and opportunity.suggested_product_id else 1
        previous_segment = customer.segment if customer else None

        if customer:
            customer.total_spent = round(customer.total_spent + paid_amount, 2)
            customer.orders_count += 1
            customer.last_order_date = now
            if customer.segment == "CHURNED_VIP":
                customer.segment = "REACTIVATED_VIP"
            elif customer.segment == "DIFFUSER_OWNER" and product_id == 2:
                customer.segment = "REACTIVE_CROSS_BUYER"

        new_order = Order(
            customer_id=customer.id if customer else 1,
            product_id=product_id,
            amount=paid_amount,
            discount_amount=round(action.original_price - paid_amount, 2),
            order_date=now,
            status="PAID"
        )
        db.add(new_order)

        event_label = "DEMO_PAYMENT_SIMULATED" if is_simulated_demo else "PAYMENT_CAPTURED_WEBHOOK"
        outcome_label = (
            f"[DEMO/TESTING SIMULATION] Simulated customer paid ₹{paid_amount:,.2f} on test link."
            if is_simulated_demo else
            f"[RAZORPAY TEST MODE] Real test payment webhook captured ₹{paid_amount:,.2f}."
        )
        goal_now = goal.realized_amount if goal else paid_amount
        segment_now = customer.segment if customer else "n/a"
        state_note = (
            f" State update: goal realized ₹{goal_now:,.2f}"
            f"{f' (was segment {previous_segment} → {segment_now})' if customer else ''}."
            f" New paid order recorded."
        )

        audit_log = AuditLog(
            timestamp=now,
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type=event_label,
            agent_recommendation="Process payment outcome and advance goal revenue progress.",
            reason=f"Payment received for link {action.razorpay_link_id}. Advancing merchant revenue goal.{state_note}",
            proposed_amount=paid_amount,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy="Payment Settlement Policy",
            policy_result="CONFIRMED",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action=f"Payment {payment_id or 'sim_pay_' + str(action.id)} confirmed",
            final_outcome=outcome_label + state_note,
            metadata_json=f'{{"is_simulated": {str(is_simulated_demo).lower()}, "amount": {paid_amount}, "customer_id": {action.target_customer_id}}}'
        )
        db.add(audit_log)

        state_audit = AuditLog(
            timestamp=now,
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type="STATE_UPDATED",
            agent_recommendation="Observe payment outcome and update customer, goal, and revenue state.",
            reason=(
                f"Observed PAID outcome. Customer RFM/segment refreshed"
                f"{f' ({previous_segment} → {segment_now})' if customer else ''}."
                f" Goal progress is now ₹{goal_now:,.2f}."
            ),
            proposed_amount=paid_amount,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy="Post-execution observe → update loop",
            policy_result="STATE_APPLIED",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action="OUTCOME_OBSERVED",
            final_outcome="Agent state updated from payment outcome. Ready for next analysis cycle.",
            metadata_json=None,
        )
        db.add(state_audit)
        db.commit()

        return {
            "status": "SUCCESS",
            "action_id": action.id,
            "payment_status": "PAID",
            "paid_amount": paid_amount,
            "goal_realized_amount": goal.realized_amount if goal else paid_amount,
            "goal_target": goal.target_amount if goal else 100000.0,
            "is_simulated": is_simulated_demo
        }

    @classmethod
    def verify_webhook_signature(cls, raw_body: bytes, signature: str) -> bool:
        """Validates HMAC SHA256 webhook signature with Razorpay webhook secret."""
        secret = settings.RAZORPAY_WEBHOOK_SECRET
        if not secret:
            return True
        generated_signature = hmac.new(
            secret.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, signature)
