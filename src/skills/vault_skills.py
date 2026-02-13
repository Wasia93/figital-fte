"""Vault skills: search, dashboard updates, task archival."""
from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.skill_registry import SkillRegistry


def search_vault(
    query: str = "",
    vault_path: str = "",
    subpath: str = "",
    **kwargs: Any,
) -> list[dict[str, str]]:
    """Search the vault for files matching a query.

    Returns list of dicts with: path, title, snippet.
    """
    from src.core.vault_manager import VaultManager

    vault = VaultManager(Path(vault_path)) if vault_path else VaultManager()
    subpath_parts = subpath.split("/") if subpath else []
    results = vault.search(query, *subpath_parts)

    output = []
    for p in results[:20]:
        try:
            text = p.read_text(encoding="utf-8")
            # Extract title from frontmatter or first heading
            title = p.stem
            for line in text.split("\n"):
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"')
                    break
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            # Get snippet around match
            idx = text.lower().find(query.lower())
            start = max(0, idx - 50)
            end = min(len(text), idx + len(query) + 50)
            snippet = text[start:end].replace("\n", " ")
            output.append({"path": str(p), "title": title, "snippet": snippet})
        except Exception:
            continue
    return output


def update_dashboard(vault_path: str = "", **kwargs: Any) -> str:
    """Regenerate the vault dashboard. Returns the path to Dashboard.md."""
    from src.dashboard.dashboard_generator import generate_dashboard
    from src.core.vault_manager import VaultManager

    vault = VaultManager(Path(vault_path)) if vault_path else VaultManager()
    return str(generate_dashboard(vault))


def archive_task(
    task_path: str = "",
    vault_path: str = "",
    **kwargs: Any,
) -> str:
    """Archive a completed task to Done/YYYY/MM/. Returns destination path."""
    from src.core.vault_manager import VaultManager

    vault = VaultManager(Path(vault_path)) if vault_path else VaultManager()
    source = Path(task_path)
    dest = vault.archive_task(source)
    return str(dest)


def register_skills(registry: SkillRegistry) -> None:
    registry.register("search_vault", search_vault)
    registry.register("update_dashboard", update_dashboard)
    registry.register("archive_task", archive_task)
