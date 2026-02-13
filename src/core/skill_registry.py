"""Central registry for reusable skills that agents can invoke by name."""
from __future__ import annotations

from typing import Any, Callable

from src.core.logger import get_logger

SkillFn = Callable[..., Any]

log = get_logger("skill_registry")


class SkillRegistry:
    """Register and invoke skills by name.

    Skills are simple functions that perform a specific task (e.g., classify an email,
    generate a social post, categorize a transaction). Agents look up skills by name
    and call them with appropriate arguments.
    """

    def __init__(self) -> None:
        self._skills: dict[str, SkillFn] = {}

    def register(self, name: str, fn: SkillFn) -> None:
        """Register a skill function under a given name."""
        if name in self._skills:
            log.warning(f"Overwriting existing skill: {name}")
        self._skills[name] = fn
        log.info(f"Registered skill: {name}")

    def get(self, name: str) -> SkillFn | None:
        return self._skills.get(name)

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Look up a skill by name and call it."""
        fn = self._skills.get(name)
        if fn is None:
            raise KeyError(f"Skill not found: {name}")
        return fn(**kwargs)

    def list_skills(self) -> list[str]:
        return sorted(self._skills.keys())

    def has(self, name: str) -> bool:
        return name in self._skills


def build_default_registry() -> SkillRegistry:
    """Build a SkillRegistry with all default skills loaded."""
    registry = SkillRegistry()

    # Import and register all skill modules
    from src.skills.email_skills import register_skills as reg_email
    from src.skills.social_skills import register_skills as reg_social
    from src.skills.finance_skills import register_skills as reg_finance
    from src.skills.document_skills import register_skills as reg_document
    from src.skills.communication_skills import register_skills as reg_communication
    from src.skills.vault_skills import register_skills as reg_vault

    reg_email(registry)
    reg_social(registry)
    reg_finance(registry)
    reg_document(registry)
    reg_communication(registry)
    reg_vault(registry)

    return registry
