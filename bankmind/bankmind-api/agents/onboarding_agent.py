"""Onboarding Agent — KYC dialogue, eligibility check, account creation."""
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from agents.base_agent import BaseAgent
from models.customer import Customer
from models.agent_log import AgentLog
from models.conversation import Conversation
from models.product_eligibility import ProductEligibility
from services.llm_service import call_llm

logger = logging.getLogger(__name__)

MAX_KYC_ATTEMPTS = 3


class OnboardingAgent(BaseAgent):
    name = "onboarding"

    def __init__(self, db: Session):
        super().__init__(db)
        self._system_prompt = self._load_prompt("onboarding.txt")

    def can_act(self, customer: Customer) -> bool:
        return (
            customer.stage == "onboarding"
            and customer.kyc_status != "verified"
            and customer.kyc_attempts < MAX_KYC_ATTEMPTS
        )

    async def run(self, customer: Customer) -> AgentLog:
        logger.info("OnboardingAgent running for customer %s (%s)", customer.name, customer.id)

        self._update_customer(customer, kyc_attempts=customer.kyc_attempts + 1)

        user_content = f"""
Customer Profile for KYC:
- Name: {customer.name}
- Age: {customer.age}
- City: {customer.city}
- Occupation: {customer.occupation}
- Monthly Income: ₹{customer.income_monthly:,.0f}
- Date of Birth: {customer.date_of_birth or 'Not provided'}

Generate a complete KYC conversation, verify the customer, determine eligibility, and create their account.
"""

        result = call_llm(
            system_prompt=self._system_prompt,
            user_content=user_content,
            max_tokens=800,
            temperature=0.4,
        )

        kyc_status = result.get("kyc_status", "verified")
        account_number = result.get("account_number", f"BKMND-{uuid.uuid4().hex[:8].upper()}")
        eligible_products = result.get("eligible_products", ["savings_account", "upi"])
        stage_before = customer.stage

        # Save conversation turns
        conversation_turns = result.get("conversation", [])
        for turn in conversation_turns:
            conv = Conversation(
                id=str(uuid.uuid4()),
                customer_id=customer.id,
                sender=turn.get("sender", "agent"),
                agent_name="onboarding",
                content=turn.get("content", ""),
                channel="whatsapp",
                is_simulated=True,
                created_at=datetime.utcnow(),
            )
            self.db.add(conv)

        # Save product eligibility
        all_products = ["savings_account", "upi", "credit_card", "home_loan", "sip", "fd"]
        for product in all_products:
            eligibility = ProductEligibility(
                id=str(uuid.uuid4()),
                customer_id=customer.id,
                product_name=product,
                eligible=product in eligible_products,
                activated=product in ["savings_account"],  # savings auto-activated on account creation
                activated_at=datetime.utcnow() if product == "savings_account" else None,
            )
            self.db.add(eligibility)

        # Initialize features_adopted
        features = {
            "upi": False,
            "sip": False,
            "fd": False,
            "credit_card": False,
            "home_loan": False,
        }

        # Update customer
        next_stage = "active" if kyc_status == "verified" else "onboarding"
        self._update_customer(
            customer,
            kyc_status=kyc_status,
            account_number=account_number if kyc_status == "verified" else None,
            stage=next_stage,
            features_adopted=features,
        )
        self.db.commit()

        log = self._create_log(
            customer=customer,
            action=result.get("action", "account_created"),
            message_sent=result.get("message"),
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            stage_before=stage_before,
            stage_after=next_stage,
            llm_raw_response=result.get("_raw"),
        )

        return log
