"""Customers router."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from models.customer import Customer
from models.conversation import Conversation
from models.banker import Banker
from routers.deps import get_current_banker

router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerCreate(BaseModel):
    name: str
    age: int
    city: str
    occupation: str
    income_monthly: float
    website_visits: int = 0
    pages_viewed: Optional[str] = None


class StageUpdate(BaseModel):
    stage: str
    reason: Optional[str] = None


def customer_to_dict(c: Customer) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "age": c.age,
        "city": c.city,
        "occupation": c.occupation,
        "income_monthly": c.income_monthly,
        "date_of_birth": c.date_of_birth.isoformat() if c.date_of_birth else None,
        "stage": c.stage,
        "lead_score": c.lead_score,
        "kyc_status": c.kyc_status,
        "account_number": c.account_number,
        "features_adopted": c.features_adopted or {},
        "currently_processing": c.currently_processing,
        "last_life_event_detected": c.last_life_event_detected,
        "website_visits": c.website_visits,
        "pages_viewed": c.pages_viewed,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@router.get("")
def list_customers(
    stage: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    query = select(Customer).order_by(Customer.created_at.desc())
    if stage:
        query = query.where(Customer.stage == stage)
    customers = db.execute(query).scalars().all()
    return [customer_to_dict(c) for c in customers]


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_to_dict(customer)


@router.post("", status_code=201)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customer = Customer(
        id=str(uuid.uuid4()),
        name=body.name,
        age=body.age,
        city=body.city,
        occupation=body.occupation,
        income_monthly=body.income_monthly,
        website_visits=body.website_visits,
        pages_viewed=body.pages_viewed,
        stage="lead",
        features_adopted={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_to_dict(customer)


@router.put("/{customer_id}/stage")
def update_customer_stage(
    customer_id: str,
    body: StageUpdate,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    valid_stages = {"lead", "onboarding", "active", "dormant"}
    if body.stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")

    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    old_stage = customer.stage
    customer.stage = body.stage
    customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(customer)

    return {"success": True, "customer_id": customer_id, "stage": body.stage, "previous_stage": old_stage}


@router.get("/{customer_id}/conversations")
def get_conversations(
    customer_id: str,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    convs = db.execute(
        select(Conversation)
        .where(Conversation.customer_id == customer_id)
        .order_by(Conversation.created_at.asc())
    ).scalars().all()

    return [
        {
            "id": c.id,
            "sender": c.sender,
            "agent_name": c.agent_name,
            "content": c.content,
            "channel": c.channel,
            "is_simulated": c.is_simulated,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in convs
    ]
