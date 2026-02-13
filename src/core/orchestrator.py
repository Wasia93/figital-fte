"""Ralph Wiggum Orchestrator - main dispatch loop for Digital FTE.

Each iteration:
1. Check for EMERGENCY_STOP.md (halt if found)
2. Scan vault directories for item counts
3. Process approved items (Approved/ -> execute via MCP -> Done/)
4. Process rejected items (Rejected/ -> archive to Done/)
5. Triage new inbox items (Inbox/ -> Needs_Action/)
6. Dispatch agents for needs_action items (sorted by priority)
7. Update Dashboard.md
8. Log iteration summary
9. Check completion (all queues empty -> sleep/stop)
"""
from __future__ import annotations

import importlib
import time
from typing import Any

from src.core.agent_base import AgentBase
from src.core.approval_manager import ApprovalManager
from src.core.config_loader import get_setting, load_agents_config
from src.core.logger import get_logger
from src.core.skill_registry import SkillRegistry, build_default_registry
from src.core.task_item import Priority, TaskItem, TaskStatus
from src.core.vault_manager import VaultManager

log = get_logger("orchestrator")


PRIORITY_ORDER = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 1,
    Priority.MEDIUM: 2,
    Priority.LOW: 3,
}


class Orchestrator:
    """The Ralph Wiggum loop - core dispatch engine."""

    def __init__(
        self,
        vault: VaultManager | None = None,
        skill_registry: SkillRegistry | None = None,
    ):
        self.vault = vault or VaultManager()
        self.skills = skill_registry or build_default_registry()
        self.approval = ApprovalManager(self.vault)
        self.agents: list[AgentBase] = []
        self.interval = get_setting("orchestrator", "interval_seconds", default=30)
        self.max_items = get_setting("orchestrator", "max_items_per_iteration", default=10)
        self._running = False
        self._iteration = 0

        self._load_agents()

    def _load_agents(self) -> None:
        """Instantiate all agents defined in agents.yaml."""
        config = load_agents_config()
        for agent_id, agent_cfg in config.get("agents", {}).items():
            try:
                mod = importlib.import_module(agent_cfg["module"])
                cls = getattr(mod, agent_cfg["class"])
                agent = cls(self.vault, self.skills, self.approval)
                self.agents.append(agent)
                log.info(f"Loaded agent: {agent.name}")
            except Exception as e:
                log.error(f"Failed to load agent {agent_id}: {e}")

    def _get_agent_for_task(self, task: TaskItem) -> AgentBase | None:
        """Find the best agent to handle a task."""
        for agent in self.agents:
            if agent.can_handle(task):
                return agent
        return None

    def run_once(self) -> dict[str, Any]:
        """Run a single iteration of the Ralph Wiggum loop."""
        self._iteration += 1
        summary: dict[str, Any] = {"iteration": self._iteration, "actions": []}

        # Step 1: Emergency stop check
        if self.vault.emergency_stop_exists():
            log.warning("EMERGENCY STOP detected! Halting.")
            self._running = False
            summary["emergency_stop"] = True
            return summary

        # Step 2: Get current counts
        counts = self.vault.get_status_counts()
        summary["counts"] = counts
        log.info(f"Iteration {self._iteration} | Counts: {counts}")

        # Step 3: Process approved items
        approved = self.approval.check_approved()
        for path, task in approved:
            try:
                task = self.approval.process_approved(task, path)
                agent = self._get_agent_for_task(task)
                if agent:
                    task = agent.execute_approved_action(task, path)
                    summary["actions"].append(f"Executed approved: {task.title}")
                # Archive
                task.status = TaskStatus.DONE
                task.touch()
                path.write_text(task.to_markdown(), encoding="utf-8")
                self.vault.archive_task(path)
                log.info(f"Approved action executed and archived: {task.title}")
            except Exception as e:
                log.error(f"Error executing approved task {task.id}: {e}")

        # Step 4: Process rejected items
        rejected = self.approval.check_rejected()
        for path, task in rejected:
            try:
                self.approval.process_rejected(task, path)
                summary["actions"].append(f"Archived rejected: {task.title}")
            except Exception as e:
                log.error(f"Error processing rejected task {task.id}: {e}")

        # Step 5: Triage inbox items
        inbox_items = self.vault.get_all_inbox_items()
        triage_agent = next((a for a in self.agents if a.name == "triage_agent"), None)
        triaged = 0
        for path, task in inbox_items[:self.max_items]:
            if triage_agent:
                try:
                    triage_agent.process(task, path)
                    triaged += 1
                except Exception as e:
                    log.error(f"Triage error for {task.id}: {e}")
        if triaged:
            summary["actions"].append(f"Triaged {triaged} inbox items")

        # Step 6: Dispatch agents for needs_action items
        needs_action = self.vault.get_all_needs_action_items()
        # Sort by priority
        needs_action.sort(key=lambda x: PRIORITY_ORDER.get(x[1].priority, 99))
        dispatched = 0
        for path, task in needs_action[:self.max_items]:
            agent = self._get_agent_for_task(task)
            if agent:
                try:
                    task.assigned_agent = agent.name
                    agent.process(task, path)
                    dispatched += 1
                except Exception as e:
                    log.error(f"Agent error for {task.id}: {e}")
        if dispatched:
            summary["actions"].append(f"Dispatched {dispatched} tasks to agents")

        # Step 7: Update dashboard
        try:
            from src.dashboard.dashboard_generator import generate_dashboard
            generate_dashboard(self.vault)
        except Exception as e:
            log.error(f"Dashboard update failed: {e}")

        # Step 8: Log summary
        log.info(f"Iteration {self._iteration} complete: {summary['actions']}")

        return summary

    def run(self, max_iterations: int = 0) -> None:
        """Run the orchestrator loop.

        Args:
            max_iterations: Stop after this many iterations. 0 = run forever.
        """
        self._running = True
        log.info(f"Ralph Wiggum loop starting (interval={self.interval}s, max_items={self.max_items})")

        while self._running:
            summary = self.run_once()

            if summary.get("emergency_stop"):
                break

            if max_iterations > 0 and self._iteration >= max_iterations:
                log.info(f"Reached max iterations ({max_iterations}), stopping.")
                break

            # Check if all queues are empty
            counts = summary.get("counts", {})
            active = sum(counts.get(k, 0) for k in ["inbox", "needs_action", "in_progress", "needs_approval", "approved"])
            if active == 0:
                log.info("All queues empty, sleeping...")

            time.sleep(self.interval)

        log.info("Orchestrator stopped.")

    def stop(self) -> None:
        self._running = False


def main() -> None:
    """Entry point for running the orchestrator."""
    orchestrator = Orchestrator()
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        log.info("Keyboard interrupt, stopping...")
        orchestrator.stop()


if __name__ == "__main__":
    main()
