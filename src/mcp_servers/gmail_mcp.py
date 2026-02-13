"""Gmail MCP Server - send/reply/search emails via FastMCP + stdio."""
from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gmail")


def _get_service() -> Any:
    """Build authenticated Gmail API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
    ]
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token_gmail_mcp.json")

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

    return build("gmail", "v1", credentials=creds)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict[str, str]:
    """Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text
    """
    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return {"status": "sent", "message_id": result.get("id", "")}


@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> dict[str, str]:
    """Create an email draft in Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text
    """
    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return {"status": "draft_created", "draft_id": result.get("id", "")}


@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search emails in Gmail.

    Args:
        query: Gmail search query (e.g., 'from:user@example.com subject:invoice')
        max_results: Maximum number of results to return
    """
    service = _get_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])

    output = []
    for msg_meta in messages:
        msg = service.users().messages().get(userId="me", id=msg_meta["id"], format="metadata").execute()
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        output.append({
            "id": msg_meta["id"],
            "subject": headers.get("subject", ""),
            "from": headers.get("from", ""),
            "date": headers.get("date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return output


@mcp.tool()
def get_email_thread(thread_id: str) -> list[dict[str, str]]:
    """Get all messages in an email thread.

    Args:
        thread_id: Gmail thread ID
    """
    service = _get_service()
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    messages = []
    for msg in thread.get("messages", []):
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        messages.append({
            "id": msg["id"],
            "subject": headers.get("subject", ""),
            "from": headers.get("from", ""),
            "date": headers.get("date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return messages


if __name__ == "__main__":
    mcp.run(transport="stdio")
