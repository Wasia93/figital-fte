"""HITL approval workflow engine.

Manages the Needs_Approval -> Approved/Rejected flow.
Human reviews items in Obsidian and moves files between folders.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.config_loader import load_safety_rules
from src.core.logger import get_logger
from src.core.task_item import TaskItem, TaskStatus
from src.core.vault_manager import VaultManager

log = get_logger("approval_manager")


class ApprovalManager:
    """Manages the human-in-the-loop approval workflow."""

    def __init__(self, vault: VaultManager):
        self.vault = vault
        self._rules = load_safety_rules()

    def requires_approval(self, action_type: str, context: dict[str, Any] | None = None) -> bool:
        """Check if an action type requires human approval per safety_rules.yaml."""
        rules = self._rules.get("approval_rules", {})
        rule = rules.get(action_type)
        if rule is not None:
            return rule.get("requires_approval", True)
        return self._rules.get("default_requires_approval", True)

    def get_risk_level(self, action_type: str) -> str:
        """Get risk level for an action type."""
        rules = self._rules.get("approval_rules", {})
        rule = rules.get(action_type)
        if rule is not None:
            return rule.get("risk_level", "high")
        return self._rules.get("default_risk_level", "high")

    def create_approval_request(self, task: TaskItem, task_path: Path) -> Path:
        """Move a task to Needs_Approval/ with human-readable approval instructions."""
        task.status = TaskStatus.NEEDS_APPROVAL
        task.approval_required = True
        task.touch()

        # Enrich the body with approval instructions
        risk = self.get_risk_level(task.action_type)
        approval_section = self._format_approval_section(task, risk)
        task.body = task.body + "\n\n" + approval_section if task.body else approval_section

        new_path = self.vault.move_task(task_path, "Needs_Approval")
        new_path.write_text(task.to_markdown(), encoding="utf-8")
        log.info(f"Created approval request: {task.title} ({task.id}) -> Needs_Approval/")
        return new_path

    def check_approved(self) -> list[tuple[Path, TaskItem]]:
        """Scan the Approved/ folder for items moved there by a human."""
        return self.vault.get_all_approved_items()

    def check_rejected(self) -> list[tuple[Path, TaskItem]]:
        """Scan the Rejected/ folder for items moved there by a human."""
        return self.vault.get_all_rejected_items()

    def process_approved(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Mark a task as approved and ready for execution."""
        task.status = TaskStatus.APPROVED
        task.touch()
        task_path.write_text(task.to_markdown(), encoding="utf-8")
        log.info(f"Task approved: {task.title} ({task.id})")
        return task

    def process_rejected(self, task: TaskItem, task_path: Path) -> Path:
        """Mark a rejected task and archive it."""
        task.status = TaskStatus.REJECTED
        task.result = "Rejected by human reviewer"
        task.touch()
        task_path.write_text(task.to_markdown(), encoding="utf-8")
        dest = self.vault.archive_task(task_path)
        log.info(f"Task rejected and archived: {task.title} ({task.id})")
        return dest

    def _format_approval_section(self, task: TaskItem, risk: str) -> str:
        """Generate human-readable approval instructions."""
        lines = [
            "---",
            "## Approval Required",
            "",
            f"**Action:** {task.action_type}",
            f"**Risk Level:** {risk.upper()}",
            "",
        ]
        if task.action_plan:
            lines.append(f"**Plan:** {task.action_plan}")
            lines.append("")
        if task.action_params:
            lines.append("**Parameters:**")
            for k, v in task.action_params.items():
                lines.append(f"- **{k}:** {v}")
            lines.append("")
        lines.extend([
            "### How to approve or reject",
            "",
            "- **APPROVE**: Move this file to the `Approved/` folder",
            "- **REJECT**: Move this file to the `Rejected/` folder",
            "",
            f"*Generated at {task.updated_at}*",
        ])
        return "\n".join(lines)
