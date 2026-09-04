import hmac
import hashlib
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import razorpay
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ActionProposal, Customer, Order, Goal, AuditLog, Opportunity

class RazorpayService:
    """
    Razorpay Test Mode Integration Service.
    - Operates STRICTLY in TEST MODE.
    - Generates Razorpay Test Payment Links.
    - Verifies Webhooks.
    - Dispatches clearly labeled DEMO/TESTING simulated payments.
    - Implements lightweight learning by updating customer & order records.
    """

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
    def create_payment_link(
        cls,
        db: Session,
        action: ActionProposal,
        customer: Customer,
        description: str
    ) -> Dict[str, Any]:
        """
        Creates a test payment link via Razorpay API or realistic test mode fallback.
        """
        client = cls.get_client()
        amount_in_paise = int(round(action.final_price * 100))
        ref_id = f"REV_ACT_{action.id}_{int(time.time())}"

        link_id = None
        short_url = None
        mode = "TEST_API"

        if client:
            try:
                # Real Razorpay Test Mode API Call
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
                        "sms": False, # Do not send real SMS in test mode
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
            except Exception as e:
                print(f"[Razorpay Test API] Error calling live test endpoint: {e}. Falling back to test link simulator.")
                client = None

        if not client:
            # High-fidelity Razorpay Test Mode Mock Generator
            mode = "TEST_MODE_EMULATED"
            uid = uuid.uuid4().hex[:10]
            link_id = f"plink_{uid}"
            short_url = f"https://rzp.io/i/test_{uid}"

        action.razorpay_link_id = link_id
        action.razorpay_short_url = short_url
        action.status = "EXECUTED"
        action.executed_at = datetime.utcnow()
        action.is_simulated = (mode == "TEST_MODE_EMULATED")

        # Update Opportunity status
        opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
        if opportunity:
            opportunity.status = "IN_PROGRESS"

        # Record Audit Log
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
            razorpay_action=f"Created Payment Link {link_id} ({short_url}) via {mode}",
            final_outcome=f"Payment link active. Awaiting customer payment.",
            metadata_json=f'{{"razorpay_link_id": "{link_id}", "short_url": "{short_url}", "mode": "{mode}"}}'
        )
        db.add(audit_log)
        db.commit()
        db.refresh(action)

        return {
            "link_id": link_id,
            "short_url": short_url,
            "amount": action.final_price,
            "mode": mode
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

        # 1. Update Goal Realized Amount
        goal = db.query(Goal).filter(Goal.id == action.goal_id).first()
        if goal:
            goal.realized_amount = round(goal.realized_amount + paid_amount, 2)
            if goal.realized_amount >= goal.target_amount:
                goal.status = "COMPLETED"

        # 2. Lightweight Learning: update customer record so next analytics reflect this order
        customer = db.query(Customer).filter(Customer.id == action.target_customer_id).first()
        opportunity = db.query(Opportunity).filter(Opportunity.id == action.opportunity_id).first()
        product_id = opportunity.suggested_product_id if opportunity and opportunity.suggested_product_id else 1

        if customer:
            customer.total_spent = round(customer.total_spent + paid_amount, 2)
            customer.orders_count += 1
            customer.last_order_date = now
            # If they were churned, re-classify to active
            if customer.segment == "CHURNED_VIP":
                customer.segment = "REACTIVATED_VIP"
            elif customer.segment == "DIFFUSER_OWNER" and product_id == 2:
                customer.segment = "REACTIVE_CROSS_BUYER"

        # 3. Create persistent Order record
        new_order = Order(
            customer_id=customer.id if customer else 1,
            product_id=product_id,
            amount=paid_amount,
            discount_amount=round(action.original_price - paid_amount, 2),
            order_date=now,
            status="PAID"
        )
        db.add(new_order)

        # 4. First-Class Audit Trail Entry
        event_label = "DEMO_PAYMENT_SIMULATED" if is_simulated_demo else "PAYMENT_CAPTURED_WEBHOOK"
        outcome_label = (
            f"[DEMO/TESTING SIMULATION] Simulated customer paid ₹{paid_amount:,.2f} on test link."
            if is_simulated_demo else
            f"[RAZORPAY TEST MODE] Real test payment webhook captured ₹{paid_amount:,.2f}."
        )

        audit_log = AuditLog(
            timestamp=now,
            goal_id=action.goal_id,
            opportunity_id=action.opportunity_id,
            action_id=action.id,
            event_type=event_label,
            agent_recommendation="Process payment outcome and advance goal revenue progress.",
            reason=f"Payment received for link {action.razorpay_link_id}. Advancing merchant revenue goal.",
            proposed_amount=paid_amount,
            proposed_discount=action.proposed_discount_pct,
            applicable_policy="Payment Settlement Policy",
            policy_result="CONFIRMED",
            human_approval="APPROVED" if action.approved_by_merchant else "AUTO_APPROVED",
            razorpay_action=f"Payment {payment_id or 'sim_pay_' + uuid.uuid4().hex[:8]} confirmed",
            final_outcome=outcome_label,
            metadata_json=f'{{"is_simulated": {str(is_simulated_demo).lower()}, "amount": {paid_amount}, "customer_id": {action.target_customer_id}}}'
        )
        db.add(audit_log)
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
