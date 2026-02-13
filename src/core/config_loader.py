"""Load and provide access to all YAML configuration files."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def _load_yaml(filename: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_settings() -> dict[str, Any]:
    return _load_yaml("settings.yaml")


@lru_cache(maxsize=1)
def load_agents_config() -> dict[str, Any]:
    return _load_yaml("agents.yaml")


@lru_cache(maxsize=1)
def load_watchers_config() -> dict[str, Any]:
    return _load_yaml("watchers.yaml")


@lru_cache(maxsize=1)
def load_mcp_servers_config() -> dict[str, Any]:
    return _load_yaml("mcp_servers.yaml")


@lru_cache(maxsize=1)
def load_safety_rules() -> dict[str, Any]:
    return _load_yaml("safety_rules.yaml")


def get_vault_path() -> Path:
    """Return the vault root path from env or config."""
    env_path = os.environ.get("VAULT_PATH")
    if env_path:
        return Path(env_path)
    settings = load_settings()
    return Path(settings.get("vault", {}).get("path", "vault"))


def get_setting(*keys: str, default: Any = None) -> Any:
    """Nested key lookup in settings. e.g. get_setting('orchestrator', 'interval_seconds')"""
    settings = load_settings()
    current = settings
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current
