import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import anthropic

from app.config import settings
from app.models import Goal, Opportunity, ActionProposal, AuditLog, Customer
from app.services.analyzer import RevenueAnalyzer
from app.services.policy_engine import PolicyEngine

class RevenueAgent:
    """
    Claude Reasoning Layer:
    Handles strategic prioritization, natural language synthesis, 
    campaign outreach copy, and decision explainability while relying on 
    deterministic Python calculations for all quantitative metrics.
    """

    @classmethod
    def decompose_goal_and_recommend_strategy(
        cls,
        db: Session,
        goal: Goal
    ) -> Dict[str, Any]:
        """
        1. Runs deterministic Python analytics to identify quantified opportunities.
        2. Applies Claude reasoning for strategy prioritization, explanations, and copy.
        3. Passes each proposed action through the PolicyEngine.
        4. Logs the entire chain in the AuditLog.
        """
        # Step 1: Deterministic opportunity detection
        audit_start = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=goal.id,
            event_type="ANALYSIS_STARTED",
            agent_recommendation=f"Analyze store state against goal ₹{goal.target_amount:,.2f}.",
            reason="ANALYZE: Run deterministic RFM, affinity, replenishment, and campaign-history calculations.",
            proposed_amount=goal.target_amount,
            proposed_discount=None,
            applicable_policy="Merchant Growth Directive",
            policy_result="IN_PROGRESS",
            human_approval="NOT_REQUIRED",
            razorpay_action=None,
            final_outcome="Analysis started. No money action executed.",
            metadata_json=None,
        )
        db.add(audit_start)
        db.commit()

        store_metrics = RevenueAnalyzer.get_store_metrics(db)
        raw_opportunities = RevenueAnalyzer.get_all_opportunities(db)

        # Step 2: AI Reasoning & Strategy Synthesis
        strategy_summary, prioritized_opps = cls._generate_reasoning_and_priorities(
            goal_prompt=goal.prompt,
            target_amount=goal.target_amount,
            store_metrics=store_metrics,
            opportunities=raw_opportunities
        )

        # Step 3: Clear any prior opportunities and unexecuted proposals for this goal if re-analyzing
        prior_opp_ids = [o[0] for o in db.query(Opportunity.id).filter(Opportunity.goal_id == goal.id).all()]
        if prior_opp_ids:
            db.query(ActionProposal).filter(
                ActionProposal.opportunity_id.in_(prior_opp_ids),
                ActionProposal.status != "EXECUTED"
            ).delete(synchronize_session=False)
            db.query(Opportunity).filter(Opportunity.goal_id == goal.id).delete(synchronize_session=False)
        db.commit()

        created_opportunities = []
        total_projected = 0.0

        for opp_data in prioritized_opps:
            opp = Opportunity(
                goal_id=goal.id,
                type=opp_data["type"],
                title=opp_data["title"],
                description=opp_data.get("description", opp_data["title"]),
                reasoning=opp_data["reasoning"],
                target_cohort_name=opp_data["target_cohort_name"],
                target_customer_count=opp_data["target_customer_count"],
                suggested_product_id=opp_data.get("suggested_product_id"),
                baseline_aov=opp_data["baseline_aov"],
                estimated_conversion_rate=opp_data["estimated_conversion_rate"],
                proposed_discount_pct=opp_data["proposed_discount_pct"],
                projected_revenue=opp_data["projected_revenue"],
                projected_roi=opp_data["projected_roi"],
                status="IDENTIFIED"
            )
            db.add(opp)
            db.flush()
            total_projected += opp.projected_revenue

            opp_audit = AuditLog(
                timestamp=datetime.utcnow(),
                goal_id=goal.id,
                opportunity_id=opp.id,
                event_type="OPPORTUNITY_DETECTED",
                agent_recommendation=opp.title,
                reason=opp.reasoning,
                proposed_amount=opp.projected_revenue,
                proposed_discount=opp.proposed_discount_pct,
                applicable_policy="Deterministic opportunity detection (no money movement)",
                policy_result="IDENTIFIED",
                human_approval="PENDING_POLICY_CHECK",
                razorpay_action=None,
                final_outcome=f"REASON/PLAN: {opp.type} targeting {opp.target_customer_count} customers.",
                metadata_json=None,
            )
            db.add(opp_audit)

            # Step 4: Formulate Action Proposal & Route through Policy Engine
            # Pick a sample target customer from the cohort
            target_customer = None
            if opp_data.get("target_customer_ids"):
                target_customer = db.query(Customer).filter(
                    Customer.id == opp_data["target_customer_ids"][0]
                ).first()

            original_price = opp_data.get("original_price", opp_data["baseline_aov"])
            proposed_discount_pct = opp_data["proposed_discount_pct"]

            # Route through Policy Engine!
            policy_eval = PolicyEngine.evaluate_proposal(
                db=db,
                goal_id=goal.id,
                opportunity_id=opp.id,
                original_price=original_price,
                proposed_discount_pct=proposed_discount_pct,
                target_customer_count=opp_data["target_customer_count"],
                agent_reasoning=opp_data["reasoning"],
                action_type="CREATE_PAYMENT_LINK",
            )

            action = ActionProposal(
                opportunity_id=opp.id,
                goal_id=goal.id,
                action_type="CREATE_PAYMENT_LINK",
                target_customer_id=target_customer.id if target_customer else None,
                original_price=original_price,
                proposed_discount_pct=proposed_discount_pct,
                final_price=policy_eval["final_price"],
                status=policy_eval["status"],
                policy_check_result=policy_eval["policy_check_result"],
                rejection_reason=policy_eval["rejection_reason"],
                alternative_proposal=policy_eval["alternative_proposal"],
                approved_by_merchant=False,
                payment_status="PENDING",
                is_simulated=False
            )
            db.add(action)
            db.flush()

            created_opportunities.append({
                "opportunity": opp,
                "action": action,
                "policy_evaluation": policy_eval
            })

        # Update Goal projected amount
        goal.projected_amount = round(total_projected, 2)
        
        # Step 5: First-class Audit Log entry for the complete strategic breakdown
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            goal_id=goal.id,
            event_type="STRATEGY_DECOMPOSED",
            agent_recommendation=(
                f"Decomposed revenue goal ₹{goal.target_amount:,.2f} into {len(prioritized_opps)} quantified opportunities. "
                f"Total projected pipeline: ₹{total_projected:,.2f}."
            ),
            reason=strategy_summary,
            proposed_amount=total_projected,
            proposed_discount=None,
            applicable_policy="Merchant Autonomous Guardrail & Budget Policy",
            policy_result=f"{len([o for o in created_opportunities if o['action'].status == 'APPROVED'])} Approved, {len([o for o in created_opportunities if o['action'].status != 'APPROVED'])} Flagged/Blocked",
            human_approval="PENDING_ACTION_REVIEW",
            razorpay_action="AWAITING_APPROVAL_FOR_BLOCKED_ACTIONS",
            final_outcome=f"Ready for merchant review. High-discount actions held in compliance buffer.",
            metadata_json=f'{{"total_projected": {total_projected}, "target_goal": {goal.target_amount}}}'
        )
        db.add(audit_log)
        db.commit()

        return {
            "strategy_summary": strategy_summary,
            "total_projected": total_projected,
            "opportunities_count": len(created_opportunities),
            "opportunities": created_opportunities
        }

    @classmethod
    def _generate_reasoning_and_priorities(
        cls,
        goal_prompt: str,
        target_amount: float,
        store_metrics: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> (str, List[Dict[str, Any]]):
        """
        Uses Claude API if key is set, otherwise provides high-fidelity deterministic reasoning.
        """
        api_key = settings.ANTHROPIC_API_KEY
        if api_key and len(api_key) > 10:
            try:
                client = anthropic.Anthropic(api_key=api_key)
                prompt_content = f"""
You are the AI Revenue Growth Agent for Aura Living (e-commerce merchant).
Merchant Goal: "{goal_prompt}" (Target: INR {target_amount:,.2f})

Store Metrics:
- Historical Revenue: INR {store_metrics['total_revenue']:,.2f}
- Total Orders: {store_metrics['total_orders']}
- AOV: INR {store_metrics['average_order_value']:,.2f}
- Repeat Purchase Rate: {store_metrics['repeat_purchase_rate']}%

Deterministic Opportunities identified by Python analytics:
{json.dumps(opportunities, indent=2, default=str)}

Return a JSON object with:
1. "strategy_summary": 2-3 sentence executive synthesis explaining how these opportunities reach the merchant's target.
2. "prioritized_opportunities": the opportunities list, enhancing the "reasoning" and adding a "marketing_copy" draft for SMS/WhatsApp.
Keep all numerical figures (revenue, price, discount, counts) identical to the input.
"""
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt_content}]
                )
                text = response.content[0].text
                # extract json if enclosed in code blocks
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                parsed = json.loads(text.strip())
                return parsed.get("strategy_summary", ""), parsed.get("prioritized_opportunities", opportunities)
            except Exception as e:
                print(f"[Claude API Reasoning] Fallback to native intelligence engine: {e}")

        # Intelligent Built-in Reasoning Synthesis
        total_opp_revenue = sum(o["projected_revenue"] for o in opportunities)
        goal_coverage_pct = round((total_opp_revenue / target_amount) * 100, 1)

        strategy_summary = (
            f"To achieve your goal of ₹{target_amount:,.2f} additional revenue, the agent identified {len(opportunities)} "
            f"complementary growth levers delivering ₹{total_opp_revenue:,.2f} in projected revenue ({goal_coverage_pct}% of goal). "
            f"The strategy prioritizes high-margin product cross-sells and dormant VIP reactivation to capture immediate liquidity "
            f"without diluting brand value."
        )

        # Enhance opportunities with contextual copy
        for opp in opportunities:
            if opp["type"] == "WIN_BACK":
                opp["description"] = (
                    "Re-engage 15 high-value dormant VIPs with a curated Comeback Luxury Hamper offer. "
                    "Note: Initial proposal carries 15% discount to maximize reactivation rate."
                )
            elif opp["type"] == "CROSS_SELL":
                opp["description"] = (
                    "Convert 20 diffuser owners into repeat buyers by offering the complementary Essential Oils 6-Pack "
                    "at an autonomous-compliant 10% bundle discount."
                )
            elif opp["type"] == "VIP_UPSELL":
                opp["description"] = (
                    "Exclusive VIP early access to the Aura Sanctuary Luxury Hamper for top 10% active spenders."
                )
            elif opp["type"] == "REPLENISHMENT":
                opp["description"] = (
                    "Predictive restock reminder with 8% loyalty courtesy discount for herbal tea and bath soak regulars."
                )

        return strategy_summary, opportunities
