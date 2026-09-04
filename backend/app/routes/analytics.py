from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Customer, Product, Order
from app.schemas import CustomerResponse, ProductResponse, StoreAnalyticsSummary
from app.services.analyzer import RevenueAnalyzer
from app.seed_data import seed_database

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=StoreAnalyticsSummary)
def get_store_summary(db: Session = Depends(get_db)):
    """Returns deterministic baseline store analytics."""
    return RevenueAnalyzer.get_store_metrics(db)

@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(segment: str = None, limit: int = 100, db: Session = Depends(get_db)):
    """Returns customers list, optionally filtered by segment."""
    query = db.query(Customer)
    if segment:
        query = query.filter(Customer.segment == segment)
    return query.limit(limit).all()

@router.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """Returns catalog products with margins and inventory."""
    return db.query(Product).all()

@router.get("/campaigns")
def get_campaign_strategy(budget: float = 20000.0, db: Session = Depends(get_db)):
    """
    Deterministic campaign orchestration analysis:
    Uses historical campaign ROAS to recommend optimal budget allocation.
    """
    historical_campaigns = [
        {
            "id": "camp_1",
            "name": "Q4 VIP Win-Back Initiative",
            "type": "WIN_BACK",
            "spend": 10000.0,
            "revenue": 48200.0,
            "orders": 11,
            "conversion_rate": 34.2,
            "roas": 4.82,
            "is_best": True
        },
        {
            "id": "camp_2",
            "name": "Diffuser Cross-Sell Wave 1",
            "type": "CROSS_SELL",
            "spend": 15000.0,
            "revenue": 63500.0,
            "orders": 24,
            "conversion_rate": 28.5,
            "roas": 4.23,
            "is_best": False
        },
        {
            "id": "camp_3",
            "name": "Monsoon Herbal Tea Refill Push",
            "type": "REPLENISHMENT",
            "spend": 6000.0,
            "revenue": 21800.0,
            "orders": 16,
            "conversion_rate": 41.0,
            "roas": 3.63,
            "is_best": False
        },
        {
            "id": "camp_4",
            "name": "Diwali Luxury Hamper Pre-Book",
            "type": "VIP_UPSELL",
            "spend": 18000.0,
            "revenue": 54000.0,
            "orders": 9,
            "conversion_rate": 19.8,
            "roas": 3.00,
            "is_best": False
        }
    ]

    # Allocation heuristic: 60% Cross-Sell (larger cohort, high liquidity) + 40% VIP Win-Back (highest historical ROAS 4.82x)
    cross_sell_pct = 60.0
    win_back_pct = 40.0
    cross_sell_spend = round(budget * 0.60, 2)
    win_back_spend = round(budget * 0.40, 2)

    projected_roas = 4.47
    projected_revenue = round(budget * projected_roas, 2)

    return {
        "budget": budget,
        "recommended_allocation": [
            {
                "type": "CROSS_SELL",
                "label": "Aroma Diffuser Cross-Sell",
                "allocation_pct": cross_sell_pct,
                "allocated_amount": cross_sell_spend,
                "projected_revenue": round(cross_sell_spend * 4.23, 2),
                "expected_roas": 4.23,
                "cohort_size": 36
            },
            {
                "type": "WIN_BACK",
                "label": "Dormant VIP Win-Back",
                "allocation_pct": win_back_pct,
                "allocated_amount": win_back_spend,
                "projected_revenue": round(win_back_spend * 4.82, 2),
                "expected_roas": 4.82,
                "cohort_size": 15
            }
        ],
        "total_projected_revenue": projected_revenue,
        "projected_blended_roas": projected_roas,
        "allocation_rationale": (
            "Historical campaign ROAS shows VIP Win-Back yields peak capital efficiency (4.82×), "
            "while Diffuser Cross-Sell delivers high transaction volume (4.23×) across the 36-customer cohort. "
            "Allocating 60% (₹" + f"{cross_sell_spend:,.0f}" + ") to Cross-Sell and 40% (₹" + f"{win_back_spend:,.0f}" + ") "
            "to Win-Back balances cohort reach with margin preservation."
        ),
        "historical_campaigns": historical_campaigns
    }

@router.post("/reset-demo-data")
def reset_demo_data(db: Session = Depends(get_db)):
    """Resets database back to clean realistic demo state."""
    seed_database(db, force=True)
    return {"status": "SUCCESS", "message": "Demo data reset successfully."}

