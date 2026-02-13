"""Email-related skills: drafting, classification, action extraction."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.skill_registry import SkillRegistry


def classify_email(subject: str = "", body: str = "", sender: str = "", **kwargs: Any) -> dict[str, Any]:
    """Classify an email into category and priority.

    Returns dict with: category, priority, is_actionable, confidence, reasoning.
    """
    text = f"{subject} {body}".lower()

    # Simple rule-based classification (can be enhanced with LLM)
    category = "General"
    priority = "medium"
    is_actionable = True

    if any(w in text for w in ["invoice", "payment", "receipt", "billing", "overdue"]):
        category = "Finance"
        priority = "high"
    elif any(w in text for w in ["meeting", "calendar", "schedule", "appointment", "call"]):
        category = "General"
        priority = "medium"
    elif any(w in text for w in ["urgent", "asap", "critical", "emergency", "deadline"]):
        priority = "critical"
    elif any(w in text for w in ["linkedin", "social", "post", "engagement", "followers"]):
        category = "Social"
        priority = "low"
    elif any(w in text for w in ["newsletter", "unsubscribe", "promotion", "deal", "offer"]):
        is_actionable = False
        priority = "low"

    # Spam / newsletter detection
    if any(w in text for w in ["unsubscribe", "no longer wish", "opt out"]):
        is_actionable = False
        priority = "low"

    return {
        "category": category,
        "priority": priority,
        "is_actionable": is_actionable,
        "confidence": 0.7,
        "reasoning": f"Rule-based classification: {category}/{priority}",
    }


def draft_email(
    to: str = "",
    subject: str = "",
    context: str = "",
    tone: str = "professional",
    **kwargs: Any,
) -> dict[str, str]:
    """Draft an email reply or new email.

    Returns dict with: to, subject, body, summary.
    """
    # Placeholder: in production this would use Claude API
    body = (
        f"Dear recipient,\n\n"
        f"Thank you for your message regarding: {subject}\n\n"
        f"[Draft based on context: {context[:200]}...]\n\n"
        f"Best regards"
    )
    return {
        "to": to,
        "subject": f"Re: {subject}" if not subject.startswith("Re:") else subject,
        "body": body,
        "summary": f"Draft reply to {to} about {subject[:50]}",
    }


def extract_action_items(body: str = "", subject: str = "", **kwargs: Any) -> list[dict[str, str]]:
    """Extract actionable items from an email body.

    Returns list of dicts with: action, deadline, assignee.
    """
    actions = []
    lines = body.split("\n")
    action_keywords = ["please", "could you", "can you", "need to", "must", "required", "deadline", "by end of"]

    for line in lines:
        line_lower = line.strip().lower()
        if any(kw in line_lower for kw in action_keywords) and len(line.strip()) > 10:
            actions.append({
                "action": line.strip(),
                "deadline": "",
                "assignee": "",
            })

    return actions


def register_skills(registry: SkillRegistry) -> None:
    registry.register("classify_email", classify_email)
    registry.register("draft_email", draft_email)
    registry.register("extract_action_items", extract_action_items)
