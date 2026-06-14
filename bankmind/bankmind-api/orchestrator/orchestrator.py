"""Orchestrator — coordinates all agents across the customer lifecycle."""
import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.customer import Customer
from agents.base_agent import BaseAgent
from agents.acquisition_agent import AcquisitionAgent
from agents.onboarding_agent import OnboardingAgent
from agents.adoption_agent import AdoptionAgent
from agents.life_event_agent import LifeEventAgent
from websocket.manager import manager

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, db: Session):
        self.db = db

    def get_active_agent(self, customer: Customer) -> BaseAgent | None:
        """Return the correct agent for this customer's current state."""
        agents = [
            AcquisitionAgent(self.db),
            OnboardingAgent(self.db),
            AdoptionAgent(self.db),
            LifeEventAgent(self.db),
        ]
        for agent in agents:
            if agent.can_act(customer):
                return agent
        return None

    async def run_for_customer(self, customer_id: str) -> dict:
        """Run the appropriate agent for one customer with processing lock."""
        customer = self.db.get(Customer, customer_id)
        if not customer:
            return {"error": "Customer not found", "customer_id": customer_id}

        if customer.currently_processing:
            logger.warning("Customer %s already being processed — skipping", customer_id)
            return {"skipped": True, "reason": "already_processing"}

        # Lock
        customer.currently_processing = True
        self.db.commit()

        try:
            agent = self.get_active_agent(customer)
            if agent is None:
                logger.info("No agent can act on customer %s (stage=%s)", customer.name, customer.stage)
                return {"skipped": True, "reason": "no_agent_available"}

            logger.info("Running %s agent for %s", agent.name, customer.name)
            log = await agent.run(customer)

            # Refresh customer to get updated state
            self.db.refresh(customer)

            # Broadcast WebSocket event
            await manager.send_agent_action(
                customer_id=customer.id,
                customer_name=customer.name,
                agent=agent.name,
                action=log.action,
                message=log.message_sent,
                reasoning=log.reasoning,
                stage=customer.stage,
                log_id=log.id,
            )

            # Emit stage change if applicable
            if log.stage_before != log.stage_after and log.stage_after:
                await manager.send_stage_change(
                    customer_id=customer.id,
                    customer_name=customer.name,
                    from_stage=log.stage_before or "unknown",
                    to_stage=log.stage_after,
                )

            await manager.send_kpi_update()

            return {
                "success": True,
                "agent": agent.name,
                "action": log.action,
                "log_id": log.id,
                "customer_id": customer_id,
            }

        except Exception as e:
            logger.error("Agent run failed for %s: %s", customer_id, e, exc_info=True)
            return {"error": str(e), "customer_id": customer_id}

        finally:
            # Always release lock
            try:
                customer = self.db.get(Customer, customer_id)
                if customer:
                    customer.currently_processing = False
                    self.db.commit()
            except Exception:
                pass

    async def run_all(self) -> list[dict]:
        """Run agents for all customers where an agent can act."""
        customers = self.db.execute(select(Customer)).scalars().all()
        results = []
        for customer in customers:
            if not customer.currently_processing:
                result = await self.run_for_customer(customer.id)
                results.append(result)
                await asyncio.sleep(0.5)  # Small delay between customers
        return results
