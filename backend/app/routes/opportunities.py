from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Goal, Opportunity, Product
from app.schemas import OpportunityResponse
from app.services.agent import RevenueAgent

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("", response_model=List[OpportunityResponse])
def get_opportunities(goal_id: int = None, db: Session = Depends(get_db)):
    """Fetches opportunities for the active goal or given goal_id."""
    if not goal_id:
        goal = db.query(Goal).filter(Goal.status == "ACTIVE").order_by(Goal.id.desc()).first()
        if not goal:
            return []
        goal_id = goal.id

    opps = db.query(Opportunity).filter(Opportunity.goal_id == goal_id).all()
    results = []
    for opp in opps:
        product_name = None
        if opp.suggested_product_id:
            prod = db.query(Product).filter(Product.id == opp.suggested_product_id).first()
            if prod:
                product_name = prod.name
        
        results.append(OpportunityResponse(
            id=opp.id,
            goal_id=opp.goal_id,
            type=opp.type,
            title=opp.title,
            description=opp.description,
            reasoning=opp.reasoning,
            target_cohort_name=opp.target_cohort_name,
            target_customer_count=opp.target_customer_count,
            suggested_product_id=opp.suggested_product_id,
            suggested_product_name=product_name,
            baseline_aov=opp.baseline_aov,
            estimated_conversion_rate=opp.estimated_conversion_rate,
            proposed_discount_pct=opp.proposed_discount_pct,
            projected_revenue=opp.projected_revenue,
            projected_roi=opp.projected_roi,
            status=opp.status,
            created_at=opp.created_at
        ))
    return results

@router.post("/analyze")
def trigger_analysis(goal_id: int = None, db: Session = Depends(get_db)):
    """Triggers deterministic analysis and Claude strategy synthesis."""
    if not goal_id:
        goal = db.query(Goal).filter(Goal.status == "ACTIVE").order_by(Goal.id.desc()).first()
        if not goal:
            raise HTTPException(status_code=400, detail="No active goal found. Please set a goal first.")
    else:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found.")

    res = RevenueAgent.decompose_goal_and_recommend_strategy(db, goal)
    return res
