"""WhatsApp MCP Server - messaging via FastMCP + stdio."""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("whatsapp")


def _api_url() -> str:
    base = os.environ.get("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
    phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    return f"{base}/{phone_id}"


def _headers() -> dict[str, str]:
    token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@mcp.tool()
def send_message(to: str, message: str) -> dict[str, str]:
    """Send a WhatsApp text message.

    Args:
        to: Recipient phone number (with country code, e.g., +27123456789)
        message: Message text
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    resp = httpx.post(f"{_api_url()}/messages", json=payload, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    msg_id = data.get("messages", [{}])[0].get("id", "")
    return {"status": "sent", "message_id": msg_id}


@mcp.tool()
def get_messages(limit: int = 20) -> list[dict[str, Any]]:
    """Get recent WhatsApp messages.

    Args:
        limit: Maximum number of messages to retrieve
    """
    resp = httpx.get(f"{_api_url()}/messages", headers=_headers(), params={"limit": limit})
    resp.raise_for_status()
    messages = resp.json().get("messages", [])
    return [
        {
            "id": m.get("id", ""),
            "from": m.get("from", ""),
            "type": m.get("type", ""),
            "text": m.get("text", {}).get("body", ""),
            "timestamp": m.get("timestamp", ""),
        }
        for m in messages
    ]


@mcp.tool()
def send_template(to: str, template_name: str, language: str = "en_US", parameters: list[str] | None = None) -> dict[str, str]:
    """Send a WhatsApp template message.

    Args:
        to: Recipient phone number
        template_name: Name of the pre-approved template
        language: Template language code
        parameters: Template parameter values
    """
    components = []
    if parameters:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in parameters],
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": components,
        },
    }
    resp = httpx.post(f"{_api_url()}/messages", json=payload, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    msg_id = data.get("messages", [{}])[0].get("id", "")
    return {"status": "sent", "message_id": msg_id, "template": template_name}


if __name__ == "__main__":
    mcp.run(transport="stdio")
