from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models import MerchantPolicy, ActionProposal, AuditLog
from app.config import settings

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
                max_campaign_budget=20000.0,
                require_human_approval_over_discount=True,
                is_active=True
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
        elif policy.max_autonomous_discount_pct > 10.0 or policy.max_campaign_budget > 20000.0:
            # These are server-side hard ceilings, irrespective of stale DB values.
            policy.max_autonomous_discount_pct = min(policy.max_autonomous_discount_pct, 10.0)
            policy.max_campaign_budget = min(policy.max_campaign_budget, 20000.0)
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
        agent_reasoning: str = ""
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
            f"Max Campaign Budget = ₹{policy.max_campaign_budget:,.2f}"
        )

        # An action above this amount is never cleared for autonomous execution.
        if final_price > settings.MAX_AUTONOMOUS_TRANSACTION:
            status = "REQUIRES_APPROVAL"
            policy_result = "TRANSACTION_LIMIT_EXCEEDED"
            rejection_reason = (
                f"Checkout amount ₹{final_price:,.2f} exceeds the ₹{settings.MAX_AUTONOMOUS_TRANSACTION:,.2f} "
                "autonomous transaction limit."
            )
            audit_log = AuditLog(
                timestamp=datetime.utcnow(), goal_id=goal_id, opportunity_id=opportunity_id,
                event_type="POLICY_THRESHOLD_EXCEEDED",
                agent_recommendation=f"Proposed checkout amount ₹{final_price:,.2f}.",
                reason=rejection_reason, proposed_amount=final_price,
                proposed_discount=proposed_discount_pct,
                applicable_policy=applicable_policy_str + f", Max Autonomous Transaction = ₹{settings.MAX_AUTONOMOUS_TRANSACTION:,.2f}",
                policy_result=policy_result, human_approval="PENDING_MERCHANT_APPROVAL",
                razorpay_action="EXECUTION_PENDING_APPROVAL",
                final_outcome="Requires merchant sign-off before Razorpay action.", metadata_json=None
            )
            db.add(audit_log)
            db.commit()
            return {
                "status": status, "policy_check_result": policy_result,
                "rejection_reason": rejection_reason,
                "alternative_proposal": "Reduce the checkout amount to ₹5,000 or obtain merchant approval.",
                "original_price": original_price, "proposed_discount_pct": proposed_discount_pct,
                "final_price": final_price, "human_approval": "PENDING_MERCHANT_APPROVAL"
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

        # 3. Passed all guardrails!
        status = "APPROVED"
        policy_result = "PASSED"
        human_approval_status = "AUTO_APPROVED"
        
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=goal_id,
            opportunity_id=opportunity_id,
            event_type="POLICY_EVALUATION",
            agent_recommendation=f"Execute offer with {proposed_discount_pct}% discount (₹{final_price:,.2f}).",
            reason=f"Complies with all policy rules (discount {proposed_discount_pct}% <= {policy.max_autonomous_discount_pct}%).",
            proposed_amount=final_price,
            proposed_discount=proposed_discount_pct,
            applicable_policy=applicable_policy_str,
            policy_result=policy_result,
            human_approval=human_approval_status,
            razorpay_action="READY_FOR_EXECUTION",
            final_outcome="Policy check passed. Cleared for Razorpay test action.",
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
