from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.models import Customer, Product, Order, MerchantPolicy, Goal, Opportunity, ActionProposal, AuditLog
from app.config import settings

PRODUCTS_DATA = [
    {
        "id": 1,
        "name": "Aromatherapy Ultrasonic Diffuser (500ml)",
        "category": "Home Fragrance",
        "price": 2499.0,
        "cost": 950.0,
        "margin_pct": 62.0,
        "inventory_count": 140,
        "description": "Whisper-quiet ceramic ultrasonic diffuser with ambient warm light."
    },
    {
        "id": 2,
        "name": "Pure Organic Essential Oils 6-Pack",
        "category": "Home Fragrance",
        "price": 1299.0,
        "cost": 380.0,
        "margin_pct": 70.7,
        "inventory_count": 250,
        "description": "100% therapeutic grade: Lavender, Eucalyptus, Peppermint, Lemongrass, Tea Tree, Orange."
    },
    {
        "id": 3,
        "name": "Calming Chamomile & Lavender Night Tea (100g)",
        "category": "Wellness Herbal Teas",
        "price": 749.0,
        "cost": 210.0,
        "margin_pct": 72.0,
        "inventory_count": 300,
        "description": "Whole flower loose herbal blend for deep sleep and stress relaxation."
    },
    {
        "id": 4,
        "name": "100% Pure Mulberry Silk Sleep Mask",
        "category": "Sleep Wellness",
        "price": 1499.0,
        "cost": 420.0,
        "margin_pct": 72.0,
        "inventory_count": 180,
        "description": "Grade 6A 22-momme pure organic silk eye mask with blackout fit."
    },
    {
        "id": 5,
        "name": "Hand-Poured Soy Candle (Sandalwood & Amber)",
        "category": "Home Fragrance",
        "price": 899.0,
        "cost": 260.0,
        "margin_pct": 71.1,
        "inventory_count": 210,
        "description": "Clean-burning non-toxic soy wax with wooden crackle wick."
    },
    {
        "id": 6,
        "name": "Magnesium Flake Bath Soak 1kg",
        "category": "Body & Bath",
        "price": 999.0,
        "cost": 280.0,
        "margin_pct": 72.0,
        "inventory_count": 175,
        "description": "Zechstein seabed pure magnesium flakes for sore muscle recovery."
    },
    {
        "id": 7,
        "name": "Insulated Ceramic Bamboo Tumbler (450ml)",
        "category": "Drinkware",
        "price": 1199.0,
        "cost": 390.0,
        "margin_pct": 67.5,
        "inventory_count": 120,
        "description": "Double-wall stainless steel with ceramic interior and bamboo lid."
    },
    {
        "id": 8,
        "name": "Organic Flaxseed Weighted Eye Pillow",
        "category": "Sleep Wellness",
        "price": 1299.0,
        "cost": 390.0,
        "margin_pct": 70.0,
        "inventory_count": 95,
        "description": "Microwaveable warm/cold therapy eye pillow infused with French lavender."
    },
    {
        "id": 9,
        "name": "Himalayan Pink Bath Salt Crystals (850g)",
        "category": "Body & Bath",
        "price": 699.0,
        "cost": 180.0,
        "margin_pct": 74.2,
        "inventory_count": 220,
        "description": "Raw unrefined mineral-rich bath crystals with floral botanicals."
    },
    {
        "id": 10,
        "name": "Aura Sanctuary Luxury Wellness Hamper",
        "category": "Gift Sets",
        "price": 4999.0,
        "cost": 1600.0,
        "margin_pct": 68.0,
        "inventory_count": 50,
        "description": "Collector set: Diffuser, 6 Essential Oils, Silk Mask, Candle & Tea in wooden keepsake box."
    },
    {
        "id": 11,
        "name": "Ceremonial Grade Uji Matcha (50g)",
        "category": "Wellness Herbal Teas",
        "price": 1499.0,
        "cost": 450.0,
        "margin_pct": 70.0,
        "inventory_count": 110,
        "description": "First harvest stone-ground shade-grown Japanese green tea."
    },
    {
        "id": 12,
        "name": "Ultrasonic Car Air Aromatherapy Ionizer",
        "category": "Home Fragrance",
        "price": 1899.0,
        "cost": 620.0,
        "margin_pct": 67.3,
        "inventory_count": 85,
        "description": "Compact cup-holder purifier with aroma pad tray and HEPA filter."
    }
]

# 60 curated Indian customer profiles
CUSTOMERS_DATA = [
    # 15 Churned VIPs (High historical spend > ₹6,000, last order > 65 days ago)
    {"name": "Ananya Sharma", "email": "ananya.sharma@example.com", "phone": "+919876543210", "segment": "CHURNED_VIP", "days_ago": 75, "spend": 9800.0, "orders": 4},
    {"name": "Vikram Malhotra", "email": "vikram.m@example.com", "phone": "+919876543211", "segment": "CHURNED_VIP", "days_ago": 82, "spend": 12400.0, "orders": 5},
    {"name": "Pooja Hegde", "email": "pooja.h@example.com", "phone": "+919876543212", "segment": "CHURNED_VIP", "days_ago": 90, "spend": 7900.0, "orders": 3},
    {"name": "Rohan Mehta", "email": "rohan.mehta@example.com", "phone": "+919876543213", "segment": "CHURNED_VIP", "days_ago": 68, "spend": 11200.0, "orders": 4},
    {"name": "Sneha Reddy", "email": "sneha.reddy@example.com", "phone": "+919876543214", "segment": "CHURNED_VIP", "days_ago": 95, "spend": 8500.0, "orders": 3},
    {"name": "Arjun Kapoor", "email": "arjun.k@example.com", "phone": "+919876543215", "segment": "CHURNED_VIP", "days_ago": 70, "spend": 14200.0, "orders": 6},
    {"name": "Divya Nair", "email": "divya.nair@example.com", "phone": "+919876543216", "segment": "CHURNED_VIP", "days_ago": 88, "spend": 6700.0, "orders": 3},
    {"name": "Aditya Verma", "email": "aditya.v@example.com", "phone": "+919876543217", "segment": "CHURNED_VIP", "days_ago": 110, "spend": 9300.0, "orders": 4},
    {"name": "Meera Joshi", "email": "meera.joshi@example.com", "phone": "+919876543218", "segment": "CHURNED_VIP", "days_ago": 73, "spend": 10500.0, "orders": 4},
    {"name": "Karan Singhal", "email": "karan.s@example.com", "phone": "+919876543219", "segment": "CHURNED_VIP", "days_ago": 80, "spend": 8100.0, "orders": 3},
    {"name": "Neha Choudhury", "email": "neha.c@example.com", "phone": "+919876543220", "segment": "CHURNED_VIP", "days_ago": 85, "spend": 7400.0, "orders": 3},
    {"name": "Rishi Saxena", "email": "rishi.saxena@example.com", "phone": "+919876543221", "segment": "CHURNED_VIP", "days_ago": 66, "spend": 13100.0, "orders": 5},
    {"name": "Tanvi Iyer", "email": "tanvi.iyer@example.com", "phone": "+919876543222", "segment": "CHURNED_VIP", "days_ago": 92, "spend": 8900.0, "orders": 3},
    {"name": "Manish Rao", "email": "manish.rao@example.com", "phone": "+919876543223", "segment": "CHURNED_VIP", "days_ago": 105, "spend": 11800.0, "orders": 4},
    {"name": "Shreya Mukherjee", "email": "shreya.m@example.com", "phone": "+919876543224", "segment": "CHURNED_VIP", "days_ago": 78, "spend": 9400.0, "orders": 4},

    # 20 Diffuser Owners (Bought diffuser Product #1, but have NOT bought Essential Oils Product #2 - Prime Cross-sell!)
    {"name": "Rahul Deshmukh", "email": "rahul.d@example.com", "phone": "+919876543225", "segment": "DIFFUSER_OWNER", "days_ago": 22, "spend": 2499.0, "orders": 1},
    {"name": "Priyanka Sen", "email": "priyanka.sen@example.com", "phone": "+919876543226", "segment": "DIFFUSER_OWNER", "days_ago": 18, "spend": 3248.0, "orders": 2},
    {"name": "Abhishek Roy", "email": "abhishek.r@example.com", "phone": "+919876543227", "segment": "DIFFUSER_OWNER", "days_ago": 30, "spend": 2499.0, "orders": 1},
    {"name": "Kavita Bajaj", "email": "kavita.b@example.com", "phone": "+919876543228", "segment": "DIFFUSER_OWNER", "days_ago": 14, "spend": 2499.0, "orders": 1},
    {"name": "Siddharth Jain", "email": "siddharth.j@example.com", "phone": "+919876543229", "segment": "DIFFUSER_OWNER", "days_ago": 40, "spend": 3998.0, "orders": 2},
    {"name": "Ayesha Khan", "email": "ayesha.khan@example.com", "phone": "+919876543230", "segment": "DIFFUSER_OWNER", "days_ago": 25, "spend": 2499.0, "orders": 1},
    {"name": "Varun Pillai", "email": "varun.p@example.com", "phone": "+919876543231", "segment": "DIFFUSER_OWNER", "days_ago": 12, "spend": 2499.0, "orders": 1},
    {"name": "Bhavna Patel", "email": "bhavna.p@example.com", "phone": "+919876543232", "segment": "DIFFUSER_OWNER", "days_ago": 35, "spend": 3398.0, "orders": 2},
    {"name": "Nikhil Agarwal", "email": "nikhil.a@example.com", "phone": "+919876543233", "segment": "DIFFUSER_OWNER", "days_ago": 28, "spend": 2499.0, "orders": 1},
    {"name": "Pallavi Kulkarni", "email": "pallavi.k@example.com", "phone": "+919876543234", "segment": "DIFFUSER_OWNER", "days_ago": 19, "spend": 2499.0, "orders": 1},
    {"name": "Gaurav Bhatt", "email": "gaurav.b@example.com", "phone": "+919876543235", "segment": "DIFFUSER_OWNER", "days_ago": 45, "spend": 3998.0, "orders": 2},
    {"name": "Deepika Das", "email": "deepika.das@example.com", "phone": "+919876543236", "segment": "DIFFUSER_OWNER", "days_ago": 16, "spend": 2499.0, "orders": 1},
    {"name": "Akash Bose", "email": "akash.bose@example.com", "phone": "+919876543237", "segment": "DIFFUSER_OWNER", "days_ago": 24, "spend": 2499.0, "orders": 1},
    {"name": "Ritu Sethi", "email": "ritu.sethi@example.com", "phone": "+919876543238", "segment": "DIFFUSER_OWNER", "days_ago": 38, "spend": 2499.0, "orders": 1},
    {"name": "Harsh Vardhan", "email": "harsh.v@example.com", "phone": "+919876543239", "segment": "DIFFUSER_OWNER", "days_ago": 11, "spend": 3698.0, "orders": 2},
    {"name": "Sonia Menon", "email": "sonia.m@example.com", "phone": "+919876543240", "segment": "DIFFUSER_OWNER", "days_ago": 29, "spend": 2499.0, "orders": 1},
    {"name": "Prateek Mathur", "email": "prateek.m@example.com", "phone": "+919876543241", "segment": "DIFFUSER_OWNER", "days_ago": 21, "spend": 2499.0, "orders": 1},
    {"name": "Kriti Chauhan", "email": "kriti.c@example.com", "phone": "+919876543242", "segment": "DIFFUSER_OWNER", "days_ago": 33, "spend": 3248.0, "orders": 2},
    {"name": "Mohit Gujral", "email": "mohit.g@example.com", "phone": "+919876543243", "segment": "DIFFUSER_OWNER", "days_ago": 15, "spend": 2499.0, "orders": 1},
    {"name": "Simran Sawhney", "email": "simran.s@example.com", "phone": "+919876543244", "segment": "DIFFUSER_OWNER", "days_ago": 27, "spend": 2499.0, "orders": 1},

    # 10 Active High Spenders / VIPs (Spent > ₹12,000, ordered recently within 30 days)
    {"name": "Kabir Oberoi", "email": "kabir.oberoi@example.com", "phone": "+919876543245", "segment": "ACTIVE_VIP", "days_ago": 8, "spend": 18500.0, "orders": 6},
    {"name": "Tarun Singhania", "email": "tarun.s@example.com", "phone": "+919876543246", "segment": "ACTIVE_VIP", "days_ago": 14, "spend": 21000.0, "orders": 7},
    {"name": "Ananya Birla", "email": "ananya.b@example.com", "phone": "+919876543247", "segment": "ACTIVE_VIP", "days_ago": 5, "spend": 16400.0, "orders": 5},
    {"name": "Rajesh Jhunjhunwala", "email": "rajesh.j@example.com", "phone": "+919876543248", "segment": "ACTIVE_VIP", "days_ago": 19, "spend": 24500.0, "orders": 8},
    {"name": "Sunita Godrej", "email": "sunita.g@example.com", "phone": "+919876543249", "segment": "ACTIVE_VIP", "days_ago": 10, "spend": 17800.0, "orders": 6},
    {"name": "Devendra Wadia", "email": "devendra.w@example.com", "phone": "+919876543250", "segment": "ACTIVE_VIP", "days_ago": 23, "spend": 19200.0, "orders": 6},
    {"name": "Malini Jindal", "email": "malini.j@example.com", "phone": "+919876543251", "segment": "ACTIVE_VIP", "days_ago": 6, "spend": 22400.0, "orders": 7},
    {"name": "Sameer Piramal", "email": "sameer.p@example.com", "phone": "+919876543252", "segment": "ACTIVE_VIP", "days_ago": 12, "spend": 15900.0, "orders": 5},
    {"name": "Radhika Merchant", "email": "radhika.m@example.com", "phone": "+919876543253", "segment": "ACTIVE_VIP", "days_ago": 17, "spend": 26000.0, "orders": 8},
    {"name": "Aman Mittal", "email": "aman.mittal@example.com", "phone": "+919876543254", "segment": "ACTIVE_VIP", "days_ago": 9, "spend": 18700.0, "orders": 6},

    # 15 Replenishment Regulars (Tea & Bath Soak regular buyers, due for refill ~30-45 days)
    {"name": "Payal Somani", "email": "payal.s@example.com", "phone": "+919876543255", "segment": "REPLENISHMENT", "days_ago": 34, "spend": 4500.0, "orders": 4},
    {"name": "Naveen Chawla", "email": "naveen.c@example.com", "phone": "+919876543256", "segment": "REPLENISHMENT", "days_ago": 41, "spend": 5200.0, "orders": 5},
    {"name": "Natasha Dalal", "email": "natasha.d@example.com", "phone": "+919876543257", "segment": "REPLENISHMENT", "days_ago": 38, "spend": 3900.0, "orders": 4},
    {"name": "Raghav Juyal", "email": "raghav.j@example.com", "phone": "+919876543258", "segment": "REPLENISHMENT", "days_ago": 44, "spend": 4800.0, "orders": 4},
    {"name": "Esha Deol", "email": "esha.d@example.com", "phone": "+919876543259", "segment": "REPLENISHMENT", "days_ago": 31, "spend": 4100.0, "orders": 4},
    {"name": "Zahir Khan", "email": "zahir.k@example.com", "phone": "+919876543260", "segment": "REPLENISHMENT", "days_ago": 42, "spend": 5600.0, "orders": 5},
    {"name": "Ankita Lokhande", "email": "ankita.l@example.com", "phone": "+919876543261", "segment": "REPLENISHMENT", "days_ago": 36, "spend": 4300.0, "orders": 4},
    {"name": "Gaurav Kapoor", "email": "gaurav.k@example.com", "phone": "+919876543262", "segment": "REPLENISHMENT", "days_ago": 40, "spend": 3700.0, "orders": 3},
    {"name": "Rhea Chakraborty", "email": "rhea.c@example.com", "phone": "+919876543263", "segment": "REPLENISHMENT", "days_ago": 33, "spend": 4600.0, "orders": 4},
    {"name": "Farhan Akhtar", "email": "farhan.a@example.com", "phone": "+919876543264", "segment": "REPLENISHMENT", "days_ago": 45, "spend": 5100.0, "orders": 4},
    {"name": "Dia Mirza", "email": "dia.mirza@example.com", "phone": "+919876543265", "segment": "REPLENISHMENT", "days_ago": 32, "spend": 4400.0, "orders": 4},
    {"name": "Ayushmann Khurrana", "email": "ayushmann.k@example.com", "phone": "+919876543266", "segment": "REPLENISHMENT", "days_ago": 39, "spend": 5800.0, "orders": 5},
    {"name": "Sonakshi Sinha", "email": "sonakshi.s@example.com", "phone": "+919876543267", "segment": "REPLENISHMENT", "days_ago": 37, "spend": 4200.0, "orders": 4},
    {"name": "Siddhant Chaturvedi", "email": "siddhant.c@example.com", "phone": "+919876543268", "segment": "REPLENISHMENT", "days_ago": 43, "spend": 4900.0, "orders": 4},
    {"name": "Tara Sutaria", "email": "tara.s@example.com", "phone": "+919876543269", "segment": "REPLENISHMENT", "days_ago": 35, "spend": 4000.0, "orders": 4}
]

def seed_database(db: Session, force: bool = False):
    """Seeds the database with rich, realistic merchant transaction data if empty or forced."""
    if not force and db.query(Product).count() > 0:
        return

    # Clear existing if force
    if force:
        # Delete dependent lifecycle records first. Leaving these behind caused Reset Demo
        # to surface stale EXECUTED actions linked to deleted goals/opportunities.
        db.query(AuditLog).delete()
        db.query(ActionProposal).delete()
        db.query(Opportunity).delete()
        db.query(Order).delete()
        db.query(Customer).delete()
        db.query(Product).delete()
        db.query(Goal).delete()
        db.query(MerchantPolicy).delete()
        db.commit()

    # 1. Seed Products
    products_map = {}
    for p_data in PRODUCTS_DATA:
        product = Product(**p_data)
        db.add(product)
        db.flush()
        products_map[product.id] = product

    # 2. Seed Default Merchant Guardrail Policy
    policy = MerchantPolicy(
        name="Default Growth Guardrails",
        max_autonomous_discount_pct=min(settings.DEFAULT_MAX_AUTONOMOUS_DISCOUNT, 10.0),
        max_campaign_budget=min(settings.DEFAULT_MAX_CAMPAIGN_BUDGET, 20000.0),
        require_human_approval_over_discount=True,
        is_active=True
    )
    db.add(policy)
    db.flush()

    # 3. Seed Customers & Historical Orders
    now = datetime.utcnow()
    customers_map = {}

    for c_data in CUSTOMERS_DATA:
        last_date = now - timedelta(days=c_data["days_ago"])
        customer = Customer(
            name=c_data["name"],
            email=c_data["email"],
            phone=c_data["phone"],
            segment=c_data["segment"],
            total_spent=c_data["spend"],
            orders_count=c_data["orders"],
            last_order_date=last_date
        )
        db.add(customer)
        db.flush()
        customers_map[customer.id] = customer

        # Generate orders matching their profile
        seg = c_data["segment"]
        if seg == "DIFFUSER_OWNER":
            # Bought Diffuser (Product 1)
            order1 = Order(
                customer_id=customer.id,
                product_id=1,
                amount=products_map[1].price,
                discount_amount=0.0,
                order_date=last_date,
                status="PAID"
            )
            db.add(order1)
            if c_data["orders"] > 1:
                # Another order of Sleep Mask or Candle, but NEVER Essential Oils!
                order2 = Order(
                    customer_id=customer.id,
                    product_id=random.choice([4, 5]),
                    amount=products_map[4].price,
                    discount_amount=0.0,
                    order_date=last_date - timedelta(days=20),
                    status="PAID"
                )
                db.add(order2)

        elif seg == "CHURNED_VIP":
            # Multiple high value orders across months, but none recently
            for i in range(c_data["orders"]):
                order_date = last_date - timedelta(days=i * 45)
                prod_id = random.choice([1, 4, 7, 10])
                order = Order(
                    customer_id=customer.id,
                    product_id=prod_id,
                    amount=products_map[prod_id].price,
                    discount_amount=0.0,
                    order_date=order_date,
                    status="PAID"
                )
                db.add(order)

        elif seg == "ACTIVE_VIP":
            # High value orders recently
            for i in range(c_data["orders"]):
                order_date = last_date - timedelta(days=i * 25)
                prod_id = random.choice([1, 2, 4, 7, 10, 11])
                order = Order(
                    customer_id=customer.id,
                    product_id=prod_id,
                    amount=products_map[prod_id].price,
                    discount_amount=0.0,
                    order_date=order_date,
                    status="PAID"
                )
                db.add(order)

        elif seg == "REPLENISHMENT":
            # Bought tea (3) or soak (6) multiple times
            for i in range(c_data["orders"]):
                order_date = last_date - timedelta(days=i * 35)
                prod_id = random.choice([3, 6, 9])
                order = Order(
                    customer_id=customer.id,
                    product_id=prod_id,
                    amount=products_map[prod_id].price,
                    discount_amount=0.0,
                    order_date=order_date,
                    status="PAID"
                )
                db.add(order)

    # 4. Default Goal: ₹1,00,000
    goal = Goal(
        prompt="Help me generate ₹1,00,000 additional revenue.",
        target_amount=100000.0,
        realized_amount=0.0,
        projected_amount=0.0,
        status="ACTIVE"
    )
    db.add(goal)
    db.flush()

    # 5. Initial Audit Log
    init_log = AuditLog(
        timestamp=now,
        goal_id=goal.id,
        event_type="SYSTEM_INITIALIZED",
        agent_recommendation="System primed with merchant store data (60 customers, 12 products, 160+ orders).",
        reason="Initial setup and database seeding completed successfully.",
        proposed_amount=None,
        proposed_discount=None,
        applicable_policy=f"Default Policy: Max Autonomous Discount {policy.max_autonomous_discount_pct}%",
        policy_result="POLICY_ENFORCED",
        human_approval="NOT_REQUIRED",
        razorpay_action=None,
        final_outcome="System ready for AI goal ingestion and deterministic revenue analytics."
    )
    db.add(init_log)

    db.commit()
    print("Database successfully seeded with realistic store data.")
