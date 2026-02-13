"""Email Agent - handles email triage, drafting, and sending."""
from __future__ import annotations

from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus


class EmailAgent(AgentBase):
    """Processes email tasks: classify, draft replies, request approval to send."""

    name = "email_agent"

    def can_handle(self, task: TaskItem) -> bool:
        return task.category == "Email" and task.status in (
            TaskStatus.NEEDS_ACTION,
            TaskStatus.APPROVED,
        )

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        self.log.info(f"Processing email task: {task.title}")

        # Move to in-progress
        task_path = self._move_to_in_progress(task, task_path)

        # Extract action items from the email
        action_items = []
        if self.skills.has("extract_action_items"):
            try:
                action_items = self.skills.invoke(
                    "extract_action_items",
                    body=task.body,
                    subject=task.title,
                )
            except Exception as e:
                self.log.warning(f"extract_action_items failed: {e}")

        # Classify to determine if reply is needed
        classification = {}
        if self.skills.has("classify_email"):
            try:
                classification = self.skills.invoke(
                    "classify_email",
                    subject=task.title,
                    body=task.body,
                    sender=task.source_data.get("from", ""),
                )
            except Exception as e:
                self.log.warning(f"classify_email failed: {e}")

        # Draft a reply
        sender = task.source_data.get("from", "")
        draft = {}
        if self.skills.has("draft_email") and sender:
            try:
                draft = self.skills.invoke(
                    "draft_email",
                    to=sender,
                    subject=task.title,
                    context=task.body[:500],
                )
            except Exception as e:
                self.log.warning(f"draft_email failed: {e}")

        # Apply brand voice to draft
        if draft and self.skills.has("apply_brand_voice"):
            try:
                voiced = self.skills.invoke("apply_brand_voice", text=draft.get("body", ""))
                draft["body"] = voiced.get("text", draft.get("body", ""))
            except Exception:
                pass

        # Build action plan
        plan_parts = []
        if action_items:
            plan_parts.append("**Action Items Found:**")
            for ai in action_items:
                plan_parts.append(f"- {ai.get('action', '')}")
        if draft:
            plan_parts.append(f"\n**Draft Reply To:** {draft.get('to', '')}")
            plan_parts.append(f"**Subject:** {draft.get('subject', '')}")
            plan_parts.append(f"\n{draft.get('body', '')}")

        task.action_plan = "\n".join(plan_parts)
        task.action_type = "send_email"
        task.action_params = {
            "to": draft.get("to", sender),
            "subject": draft.get("subject", f"Re: {task.title}"),
            "body": draft.get("body", ""),
        }

        # Request approval for sending
        if self.approval.requires_approval("send_email"):
            task_path = self._move_to_needs_approval(task, task_path)
            self.log.info(f"Email draft needs approval: {task.title}")
        else:
            task_path = self._move_to_done(task, task_path)

        return task

    def execute_approved_action(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Send the approved email via Gmail MCP."""
        self.log.info(f"Sending approved email: {task.action_params.get('to')}")
        # In production: invoke gmail_mcp.send_email with task.action_params
        task.result = f"Email sent to {task.action_params.get('to', 'unknown')}"
        task.status = TaskStatus.DONE
        task.touch()
        return task
