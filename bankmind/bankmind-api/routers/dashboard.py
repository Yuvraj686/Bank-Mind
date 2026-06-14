"""Dashboard router — KPIs and pipeline data."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database import get_db
from models.customer import Customer
from models.agent_log import AgentLog
from models.banker import Banker
from routers.deps import get_current_banker

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
def get_kpis(
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    total = db.execute(select(func.count(Customer.id))).scalar() or 0
    onboarding = db.execute(select(func.count(Customer.id)).where(Customer.stage == "onboarding")).scalar() or 0
    active = db.execute(select(func.count(Customer.id)).where(Customer.stage == "active")).scalar() or 0
    leads = db.execute(select(func.count(Customer.id)).where(Customer.stage == "lead")).scalar() or 0
    dormant = db.execute(select(func.count(Customer.id)).where(Customer.stage == "dormant")).scalar() or 0

    converted = onboarding + active + dormant
    conversion_rate = round((converted / total * 100), 1) if total > 0 else 0.0

    # Adoption rate: % of active customers with at least 1 feature adopted
    active_customers = db.execute(select(Customer).where(Customer.stage == "active")).scalars().all()
    adopted_count = sum(
        1 for c in active_customers
        if c.features_adopted and any(v for v in c.features_adopted.values())
    )
    adoption_rate = round((adopted_count / len(active_customers) * 100), 1) if active_customers else 0.0

    # Estimated revenue impact (₹500/lead + ₹5000/active)
    estimated_revenue = (leads * 500) + (active * 5000)

    return {
        "total_customers": total,
        "total_leads": leads,
        "conversion_rate": conversion_rate,
        "adoption_rate": adoption_rate,
        "active_customers": active,
        "onboarding_customers": onboarding,
        "dormant_customers": dormant,
        "estimated_revenue_impact": estimated_revenue,
    }


@router.get("/pipeline")
def get_pipeline(
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    stages = ["lead", "onboarding", "active", "dormant"]
    result = {}
    for stage in stages:
        customers = db.execute(
            select(Customer).where(Customer.stage == stage).order_by(Customer.updated_at.desc())
        ).scalars().all()
        result[stage] = {
            "count": len(customers),
            "customers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "lead_score": c.lead_score,
                    "occupation": c.occupation,
                    "city": c.city,
                    "currently_processing": c.currently_processing,
                    "kyc_status": c.kyc_status,
                    "features_adopted": c.features_adopted or {},
                }
                for c in customers
            ],
        }
    return result


@router.get("/activity-feed")
def get_activity_feed(
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    logs = db.execute(
        select(AgentLog, Customer.name.label("customer_name"))
        .join(Customer, AgentLog.customer_id == Customer.id)
        .order_by(AgentLog.created_at.desc())
        .limit(50)
    ).all()

    return [
        {
            "id": log.AgentLog.id,
            "customer_id": log.AgentLog.customer_id,
            "customer_name": log.customer_name,
            "agent_name": log.AgentLog.agent_name,
            "action": log.AgentLog.action,
            "message_sent": log.AgentLog.message_sent,
            "reasoning": log.AgentLog.reasoning,
            "confidence": log.AgentLog.confidence,
            "stage_before": log.AgentLog.stage_before,
            "stage_after": log.AgentLog.stage_after,
            "was_overridden": log.AgentLog.was_overridden,
            "created_at": log.AgentLog.created_at.isoformat() if log.AgentLog.created_at else None,
        }
        for log in logs
    ]
