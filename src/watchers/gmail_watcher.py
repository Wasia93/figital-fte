"""Gmail API watcher - polls for new emails and creates TaskItems."""
from __future__ import annotations

import base64
import os
from typing import Any

from src.core.task_item import TaskItem, Priority
from src.core.vault_manager import VaultManager
from src.watchers.base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new emails using the Gmail API."""

    name = "gmail_watcher"
    poll_interval = 60

    def __init__(self, vault: VaultManager, config: dict[str, Any] | None = None):
        super().__init__(vault, config)
        self._service = None
        self._last_history_id: str | None = None
        self.max_results = self.config.get("max_results_per_poll", 20)

    def _get_service(self) -> Any:
        """Build Gmail API service with OAuth2 credentials."""
        if self._service is not None:
            return self._service

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")

        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as f:
                f.write(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    async def poll(self) -> list[TaskItem]:
        """Poll Gmail for new unread messages."""
        try:
            service = self._get_service()
        except Exception as e:
            self.log.error(f"Failed to connect to Gmail: {e}")
            return []

        try:
            results = service.users().messages().list(
                userId="me", q="is:unread", maxResults=self.max_results
            ).execute()
            messages = results.get("messages", [])
        except Exception as e:
            self.log.error(f"Failed to list messages: {e}")
            return []

        items = []
        for msg_meta in messages:
            msg_id = msg_meta["id"]
            if self.is_duplicate(msg_id):
                continue

            try:
                msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
                task = self._message_to_task(msg)
                items.append(task)
            except Exception as e:
                self.log.error(f"Failed to fetch message {msg_id}: {e}")

        return items

    def _message_to_task(self, msg: dict[str, Any]) -> TaskItem:
        """Convert a Gmail API message to a TaskItem."""
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        subject = headers.get("subject", "(No Subject)")
        sender = headers.get("from", "unknown")
        date = headers.get("date", "")
        to = headers.get("to", "")

        # Extract body
        body = self._extract_body(msg.get("payload", {}))

        # Determine priority from labels
        labels = msg.get("labelIds", [])
        priority = Priority.MEDIUM
        if "IMPORTANT" in labels:
            priority = Priority.HIGH

        return TaskItem(
            title=subject,
            source="Email",
            source_id=msg["id"],
            category="Email",
            priority=priority,
            tags=[f"from:{sender}"],
            source_data={
                "from": sender,
                "to": to,
                "date": date,
                "labels": labels,
                "thread_id": msg.get("threadId", ""),
                "message_id": msg["id"],
            },
            body=f"**From:** {sender}\n**Date:** {date}\n**To:** {to}\n\n---\n\n{body}",
        )

    def _extract_body(self, payload: dict[str, Any]) -> str:
        """Extract plain text body from Gmail message payload."""
        if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        parts = payload.get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            # Recurse into multipart
            if part.get("parts"):
                result = self._extract_body(part)
                if result:
                    return result

        return "(No text body)"

    def get_target_inbox(self) -> str:
        return self.config.get("target_inbox", "Inbox/Email")
