from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    cost: float
    margin_pct: float
    inventory_count: int
    description: Optional[str] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    segment: str
    total_spent: float
    orders_count: int
    last_order_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    prompt: str = Field(..., example="Help me generate ₹1,00,000 additional revenue.")
    target_amount: Optional[float] = Field(None, example=100000.0)

class GoalResponse(BaseModel):
    id: int
    prompt: str
    target_amount: float
    realized_amount: float
    projected_amount: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunityResponse(BaseModel):
    id: int
    goal_id: int
    type: str
    title: str
    description: str
    reasoning: str
    target_cohort_name: str
    target_customer_count: int
    suggested_product_id: Optional[int]
    suggested_product_name: Optional[str] = None
    baseline_aov: float
    estimated_conversion_rate: float
    proposed_discount_pct: float
    projected_revenue: float
    projected_roi: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PolicyResponse(BaseModel):
    id: int
    name: str
    max_autonomous_discount_pct: float
    max_campaign_budget: float
    require_human_approval_over_discount: bool
    is_active: bool

    class Config:
        from_attributes = True

class PolicyUpdate(BaseModel):
    max_autonomous_discount_pct: Optional[float] = None
    max_campaign_budget: Optional[float] = None
    require_human_approval_over_discount: Optional[bool] = None

class ActionProposalResponse(BaseModel):
    id: int
    opportunity_id: int
    goal_id: int
    action_type: str
    target_customer_id: Optional[int]
    target_customer_name: Optional[str] = None
    original_price: float
    proposed_discount_pct: float
    final_price: float
    status: str
    policy_check_result: Optional[str]
    rejection_reason: Optional[str]
    alternative_proposal: Optional[str]
    approved_by_merchant: bool
    razorpay_link_id: Optional[str]
    razorpay_short_url: Optional[str]
    payment_status: str
    is_simulated: bool
    created_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ActionApproveRequest(BaseModel):
    action_id: int
    override_discount_pct: Optional[float] = None
    merchant_notes: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    goal_id: Optional[int]
    opportunity_id: Optional[int]
    action_id: Optional[int]
    event_type: str
    agent_recommendation: str
    reason: str
    proposed_amount: Optional[float]
    proposed_discount: Optional[float]
    applicable_policy: str
    policy_result: str
    human_approval: Optional[str]
    razorpay_action: Optional[str]
    final_outcome: str
    metadata_json: Optional[str]

    class Config:
        from_attributes = True

class SimulatePaymentRequest(BaseModel):
    action_id: int

class StoreAnalyticsSummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    average_order_value: float
    repeat_purchase_rate: float
    segments_breakdown: Dict[str, int]
