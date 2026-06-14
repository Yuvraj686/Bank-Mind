"""Adoption Agent — detects unused features and sends contextual nudges."""
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from agents.base_agent import BaseAgent
from models.customer import Customer
from models.agent_log import AgentLog
from models.conversation import Conversation
from services.llm_service import call_llm
from services.redis_service import get_nudge_count, increment_nudge_count

logger = logging.getLogger(__name__)

MAX_NUDGES_PER_DAY = 2
FEATURE_PRIORITY = ["upi", "sip", "fd", "credit_card", "home_loan"]


class AdoptionAgent(BaseAgent):
    name = "adoption"

    def __init__(self, db: Session):
        super().__init__(db)
        self._system_prompt = self._load_prompt("adoption.txt")

    def can_act(self, customer: Customer) -> bool:
        if customer.stage != "active":
            return False
        # Check Redis nudge limit
        nudge_count = get_nudge_count(customer.id)
        if nudge_count >= MAX_NUDGES_PER_DAY:
            return False
        # Check if any feature not yet adopted
        features = customer.features_adopted or {}
        return any(not features.get(f, False) for f in FEATURE_PRIORITY)

    def _get_next_feature(self, customer: Customer) -> str | None:
        features = customer.features_adopted or {}
        for f in FEATURE_PRIORITY:
            if not features.get(f, False):
                return f
        return None

    async def run(self, customer: Customer) -> AgentLog:
        logger.info("AdoptionAgent running for customer %s (%s)", customer.name, customer.id)

        feature = self._get_next_feature(customer)
        if not feature:
            return self._create_log(
                customer=customer,
                action="no_action",
                reasoning="All features already adopted.",
                confidence=1.0,
                stage_before=customer.stage,
                stage_after=customer.stage,
            )

        user_content = f"""
Customer Profile:
- Name: {customer.name}
- Age: {customer.age}
- City: {customer.city}
- Occupation: {customer.occupation}
- Monthly Income: ₹{customer.income_monthly:,.0f}
- Account Number: {customer.account_number}
- Features Adopted: {customer.features_adopted}

Next feature to nudge: {feature}

Send a personalized, helpful WhatsApp nudge for the '{feature}' feature.
"""

        result = call_llm(
            system_prompt=self._system_prompt,
            user_content=user_content,
            max_tokens=400,
            temperature=0.5,
        )

        message = result.get("message", "")

        # Save conversation
        conv = Conversation(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            sender="agent",
            agent_name="adoption",
            content=message,
            channel="whatsapp",
            is_simulated=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(conv)
        self.db.commit()

        # Increment Redis nudge counter
        increment_nudge_count(customer.id)

        # Mark feature as adopted (optimistic — next run will confirm)
        features = dict(customer.features_adopted or {})
        features[feature] = True
        self._update_customer(customer, features_adopted=features)

        log = self._create_log(
            customer=customer,
            action=result.get("action", "nudge_sent"),
            message_sent=message,
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            stage_before=customer.stage,
            stage_after=customer.stage,
            llm_raw_response=result.get("_raw"),
        )

        return log
