"""Abstract base class for all Digital FTE agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.logger import get_logger
from src.core.task_item import TaskItem, TaskStatus

if TYPE_CHECKING:
    from src.core.approval_manager import ApprovalManager
    from src.core.skill_registry import SkillRegistry
    from src.core.vault_manager import VaultManager


class AgentBase(ABC):
    """Base class for all agents in the Digital FTE system.

    Each agent:
    - Has a name and list of skills it can use
    - Processes TaskItems from its assigned queue
    - Can request human approval for risky actions
    - Logs its actions to the vault
    """

    name: str = "base_agent"

    def __init__(
        self,
        vault: VaultManager,
        skill_registry: SkillRegistry,
        approval_manager: ApprovalManager,
    ):
        self.vault = vault
        self.skills = skill_registry
        self.approval = approval_manager
        self.log = get_logger(self.name)

    @abstractmethod
    def can_handle(self, task: TaskItem) -> bool:
        """Return True if this agent can process the given task."""
        ...

    @abstractmethod
    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Process a task item. Returns the updated task.

        The agent should:
        1. Analyze the task
        2. Decide on actions
        3. If action needs approval, set task.approval_required = True and
           populate action_plan, action_type, action_params
        4. If action is safe, execute directly and set result
        5. Update task status accordingly
        """
        ...

    def execute_approved_action(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Execute an action that has been approved by a human.

        Default implementation logs a message. Override in subclasses
        that interact with MCP servers.
        """
        self.log.info(f"Executing approved action: {task.action_type} for task {task.id}")
        task.status = TaskStatus.DONE
        task.touch()
        return task

    def _move_to_in_progress(self, task: TaskItem, task_path: Path) -> Path:
        """Move task to In_Progress directory."""
        task.status = TaskStatus.IN_PROGRESS
        task.touch()
        category = task.category or "General"
        new_path = self.vault.move_task(task_path, "In_Progress", category)
        # Rewrite with updated status
        new_path.write_text(task.to_markdown(), encoding="utf-8")
        return new_path

    def _move_to_needs_approval(self, task: TaskItem, task_path: Path) -> Path:
        """Move task to Needs_Approval directory."""
        task.status = TaskStatus.NEEDS_APPROVAL
        task.approval_required = True
        task.touch()
        new_path = self.vault.move_task(task_path, "Needs_Approval")
        new_path.write_text(task.to_markdown(), encoding="utf-8")
        return new_path

    def _move_to_done(self, task: TaskItem, task_path: Path) -> Path:
        """Archive task to Done directory."""
        task.status = TaskStatus.DONE
        task.touch()
        # Write updated content before archiving
        task_path.write_text(task.to_markdown(), encoding="utf-8")
        return self.vault.archive_task(task_path)
