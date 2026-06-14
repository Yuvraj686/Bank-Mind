"""Agents router — manual trigger and log endpoints."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from models.agent_log import AgentLog
from models.customer import Customer
from models.banker import Banker
from routers.deps import get_current_banker
from orchestrator.orchestrator import Orchestrator

router = APIRouter(prefix="/agents", tags=["agents"])


class OverrideRequest(BaseModel):
    action: str  # cancel | edit_message | move_stage
    note: Optional[str] = None
    new_message: Optional[str] = None
    new_stage: Optional[str] = None


def log_to_dict(log: AgentLog, customer_name: str | None = None) -> dict:
    return {
        "id": log.id,
        "customer_id": log.customer_id,
        "customer_name": customer_name,
        "agent_name": log.agent_name,
        "action": log.action,
        "message_sent": log.message_sent,
        "reasoning": log.reasoning,
        "confidence": log.confidence,
        "stage_before": log.stage_before,
        "stage_after": log.stage_after,
        "was_overridden": log.was_overridden,
        "override_note": log.override_note,
        "override_by": log.override_by,
        "override_at": log.override_at.isoformat() if log.override_at else None,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


@router.post("/run/{customer_id}")
async def run_agent(
    customer_id: str,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    orchestrator = Orchestrator(db)
    result = await orchestrator.run_for_customer(customer_id)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/logs")
def get_logs(
    agent_name: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    query = (
        select(AgentLog, Customer.name.label("customer_name"))
        .join(Customer, AgentLog.customer_id == Customer.id)
        .order_by(AgentLog.created_at.desc())
    )
    if agent_name:
        query = query.where(AgentLog.agent_name == agent_name)
    if customer_id:
        query = query.where(AgentLog.customer_id == customer_id)

    total_query = select(AgentLog)
    if agent_name:
        total_query = total_query.where(AgentLog.agent_name == agent_name)
    if customer_id:
        total_query = total_query.where(AgentLog.customer_id == customer_id)

    total = len(db.execute(total_query).scalars().all())
    offset = (page - 1) * page_size
    logs = db.execute(query.offset(offset).limit(page_size)).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "logs": [log_to_dict(row.AgentLog, row.customer_name) for row in logs],
    }


@router.get("/logs/{customer_id}")
def get_customer_logs(
    customer_id: str,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    logs = db.execute(
        select(AgentLog)
        .where(AgentLog.customer_id == customer_id)
        .order_by(AgentLog.created_at.desc())
    ).scalars().all()

    return [log_to_dict(log, customer.name) for log in logs]


@router.patch("/logs/{log_id}/override")
async def override_log(
    log_id: str,
    body: OverrideRequest,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    log = db.get(AgentLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Agent log not found")

    log.was_overridden = True
    log.override_note = body.note
    log.override_by = banker.name
    log.override_at = datetime.utcnow()

    if body.action == "edit_message" and body.new_message:
        log.message_sent = body.new_message

    if body.action == "move_stage" and body.new_stage:
        customer = db.get(Customer, log.customer_id)
        if customer:
            customer.stage = body.new_stage
            customer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(log)

    # Broadcast override via WebSocket
    from websocket.manager import manager
    await manager.broadcast("override", {
        "log_id": log_id,
        "customer_id": log.customer_id,
        "override_by": banker.name,
        "action": body.action,
    })

    return log_to_dict(log)
