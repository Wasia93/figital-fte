"""WhatsApp Business API watcher - polls for new messages."""
from __future__ import annotations

import os
from typing import Any

import httpx

from src.core.task_item import TaskItem, Priority
from src.core.vault_manager import VaultManager
from src.watchers.base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Business API for new messages."""

    name = "whatsapp_watcher"
    poll_interval = 30

    def __init__(self, vault: VaultManager, config: dict[str, Any] | None = None):
        super().__init__(vault, config)
        self.api_url = os.environ.get("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
        self.phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")

    async def poll(self) -> list[TaskItem]:
        """Poll WhatsApp Business API for new messages."""
        if not self.phone_number_id or not self.access_token:
            self.log.warning("WhatsApp credentials not configured")
            return []

        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{self.phone_number_id}/messages"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            self.log.error(f"WhatsApp API error: {e}")
            return []

        items = []
        for msg in data.get("messages", []):
            msg_id = msg.get("id", "")
            if self.is_duplicate(msg_id):
                continue

            sender = msg.get("from", "unknown")
            text = msg.get("text", {}).get("body", "")
            timestamp = msg.get("timestamp", "")

            task = TaskItem(
                title=f"WhatsApp from {sender}",
                source="WhatsApp",
                source_id=msg_id,
                category="Email",  # Routed same as email for now
                priority=Priority.MEDIUM,
                tags=[f"from:{sender}"],
                source_data={
                    "from": sender,
                    "timestamp": timestamp,
                    "message_id": msg_id,
                    "type": msg.get("type", "text"),
                },
                body=f"**From:** {sender}\n**Time:** {timestamp}\n\n---\n\n{text}",
            )
            items.append(task)

        return items

    def get_target_inbox(self) -> str:
        return self.config.get("target_inbox", "Inbox/WhatsApp")
