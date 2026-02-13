"""Tests for VaultManager - file operations on the markdown vault."""
import pytest
from pathlib import Path
from src.core.vault_manager import VaultManager
from src.core.task_item import TaskItem, TaskStatus, Priority


@pytest.fixture
def vault(tmp_path):
    """Create a VaultManager with a temporary vault directory."""
    vm = VaultManager(tmp_path)
    # Create standard directories
    for d in ["Inbox/Email", "Inbox/WhatsApp", "Needs_Action/Email", "Needs_Action/Finance",
              "Needs_Action/General", "In_Progress/Email", "Needs_Approval", "Approved",
              "Rejected", "Done", "Logs"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return vm


def test_write_and_read_task(vault):
    task = TaskItem(title="Test task", source="Email", body="Hello")
    path = vault.write_task(task, "Inbox", "Email")
    assert path.exists()

    loaded = vault.read_task(path)
    assert loaded.title == "Test task"
    assert loaded.source == "Email"


def test_list_items(vault):
    # Create some files
    for i in range(3):
        task = TaskItem(title=f"Task {i}", source="Email")
        vault.write_task(task, "Inbox", "Email")

    items = vault.list_items("Inbox", "Email")
    assert len(items) == 3


def test_list_items_recursive(vault):
    vault.write_task(TaskItem(title="Email task"), "Inbox", "Email")
    vault.write_task(TaskItem(title="WhatsApp task"), "Inbox", "WhatsApp")

    items = vault.list_items_recursive("Inbox")
    assert len(items) == 2


def test_count_items(vault):
    for i in range(5):
        vault.write_task(TaskItem(title=f"Task {i}"), "Inbox", "Email")
    assert vault.count_items("Inbox") == 5


def test_move_task(vault):
    task = TaskItem(title="Move me", source="Email")
    path = vault.write_task(task, "Inbox", "Email")
    assert path.exists()

    new_path = vault.move_task(path, "Needs_Action", "Email")
    assert new_path.exists()
    assert not path.exists()
    assert "Needs_Action" in str(new_path)


def test_archive_task(vault):
    task = TaskItem(title="Archive me")
    path = vault.write_task(task, "Needs_Action", "Email")

    archived = vault.archive_task(path)
    assert archived.exists()
    assert not path.exists()
    assert "Done" in str(archived)


def test_search(vault):
    vault.write_task(TaskItem(title="Invoice from Acme", body="Please pay invoice #123"), "Inbox", "Email")
    vault.write_task(TaskItem(title="Meeting tomorrow", body="Let's meet at 3pm"), "Inbox", "Email")

    results = vault.search("invoice", "Inbox")
    assert len(results) == 1
    assert "Invoice" in results[0].stem or "invoice" in results[0].read_text(encoding="utf-8").lower()


def test_write_raw(vault):
    path = vault.write_raw("# Test Content\n\nHello world", "test_file.md")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# Test Content\n\nHello world"


def test_get_status_counts(vault):
    vault.write_task(TaskItem(title="Inbox 1"), "Inbox", "Email")
    vault.write_task(TaskItem(title="Inbox 2"), "Inbox", "Email")
    vault.write_task(TaskItem(title="Action 1"), "Needs_Action", "Email")

    counts = vault.get_status_counts()
    assert counts["inbox"] == 2
    assert counts["needs_action"] == 1


def test_emergency_stop(vault):
    assert not vault.emergency_stop_exists()
    (vault.root / "EMERGENCY_STOP.md").write_text("STOP!", encoding="utf-8")
    assert vault.emergency_stop_exists()


def test_get_all_inbox_items(vault):
    vault.write_task(TaskItem(title="Email 1", source="Email"), "Inbox", "Email")
    vault.write_task(TaskItem(title="WA 1", source="WhatsApp"), "Inbox", "WhatsApp")

    items = vault.get_all_inbox_items()
    assert len(items) == 2
    titles = {t.title for _, t in items}
    assert "Email 1" in titles
    assert "WA 1" in titles


def test_parse_frontmatter(vault):
    text = "---\ntitle: Test\npriority: high\n---\n\nBody content"
    fm = VaultManager.parse_frontmatter(text)
    assert fm["title"] == "Test"
    assert fm["priority"] == "high"
