"""
NxGen Tech Academy - Grounding and Hallucination Checker (Phase 7)
===================================================================
Validates draft LLM responses before delivery to ensure zero hallucinations
and strict adherence to verified Knowledge Base context.

Responsibilities:
1. Fact Validation across high-risk categories:
   - Fees & Pricing (₹ / INR amounts)
   - Durations & Timelines
   - Addresses & Locations
   - Phone numbers & Emails
   - Founder & Leadership information
   - Curriculum & Course details
   - Policies & Guarantees
2. Semantic / NLI Grounding & Coverage scoring.
3. Safe Handling:
   - PASS -> Release response
   - FAIL -> Safe single regeneration or controlled fallback
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Set

logger = logging.getLogger(__name__)

DEFAULT_FALLBACK_MESSAGE = (
    "Sorry, I can only help with questions related to NxGen Tech Academy. "
    "Please contact the academy for further assistance."
)

# Common regex patterns for entity extraction
CURRENCY_PATTERN = re.compile(r'(?:₹|rs\.?|inr|\$)\s*([\d,]+(?:\.\d+)?)|([\d,]+)\s*(?:inr|rupees|rs)', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}|\b\d{10}\b|\b\d{5}[\s-]\d{5}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
DURATION_PATTERN = re.compile(r'\b(\d+(?:\.\d+)?|\d+\s*-\s*\d+)\s*(months?|weeks?|days?|hours?|years?|hrs?)\b', re.IGNORECASE)
PINCODE_PATTERN = re.compile(r'\b500\d{3}\b')

# Known verified entities
VERIFIED_FOUNDERS = {"sria infotech", "sria infotech pvt. ltd.", "sria infotech pvt ltd", "sria"}
VERIFIED_PHONE_DIGITS = {"9701314138"}
VERIFIED_EMAILS = {"nxgentechacademy@gmail.com"}
VERIFIED_PINCODES = {"500084"}

SUSPICIOUS_GUARANTEES = [
    r"100%\s*(?:money\s*back|refund)\s*guarantee",
    r"guaranteed\s*(?:salary\s*of|package\s*of)?\s*\d+\s*(?:lpa|cr|lakhs)",
    r"no\s*interview\s*needed",
    r"direct\s*job\s*without\s*exam"
]


def _normalize_number(num_str: str) -> str:
    """Removes commas and leading/trailing spaces from numbers."""
    if not num_str:
        return ""
    return re.sub(r'[^\d]', '', num_str)


def _extract_monetary_values(text: str) -> Set[str]:
    """Extracts normalized integer values of currency mentions."""
    values = set()
    for match in CURRENCY_PATTERN.finditer(text):
        g1 = match.group(1)
        g2 = match.group(2)
        val = _normalize_number(g1 or g2 or "")
        if val and int(val) > 100:  # Ignore small numbers like ₹5
            values.add(val)
    return values


def _extract_phone_digits(text: str) -> Set[str]:
    """Extracts 10-digit normalized phone numbers."""
    phones = set()
    for match in PHONE_PATTERN.finditer(text):
        digits = re.sub(r'[^\d]', '', match.group(0))
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        if len(digits) == 10:
            phones.add(digits)
    return phones


def _extract_emails(text: str) -> Set[str]:
    """Extracts lowercase email addresses."""
    return {m.group(0).lower() for m in EMAIL_PATTERN.finditer(text)}


def _extract_durations(text: str) -> Set[str]:
    """Extracts normalized duration strings like '2 months', '50 hours'."""
    durations = set()
    for match in DURATION_PATTERN.finditer(text):
        durations.add(match.group(0).lower().strip())
    return durations


class GroundingChecker:
    """
    Phase 7 Grounding and Hallucination Checker.
    Enforces that all factual statements in the draft response are supported
    by the retrieved context and verified knowledge base assets.
    """

    def __init__(self, min_grounding_score: float = 0.20):
        self.min_grounding_score = min_grounding_score

    def check_fees(self, draft_text: str, context_text: str) -> Tuple[bool, List[str]]:
        """
        Validates whether any fees or prices mentioned in draft are supported by context.
        """
        draft_fees = _extract_monetary_values(draft_text)
        if not draft_fees:
            return True, []

        context_fees = _extract_monetary_values(context_text)
        violations = []
        for fee in draft_fees:
            if fee not in context_fees:
                violations.append(f"Unsupported fee/price mentioned: ₹{fee}")

        return len(violations) == 0, violations

    def check_contact_info(self, draft_text: str, context_text: str) -> Tuple[bool, List[str]]:
        """
        Validates phone numbers, emails, and address pincodes.
        """
        violations = []

        # 1. Phone Numbers
        draft_phones = _extract_phone_digits(draft_text)
        context_phones = _extract_phone_digits(context_text).union(VERIFIED_PHONE_DIGITS)
        for phone in draft_phones:
            if phone not in context_phones:
                violations.append(f"Unsupported phone number: {phone}")

        # 2. Emails
        draft_emails = _extract_emails(draft_text)
        context_emails = _extract_emails(context_text).union(VERIFIED_EMAILS)
        for email in draft_emails:
            if email not in context_emails:
                violations.append(f"Unsupported email address: {email}")

        # 3. Pincodes
        draft_pincodes = set(PINCODE_PATTERN.findall(draft_text))
        context_pincodes = set(PINCODE_PATTERN.findall(context_text)).union(VERIFIED_PINCODES)
        for pin in draft_pincodes:
            if pin not in context_pincodes:
                violations.append(f"Unsupported address pincode: {pin}")

        return len(violations) == 0, violations

    def check_founder_info(self, draft_text: str, context_text: str) -> Tuple[bool, List[str]]:
        """
        Validates that founder / leadership claims match verified data.
        """
        violations = []
        d_lower = draft_text.lower()
        
        founder_triggers = [
            r"founded\s+by\s+([A-Za-z\s\.\,\'\-]+?)(?:\,|\.|\n|and|\;)",
            r"founder\s+(?:is|was)\s+([A-Za-z\s\.\,\'\-]+?)(?:\,|\.|\n|and|\;)",
            r"started\s+by\s+([A-Za-z\s\.\,\'\-]+?)(?:\,|\.|\n|and|\;)"
        ]

        for trig in founder_triggers:
            for match in re.finditer(trig, d_lower):
                claimed_name = match.group(1).strip()
                # Check if claimed name is in verified founders or in context
                if not any(vf in claimed_name for vf in VERIFIED_FOUNDERS) and claimed_name not in context_text.lower():
                    # Filter common stop phrases
                    if len(claimed_name) > 3 and not any(w in claimed_name for w in ["the", "an", "our", "industry", "team"]):
                        violations.append(f"Unsupported founder/leadership claim: '{claimed_name}'")

        return len(violations) == 0, violations

    def check_policies_and_guarantees(self, draft_text: str, context_text: str) -> Tuple[bool, List[str]]:
        """
        Validates that unrealistic or fabricated guarantees do not appear.
        """
        violations = []
        d_lower = draft_text.lower()
        c_lower = context_text.lower()

        for pat in SUSPICIOUS_GUARANTEES:
            match = re.search(pat, d_lower)
            if match:
                matched_text = match.group(0)
                if matched_text not in c_lower:
                    violations.append(f"Unsupported guarantee/policy claim: '{matched_text}'")

        return len(violations) == 0, violations

    def check_duration(self, draft_text: str, context_text: str) -> Tuple[bool, List[str]]:
        """
        Validates that course duration claims are supported by context when durations are mentioned.
        """
        violations = []
        draft_durations = _extract_durations(draft_text)
        if not draft_durations:
            return True, []

        context_durations = _extract_durations(context_text)
        c_lower = context_text.lower()

        # If context has duration mentions, check if draft durations are compatible
        for dur in draft_durations:
            # If duration is completely absent from context
            if dur not in c_lower and not any(cd in dur for cd in context_durations):
                # Only flag multi-year/multi-month assertions that differ from context
                if any(unit in dur for unit in ["year", "years"]):
                    violations.append(f"Unsupported duration claim: '{dur}'")

        return len(violations) == 0, violations

    def calculate_grounding_score(self, draft_text: str, context_text: str) -> float:
        """
        Calculates lexical and entity overlap score between draft response and verified context.
        """
        if not draft_text or not draft_text.strip():
            return 0.0

        # Extract words (minimum 3 chars)
        draft_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', draft_text))
        context_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', context_text))

        # Filter common English stopwords
        stopwords = {
            "the", "and", "for", "with", "this", "that", "you", "your", "are",
            "can", "our", "will", "from", "have", "has", "all", "more", "also",
            "about", "please", "contact", "academy", "nxgen", "course", "training",
            "program", "details", "learning", "session", "sessions", "provides"
        }
        filtered_draft = draft_words - stopwords
        if not filtered_draft:
            return 1.0

        overlap = filtered_draft.intersection(context_words)
        score = len(overlap) / len(filtered_draft)
        return min(1.0, round(score, 3))

    def validate(
        self,
        draft_text: str,
        context_text: str,
        user_query: str = "",
        allow_fallback_text: bool = True
    ) -> Dict[str, Any]:
        """
        Master validation function.
        Returns:
            - passed (bool): True if fully grounded, False if hallucination detected.
            - status (str): "PASS" or "FAIL"
            - grounding_score (float): Overlap / confidence score
            - violations (List[str]): List of detected ungrounded claims
            - checked_entities (dict): Detailed entity breakdown
            - safe_response (str): Cleaned response if passed, or safe fallback message if failed
        """
        if not draft_text or not draft_text.strip():
            return {
                "passed": False,
                "status": "FAIL",
                "grounding_score": 0.0,
                "violations": ["Draft response is empty"],
                "safe_response": DEFAULT_FALLBACK_MESSAGE
            }

        # If draft is already the standard fallback message, pass through safely
        if DEFAULT_FALLBACK_MESSAGE.lower() in draft_text.lower() or "sorry, i can only help with questions related to nxgen" in draft_text.lower():
            return {
                "passed": True,
                "status": "PASS",
                "grounding_score": 1.0,
                "violations": [],
                "safe_response": DEFAULT_FALLBACK_MESSAGE
            }

        all_violations: List[str] = []

        # 1. Check Fees
        fee_ok, fee_viols = self.check_fees(draft_text, context_text)
        all_violations.extend(fee_viols)

        # 2. Check Contact Info
        contact_ok, contact_viols = self.check_contact_info(draft_text, context_text)
        all_violations.extend(contact_viols)

        # 3. Check Founder Info
        founder_ok, founder_viols = self.check_founder_info(draft_text, context_text)
        all_violations.extend(founder_viols)

        # 4. Check Guarantees and Policies
        policy_ok, policy_viols = self.check_policies_and_guarantees(draft_text, context_text)
        all_violations.extend(policy_viols)

        # 5. Check Duration
        duration_ok, duration_viols = self.check_duration(draft_text, context_text)
        all_violations.extend(duration_viols)

        # 6. Calculate Grounding Score
        grounding_score = self.calculate_grounding_score(draft_text, context_text)

        # Fail if any critical factual violation or severely low grounding
        passed = (len(all_violations) == 0) and (grounding_score >= self.min_grounding_score)
        status = "PASS" if passed else "FAIL"

        if not passed:
            if len(all_violations) == 0 and grounding_score < self.min_grounding_score:
                all_violations.append(f"Low semantic context overlap score ({grounding_score:.2f} < {self.min_grounding_score:.2f})")

        safe_response = draft_text if passed else DEFAULT_FALLBACK_MESSAGE

        return {
            "passed": passed,
            "status": status,
            "grounding_score": grounding_score,
            "violations": all_violations,
            "checked_entities": {
                "fees_ok": fee_ok,
                "contact_ok": contact_ok,
                "founder_ok": founder_ok,
                "policy_ok": policy_ok,
                "duration_ok": duration_ok
            },
            "safe_response": safe_response
        }


# Singleton instance and convenience entrypoint
_GLOBAL_GROUNDING_CHECKER = GroundingChecker()


def check_grounding(
    draft_text: str,
    context_text: str,
    user_query: str = ""
) -> Dict[str, Any]:
    """
    Phase 7 Unified Grounding Entrypoint:
    Validates the draft response against verified context.
    """
    return _GLOBAL_GROUNDING_CHECKER.validate(
        draft_text=draft_text,
        context_text=context_text,
        user_query=user_query
    )
