"""Regenerates Dashboard.md with live status counts and recent activity."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.core.vault_manager import VaultManager


def generate_dashboard(vault: VaultManager) -> Path:
    """Generate the vault Dashboard.md with current status."""
    counts = vault.get_status_counts()
    now = datetime.now(timezone.utc)

    # Get recent items from each queue
    inbox_items = vault.list_items_recursive("Inbox")
    needs_action_items = vault.list_items_recursive("Needs_Action")
    needs_approval_items = vault.list_items_recursive("Needs_Approval")
    in_progress_items = vault.list_items_recursive("In_Progress")

    lines = [
        "# Digital FTE Dashboard",
        "",
        f"> Last updated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Queue Status",
        "",
        "| Queue | Count |",
        "|-------|-------|",
        f"| Inbox | {counts.get('inbox', 0)} |",
        f"| Needs Action | {counts.get('needs_action', 0)} |",
        f"| In Progress | {counts.get('in_progress', 0)} |",
        f"| Needs Approval | {counts.get('needs_approval', 0)} |",
        f"| Approved | {counts.get('approved', 0)} |",
        f"| Rejected | {counts.get('rejected', 0)} |",
        f"| Done | {counts.get('done', 0)} |",
        "",
    ]

    # Needs Approval section (most important for HITL)
    if needs_approval_items:
        lines.extend([
            "## Awaiting Your Approval",
            "",
        ])
        for path in needs_approval_items[:10]:
            try:
                task = vault.read_task(path)
                lines.append(f"- **{task.title}** (priority: {task.priority.value}) - [[{path.name}]]")
            except Exception:
                lines.append(f"- [[{path.name}]]")
        lines.append("")

    # In Progress
    if in_progress_items:
        lines.extend([
            "## In Progress",
            "",
        ])
        for path in in_progress_items[:10]:
            try:
                task = vault.read_task(path)
                lines.append(f"- {task.title} (agent: {task.assigned_agent})")
            except Exception:
                lines.append(f"- {path.stem}")
        lines.append("")

    # Inbox
    if inbox_items:
        lines.extend([
            "## Inbox (Awaiting Triage)",
            "",
        ])
        for path in inbox_items[:10]:
            try:
                task = vault.read_task(path)
                lines.append(f"- [{task.source}] {task.title}")
            except Exception:
                lines.append(f"- {path.stem}")
        lines.append("")

    # Needs Action
    if needs_action_items:
        lines.extend([
            "## Needs Action",
            "",
        ])
        for path in needs_action_items[:10]:
            try:
                task = vault.read_task(path)
                lines.append(f"- [{task.category}] {task.title} (priority: {task.priority.value})")
            except Exception:
                lines.append(f"- {path.stem}")
        lines.append("")

    # Quick links
    lines.extend([
        "## Quick Links",
        "",
        "- [[Company_Handbook]] - Business rules and SOPs",
        "- [[Weekly_Briefing]] - Latest CEO briefing",
        "- [[vault/Logs/]] - Execution logs",
        "",
        "---",
        f"*Digital FTE v0.1.0 | {now.strftime('%Y')}*",
    ])

    content = "\n".join(lines)
    return vault.write_raw(content, "Dashboard.md")
