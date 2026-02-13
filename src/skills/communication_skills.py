"""Communication skills: brand voice, response formatting."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.skill_registry import SkillRegistry

# Default brand voice guidelines
DEFAULT_BRAND_VOICE = {
    "tone": "professional yet approachable",
    "avoid": ["slang", "overly casual language", "jargon without explanation"],
    "prefer": ["clear language", "active voice", "concise sentences"],
    "sign_off": "Best regards",
}


def apply_brand_voice(
    text: str = "",
    brand_voice: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, str]:
    """Apply brand voice guidelines to text.

    Returns dict with: text, changes_made, voice_applied.
    """
    if brand_voice is None:
        brand_voice = DEFAULT_BRAND_VOICE

    # Simple transformations (placeholder for LLM-powered version)
    result = text

    # Ensure proper sign-off
    sign_off = brand_voice.get("sign_off", "Best regards")
    if sign_off and sign_off not in result:
        result = result.rstrip() + f"\n\n{sign_off}"

    return {
        "text": result,
        "changes_made": "Applied brand voice formatting",
        "voice_applied": brand_voice.get("tone", "professional"),
    }


def format_response(
    content: str = "",
    format_type: str = "email",
    recipient: str = "",
    **kwargs: Any,
) -> str:
    """Format a response based on type (email, message, post).

    Returns the formatted response string.
    """
    if format_type == "email":
        greeting = f"Dear {recipient},\n\n" if recipient else ""
        return f"{greeting}{content}\n\nBest regards"
    elif format_type == "message":
        return content
    elif format_type == "post":
        return content.strip()
    return content


def register_skills(registry: SkillRegistry) -> None:
    registry.register("apply_brand_voice", apply_brand_voice)
    registry.register("format_response", format_response)
