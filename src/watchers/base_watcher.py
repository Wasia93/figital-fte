"""Abstract base class for all watchers (polling loops)."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from src.core.logger import get_logger
from src.core.task_item import TaskItem
from src.core.vault_manager import VaultManager


class BaseWatcher(ABC):
    """Base class for watchers that poll external sources and create TaskItems."""

    name: str = "base_watcher"
    poll_interval: int = 60  # seconds

    def __init__(self, vault: VaultManager, config: dict[str, Any] | None = None):
        self.vault = vault
        self.config = config or {}
        self.poll_interval = self.config.get("poll_interval_seconds", self.poll_interval)
        self.log = get_logger(self.name)
        self._seen_ids: set[str] = set()
        self._running = False

    @abstractmethod
    async def poll(self) -> list[TaskItem]:
        """Poll the external source and return new TaskItems.

        Implementations should:
        1. Connect to the external source
        2. Fetch new items since last poll
        3. Convert to TaskItem objects
        4. Return only truly new items (dedup)
        """
        ...

    @abstractmethod
    def get_target_inbox(self) -> str:
        """Return the inbox subdirectory (e.g., 'Inbox/Email')."""
        ...

    def is_duplicate(self, source_id: str) -> bool:
        """Check if we've already seen this source item."""
        if source_id in self._seen_ids:
            return True
        # Also check if a file with this source_id exists in inbox
        inbox_path = self.vault.root / self.get_target_inbox()
        if inbox_path.exists():
            for f in inbox_path.glob("*.md"):
                try:
                    task = TaskItem.from_file(f)
                    if task.source_id == source_id:
                        self._seen_ids.add(source_id)
                        return True
                except Exception:
                    continue
        return False

    def mark_seen(self, source_id: str) -> None:
        self._seen_ids.add(source_id)

    async def run(self) -> None:
        """Main polling loop."""
        self._running = True
        self.log.info(f"{self.name} started (interval: {self.poll_interval}s)")

        while self._running:
            try:
                items = await self.poll()
                for item in items:
                    if not self.is_duplicate(item.source_id):
                        target = self.get_target_inbox()
                        parts = target.split("/")
                        item.save(self.vault.root / target)
                        self.mark_seen(item.source_id)
                        self.log.info(f"New item: {item.title} -> {target}")
                if items:
                    self.log.info(f"Polled {len(items)} new items")
            except Exception as e:
                self.log.error(f"Poll error: {e}")

            await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        self._running = False
        self.log.info(f"{self.name} stopped")
