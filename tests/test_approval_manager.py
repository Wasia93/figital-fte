"""Tests for ApprovalManager - HITL approval workflow."""
import pytest
from pathlib import Path
from src.core.approval_manager import ApprovalManager
from src.core.vault_manager import VaultManager
from src.core.task_item import TaskItem, TaskStatus


@pytest.fixture
def vault(tmp_path):
    vm = VaultManager(tmp_path)
    for d in ["Inbox/Email", "Needs_Action/Email", "In_Progress/Email",
              "Needs_Approval", "Approved", "Rejected", "Done", "Logs"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return vm


@pytest.fixture
def approval(vault):
    return ApprovalManager(vault)


def test_requires_approval_send_email(approval):
    assert approval.requires_approval("send_email") is True


def test_requires_approval_create_draft(approval):
    assert approval.requires_approval("create_draft") is False


def test_requires_approval_unknown_defaults_true(approval):
    assert approval.requires_approval("unknown_action") is True


def test_get_risk_level(approval):
    assert approval.get_risk_level("send_email") == "medium"
    assert approval.get_risk_level("create_post") == "high"
    assert approval.get_risk_level("read_file") == "none"


def test_create_approval_request(vault, approval):
    task = TaskItem(
        title="Send reply to client",
        source="Email",
        action_type="send_email",
        action_params={"to": "client@example.com", "subject": "Re: Invoice"},
    )
    path = vault.write_task(task, "In_Progress", "Email")

    approval_path = approval.create_approval_request(task, path)
    assert approval_path.exists()
    assert "Needs_Approval" in str(approval_path)

    content = approval_path.read_text(encoding="utf-8")
    assert "Approval Required" in content
    assert "send_email" in content
    assert "APPROVE" in content
    assert "REJECT" in content


def test_check_approved(vault, approval):
    task = TaskItem(title="Approved task", status=TaskStatus.NEEDS_APPROVAL)
    vault.write_task(task, "Approved")

    approved = approval.check_approved()
    assert len(approved) == 1
    assert approved[0][1].title == "Approved task"


def test_check_rejected(vault, approval):
    task = TaskItem(title="Rejected task", status=TaskStatus.NEEDS_APPROVAL)
    vault.write_task(task, "Rejected")

    rejected = approval.check_rejected()
    assert len(rejected) == 1
    assert rejected[0][1].title == "Rejected task"


def test_process_rejected_archives(vault, approval):
    task = TaskItem(title="Reject me", status=TaskStatus.NEEDS_APPROVAL)
    path = vault.write_task(task, "Rejected")

    dest = approval.process_rejected(task, path)
    assert dest.exists()
    assert "Done" in str(dest)
    assert not path.exists()


def test_full_approval_flow(vault, approval):
    """Test the complete flow: create request -> approve -> process."""
    # Step 1: Create a task needing approval
    task = TaskItem(
        title="Send email to partner",
        source="Email",
        action_type="send_email",
        action_params={"to": "partner@example.com"},
    )
    in_progress_path = vault.write_task(task, "In_Progress", "Email")

    # Step 2: Create approval request
    approval_path = approval.create_approval_request(task, in_progress_path)
    assert (vault.root / "Needs_Approval").exists()

    # Step 3: Simulate human moving file to Approved
    import shutil
    approved_path = vault.root / "Approved" / approval_path.name
    shutil.move(str(approval_path), str(approved_path))

    # Step 4: Check for approved items
    approved = approval.check_approved()
    assert len(approved) == 1

    # Step 5: Process the approved task
    path, approved_task = approved[0]
    result = approval.process_approved(approved_task, path)
    assert result.status == TaskStatus.APPROVED
