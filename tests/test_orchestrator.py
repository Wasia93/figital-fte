"""Tests for the Orchestrator - Ralph Wiggum loop."""
import pytest
from pathlib import Path
from src.core.orchestrator import Orchestrator
from src.core.vault_manager import VaultManager
from src.core.task_item import TaskItem, TaskStatus, Priority
from src.core.skill_registry import build_default_registry


@pytest.fixture
def vault(tmp_path):
    vm = VaultManager(tmp_path)
    for d in ["Inbox/Email", "Inbox/WhatsApp", "Inbox/Banking", "Inbox/Filesystem",
              "Needs_Action/Email", "Needs_Action/Social", "Needs_Action/Finance",
              "Needs_Action/General", "In_Progress/Email", "In_Progress/Social",
              "In_Progress/Finance", "In_Progress/General",
              "Needs_Approval", "Approved", "Rejected", "Done", "Logs"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return vm


@pytest.fixture
def orchestrator(vault):
    return Orchestrator(vault=vault, skill_registry=build_default_registry())


def test_emergency_stop(vault, orchestrator):
    (vault.root / "EMERGENCY_STOP.md").write_text("STOP", encoding="utf-8")
    summary = orchestrator.run_once()
    assert summary.get("emergency_stop") is True


def test_run_once_empty_vault(orchestrator):
    summary = orchestrator.run_once()
    assert summary["iteration"] == 1
    counts = summary["counts"]
    assert counts["inbox"] == 0
    assert counts["needs_action"] == 0


def test_triage_inbox_item(vault, orchestrator):
    task = TaskItem(
        title="Test email from client",
        source="Email",
        source_id="msg_001",
        body="Please send the invoice for last month",
    )
    vault.write_task(task, "Inbox", "Email")
    assert vault.count_items("Inbox") == 1

    orchestrator.run_once()

    # Item should have moved out of inbox
    # (either to Needs_Action or Done depending on classification)
    assert vault.count_items("Inbox") == 0


def test_process_approved_item(vault, orchestrator):
    task = TaskItem(
        title="Send reply to vendor",
        source="Email",
        status=TaskStatus.APPROVED,
        category="Email",
        action_type="send_email",
        action_params={"to": "vendor@example.com", "subject": "Re: Quote"},
    )
    vault.write_task(task, "Approved")
    assert vault.count_items("Approved") == 1

    orchestrator.run_once()

    # Approved item should be archived to Done
    assert vault.count_items("Approved") == 0
    assert vault.count_items("Done") >= 1


def test_process_rejected_item(vault, orchestrator):
    task = TaskItem(
        title="Rejected post",
        source="Manual",
        status=TaskStatus.REJECTED,
        category="Social",
    )
    vault.write_task(task, "Rejected")

    orchestrator.run_once()

    assert vault.count_items("Rejected") == 0
    assert vault.count_items("Done") >= 1


def test_dashboard_generated(vault, orchestrator):
    orchestrator.run_once()
    dashboard = vault.root / "Dashboard.md"
    assert dashboard.exists()
    content = dashboard.read_text(encoding="utf-8")
    assert "Dashboard" in content
    assert "Queue Status" in content


def test_max_iterations(vault, orchestrator):
    orchestrator.interval = 0  # No sleep
    orchestrator.run(max_iterations=3)
    assert orchestrator._iteration == 3


def test_multiple_inbox_items_triaged(vault, orchestrator):
    for i in range(5):
        vault.write_task(
            TaskItem(title=f"Email {i}", source="Email", source_id=f"msg_{i}"),
            "Inbox", "Email",
        )
    assert vault.count_items("Inbox") == 5

    orchestrator.run_once()

    assert vault.count_items("Inbox") == 0
