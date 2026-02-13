"""Document skills: summarization, entity extraction, report generation."""
from __future__ import annotations

import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.skill_registry import SkillRegistry


def summarize_document(text: str = "", max_sentences: int = 5, **kwargs: Any) -> dict[str, str]:
    """Summarize a document into key points.

    Returns dict with: summary, word_count, key_points.
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    summary_sentences = sentences[:max_sentences]
    summary = ". ".join(summary_sentences) + "." if summary_sentences else "No content to summarize."

    return {
        "summary": summary,
        "word_count": str(len(text.split())),
        "sentence_count": str(len(sentences)),
        "key_points": "\n".join(f"- {s}" for s in summary_sentences),
    }


def extract_entities(text: str = "", **kwargs: Any) -> dict[str, list[str]]:
    """Extract named entities from text (simple pattern-based).

    Returns dict with: emails, urls, dates, amounts, phone_numbers.
    """
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    urls = re.findall(r"https?://[^\s<>\"']+", text)
    dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    amounts = re.findall(r"[R$]\s?\d[\d,]*\.?\d*", text)
    phones = re.findall(r"\+?\d[\d\s-]{8,15}\d", text)

    return {
        "emails": list(set(emails)),
        "urls": list(set(urls)),
        "dates": list(set(dates)),
        "amounts": list(set(amounts)),
        "phone_numbers": list(set(phones)),
    }


def generate_report(
    title: str = "Report",
    sections: list[dict[str, str]] | None = None,
    **kwargs: Any,
) -> str:
    """Generate a formatted markdown report.

    Returns the report as a markdown string.
    """
    if sections is None:
        sections = []

    lines = [f"# {title}", ""]
    for section in sections:
        heading = section.get("heading", "Section")
        content = section.get("content", "")
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def register_skills(registry: SkillRegistry) -> None:
    registry.register("summarize_document", summarize_document)
    registry.register("extract_entities", extract_entities)
    registry.register("generate_report", generate_report)
