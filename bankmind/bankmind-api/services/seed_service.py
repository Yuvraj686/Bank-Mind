"""Seed service — creates 5 demo customers with 60 transactions each."""
import uuid
import random
import logging
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.customer import Customer
from models.transaction import Transaction
from models.product_eligibility import ProductEligibility

logger = logging.getLogger(__name__)

# ─── 5 Demo Profiles ──────────────────────────────────────────────────────────

DEMO_CUSTOMERS = [
    {
        "name": "Priya Sharma",
        "age": 28,
        "city": "Mumbai",
        "occupation": "Software Engineer",
        "income_monthly": 80000,
        "date_of_birth": date(1998, 3, 15),
        "website_visits": 12,
        "pages_viewed": "pricing,features,home_loan,savings",
        "life_event": "salary_jump",
    },
    {
        "name": "Rahul Mehta",
        "age": 35,
        "city": "Bangalore",
        "occupation": "Marketing Manager",
        "income_monthly": 65000,
        "date_of_birth": date(1991, 7, 22),
        "website_visits": 8,
        "pages_viewed": "education_loan,savings,features",
        "life_event": "school_fees",
    },
    {
        "name": "Ananya Krishnan",
        "age": 42,
        "city": "Chennai",
        "occupation": "Doctor",
        "income_monthly": 150000,
        "date_of_birth": date(1984, 11, 8),
        "website_visits": 5,
        "pages_viewed": "fd,home_loan,premium",
        "life_event": "medical_expense",
    },
    {
        "name": "Vikram Patel",
        "age": 31,
        "city": "Ahmedabad",
        "occupation": "Business Owner",
        "income_monthly": 120000,
        "date_of_birth": date(1995, 2, 28),
        "website_visits": 15,
        "pages_viewed": "credit_card,travel,premium,pricing",
        "life_event": "travel_increase",
    },
    {
        "name": "Sneha Iyer",
        "age": 25,
        "city": "Hyderabad",
        "occupation": "Product Manager",
        "income_monthly": 55000,
        "date_of_birth": date(2001, 9, 5),
        "website_visits": 6,
        "pages_viewed": "savings,upi,features",
        "life_event": None,
    },
]

# ─── Transaction templates per life event ─────────────────────────────────────

def _generate_transactions(customer_id: str, income: float, life_event: str | None) -> list[Transaction]:
    today = date.today()
    txns = []

    def add(days_ago: int, txn_type: str, amount: float, category: str, description: str):
        txns.append(Transaction(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            type=txn_type,
            amount=amount,
            category=category,
            description=description,
            transaction_date=today - timedelta(days=days_ago),
        ))

    # Regular salary (last 2 months)
    base_salary = income
    for i in [58, 28]:
        # Salary jump for relevant customer
        salary = base_salary * 1.35 if (life_event == "salary_jump" and i == 28) else base_salary
        add(i, "credit", salary, "salary", "Salary credit")

    # Regular expenses (60 days)
    for day in range(1, 61, 3):
        add(day, "debit", random.uniform(500, 3000), "food", f"Swiggy/Zomato order #{random.randint(1000, 9999)}")
        if day % 7 == 0:
            add(day, "debit", random.uniform(200, 1500), "utilities", "Electricity/Water bill")
        if day % 14 == 0:
            add(day, "debit", random.uniform(1000, 5000), "shopping", "Amazon/Flipkart purchase")

    # Life event specific transactions
    if life_event == "new_emi":
        for i in [5, 35]:
            add(i, "debit", 18000, "emi", "Home loan EMI - HDFC Bank")

    elif life_event == "travel_increase":
        for i in [3, 10, 18, 25]:
            add(i, "debit", random.uniform(4000, 12000), "travel", f"IndiGo/Air India booking #{random.randint(100, 999)}")
        add(7, "debit", 8500, "travel", "MakeMyTrip hotel booking")

    elif life_event == "school_fees":
        add(12, "debit", 45000, "education", "DPS School - Term 2 fees")
        add(42, "debit", 3000, "education", "Tuition fees - Math coach")

    elif life_event == "medical_expense":
        add(8, "debit", 28000, "medical", "Apollo Hospital - consultation + tests")
        add(15, "debit", 5500, "medical", "Pharmacy - medications")
        add(22, "debit", 12000, "medical", "Fortis Hospital - follow-up")

    elif life_event == "salary_jump":
        # Extra spending due to higher income
        add(5, "debit", 8000, "shopping", "Myntra - clothing haul")
        add(10, "debit", 15000, "shopping", "Croma - electronics")

    return txns


def seed_customers(db: Session) -> list[Customer]:
    """Create 5 demo customers with transactions and product eligibility."""
    # Clear existing seeded data
    existing = db.execute(select(Customer)).scalars().all()
    if existing:
        logger.info("Customers already exist — clearing and re-seeding")
        for c in existing:
            db.delete(c)
        db.commit()

    created_customers = []
    for profile in DEMO_CUSTOMERS:
        customer = Customer(
            id=str(uuid.uuid4()),
            name=profile["name"],
            age=profile["age"],
            city=profile["city"],
            occupation=profile["occupation"],
            income_monthly=profile["income_monthly"],
            date_of_birth=profile["date_of_birth"],
            website_visits=profile["website_visits"],
            pages_viewed=profile["pages_viewed"],
            stage="lead",
            features_adopted={},
            currently_processing=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(customer)
        db.flush()

        # Add transactions
        txns = _generate_transactions(customer.id, profile["income_monthly"], profile["life_event"])
        for t in txns:
            db.add(t)

        created_customers.append(customer)
        logger.info("Seeded customer: %s (%d transactions)", customer.name, len(txns))

    db.commit()
    logger.info("Seed complete: %d customers created", len(created_customers))
    return created_customers
