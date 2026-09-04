from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import MerchantPolicy, AuditLog
from app.config import settings

# Server-side bounds (not bypassable from the UI). Refunds are never proposed or executed.
MAX_AUTONOMOUS_TRANSACTION_INR = settings.DEFAULT_MAX_AUTONOMOUS_TRANSACTION
REFUNDS_ALLOWED = False


class PolicyEngine:
    """
    Deterministic Merchant Guardrail & Policy Engine.
    Enforces that the AI agent NEVER directly executes a money-related action 
    without passing through strict policy checks.
    """

    @staticmethod
    def get_active_policy(db: Session) -> MerchantPolicy:
        policy = db.query(MerchantPolicy).filter(MerchantPolicy.is_active == True).first()
        if not policy:
            policy = MerchantPolicy(
                name="Default Growth Guardrails",
                max_autonomous_discount_pct=10.0,
                max_campaign_budget=settings.DEFAULT_MAX_CAMPAIGN_BUDGET,
                require_human_approval_over_discount=True,
                is_active=True
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
        return policy

    @classmethod
    def evaluate_proposal(
        cls, 
        db: Session, 
        goal_id: int,
        opportunity_id: int,
        original_price: float,
        proposed_discount_pct: float,
        target_customer_count: int = 1,
        agent_reasoning: str = "",
        action_type: str = "CREATE_PAYMENT_LINK",
    ) -> Dict[str, Any]:
        """
        Evaluates a proposed action against merchant guardrails.
        Flow:
        Agent proposes structured action -> Policy Engine -> APPROVED / REQUIRES_APPROVAL / BLOCKED
        """
        policy = cls.get_active_policy(db)
        
        calculated_discount_amount = round(original_price * (proposed_discount_pct / 100.0), 2)
        final_price = round(original_price - calculated_discount_amount, 2)
        total_discount_investment = calculated_discount_amount * target_customer_count

        applicable_policy_str = (
            f"Merchant Policy Guardrail: Max Autonomous Discount = {policy.max_autonomous_discount_pct}%, "
            f"Max Campaign Budget = ₹{policy.max_campaign_budget:,.2f}, "
            f"Max Autonomous Transaction = ₹{MAX_AUTONOMOUS_TRANSACTION_INR:,.2f}, Refunds = DISABLED"
        )

        # 0. Refunds are never allowed
        if (not REFUNDS_ALLOWED) and "REFUND" in (action_type or "").upper():
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal_id,
                opportunity_id=opportunity_id,
                event_type="POLICY_BLOCKED",
                agent_recommendation="Autonomous refund proposed.",
                reason="Merchant policy disables AI-initiated refunds.",
                proposed_amount=final_price,
                proposed_discount=proposed_discount_pct,
                applicable_policy=applicable_policy_str,
                policy_result="REFUND_DISABLED",
                human_approval="DENIED",
                razorpay_action="EXECUTION_PREVENTED",
                final_outcome="Refund action blocked server-side.",
                metadata_json=None,
            )
            db.add(audit_log)
            db.commit()
            return {
                "status": "BLOCKED",
                "policy_check_result": "REFUND_DISABLED",
                "rejection_reason": "Autonomous refunds are disabled by merchant policy.",
                "alternative_proposal": "No refund alternative. Payment-link offers only.",
                "original_price": original_price,
                "proposed_discount_pct": proposed_discount_pct,
                "final_price": final_price,
                "human_approval": "DENIED",
            }

        # 1. Check for demonstrative discount violation (> 10.0%)
        if proposed_discount_pct > policy.max_autonomous_discount_pct:
            # Policy Violation! Autonomous execution is BLOCKED.
            status = "BLOCKED"
            policy_result = "VIOLATION_BLOCKED"
            rejection_reason = (
                f"Autonomous execution BLOCKED: Proposed discount of {proposed_discount_pct}% exceeds the "
                f"merchant's maximum autonomous discount limit of {policy.max_autonomous_discount_pct}%."
            )
            
            # Formulate the compliant 10% alternative proposal
            allowed_discount_pct = policy.max_autonomous_discount_pct
            allowed_final_price = round(original_price * (1.0 - (allowed_discount_pct / 100.0)), 2)
            alternative_proposal = (
                f"Alternative Compliant Proposal: Adjust discount to policy-capped {allowed_discount_pct}% "
                f"(Discounted price: ₹{allowed_final_price:,.2f}). Requires merchant approval to execute."
            )
            human_approval_status = "PENDING_MERCHANT_APPROVAL"

            # Log this demonstrable failure in Audit Log
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal_id,
                opportunity_id=opportunity_id,
                event_type="POLICY_BLOCKED",
                agent_recommendation=f"Proposed {proposed_discount_pct}% discount on ₹{original_price:,.2f} item.",
                reason=agent_reasoning or "Agent sought higher conversion via aggressive discount.",
                proposed_amount=final_price,
                proposed_discount=proposed_discount_pct,
                applicable_policy=applicable_policy_str,
                policy_result=policy_result,
                human_approval=human_approval_status,
                razorpay_action="EXECUTION_PREVENTED",
                final_outcome=f"{rejection_reason} Generated compliant alternative at {allowed_discount_pct}% discount.",
                metadata_json=f'{{"original_price": {original_price}, "proposed_discount_pct": {proposed_discount_pct}, "policy_max": {policy.max_autonomous_discount_pct}}}'
            )
            db.add(audit_log)
            alt_audit = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal_id,
                opportunity_id=opportunity_id,
                event_type="COMPLIANT_ALTERNATIVE",
                agent_recommendation=f"Adopt {allowed_discount_pct}% discount (₹{allowed_final_price:,.2f}).",
                reason=(
                    f"Compliant alternative generated because {proposed_discount_pct}% exceeds the "
                    f"{policy.max_autonomous_discount_pct}% autonomous discount guardrail. "
                    f"Merchant approval is required before Razorpay execution."
                ),
                proposed_amount=allowed_final_price,
                proposed_discount=allowed_discount_pct,
                applicable_policy=applicable_policy_str,
                policy_result="ALTERNATIVE_READY",
                human_approval=human_approval_status,
                razorpay_action="AWAITING_MERCHANT_APPROVAL",
                final_outcome=alternative_proposal,
                metadata_json=None,
            )
            db.add(alt_audit)
            db.commit()

            return {
                "status": status,
                "policy_check_result": policy_result,
                "rejection_reason": rejection_reason,
                "alternative_proposal": alternative_proposal,
                "original_price": original_price,
                "proposed_discount_pct": proposed_discount_pct,
                "final_price": final_price,
                "allowed_discount_pct": allowed_discount_pct,
                "allowed_final_price": allowed_final_price,
                "human_approval": human_approval_status
            }

        # 2. Check budget limit
        if total_discount_investment > policy.max_campaign_budget:
            status = "REQUIRES_APPROVAL"
            policy_result = "BUDGET_THRESHOLD_EXCEEDED"
            rejection_reason = (
                f"Campaign discount budget (₹{total_discount_investment:,.2f}) exceeds autonomous limit "
                f"of ₹{policy.max_campaign_budget:,.2f}."
            )
            alternative_proposal = f"Cap target cohort to {int(policy.max_campaign_budget // calculated_discount_amount)} customers."
            human_approval_status = "PENDING_MERCHANT_APPROVAL"

            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal_id,
                opportunity_id=opportunity_id,
                event_type="POLICY_THRESHOLD_EXCEEDED",
                agent_recommendation=f"Campaign allocation of ₹{total_discount_investment:,.2f}",
                reason=rejection_reason,
                proposed_amount=final_price,
                proposed_discount=proposed_discount_pct,
                applicable_policy=applicable_policy_str,
                policy_result=policy_result,
                human_approval=human_approval_status,
                razorpay_action="EXECUTION_PENDING_APPROVAL",
                final_outcome="Requires merchant sign-off before Razorpay action.",
                metadata_json=None
            )
            db.add(audit_log)
            db.commit()

            return {
                "status": status,
                "policy_check_result": policy_result,
                "rejection_reason": rejection_reason,
                "alternative_proposal": alternative_proposal,
                "original_price": original_price,
                "proposed_discount_pct": proposed_discount_pct,
                "final_price": final_price,
                "human_approval": human_approval_status
            }

        # 3. Maximum autonomous transaction (₹5,000)
        ticket = max(original_price, final_price)
        if ticket > MAX_AUTONOMOUS_TRANSACTION_INR:
            status = "REQUIRES_APPROVAL"
            policy_result = "TRANSACTION_CAP_EXCEEDED"
            rejection_reason = (
                f"Offer ticket ₹{ticket:,.2f} exceeds the maximum autonomous transaction of "
                f"₹{MAX_AUTONOMOUS_TRANSACTION_INR:,.2f}."
            )
            alternative_proposal = "Requires merchant approval before generating a Razorpay test link."
            human_approval_status = "PENDING_MERCHANT_APPROVAL"
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal_id,
                opportunity_id=opportunity_id,
                event_type="POLICY_THRESHOLD_EXCEEDED",
                agent_recommendation=f"Create payment link for ₹{final_price:,.2f}.",
                reason=rejection_reason,
                proposed_amount=final_price,
                proposed_discount=proposed_discount_pct,
                applicable_policy=applicable_policy_str,
                policy_result=policy_result,
                human_approval=human_approval_status,
                razorpay_action="EXECUTION_PENDING_APPROVAL",
                final_outcome="Human approval required for over-cap ticket size.",
                metadata_json=None,
            )
            db.add(audit_log)
            db.commit()
            return {
                "status": status,
                "policy_check_result": policy_result,
                "rejection_reason": rejection_reason,
                "alternative_proposal": alternative_proposal,
                "original_price": original_price,
                "proposed_discount_pct": proposed_discount_pct,
                "final_price": final_price,
                "human_approval": human_approval_status,
            }

        # 4. Passed all guardrails!
        status = "APPROVED"
        policy_result = "PASSED"
        human_approval_status = "AUTO_APPROVED"
        
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=goal_id,
            opportunity_id=opportunity_id,
            event_type="POLICY_EVALUATION",
            agent_recommendation=f"Execute offer with {proposed_discount_pct}% discount (₹{final_price:,.2f}).",
            reason=(
                f"Complies with merchant guardrails: discount {proposed_discount_pct}% ≤ "
                f"{policy.max_autonomous_discount_pct}%; ticket ₹{ticket:,.2f} ≤ "
                f"₹{MAX_AUTONOMOUS_TRANSACTION_INR:,.2f}; refunds disabled; human approval required above "
                f"{policy.max_autonomous_discount_pct}%."
            ),
            proposed_amount=final_price,
            proposed_discount=proposed_discount_pct,
            applicable_policy=applicable_policy_str,
            policy_result=policy_result,
            human_approval=human_approval_status,
            razorpay_action="READY_FOR_EXECUTION",
            final_outcome="Policy check passed. Awaiting explicit merchant click to generate Razorpay TEST MODE link.",
            metadata_json=None
        )
        db.add(audit_log)
        db.commit()

        return {
            "status": status,
            "policy_check_result": policy_result,
            "rejection_reason": None,
            "alternative_proposal": None,
            "original_price": original_price,
            "proposed_discount_pct": proposed_discount_pct,
            "final_price": final_price,
            "human_approval": human_approval_status
        }

    @classmethod
    def assert_can_execute(cls, db: Session, action) -> None:
        """
        Re-enforces guardrails at execution time so a direct API call cannot skip policy.
        Merchant-approved overrides may exceed the autonomous discount cap.
        Raises ValueError with a merchant-safe message when blocked.
        """
        if "REFUND" in (action.action_type or "").upper() and not REFUNDS_ALLOWED:
            raise ValueError("Refunds are disabled. No payment action was executed.")

        policy = cls.get_active_policy(db)
        ticket = max(action.original_price or 0, action.final_price or 0)

        if not action.approved_by_merchant:
            if action.proposed_discount_pct > policy.max_autonomous_discount_pct:
                raise ValueError(
                    f"Discount {action.proposed_discount_pct}% exceeds the {policy.max_autonomous_discount_pct}% "
                    "autonomous limit. Merchant approval is required."
                )
            if ticket > MAX_AUTONOMOUS_TRANSACTION_INR:
                raise ValueError(
                    f"Ticket ₹{ticket:,.2f} exceeds the ₹{MAX_AUTONOMOUS_TRANSACTION_INR:,.0f} "
                    "autonomous transaction cap. Merchant approval is required."
                )

