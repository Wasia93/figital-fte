"""Filesystem MCP Server - local file operations via FastMCP + stdio."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("filesystem")

# Restrict operations to vault directory for safety
ALLOWED_ROOT = os.environ.get("VAULT_PATH", "vault")


def _safe_path(path: str) -> Path:
    """Ensure path is within the allowed root."""
    resolved = Path(path).resolve()
    root = Path(ALLOWED_ROOT).resolve()
    if not str(resolved).startswith(str(root)):
        raise PermissionError(f"Access denied: {path} is outside allowed root {root}")
    return resolved


@mcp.tool()
def read_file(path: str) -> dict[str, str]:
    """Read a file from the vault.

    Args:
        path: File path (relative to vault or absolute)
    """
    safe = _safe_path(path)
    if not safe.exists():
        return {"error": f"File not found: {path}"}
    content = safe.read_text(encoding="utf-8")
    return {"path": str(safe), "content": content, "size": str(safe.stat().st_size)}


@mcp.tool()
def write_file(path: str, content: str) -> dict[str, str]:
    """Write content to a file in the vault.

    Args:
        path: File path (relative to vault or absolute)
        content: File content to write
    """
    safe = _safe_path(path)
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_text(content, encoding="utf-8")
    return {"status": "written", "path": str(safe), "size": str(len(content))}


@mcp.tool()
def list_directory(path: str, pattern: str = "*") -> list[dict[str, Any]]:
    """List files in a vault directory.

    Args:
        path: Directory path
        pattern: Glob pattern to filter files
    """
    safe = _safe_path(path)
    if not safe.is_dir():
        return [{"error": f"Not a directory: {path}"}]

    entries = []
    for item in sorted(safe.glob(pattern)):
        entries.append({
            "name": item.name,
            "path": str(item),
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else 0,
        })
    return entries


@mcp.tool()
def move_file(source: str, destination: str) -> dict[str, str]:
    """Move a file within the vault.

    Args:
        source: Source file path
        destination: Destination path (file or directory)
    """
    src = _safe_path(source)
    dst = _safe_path(destination)

    if not src.exists():
        return {"error": f"Source not found: {source}"}

    if dst.is_dir():
        dst = dst / src.name

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return {"status": "moved", "from": str(src), "to": str(dst)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
