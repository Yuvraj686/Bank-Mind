"""LLM service — Anthropic Claude integration with Redis caching, retry, and fallback."""
import json
import hashlib
import logging
import time
from typing import Any

import anthropic

from config import get_settings
from services.redis_service import get_redis

logger = logging.getLogger(__name__)
settings = get_settings()

LLM_CACHE_TTL = 3600  # 1 hour

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _cache_key(system_prompt: str, user_content: str) -> str:
    """Generate a deterministic Redis key from prompt content."""
    raw = f"{system_prompt}::{user_content}"
    return f"llm:cache:{hashlib.sha256(raw.encode()).hexdigest()}"


def call_llm(
    system_prompt: str,
    user_content: str,
    max_tokens: int = 500,
    temperature: float = 0.3,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Call Claude claude-sonnet-4-6 and return parsed JSON response.
    - Checks Redis cache first (1h TTL)
    - Retries once on bad JSON / timeout
    - Returns fallback mock dict on failure or if API key is not configured
    """
    # ── Cache check ──────────────────────────────────────────────────────────
    cache_key = _cache_key(system_prompt, user_content)
    if use_cache:
        try:
            cached = get_redis().get(cache_key)
            if cached:
                logger.info("LLM cache hit for key %s", cache_key[:16])
                return json.loads(cached)
        except Exception:
            pass  # Redis unavailable — proceed without cache

    # Check if API key is not configured/default
    api_key_configured = settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key-here"

    if not api_key_configured:
        logger.info("Anthropic API key not configured. Generating high-fidelity mock response.")
        mock_res = generate_mock_response(system_prompt, user_content)
        if use_cache:
            try:
                get_redis().setex(cache_key, LLM_CACHE_TTL, json.dumps(mock_res))
            except Exception:
                pass
        return mock_res

    # ── LLM call (with 1 retry) ──────────────────────────────────────────────
    for attempt in range(2):
        try:
            response = get_client().messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            raw_text = response.content[0].text.strip()

            # Parse JSON block if wrapped in ```json ... ```
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            result = json.loads(raw_text)
            result["_raw"] = raw_text

            # ── Cache success ────────────────────────────────────────────────
            if use_cache:
                try:
                    get_redis().setex(cache_key, LLM_CACHE_TTL, json.dumps(result))
                except Exception:
                    pass

            return result

        except (json.JSONDecodeError, IndexError) as e:
            logger.warning("LLM JSON parse error (attempt %d): %s", attempt + 1, e)
            if attempt == 0:
                time.sleep(2)
            continue

        except anthropic.APITimeoutError:
            logger.warning("LLM timeout (attempt %d)", attempt + 1)
            if attempt == 0:
                time.sleep(5)
            continue

        except anthropic.APIError as e:
            logger.error("LLM API error: %s. Falling back to mock response.", e)
            break

    # ── Fallback to Mock ─────────────────────────────────────────────────────
    logger.info("LLM call failed or unauthorized — generating high-fidelity mock response.")
    mock_res = generate_mock_response(system_prompt, user_content)
    if use_cache:
        try:
            get_redis().setex(cache_key, LLM_CACHE_TTL, json.dumps(mock_res))
        except Exception:
            pass
    return mock_res


def generate_mock_response(system_prompt: str, user_content: str) -> dict[str, Any]:
    """Generates realistic mock JSON responses for the 4 agents to allow offline testing."""
    import re
    import uuid
    import random

    # Extract customer info
    name = ""
    name_match = re.search(r"Name:\s*([^\n\r]+)", user_content)
    if name_match:
        name = name_match.group(1).strip()
        
    city = "Mumbai"
    city_match = re.search(r"City:\s*([^\n\r]+)", user_content)
    if city_match:
        city = city_match.group(1).strip()
        
    occupation = "Professional"
    occ_match = re.search(r"Occupation:\s*([^\n\r]+)", user_content)
    if occ_match:
        occupation = occ_match.group(1).strip()
        
    income = 50000.0
    inc_match = re.search(r"Monthly Income:\s*₹?([0-9,]+)", user_content)
    if inc_match:
        income = float(inc_match.group(1).replace(",", ""))
        
    # Detect agent type
    is_acquisition = "Acquisition" in system_prompt or "acquisition" in system_prompt.lower()
    is_onboarding = "Onboarding" in system_prompt or "onboarding" in system_prompt.lower()
    is_adoption = "Adoption" in system_prompt or "adoption" in system_prompt.lower()
    is_life_event = "Life-Event" in system_prompt or "life_event" in system_prompt.lower() or "life-event" in system_prompt.lower()
    
    res = {}
    
    if is_acquisition:
        score = 85
        msg = f"Hi {name}! Welcome to BankMind. Since you're looking into our modern banking features, I wanted to share that we offer seamless solutions. Let me know if you would like to discuss further."
        reason = f"Customer {name} shows good potential as a {occupation} in {city} with solid monthly income."
        
        if "Priya" in name:
            score = 92
            msg = f"Hi Priya! I noticed you were exploring BankMind's high-yield savings options and home loan products. We'd love to help you customize a plan for your needs in Mumbai. Are you free for a quick 2-minute call today?"
            reason = "Priya shows very high digital intent with 12 website visits and checks on savings/home loan pages. As a Software Engineer in Mumbai with a ₹80,000 monthly income, she is an ideal candidate for onboarding."
        elif "Rahul" in name:
            score = 85
            msg = "Hi Rahul! Welcome to BankMind. Since you're looking into education planning features, I wanted to share that we offer special education plans with tax-saving benefits. Can I share a brief brochure with you?"
            reason = "Rahul shows strong interest in education loans and savings pages. As a Marketing Manager in Bangalore, his ₹65,000 monthly income and targeted browsing justify immediate onboarding."
        elif "Ananya" in name:
            score = 88
            msg = "Hello Dr. Ananya! Thank you for visiting BankMind. I saw you were looking at our premium FD and home loan solutions. As a medical professional, you are eligible for our exclusive Private Banking benefits. Let me know if you would like an overview."
            reason = "Dr. Ananya is a high-income doctor in Chennai checking premium services. Her high profile and target pages make her an excellent lead for onboarding."
        elif "Vikram" in name:
            score = 95
            msg = "Hi Vikram! I saw you were checking out our premium travel credit cards. For a business owner in Ahmedabad, our cards offer unlimited lounge access and 3x rewards on business travel. Would you like to check your pre-approved limit?"
            reason = "Vikram shows maximum intent with 15 visits, targeting travel and credit card sections. High business income makes him a premium candidate for our active onboarding flow."
        elif "Sneha" in name:
            score = 78
            msg = "Hi Sneha! Hope you're doing well in Hyderabad. I noticed you were checking our UPI and savings features. We've got a seamless digital account setup that takes under 5 minutes. Would you like to get started?"
            reason = "Sneha is a Product Manager in Hyderabad with solid income. Her interest in daily utility features (UPI, savings) indicates she's ready for onboarding."
            
        res = {
            "action": "lead_scored",
            "lead_score": score,
            "message": msg,
            "reasoning": reason,
            "confidence": 0.9,
            "next_stage": "onboarding" if score >= 70 else "lead"
        }
        
    elif is_onboarding:
        acc_num = f"BKMND-{uuid.uuid4().hex[:8].upper()}"
        eligible = ["savings_account", "upi"]
        if income >= 100000:
            eligible.extend(["credit_card", "home_loan", "fd", "sip"])
        elif income >= 50000:
            eligible.extend(["credit_card", "fd", "sip"])
        else:
            eligible.extend(["fd", "sip"])
            
        # Simulated PAN and Aadhaar
        pan = f"ABCDE{random.randint(1000, 9999)}F"
        aadhaar = f"{random.randint(1000, 9999)}"
        
        convo = [
            {"sender": "agent", "content": f"Hello {name}, welcome to BankMind's automated onboarding! To get started with your account activation, could you please confirm your PAN and Aadhaar last 4 digits?"},
            {"sender": "customer", "content": f"Sure! Here is my PAN: {pan} and my Aadhaar last 4: {aadhaar}."},
            {"sender": "agent", "content": "Thank you! Our automated verification system is running check on your documents... Perfect! Everything is successfully verified."},
            {"sender": "customer", "content": "Great, thanks! How long does the account setup take?"},
            {"sender": "agent", "content": f"It is instant! Your account has been created. Your account number is {acc_num}. We've also enabled UPI and savings account access."}
        ]
        
        res = {
            "action": "account_created",
            "kyc_status": "verified",
            "account_number": acc_num,
            "pan_number": pan,
            "aadhaar_last4": aadhaar,
            "eligible_products": eligible,
            "conversation": convo,
            "message": f"Welcome to BankMind, {name}! Your account is active. Your account number is {acc_num}. You can now set up UPI and activate other premium benefits.",
            "reasoning": f"KYC documents verified successfully. Monthly income of ₹{income:,.0f} qualifies customer for: {', '.join(eligible)}.",
            "confidence": 0.95,
            "next_stage": "active"
        }
        
    elif is_adoption:
        # Get feature nudged
        feature_match = re.search(r"Next feature to nudge:\s*([^\n\r]+)", user_content)
        feature = feature_match.group(1).strip() if feature_match else "upi"
        
        msg = f"Hi {name}! Tap into more value with BankMind. Set up {feature.upper()} in just 3 steps: 1. Open App, 2. Tap {feature.upper()}, 3. Confirm details. Enjoy instant benefits!"
        if feature == "upi":
            msg = f"Hi {name}! Set up UPI on BankMind in 3 easy steps: 1. Go to Profile, 2. Link your active phone number, 3. Verify bank account. Enjoy instant, seamless daily payments in {city}!"
        elif feature == "sip":
            msg = f"Hi {name}! Start wealth building today. Set up a mutual fund SIP in 3 steps: 1. Tap Wealth, 2. Select a fund, 3. Set monthly debit (starts at just ₹500). Perfect for matching your financial goals as a {occupation}!"
        elif feature == "fd":
            msg = f"Hi {name}! Secure your savings with guaranteed returns. Set up a Fixed Deposit: 1. Tap Deposits, 2. Choose term and amount, 3. Confirm with one click. Get higher interest rates today!"
        elif feature == "credit_card":
            msg = f"Hi {name}! Unlock premium benefits. Apply for your pre-approved Credit Card: 1. Tap Cards, 2. Confirm your details, 3. Get instant virtual card. Enjoy reward points on all spends!"
        elif feature == "home_loan":
            msg = f"Hi {name}! Let's get you closer to your dream home. Apply for a pre-approved Home Loan: 1. Tap Loans, 2. Check eligible amount, 3. Submit documents. Special low rates for {occupation}s!"
            
        res = {
            "action": "nudge_sent",
            "feature_nudged": feature,
            "message": msg,
            "reasoning": f"Nudged {feature} because it is the next priority unused feature. Highly relevant for {name}'s occupation as a {occupation} in {city}.",
            "confidence": 0.9,
            "next_stage": "active"
        }
        
    elif is_life_event:
        event = "none"
        prod = []
        msg = None
        reason = "No significant signals found."
        
        if "Priya" in name:
            event = "salary_jump"
            prod = ["mutual_fund_sip", "premium_savings"]
            msg = "Congratulations Priya on your recent salary increment! 🚀 To celebrate, we've unlocked a pre-approved mutual fund SIP for you. Start investing a portion of your bonus today with just one click."
            reason = "Salary credit increased from ₹80,000 to ₹108,000 (35% increase) in the latest month. Recommending mutual fund SIP to help grow her surplus wealth."
        elif "Rahul" in name:
            event = "school_fees"
            prod = ["education_loan", "children_savings_plan"]
            msg = "Hi Rahul! We noticed your school fee payment this month. To help manage educational expenses seamlessly, BankMind offers a flexible Children's Savings Plan with attractive interest rates. Let us know if you'd like to check it out."
            reason = "Detected education payment of ₹45,000 to DPS School. Recommended children's savings plan to help plan for future educational expenses."
        elif "Ananya" in name:
            event = "medical_expense"
            prod = ["health_insurance", "medical_fd"]
            msg = "Hello Dr. Ananya! We noticed some recent healthcare-related expenses. To protect your family against unexpected events, we've customized a premium Health Insurance coverage package for you. Get details here."
            reason = "Detected high medical category transaction of ₹28,000 at Apollo Hospital. Recommended health insurance for better coverage."
        elif "Vikram" in name:
            event = "travel_increase"
            prod = ["travel_credit_card", "forex_card"]
            msg = "Hi Vikram! Since you've been traveling frequently lately, we've pre-approved you for our Premium Signature Travel Card. Get unlimited lounge access across India and 5x rewards on flight bookings."
            reason = "Detected multiple travel transactions (IndiGo/Air India bookings totaling over ₹35,000) in the past month. Recommended Travel Credit Card."
            
        res = {
            "action": "life_event_detected" if event != "none" else "no_life_event",
            "event_detected": event,
            "recommended_products": prod,
            "message": msg,
            "reasoning": reason,
            "confidence": 0.95,
            "next_stage": "active"
        }
        
    res["_raw"] = json.dumps(res)
    res["_mocked"] = True
    return res

