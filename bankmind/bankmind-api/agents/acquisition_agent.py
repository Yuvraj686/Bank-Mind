"""Acquisition Agent — scores leads and sends personalized outreach."""
import logging
from sqlalchemy.orm import Session

from agents.base_agent import BaseAgent
from models.customer import Customer
from models.agent_log import AgentLog
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


class AcquisitionAgent(BaseAgent):
    name = "acquisition"

    def __init__(self, db: Session):
        super().__init__(db)
        self._system_prompt = self._load_prompt("acquisition.txt")

    def can_act(self, customer: Customer) -> bool:
        """Act only on leads without a score yet."""
        return customer.stage == "lead" and customer.lead_score is None

    async def run(self, customer: Customer) -> AgentLog:
        logger.info("AcquisitionAgent running for customer %s (%s)", customer.name, customer.id)

        # Build user content
        pages = customer.pages_viewed or "pricing, features"
        user_content = f"""
Customer Profile:
- Name: {customer.name}
- Age: {customer.age}
- City: {customer.city}
- Occupation: {customer.occupation}
- Monthly Income: ₹{customer.income_monthly:,.0f}
- Website Visits: {customer.website_visits}
- Pages Viewed: {pages}
"""

        result = call_llm(
            system_prompt=self._system_prompt,
            user_content=user_content,
            max_tokens=500,
            temperature=0.3,
        )

        score = float(result.get("lead_score", 50))
        next_stage = "onboarding" if score >= 70 else "lead"

        # Update customer
        stage_before = customer.stage
        self._update_customer(
            customer,
            lead_score=score,
            stage=next_stage,
        )

        log = self._create_log(
            customer=customer,
            action=result.get("action", "lead_scored"),
            message_sent=result.get("message"),
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            stage_before=stage_before,
            stage_after=next_stage,
            llm_raw_response=result.get("_raw"),
        )

        return log
