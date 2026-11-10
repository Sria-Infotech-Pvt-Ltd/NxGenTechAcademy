"""
NxGen Tech Academy - Complete End-to-End RAG & Intelligence Pipeline (Phases 1-8)
================================================================================
PHASE 1: Query Processor (Language -> Intent -> Entities -> Query Rewrite)
PHASE 2: RAG Search (Dense Vector Search + Okapi BM25 + Metadata Filtering)
PHASE 3: Website Tools (Pricing, Products/Courses, FAQs, Academy Info, Demo Booking)
PHASE 4: Reranker (Reciprocal Rank Fusion + Intent/Course/Section Boosts)
PHASE 5: Context Builder (Clean Structured Context Assembly for LLM)
PHASE 6: LLM Integration (Groq LLaMA / DeepSeek Grounded Generation)
PHASE 7: Grounding & Hallucination Check (Multi-layer Fact Verification & Safe Fallback)
PHASE 8: Final Response Formatter & Pipeline Integration (Clean Markdown, Action Routing)

Architecture Flow:
  User Query
  ↓
  Phase 1: Query Processor (Language -> Intent -> Entities -> Query Rewrite)
  ↓
  Phase 2 & 3: RAG Search + Website Tools
  ↓
  Phase 4: Reranker (Ranked by Relevance)
  ↓
  Phase 5: Context Builder (Structured Context)
  ↓
  Phase 6: LLM via Groq (Draft Response)
  ↓
  Phase 7: Grounding & Hallucination Check (Fact Verification)
  ↓
  Phase 8: Final Response Formatter (Clean Markdown, Preserved Actions & Navigation)
  ↓
  React Chat UI (SPA Navigation & Fast Rendering)
"""

import os
import re
import math
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

try:
    from .groq_client import run_kb_chat, generate_rag_response, DEFAULT_FALLBACK_MESSAGE
    from .grounding_check import check_grounding, GroundingChecker
    from .kb_tools import (
        COURSE_REGISTRY,
        _resolve_course,
        get_academy_information,
        get_course_information,
        get_course_section,
        get_common_course_highlights,
        get_course_catalog,
        get_pricing_tool,
        get_product_tool,
        get_faq_tool,
        website_tools_dispatcher
    )
except ImportError:
    from rag.groq_client import run_kb_chat, generate_rag_response, DEFAULT_FALLBACK_MESSAGE
    from rag.grounding_check import check_grounding, GroundingChecker
    from rag.kb_tools import (
        COURSE_REGISTRY,
        _resolve_course,
        get_academy_information,
        get_course_information,
        get_course_section,
        get_common_course_highlights,
        get_course_catalog,
        get_pricing_tool,
        get_product_tool,
        get_faq_tool,
        website_tools_dispatcher
    )

GREETING_RESPONSE = (
    "Hello! Welcome to NxGen Tech Academy. How can I help you today? "
    "I can provide details on our IT courses (Python, AI/ML, Data Analytics, SAP, Digital Marketing), "
    "admission process, demo sessions, placements, and more."
)

GREETING_PATTERNS = [
    r"^hi+$",
    r"^hello+$",
    r"^hey+$",
    r"^heyy+$",
    r"^good\s+(morning|afternoon|evening)$",
    r"^greetings$",
    r"^namaste$",
    r"^namaskar$",
    r"^hola$",
    r"^howdy$",
    r"^vanakkam$",
    r"^pranam$",
    r"^(hi|hello|hey)\s+(there|everyone|team|all|bot|assistant)$"
]

# Common Hinglish and transliterated Indic keywords
HINGLISH_KEYWORDS = {
    "kya", "hai", "kaise", "kitna", "kitni", "batao", "bataiye", "kaha", "kab",
    "kisko", "padhna", "seekhna", "kare", "hoga", "chahiye", "janna", "baare",
    "mein", "me", "aur", "koi", "sir", "madam", "cheppandi", "ekkada", "entha",
    "unndha", "namaskar", "namaste", "shukriya", "dhanyavad", "bata"
}

# Section keyword mapping to standardized section names
SECTION_KEYWORDS = {
    "curriculum": ["curriculum", "syllabus", "module", "modules", "topics", "topic", "chapters", "content", "what will i learn", "course outline", "subjects"],
    "fees": ["fee", "fees", "cost", "price", "pricing", "charge", "charges", "kitna", "kitni", "payment", "installment", "emi"],
    "duration": ["duration", "how long", "time", "months", "weeks", "hours", "timeline", "period", "kitna time"],
    "eligibility": ["eligibility", "eligible", "prerequisite", "prerequisites", "qualification", "who can join", "who can learn", "criteria", "background"],
    "projects": ["project", "projects", "real world", "real-time", "hands-on", "capstone", "assignments", "practical"],
    "certification": ["certification", "certificate", "certified", "exam", "completion certificate", "degree", "diploma"],
    "placement": ["placement", "job", "jobs", "placements", "package", "salary", "hiring", "interview", "resume", "guarantee", "career"],
    "location": ["location", "address", "where", "kaha", "branch", "office", "hyderabad", "kphb", "kukatpally", "city", "place", "map"],
    "contact": ["contact", "phone", "number", "email", "call", "whatsapp", "reach", "talk", "helpline"],
    "founder": ["founder", "ceo", "director", "started", "who started", "who runs", "owner", "leadership"],
    "demo": ["demo", "trial", "free session", "live demo", "attend demo", "book demo", "trial class"],
    "highlights": ["highlight", "highlights", "key highlights", "features", "benefits", "why join"]
}

# Out-of-domain rejection patterns
OUT_OF_DOMAIN_PATTERNS = [
    r"\b(weather|forecast|temperature)\b",
    r"\b(president|prime minister|politician|election|politics)\b",
    r"\b(recipe|cook|ingredients|cake|pizza|burger)\b",
    r"\b(football|cricket|fifa|world cup|olympics|ipl)\b",
    r"\b(crypto|bitcoin|ethereum|stock market|share price)\b",
    r"\b(movie|cinema|actor|actress|box office)\b",
    r"\b(capital of|largest country|tallest mountain)\b",
    r"\b(write a (poem|story|song|essay|joke))\b",
    r"\b(solve this math|algebra|calculus)\b"
]


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: QUERY PROCESSOR IMPLEMENTATION
# ═════════════════════════════════════════════════════════════════════════════

class QueryProcessor:
    """
    Phase 1 Query Processor for NxGen Tech Academy Chatbot.
    Transforms raw user queries into structured, normalized, and disambiguated
    query representations for subsequent retrieval and LLM stages.
    """

    @staticmethod
    def detect_language(text: str) -> Tuple[str, bool, float]:
        """
        Detects query language:
        - 'en': Standard English
        - 'hinglish': Transliterated Hindi/Indic in Latin script
        - 'hi': Devanagari script Hindi
        - 'other': Other languages or non-English script
        Returns (language_code, is_english, confidence).
        """
        if not text:
            return "en", True, 1.0

        # Check for Devanagari Unicode block
        if re.search(r'[\u0900-\u097F]', text):
            return "hi", False, 0.95

        # Check for other non-Latin alphabetic scripts
        if re.search(r'[^\x00-\x7F\u0900-\u097F]', text) and not re.search(r'[•\u2011\u2013\u2014]', text):
            return "other", False, 0.85

        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return "en", True, 1.0

        hinglish_matches = [w for w in words if w in HINGLISH_KEYWORDS]
        ratio = len(hinglish_matches) / len(words)

        if ratio >= 0.25 or len(hinglish_matches) >= 2:
            return "hinglish", False, min(0.6 + ratio * 0.4, 0.98)

        if len(hinglish_matches) == 1 and len(words) <= 3:
            return "hinglish", False, 0.80

        return "en", True, 0.95

    @staticmethod
    def extract_entities(text: str, course_context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Extracts domain entities from the query text and active conversation context:
        - course: Specific resolved course name (e.g., 'Python Programming')
        - course_slug: Canonical URL slug
        - course_url: Canonical route URL
        - category: Course category ('SAP Courses', 'Digital Marketing', etc.)
        - section: Course/academy section ('curriculum', 'fees', 'duration', etc.)
        - topic: Specific academy topic ('location', 'founder', 'demo', etc.)
        """
        entities: Dict[str, Any] = {
            "course": None,
            "course_slug": None,
            "course_url": None,
            "category": None,
            "section": None,
            "topic": None
        }

        q_lower = text.lower().strip()

        # Check if query is explicitly an academy-level inquiry (location, address, founder, contact, about)
        is_academy_query = any(
            k in q_lower for k in [
                "where is", "location", "address", "founder", "ceo", "director", "who started",
                "who founded", "contact", "phone", "email", "about nxgen", "about academy",
                "kaha hai", "headquarters", "office", "hyderabad branch", "reach us", "call us"
            ]
        )

        # Check if query is explicitly a course catalog / general courses / trending inquiry
        catalog_patterns = [
            r"\b(courses?\s+offered|courses?\s+available|available\s+courses?|available\s+programs?|available\s+training)\b",
            r"\b(what\s+(types?\s+of\s+)?courses?|which\s+(types?\s+of\s+)?courses?|what\s+courses?)\b",
            r"\b(what\s+(types?\s+of\s+)?programs?|which\s+(types?\s+of\s+)?programs?|what\s+programs?)\b",
            r"\b(what\s+(types?\s+of\s+)?training|which\s+(types?\s+of\s+)?training|what\s+training)\b",
            r"\b(list\s+(of\s+)?(all\s+|the\s+)?(courses?|programs?)|show\s+(me\s+)?(all\s+|the\s+|your\s+)?(courses?|programs?))\b",
            r"\b(course\s+catalog|course\s+catalogue|course\s+list|training\s+catalog|training\s+programs?|program\s+list)\b",
            r"\b(all\s+courses?|all\s+training\s+programs?|complete\s+courses?|all\s+programs?)\b",
            r"\b(give\s+(me\s+)?(the\s+|your\s+)?(course\s+|program\s+)?(catalog|catalogue|list(\s+of\s+programs?)?))\b",
            r"\b(see\s+all\s+(your\s+)?(courses?|programs?)|view\s+(all\s+)?(courses?|programs?))\b",
            r"\b(what\s+can\s+i\s+learn|what\s+do\s+you\s+teach|what\s+training\s+do\s+you\s+provide)\b",
            r"\b(trending\s+courses?|popular\s+courses?|top\s+courses?|best\s+courses?|most\s+popular\s+courses?)\b",
            r"\b(trending\s+programs?|popular\s+programs?|top\s+programs?|best\s+programs?)\b",
            r"\b(which\s+courses?\s+(are\s+)?(trending|popular|best|top|most\s+popular))\b",
            r"\b(which\s+courses?\s+are\s+suitable\s+for\s+beginners|courses?\s+for\s+beginners)\b",
            r"^(courses?|training|programs?)\s*\?*$"
        ]
        is_catalog_query = any(re.search(pat, q_lower) for pat in catalog_patterns)

        # 1. Match Course Names and Aliases explicitly mentioned in the query text
        # Sort keys by length descending to match longer specific names first (e.g. "sap btp freshers" before "sap btp")
        sorted_keys = sorted(COURSE_REGISTRY.keys(), key=len, reverse=True)
        for key in sorted_keys:
            # Word boundary regex matching
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, q_lower):
                c_info = COURSE_REGISTRY[key]
                entities["course"] = c_info["name"]
                entities["course_slug"] = c_info["slug"]
                entities["course_url"] = c_info["url"]
                break

        # 2. Extract Category (using word boundaries to prevent substring collisions like 'pp' in 'opportunities')
        if re.search(r'\b(sap|fico|abap|btp|cpi|basis|sd|mm|pp|qm|fiori|ui5)\b', q_lower):
            entities["category"] = "SAP Courses"
        elif re.search(r'\b(digital marketing|seo|sem|social media|dm)\b', q_lower):
            entities["category"] = "Digital Marketing"
        elif re.search(r'\b(python)\b', q_lower):
            entities["category"] = "Python"
        elif re.search(r'\b(analytics|power bi|data analytics|tableau)\b', q_lower):
            entities["category"] = "Data Analytics"
        elif re.search(r'\b(aiml|ai/ml|machine learning)\b', q_lower):
            entities["category"] = "AIML"
        elif re.search(r'\b(ai|artificial intelligence)\b', q_lower):
            entities["category"] = "AI"

        # 3. Extract Section / Topic (find longest matching keyword across all section categories)
        best_sec = None
        best_len = 0
        for sec_name, kw_list in SECTION_KEYWORDS.items():
            for kw in kw_list:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, q_lower):
                    if len(kw) > best_len:
                        best_len = len(kw)
                        best_sec = sec_name

        if best_sec:
            entities["section"] = best_sec
            if best_sec in ["location", "contact", "founder", "demo", "highlights"]:
                entities["topic"] = best_sec

        # 4. Fallback to active course context only if genuine follow-up and NOT an explicit new category/catalog query
        is_follow_up = (
            entities.get("section") in ["curriculum", "fees", "duration", "eligibility", "projects", "certification", "placement"]
            or any(re.search(r'\b' + re.escape(p) + r'\b', q_lower) for p in ["it", "its", "this course", "the course", "this training", "this program", "this"])
            or any(k in q_lower for k in ["how long", "how much", "what is duration", "what are fees", "tell me about it"])
        )

        has_explicit_category = bool(entities["category"] and not entities["course"])

        if (
            not entities["course"]
            and course_context
            and not is_academy_query
            and not is_catalog_query
            and not has_explicit_category
            and is_follow_up
        ):
            ctx_name = None
            if isinstance(course_context, dict):
                ctx_name = course_context.get("name") or course_context.get("course") or course_context.get("course_name")
            elif isinstance(course_context, str):
                ctx_match = re.search(r'Course:\s*([^,\n\r]+)', course_context, re.IGNORECASE)
                if ctx_match:
                    ctx_name = ctx_match.group(1).strip()
                elif course_context.strip():
                    ctx_name = course_context.strip()

            if ctx_name:
                resolved = _resolve_course(ctx_name)
                if resolved:
                    entities["course"] = resolved["name"]
                    entities["course_slug"] = resolved["slug"]
                    entities["course_url"] = resolved["url"]

        return entities

    @staticmethod
    def identify_intent(
        text: str,
        entities: Dict[str, Any],
        has_context: bool = False
    ) -> Tuple[str, float]:
        """
        Identifies user intent:
        - GREETING
        - DEMO_BOOKING
        - COURSE_CATALOG
        - COURSE_SPECIFIC
        - COURSE_HIGHLIGHTS
        - ACADEMY_INFO
        - ADMISSIONS_FEES
        - PLACEMENT_INFO
        - OUT_OF_DOMAIN
        - GENERAL_INQUIRY
        """
        q_lower = text.lower().strip()

        # 1. Greeting
        for pattern in GREETING_PATTERNS:
            if re.match(pattern, q_lower):
                return "GREETING", 1.0

        # 2. Out of domain check
        for ood_pat in OUT_OF_DOMAIN_PATTERNS:
            if re.search(ood_pat, q_lower):
                # Ensure it is not an academy course question
                if not any(k in q_lower for k in ["course", "training", "nxgen", "academy", "fees", "syllabus", "admission", "demo"]):
                    return "OUT_OF_DOMAIN", 0.95

        # 3. Demo Booking
        if any(k in q_lower for k in ["book a demo", "book demo", "schedule demo", "request demo", "trial class", "free demo", "live demo"]):
            return "DEMO_BOOKING", 0.98

        # 4. Course Highlights
        if any(k in q_lower for k in ["course highlights", "academy highlights", "what are the highlights", "key highlights"]):
            return "COURSE_HIGHLIGHTS", 0.95

        # 5. Academy Info (Location, Founder, Contact, About) — prioritized over course context
        if (
            entities.get("section") in ["location", "contact", "founder"]
            or any(k in q_lower for k in ["where is", "location", "address", "founder", "ceo", "director", "contact", "phone", "email", "about nxgen", "about academy", "kaha hai", "headquarters", "office", "who started", "who founded"])
        ):
            return "ACADEMY_INFO", 0.95

        # 6. Fees & Duration / Pricing Overview (multi-course / general)
        if (
            any(k in q_lower for k in ["check fees & duration", "check fees and duration", "fees & duration", "fees and duration", "course fees & duration", "course fees and duration", "all course fees", "fee structure", "how much are the fees"])
            or (entities.get("section") in ["fees", "duration"] and not entities.get("course"))
        ):
            return "ADMISSIONS_FEES", 0.95

        # 7. Placements / Industrial Readiness
        if any(k in q_lower for k in ["placement", "explore placement", "explore placement opportunities", "placement opportunities", "placement support", "job guarantee", "interview prep", "hiring partners", "industry readiness"]):
            return "PLACEMENT_INFO", 0.95

        # 8. Course Catalog / Multi-course list / Category inquiry
        catalog_patterns = [
            r"\b(explore\s+(our\s+|all\s+|the\s+)?courses?|explore\s+training|explore\s+programs?)\b",
            r"\b(courses?\s+offered|courses?\s+available|available\s+courses?|available\s+programs?|available\s+training)\b",
            r"\b(what\s+(types?\s+of\s+)?courses?|which\s+(types?\s+of\s+)?courses?|what\s+courses?)\b",
            r"\b(what\s+(types?\s+of\s+)?programs?|which\s+(types?\s+of\s+)?programs?|what\s+programs?)\b",
            r"\b(what\s+(types?\s+of\s+)?training|which\s+(types?\s+of\s+)?training|what\s+training)\b",
            r"\b(list\s+(of\s+)?(all\s+|the\s+)?(courses?|programs?)|show\s+(me\s+)?(all\s+|the\s+|your\s+)?(courses?|programs?))\b",
            r"\b(course\s+catalog|course\s+catalogue|course\s+list|training\s+catalog|training\s+programs?|program\s+list)\b",
            r"\b(all\s+courses?|all\s+training\s+programs?|complete\s+courses?|all\s+programs?)\b",
            r"\b(give\s+(me\s+)?(the\s+|your\s+)?(course\s+|program\s+)?(catalog|catalogue|list(\s+of\s+programs?)?))\b",
            r"\b(see\s+all\s+(your\s+)?(courses?|programs?)|view\s+(all\s+)?(courses?|programs?))\b",
            r"\b(what\s+can\s+i\s+learn|what\s+do\s+you\s+teach|what\s+training\s+do\s+you\s+provide)\b",
            r"\b(trending\s+courses?|popular\s+courses?|top\s+courses?|best\s+courses?|most\s+popular\s+courses?)\b",
            r"\b(trending\s+programs?|popular\s+programs?|top\s+programs?|best\s+programs?)\b",
            r"\b(which\s+courses?\s+(are\s+)?(trending|popular|best|top|most\s+popular))\b",
            r"\b(which\s+courses?\s+are\s+suitable\s+for\s+beginners|courses?\s+for\s+beginners)\b",
            r"^(courses?|training|programs?)\s*\?*$"
        ]
        is_catalog = any(re.search(pat, q_lower) for pat in catalog_patterns)

        if is_catalog or (entities.get("category") and not entities.get("course")):
            return "COURSE_CATALOG", 0.95

        # 9. Specific Course Inquiry
        if entities.get("course"):
            return "COURSE_SPECIFIC", 0.95

        # 10. Admissions / Enrollment
        if any(k in q_lower for k in ["admission", "enroll", "enrollment", "register", "registration", "how to join"]):
            return "ADMISSIONS_FEES", 0.90

        if has_context and entities.get("section"):
            return "COURSE_SPECIFIC", 0.85

        return "GENERAL_INQUIRY", 0.75

    @staticmethod
    def rewrite_query(
        raw_query: str,
        intent: str,
        entities: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Rewrites conversational or ambiguous queries into concise, disambiguated retrieval queries.
        """
        cleaned = normalize_query(raw_query)

        # 1. Greetings
        if intent == "GREETING":
            return cleaned

        # 2. Demo Booking
        if intent == "DEMO_BOOKING":
            course_part = f" for {entities['course']}" if entities.get("course") else ""
            return f"Book a free live demo session{course_part}"

        # 3. Course Highlights
        if intent == "COURSE_HIGHLIGHTS":
            return "NxGen Tech Academy official common course highlights"

        # 4. Course Catalog
        if intent == "COURSE_CATALOG":
            category = entities.get("category")
            if category:
                return f"NxGen Tech Academy {category} course catalog and training programs"
            if any(k in cleaned.lower() for k in ["trending", "popular", "top", "best"]):
                return "NxGen Tech Academy complete technology course catalog and available training programs"
            return "NxGen Tech Academy all 18 courses offered catalog across Python, AI/ML, Data Analytics, Digital Marketing, and SAP"

        # 5. Specific Course Queries
        if intent == "COURSE_SPECIFIC" and entities.get("course"):
            course_name = entities["course"]
            sec = entities.get("section")
            if sec == "curriculum":
                return f"{course_name} course modules and syllabus"
            elif sec == "fees":
                return f"{course_name} course fee structure"
            elif sec == "duration":
                return f"{course_name} course duration and timeline"
            elif sec == "eligibility":
                return f"{course_name} course eligibility and prerequisites"
            elif sec == "projects":
                return f"{course_name} course practical projects and capstone"
            elif sec == "certification":
                return f"{course_name} course certification details"
            elif sec == "placement":
                return f"{course_name} course placement and career opportunities"
            elif sec == "faqs":
                return f"{course_name} frequently asked questions"
            else:
                return f"{course_name} course comprehensive overview and details"

        # 6. Academy Information
        if intent == "ACADEMY_INFO":
            topic = entities.get("topic") or entities.get("section")
            if topic == "location" or "where" in cleaned.lower() or "address" in cleaned.lower() or "kaha" in cleaned.lower():
                return "NxGen Tech Academy address and location details"
            elif topic == "founder" or "who" in cleaned.lower():
                return "NxGen Tech Academy founder and leadership background"
            elif topic == "contact":
                return "NxGen Tech Academy official contact numbers and email"
            return "NxGen Tech Academy about us and overview"

        # 7. Admissions & Placements
        if intent == "ADMISSIONS_FEES":
            if any(k in cleaned.lower() for k in ["fee", "fees", "duration", "cost", "price", "check fees", "pricing"]):
                return "NxGen Tech Academy course fees and duration overview for all programs"
            return "NxGen Tech Academy admission process and enrollment procedure"

        if intent == "PLACEMENT_INFO":
            return "NxGen Tech Academy placement opportunities, mock interviews, and career support across all programs"

        # 8. Out of Domain
        if intent == "OUT_OF_DOMAIN":
            return cleaned

        # 9. Clean filler phrases from general inquiries
        filler_patterns = [
            r"^(can\s+you\s+(please\s+)?tell\s+me(\s+about)?\s*)",
            r"^(i\s+want\s+to\s+know(\s+about)?\s*)",
            r"^(could\s+you\s+(please\s+)?explain(\s+about)?\s*)",
            r"^(please\s+give\s+me(\s+the)?\s*details\s+(of|on|about)\s*)",
            r"^(what\s+is\s+the\s+information\s+(on|about)\s*)",
            r"^(bataiye\s+|batao\s+|mujhe\s+janna\s+hai\s+)"
        ]
        rewritten = cleaned
        for pat in filler_patterns:
            rewritten = re.sub(pat, "", rewritten, flags=re.IGNORECASE).strip()

        return rewritten if rewritten else cleaned


def process_query(
    query_text: str,
    course_context: Optional[Any] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Main entrypoint for Phase 1 Query Processor.
    Transforms raw user query into standardized structured output.
    """
    cleaned = normalize_query(query_text)
    if not cleaned:
        return {
            "raw_query": query_text or "",
            "cleaned_query": "",
            "rewritten_query": "",
            "language": "en",
            "is_english": True,
            "intent": "EMPTY",
            "entities": {
                "course": None,
                "course_slug": None,
                "course_url": None,
                "category": None,
                "section": None,
                "topic": None
            },
            "is_greeting": False,
            "is_out_of_domain": False,
            "confidence": 0.0
        }

    lang, is_en, lang_conf = QueryProcessor.detect_language(cleaned)
    entities = QueryProcessor.extract_entities(cleaned, course_context=course_context)
    has_context = bool(course_context or (conversation_history and len(conversation_history) > 0))
    intent, intent_conf = QueryProcessor.identify_intent(cleaned, entities, has_context=has_context)
    rewritten = QueryProcessor.rewrite_query(cleaned, intent, entities, language=lang)

    is_greeting_flag = (intent == "GREETING")
    is_ood_flag = (intent == "OUT_OF_DOMAIN")

    return {
        "raw_query": query_text,
        "cleaned_query": cleaned,
        "rewritten_query": rewritten,
        "language": lang,
        "is_english": is_en,
        "intent": intent,
        "entities": entities,
        "is_greeting": is_greeting_flag,
        "is_out_of_domain": is_ood_flag,
        "confidence": round(intent_conf * lang_conf, 3)
    }


def normalize_query(query: str) -> str:
    """
    Performs harmless text cleanup on user queries:
    - Strips leading and trailing whitespace
    - Collapses multiple whitespace characters to a single space
    - Strips leading/trailing punctuation noise
    """
    if not query:
        return ""
    q = query.strip()
    q = re.sub(r'\s+', ' ', q)
    q = re.sub(r'^[^\w\s]+|[^\w\s?]+$', '', q).strip()
    return q


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: RAG SEARCH (VECTOR + BM25 + METADATA FILTERING)
# ═════════════════════════════════════════════════════════════════════════════

class BM25Index:
    """
    Okapi BM25 Lexical Keyword Search Engine for Knowledge Base Chunks.
    Parameters:
      k1 = 1.5 (term frequency saturation)
      b  = 0.75 (document length penalization)
    """
    def __init__(self, chunks: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks = chunks
        self.N = len(chunks)
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self._build_index()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'[a-zA-Z0-9]+', text.lower())

    def _build_index(self):
        total_tokens = 0
        for chunk in self.chunks:
            meta = chunk.get("metadata", {})
            header = f"{meta.get('course', '')} {meta.get('section', '')}"
            full_text = f"{header} {chunk.get('text', '')}"
            tokens = self._tokenize(full_text)
            
            self.doc_lengths.append(len(tokens))
            total_tokens += len(tokens)

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)

            for t in tf.keys():
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avgdl = (total_tokens / self.N) if self.N > 0 else 1.0

        # Precompute Robertson-Spärck Jones IDF with smoothing
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))

    def search(
        self,
        query: str,
        top_k: int = 5,
        allowed_indices: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes BM25 search over all chunks or a metadata-filtered subset.
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        scores: List[Tuple[int, float]] = []
        target_indices = allowed_indices if allowed_indices is not None else range(self.N)

        for idx in target_indices:
            if idx >= self.N:
                continue
            doc_len = self.doc_lengths[idx]
            tf_dict = self.doc_term_freqs[idx]
            len_norm = 1.0 - self.b + self.b * (doc_len / self.avgdl)

            score = 0.0
            for t in tokens:
                if t in tf_dict:
                    freq = tf_dict[t]
                    term_idf = self.idf.get(t, 0.0)
                    term_score = term_idf * (freq * (self.k1 + 1.0)) / (freq + self.k1 * len_norm)
                    score += term_score

            if score > 0.0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:top_k]

        max_score = top_scores[0][1] if top_scores else 1.0
        results: List[Dict[str, Any]] = []

        for rank, (chunk_id, raw_score) in enumerate(top_scores, 1):
            chunk = self.chunks[chunk_id]
            norm_score = round(raw_score / max_score, 4) if max_score > 0 else 0.0
            results.append({
                "rank": rank,
                "chunk_id": chunk_id,
                "score": norm_score,
                "raw_score": round(raw_score, 4),
                "course": chunk.get("metadata", {}).get("course"),
                "section": chunk.get("metadata", {}).get("section"),
                "source_file": chunk.get("metadata", {}).get("source_file"),
                "text": chunk.get("text", "")
            })

        return results


# Global RAG Search Resource Caches
_CACHED_CHUNKS: Optional[List[Dict[str, Any]]] = None
_CACHED_EMBEDDINGS: Optional[np.ndarray] = None
_CACHED_ST_MODEL: Any = None
_CACHED_BM25_INDEX: Optional[BM25Index] = None


def find_project_rag_files() -> Tuple[Path, Path]:
    """Locates chunks.json and embeddings.npy across project directories."""
    base_dir = Path(__file__).resolve().parent

    chunks_candidates = [
        base_dir / "chunks" / "chunks.json",
        base_dir.parent / "rag" / "chunks" / "chunks.json",
        base_dir.parent / "chunks" / "chunks.json",
    ]
    chunks_path = None
    for p in chunks_candidates:
        if p.is_file():
            chunks_path = p.resolve()
            break

    embeddings_candidates = [
        base_dir / "embeddings" / "embeddings.npy",
        base_dir.parent / "rag" / "embeddings" / "embeddings.npy",
        base_dir.parent / "embeddings" / "embeddings.npy",
    ]
    embeddings_path = None
    for p in embeddings_candidates:
        if p.is_file():
            embeddings_path = p.resolve()
            break

    if not chunks_path:
        raise FileNotFoundError("Could not locate chunks.json in expected directories.")
    if not embeddings_path:
        raise FileNotFoundError("Could not locate embeddings.npy in expected directories.")

    return chunks_path, embeddings_path


def get_rag_resources() -> Tuple[List[Dict[str, Any]], np.ndarray, Any, BM25Index]:
    """
    Lazily loads and caches chunks.json, embeddings.npy, SentenceTransformer model,
    and BM25Index for high-throughput sub-millisecond retrieval.
    """
    global _CACHED_CHUNKS, _CACHED_EMBEDDINGS, _CACHED_ST_MODEL, _CACHED_BM25_INDEX

    if (
        _CACHED_CHUNKS is not None
        and _CACHED_EMBEDDINGS is not None
        and _CACHED_BM25_INDEX is not None
    ):
        return _CACHED_CHUNKS, _CACHED_EMBEDDINGS, _CACHED_ST_MODEL, _CACHED_BM25_INDEX

    chunks_path, embeddings_path = find_project_rag_files()

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embeddings = np.load(embeddings_path)

    # Initialize SentenceTransformer model with graceful fallback
    st_model = None
    try:
        from sentence_transformers import SentenceTransformer
        st_model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        pass

    bm25_index = BM25Index(chunks)

    _CACHED_CHUNKS = chunks
    _CACHED_EMBEDDINGS = embeddings
    _CACHED_ST_MODEL = st_model
    _CACHED_BM25_INDEX = bm25_index

    return chunks, embeddings, st_model, bm25_index


def filter_chunks_by_metadata(
    chunks: List[Dict[str, Any]],
    course: Optional[str] = None,
    category: Optional[str] = None,
    section: Optional[str] = None,
    source_file: Optional[str] = None
) -> List[int]:
    """
    Returns the list of chunk indices matching the specified metadata constraints.
    """
    matching_indices: List[int] = []

    for idx, chunk in enumerate(chunks):
        meta = chunk.get("metadata", {})
        c_course = (meta.get("course") or "").strip().lower()
        c_section = (meta.get("section") or "").strip().lower()
        c_file = (meta.get("source_file") or "").strip().lower()

        # 1. Course Filter
        if course:
            course_clean = course.strip().lower()
            if course_clean not in c_course and c_course not in course_clean:
                continue

        # 2. Section Filter
        if section:
            sec_clean = section.strip().lower()
            if sec_clean in ["curriculum", "syllabus", "modules"]:
                if not any(k in c_section for k in ["curriculum", "module", "syllabus", "topic"]):
                    continue
            elif sec_clean in ["fees", "cost", "pricing"]:
                if not any(k in c_section for k in ["fee", "cost", "pricing"]):
                    continue
            elif sec_clean in ["duration", "timeline"]:
                if not any(k in c_section for k in ["duration", "timeline"]):
                    continue
            elif sec_clean in ["eligibility", "prerequisites"]:
                if not any(k in c_section for k in ["eligibility", "prerequisite"]):
                    continue
            elif sec_clean in ["projects"]:
                if not any(k in c_section for k in ["project", "hands-on", "real-world"]):
                    continue
            elif sec_clean in ["certification"]:
                if not any(k in c_section for k in ["certification", "certificate"]):
                    continue
            elif sec_clean in ["placement", "industrial_readiness"]:
                if not any(k in c_section for k in ["placement", "industrial readiness", "job"]):
                    continue
            elif sec_clean in ["location", "address"]:
                if not any(k in c_section or k in c_file for k in ["contact", "location", "about"]):
                    continue
            elif sec_clean in ["highlights"]:
                if not any(k in c_section for k in ["highlight", "stat"]):
                    continue
            elif sec_clean not in c_section:
                continue

        # 3. Category Filter
        if category:
            cat_clean = category.strip().lower()
            if "sap" in cat_clean:
                if "sap" not in c_course and "sap" not in c_file:
                    continue
            elif "digital marketing" in cat_clean or "dm" in cat_clean:
                if "digital marketing" not in c_course and "digital_marketing" not in c_file:
                    continue
            elif "python" in cat_clean:
                if "python" not in c_course and "python" not in c_file:
                    continue
            elif "analytics" in cat_clean:
                if "data analytics" not in c_course and "data_analytics" not in c_file:
                    continue
            elif "aiml" in cat_clean:
                if "aiml" not in c_course and "aiml" not in c_file:
                    continue

        # 4. Source File Filter
        if source_file:
            if source_file.lower() not in c_file:
                continue

        matching_indices.append(idx)

    return matching_indices


def vector_search(
    query: str,
    top_k: int = 5,
    allowed_indices: Optional[List[int]] = None,
    threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Executes dense vector cosine similarity search over stored 384-d embeddings.
    """
    chunks, embeddings, st_model, _ = get_rag_resources()

    if st_model is not None:
        query_emb = st_model.encode([query], convert_to_numpy=True)[0]
    else:
        # Fallback dense projection if sentence_transformers is unavailable
        query_emb = np.zeros(embeddings.shape[1], dtype=np.float32)

    # Compute cosine similarities
    dot_products = np.dot(embeddings, query_emb)
    norm_embeds = np.linalg.norm(embeddings, axis=1)
    norm_query = np.linalg.norm(query_emb)

    if norm_query > 0:
        sims = dot_products / (norm_embeds * norm_query + 1e-9)
    else:
        sims = np.zeros(len(chunks), dtype=np.float32)

    scores: List[Tuple[int, float]] = []
    target_indices = allowed_indices if allowed_indices is not None else range(len(chunks))

    for idx in target_indices:
        if idx >= len(chunks):
            continue
        score = float(sims[idx])
        if score >= threshold:
            scores.append((idx, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_scores = scores[:top_k]

    results: List[Dict[str, Any]] = []
    for rank, (chunk_id, score) in enumerate(top_scores, 1):
        chunk = chunks[chunk_id]
        results.append({
            "rank": rank,
            "chunk_id": chunk_id,
            "score": round(score, 4),
            "course": chunk.get("metadata", {}).get("course"),
            "section": chunk.get("metadata", {}).get("section"),
            "source_file": chunk.get("metadata", {}).get("source_file"),
            "text": chunk.get("text", "")
        })

    return results


def rag_search(
    query_input: Any,
    course_context: Optional[Any] = None,
    top_k: int = 5,
    strict_metadata: bool = False
) -> Dict[str, Any]:
    """
    Phase 2 Unified RAG Search Pipeline:
    1. Ingests Query Processor output (or processes raw query).
    2. Runs Vector Search (dense semantic similarity).
    3. Runs BM25 Search (sparse lexical matching).
    4. Applies Metadata Filtering (course, category, section).
    5. Returns candidate pool ready for Phase 4 Reranker.
    """
    if isinstance(query_input, dict) and "rewritten_query" in query_input:
        processed = query_input
    else:
        processed = process_query(str(query_input), course_context=course_context)

    query_str = processed["rewritten_query"] or processed["cleaned_query"]
    entities = processed.get("entities", {})

    course_filter = entities.get("course")
    category_filter = entities.get("category")
    section_filter = entities.get("section")

    chunks, _, _, bm25_index = get_rag_resources()

    # 1. Metadata Filtering
    filtered_indices = filter_chunks_by_metadata(
        chunks=chunks,
        course=course_filter,
        category=category_filter,
        section=section_filter
    )

    allowed_indices = filtered_indices if (strict_metadata and filtered_indices) else None

    # 2. Vector Search
    vector_results = vector_search(
        query=query_str,
        top_k=top_k,
        allowed_indices=allowed_indices
    )

    # 3. BM25 Search
    bm25_results = bm25_index.search(
        query=query_str,
        top_k=top_k,
        allowed_indices=allowed_indices
    )

    # 4. Construct Unified Candidate Pool (Deduplicated with Source Tracking)
    candidate_map: Dict[int, Dict[str, Any]] = {}

    for item in vector_results:
        cid = item["chunk_id"]
        candidate_map[cid] = {
            "chunk_id": cid,
            "course": item["course"],
            "section": item["section"],
            "source_file": item["source_file"],
            "text": item["text"],
            "vector_score": item["score"],
            "bm25_score": None,
            "retrieval_sources": ["vector"],
            "metadata_match": cid in filtered_indices
        }

    for item in bm25_results:
        cid = item["chunk_id"]
        if cid in candidate_map:
            candidate_map[cid]["bm25_score"] = item["score"]
            candidate_map[cid]["retrieval_sources"].append("bm25")
        else:
            candidate_map[cid] = {
                "chunk_id": cid,
                "course": item["course"],
                "section": item["section"],
                "source_file": item["source_file"],
                "text": item["text"],
                "vector_score": None,
                "bm25_score": item["score"],
                "retrieval_sources": ["bm25"],
                "metadata_match": cid in filtered_indices
            }

    candidate_list = list(candidate_map.values())

    return {
        "query": processed["cleaned_query"],
        "rewritten_query": query_str,
        "language": processed.get("language", "en"),
        "intent": processed.get("intent", "GENERAL_INQUIRY"),
        "metadata_filters": {
            "course": course_filter,
            "category": category_filter,
            "section": section_filter,
            "matching_chunks_count": len(filtered_indices)
        },
        "vector_results": vector_results,
        "bm25_results": bm25_results,
        "candidates": candidate_list,
        "total_candidates": len(candidate_list)
    }


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4: RERANKER
# ═════════════════════════════════════════════════════════════════════════════

class CandidateReranker:
    """
    Phase 4 Multi-Factor Relevance Reranker:
    Consumes heterogeneous candidate pools from:
    1. Phase 2 RAG Search (Vector + BM25 + Metadata chunks)
    2. Phase 3 Website Tools (Pricing, Products, FAQ)

    Computes a grounded multi-factor score:
    - Base Retrieval Score (Vector / BM25 / Tool Prior)
    - Course & Entity Exact Alignment Boost / Conflict Penalty
    - Section & Topic Intent Alignment Boost
    - Keyword / Lexical Overlap Density Boost
    - Structured Tool Utility Boost

    Returns ordered, ranked candidates prioritized for answering the user's specific query.
    """

    def __init__(
        self,
        course_match_boost: float = 0.30,
        section_match_boost: float = 0.35,
        intent_match_boost: float = 0.20,
        lexical_match_boost: float = 0.15,
        conflict_penalty: float = 0.40
    ):
        self.course_match_boost = course_match_boost
        self.section_match_boost = section_match_boost
        self.intent_match_boost = intent_match_boost
        self.lexical_match_boost = lexical_match_boost
        self.conflict_penalty = conflict_penalty

    def _extract_query_tokens(self, text: str) -> set:
        """Extracts significant alphanumeric query tokens excluding basic stopwords."""
        stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "and", "or",
            "is", "are", "was", "were", "what", "which", "who", "whom", "this", "that",
            "these", "those", "how", "can", "i", "you", "we", "they", "it", "do", "does",
            "did", "tell", "me", "about", "give", "details", "info", "please", "want",
            "know", "like", "would", "many", "much", "there", "have", "offer", "provide"
        }
        tokens = set(re.findall(r'[a-zA-Z0-9]+', text.lower()))
        return {t for t in tokens if t not in stopwords and len(t) > 1}

    def _compute_lexical_overlap(self, query_tokens: set, candidate_text: str) -> float:
        """Computes query term coverage in candidate text."""
        if not query_tokens or not candidate_text:
            return 0.0
        doc_tokens = set(re.findall(r'[a-zA-Z0-9]+', candidate_text.lower()))
        if not doc_tokens:
            return 0.0
        matched = query_tokens.intersection(doc_tokens)
        return len(matched) / len(query_tokens)

    def score_candidate(
        self,
        candidate: Dict[str, Any],
        processed_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates individual candidate relevance score and full explanation breakdown.
        """
        query_str = processed_query.get("cleaned_query", "")
        intent = processed_query.get("intent", "GENERAL_INQUIRY")
        entities = processed_query.get("entities", {})

        target_course = (entities.get("course") or "").strip().lower()
        target_category = (entities.get("category") or "").strip().lower()
        target_section = (entities.get("section") or "").strip().lower()
        target_topic = (entities.get("topic") or "").strip().lower()

        # Extract candidate attributes
        cand_course = (candidate.get("course") or candidate.get("course_name") or "").strip().lower()
        cand_category = (candidate.get("category") or "").strip().lower()
        cand_section = (candidate.get("section") or "").strip().lower()
        cand_text = candidate.get("text", "")
        source_type = candidate.get("source_type", candidate.get("source", "rag"))
        tool_type = candidate.get("tool_type")

        # 1. Base Score
        base_score = 0.0
        if source_type == "website_tool" or tool_type:
            # Website tools carry high prior confidence when dispatched
            base_score = 0.70
        else:
            v_score = candidate.get("vector_score")
            b_score = candidate.get("bm25_score")
            if v_score is not None and b_score is not None:
                base_score = (0.50 * float(v_score)) + (0.50 * float(b_score))
            elif v_score is not None:
                base_score = 0.85 * float(v_score)
            elif b_score is not None:
                base_score = 0.85 * float(b_score)
            elif candidate.get("score") is not None:
                base_score = float(candidate["score"])
            else:
                base_score = 0.50

        course_boost = 0.0
        section_boost = 0.0
        intent_boost = 0.0
        lexical_boost = 0.0
        penalty = 0.0

        # 2. Course / Entity Alignment & Conflict Checks
        if target_course:
            if cand_course and (target_course in cand_course or cand_course in target_course):
                course_boost += self.course_match_boost
            elif target_category and target_category in cand_course:
                course_boost += self.course_match_boost * 0.6
            elif cand_course and cand_course not in ["all courses", "about nxgen tech academy", "courses overview", "book a free demo"]:
                # Conflicting specific course
                penalty += self.conflict_penalty
        elif target_category:
            if target_category in cand_category or target_category in cand_course:
                course_boost += self.course_match_boost * 0.8
            elif cand_course and cand_course not in ["all courses", "about nxgen tech academy", "courses overview", "book a free demo"]:
                # If target is SAP Courses and candidate is Python, penalize
                if not any(k in cand_course for k in ["sap", "btp", "abap", "fico", "mm", "sd", "pp", "qm", "cpi", "basis"]):
                    penalty += self.conflict_penalty * 0.7

        # 3. Section / Topic Alignment
        if target_section:
            if cand_section and (target_section == cand_section or target_section in cand_section or cand_section in target_section):
                section_boost += self.section_match_boost
            elif target_section in cand_text.lower():
                section_boost += self.section_match_boost * 0.5
            elif cand_section and cand_section not in ["overview", "details", "complete catalog", "faqs", "course catalog", "pricing & fees"]:
                # If query is asking specifically for projects and this chunk is fees
                if target_section in ["projects", "curriculum", "fees", "placement", "eligibility"] and cand_section in ["projects", "curriculum", "fees", "placement", "eligibility"]:
                    penalty += 0.15

        if target_topic:
            if target_topic in cand_section or target_topic in cand_course or target_topic in cand_text.lower():
                section_boost += self.section_match_boost * 0.7

        # 4. Intent Alignment
        if intent == "COURSE_CATALOG":
            if tool_type == "product" or "catalog" in cand_section or "all courses" in cand_course:
                intent_boost += self.intent_match_boost
        elif intent == "DEMO_BOOKING":
            if "demo" in cand_section or "demo" in cand_text.lower() or candidate.get("action_text") == "Book Demo":
                intent_boost += self.intent_match_boost
        elif intent == "ADMISSIONS_FEES":
            if tool_type == "pricing" or cand_section == "fees" or "fee" in cand_text.lower() or "price" in cand_text.lower():
                intent_boost += self.intent_match_boost
        elif intent == "PLACEMENT_INFO":
            if cand_section == "placement" or "placement" in cand_text.lower() or candidate.get("action_url") == "/why-choose-us":
                intent_boost += self.intent_match_boost
        elif intent == "ACADEMY_INFO":
            if "about" in cand_course or "about" in cand_section or any(k in cand_text.lower() for k in ["founder", "location", "address", "udaya vensar"]):
                intent_boost += self.intent_match_boost
        elif intent == "COURSE_HIGHLIGHTS":
            if "highlight" in cand_section or "highlights" in cand_text.lower():
                intent_boost += self.intent_match_boost

        # 5. Lexical & Query Token Coverage
        query_tokens = self._extract_query_tokens(query_str)
        lexical_coverage = self._compute_lexical_overlap(query_tokens, cand_text)
        lexical_boost = self.lexical_match_boost * lexical_coverage

        # Section keyword density bonus
        if target_section == "curriculum" and any(k in cand_text.lower() for k in ["module 1", "module 2", "syllabus", "topics"]):
            lexical_boost += 0.10
        elif target_section == "projects" and any(k in cand_text.lower() for k in ["capstone", "real-time project", "mini project", "hands-on"]):
            lexical_boost += 0.10

        raw_total = base_score + course_boost + section_boost + intent_boost + lexical_boost - penalty
        norm_score = max(0.0, min(1.0, raw_total / 1.6))

        # Standardize Course / Academy / FAQ Navigation Metadata
        action_url = candidate.get("action_url")
        action_text = candidate.get("action_text")
        course_slug = candidate.get("course_slug")

        if not action_url:
            source_file = (candidate.get("source_file") or "").lower()
            if "faq" in source_file or "faq" in cand_course:
                if any(k in source_file or k in cand_course for k in ["demo", "admission"]):
                    action_url = "/courses/sap-btp-freshers-course-training"
                    action_text = "Book Demo"
                elif any(k in source_file or k in cand_course for k in ["placement", "job", "career"]):
                    action_url = "/why-choose-us"
                    action_text = "Why Choose Us"
                elif any(k in source_file or k in cand_course for k in ["location", "contact", "address"]):
                    action_url = "/contact-us"
                    action_text = "Contact Us"
                elif any(k in source_file or k in cand_course for k in ["bsnl", "partner", "association"]):
                    action_url = "/bsnl-skill-development-partner"
                    action_text = "View Partners"
                elif any(k in source_file or k in cand_course for k in ["about"]):
                    action_url = "/about-us"
                    action_text = "About Us"
                else:
                    action_url = "/training-programs"
                    action_text = "View Courses"
            elif cand_course and ("about" in cand_course.lower() or "about" in source_file):
                if any(k in cand_section.lower() or k in cand_text.lower() for k in ["location", "contact", "address"]):
                    action_url = "/contact-us"
                    action_text = "Contact Us"
                elif any(k in cand_section.lower() or k in cand_text.lower() for k in ["placement", "why choose"]):
                    action_url = "/why-choose-us"
                    action_text = "Why Choose Us"
                else:
                    action_url = "/about-us"
                    action_text = "About Us"
            elif cand_course and "all courses" in cand_course.lower():
                action_url = "/training-programs"
                action_text = "View Courses"
            elif cand_course:
                c_info = _resolve_course(cand_course)
                if c_info:
                    action_url = c_info["url"]
                    action_text = c_info["action_text"]
                    course_slug = c_info["slug"]

        # Intent-specific action override
        if intent == "DEMO_BOOKING":
            action_url = "/courses/sap-btp-freshers-course-training"
            action_text = "Book Demo"
        elif intent == "COURSE_CATALOG":
            action_text = "View Courses"
            if target_category == "sap courses" or (cand_category and "sap" in cand_category.lower()):
                action_url = "/training-programs?category=SAP+Courses"
            elif target_category == "digital marketing" or (cand_category and "digital" in cand_category.lower()):
                action_url = "/training-programs?category=Digital+Marketing"
            elif not action_url:
                action_url = "/training-programs"

        title = candidate.get("title")
        if not title:
            sec_display = cand_section.capitalize() if cand_section else "Overview"
            c_display = candidate.get("course") or candidate.get("course_name") or "NxGen Tech Academy"
            title = f"{c_display} - {sec_display}"

        return {
            "title": title,
            "source_type": source_type,
            "tool_type": tool_type,
            "course": candidate.get("course") or candidate.get("course_name"),
            "course_slug": course_slug,
            "category": candidate.get("category"),
            "section": candidate.get("section"),
            "source_file": candidate.get("source_file"),
            "chunk_id": candidate.get("chunk_id"),
            "action_url": action_url,
            "action_text": action_text,
            "text": cand_text,
            "score": round(norm_score, 4),
            "score_breakdown": {
                "raw_score": round(raw_total, 4),
                "base_score": round(base_score, 4),
                "course_boost": round(course_boost, 4),
                "section_boost": round(section_boost, 4),
                "intent_boost": round(intent_boost, 4),
                "lexical_boost": round(lexical_boost, 4),
                "penalty": round(penalty, 4),
                "final_score": round(norm_score, 4)
            }
        }

    def rerank(
        self,
        query_input: Any,
        rag_results: Optional[Any] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None,
        candidates: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 5,
        course_context: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Reranks all input candidates (from RAG search and Website tools) based on query relevance.
        """
        # 1. Resolve processed query
        if isinstance(query_input, dict) and "intent" in query_input:
            processed = query_input
        else:
            processed = process_query(str(query_input), course_context=course_context)

        # 2. Gather candidates pool
        all_candidates: List[Dict[str, Any]] = []

        if candidates:
            all_candidates.extend(candidates)
        else:
            if rag_results:
                if isinstance(rag_results, dict) and "candidates" in rag_results:
                    for c in rag_results["candidates"]:
                        item = dict(c)
                        item["source_type"] = "rag"
                        all_candidates.append(item)
                elif isinstance(rag_results, list):
                    for c in rag_results:
                        item = dict(c)
                        item.setdefault("source_type", "rag")
                        all_candidates.append(item)

            if tool_results:
                for t in tool_results:
                    item = dict(t)
                    item["source_type"] = "website_tool"
                    all_candidates.append(item)

        # If no candidates provided, automatically retrieve them via Phase 2 & 3
        if not all_candidates:
            rag_res = rag_search(processed, top_k=top_k * 2)
            for c in rag_res.get("candidates", []):
                item = dict(c)
                item["source_type"] = "rag"
                all_candidates.append(item)

            tools_res = website_tools_dispatcher(processed)
            for t in tools_res:
                item = dict(t)
                item["source_type"] = "website_tool"
                all_candidates.append(item)

        # 3. Score and Rerank
        scored_candidates = []
        for cand in all_candidates:
            scored = self.score_candidate(cand, processed)
            scored_candidates.append(scored)

        # 4. Sort deterministically by raw_score (descending), section_boost (descending), course_boost (descending), base_score (descending)
        scored_candidates.sort(
            key=lambda x: (
                x["score_breakdown"]["raw_score"],
                x["score_breakdown"]["section_boost"],
                x["score_breakdown"]["course_boost"],
                x["score_breakdown"]["base_score"],
                1 if x["source_type"] == "rag" else 0
            ),
            reverse=True
        )

        # 5. Assign final ranks
        for rank_idx, item in enumerate(scored_candidates, 1):
            item["rank"] = rank_idx

        return scored_candidates[:top_k]


# Singleton instance and convenience functional entrypoint
_GLOBAL_RERANKER = CandidateReranker()


def rerank_candidates(
    query_input: Any,
    rag_results: Optional[Any] = None,
    tool_results: Optional[List[Dict[str, Any]]] = None,
    candidates: Optional[List[Dict[str, Any]]] = None,
    top_k: int = 5,
    course_context: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Phase 4 Unified Reranker Entrypoint:
    Reranks candidates from RAG search and Website Tools to prioritize
    the most relevant information for answering the specific question.
    """
    return _GLOBAL_RERANKER.rerank(
        query_input=query_input,
        rag_results=rag_results,
        tool_results=tool_results,
        candidates=candidates,
        top_k=top_k,
        course_context=course_context
    )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 5: CONTEXT BUILDER
# ═════════════════════════════════════════════════════════════════════════════

class ContextBuilder:
    """
    Phase 5 Context Builder:
    Constructs a clean, structured, grounded context for the LLM by combining:
    - Phase 1 Processed User Query & Entities
    - Phase 2 & 3 Heterogeneous Candidates
    - Phase 4 Reranked Top Results (RAG Chunks + Website Tools)

    Clearly separates:
    1. User Question & Intent Details
    2. Retrieved Knowledge Base Information (RAG Chunks)
    3. Relevant Website Tool Results (Pricing, Products, FAQ)
    4. Source Information & Navigation Actions
    """

    def __init__(self, max_context_chars: int = 8000, max_top_candidates: int = 4):
        self.max_context_chars = max_context_chars
        self.max_top_candidates = max_top_candidates

    def build_context(
        self,
        query_input: Any,
        reranked_results: Optional[List[Dict[str, Any]]] = None,
        rag_results: Optional[Any] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None,
        course_context: Optional[Any] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Builds a structured LLM context and formatted prompt string from reranked results.
        """
        # 1. Resolve Processed Query
        if isinstance(query_input, dict) and "intent" in query_input:
            processed = query_input
        else:
            processed = process_query(str(query_input), course_context=course_context)

        # 2. If reranked_results not provided, run Phase 4 Reranker
        if reranked_results is None:
            reranked_results = rerank_candidates(
                query_input=processed,
                rag_results=rag_results,
                tool_results=tool_results,
                top_k=top_k or self.max_top_candidates,
                course_context=course_context
            )

        top_candidates = reranked_results[:(top_k or self.max_top_candidates)]

        # 3. Categorize into RAG Chunks vs Website Tools
        rag_chunks: List[Dict[str, Any]] = []
        website_tool_items: List[Dict[str, Any]] = []
        sources: List[Dict[str, Any]] = []
        primary_action = {"action_url": None, "action_text": None}

        for item in top_candidates:
            # Capture first valid primary action
            if not primary_action["action_url"] and item.get("action_url"):
                primary_action["action_url"] = item.get("action_url")
                primary_action["action_text"] = item.get("action_text")

            source_type = item.get("source_type", "rag")
            if source_type == "website_tool" or item.get("tool_type"):
                website_tool_items.append(item)
                sources.append({
                    "type": "website_tool",
                    "title": item.get("title"),
                    "tool_type": item.get("tool_type"),
                    "action_url": item.get("action_url"),
                    "action_text": item.get("action_text")
                })
            else:
                rag_chunks.append(item)
                sources.append({
                    "type": "rag_chunk",
                    "title": item.get("title"),
                    "course": item.get("course"),
                    "section": item.get("section"),
                    "source_file": item.get("source_file"),
                    "score": item.get("score")
                })

        # 4. Assemble Formatted Context Sections
        sections = []

        # SECTION 1: USER QUESTION & INTENT
        q_text = processed.get("rewritten_query") or processed.get("cleaned_query") or ""
        intent = processed.get("intent", "GENERAL_INQUIRY")
        entities = processed.get("entities", {})

        ent_summary = []
        if entities.get("course"):
            ent_summary.append(f"Course: {entities['course']}")
        if entities.get("category"):
            ent_summary.append(f"Category: {entities['category']}")
        if entities.get("section"):
            ent_summary.append(f"Section: {entities['section']}")
        if entities.get("topic"):
            ent_summary.append(f"Topic: {entities['topic']}")

        user_block = [
            "### [1] USER INQUIRY",
            f"- **User Question:** {q_text}",
            f"- **Identified Intent:** {intent}",
            f"- **Key Entities:** {', '.join(ent_summary) if ent_summary else 'None'}"
        ]
        sections.append("\n".join(user_block))

        # SECTION 2: RETRIEVED KNOWLEDGE BASE INFORMATION
        if rag_chunks:
            kb_block = ["### [2] RETRIEVED KNOWLEDGE BASE INFORMATION"]
            for idx, chk in enumerate(rag_chunks, 1):
                c_title = chk.get("title", f"Chunk {idx}")
                c_score = chk.get("score", "N/A")
                c_text = chk.get("text", "").strip()
                if len(c_text) > 1200:
                    c_text = c_text[:1200] + "..."
                kb_block.append(f"#### Document [{idx}]: {c_title} (Score: {c_score})\n{c_text}\n")
            sections.append("\n".join(kb_block))
        else:
            sections.append("### [2] RETRIEVED KNOWLEDGE BASE INFORMATION\nNo direct knowledge base text chunks retrieved.")

        # SECTION 3: RELEVANT WEBSITE TOOL RESULTS
        if website_tool_items:
            tools_block = ["### [3] RELEVANT WEBSITE TOOL RESULTS"]
            for idx, tool in enumerate(website_tool_items, 1):
                t_type = (tool.get("tool_type") or "Tool").upper()
                t_title = tool.get("title", f"Tool {idx}")
                t_text = tool.get("text", "").strip()
                if len(t_text) > 3500:
                    t_text = t_text[:3500] + "..."
                t_action = f"{tool.get('action_text')} -> {tool.get('action_url')}" if tool.get('action_url') else "None"
                tools_block.append(f"#### Tool [{idx}] [{t_type}]: {t_title} (Action: {t_action})\n{t_text}\n")
            sections.append("\n".join(tools_block))
        else:
            sections.append("### [3] RELEVANT WEBSITE TOOL RESULTS\nNo active website tool results.")

        # SECTION 4: SOURCE INFORMATION & NAVIGATION ACTIONS
        src_block = ["### [4] SOURCE INFORMATION & NAVIGATION METADATA"]
        for s in sources:
            if s["type"] == "rag_chunk":
                src_block.append(f"- **[KB Chunk]** {s.get('title')} ({s.get('source_file') or 'KB'}) [Relevance: {s.get('score')}]")
            else:
                src_block.append(f"- **[Website Tool]** {s.get('title')} (Action: {s.get('action_url')})")

        src_block.append(f"\n- **Primary Navigation Action:** {primary_action['action_text'] or 'View Courses'} -> {primary_action['action_url'] or '/training-programs'}")
        sections.append("\n".join(src_block))

        # Join full context string
        full_context_text = "\n\n" + ("\n" + "=" * 60 + "\n").join(sections) + "\n\n"

        # Character budgeting
        if len(full_context_text) > self.max_context_chars:
            full_context_text = full_context_text[:self.max_context_chars] + "\n\n[... Context truncated for token budget ...]"

        token_estimate = len(full_context_text.split())

        return {
            "query": q_text,
            "intent": intent,
            "entities": entities,
            "context_text": full_context_text,
            "rag_chunks_count": len(rag_chunks),
            "tool_results_count": len(website_tool_items),
            "total_top_candidates": len(top_candidates),
            "sources": sources,
            "primary_action": primary_action,
            "token_estimate": token_estimate,
            "structured_context": {
                "user_inquiry": {
                    "question": q_text,
                    "intent": intent,
                    "entities": entities
                },
                "retrieved_information": rag_chunks,
                "tool_results": website_tool_items,
                "source_information": sources,
                "primary_action": primary_action
            }
        }


# Singleton instance and convenience functional entrypoint
_GLOBAL_CONTEXT_BUILDER = ContextBuilder()


def build_llm_context(
    query_input: Any,
    reranked_results: Optional[List[Dict[str, Any]]] = None,
    rag_results: Optional[Any] = None,
    tool_results: Optional[List[Dict[str, Any]]] = None,
    course_context: Optional[Any] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    top_k: int = 4
) -> Dict[str, Any]:
    """
    Phase 5 Unified Context Builder Entrypoint:
    Takes the best results from RAG Search, Website Tools, and Reranker,
    and creates a clean, structured context for the LLM.
    """
    return _GLOBAL_CONTEXT_BUILDER.build_context(
        query_input=query_input,
        reranked_results=reranked_results,
        rag_results=rag_results,
        tool_results=tool_results,
        course_context=course_context,
        conversation_history=conversation_history,
        top_k=top_k
    )


def query_knowledge_base(
    query_text: str,
    course_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main entrypoint for chatbot queries.
    Integrates the full Phase 1-6 Architecture:
    User Query -> Query Processor -> RAG Search + Tools -> Reranker -> Context Builder -> LLM (Groq) -> Draft Response
    """
    # 1. Run Phase 1: Query Processor
    processed = process_query(
        query_text=query_text,
        course_context=course_context,
        conversation_history=conversation_history
    )

    cleaned_query = processed["cleaned_query"]
    if not cleaned_query:
        return {
            "found": False,
            "reply": DEFAULT_FALLBACK_MESSAGE,
            "course": None,
            "course_name": None,
            "course_slug": None,
            "section": None,
            "similarity": 0.0,
            "source_file": None,
            "db_id": None,
            "action_url": None,
            "action_text": None,
            "processed_query": processed
        }

    # 2. Short-circuit Greeting Handling
    if processed["is_greeting"]:
        return {
            "found": True,
            "reply": GREETING_RESPONSE,
            "course": None,
            "course_name": None,
            "course_slug": None,
            "section": None,
            "similarity": 1.0,
            "source_file": None,
            "db_id": None,
            "action_url": None,
            "action_text": None,
            "processed_query": processed
        }

    # 3. Short-circuit Out-of-Domain Safety Handling
    if processed.get("intent") == "OUT_OF_DOMAIN":
        return {
            "found": False,
            "reply": DEFAULT_FALLBACK_MESSAGE,
            "course": None,
            "course_name": None,
            "course_slug": None,
            "section": None,
            "similarity": 0.0,
            "source_file": None,
            "db_id": None,
            "action_url": None,
            "action_text": None,
            "processed_query": processed
        }

    # 4. Phase 2 & 3: RAG Search + Website Tools
    rag_res = rag_search(processed, course_context=course_context, top_k=5)
    tools_res = website_tools_dispatcher(processed, course_context=course_context)

    # 5. Phase 4: Reranker
    reranked_results = rerank_candidates(
        query_input=processed,
        rag_results=rag_res,
        tool_results=tools_res,
        top_k=4,
        course_context=course_context
    )

    # 6. Phase 5: Context Builder
    built_context = build_llm_context(
        query_input=processed,
        reranked_results=reranked_results,
        course_context=course_context,
        conversation_history=conversation_history,
        top_k=4
    )

    # 7. Phase 6 & 7: LLM Integration + Grounding and Hallucination Check
    llm_res = generate_rag_response(
        user_query=query_text,
        built_context=built_context,
        course_context=course_context,
        conversation_history=conversation_history
    )

    found = llm_res.get("found", True)
    raw_reply = llm_res.get("reply", DEFAULT_FALLBACK_MESSAGE)
    grounding_status = llm_res.get("grounding_status", "PASS" if found else "FAIL")
    grounding_info = llm_res.get("grounding", {})

    # 8. Phase 8: Final Response Post-Processing & Payload Assembly
    final_reply = FinalResponseFormatter.format(raw_reply)

    # Extract navigation metadata and actions
    primary_action = built_context.get("primary_action", {})
    action_url = primary_action.get("action_url")
    action_text = primary_action.get("action_text")

    # Determine canonical action_type
    if action_text == "Book Demo" or processed.get("intent") == "DEMO_BOOKING":
        action_type = "book_demo"
        action_text = action_text or "Book Demo"
        action_url = action_url or "/courses/sap-btp-freshers-course-training"
    elif action_text in ["View Course", "View Program"] or processed["entities"].get("course_slug"):
        action_type = "view_course"
        action_text = action_text or "View Course"
        if not action_url and processed["entities"].get("course_slug"):
            action_url = f"/courses/{processed['entities']['course_slug']}"
    elif action_text in ["View Courses", "View Catalog"] or processed.get("intent") == "COURSE_CATALOG":
        action_type = "view_courses"
        action_text = action_text or "View Courses"
        action_url = action_url or "/training-programs"
    else:
        action_type = "view_page" if action_url else None

    course_name = processed["entities"].get("course")
    course_slug = processed["entities"].get("course_slug")
    section = processed["entities"].get("section")

    if not course_name and reranked_results:
        course_name = reranked_results[0].get("course")
        course_slug = reranked_results[0].get("course_slug")
        section = section or reranked_results[0].get("section")

    return {
        "found": found,
        "reply": final_reply,
        "course": course_name,
        "course_name": course_name,
        "course_slug": course_slug,
        "section": section,
        "similarity": 1.0 if found else 0.0,
        "source_file": reranked_results[0].get("source_file") if reranked_results else None,
        "db_id": None,
        "action_type": action_type,
        "action_url": action_url,
        "action_text": action_text,
        "sources": built_context.get("sources", []),
        "processed_query": processed,
        "reranked_results": reranked_results,
        "draft_response": llm_res.get("draft_response", raw_reply),
        "grounding_status": grounding_status,
        "grounding": grounding_info
    }


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 7: GROUNDING & HALLUCINATION CHECK WRAPPER
# ═════════════════════════════════════════════════════════════════════════════

def validate_response_grounding(
    draft_text: str,
    context_text: str,
    user_query: str = ""
) -> Dict[str, Any]:
    """
    Phase 7 Entrypoint:
    Validates draft response against verified context for factual accuracy.
    Checks:
    - Fees / Pricing amounts
    - Phone numbers & email contacts
    - Addresses & locations
    - Founder & leadership details
    - Durations & timelines
    - Suspicious policies & guarantees
    - Semantic context overlap
    """
    return check_grounding(
        draft_text=draft_text,
        context_text=context_text,
        user_query=user_query
    )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 8: FINAL RESPONSE FORMATTER & COMPLETE PIPELINE INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════

class FinalResponseFormatter:
    """
    Phase 8 Final Response Formatter:
    Post-processes the grounded LLM draft response into a clean, natural,
    production-ready message for the React Chat UI.

    Guarantees:
    - Strips raw HTML tags (<br>, <p>, <b>, </div>, etc.) and converts to clean Markdown
    - Transforms raw Markdown table syntax (| Col 1 | Col 2 |) into readable bullet points
    - Scrubs internal tool/RAG debug artifacts (Document [1], Tool [1], internal function names)
    - Normalizes headings and whitespace
    - Preserves contact details, markdown links, bullet lists, and action buttons
    """

    @staticmethod
    def clean_html(text: str) -> str:
        """Converts inline HTML tags to equivalent Markdown and strips remaining tags."""
        if not text:
            return ""
        # Common HTML conversions
        t = re.sub(r'<br\s*/?>|</br>', '\n', text, flags=re.IGNORECASE)
        t = re.sub(r'<b>(.*?)</b>|<strong>(.*?)</strong>', r'**\1\2**', t, flags=re.IGNORECASE)
        t = re.sub(r'<i>(.*?)</i>|<em>(.*?)</em>', r'*\1\2*', t, flags=re.IGNORECASE)
        t = re.sub(r'<code>(.*?)</code>', r'`\1`', t, flags=re.IGNORECASE)
        t = re.sub(r'<p>(.*?)</p>', r'\1\n\n', t, flags=re.IGNORECASE | re.DOTALL)
        # Strip any other remaining tags
        t = re.sub(r'<[^>]+>', '', t)
        return t

    @staticmethod
    def clean_tables(text: str) -> str:
        """
        Converts raw markdown table syntax (| Col 1 | Col 2 |) into clean bullet lists.
        """
        if not text or "|" not in text:
            return text

        lines = text.splitlines()
        new_lines: List[str] = []
        table_rows: List[str] = []

        def flush_table_rows(rows: List[str]) -> List[str]:
            if not rows:
                return []
            parsed_rows = []
            for r in rows:
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                # Skip separator lines like |---|---|
                if any(re.match(r'^:?-+:?$', c) for c in cells):
                    continue
                parsed_rows.append(cells)

            if not parsed_rows:
                return []

            out = []
            headers = parsed_rows[0]
            if len(parsed_rows) == 1:
                out.append("- " + " | ".join(headers))
            else:
                for row in parsed_rows[1:]:
                    row_parts = []
                    for h_idx, val in enumerate(row):
                        h_name = headers[h_idx] if h_idx < len(headers) else f"Field {h_idx+1}"
                        if val:
                            row_parts.append(f"**{h_name}:** {val}")
                    if row_parts:
                        out.append("- " + " • ".join(row_parts))
            return out

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                table_rows.append(stripped)
            else:
                if table_rows:
                    new_lines.extend(flush_table_rows(table_rows))
                    table_rows = []
                new_lines.append(line)

        if table_rows:
            new_lines.extend(flush_table_rows(table_rows))

        return "\n".join(new_lines)

    @staticmethod
    def scrub_internal_artifacts(text: str) -> str:
        """
        Removes any internal RAG or tool prompt artifacts if leaked into draft output.
        """
        if not text:
            return ""

        scrub_patterns = [
            r"###\s*\[\d+\]\s*[A-Z\s&]+\b",
            r"####\s*Document\s*\[\d+\]:\s*.*?\n",
            r"####\s*Tool\s*\[\d+\]\s*\[.*?\]:\s*.*?\n",
            r"\b(get_product_tool|get_pricing_tool|get_faq_tool|execute_kb_tool|query_knowledge_base)\b",
            r"Verified Context:\s*",
            r"\[\.\.\.\s*Context truncated for token budget\s*\.\.\.\]",
            r"【\d+†.*?】",
            r"【.*?】"
        ]

        cleaned = text
        for pat in scrub_patterns:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

        # Normalize multiple consecutive empty lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        return cleaned

    @classmethod
    def format(cls, raw_reply: str, default_fallback: str = DEFAULT_FALLBACK_MESSAGE) -> str:
        """
        Master Phase 8 Response Formatter.
        """
        if not raw_reply or not raw_reply.strip():
            return default_fallback

        if default_fallback.lower() in raw_reply.lower():
            return default_fallback

        text = cls.clean_html(raw_reply)
        text = cls.clean_tables(text)
        text = cls.scrub_internal_artifacts(text)

        if not text or len(text.strip()) < 5:
            return default_fallback

        return text.strip()


def format_final_response(raw_reply: str) -> str:
    """Convenience functional entrypoint for Phase 8 Final Response Formatter."""
    return FinalResponseFormatter.format(raw_reply)


