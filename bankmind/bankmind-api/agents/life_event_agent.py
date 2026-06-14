"""Life-Event Agent — detects life signals from transaction history and recommends products."""
import uuid
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from agents.base_agent import BaseAgent
from models.customer import Customer
from models.agent_log import AgentLog
from models.transaction import Transaction
from models.conversation import Conversation
from services.llm_service import call_llm

logger = logging.getLogger(__name__)

COOLDOWN_DAYS = 7
LOOKBACK_DAYS = 60


class LifeEventAgent(BaseAgent):
    name = "life_event"

    def __init__(self, db: Session):
        super().__init__(db)
        self._system_prompt = self._load_prompt("life_event.txt")

    def can_act(self, customer: Customer) -> bool:
        if customer.stage != "active":
            return False
        # Check 7-day cooldown
        if customer.last_life_event_at:
            cooldown_until = customer.last_life_event_at + timedelta(days=COOLDOWN_DAYS)
            if datetime.utcnow() < cooldown_until:
                return False
        return True

    def _get_transactions(self, customer_id: str) -> list[Transaction]:
        cutoff = datetime.utcnow().date() - timedelta(days=LOOKBACK_DAYS)
        return self.db.execute(
            select(Transaction)
            .where(Transaction.customer_id == customer_id)
            .where(Transaction.transaction_date >= cutoff)
            .order_by(Transaction.transaction_date.desc())
        ).scalars().all()

    def _format_transactions(self, transactions: list[Transaction]) -> str:
        if not transactions:
            return "No recent transactions."
        lines = []
        for t in transactions[:40]:  # Cap at 40 for prompt size
            lines.append(
                f"{t.transaction_date} | {t.type.upper()} | ₹{t.amount:,.0f} | "
                f"{t.category} | {t.description}"
            )
        return "\n".join(lines)

    async def run(self, customer: Customer) -> AgentLog:
        logger.info("LifeEventAgent running for customer %s (%s)", customer.name, customer.id)

        transactions = self._get_transactions(customer.id)
        transaction_text = self._format_transactions(transactions)

        user_content = f"""
Customer Profile:
- Name: {customer.name}
- Age: {customer.age}
- City: {customer.city}
- Occupation: {customer.occupation}
- Monthly Income: ₹{customer.income_monthly:,.0f}

Transaction History (last 60 days):
{transaction_text}

Analyze the transactions and detect any life events. Generate a personalized message if an event is found.
"""

        result = call_llm(
            system_prompt=self._system_prompt,
            user_content=user_content,
            max_tokens=500,
            temperature=0.3,
        )

        event_detected = result.get("event_detected", "none")
        message = result.get("message")

        # Save conversation if event found
        if event_detected != "none" and message:
            conv = Conversation(
                id=str(uuid.uuid4()),
                customer_id=customer.id,
                sender="agent",
                agent_name="life_event",
                content=message,
                channel="whatsapp",
                is_simulated=True,
                created_at=datetime.utcnow(),
            )
            self.db.add(conv)
            self.db.commit()

        # Update customer life event tracking
        self._update_customer(
            customer,
            last_life_event_detected=event_detected if event_detected != "none" else customer.last_life_event_detected,
            last_life_event_at=datetime.utcnow(),
        )

        action = "life_event_detected" if event_detected != "none" else "no_life_event"
        log = self._create_log(
            customer=customer,
            action=action,
            message_sent=message,
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            stage_before=customer.stage,
            stage_after=customer.stage,
            llm_raw_response=result.get("_raw"),
        )

        return log
