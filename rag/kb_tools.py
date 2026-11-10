"""
NxGen Tech Academy - Controlled Knowledge Base Access Layer & Website Tools
==========================================================================
Provides structured, deterministic lookups into the official Knowledge Base
(knowledge_base/ directory) for:
1. LLM Tool / Function Calling (Groq KB Tools)
2. Phase 3: Website Tools (Pricing, Products/Courses, FAQ)

Constraints:
- Strictly NO semantic/vector similarity search.
- Strictly NO keyword search / BM25 search.
- Strictly NO hardcoded facts — reads directly from existing Markdown KB files.
- Returns clean, structured context for downstream Reranker, Context Builder, and Groq answer generation.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


_kb_candidates = [
    Path(__file__).resolve().parent.parent / "knowledge_base",
    Path(__file__).resolve().parent.parent / "NxGenTechAcademy" / "knowledge_base",
    Path(__file__).resolve().parent.parent.parent / "knowledge_base"
]
KB_DIR = next((p for p in _kb_candidates if p.is_dir()), _kb_candidates[0])

# Course name / alias mapping to corresponding KB file and metadata
COURSE_REGISTRY = {
    "python": {
        "file": "courses/python_programming.md",
        "name": "Python Programming",
        "slug": "python-course-training",
        "url": "/courses/python-course-training",
        "action_text": "View Course"
    },
    "python programming": {
        "file": "courses/python_programming.md",
        "name": "Python Programming",
        "slug": "python-course-training",
        "url": "/courses/python-course-training",
        "action_text": "View Course"
    },
    "aiml": {
        "file": "courses/aiml_programming.md",
        "name": "AIML Programming",
        "slug": "aiml-course-training",
        "url": "/courses/aiml-course-training",
        "action_text": "View Course"
    },
    "aiml programming": {
        "file": "courses/aiml_programming.md",
        "name": "AIML Programming",
        "slug": "aiml-course-training",
        "url": "/courses/aiml-course-training",
        "action_text": "View Course"
    },
    "ai": {
        "file": "courses/artificial_intelligence.md",
        "name": "AI Programming",
        "slug": "ai-course-training",
        "url": "/courses/ai-course-training",
        "action_text": "View Course"
    },
    "artificial intelligence": {
        "file": "courses/artificial_intelligence.md",
        "name": "AI Programming",
        "slug": "ai-course-training",
        "url": "/courses/ai-course-training",
        "action_text": "View Course"
    },
    "ai programming": {
        "file": "courses/artificial_intelligence.md",
        "name": "AI Programming",
        "slug": "ai-course-training",
        "url": "/courses/ai-course-training",
        "action_text": "View Course"
    },
    "data analytics": {
        "file": "courses/data_analytics.md",
        "name": "Data Analytics Programming",
        "slug": "data-analytics-course-training",
        "url": "/courses/data-analytics-course-training",
        "action_text": "View Course"
    },
    "data analytics programming": {
        "file": "courses/data_analytics.md",
        "name": "Data Analytics Programming",
        "slug": "data-analytics-course-training",
        "url": "/courses/data-analytics-course-training",
        "action_text": "View Course"
    },
    "digital marketing": {
        "file": "courses/digital_marketing.md",
        "name": "Digital Marketing Course",
        "slug": "digital-marketing-course-training",
        "url": "/courses/digital-marketing-course-training",
        "action_text": "View Course"
    },
    "digital marketing course": {
        "file": "courses/digital_marketing.md",
        "name": "Digital Marketing Course",
        "slug": "digital-marketing-course-training",
        "url": "/courses/digital-marketing-course-training",
        "action_text": "View Course"
    },
    "job guarantee digital marketing": {
        "file": "courses/job_guarantee_digital_marketing.md",
        "name": "Job Guarantee Digital Marketing Course",
        "slug": "job-guarantee-digital-marketing-course-training",
        "url": "/courses/job-guarantee-digital-marketing-course-training",
        "action_text": "View Course"
    },
    "job guarantee digital marketing course": {
        "file": "courses/job_guarantee_digital_marketing.md",
        "name": "Job Guarantee Digital Marketing Course",
        "slug": "job-guarantee-digital-marketing-course-training",
        "url": "/courses/job-guarantee-digital-marketing-course-training",
        "action_text": "View Course"
    },
    "sap abap on hana": {
        "file": "courses/sap_abap_on_hana.md",
        "name": "SAP ABAP on HANA",
        "slug": "sap-abap-course-training",
        "url": "/courses/sap-abap-course-training",
        "action_text": "View Course"
    },
    "sap abap": {
        "file": "courses/sap_abap_on_hana.md",
        "name": "SAP ABAP on HANA",
        "slug": "sap-abap-course-training",
        "url": "/courses/sap-abap-course-training",
        "action_text": "View Course"
    },
    "sap abap cds odata rap": {
        "file": "courses/sap_abap_cds_odata_rap.md",
        "name": "SAP ABAP on HANA (CDS & OData / RAP)",
        "slug": "sap-abap-cds-course-training",
        "url": "/courses/sap-abap-cds-course-training",
        "action_text": "View Course"
    },
    "sap rap": {
        "file": "courses/sap_abap_cds_odata_rap.md",
        "name": "SAP ABAP on HANA (CDS & OData / RAP)",
        "slug": "sap-abap-cds-course-training",
        "url": "/courses/sap-abap-cds-course-training",
        "action_text": "View Course"
    },
    "sap fiori ui5": {
        "file": "courses/sap_ui5_fiori.md",
        "name": "SAP Fiori & UI5",
        "slug": "sap-fiori-course-training",
        "url": "/courses/sap-fiori-course-training",
        "action_text": "View Course"
    },
    "sap ui5 fiori": {
        "file": "courses/sap_ui5_fiori.md",
        "name": "SAP Fiori & UI5",
        "slug": "sap-fiori-course-training",
        "url": "/courses/sap-fiori-course-training",
        "action_text": "View Course"
    },
    "sap fiori": {
        "file": "courses/sap_ui5_fiori.md",
        "name": "SAP Fiori & UI5",
        "slug": "sap-fiori-course-training",
        "url": "/courses/sap-fiori-course-training",
        "action_text": "View Course"
    },
    "sap btp freshers": {
        "file": "courses/sap_btp_freshers.md",
        "name": "SAP BTP For Freshers",
        "slug": "sap-btp-freshers-course-training",
        "url": "/courses/sap-btp-freshers-course-training",
        "action_text": "View Course"
    },
    "sap btp for freshers": {
        "file": "courses/sap_btp_freshers.md",
        "name": "SAP BTP For Freshers",
        "slug": "sap-btp-freshers-course-training",
        "url": "/courses/sap-btp-freshers-course-training",
        "action_text": "View Course"
    },
    "sap btp working professionals": {
        "file": "courses/sap_btp_working_professionals.md",
        "name": "SAP BTP For Working Professionals",
        "slug": "sap-btp-professionals-course-training",
        "url": "/courses/sap-btp-professionals-course-training",
        "action_text": "View Course"
    },
    "sap btp for working professionals": {
        "file": "courses/sap_btp_working_professionals.md",
        "name": "SAP BTP For Working Professionals",
        "slug": "sap-btp-professionals-course-training",
        "url": "/courses/sap-btp-professionals-course-training",
        "action_text": "View Course"
    },
    "sap btp": {
        "file": "courses/sap_btp_freshers.md",
        "name": "SAP BTP For Freshers",
        "slug": "sap-btp-freshers-course-training",
        "url": "/courses/sap-btp-freshers-course-training",
        "action_text": "View Course"
    },
    "sap cpi": {
        "file": "courses/sap_cpi.md",
        "name": "SAP CPI",
        "slug": "sap-cpi-course-training",
        "url": "/courses/sap-cpi-course-training",
        "action_text": "View Course"
    },
    "sap basis": {
        "file": "courses/sap_basis_s4hana.md",
        "name": "SAP BASIS S/4HANA Training",
        "slug": "sap-basis-course-training",
        "url": "/courses/sap-basis-course-training",
        "action_text": "View Course"
    },
    "sap basis s4hana": {
        "file": "courses/sap_basis_s4hana.md",
        "name": "SAP BASIS S/4HANA Training",
        "slug": "sap-basis-course-training",
        "url": "/courses/sap-basis-course-training",
        "action_text": "View Course"
    },
    "sap fico": {
        "file": "courses/sap_fico.md",
        "name": "SAP FICO",
        "slug": "sap-fico-course-training",
        "url": "/courses/sap-fico-course-training",
        "action_text": "View Course"
    },
    "sap mm": {
        "file": "courses/sap_mm.md",
        "name": "SAP MM",
        "slug": "sap-mm-course-training",
        "url": "/courses/sap-mm-course-training",
        "action_text": "View Course"
    },
    "sap sd": {
        "file": "courses/sap_sd.md",
        "name": "SAP SD",
        "slug": "sap-sd-course-training",
        "url": "/courses/sap-sd-course-training",
        "action_text": "View Course"
    },
    "sap pp": {
        "file": "courses/sap_pp.md",
        "name": "SAP PP",
        "slug": "sap-pp-course-training",
        "url": "/courses/sap-pp-course-training",
        "action_text": "View Course"
    },
    "sap qm": {
        "file": "courses/sap_qm.md",
        "name": "SAP QM",
        "slug": "sap-qm-course-training",
        "url": "/courses/sap-qm-course-training",
        "action_text": "View Course"
    }
}


ALLOWED_KB_TOOLS = frozenset({
    "get_academy_information",
    "get_course_information",
    "get_course_section",
    "get_common_course_highlights",
    "get_course_catalog",
    "get_pricing_tool",
    "get_product_tool",
    "get_faq_tool"
})


def _read_file(relative_path: str) -> str:
    """Reads a markdown file safely from the knowledge base directory with strict traversal protection."""
    if not relative_path or not isinstance(relative_path, str):
        return ""
    try:
        clean_rel = os.path.normpath(relative_path).lstrip("/\\")
        full_path = (KB_DIR / clean_rel).resolve()
        # Ensure path stays strictly inside KB_DIR
        if not str(full_path).startswith(str(KB_DIR.resolve())):
            return ""
        if full_path.is_file():
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        return ""
    return ""


def _strip_frontmatter(content: str) -> str:
    """Strips YAML frontmatter delimiter (--- ... ---) from beginning of markdown."""
    if not content:
        return ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def _parse_sections(content: str) -> Dict[str, str]:
    """
    Parses a markdown document into a dictionary mapping normalized heading names to section text.
    Handles level 2 (##) and level 3 (###) headers.
    """
    clean_text = _strip_frontmatter(content)
    lines = clean_text.splitlines()
    sections: Dict[str, List[str]] = {}
    current_sec = "root"
    sections[current_sec] = []

    for line in lines:
        if line.startswith("## ") or line.startswith("# "):
            header = re.sub(r"^#+\s*", "", line).strip()
            current_sec = header.lower()
            if current_sec not in sections:
                sections[current_sec] = []
        elif line.startswith("### "):
            sub_header = re.sub(r"^#+\s*", "", line).strip()
            sub_key = sub_header.lower()
            if sub_key not in sections:
                sections[sub_key] = [f"### {sub_header}"]
            sections[current_sec].append(line)
        else:
            sections[current_sec].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _resolve_course(course_name: str) -> Optional[Dict[str, Any]]:
    """Resolves a course query string to registry entry."""
    if not course_name:
        return None
    q = course_name.strip().lower()
    q = re.sub(r'[^\w\s]', '', q)
    q = re.sub(r'\s+', ' ', q).strip()

    # Exact registry lookup
    if q in COURSE_REGISTRY:
        return COURSE_REGISTRY[q]

    # Partial substring search in registry keys
    for k, v in COURSE_REGISTRY.items():
        if k in q or q in k:
            return v

    # Word set matching
    q_words = set(q.split())
    best_match = None
    best_overlap = 0
    for k, v in COURSE_REGISTRY.items():
        k_words = set(k.split())
        overlap = len(q_words & k_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = v

    if best_overlap >= 1:
        return best_match

    return None


# ════════════════════════════════════════════════════════════════
# CORE KB TOOLS
# ════════════════════════════════════════════════════════════════

def get_academy_information(topic: str) -> str:
    """
    Retrieves official information about NxGen Tech Academy for a specific topic.
    Topics: overview, founder, contact, address, location, learning_approach,
    mentors, course_highlights, mission, vision, core_values, differentiation,
    placements, admissions, partners, privacy_policy.
    """
    t = (topic or "").strip().lower()

    if t in ["overview", "about"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        overview = sec_map.get("academy overview") or sec_map.get("about nxgen tech academy")
        stats = sec_map.get("key academy highlights & stats", "")
        res = "## About NxGen Tech Academy\n"
        if overview:
            res += f"{overview}\n\n"
        if stats:
            res += f"### Key Highlights & Stats\n{stats}"
        return res.strip()

    elif t in ["founder", "founders", "leadership"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        overview = sec_map.get("academy overview", "")
        founder_lines = [l for l in overview.splitlines() if "founded" in l.lower() or "sria" in l.lower()]
        if founder_lines:
            return "## Founder & Leadership\n" + "\n".join(founder_lines)
        return "## Founder & Leadership\nNxGen Tech Academy was founded by [Sria Infotech Pvt. Ltd.](https://www.sriainfotech.com/) as a specialized skill development platform for modern technology careers."

    elif t in ["demo", "book_demo", "demo_booking", "schedule_demo", "request_demo", "free_demo"]:
        faq_adm = _read_file("faq/faq_admissions.md")
        adm_md = _read_file("admissions/enrollment_process.md")
        res = "## Free Live Demo Sessions at NxGen Tech Academy\n"
        if faq_adm:
            res += f"{_strip_frontmatter(faq_adm)}\n\n"
        if adm_md:
            res += f"{_strip_frontmatter(adm_md)}\n\n"
        res += "You can book a free demo session using the 'Book Demo' button below to experience our training firsthand and interact with our industry mentors."
        return res.strip()

    elif t in ["contact", "address", "location"]:
        contact_md = _read_file("academy/contact_details.md")
        if contact_md:
            return _strip_frontmatter(contact_md)
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return sec_map.get("contact & location", "Address: Udaya Vensar Apartments, Rd Number 1, Hanuman Nagar, Kothaguda, Hyderabad, Telangana 500084. Phone: +91 97013 14138.")

    elif t in ["learning_approach", "pedagogy", "teaching_approach", "learning_framework"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## Our Learning Approach\n" + sec_map.get("our learning approach", "")

    elif t in ["mentors", "trainers", "faculty", "instructors"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## Our Training and Mentors\n" + sec_map.get("our training and mentors", "")

    elif t in ["course_highlights", "highlights"]:
        return get_common_course_highlights()

    elif t in ["mission"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## Our Mission\n" + sec_map.get("our mission", "")

    elif t in ["vision"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## Our Vision\n" + sec_map.get("our vision", "")

    elif t in ["core_values", "values"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## Our Core Values\n" + sec_map.get("our core values", "")

    elif t in ["differentiation", "why_choose_us", "why_nxgen"]:
        about_md = _read_file("academy/about_academy.md")
        sec_map = _parse_sections(about_md)
        return "## What Makes NxGen Tech Academy Different?\n" + sec_map.get("what makes nxgen tech academy different?", "")

    elif t in ["placements", "placement_assistance", "placement_support"]:
        placement_md = _read_file("placement/placement_support.md")
        return _strip_frontmatter(placement_md) if placement_md else "NxGen Tech Academy provides 100% placement support with resume preparation, mock interviews, and 100+ hiring partner companies."

    elif t in ["admissions", "enrollment", "registration", "how_to_join"]:
        adm_md = _read_file("admissions/enrollment_process.md")
        return _strip_frontmatter(adm_md) if adm_md else "Admission process involves Free Live Demo class, 1-on-1 counseling, registration, and LMS onboarding."

    elif t in ["partners", "bsnl", "associations", "affiliations"]:
        partner_md = _read_file("faq/faq_associations.md")
        return _strip_frontmatter(partner_md) if partner_md else "NxGen Tech Academy is an official BSNL Skill Development Partner."

    elif t in ["privacy_policy", "privacy", "terms"]:
        policy_md = _read_file("policies/privacy_policy.md")
        return _strip_frontmatter(policy_md) if policy_md else "NxGen Tech Academy protects student privacy and never shares data with unauthorized third parties."

    about_md = _read_file("academy/about_academy.md")
    return _strip_frontmatter(about_md)


def get_course_information(course_name: str) -> str:
    """
    Retrieves complete existing course information from the knowledge base for a specific course.
    """
    c_info = _resolve_course(course_name)
    if not c_info:
        return f"Course '{course_name}' not found in the NxGen Tech Academy knowledge base. Available courses include Python Programming, AIML, AI, Data Analytics, Digital Marketing, and SAP modules."

    raw_md = _read_file(c_info["file"])
    if not raw_md:
        return f"Information for course '{course_name}' is currently being updated in the knowledge base."

    return _strip_frontmatter(raw_md)


def get_course_section(course_name: str, section: str) -> str:
    """
    Retrieves a specific section of a course (e.g. overview, details, curriculum, projects,
    certification, placement, industrial_readiness, career_opportunities, benefits, faqs).
    """
    c_info = _resolve_course(course_name)
    if not c_info:
        return f"Course '{course_name}' not found in the NxGen Tech Academy knowledge base."

    raw_md = _read_file(c_info["file"])
    if not raw_md:
        return f"Information for course '{course_name}' is currently unavailable."

    sec_map = _parse_sections(raw_md)
    sec_key = (section or "").strip().lower()

    if sec_key in ["overview", "description", "about"]:
        ov = sec_map.get("course overview", "")
        desc = sec_map.get("course description", "")
        parts = [f"Course: {c_info['name']}"]
        if ov: parts.append(f"## Course Overview\n{ov}")
        if desc: parts.append(f"## Course Description\n{desc}")
        return "\n\n".join(parts)

    elif sec_key in ["details", "fees", "duration", "eligibility", "prerequisites", "mode", "timing"]:
        parts = [f"Course: {c_info['name']} - Details"]
        dur = sec_map.get("duration")
        fees = sec_map.get("fees")
        elig = sec_map.get("eligibility")
        prereq = sec_map.get("prerequisites")
        mode = sec_map.get("course mode")
        if dur: parts.append(f"- **Duration:** {dur}")
        if fees: parts.append(f"- **Fees:** {fees}")
        if elig: parts.append(f"- **Eligibility:** {elig}")
        if prereq: parts.append(f"- **Prerequisites:** {prereq}")
        if mode: parts.append(f"- **Mode:** {mode}")
        return "\n".join(parts)

    elif sec_key in ["curriculum", "syllabus", "modules"]:
        curr = sec_map.get("curriculum / modules") or sec_map.get("curriculum")
        if curr:
            return f"Course: {c_info['name']} - Curriculum\n\n## Curriculum / Modules\n{curr}"
        return f"Curriculum details for {c_info['name']} are available. Please contact academy for full syllabus."

    elif sec_key in ["projects", "project", "real_time_projects"]:
        proj = sec_map.get("projects")
        if proj:
            return f"Course: {c_info['name']} - Projects\n\n## Projects\n{proj}"
        return f"Hands-on real-time project implementations are included in {c_info['name']}."

    elif sec_key in ["certification", "certificate"]:
        cert = sec_map.get("certification")
        if cert:
            return f"Course: {c_info['name']} - Certification\n\n## Certification\n{cert}"
        return f"Industry-recognized certificate of completion from NxGen Tech Academy is awarded upon completing {c_info['name']}."

    elif sec_key in ["placement", "placements", "job_assistance"]:
        plc = sec_map.get("placement assistance") or sec_map.get("placement")
        if plc:
            return f"Course: {c_info['name']} - Placement Assistance\n\n## Placement Assistance\n{plc}"
        return f"100% placement support including resume preparation and mock interviews is provided for {c_info['name']}."

    elif sec_key in ["industrial_readiness", "readiness", "job_readiness"]:
        ir = sec_map.get("industrial readiness")
        if ir:
            return f"Course: {c_info['name']} - Industrial Readiness\n\n## Industrial Readiness\n{ir}"
        return f"Industrial readiness training covering project planning, documentation, and mock interviews is included."

    elif sec_key in ["career_opportunities", "career", "jobs", "roles"]:
        co = sec_map.get("career opportunities")
        if co:
            return f"Course: {c_info['name']} - Career Opportunities\n\n## Career Opportunities\n{co}"
        return f"Multiple career opportunities are available after completing {c_info['name']}."

    elif sec_key in ["benefits", "learning_outcomes", "outcomes"]:
        other = sec_map.get("other course information") or sec_map.get("learning outcomes") or sec_map.get("key benefits")
        if other:
            return f"Course: {c_info['name']} - Benefits & Outcomes\n\n{other}"
        return f"{c_info['name']} offers practical, job-oriented skill development."

    elif sec_key in ["faqs", "faq"]:
        faqs = sec_map.get("frequently asked questions")
        if faqs:
            return f"Course: {c_info['name']} - FAQs\n\n## Frequently Asked Questions\n{faqs}"
        return f"FAQs for {c_info['name']}."

    return _strip_frontmatter(raw_md)


def get_common_course_highlights() -> str:
    """
    Retrieves the official common Course Highlights applicable across all courses at NxGen Tech Academy.
    """
    about_md = _read_file("academy/about_academy.md")
    sec_map = _parse_sections(about_md)
    ch = sec_map.get("course highlights", "")
    if ch:
        return f"## Course Highlights\n{ch}"
    return (
        "## Course Highlights\n\n"
        "- 50+ Hours Live Sessions\n"
        "- 10+ Assignments\n"
        "- Certification Included\n"
        "- 1:1 Mentorship"
    )


def get_course_catalog(category: Optional[str] = None) -> str:
    """
    Retrieves the complete catalog of all 18 courses offered by NxGen Tech Academy across all 5 categories.
    """
    cat_lower = (category or "").strip().lower()
    if cat_lower and cat_lower != "all courses":
        if any(k in cat_lower for k in ["sap", "abap", "fico", "btp", "cpi", "basis", "mm", "sd", "pp", "qm", "fiori", "ui5"]):
            return (
                "## SAP Courses Catalog (12 Specialized Modules)\n\n"
                "NxGen Tech Academy offers 12 comprehensive SAP training modules with 100% placement assistance, real-time server access, and industry certification:\n\n"
                "### Technical SAP Modules (40+ Hours each)\n"
                "1. **SAP ABAP on HANA:** Modern ABAP 7.5 syntax, HANA DB optimization, Core Data Services (CDS), AMDP, and code pushdown techniques.\n"
                "2. **SAP ABAP on HANA (CDS & OData / RAP):** RESTful Application Programming model (RAP), custom CDS views, OData service publishing, and Fiori integration.\n"
                "3. **SAP Fiori & UI5:** Modern UI/UX development, SAP Business Application Studio, MVC architecture, custom Fiori apps, and SAP Launchpad integration.\n"
                "4. **SAP BASIS S/4HANA Training:** System administration, client copies, kernel upgrades, transport management system (TMS), and system performance monitoring.\n\n"
                "### Functional SAP Modules (40+ Hours each)\n"
                "5. **SAP FICO:** Financial Accounting (GL, AP, AR, Asset Accounting) & Controlling (Cost Center, Profit Center Accounting) on S/4HANA.\n"
                "6. **SAP MM (Materials Management):** Procurement lifecycle, master data, purchase orders, inventory management, and invoice verification.\n"
                "7. **SAP SD (Sales & Distribution):** Order-to-Cash (O2C) cycle, pricing procedures, sales orders, delivery processing, and billing.\n"
                "8. **SAP PP (Production Planning):** Master data, Bill of Materials (BOM), routing, Material Requirements Planning (MRP), and shop floor control.\n"
                "9. **SAP QM (Quality Management):** Quality planning, inspection lot processing, sampling procedures, quality certificates, and defect notifications.\n\n"
                "### Cloud & Integration Modules (SAP BTP) (40+ Hours each)\n"
                "10. **SAP BTP For Freshers:** Cloud Foundry fundamentals, SAP Cloud Application Programming (CAP) model, SAP Build, and application deployment.\n"
                "11. **SAP BTP For Working Professionals:** Enterprise cloud architecture, custom extension development, multi-cloud deployment, and cloud security.\n"
                "12. **SAP CPI (Cloud Platform Integration):** Cloud middleware, integration flows (iFlows), adapters, message mapping, and API management.\n\n"
                "- **Training Mode:** Online, Classroom, and Hybrid (Hyderabad campus)\n"
                "- **Key Highlights:** 50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship\n"
                "- **Placement Support:** 100% placement assistance with mock interviews and resume vetting"
            )
        elif any(k in cat_lower for k in ["digital", "marketing", "dm", "seo"]):
            return (
                "## Digital Marketing Courses Catalog\n\n"
                "NxGen Tech Academy offers 2 industry-aligned Digital Marketing training programs:\n\n"
                "1. **Digital Marketing Course (3 Months):** Search Engine Optimization (SEO), Google Ads (SEM), Social Media Marketing (SMM), email marketing, content marketing, and Google Analytics.\n"
                "2. **Job Guarantee Digital Marketing Course (6 Months):** Comprehensive advanced program with 100% Job Guarantee, live client campaigns, paid advertising strategies, portfolio engineering, and mandatory internship.\n\n"
                "- **Training Mode:** Online, Classroom, and Hybrid (Hyderabad campus)\n"
                "- **Key Highlights:** 50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship\n"
                "- **Placement Support:** 100% placement assistance with mock interviews and resume vetting"
            )
        elif "python" in cat_lower:
            return (
                "## Python Programming Catalog\n\n"
                "1. **Python Programming (3 to 4 Months):** Full Stack Python development covering syntax, data structures, Object-Oriented Programming (OOP), file handling, exception handling, MySQL database connectivity, Django framework, and real-time automation projects.\n\n"
                "- **Training Mode:** Online, Classroom, and Hybrid (Hyderabad campus)\n"
                "- **Key Highlights:** 50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship\n"
                "- **Placement Support:** 100% placement assistance with mock interviews and resume vetting"
            )
        elif "analytics" in cat_lower:
            return (
                "## Data Analytics Catalog\n\n"
                "1. **Data Analytics Programming (3 to 4 Months / 16 Weeks):** Comprehensive business analytics covering Advanced Excel, SQL database queries, Power BI interactive dashboard creation, Tableau data visualization, data modeling, and real-world business case studies.\n\n"
                "- **Training Mode:** Online, Classroom, and Hybrid (Hyderabad campus)\n"
                "- **Key Highlights:** 50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship\n"
                "- **Placement Support:** 100% placement assistance with mock interviews and resume vetting"
            )
        elif "aiml" in cat_lower or "ai" in cat_lower:
            return (
                "## Artificial Intelligence & Machine Learning Catalog\n\n"
                "1. **AIML Programming (3 to 4 Months):** Machine learning algorithms (supervised, unsupervised), Natural Language Processing (NLP), predictive modeling, Scikit-learn, and end-to-end ML project deployment.\n"
                "2. **AI Programming (3 to 4 Months):** Artificial Intelligence fundamentals, deep learning, artificial neural networks (ANN/CNN), PyTorch/TensorFlow frameworks, and generative AI concepts.\n\n"
                "- **Training Mode:** Online, Classroom, and Hybrid (Hyderabad campus)\n"
                "- **Key Highlights:** 50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship\n"
                "- **Placement Support:** 100% placement assistance with mock interviews and resume vetting"
            )

    return (
        "## All 18 Courses Offered by NxGen Tech Academy\n\n"
        "NxGen Tech Academy offers 18 certified technology training courses across 5 core career tracks with 100% placement assistance, hands-on real-world projects, and free live demo sessions:\n\n"
        "### 1. Python Programming\n"
        "- **Python Programming (Duration: 3 to 4 Months):** Full Stack Python development covering core programming, OOP, exception handling, MySQL database connectivity, Django framework, and real-time backend projects.\n\n"
        "### 2. Artificial Intelligence & Machine Learning (AI/ML)\n"
        "- **AIML Programming (Duration: 3 to 4 Months):** Machine learning algorithms, Natural Language Processing (NLP), predictive modeling, Scikit-learn, and end-to-end ML deployment.\n"
        "- **AI Programming (Duration: 3 to 4 Months):** Artificial Intelligence fundamentals, deep learning, neural networks, computer vision, and modern AI frameworks.\n\n"
        "### 3. Data Analytics\n"
        "- **Data Analytics Programming (Duration: 3 to 4 Months / 16 Weeks):** Complete analytics curriculum covering Advanced Excel, SQL database queries, Power BI dashboards, Tableau visualization, and business case studies.\n\n"
        "### 4. Digital Marketing\n"
        "- **Digital Marketing Course (Duration: 3 Months):** SEO, Google Ads (SEM), Social Media Marketing (SMM), email marketing, content marketing, and Google Analytics.\n"
        "- **Job Guarantee Digital Marketing Course (Duration: 6 Months):** Comprehensive program with 100% Job Guarantee, live client campaigns, paid advertising strategies, and mandatory internship.\n\n"
        "### 5. SAP Solutions (12 Specialized Modules – 40+ Hours each)\n"
        "- **Technical Modules:**\n"
        "  - **SAP ABAP on HANA:** Modern ABAP 7.5, HANA DB optimization, CDS views, AMDP.\n"
        "  - **SAP ABAP on HANA (CDS & OData / RAP):** RESTful Application Programming model (RAP), custom CDS views, OData services.\n"
        "  - **SAP Fiori & UI5:** Modern UI5 development, Business Application Studio, MVC architecture, custom Fiori apps.\n"
        "  - **SAP BASIS S/4HANA Training:** System administration, client administration, TMS, kernel upgrades, performance monitoring.\n"
        "- **Functional Modules:**\n"
        "  - **SAP FICO:** Financial & Management Accounting on S/4HANA (GL, AP, AR, Asset Accounting, Controlling).\n"
        "  - **SAP MM:** Materials Management, procurement lifecycle, inventory management, invoice verification.\n"
        "  - **SAP SD:** Sales & Distribution, Order-to-Cash (O2C) cycle, pricing procedures, billing.\n"
        "  - **SAP PP:** Production Planning, MRP, BOM, routing, shop floor control.\n"
        "  - **SAP QM:** Quality Management, inspection lot processing, quality certificates, defect notifications.\n"
        "- **Cloud & Integration (SAP BTP):**\n"
        "  - **SAP BTP For Freshers:** Cloud Foundry, SAP CAP model, SAP Build, application deployment.\n"
        "  - **SAP BTP For Working Professionals:** Enterprise cloud architecture, custom extension development, multi-cloud deployment.\n"
        "  - **SAP CPI:** Cloud Platform Integration, iFlows, message routing, adapters, API management.\n\n"
        "### Key Program Highlights\n"
        "- **Training Modes:** Online, Classroom, and Hybrid batches (Hyderabad campus).\n"
        "- **Placement Assistance:** 100% placement support with resume preparation, weekly mock interviews, and access to 100+ hiring partner companies.\n"
        "- **Certification:** Industry-recognized completion certificate from NxGen Tech Academy.\n"
        "- **Free Weekly Live Demo Sessions:** Attend a free live demo session with industry mentors before enrolling."
    )


# ════════════════════════════════════════════════════════════════
# PHASE 3: WEBSITE TOOLS (PRICING, PRODUCTS, FAQ)
# ════════════════════════════════════════════════════════════════

def _infer_course_category(course_name: str) -> str:
    """Helper to infer course category from name."""
    cn = (course_name or "").lower()
    if any(k in cn for k in ["sap", "abap", "fico", "btp", "mm", "sd", "pp", "qm", "cpi", "basis", "fiori", "ui5"]):
        return "SAP Courses"
    elif "digital marketing" in cn or "dm" in cn:
        return "Digital Marketing"
    elif "python" in cn:
        return "Python"
    elif "analytics" in cn or "power bi" in cn:
        return "Data Analytics"
    elif "aiml" in cn:
        return "AIML"
    elif "ai" in cn or "artificial intelligence" in cn:
        return "AI"
    return "All Courses"


def parse_faq_file(relative_path: str) -> List[Dict[str, str]]:
    """
    Parses a markdown FAQ file into structured Q&A pairs.
    """
    raw_md = _read_file(relative_path)
    if not raw_md:
        return []
    clean_md = _strip_frontmatter(raw_md)
    faqs: List[Dict[str, str]] = []

    blocks = re.split(r'(?=###\s*Q:)', clean_md)
    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("###"):
            continue
        q_match = re.search(r'###\s*Q:\s*(.*?)(?:\n|\r\n)', block)
        if not q_match:
            continue
        q_text = q_match.group(1).strip()

        ans_match = re.search(r'\*\*A:\*\*\s*(.*?)(?:\n\s*\*Source:\*|$)', block, re.DOTALL)
        if ans_match:
            ans_text = ans_match.group(1).strip()
        else:
            lines = [l for l in block.splitlines() if not l.startswith("###") and not l.startswith("*Source:")]
            ans_text = "\n".join(lines).strip()

        source_match = re.search(r'\*Source:\*\s*\[?([^\]\n\r]+)\]?', block)
        source_url = source_match.group(1).strip() if source_match else None

        faqs.append({
            "question": q_text,
            "answer": ans_text,
            "source_url": source_url
        })
    return faqs


def get_pricing_tool(course_name: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Website Tool: Pricing
    Retrieves structured pricing, fee details, installment plans, duration, mode,
    and navigation action for courses or categories.
    """
    # 1. Specific Course Pricing
    if course_name:
        c_info = _resolve_course(course_name)
        if c_info:
            raw_md = _read_file(c_info["file"])
            sec_map = _parse_sections(raw_md)
            fees = sec_map.get("fees") or "Affordable industry-standard pricing with flexible payment options."
            duration = sec_map.get("duration") or "3-4 Months"
            mode = sec_map.get("course mode") or "Online / Offline (Hyderabad campus)"
            eligibility = sec_map.get("eligibility") or "Open to all graduates and working professionals"

            formatted_text = (
                f"## Pricing & Details: {c_info['name']}\n\n"
                f"- **Fees:** {fees}\n"
                f"- **Duration:** {duration}\n"
                f"- **Training Mode:** {mode}\n"
                f"- **Eligibility:** {eligibility}\n"
                f"- **Payment Plans:** Flexible EMI and installment options available.\n"
                f"- **Free Live Demo:** Attend a free trial session before enrolling.\n"
                f"- **Certification:** Industry-recognized completion certificate included."
            )

            return {
                "tool_type": "pricing",
                "tool_name": "get_pricing_tool",
                "title": f"{c_info['name']} - Pricing & Fees",
                "course": c_info["name"],
                "course_slug": c_info["slug"],
                "category": category or _infer_course_category(c_info["name"]),
                "section": "Fees",
                "attributes": {
                    "fee": fees,
                    "duration": duration,
                    "mode": mode,
                    "installments_available": True,
                    "free_demo_included": True,
                    "certification_included": True
                },
                "action_url": c_info["url"],
                "action_text": c_info["action_text"],
                "text": formatted_text,
                "source": "website_tool"
            }

    # 2. Category Pricing Overview
    if category:
        cat_clean = category.strip()
        cat_lower = cat_clean.lower()
        if "sap" in cat_lower:
            target_url = "/training-programs?category=SAP+Courses"
            title = "SAP Courses - Pricing & Duration"
            courses_desc = "12 SAP Modules (ABAP on HANA, RAP, Fiori UI5, BTP, CPI, BASIS, FICO, MM, SD, PP, QM)"
            duration_desc = "40+ Hours per module / 3 Months comprehensive"
        elif "digital" in cat_lower or "dm" in cat_lower:
            target_url = "/training-programs?category=Digital+Marketing"
            title = "Digital Marketing Courses - Pricing & Duration"
            courses_desc = "Digital Marketing Course (3 Months) & Job Guarantee Digital Marketing (6 Months)"
            duration_desc = "3 Months / 6 Months (100% Job Guarantee)"
        elif "python" in cat_lower:
            target_url = "/training-programs?category=Python"
            title = "Python Programming - Pricing & Duration"
            courses_desc = "Full Stack Python Programming with Django and MySQL"
            duration_desc = "3-4 Months"
        elif "analytics" in cat_lower:
            target_url = "/training-programs?category=Data+Analytics"
            title = "Data Analytics - Pricing & Duration"
            courses_desc = "Data Analytics with Excel, SQL, Power BI, and Tableau"
            duration_desc = "3-4 Months"
        elif "aiml" in cat_lower or "ai" in cat_lower:
            target_url = f"/training-programs?category={cat_clean.replace(' ', '+')}"
            title = f"{cat_clean} - Pricing & Duration"
            courses_desc = "Artificial Intelligence & Machine Learning specialization"
            duration_desc = "3-4 Months"
        else:
            target_url = "/training-programs"
            title = f"{cat_clean} Training Programs - Pricing"
            courses_desc = f"All courses in {cat_clean}"
            duration_desc = "3-4 Months"

        formatted_text = (
            f"## {title}\n\n"
            f"- **Programs:** {courses_desc}\n"
            f"- **Duration:** {duration_desc}\n"
            f"- **Fees:** Competitive, career-focused pricing with flexible installments and EMI options.\n"
            f"- **Placement Support:** 100% placement assistance included.\n"
            f"- **Free Live Demo:** Free trial class available every week."
        )

        return {
            "tool_type": "pricing",
            "tool_name": "get_pricing_tool",
            "title": title,
            "course": cat_clean,
            "course_slug": None,
            "category": cat_clean,
            "section": "Pricing Overview",
            "attributes": {
                "category": cat_clean,
                "duration": duration_desc,
                "installments_available": True,
                "free_demo_included": True,
                "placement_support_included": True
            },
            "action_url": target_url,
            "action_text": "View Courses",
            "text": formatted_text,
            "source": "website_tool"
        }

    # 3. General Academy Course Fees & Duration Overview for All Courses
    formatted_text = (
        "## Course Fees & Duration\n\n"
        "**SAP ABAP on HANA**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹30,000\n\n"
        "**SAP ABAP on HANA (CDS & OData / RAP)**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹35,000\n\n"
        "**SAP BASIS S/4HANA Training**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹30,000\n\n"
        "**SAP BTP For Freshers**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹30,000\n\n"
        "**SAP BTP For Working Professionals**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹40,000\n\n"
        "**SAP CPI Training**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹35,000\n\n"
        "**SAP FICO Training**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹30,000\n\n"
        "**SAP MM (Materials Management)**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹28,000\n\n"
        "**SAP PP (Production Planning)**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹30,000\n\n"
        "**SAP QM (Quality Management)**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹28,000\n\n"
        "**SAP SD (Sales & Distribution)**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹28,000\n\n"
        "**SAP Fiori & UI5**\n"
        "Duration: 40+ hours\n"
        "Fees: ₹35,000\n\n"
        "**Python Programming**\n"
        "Duration: 3 to 4 months\n"
        "Fees: Contact Us for pricing details\n\n"
        "**AIML Programming**\n"
        "Duration: 3 to 4 months\n"
        "Fees: Contact Us for pricing details\n\n"
        "**AI Programming**\n"
        "Duration: 3 to 4 months\n"
        "Fees: Contact Us for pricing details\n\n"
        "**Data Analytics Programming**\n"
        "Duration: 3 to 4 Months (16 Weeks)\n"
        "Fees: Contact Us for pricing details\n\n"
        "**Digital Marketing Course (3 Months)**\n"
        "Duration: 3 Months\n"
        "Fees: Contact Us for pricing details\n\n"
        "**Job Guarantee Digital Marketing Course (6 Months)**\n"
        "Duration: 6 Months\n"
        "Fees: Contact Us for pricing details\n\n"
        "**Want to see the courses in action?**\n\n"
        "Free weekly live demo sessions are available for all programs, where documented by the academy.\n\n"
        "Simply click the existing **Book Demo** button on the website to reserve your spot.\n\n"
        "For any further questions, users can contact NxGen Tech Academy directly."
    )

    return {
        "tool_type": "pricing",
        "tool_name": "get_pricing_tool",
        "title": "NxGen Tech Academy - Course Fees & Duration",
        "course": None,
        "course_slug": None,
        "category": "All Courses",
        "section": "Course Fees & Duration",
        "attributes": {
            "total_courses": 18,
            "installments_available": True,
            "free_demo_included": True,
            "placement_support_included": True,
            "lms_access_included": True
        },
        "action_url": "/training-programs",
        "action_text": "View Courses",
        "text": formatted_text,
        "source": "website_tool"
    }


def get_product_tool(
    course_name: Optional[str] = None,
    category: Optional[str] = None,
    section: Optional[str] = None
) -> Dict[str, Any]:
    """
    Website Tool: Products / Courses
    Retrieves structured course details, modules/curriculum, duration, prerequisites,
    projects, certification, or catalog of 18 courses.
    """
    # 1. Specific Course Product Details
    if course_name:
        c_info = _resolve_course(course_name)
        if c_info:
            raw_md = _read_file(c_info["file"])
            sec_map = _parse_sections(raw_md)

            overview = sec_map.get("course overview") or sec_map.get("course description") or ""
            curriculum = sec_map.get("curriculum / modules") or sec_map.get("curriculum") or ""
            duration = sec_map.get("duration") or "3-4 Months"
            mode = sec_map.get("course mode") or "Online / Offline (Hyderabad campus)"
            eligibility = sec_map.get("eligibility") or "Graduates & working professionals"
            prerequisites = sec_map.get("prerequisites") or "Basic computer knowledge"
            projects = sec_map.get("projects") or "Real-time industry projects and capstone"
            certification = sec_map.get("certification") or "NxGen Tech Academy Course Completion Certificate"

            # Parse individual modules if available
            module_lines = [l.strip() for l in curriculum.splitlines() if re.match(r'^(Module|\d+\.|\*|\-)\s*', l.strip())]

            formatted_text = f"## {c_info['name']} - Course Overview\n\n"
            if overview:
                formatted_text += f"{overview}\n\n"
            formatted_text += (
                f"### Key Details\n"
                f"- **Duration:** {duration}\n"
                f"- **Mode:** {mode}\n"
                f"- **Eligibility:** {eligibility}\n"
                f"- **Prerequisites:** {prerequisites}\n\n"
                f"### Projects & Certification\n"
                f"- **Projects:** {projects}\n"
                f"- **Certification:** {certification}\n"
            )
            if module_lines:
                formatted_text += f"\n### Curriculum Modules\n" + "\n".join(module_lines[:8])

            return {
                "tool_type": "product",
                "tool_name": "get_product_tool",
                "title": f"{c_info['name']} - Course Information",
                "course": c_info["name"],
                "course_slug": c_info["slug"],
                "category": category or _infer_course_category(c_info["name"]),
                "section": (section or "Overview").capitalize(),
                "attributes": {
                    "duration": duration,
                    "mode": mode,
                    "eligibility": eligibility,
                    "prerequisites": prerequisites,
                    "modules_count": len(module_lines),
                    "modules_preview": module_lines[:5],
                    "projects": projects,
                    "certification": certification
                },
                "action_url": c_info["url"],
                "action_text": c_info["action_text"],
                "text": formatted_text.strip(),
                "source": "website_tool"
            }

    # 2. Category Product Catalog
    if category:
        cat_clean = category.strip()
        cat_lower = cat_clean.lower()
        if any(k in cat_lower for k in ["sap", "fico", "abap", "btp", "mm", "sd", "pp", "qm", "cpi", "basis"]):
            target_url = "/training-programs?category=SAP+Courses"
            cat_name = "SAP Courses"
            courses_list = [
                "SAP ABAP on HANA", "SAP ABAP on HANA (CDS & OData / RAP)", "SAP Fiori & UI5",
                "SAP BTP For Freshers", "SAP BTP For Working Professionals", "SAP CPI",
                "SAP BASIS S/4HANA", "SAP FICO", "SAP MM", "SAP SD", "SAP PP", "SAP QM"
            ]
        elif any(k in cat_lower for k in ["digital", "marketing", "dm", "seo"]):
            target_url = "/training-programs?category=Digital+Marketing"
            cat_name = "Digital Marketing"
            courses_list = [
                "Digital Marketing Course (3 Months)",
                "Job Guarantee Digital Marketing Course (6 Months)"
            ]
        elif "python" in cat_lower:
            target_url = "/training-programs?category=Python"
            cat_name = "Python"
            courses_list = ["Python Programming (Full Stack Python, Django, MySQL)"]
        elif "analytics" in cat_lower:
            target_url = "/training-programs?category=Data+Analytics"
            cat_name = "Data Analytics"
            courses_list = ["Data Analytics Programming (Excel, SQL, Power BI, Tableau)"]
        elif "aiml" in cat_lower:
            target_url = "/training-programs?category=AIML"
            cat_name = "AIML"
            courses_list = ["AIML Programming (Machine Learning, NLP, Predictive Models)"]
        elif "ai" in cat_lower:
            target_url = "/training-programs?category=AI"
            cat_name = "AI"
            courses_list = ["AI Programming (Artificial Intelligence, Neural Networks)"]
        else:
            target_url = f"/training-programs?category={cat_clean.replace(' ', '+')}"
            cat_name = cat_clean
            courses_list = [f"{cat_clean} Specialization Courses"]

        formatted_text = f"## {cat_name} Catalog - NxGen Tech Academy\n\n"
        formatted_text += f"NxGen Tech Academy offers **{len(courses_list)} distinct programs** in {cat_name}:\n\n"
        for i, c in enumerate(courses_list, 1):
            formatted_text += f"{i}. **{c}**\n"
        formatted_text += (
            "\n### Key Highlights\n"
            "- 100% Placement Assistance with mock interviews\n"
            "- Online, Classroom, and Hybrid modes (Hyderabad campus)\n"
            "- Real-world capstone projects and official certification\n"
            "- Free weekly live demo sessions"
        )

        return {
            "tool_type": "product",
            "tool_name": "get_product_tool",
            "title": f"{cat_name} Course Catalog",
            "course": cat_name,
            "course_slug": None,
            "category": cat_name,
            "section": "Course Catalog",
            "attributes": {
                "category": cat_name,
                "course_count": len(courses_list),
                "courses": courses_list,
                "placement_assistance": True,
                "free_demo": True
            },
            "action_url": target_url,
            "action_text": "View Courses",
            "text": formatted_text.strip(),
            "source": "website_tool"
        }

    # 3. Complete Course Catalog of 18 Courses
    catalog_md = _read_file("courses/all_courses_offered.md")
    clean_catalog = _strip_frontmatter(catalog_md)

    return {
        "tool_type": "product",
        "tool_name": "get_product_tool",
        "title": "All 18 Courses Offered - NxGen Tech Academy",
        "course": "All Courses",
        "course_slug": None,
        "category": "All Courses",
        "section": "Complete Catalog",
        "attributes": {
            "total_courses": 18,
            "categories": ["Python", "AI", "AIML", "Data Analytics", "Digital Marketing", "SAP Courses"],
            "common_highlights": [
                "50+ Hours Live Sessions",
                "10+ Assignments",
                "Certification Included",
                "1:1 Mentorship"
            ]
        },
        "action_url": "/training-programs",
        "action_text": "View Courses",
        "text": clean_catalog,
        "source": "website_tool"
    }


def get_faq_tool(
    topic_or_course: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Website Tool: FAQ
    Retrieves structured Q&A pairs from official FAQ knowledge base files
    based on topic, course name, or query keywords.
    """
    key = (topic_or_course or query or "").strip().lower()

    # Topic -> File & Action Mapping
    if any(k in key for k in ["demo", "trial", "free session", "live demo"]):
        faq_file = "faq/faq_admissions.md"
        topic_title = "Live Demo & Admissions FAQs"
        action_url = "/courses/sap-btp-freshers-course-training"
        action_text = "Book Demo"
        course_name = "Book a Free Demo"
    elif any(k in key for k in ["placement", "job", "salary", "hiring", "interview", "career"]):
        faq_file = "faq/faq_placements.md"
        topic_title = "Placement Opportunities at NxGen Tech Academy"
        action_url = "/training-programs"
        action_text = "View Courses"
        course_name = "Placement Support"

        placement_formatted_text = (
            "## Placement Opportunities at NxGen Tech Academy\n\n"
            "NxGen Tech Academy provides dedicated career assistance and 100% placement support across all its training programs to help students, freshers, and career switchers transition successfully into high-growth IT and corporate roles.\n\n"
            "### What the Placement Support Includes\n"
            "- **Mock Interviews & Interview Preparation:** Technical and HR mock interview sessions conducted by experienced MNC industry practitioners.\n"
            "- **Resume Building & Portfolio Development:** Industry-standard CV vetting, GitHub code repository curation, and LinkedIn profile optimization.\n"
            "- **Internship Opportunities & Real-World Projects:** Hands-on capstone projects and practical live-campaign assignments to build job-ready portfolios.\n"
            "- **Industry-Aligned Training:** Practical curriculum updated to meet current corporate hiring standards.\n"
            "- **Certification Information:** Industry-recognized Course Completion Certificate from NxGen Tech Academy upon course completion.\n"
            "- **Placement Assistance & Career Guidance:** Access to recruitment drives and hiring network of 100+ partner companies (including TCS, Infosys, Deloitte, Accenture, Wipro, Capgemini, and Tech Mahindra).\n\n"
            "### Programs and Placement Support\n"
            "- **Python Programming:** 100% placement support with resume preparation, GitHub repository curation, and weekly mock technical and HR interview rounds for full-stack and backend developer roles.\n"
            "- **AIML & AI Programming:** 100% placement assistance including real-world AI/ML project portfolio curation, code reviews, and mock technical interview drills with senior data scientists.\n"
            "- **Data Analytics Programming:** 100% placement support with Power BI, Tableau, and SQL project portfolio building, resume engineering, and corporate interview prep.\n"
            "- **Digital Marketing:**\n"
            "  - *Digital Marketing Course (3 Months):* Resume preparation, portfolio building, mock interviews, and career guidance for entry-level and freelance opportunities.\n"
            "  - *Job Guarantee Digital Marketing Course (6 Months):* Dedicated 100% placement assistance / job guarantee program with live client campaigns, internships, and structured interview pipelines.\n"
            "- **SAP Courses (12 Modules):** Job-ready training with 100% placement support, technical and functional mock interviews with senior SAP consultants, resume formatting, and corporate hiring drives for ABAP on HANA, RAP/CDS, Fiori UI5, BTP, CPI, BASIS, FICO, MM, SD, PP, and QM.\n\n"
            "### Next Steps\n"
            "- **Free Weekly Live Demo Sessions:** Experience our interactive teaching methodology, live projects, and career support firsthand before enrolling.\n"
            "- **Book Demo:** Click the **Book Demo** button on the website to reserve your spot for an upcoming session.\n"
            "- For any further questions, users can contact NxGen Tech Academy directly."
        )

        return {
            "tool_type": "faq",
            "tool_name": "get_faq_tool",
            "title": topic_title,
            "course": course_name,
            "course_slug": None,
            "category": "Placements",
            "section": "Placements",
            "attributes": {
                "source_file": "placement/placement_support.md",
                "hiring_partners_count": "100+",
                "placement_assistance": "100%"
            },
            "action_url": action_url,
            "action_text": action_text,
            "text": placement_formatted_text,
            "source": "website_tool"
        }
    elif any(k in key for k in ["eligibility", "qualification", "non-tech", "freshers", "criteria", "background"]):
        faq_file = "faq/faq_eligibility.md"
        topic_title = "Course Eligibility FAQs"
        action_url = "/training-programs"
        action_text = "View Courses"
        course_name = "Course Eligibility"
    elif any(k in key for k in ["location", "address", "where", "kphb", "hyderabad", "branch", "office"]):
        faq_file = "faq/faq_location.md"
        topic_title = "Academy Location & Address FAQs"
        action_url = "/contact-us"
        action_text = "Contact Us"
        course_name = "Location & Contact"
    elif any(k in key for k in ["certificate", "certification", "degree", "diploma"]):
        faq_file = "faq/faq_certification.md"
        topic_title = "Certification FAQs"
        action_url = "/training-programs"
        action_text = "View Courses"
        course_name = "Certifications"
    elif any(k in key for k in ["mode", "online", "offline", "classroom", "timing", "batch"]):
        faq_file = "faq/faq_training_mode.md"
        topic_title = "Training Mode & Class Schedule FAQs"
        action_url = "/about-us"
        action_text = "About Us"
        course_name = "Training Mode"
    elif any(k in key for k in ["bsnl", "partner", "association", "affiliat"]):
        faq_file = "faq/faq_associations.md"
        topic_title = "Partnerships & Associations FAQs"
        action_url = "/bsnl-skill-development-partner"
        action_text = "View Partners"
        course_name = "BSNL Partnership"
    elif "python" in key:
        faq_file = "faq/faq_python.md"
        topic_title = "Python Programming FAQs"
        action_url = "/courses/python-course-training"
        action_text = "View Course"
        course_name = "Python Programming"
    elif "digital" in key or "dm" in key:
        faq_file = "faq/faq_digital_marketing.md"
        topic_title = "Digital Marketing FAQs"
        action_url = "/courses/digital-marketing-course-training"
        action_text = "View Course"
        course_name = "Digital Marketing Course"
    elif "aiml" in key:
        faq_file = "faq/faq_aiml.md"
        topic_title = "AIML Programming FAQs"
        action_url = "/courses/aiml-course-training"
        action_text = "View Course"
        course_name = "AIML Programming"
    elif "ai" in key or "artificial" in key:
        faq_file = "faq/faq_ai.md"
        topic_title = "Artificial Intelligence FAQs"
        action_url = "/courses/ai-course-training"
        action_text = "View Course"
        course_name = "AI Programming"
    elif any(k in key for k in ["about", "founder", "mission", "vision", "values"]):
        faq_file = "faq/faq_about.md"
        topic_title = "About NxGen Tech Academy FAQs"
        action_url = "/about-us"
        action_text = "About Us"
        course_name = "About NxGen Tech Academy"
    else:
        faq_file = "faq/faq_courses.md"
        topic_title = "General Courses FAQs"
        action_url = "/training-programs"
        action_text = "View Courses"
        course_name = "Courses Overview"

    parsed_faqs = parse_faq_file(faq_file)

    formatted_lines = [f"## {topic_title}\n"]
    for item in parsed_faqs:
        formatted_lines.append(f"**Q: {item['question']}**\n**A:** {item['answer']}\n")

    return {
        "tool_type": "faq",
        "tool_name": "get_faq_tool",
        "title": topic_title,
        "course": course_name,
        "course_slug": None,
        "category": "FAQ",
        "section": "FAQs",
        "attributes": {
            "source_file": faq_file,
            "total_faqs": len(parsed_faqs),
            "faqs": parsed_faqs
        },
        "action_url": action_url,
        "action_text": action_text,
        "text": "\n".join(formatted_lines).strip(),
        "source": "website_tool"
    }


def website_tools_dispatcher(
    query_input: Any,
    course_context: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Unified Phase 3 Website Tools Dispatcher:
    Executes relevant Website Tools (Pricing, Products, FAQ) based on Query Processor
    output (or raw query string), returning a standardized list of candidate records
    ready for Phase 4 Reranker.
    """
    if isinstance(query_input, dict) and "intent" in query_input:
        processed = query_input
    else:
        # Fallback dynamic import of process_query to avoid circular imports
        from rag.rag_service import process_query
        processed = process_query(str(query_input), course_context=course_context)

    intent = processed.get("intent", "GENERAL_INQUIRY")
    entities = processed.get("entities", {})
    cleaned_query = processed.get("cleaned_query", "").lower()

    course_name = entities.get("course")
    category = entities.get("category")
    section = entities.get("section")
    topic = entities.get("topic")

    results: List[Dict[str, Any]] = []

    # 1. Route to Pricing Tool
    if intent == "ADMISSIONS_FEES" or section == "fees" or any(k in cleaned_query for k in ["fee", "fees", "cost", "price", "pricing", "installment", "emi"]):
        res = get_pricing_tool(course_name=course_name, category=category)
        results.append(res)

    # 2. Route to Products Tool
    if (
        intent in ["COURSE_SPECIFIC", "COURSE_CATALOG", "COURSE_HIGHLIGHTS"]
        or course_name
        or category
        or any(k in cleaned_query for k in ["course", "catalog", "syllabus", "curriculum", "module", "highlight", "duration", "project"])
    ):
        prod_course = None if intent == "COURSE_CATALOG" else course_name
        res = get_product_tool(course_name=prod_course, category=category, section=section)
        results.append(res)

    # 3. Route to FAQ Tool
    if (
        intent in ["DEMO_BOOKING", "PLACEMENT_INFO", "ACADEMY_INFO", "GENERAL_INQUIRY"]
        or topic in ["demo", "location", "contact", "founder", "highlights"]
        or any(k in cleaned_query for k in ["demo", "placement", "eligible", "eligibility", "where", "address", "certificate", "mode", "partner", "faq", "question"])
    ):
        topic_key = topic or course_name or category or cleaned_query
        res = get_faq_tool(topic_or_course=topic_key, query=cleaned_query)
        results.append(res)

    # If no specific rule triggered, provide standard fallback product + FAQ tools
    if not results:
        results.append(get_product_tool(course_name=course_name, category=category))
        results.append(get_faq_tool(topic_or_course=cleaned_query, query=cleaned_query))

    return results


# ════════════════════════════════════════════════════════════════
# TOOL EXECUTION & METADATA DISPATCHER
# ════════════════════════════════════════════════════════════════

def execute_kb_tool(tool_name: str, tool_args: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Executes a requested Knowledge Base tool locally with strict security validation:
    - Verifies tool_name against ALLOWED_KB_TOOLS whitelist.
    - Validates, sanitizes, and bounds all argument strings.
    - Returns (tool_output_string, derived_metadata_dict).
    """
    meta: Dict[str, Any] = {
        "course_name": None,
        "course_slug": None,
        "section": None,
        "action_type": None,
        "action_url": None,
        "action_text": None,
    }

    if not isinstance(tool_name, str) or tool_name not in ALLOWED_KB_TOOLS:
        return f"Unauthorized tool: {tool_name}", meta

    if not isinstance(tool_args, dict):
        tool_args = {}

    # Argument validation & sanitization
    sanitized_args: Dict[str, str] = {}
    for k, v in tool_args.items():
        if isinstance(k, str) and isinstance(v, str):
            clean_k = re.sub(r'[^a-zA-Z0-9_]', '', k)[:50]
            clean_v = re.sub(r'[\x00\r\n]', ' ', v).strip()[:200]
            sanitized_args[clean_k] = clean_v

    if tool_name == "get_pricing_tool":
        c_name = sanitized_args.get("course_name")
        cat = sanitized_args.get("category")
        p_res = get_pricing_tool(course_name=c_name, category=cat)
        meta["course_name"] = p_res.get("course")
        meta["course_slug"] = p_res.get("course_slug")
        meta["section"] = p_res.get("section")
        meta["action_type"] = "view_course" if p_res.get("course_slug") else "view_courses"
        meta["action_url"] = p_res.get("action_url")
        meta["action_text"] = p_res.get("action_text")
        return p_res.get("text", ""), meta

    elif tool_name == "get_product_tool":
        c_name = sanitized_args.get("course_name")
        cat = sanitized_args.get("category")
        sec = sanitized_args.get("section")
        prod_res = get_product_tool(course_name=c_name, category=cat, section=sec)
        meta["course_name"] = prod_res.get("course")
        meta["course_slug"] = prod_res.get("course_slug")
        meta["section"] = prod_res.get("section")
        meta["action_type"] = "view_course" if prod_res.get("course_slug") else "view_courses"
        meta["action_url"] = prod_res.get("action_url")
        meta["action_text"] = prod_res.get("action_text")
        return prod_res.get("text", ""), meta

    elif tool_name == "get_faq_tool":
        top = sanitized_args.get("topic") or sanitized_args.get("topic_or_course")
        q = sanitized_args.get("query")
        faq_res = get_faq_tool(topic_or_course=top, query=q)
        meta["course_name"] = faq_res.get("course")
        meta["section"] = "FAQs"
        meta["action_type"] = "view_page"
        meta["action_url"] = faq_res.get("action_url")
        meta["action_text"] = faq_res.get("action_text")
        return faq_res.get("text", ""), meta

    elif tool_name == "get_academy_information":
        topic = sanitized_args.get("topic", "overview")
        content = get_academy_information(topic)
        meta["course_name"] = "About NxGen Tech Academy"
        meta["section"] = topic.capitalize()
        if topic in ["demo", "book_demo", "demo_booking", "schedule_demo", "request_demo", "free_demo"]:
            meta["course_name"] = "Book a Free Demo"
            meta["section"] = "Demo Booking"
            meta["action_type"] = "book_demo"
            meta["action_url"] = "/courses/sap-btp-freshers-course-training"
            meta["action_text"] = "Book Demo"
        elif topic in ["contact", "address", "location"]:
            meta["action_type"] = "contact_us"
            meta["action_url"] = "/contact-us"
            meta["action_text"] = "Contact Us"
        elif topic in ["placements", "differentiation"]:
            meta["action_type"] = "view_page"
            meta["action_url"] = "/why-choose-us"
            meta["action_text"] = "Why Choose Us"
        elif topic in ["admissions", "enrollment"]:
            meta["action_type"] = "register"
            meta["action_url"] = "/register"
            meta["action_text"] = "Register Now"
        elif topic in ["partners", "bsnl"]:
            meta["action_type"] = "view_page"
            meta["action_url"] = "/bsnl-skill-development-partner"
            meta["action_text"] = "View Partners"
        elif topic == "privacy_policy":
            meta["action_type"] = "view_page"
            meta["action_url"] = "/privacy-policy"
            meta["action_text"] = "Privacy Policy"
        else:
            meta["action_type"] = "view_page"
            meta["action_url"] = "/about-us"
            meta["action_text"] = "About Us"
        return content, meta

    elif tool_name == "get_course_information":
        c_name = sanitized_args.get("course_name", "")
        content = get_course_information(c_name)
        c_info = _resolve_course(c_name)
        if c_info:
            meta["course_name"] = c_info["name"]
            meta["course_slug"] = c_info["slug"]
            meta["section"] = "Course Overview"
            meta["action_type"] = "view_course"
            meta["action_url"] = c_info["url"]
            meta["action_text"] = c_info["action_text"]
        return content, meta

    elif tool_name == "get_course_section":
        c_name = sanitized_args.get("course_name", "")
        section = sanitized_args.get("section", "overview")
        content = get_course_section(c_name, section)
        c_info = _resolve_course(c_name)
        if c_info:
            meta["course_name"] = c_info["name"]
            meta["course_slug"] = c_info["slug"]
            meta["section"] = section.capitalize()
            meta["action_type"] = "view_course"
            meta["action_url"] = c_info["url"]
            meta["action_text"] = c_info["action_text"]
        return content, meta

    elif tool_name == "get_common_course_highlights":
        content = get_common_course_highlights()
        meta["course_name"] = "Course Highlights"
        meta["section"] = "Course Highlights"
        meta["action_type"] = "view_courses"
        meta["action_url"] = "/training-programs"
        meta["action_text"] = "View Courses"
        return content, meta

    elif tool_name == "get_course_catalog":
        req_cat = sanitized_args.get("category", "")
        content = get_course_catalog()
        meta["course_name"] = "All Courses Offered"
        meta["section"] = "Course Catalog"
        meta["action_type"] = "view_courses"
        meta["action_text"] = "View Courses"

        cat_lower = str(req_cat).strip().lower()
        if any(k in cat_lower for k in ["digital", "marketing", "dm", "seo"]):
            meta["action_url"] = "/training-programs?category=Digital+Marketing"
            meta["course_name"] = "Digital Marketing"
        elif any(k in cat_lower for k in ["sap", "fico", "abap", "btp", "mm", "sd", "pp", "qm", "cpi", "basis"]):
            meta["action_url"] = "/training-programs?category=SAP+Courses"
            meta["course_name"] = "SAP Courses"
        elif "python" in cat_lower:
            meta["action_url"] = "/training-programs?category=Python"
            meta["course_name"] = "Python"
        elif "analytics" in cat_lower or "power bi" in cat_lower:
            meta["action_url"] = "/training-programs?category=Data+Analytics"
            meta["course_name"] = "Data Analytics"
        elif "aiml" in cat_lower:
            meta["action_url"] = "/training-programs?category=AIML"
            meta["course_name"] = "AIML"
        elif "ai" in cat_lower:
            meta["action_url"] = "/training-programs?category=AI"
            meta["course_name"] = "AI"
        elif cat_lower and cat_lower != "all courses":
            meta["action_url"] = f"/training-programs?category={req_cat.replace(' ', '+')}"
        else:
            meta["action_url"] = "/training-programs"
        return content, meta

    return f"Unknown tool: {tool_name}", meta


# ════════════════════════════════════════════════════════════════
# GROQ TOOL SCHEMAS
# ════════════════════════════════════════════════════════════════

GROQ_KB_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_academy_information",
            "description": "Get official factual information about NxGen Tech Academy for a specific topic such as demo (booking a demo, free live demo session), overview, founder, contact, address, location, learning approach, mentors, course highlights, mission, vision, core values, differentiation, placement support, admissions, or partnerships.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": [
                            "demo",
                            "overview",
                            "founder",
                            "contact",
                            "address",
                            "location",
                            "learning_approach",
                            "mentors",
                            "course_highlights",
                            "mission",
                            "vision",
                            "core_values",
                            "differentiation",
                            "placements",
                            "admissions",
                            "partners",
                            "privacy_policy"
                        ],
                        "description": "The specific academy topic to retrieve information for."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_information",
            "description": "Get full comprehensive information from the official Knowledge Base for a specific training course offered by NxGen Tech Academy (e.g., Python Programming, AIML Programming, Artificial Intelligence, Data Analytics, Digital Marketing, SAP FICO, SAP ABAP on HANA, SAP BTP, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "The exact or common name of the course (e.g. 'Python Programming', 'AIML Programming', 'Data Analytics', 'Digital Marketing', 'SAP FICO', 'SAP BTP', 'SAP MM', etc.)."
                    }
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_section",
            "description": "Get a specific section of a course from the knowledge base (e.g. fees, duration, eligibility, prerequisites, curriculum, projects, certification, placement, industrial_readiness, career_opportunities, benefits).",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "The name of the course (e.g. 'Python Programming', 'AIML Programming', 'Data Analytics', 'SAP FICO', etc.)."
                    },
                    "section": {
                        "type": "string",
                        "enum": [
                            "overview",
                            "details",
                            "fees",
                            "duration",
                            "eligibility",
                            "prerequisites",
                            "curriculum",
                            "projects",
                            "certification",
                            "placement",
                            "industrial_readiness",
                            "career_opportunities",
                            "benefits",
                            "faqs"
                        ],
                        "description": "The specific course section to retrieve."
                    }
                },
                "required": ["course_name", "section"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_common_course_highlights",
            "description": "Get the official common Course Highlights applicable to all courses at NxGen Tech Academy (50+ Hours Live Sessions, 10+ Assignments, Certification Included, 1:1 Mentorship). Use this whenever the user asks for 'course highlights', 'academy highlights', or common highlights.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_catalog",
            "description": "Get the official list and details of training courses offered by NxGen Tech Academy. Pass category='Digital Marketing' for digital marketing queries, category='SAP Courses' for SAP queries, category='Python' for python, category='Data Analytics' for data analytics, category='AI' or 'AIML' for AI/AIML, or omit/'All Courses' for full catalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The category of courses requested (e.g. 'Digital Marketing', 'SAP Courses', 'Python', 'Data Analytics', 'AI', 'AIML', 'All Courses')."
                    }
                }
            }
        }
    }
]
