"""Tests for TaskItem model - serialization, deserialization, round-trip."""
import pytest
from src.core.task_item import TaskItem, TaskStatus, Priority


def test_create_default():
    task = TaskItem(title="Test task")
    assert task.title == "Test task"
    assert task.status == TaskStatus.INBOX
    assert task.priority == Priority.MEDIUM
    assert len(task.id) == 12


def test_to_markdown_basic():
    task = TaskItem(
        id="abc123def456",
        title="Test email",
        source="Email",
        status=TaskStatus.INBOX,
        body="Hello world",
    )
    md = task.to_markdown()
    assert "---" in md
    assert "title: Test email" in md
    assert "source: Email" in md
    assert "Hello world" in md


def test_from_markdown_roundtrip():
    original = TaskItem(
        id="test12345678",
        title="Roundtrip test",
        source="Email",
        source_id="msg_123",
        status=TaskStatus.NEEDS_ACTION,
        priority=Priority.HIGH,
        category="Email",
        tags=["urgent", "client"],
        body="This is the body",
        action_plan="Reply to the email",
    )
    md = original.to_markdown()
    restored = TaskItem.from_markdown(md)

    assert restored.id == original.id
    assert restored.title == original.title
    assert restored.source == original.source
    assert restored.source_id == original.source_id
    assert restored.status == original.status
    assert restored.priority == original.priority
    assert restored.category == original.category
    assert restored.tags == original.tags
    assert restored.body == original.body
    assert restored.action_plan == original.action_plan


def test_filename_format():
    task = TaskItem(
        id="abc123def456",
        title="Test Email Subject!",
        created_at="2024-06-15T10:30:00+00:00",
    )
    fn = task.filename()
    assert fn.startswith("2024-06-15_1030")
    assert "abc123def456" in fn
    assert fn.endswith(".md")
    # No special characters in filename
    assert "!" not in fn


def test_from_markdown_no_frontmatter():
    with pytest.raises(ValueError, match="no frontmatter"):
        TaskItem.from_markdown("Just plain text without frontmatter")


def test_touch_updates_timestamp():
    task = TaskItem(title="Test")
    old_updated = task.updated_at
    import time
    time.sleep(0.01)
    task.touch()
    assert task.updated_at != old_updated


def test_save_and_load(tmp_path):
    task = TaskItem(
        title="Save test",
        source="Email",
        body="Test body content",
    )
    saved_path = task.save(tmp_path)
    assert saved_path.exists()

    loaded = TaskItem.from_file(saved_path)
    assert loaded.title == "Save test"
    assert loaded.source == "Email"
    assert loaded.body == "Test body content"


def test_source_data_serialization():
    task = TaskItem(
        title="With metadata",
        source_data={"from": "user@example.com", "thread_id": "t123"},
    )
    md = task.to_markdown()
    restored = TaskItem.from_markdown(md)
    assert restored.source_data["from"] == "user@example.com"
    assert restored.source_data["thread_id"] == "t123"


def test_action_params_serialization():
    task = TaskItem(
        title="With action",
        action_type="send_email",
        action_params={"to": "user@example.com", "subject": "Test"},
    )
    md = task.to_markdown()
    restored = TaskItem.from_markdown(md)
    assert restored.action_type == "send_email"
    assert restored.action_params["to"] == "user@example.com"
