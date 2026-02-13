"""CEO Briefing Agent - generates weekly audit and briefing reports."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus


class CEOBriefingAgent(AgentBase):
    """Generates a weekly CEO briefing summarizing all activity."""

    name = "ceo_briefing_agent"

    def can_handle(self, task: TaskItem) -> bool:
        return False  # Triggered by schedule, not task queue

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        # Not used directly - see generate_briefing()
        return task

    def generate_briefing(self) -> str:
        """Generate the weekly CEO briefing report.

        Returns the path to the generated briefing file.
        """
        self.log.info("Generating weekly CEO briefing")

        counts = self.vault.get_status_counts()
        now = datetime.now(timezone.utc)
        week_str = now.strftime("%Y-W%W")

        # Collect recent activity from Done
        done_items = self.vault.list_items_recursive("Done")
        recent_done = done_items[-20:]  # Last 20 completed items

        # Build sections
        sections = []

        # Executive summary
        sections.append({
            "heading": "Executive Summary",
            "content": (
                f"**Week:** {week_str}\n"
                f"**Report generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                f"**Current queue status:**\n"
                f"- Inbox: {counts.get('inbox', 0)}\n"
                f"- Needs Action: {counts.get('needs_action', 0)}\n"
                f"- In Progress: {counts.get('in_progress', 0)}\n"
                f"- Awaiting Approval: {counts.get('needs_approval', 0)}\n"
                f"- Completed this period: {len(recent_done)}\n"
            ),
        })

        # Completed items summary
        done_summaries = []
        for path in recent_done:
            try:
                task = self.vault.read_task(path)
                done_summaries.append(f"- [{task.source}] {task.title} ({task.result or 'completed'})")
            except Exception:
                done_summaries.append(f"- {path.stem}")

        sections.append({
            "heading": "Completed Items",
            "content": "\n".join(done_summaries) if done_summaries else "No items completed in this period.",
        })

        # Pending items requiring attention
        needs_approval = self.vault.list_items_recursive("Needs_Approval")
        if needs_approval:
            approval_lines = []
            for path in needs_approval:
                try:
                    task = self.vault.read_task(path)
                    approval_lines.append(f"- **{task.title}** (priority: {task.priority.value}) - {task.action_type}")
                except Exception:
                    approval_lines.append(f"- {path.stem}")
            sections.append({
                "heading": "Items Awaiting Your Approval",
                "content": "\n".join(approval_lines),
            })

        # Generate the report
        if self.skills.has("generate_report"):
            report = self.skills.invoke(
                "generate_report",
                title=f"CEO Briefing - {week_str}",
                sections=sections,
            )
        else:
            report = f"# CEO Briefing - {week_str}\n\n"
            for s in sections:
                report += f"## {s['heading']}\n\n{s['content']}\n\n"

        # Write to vault
        briefing_path = self.vault.write_raw(report, "Weekly_Briefing.md")
        self.log.info(f"CEO briefing written to {briefing_path}")
        return str(briefing_path)
