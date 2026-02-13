"""Finance Agent - handles transaction categorization, invoicing, payments."""
from __future__ import annotations

from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus


class FinanceAgent(AgentBase):
    """Processes financial tasks: categorize transactions, match invoices, handle payments."""

    name = "finance_agent"

    def can_handle(self, task: TaskItem) -> bool:
        return task.category == "Finance" and task.status in (
            TaskStatus.NEEDS_ACTION,
            TaskStatus.APPROVED,
        )

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        self.log.info(f"Processing finance task: {task.title}")

        task_path = self._move_to_in_progress(task, task_path)

        # Categorize the transaction
        categorization = {}
        if self.skills.has("categorize_transaction"):
            try:
                categorization = self.skills.invoke(
                    "categorize_transaction",
                    description=task.title,
                    amount=task.source_data.get("amount", 0),
                    vendor=task.source_data.get("partner", ""),
                )
            except Exception as e:
                self.log.warning(f"categorize_transaction failed: {e}")

        # Check for anomalies
        anomaly = {}
        if self.skills.has("detect_anomaly"):
            try:
                anomaly = self.skills.invoke(
                    "detect_anomaly",
                    transaction=task.source_data,
                    historical_avg=5000.0,  # Placeholder
                )
            except Exception as e:
                self.log.warning(f"detect_anomaly failed: {e}")

        # Build action plan
        plan_parts = []
        if categorization:
            cat = categorization.get("category", "Uncategorized")
            conf = categorization.get("confidence", 0)
            plan_parts.append(f"**Category:** {cat} (confidence: {conf:.0%})")
            plan_parts.append(f"**Account:** {categorization.get('suggested_account', 'N/A')}")
            plan_parts.append(f"**Type:** {'Expense' if categorization.get('is_expense') else 'Revenue'}")

        if anomaly and anomaly.get("is_anomaly"):
            plan_parts.append(f"\n**ANOMALY DETECTED:** {anomaly.get('reason')}")
            plan_parts.append(f"**Severity:** {anomaly.get('severity', 'unknown').upper()}")

        plan_parts.append(f"\n**Recommended Action:** Record transaction in accounting system")

        task.action_plan = "\n".join(plan_parts)
        task.action_type = "record_payment"
        task.action_params = {
            "category": categorization.get("category", "Uncategorized"),
            "account": categorization.get("suggested_account", ""),
            "amount": task.source_data.get("amount", 0),
            "reference": task.source_data.get("reference", ""),
        }

        # All financial operations need approval
        if self.approval.requires_approval("record_payment"):
            task_path = self._move_to_needs_approval(task, task_path)
            self.log.info(f"Finance action needs approval: {task.title}")
        else:
            task_path = self._move_to_done(task, task_path)

        return task

    def execute_approved_action(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Execute the approved financial action via Odoo MCP."""
        self.log.info(f"Executing approved finance action: {task.action_type}")
        # In production: invoke odoo_mcp with task.action_params
        task.result = f"Transaction recorded: {task.action_params.get('reference', 'N/A')}"
        task.status = TaskStatus.DONE
        task.touch()
        return task
