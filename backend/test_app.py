"""
End-to-End Verification Test for RevenueSystem Phase 1
Tests:
1. Database initialization and seeding
2. Deterministic store analytics & RFM segmentation
3. Revenue opportunity detection
4. Demonstrable Policy Violation (15% blocked -> 10% alternative)
5. Merchant HITL approval
6. Razorpay Test-Mode Payment Link creation
7. Payment outcome recording & goal update
8. Audit Trail verification
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database
from app.models import Goal, Customer, Product, Order, Opportunity, ActionProposal, AuditLog, MerchantPolicy
from app.services.analyzer import RevenueAnalyzer
from app.services.policy_engine import PolicyEngine
from app.services.agent import RevenueAgent
from app.services.razorpay_service import RazorpayService

def run_tests():
    print("=" * 60)
    print("STEP 1: Initializing Database & Seeding Realistic Data")
    print("=" * 60)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, force=True)

    cust_count = db.query(Customer).count()
    prod_count = db.query(Product).count()
    order_count = db.query(Order).count()
    policy = PolicyEngine.get_active_policy(db)
    print(f"Seeded: {cust_count} Customers, {prod_count} Products, {order_count} Orders.")
    print(f"Active Policy Guardrail: Max Autonomous Discount = {policy.max_autonomous_discount_pct}%")
    assert cust_count == 60, f"Expected 60 customers, got {cust_count}"
    assert prod_count == 12, f"Expected 12 products, got {prod_count}"
    assert policy.max_autonomous_discount_pct == 10.0, "Expected 10.0% max autonomous discount"

    print("\n" + "=" * 60)
    print("STEP 2: Deterministic Store Analytics Calculation")
    print("=" * 60)
    metrics = RevenueAnalyzer.get_store_metrics(db)
    print(f"Total Historical Revenue: ₹{metrics['total_revenue']:,.2f}")
    print(f"Total Orders: {metrics['total_orders']}")
    print(f"Average Order Value: ₹{metrics['average_order_value']:,.2f}")
    print(f"Repeat Purchase Rate: {metrics['repeat_purchase_rate']}%")
    print(f"Segments: {metrics['segments_breakdown']}")

    print("\n" + "=" * 60)
    print("STEP 3: Decomposing Merchant Goal & Finding Opportunities")
    print("=" * 60)
    goal = db.query(Goal).first()
    print(f"Merchant Goal: '{goal.prompt}' (Target: ₹{goal.target_amount:,.2f})")
    
    analysis_result = RevenueAgent.decompose_goal_and_recommend_strategy(db, goal)
    print(f"Strategy: {analysis_result['strategy_summary']}")
    print(f"Total Projected Revenue Pipeline: ₹{analysis_result['total_projected']:,.2f}")
    print(f"Opportunities Identified: {analysis_result['opportunities_count']}")

    opps = db.query(Opportunity).filter(Opportunity.goal_id == goal.id).all()
    for o in opps:
        print(f"  - [{o.type}] {o.title}: Target={o.target_customer_count} customers, Proposed Discount={o.proposed_discount_pct}%, Projected Rev=₹{o.projected_revenue:,.2f}")

    print("\n" + "=" * 60)
    print("STEP 4: Demonstrable Failure & Guardrail Enforcement Test")
    print("=" * 60)
    # Find the VIP Churn Win-Back proposal that asked for 15% discount
    blocked_action = db.query(ActionProposal).filter(
        ActionProposal.proposed_discount_pct > 10.0
    ).first()

    assert blocked_action is not None, "Demonstrable failure test failed: No action with >10% discount found!"
    print(f"Action #{blocked_action.id} Proposed Discount: {blocked_action.proposed_discount_pct}%")
    print(f"Policy Result: {blocked_action.policy_check_result}")
    print(f"Status: {blocked_action.status}")
    print(f"Rejection Reason: {blocked_action.rejection_reason}")
    print(f"Alternative Proposal: {blocked_action.alternative_proposal}")
    assert blocked_action.status == "BLOCKED", f"Expected BLOCKED, got {blocked_action.status}"
    assert "exceeds the merchant's maximum autonomous discount limit of 10.0%" in blocked_action.rejection_reason

    print("\n" + "=" * 60)
    print("STEP 5: Human-In-The-Loop Approval of Compliant Alternative")
    print("=" * 60)
    # Merchant accepts the compliant 10% alternative proposal
    blocked_action.proposed_discount_pct = 10.0
    blocked_action.final_price = round(blocked_action.original_price * 0.90, 2)
    blocked_action.approved_by_merchant = True
    blocked_action.status = "APPROVED"
    db.commit()
    print(f"Merchant adjusted discount to 10.0% (Final Price: ₹{blocked_action.final_price:,.2f}) and signed off.")

    print("\n" + "=" * 60)
    print("STEP 6: Executing Razorpay Test Payment Link Creation")
    print("=" * 60)
    customer = db.query(Customer).filter(Customer.id == blocked_action.target_customer_id).first()
    opp = db.query(Opportunity).filter(Opportunity.id == blocked_action.opportunity_id).first()
    rzp_res = RazorpayService.create_payment_link(
        db=db,
        action=blocked_action,
        customer=customer,
        description=f"{opp.title} - Exclusive Win-back Offer"
    )
    print(f"Razorpay Link ID: {rzp_res['link_id']}")
    print(f"Checkout URL: {rzp_res['short_url']}")
    print(f"Execution Mode: {rzp_res['mode']}")
    assert blocked_action.status == "EXECUTED"
    assert blocked_action.razorpay_link_id is not None

    print("\n" + "=" * 60)
    print("STEP 7: Processing Payment Outcome & Goal Realization")
    print("=" * 60)
    initial_realized = goal.realized_amount
    print(f"Initial Realized Revenue: ₹{initial_realized:,.2f}")
    
    # Process simulated demo payment
    pay_res = RazorpayService.record_payment_outcome(
        db=db,
        action_id=blocked_action.id,
        is_simulated_demo=True,
        payment_id=f"pay_sim_{blocked_action.id}"
    )
    db.refresh(goal)
    print(f"Payment Status: {pay_res['payment_status']}")
    print(f"Paid Amount: ₹{pay_res['paid_amount']:,.2f}")
    print(f"Updated Realized Revenue: ₹{goal.realized_amount:,.2f}")
    print(f"Goal Progress: {(goal.realized_amount / goal.target_amount) * 100:.1f}%")
    assert goal.realized_amount == initial_realized + blocked_action.final_price

    # Verify lightweight learning (customer stats and order history updated)
    db.refresh(customer)
    print(f"Customer {customer.name} Updated Spend: ₹{customer.total_spent:,.2f}, Total Orders: {customer.orders_count}, Segment: {customer.segment}")
    assert customer.segment == "REACTIVATED_VIP"

    print("\n" + "=" * 60)
    print("STEP 8: First-Class Audit Trail Verification")
    print("=" * 60)
    logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
    print(f"Total Audit Entries: {len(logs)}")
    for log in logs:
        print(f"[{log.timestamp.strftime('%H:%M:%S')}] [{log.event_type}]")
        print(f"   Rec: {log.agent_recommendation}")
        print(f"   Policy Result: {log.policy_result} | Human Sign-off: {log.human_approval}")
        print(f"   Razorpay Action: {log.razorpay_action}")
        print(f"   Final Outcome: {log.final_outcome}")
        print("-" * 50)

    # Verify demonstrative failure audit entry is present
    blocked_audit = [l for l in logs if l.event_type == "POLICY_BLOCKED"]
    assert len(blocked_audit) > 0, "Audit log must contain POLICY_BLOCKED entry!"
    print("\nSUCCESS! All Phase 1 end-to-end verification assertions passed!")
    db.close()

if __name__ == "__main__":
    run_tests()
