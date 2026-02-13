"""Async process manager that starts and manages all enabled watchers."""
from __future__ import annotations

import asyncio
import importlib
from typing import Any

from src.core.config_loader import load_watchers_config
from src.core.logger import get_logger
from src.core.vault_manager import VaultManager
from src.watchers.base_watcher import BaseWatcher

log = get_logger("watcher_runner")


def _load_watcher_class(module_path: str, class_name: str) -> type[BaseWatcher]:
    """Dynamically import a watcher class."""
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def build_watchers(vault: VaultManager) -> list[BaseWatcher]:
    """Instantiate all enabled watchers from config."""
    config = load_watchers_config()
    watchers = []
    for name, watcher_cfg in config.get("watchers", {}).items():
        if not watcher_cfg.get("enabled", False):
            log.info(f"Skipping disabled watcher: {name}")
            continue
        try:
            cls = _load_watcher_class(watcher_cfg["module"], watcher_cfg["class"])
            watcher = cls(vault, watcher_cfg)
            watchers.append(watcher)
            log.info(f"Loaded watcher: {name} ({cls.__name__})")
        except Exception as e:
            log.error(f"Failed to load watcher {name}: {e}")
    return watchers


async def run_all_watchers(vault: VaultManager | None = None) -> None:
    """Start all enabled watchers concurrently."""
    if vault is None:
        vault = VaultManager()

    watchers = build_watchers(vault)
    if not watchers:
        log.warning("No watchers enabled")
        return

    tasks = [asyncio.create_task(w.run()) for w in watchers]
    log.info(f"Started {len(tasks)} watcher(s)")

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log.info("Watchers cancelled")
        for w in watchers:
            w.stop()


if __name__ == "__main__":
    asyncio.run(run_all_watchers())
