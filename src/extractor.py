import re
import statistics
from typing import List, Tuple
import fitz

DECIMAL_HEADER_PATTERN = re.compile(r"^\s*\d+(\.\d+)+\s+\S+")
TITLE_CASE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9 ,/&\-]{6,}$")

def find_headings(page: fitz.Page) -> List[str]:
    text_blocks = page.get_text("dict")["blocks"]
    heading_candidates = []

    for block in text_blocks:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            line_text = "".join(span["text"] for span in line["spans"]).strip()
            if not line_text:
                continue

            font_sizes = [span["size"] for span in line["spans"]]
            avg_size = statistics.mean(font_sizes)
            median_size = statistics.median(font_sizes)
            is_large_font = avg_size > 0 and avg_size >= (median_size + 1.5)

            matches_heading_pattern = (
                DECIMAL_HEADER_PATTERN.match(line_text) or
                TITLE_CASE_PATTERN.match(line_text) or
                line_text.isupper()
            )

            if is_large_font or matches_heading_pattern:
                heading_candidates.append(line_text)

    return heading_candidates

def segment_document(pages: List[str]) -> List[Tuple[str, str, int]]:
    document_segments = []
    content_buffer = []
    current_section_title = None
    section_start_page = 1

    for page_idx, page_content in enumerate(pages):
        if not page_content.strip():
            continue

        page_lines = [line.strip() for line in page_content.splitlines() if line.strip()]
        if not page_lines:
            continue

        first_line = page_lines[0]
        is_heading = (
            DECIMAL_HEADER_PATTERN.match(first_line) or
            TITLE_CASE_PATTERN.match(first_line) or
            first_line.isupper()
        )

        if is_heading:
            if current_section_title:
                section_body = "\n".join(content_buffer).strip()
                document_segments.append((current_section_title, section_body, section_start_page))

            current_section_title = first_line
            content_buffer = page_lines[1:]
            section_start_page = page_idx + 1
        else:
            content_buffer.extend(page_lines)

    if current_section_title and content_buffer:
        final_body = "\n".join(content_buffer).strip()
        document_segments.append((current_section_title, final_body, section_start_page))

    return document_segments
