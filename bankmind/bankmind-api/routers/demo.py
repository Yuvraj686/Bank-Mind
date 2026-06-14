"""Demo router — seed, run, and reset endpoints."""
import asyncio
import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database import get_db
from models.customer import Customer
from models.transaction import Transaction
from models.conversation import Conversation
from models.agent_log import AgentLog
from models.product_eligibility import ProductEligibility
from models.banker import Banker
from routers.deps import get_current_banker
from services.seed_service import seed_customers
from services.redis_service import set_demo_state, get_demo_state, clear_demo_state
from orchestrator.orchestrator import Orchestrator
from websocket.manager import manager

router = APIRouter(prefix="/demo", tags=["demo"])
logger = logging.getLogger(__name__)


@router.post("/seed")
def seed_demo(
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    customers = seed_customers(db)
    return {
        "success": True,
        "message": f"Seeded {len(customers)} demo customers",
        "customers": [{"id": c.id, "name": c.name, "stage": c.stage} for c in customers],
    }


async def _run_demo_sequence(db: Session):
    """Background task: runs agents for all customers in sequence with delays."""
    orchestrator = Orchestrator(db)

    set_demo_state({"status": "running", "step": "acquisition", "progress": 0})

    try:
        customers = db.execute(select(Customer)).scalars().all()

        # Step 1: Acquisition (2s delay per customer)
        await manager.send_demo_progress("acquisition", "running")
        set_demo_state({"status": "running", "step": "acquisition", "progress": 20})
        for customer in customers:
            db.refresh(customer)
            await orchestrator.run_for_customer(customer.id)
            await asyncio.sleep(2)

        # Step 2: Onboarding (3s delay per customer)
        await manager.send_demo_progress("onboarding", "running")
        set_demo_state({"status": "running", "step": "onboarding", "progress": 40})
        customers = db.execute(select(Customer)).scalars().all()
        for customer in customers:
            db.refresh(customer)
            if customer.stage == "onboarding":
                await orchestrator.run_for_customer(customer.id)
                await asyncio.sleep(3)

        # Step 3: Adoption (1.5s delay per customer)
        await manager.send_demo_progress("adoption", "running")
        set_demo_state({"status": "running", "step": "adoption", "progress": 60})
        customers = db.execute(select(Customer)).scalars().all()
        for customer in customers:
            db.refresh(customer)
            if customer.stage == "active":
                await orchestrator.run_for_customer(customer.id)
                await asyncio.sleep(1.5)

        # Step 4: Life-Event (1.5s delay per customer)
        await manager.send_demo_progress("life_event", "running")
        set_demo_state({"status": "running", "step": "life_event", "progress": 80})
        customers = db.execute(select(Customer)).scalars().all()
        for customer in customers:
            db.refresh(customer)
            if customer.stage == "active":
                await orchestrator.run_for_customer(customer.id)
                await asyncio.sleep(1.5)

        set_demo_state({"status": "complete", "step": "done", "progress": 100})
        await manager.send_demo_progress("done", "complete")
        await manager.broadcast("demo_complete", {"message": "Demo complete — all 4 agents ran"})

    except Exception as e:
        logger.error("Demo run failed: %s", e, exc_info=True)
        set_demo_state({"status": "failed", "error": str(e), "progress": -1})
        await manager.broadcast("demo_failed", {"error": str(e)})


@router.post("/run")
async def run_demo(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    state = get_demo_state()
    if state and state.get("status") == "running":
        return {"message": "Demo already running", "state": state}

    set_demo_state({"status": "starting", "step": "init", "progress": 0})
    background_tasks.add_task(_run_demo_sequence, db)

    return {"success": True, "message": "Demo started", "state": get_demo_state()}


@router.post("/reset")
def reset_demo(
    db: Session = Depends(get_db),
    banker: Banker = Depends(get_current_banker),
):
    """Wipe all customer data and re-seed."""
    # Clear all related data (CASCADE handles children)
    db.execute(delete(Customer))
    db.commit()

    # Clear Redis demo state
    clear_demo_state()

    # Re-seed
    customers = seed_customers(db)

    return {
        "success": True,
        "message": "Demo reset and re-seeded",
        "customers": [{"id": c.id, "name": c.name} for c in customers],
    }


@router.get("/state")
def get_state(banker: Banker = Depends(get_current_banker)):
    """Get current demo state from Redis."""
    state = get_demo_state()
    return state or {"status": "idle", "step": None, "progress": 0}
