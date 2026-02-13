"""Filesystem watcher - uses watchdog to detect new files and create TaskItems."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

from src.core.task_item import TaskItem, Priority
from src.core.vault_manager import VaultManager
from src.watchers.base_watcher import BaseWatcher


class _FileHandler(FileSystemEventHandler):
    """Watchdog event handler that queues new file events."""

    def __init__(self, queue: asyncio.Queue[Path], patterns: list[str]):
        self.queue = queue
        self.patterns = patterns

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self.patterns:
            if not any(path.match(p) for p in self.patterns):
                return
        try:
            self.queue.put_nowait(path)
        except asyncio.QueueFull:
            pass


class FilesystemWatcher(BaseWatcher):
    """Watches local filesystem directories for new files."""

    name = "filesystem_watcher"
    poll_interval = 5  # Check queue every 5 seconds

    def __init__(self, vault: VaultManager, config: dict[str, Any] | None = None):
        super().__init__(vault, config)
        self.watch_paths = [Path(p) for p in self.config.get("watch_paths", [])]
        self.file_patterns = self.config.get("file_patterns", [])
        self._queue: asyncio.Queue[Path] = asyncio.Queue(maxsize=1000)
        self._observer: Observer | None = None

    def _start_observer(self) -> None:
        if self._observer is not None:
            return
        self._observer = Observer()
        handler = _FileHandler(self._queue, self.file_patterns)
        for watch_path in self.watch_paths:
            if watch_path.exists():
                self._observer.schedule(handler, str(watch_path), recursive=False)
                self.log.info(f"Watching: {watch_path}")
        self._observer.start()

    async def poll(self) -> list[TaskItem]:
        """Drain the file event queue and create TaskItems."""
        self._start_observer()

        items = []
        while not self._queue.empty():
            try:
                file_path = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            source_id = f"fs_{file_path.name}_{file_path.stat().st_size}"
            if self.is_duplicate(source_id):
                continue

            task = TaskItem(
                title=f"New file: {file_path.name}",
                source="Filesystem",
                source_id=source_id,
                category="General",
                priority=Priority.LOW,
                tags=["file", f"ext:{file_path.suffix}"],
                source_data={
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "suffix": file_path.suffix,
                },
                body=f"**File:** {file_path.name}\n**Path:** {file_path}\n**Size:** {file_path.stat().st_size} bytes",
            )
            items.append(task)

        return items

    def get_target_inbox(self) -> str:
        return self.config.get("target_inbox", "Inbox/Filesystem")

    def stop(self) -> None:
        super().stop()
        if self._observer:
            self._observer.stop()
            self._observer.join()
