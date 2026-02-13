"""TaskItem dataclass with YAML frontmatter + markdown serialization."""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    INBOX = "inbox"
    NEEDS_ACTION = "needs_action"
    IN_PROGRESS = "in_progress"
    NEEDS_APPROVAL = "needs_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DONE = "done"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskItem(BaseModel):
    """A single work item flowing through the Digital FTE pipeline."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    source: str = ""  # Email, WhatsApp, Banking, Filesystem, Manual
    source_id: str = ""  # Dedup key (e.g. Gmail message ID)
    status: TaskStatus = TaskStatus.INBOX
    priority: Priority = Priority.MEDIUM
    assigned_agent: str = ""
    category: str = ""  # Email, Social, Finance, General
    tags: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_data: dict[str, Any] = Field(default_factory=dict)
    body: str = ""
    approval_required: bool = False
    action_plan: str = ""
    action_type: str = ""  # The MCP tool to call (e.g. send_email)
    action_params: dict[str, Any] = Field(default_factory=dict)
    result: str = ""
    error: str = ""

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def filename(self) -> str:
        """Generate filesystem-safe filename."""
        ts = datetime.fromisoformat(self.created_at)
        date_part = ts.strftime("%Y-%m-%d_%H%M")
        slug = re.sub(r"[^\w\s-]", "", self.title.lower())
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")[:50]
        return f"{date_part}_{self.id}_{slug}.md"

    def to_markdown(self) -> str:
        """Serialize to YAML frontmatter + markdown body."""
        frontmatter = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "source_id": self.source_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_agent": self.assigned_agent,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "approval_required": self.approval_required,
            "action_type": self.action_type,
        }
        if self.source_data:
            frontmatter["source_data"] = self.source_data
        if self.action_params:
            frontmatter["action_params"] = self.action_params
        if self.result:
            frontmatter["result"] = self.result
        if self.error:
            frontmatter["error"] = self.error

        fm_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
        parts = [f"---\n{fm_str}---\n"]
        if self.body:
            parts.append(f"\n{self.body}\n")
        if self.action_plan:
            parts.append(f"\n## Action Plan\n\n{self.action_plan}\n")
        return "".join(parts)

    @classmethod
    def from_markdown(cls, text: str) -> TaskItem:
        """Deserialize from YAML frontmatter + markdown body."""
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
        if not fm_match:
            raise ValueError("Invalid TaskItem markdown: no frontmatter found")

        fm_raw = fm_match.group(1)
        rest = fm_match.group(2).strip()
        data = yaml.safe_load(fm_raw) or {}

        # Extract body and action_plan from markdown body
        body = rest
        action_plan = ""
        ap_match = re.split(r"\n## Action Plan\s*\n", rest, maxsplit=1)
        if len(ap_match) == 2:
            body = ap_match[0].strip()
            action_plan = ap_match[1].strip()

        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            title=data.get("title", ""),
            source=data.get("source", ""),
            source_id=data.get("source_id", ""),
            status=TaskStatus(data.get("status", "inbox")),
            priority=Priority(data.get("priority", "medium")),
            assigned_agent=data.get("assigned_agent", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            source_data=data.get("source_data", {}),
            body=body,
            approval_required=data.get("approval_required", False),
            action_type=data.get("action_type", ""),
            action_params=data.get("action_params", {}),
            action_plan=action_plan,
            result=data.get("result", ""),
            error=data.get("error", ""),
        )

    @classmethod
    def from_file(cls, path: Path) -> TaskItem:
        """Load TaskItem from a markdown file."""
        text = path.read_text(encoding="utf-8")
        return cls.from_markdown(text)

    def save(self, directory: Path) -> Path:
        """Write this TaskItem to a markdown file in the given directory."""
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / self.filename()
        path.write_text(self.to_markdown(), encoding="utf-8")
        return path
