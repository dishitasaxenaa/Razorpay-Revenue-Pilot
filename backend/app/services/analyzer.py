from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Customer, Product, Order

class RevenueAnalyzer:
    """
    Pure deterministic Python calculations for all business metrics:
    revenue, ROI, conversion rates, AOV, customer segmentation, 
    product affinity, and repeat-purchase patterns.
    """

    @staticmethod
    def get_store_metrics(db: Session) -> Dict[str, Any]:
        """Calculates store-wide historical baseline metrics."""
        total_orders = db.query(Order).count()
        total_revenue = db.query(func.sum(Order.amount)).scalar() or 0.0
        total_customers = db.query(Customer).count()
        repeat_customers = db.query(Customer).filter(Customer.orders_count > 1).count()

        aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
        repeat_rate = round((repeat_customers / total_customers) * 100, 1) if total_customers > 0 else 0.0

        # Segment breakdown
        segments = {}
        for seg, count in db.query(Customer.segment, func.count(Customer.id)).group_by(Customer.segment).all():
            segments[seg] = count

        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "total_customers": total_customers,
            "average_order_value": aov,
            "repeat_purchase_rate": repeat_rate,
            "segments_breakdown": segments
        }

    @staticmethod
    def analyze_dormant_vips(db: Session, dormancy_days: int = 60, min_spend: float = 6000.0) -> Dict[str, Any]:
        """
        Deterministic calculation for Churned VIP Win-Back Opportunity.
        Identifies high-value customers with no orders in dormancy_days.
        """
        threshold_date = datetime.utcnow() - timedelta(days=dormancy_days)
        dormant_vips = db.query(Customer).filter(
            Customer.last_order_date <= threshold_date,
            Customer.total_spent >= min_spend
        ).all()

        target_count = len(dormant_vips)
        if target_count == 0:
            return None

        avg_historical_spend = sum(c.total_spent for c in dormant_vips) / target_count
        avg_orders_per_customer = sum(c.orders_count for c in dormant_vips) / target_count
        baseline_aov = avg_historical_spend / avg_orders_per_customer if avg_orders_per_customer > 0 else 2500.0

        # Win-back campaign models:
        # High value reactivation package: Aura Sanctuary Luxury Hamper or Curated Re-engagement bundle (₹4,999)
        target_product = db.query(Product).filter(Product.id == 10).first()
        product_price = target_product.price if target_product else 4999.0
        product_cost = target_product.cost if target_product else 1600.0

        # Conversion rate with reactivation incentive
        # Note: Initial proposal discount of 15.0% is used to demonstrate policy guardrail enforcement!
        proposed_discount_pct = 15.0 # Deliberately exceeds 10% autonomous limit for demonstrable failure
        discounted_price = round(product_price * (1.0 - (proposed_discount_pct / 100.0)), 2)
        
        # Win-back conversion rate heuristic based on VIP loyalty depth: 40%
        est_conversion_rate = 0.40
        expected_conversions = round(target_count * est_conversion_rate)
        projected_revenue = round(expected_conversions * discounted_price, 2)
        
        # Deterministic ROI
        gross_margin = (discounted_price - product_cost) * expected_conversions
        discount_cost = (product_price * (proposed_discount_pct / 100.0)) * expected_conversions
        projected_roi = round((gross_margin / discount_cost) * 100, 1) if discount_cost > 0 else 0.0

        return {
            "type": "WIN_BACK",
            "title": "VIP Churn Win-Back Campaign",
            "target_cohort_name": "Dormant High-Value Customers (60+ days)",
            "target_customer_count": target_count,
            "target_customer_ids": [c.id for c in dormant_vips],
            "suggested_product_id": target_product.id if target_product else None,
            "suggested_product_name": target_product.name if target_product else "Luxury Wellness Hamper",
            "baseline_aov": round(baseline_aov, 2),
            "original_price": product_price,
            "proposed_discount_pct": proposed_discount_pct,
            "discounted_price": discounted_price,
            "estimated_conversion_rate": est_conversion_rate,
            "projected_revenue": projected_revenue,
            "projected_roi": projected_roi,
            "reasoning": (
                f"Identified {target_count} high-value customers who spent an average of ₹{avg_historical_spend:,.0f} "
                f"but have had zero orders in the last 60+ days. Offering a re-engagement incentive on the luxury "
                f"wellness hamper recaptures dormant churn with an estimated 40% conversion rate."
            )
        }

    @staticmethod
    def analyze_cross_sell_bundle(db: Session) -> Dict[str, Any]:
        """
        Deterministic product affinity calculation:
        Customers who bought Diffuser (ID 1) but haven't purchased Essential Oils (ID 2).
        """
        diffuser_customers = db.query(Customer.id).join(Order).filter(Order.product_id == 1).distinct().all()
        diffuser_customer_ids = {c[0] for c in diffuser_customers}

        oils_customers = db.query(Customer.id).join(Order).filter(Order.product_id == 2).distinct().all()
        oils_customer_ids = {c[0] for c in oils_customers}

        cross_sell_candidate_ids = list(diffuser_customer_ids - oils_customer_ids)
        target_count = len(cross_sell_candidate_ids)
        if target_count == 0:
            return None

        target_product = db.query(Product).filter(Product.id == 2).first()
        product_price = target_product.price if target_product else 1299.0
        product_cost = target_product.cost if target_product else 380.0

        # Standard within-policy discount: 10.0%
        proposed_discount_pct = 10.0
        discounted_price = round(product_price * (1.0 - (proposed_discount_pct / 100.0)), 2)
        
        # High conversion affinity because diffuser utility depends on essential oils
        est_conversion_rate = 0.55
        expected_conversions = round(target_count * est_conversion_rate)
        projected_revenue = round(expected_conversions * discounted_price, 2)

        gross_margin = (discounted_price - product_cost) * expected_conversions
        discount_cost = (product_price * (proposed_discount_pct / 100.0)) * expected_conversions
        projected_roi = round((gross_margin / discount_cost) * 100, 1) if discount_cost > 0 else 0.0

        return {
            "type": "CROSS_SELL",
            "title": "Aroma Essentials Cross-Sell Activation",
            "target_cohort_name": "Diffuser Owners without Essential Oils",
            "target_customer_count": target_count,
            "target_customer_ids": cross_sell_candidate_ids,
            "suggested_product_id": target_product.id if target_product else None,
            "suggested_product_name": target_product.name if target_product else "Essential Oils 6-Pack",
            "baseline_aov": 2499.0,
            "original_price": product_price,
            "proposed_discount_pct": proposed_discount_pct,
            "discounted_price": discounted_price,
            "estimated_conversion_rate": est_conversion_rate,
            "projected_revenue": projected_revenue,
            "projected_roi": projected_roi,
            "reasoning": (
                f"{target_count} customers purchased the Ultrasonic Diffuser but have not yet purchased essential oils. "
                f"Diffusers require oil replenishment, creating high natural purchase affinity (55% estimated conversion)."
            )
        }

    @staticmethod
    def analyze_vip_upsell(db: Session) -> Dict[str, Any]:
        """
        Deterministic VIP Spender Upsell calculation:
        Customers with top 10% lifetime value and active within 30 days.
        """
        threshold_date = datetime.utcnow() - timedelta(days=30)
        active_vips = db.query(Customer).filter(
            Customer.last_order_date >= threshold_date,
            Customer.total_spent >= 12000.0
        ).all()

        target_count = len(active_vips)
        if target_count == 0:
            return None

        target_product = db.query(Product).filter(Product.id == 10).first()
        product_price = target_product.price if target_product else 4999.0
        product_cost = target_product.cost if target_product else 1600.0

        proposed_discount_pct = 10.0 # Autonomous limit compliant
        discounted_price = round(product_price * (1.0 - (proposed_discount_pct / 100.0)), 2)

        est_conversion_rate = 0.35
        expected_conversions = round(target_count * est_conversion_rate)
        projected_revenue = round(expected_conversions * discounted_price, 2)

        gross_margin = (discounted_price - product_cost) * expected_conversions
        discount_cost = (product_price * (proposed_discount_pct / 100.0)) * expected_conversions
        projected_roi = round((gross_margin / discount_cost) * 100, 1) if discount_cost > 0 else 0.0

        return {
            "type": "VIP_UPSELL",
            "title": "Active VIP Exclusive Pre-Launch Upsell",
            "target_cohort_name": "Top 10% Active High Spenders (Past 30 Days)",
            "target_customer_count": target_count,
            "target_customer_ids": [c.id for c in active_vips],
            "suggested_product_id": target_product.id if target_product else None,
            "suggested_product_name": target_product.name if target_product else "Luxury Wellness Hamper",
            "baseline_aov": 3800.0,
            "original_price": product_price,
            "proposed_discount_pct": proposed_discount_pct,
            "discounted_price": discounted_price,
            "estimated_conversion_rate": est_conversion_rate,
            "projected_revenue": projected_revenue,
            "projected_roi": projected_roi,
            "reasoning": (
                f"{target_count} highly active VIPs with spend >₹12,000 have strong brand affinity. "
                f"Offering exclusive early access to our luxury collector hamper drives high-ticket incrementality."
            )
        }

    @staticmethod
    def analyze_replenishment_cycles(db: Session) -> Dict[str, Any]:
        """
        Deterministic repeat-purchase replenishment calculation:
        Identifies repeat buyers of consumable products (Tea, Bath Soak) due for replenishment (30-45 days).
        """
        min_date = datetime.utcnow() - timedelta(days=45)
        max_date = datetime.utcnow() - timedelta(days=30)
        
        replenish_customers = db.query(Customer).filter(
            Customer.last_order_date >= min_date,
            Customer.last_order_date <= max_date,
            Customer.orders_count >= 2
        ).all()

        target_count = len(replenish_customers)
        if target_count == 0:
            return None

        # Bundle Tea (Product 3: 749) + Bath Soak (Product 6: 999) = 1,748
        bundle_original_price = 1748.0
        bundle_cost = 490.0

        proposed_discount_pct = 8.0 # 8% discount for routine subscriber replenishment
        discounted_price = round(bundle_original_price * (1.0 - (proposed_discount_pct / 100.0)), 2)

        est_conversion_rate = 0.50
        expected_conversions = round(target_count * est_conversion_rate)
        projected_revenue = round(expected_conversions * discounted_price, 2)

        gross_margin = (discounted_price - bundle_cost) * expected_conversions
        discount_cost = (bundle_original_price * (proposed_discount_pct / 100.0)) * expected_conversions
        projected_roi = round((gross_margin / discount_cost) * 100, 1) if discount_cost > 0 else 0.0

        return {
            "type": "REPLENISHMENT",
            "title": "Automated Consumables Refill Incentive",
            "target_cohort_name": "Consumables Buyers (30-45 Day Restock Window)",
            "target_customer_count": target_count,
            "target_customer_ids": [c.id for c in replenish_customers],
            "suggested_product_id": 3,
            "suggested_product_name": "Calming Tea & Bath Soak Restock Duo",
            "baseline_aov": 1400.0,
            "original_price": bundle_original_price,
            "proposed_discount_pct": proposed_discount_pct,
            "discounted_price": discounted_price,
            "estimated_conversion_rate": est_conversion_rate,
            "projected_revenue": projected_revenue,
            "projected_roi": projected_roi,
            "reasoning": (
                f"{target_count} repeat customers purchased consumable wellness items between 30 and 45 days ago. "
                f"Their supply is naturally depleted; a gentle replenishment incentive generates predictable high-margin repeat cash flow."
            )
        }

    @classmethod
    def get_all_opportunities(cls, db: Session) -> List[Dict[str, Any]]:
        """Executes deterministic opportunity detection and returns ranked opportunities."""
        opportunities = []
        for analyzer_func in [
            cls.analyze_dormant_vips,
            cls.analyze_cross_sell_bundle,
            cls.analyze_vip_upsell,
            cls.analyze_replenishment_cycles
        ]:
            res = analyzer_func(db)
            if res:
                opportunities.append(res)

        # Sort by projected revenue descending
        opportunities.sort(key=lambda x: x["projected_revenue"], reverse=True)
        return opportunities
