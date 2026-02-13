"""Triage Agent - classifies and routes Inbox items to Needs_Action."""
from __future__ import annotations

from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus, Priority


class TriageAgent(AgentBase):
    """Routes Inbox items to the correct Needs_Action subdirectory.

    Uses the classify_email skill (and source metadata) to determine:
    - Category (Email, Social, Finance, General)
    - Priority (critical, high, medium, low)
    - Whether the item is actionable
    """

    name = "triage_agent"

    def can_handle(self, task: TaskItem) -> bool:
        return task.status == TaskStatus.INBOX

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        self.log.info(f"Triaging: {task.title} (source={task.source})")

        # Classify based on source and content
        classification = self._classify(task)
        category = classification["category"]
        priority = classification["priority"]
        is_actionable = classification["is_actionable"]

        task.category = category
        task.priority = Priority(priority)
        task.status = TaskStatus.NEEDS_ACTION
        task.touch()

        if not is_actionable:
            # Non-actionable items go straight to Done
            self.log.info(f"Non-actionable, archiving: {task.title}")
            task.status = TaskStatus.DONE
            task.result = "Triaged as non-actionable"
            task_path.write_text(task.to_markdown(), encoding="utf-8")
            self.vault.archive_task(task_path)
            return task

        # Move to appropriate Needs_Action subdirectory
        dest = self.vault.move_task(task_path, "Needs_Action", category)
        dest.write_text(task.to_markdown(), encoding="utf-8")
        self.log.info(f"Routed to Needs_Action/{category}: {task.title} (priority={priority})")

        return task

    def _classify(self, task: TaskItem) -> dict:
        """Classify a task using the classify_email skill or source-based routing."""
        # Source-based routing
        source_to_category = {
            "Email": "Email",
            "WhatsApp": "Email",
            "Banking": "Finance",
            "Filesystem": "General",
        }
        default_category = source_to_category.get(task.source, "General")

        # Use classify_email skill if available for richer classification
        if self.skills.has("classify_email"):
            try:
                result = self.skills.invoke(
                    "classify_email",
                    subject=task.title,
                    body=task.body,
                    sender=task.source_data.get("from", ""),
                )
                return {
                    "category": result.get("category", default_category),
                    "priority": result.get("priority", "medium"),
                    "is_actionable": result.get("is_actionable", True),
                }
            except Exception as e:
                self.log.warning(f"classify_email failed, using defaults: {e}")

        return {
            "category": default_category,
            "priority": task.priority.value,
            "is_actionable": True,
        }
