"""
Structure-Aware Knowledge-Base Chunking for NxGen Tech Academy
=============================================================
This module parses individual course Markdown documents from the knowledge base,
understands the semantic and document structure, groups related short sections,
splits oversized sections recursively at logical boundaries, retains course context,
and produces structured JSON chunks with metadata.

Rules strictly adhered to:
1. Each course is processed completely separately.
2. Every chunk retains course context (in text and metadata).
3. Logically related info is kept together.
4. Short sections (Duration, Fees, Eligibility, Prerequisites, Course Mode) are grouped into 'Course Details'.
5. Major sections (Overview, Curriculum, Projects, Industrial Readiness, Certification, Placement, Careers, FAQ, Other) remain separate.
6. Large sections are split logically at sub-module/Q&A/paragraph boundaries with overlap.
7. Target chunk size: 1000–1500 characters (natural boundaries preserved).
8. Overlap: 150–200 characters applied when large sections are split.
9. FAQ question-answer pairs are never separated.
10. No cross-course mixing.
11. Source URL sections are ignored and excluded from chunk text.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


# Configuration
TARGET_CHUNK_SIZE = 1400       # Target max size in chars for a section chunk
MIN_CHUNK_SPLIT_SIZE = 1100    # When packing sub-elements, target range ~1000-1400
OVERLAP_SIZE = 180             # Target overlap in chars when splitting oversized text


def clean_text(text: str) -> str:
    """Strip extraneous whitespace while preserving line breaks."""
    text = text.strip()
    # Normalize multiple blank lines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def extract_course_title_and_slug(content: str, filename: str) -> Tuple[str, Optional[str], str]:
    """
    Extracts the course title, course_slug, and body content from the document.
    Returns (course_title, course_slug, body_content_without_title_and_frontmatter).
    """
    course_slug: Optional[str] = None
    body = content
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            # Extract course_slug from frontmatter
            slug_match = re.search(r'course_slug:\s*["\']?([^"\'\n]+)["\']?', fm_text)
            if slug_match:
                course_slug = slug_match.group(1).strip()

    body = body.strip()

    # Find the first H1 heading (# Course Name)
    match = re.search(r'^#\s+([^\n]+)', body, re.MULTILINE)
    if match:
        course_title = match.group(1).strip()
        # Remove the title line from body
        body = body[:match.start()] + body[match.end():]
        return course_title, course_slug, body.strip()

    # Fallback to file name formatted nicely
    name = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
    return name, course_slug, body


def parse_document_sections(body: str) -> List[Tuple[str, str]]:
    """
    Splits the body into top-level sections (## Heading or # Heading).
    Returns list of (heading_name, heading_content).
    """
    # Find all level 2 or level 1 headings
    heading_pattern = re.compile(r'^(?:##|#)\s+([^\n]+)', re.MULTILINE)
    matches = list(heading_pattern.finditer(body))

    if not matches:
        return [("Content", body)]

    sections = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections.append((heading, content))

    return sections


def classify_section(heading: str) -> str:
    """Maps arbitrary section headings to canonical section categories."""
    h = heading.lower().strip()
    
    # Source URL -> ignore
    if any(k in h for k in ['source url', 'source_url', 'source link']):
        return "IGNORE_SOURCE_URL"

    # Course Details sub-sections
    if h in ['duration', 'course duration', 'fees', 'fee', 'course fee', 'course fees',
             'eligibility', 'prerequisite', 'prerequisites', 'course mode', 
             'mode of training', 'training mode', 'mode']:
        return "COURSE_DETAILS_FIELD"

    # Overview & Description
    if any(k in h for k in ['course overview', 'overview']):
        return "Course Overview"
    if any(k in h for k in ['course description', 'description', 'about course', 'about the course']):
        return "Course Description"

    # Curriculum / Modules
    if any(k in h for k in ['curriculum', 'modules', 'syllabus', 'course content', 'topics covered']):
        return "Curriculum"

    # Projects
    if any(k in h for k in ['projects', 'project work', 'real-time projects', 'capstone']):
        return "Projects"

    # Industrial Readiness
    if any(k in h for k in ['industrial readiness', 'industry readiness', 'job readiness']):
        return "Industrial Readiness"

    # Certification
    if any(k in h for k in ['certification', 'certificates', 'exam']):
        return "Certification"

    # Placement Assistance
    if any(k in h for k in ['placement assistance', 'placement support', 'placements', 'placement']):
        return "Placement Assistance"

    # Career Opportunities
    if any(k in h for k in ['career opportunities', 'career paths', 'job roles', 'job opportunities', 'career scope']):
        return "Career Opportunities"

    # FAQ
    if any(k in h for k in ['frequently asked questions', 'faq', 'faqs', 'q&a', 'questions & answers']):
        return "Frequently Asked Questions"

    # Other Course Information
    if any(k in h for k in ['other course information', 'other information', 'learning outcomes', 'key benefits', 'highlights']):
        return "Other Course Information"

    return heading


def split_subsections(content: str) -> List[Tuple[str, str]]:
    """
    Splits content containing ### Sub-headings into individual items.
    Returns list of (subheading_title, subcontent).
    """
    sub_pattern = re.compile(r'^###\s+([^\n]+)', re.MULTILINE)
    matches = list(sub_pattern.finditer(content))

    if not matches:
        return [("", content)]

    items = []
    # If there is text before the first ### heading
    if matches[0].start() > 0:
        pre_text = content[:matches[0].start()].strip()
        if pre_text:
            items.append(("", pre_text))

    for i, match in enumerate(matches):
        sub_title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sub_content = content[start:end].strip()
        items.append((sub_title, sub_content))

    return items


def split_faq_entries(content: str) -> List[str]:
    """
    Splits FAQ content into distinct Q&A units, ensuring questions are never separated from answers.
    Also strips out any stray Source: lines within FAQs.
    """
    # Strip source URLs inside FAQ if any
    cleaned = re.sub(r'\*Source:\*.*?(?:\n|$)', '', content)
    cleaned = re.sub(r'Source:\s*https?://\S+', '', cleaned)
    
    # Split by ### Q: or ### Question:
    pattern = re.compile(r'(?=^###\s+Q(?:uestion)?[:\s])', re.MULTILINE)
    parts = pattern.split(cleaned)
    
    faqs = []
    for p in parts:
        p = p.strip()
        # Remove trailing markdown divider if present
        p = re.sub(r'\n---+\s*$', '', p).strip()
        if p:
            faqs.append(p)

    if not faqs:
        sub_items = split_subsections(cleaned)
        faqs = [f"### {title}\n{c}".strip() if title else c for title, c in sub_items if c]

    return faqs


def recursive_split_text(
    text: str,
    target_size: int = TARGET_CHUNK_SIZE,
    overlap: int = OVERLAP_SIZE
) -> List[str]:
    """
    Splits long section text into overlapping chunks if it exceeds target size.
    Prefers splitting on paragraphs, then sentences, then lines.
    """
    text = clean_text(text)
    if len(text) <= target_size:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_len = len(para) + 2
        if current_length + para_len > target_size and current_chunk:
            combined = "\n\n".join(current_chunk).strip()
            chunks.append(combined)

            # Build overlap from the end of current_chunk
            overlap_chunk = []
            overlap_length = 0
            for prev_p in reversed(current_chunk):
                if overlap_length + len(prev_p) + 2 <= overlap:
                    overlap_chunk.insert(0, prev_p)
                    overlap_length += len(prev_p) + 2
                else:
                    break

            current_chunk = overlap_chunk + [para]
            current_length = sum(len(p) + 2 for p in current_chunk)
        else:
            current_chunk.append(para)
            current_length += para_len

    if current_chunk:
        combined = "\n\n".join(current_chunk).strip()
        if not chunks or combined != chunks[-1]:
            chunks.append(combined)

    return chunks


def chunk_course_document(
    file_path: Path,
    workspace_root: Path
) -> List[Dict[str, Any]]:
    """
    Processes a single course Markdown document and produces structured chunks.
    Extracts canonical course_slug from frontmatter if available.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Relative source path
    try:
        source_file = str(file_path.relative_to(workspace_root)).replace("\\", "/")
    except ValueError:
        source_file = str(file_path.name)

    course_title, course_slug, body = extract_course_title_and_slug(raw_content, file_path.name)
    raw_sections = parse_document_sections(body)

    # Buckets for grouping
    course_details_items: List[Tuple[str, str]] = []
    course_overview_parts: List[Tuple[str, str]] = []
    structured_sections: Dict[str, Any] = {}

    for heading, content in raw_sections:
        category = classify_section(heading)

        if category == "IGNORE_SOURCE_URL":
            continue

        elif category == "COURSE_DETAILS_FIELD":
            course_details_items.append((heading, content))

        elif category in ["Course Overview", "Course Description"]:
            course_overview_parts.append((heading, content))

        else:
            if category not in structured_sections:
                structured_sections[category] = []
            structured_sections[category].append((heading, content))

    generated_chunks: List[Dict[str, Any]] = []

    # 1. Course Overview Chunk (Principle 5)
    if course_overview_parts:
        overview_text_parts = []
        for h, c in course_overview_parts:
            overview_text_parts.append(f"### {h}\n{c}")
        full_overview = "\n\n".join(overview_text_parts)
        
        chunk_text = f"Course: {course_title}\nSection: Course Overview\n\n{full_overview}"
        generated_chunks.append({
            "text": clean_text(chunk_text),
            "metadata": {
                "course": course_title,
                "course_slug": course_slug,
                "section": "Course Overview",
                "source_file": source_file
            }
        })

    # 2. Course Details Chunk (Principle 4: Duration, Fees, Eligibility, Prerequisites, Mode)
    if course_details_items:
        details_lines = []
        for field_name, val in course_details_items:
            clean_val = val.strip()
            if "\n" in clean_val:
                details_lines.append(f"**{field_name}:**\n{clean_val}")
            else:
                details_lines.append(f"**{field_name}:** {clean_val}")
        details_body = "\n\n".join(details_lines)

        chunk_text = f"Course: {course_title}\nSection: Course Details\n\n{details_body}"
        generated_chunks.append({
            "text": clean_text(chunk_text),
            "metadata": {
                "course": course_title,
                "course_slug": course_slug,
                "section": "Course Details",
                "source_file": source_file
            }
        })

    # 3. Process remaining major sections
    ordered_section_keys = [
        "Curriculum",
        "Projects",
        "Industrial Readiness",
        "Certification",
        "Placement Assistance",
        "Career Opportunities",
        "Frequently Asked Questions",
        "Other Course Information"
    ]
    for k in structured_sections.keys():
        if k not in ordered_section_keys:
            ordered_section_keys.append(k)

    for section_name in ordered_section_keys:
        if section_name not in structured_sections:
            continue

        items = structured_sections[section_name]
        combined_content = "\n\n".join(
            c if h == section_name else f"### {h}\n{c}" for h, c in items
        ).strip()

        # Handle specific section types
        if section_name == "Frequently Asked Questions":
            # FAQ: Never separate a question from its answer (Principle 9)
            faqs = split_faq_entries(combined_content)
            
            total_faq_len = sum(len(f) for f in faqs)
            if total_faq_len <= TARGET_CHUNK_SIZE:
                faq_body = "\n\n".join(faqs)
                chunk_text = f"Course: {course_title}\nSection: Frequently Asked Questions\n\n{faq_body}"
                generated_chunks.append({
                    "text": clean_text(chunk_text),
                    "metadata": {
                        "course": course_title,
                        "course_slug": course_slug,
                        "section": "Frequently Asked Questions",
                        "source_file": source_file
                    }
                })
            else:
                # Group FAQs into sub-chunks
                faq_chunks = []
                current_group = []
                current_len = 0
                for item in faqs:
                    item_len = len(item) + 2
                    if current_len + item_len > TARGET_CHUNK_SIZE and current_group:
                        faq_chunks.append("\n\n".join(current_group))
                        current_group = [item]
                        current_len = item_len
                    else:
                        current_group.append(item)
                        current_len += item_len
                if current_group:
                    faq_chunks.append("\n\n".join(current_group))

                total_parts = len(faq_chunks)
                for idx, part in enumerate(faq_chunks, 1):
                    part_section = f"Frequently Asked Questions (Part {idx} of {total_parts})" if total_parts > 1 else "Frequently Asked Questions"
                    chunk_text = f"Course: {course_title}\nSection: {part_section}\n\n{part}"
                    generated_chunks.append({
                        "text": clean_text(chunk_text),
                        "metadata": {
                            "course": course_title,
                            "course_slug": course_slug,
                            "section": part_section,
                            "source_file": source_file
                        }
                    })

        elif section_name in ["Curriculum", "Industrial Readiness"]:
            # Structural breakdown by ### Module X:
            subsections = split_subsections(combined_content)
            
            module_blocks = []
            for sub_title, sub_body in subsections:
                if sub_title:
                    module_blocks.append(f"### {sub_title}\n{sub_body}".strip())
                else:
                    module_blocks.append(sub_body.strip())

            total_mod_len = sum(len(b) for b in module_blocks)
            if total_mod_len <= TARGET_CHUNK_SIZE:
                mod_body = "\n\n".join(module_blocks)
                chunk_text = f"Course: {course_title}\nSection: {section_name}\n\n{mod_body}"
                generated_chunks.append({
                    "text": clean_text(chunk_text),
                    "metadata": {
                        "course": course_title,
                        "course_slug": course_slug,
                        "section": section_name,
                        "source_file": source_file
                    }
                })
            else:
                # Group module blocks into chunks of ~1000-1400 chars
                mod_chunks = []
                current_group = []
                current_len = 0

                for block in module_blocks:
                    block_len = len(block) + 2
                    if block_len > TARGET_CHUNK_SIZE:
                        if current_group:
                            mod_chunks.append("\n\n".join(current_group))
                            current_group = []
                            current_len = 0
                        sub_splits = recursive_split_text(block, TARGET_CHUNK_SIZE, OVERLAP_SIZE)
                        for sp in sub_splits:
                            mod_chunks.append(sp)
                    elif current_len + block_len > TARGET_CHUNK_SIZE and current_group:
                        mod_chunks.append("\n\n".join(current_group))
                        current_group = [block]
                        current_len = block_len
                    else:
                        current_group.append(block)
                        current_len += block_len

                if current_group:
                    mod_chunks.append("\n\n".join(current_group))

                total_parts = len(mod_chunks)
                for idx, part in enumerate(mod_chunks, 1):
                    part_section = f"{section_name} (Part {idx} of {total_parts})" if total_parts > 1 else section_name
                    chunk_text = f"Course: {course_title}\nSection: {part_section}\n\n{part}"
                    generated_chunks.append({
                        "text": clean_text(chunk_text),
                        "metadata": {
                            "course": course_title,
                            "course_slug": course_slug,
                            "section": part_section,
                            "source_file": source_file
                        }
                    })

        else:
            # General sections
            if len(combined_content) <= TARGET_CHUNK_SIZE:
                chunk_text = f"Course: {course_title}\nSection: {section_name}\n\n{combined_content}"
                generated_chunks.append({
                    "text": clean_text(chunk_text),
                    "metadata": {
                        "course": course_title,
                        "course_slug": course_slug,
                        "section": section_name,
                        "source_file": source_file
                    }
                })
            else:
                sub_parts = recursive_split_text(combined_content, TARGET_CHUNK_SIZE, OVERLAP_SIZE)
                total_parts = len(sub_parts)
                for idx, part in enumerate(sub_parts, 1):
                    part_section = f"{section_name} (Part {idx} of {total_parts})" if total_parts > 1 else section_name
                    chunk_text = f"Course: {course_title}\nSection: {part_section}\n\n{part}"
                    generated_chunks.append({
                        "text": clean_text(chunk_text),
                        "metadata": {
                            "course": course_title,
                            "course_slug": course_slug,
                            "section": part_section,
                            "source_file": source_file
                        }
                    })

    return generated_chunks


def process_knowledge_base(
    kb_dir: Path,
    output_file: Path,
    workspace_root: Path
) -> Dict[str, Any]:
    """
    Scans the entire knowledge base directory recursively, generates chunks, and writes chunks.json.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if kb_dir.is_dir():
        md_files = sorted(list(kb_dir.rglob("*.md")))
    else:
        md_files = []

    all_chunks: List[Dict[str, Any]] = []
    course_chunk_counts: Dict[str, int] = {}
    files_processed = 0

    for md_file in md_files:
        chunks = chunk_course_document(md_file, workspace_root)
        files_processed += 1

        for ch in chunks:
            course = ch["metadata"]["course"]
            course_chunk_counts[course] = course_chunk_counts.get(course, 0) + 1

        all_chunks.extend(chunks)

    # Save to chunks.json
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    stats = {
        "files_processed": files_processed,
        "total_chunks": len(all_chunks),
        "chunks_per_course": course_chunk_counts
    }

    return stats


def main():
    workspace_root = Path(__file__).resolve().parent.parent.parent
    kb_dir = workspace_root / "knowledge_base"
    output_file = workspace_root / "rag" / "chunks" / "chunks.json"

    print("=" * 60)
    print("NxGen Tech Academy - Structure-Aware Knowledge-Base Chunking")
    print("=" * 60)
    print(f"Source Knowledge Base: {kb_dir}")
    print(f"Output Chunks File:    {output_file}")
    print("-" * 60)

    stats = process_knowledge_base(kb_dir, output_file, workspace_root)

    print(f"Files Processed: {stats['files_processed']}")
    print(f"Total Chunks:    {stats['total_chunks']}")
    print("-" * 60)
    print("Chunks Per Course / Category:")
    for course, count in sorted(stats["chunks_per_course"].items()):
        print(f"  • {course:<40} : {count} chunks")
    print("=" * 60)
    print(f"Successfully saved all {stats['total_chunks']} chunks to {output_file}")


if __name__ == "__main__":
    main()
