from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=False)
    segment = Column(String, nullable=False, default="NEW") # VIP, CHURNED_VIP, FREQUENT, ONE_TIME
    total_spent = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    last_order_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")
    action_proposals = relationship("ActionProposal", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    margin_pct = Column(Float, nullable=False)
    inventory_count = Column(Integer, default=100)
    description = Column(Text, nullable=True)

    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="PAID") # PAID, REFUNDED

    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False) # e.g. 100000.0
    realized_amount = Column(Float, default=0.0)
    projected_amount = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE") # ACTIVE, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opportunities = relationship("Opportunity", back_populates="goal", cascade="all, delete-orphan")
    action_proposals = relationship("ActionProposal", back_populates="goal")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    type = Column(String, nullable=False) # WIN_BACK, CROSS_SELL, VIP_UPSELL, REPLENISHMENT
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False) # Explainability: why agent chose this
    target_cohort_name = Column(String, nullable=False)
    target_customer_count = Column(Integer, nullable=False)
    suggested_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    baseline_aov = Column(Float, nullable=False)
    estimated_conversion_rate = Column(Float, nullable=False)
    proposed_discount_pct = Column(Float, nullable=False)
    projected_revenue = Column(Float, nullable=False)
    projected_roi = Column(Float, nullable=False)
    status = Column(String, default="IDENTIFIED") # IDENTIFIED, ACTION_PROPOSED, IN_PROGRESS, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow)

    goal = relationship("Goal", back_populates="opportunities")
    suggested_product = relationship("Product")
    action_proposals = relationship("ActionProposal", back_populates="opportunity")

class MerchantPolicy(Base):
    __tablename__ = "merchant_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default Growth Guardrails")
    max_autonomous_discount_pct = Column(Float, default=10.0) # Crucial: default is 10%
    max_campaign_budget = Column(Float, default=25000.0)
    require_human_approval_over_discount = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActionProposal(Base):
    __tablename__ = "action_proposals"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    action_type = Column(String, default="CREATE_PAYMENT_LINK") # CREATE_PAYMENT_LINK, BUNDLE_OFFER_LINK
    target_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    original_price = Column(Float, nullable=False)
    proposed_discount_pct = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)
    
    # Policy evaluation
    status = Column(String, default="PROPOSED") # PROPOSED, BLOCKED, REQUIRES_APPROVAL, APPROVED, EXECUTED, REJECTED
    policy_check_result = Column(String, nullable=True) # PASSED, VIOLATION_BLOCKED, REQUIRES_APPROVAL
    rejection_reason = Column(Text, nullable=True)
    alternative_proposal = Column(Text, nullable=True)
    approved_by_merchant = Column(Boolean, default=False)
    
    # Razorpay Test Execution
    razorpay_link_id = Column(String, nullable=True)
    razorpay_short_url = Column(String, nullable=True)
    payment_status = Column(String, default="PENDING") # PENDING, PAID, EXPIRED
    is_simulated = Column(Boolean, default=False) # Transparent flag: Real Razorpay Test API vs Demo Simulator
    
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

    opportunity = relationship("Opportunity", back_populates="action_proposals")
    goal = relationship("Goal", back_populates="action_proposals")
    customer = relationship("Customer", back_populates="action_proposals")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    goal_id = Column(Integer, nullable=True)
    opportunity_id = Column(Integer, nullable=True)
    action_id = Column(Integer, nullable=True)
    
    event_type = Column(String, nullable=False) # e.g. GOAL_INITIALIZED, OPPORTUNITY_DISCOVERED, POLICY_EVALUATED, POLICY_BLOCKED, POLICY_MODIFIED, MERCHANT_APPROVED, RAZORPAY_LINK_CREATED, PAYMENT_RECORDED, DEMO_PAYMENT_SIMULATED
    agent_recommendation = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    proposed_amount = Column(Float, nullable=True)
    proposed_discount = Column(Float, nullable=True)
    applicable_policy = Column(Text, nullable=False)
    policy_result = Column(Text, nullable=False)
    human_approval = Column(Text, nullable=True) # "NOT_REQUIRED", "PENDING", "APPROVED", "REJECTED"
    razorpay_action = Column(Text, nullable=True)
    final_outcome = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
