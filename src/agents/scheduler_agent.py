"""Scheduler Agent - handles calendar and meeting management."""
from __future__ import annotations

from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus


class SchedulerAgent(AgentBase):
    """Manages calendar events, meeting scheduling, and availability checks."""

    name = "scheduler_agent"

    def can_handle(self, task: TaskItem) -> bool:
        # Handle general tasks that mention scheduling keywords
        if task.status not in (TaskStatus.NEEDS_ACTION, TaskStatus.APPROVED):
            return False
        if task.category == "General":
            text = f"{task.title} {task.body}".lower()
            return any(w in text for w in ["meeting", "calendar", "schedule", "appointment", "call", "event"])
        return False

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        self.log.info(f"Processing scheduler task: {task.title}")

        task_path = self._move_to_in_progress(task, task_path)

        # Extract scheduling details from the task
        entities = {}
        if self.skills.has("extract_entities"):
            try:
                entities = self.skills.invoke("extract_entities", text=f"{task.title}\n{task.body}")
            except Exception:
                pass

        dates = entities.get("dates", [])
        emails = entities.get("emails", [])

        # Build action plan
        plan_parts = [f"**Event:** {task.title}"]
        if dates:
            plan_parts.append(f"**Detected dates:** {', '.join(dates)}")
        if emails:
            plan_parts.append(f"**Participants:** {', '.join(emails)}")
        plan_parts.append("\n**Action:** Create calendar event")

        task.action_plan = "\n".join(plan_parts)
        task.action_type = "create_event"
        task.action_params = {
            "title": task.title,
            "dates": dates,
            "participants": emails,
        }

        # Calendar events need approval
        if self.approval.requires_approval("create_event"):
            task_path = self._move_to_needs_approval(task, task_path)
            self.log.info(f"Calendar event needs approval: {task.title}")
        else:
            task_path = self._move_to_done(task, task_path)

        return task

    def execute_approved_action(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Create the approved calendar event via Calendar MCP."""
        self.log.info(f"Creating approved calendar event: {task.title}")
        # In production: invoke calendar_mcp.create_event
        task.result = f"Calendar event created: {task.title}"
        task.status = TaskStatus.DONE
        task.touch()
        return task
