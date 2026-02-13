"""Structured logging to vault/Logs/ and console."""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.core.config_loader import get_vault_path, get_setting


class VaultLogHandler(logging.Handler):
    """Writes log entries as markdown to vault/Logs/YYYY-MM-DD.md."""

    def __init__(self, vault_path: Path | None = None):
        super().__init__()
        self.vault_path = vault_path or get_vault_path()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            now = datetime.now(timezone.utc)
            log_dir = self.vault_path / "Logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{now.strftime('%Y-%m-%d')}.md"

            time_str = now.strftime("%H:%M:%S")
            level = record.levelname
            source = record.name
            message = self.format(record)

            entry = f"- `{time_str}` **{level}** [{source}] {message}\n"

            # Create file with header if new
            if not log_file.exists():
                header = f"# Logs for {now.strftime('%Y-%m-%d')}\n\n"
                log_file.write_text(header, encoding="utf-8")

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass  # Don't let logging failures crash the system


def get_logger(name: str, vault_path: Path | None = None) -> logging.Logger:
    """Create a logger that writes to both console and vault/Logs/."""
    logger = logging.getLogger(f"digital_fte.{name}")

    if logger.handlers:
        return logger

    level_str = get_setting("logging", "level", default="INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(console)

    # Vault handler
    if get_setting("logging", "log_to_vault", default=True):
        vault_handler = VaultLogHandler(vault_path)
        vault_handler.setLevel(level)
        logger.addHandler(vault_handler)

    return logger
