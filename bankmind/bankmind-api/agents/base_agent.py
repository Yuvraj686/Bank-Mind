"""Base agent class with shared interface."""
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

from models.customer import Customer
from models.agent_log import AgentLog

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = "base"

    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def can_act(self, customer: Customer) -> bool:
        """Return True if this agent should act on this customer."""
        ...

    @abstractmethod
    async def run(self, customer: Customer) -> AgentLog:
        """Execute the agent logic and return the created AgentLog."""
        ...

    def _load_prompt(self, prompt_file: str) -> str:
        """Load a system prompt from the prompts/ directory."""
        import os
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", prompt_file
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _create_log(
        self,
        customer: Customer,
        action: str,
        message_sent: str | None = None,
        reasoning: str | None = None,
        confidence: float | None = None,
        stage_before: str | None = None,
        stage_after: str | None = None,
        llm_raw_response: str | None = None,
    ) -> AgentLog:
        """Create and commit an agent log entry."""
        log = AgentLog(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            agent_name=self.name,
            action=action,
            message_sent=message_sent,
            reasoning=reasoning,
            confidence=confidence,
            stage_before=stage_before,
            stage_after=stage_after,
            llm_raw_response=llm_raw_response,
            created_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def _update_customer(self, customer: Customer, **kwargs) -> None:
        """Update customer fields and commit."""
        for key, value in kwargs.items():
            setattr(customer, key, value)
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
