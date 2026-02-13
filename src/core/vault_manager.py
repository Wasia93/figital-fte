"""Read/write/move/archive/search operations on the markdown vault."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.core.config_loader import get_vault_path
from src.core.task_item import TaskItem, TaskStatus


class VaultManager:
    """Manages all file operations within the Obsidian vault."""

    def __init__(self, vault_path: Path | None = None):
        self.root = vault_path or get_vault_path()

    # -- Directory helpers --

    def _dir(self, *parts: str) -> Path:
        d = self.root.joinpath(*parts)
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def inbox_dir(self) -> Path:
        return self._dir("Inbox")

    @property
    def needs_action_dir(self) -> Path:
        return self._dir("Needs_Action")

    @property
    def in_progress_dir(self) -> Path:
        return self._dir("In_Progress")

    @property
    def needs_approval_dir(self) -> Path:
        return self._dir("Needs_Approval")

    @property
    def approved_dir(self) -> Path:
        return self._dir("Approved")

    @property
    def rejected_dir(self) -> Path:
        return self._dir("Rejected")

    @property
    def done_dir(self) -> Path:
        return self._dir("Done")

    @property
    def logs_dir(self) -> Path:
        return self._dir("Logs")

    # -- List items --

    def list_items(self, *subpath: str) -> list[Path]:
        """List all .md files in a vault subdirectory (non-recursive by default)."""
        d = self.root.joinpath(*subpath)
        if not d.exists():
            return []
        return sorted(p for p in d.glob("*.md") if p.is_file() and not p.name.startswith("."))

    def list_items_recursive(self, *subpath: str) -> list[Path]:
        """List all .md files recursively under a vault subdirectory."""
        d = self.root.joinpath(*subpath)
        if not d.exists():
            return []
        return sorted(p for p in d.rglob("*.md") if p.is_file() and not p.name.startswith("."))

    def count_items(self, *subpath: str) -> int:
        return len(self.list_items_recursive(*subpath))

    # -- Read / Write --

    def read_task(self, path: Path) -> TaskItem:
        return TaskItem.from_file(path)

    def write_task(self, task: TaskItem, *subpath: str) -> Path:
        directory = self.root.joinpath(*subpath)
        return task.save(directory)

    def read_raw(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def write_raw(self, content: str, *subpath_and_filename: str) -> Path:
        parts = list(subpath_and_filename)
        filename = parts[-1]
        directory = self.root.joinpath(*parts[:-1])
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / filename
        path.write_text(content, encoding="utf-8")
        return path

    # -- Move / Archive --

    def move_task(self, source_path: Path, *dest_subpath: str) -> Path:
        """Move a task file to a new vault subdirectory."""
        dest_dir = self.root.joinpath(*dest_subpath)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / source_path.name
        shutil.move(str(source_path), str(dest))
        return dest

    def archive_task(self, source_path: Path) -> Path:
        """Move a task to Done/YYYY/MM/."""
        now = datetime.now(timezone.utc)
        archive_dir = self.done_dir / str(now.year) / f"{now.month:02d}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / source_path.name
        shutil.move(str(source_path), str(dest))
        return dest

    # -- Search --

    def search(self, query: str, *subpath: str) -> list[Path]:
        """Simple text search across .md files in a subdirectory."""
        results = []
        q_lower = query.lower()
        for path in self.list_items_recursive(*subpath):
            try:
                content = path.read_text(encoding="utf-8").lower()
                if q_lower in content:
                    results.append(path)
            except Exception:
                continue
        return results

    # -- Frontmatter parsing --

    @staticmethod
    def parse_frontmatter(text: str) -> dict[str, Any]:
        """Extract YAML frontmatter from markdown text."""
        import re
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            return {}
        return yaml.safe_load(match.group(1)) or {}

    # -- Convenience --

    def get_all_inbox_items(self) -> list[tuple[Path, TaskItem]]:
        """Load all tasks from all Inbox subdirs."""
        items = []
        for path in self.list_items_recursive("Inbox"):
            try:
                items.append((path, self.read_task(path)))
            except Exception:
                continue
        return items

    def get_all_needs_action_items(self) -> list[tuple[Path, TaskItem]]:
        items = []
        for path in self.list_items_recursive("Needs_Action"):
            try:
                items.append((path, self.read_task(path)))
            except Exception:
                continue
        return items

    def get_all_approved_items(self) -> list[tuple[Path, TaskItem]]:
        items = []
        for path in self.list_items_recursive("Approved"):
            try:
                items.append((path, self.read_task(path)))
            except Exception:
                continue
        return items

    def get_all_rejected_items(self) -> list[tuple[Path, TaskItem]]:
        items = []
        for path in self.list_items_recursive("Rejected"):
            try:
                items.append((path, self.read_task(path)))
            except Exception:
                continue
        return items

    def emergency_stop_exists(self) -> bool:
        return (self.root / "EMERGENCY_STOP.md").exists()

    def get_status_counts(self) -> dict[str, int]:
        return {
            "inbox": self.count_items("Inbox"),
            "needs_action": self.count_items("Needs_Action"),
            "in_progress": self.count_items("In_Progress"),
            "needs_approval": self.count_items("Needs_Approval"),
            "approved": self.count_items("Approved"),
            "rejected": self.count_items("Rejected"),
            "done": self.count_items("Done"),
        }
