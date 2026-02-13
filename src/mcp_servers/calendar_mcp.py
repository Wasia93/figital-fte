"""Google Calendar MCP Server - events and availability via FastMCP + stdio."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calendar")


def _get_service() -> Any:
    """Build authenticated Google Calendar API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token_calendar_mcp.json")

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

    return build("calendar", "v3", credentials=creds)


@mcp.tool()
def get_events(
    days_ahead: int = 7,
    max_results: int = 20,
    calendar_id: str = "primary",
) -> list[dict[str, str]]:
    """Get upcoming calendar events.

    Args:
        days_ahead: Number of days to look ahead
        max_results: Maximum events to return
        calendar_id: Calendar ID (default: primary)
    """
    service = _get_service()
    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=days_ahead)

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now.isoformat(),
        timeMax=time_max.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    return [
        {
            "id": e.get("id", ""),
            "summary": e.get("summary", ""),
            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
            "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date", "")),
            "location": e.get("location", ""),
            "status": e.get("status", ""),
        }
        for e in events
    ]


@mcp.tool()
def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendees: list[str] | None = None,
    location: str = "",
    calendar_id: str = "primary",
) -> dict[str, str]:
    """Create a calendar event.

    Args:
        summary: Event title
        start_time: Start time in ISO format (e.g., 2024-01-15T10:00:00+02:00)
        end_time: End time in ISO format
        description: Event description
        attendees: List of attendee email addresses
        location: Event location
        calendar_id: Calendar ID (default: primary)
    """
    service = _get_service()
    event = {
        "summary": summary,
        "description": description,
        "location": location,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }
    if attendees:
        event["attendees"] = [{"email": a} for a in attendees]

    result = service.events().insert(calendarId=calendar_id, body=event).execute()
    return {
        "status": "created",
        "event_id": result.get("id", ""),
        "link": result.get("htmlLink", ""),
    }


@mcp.tool()
def check_availability(
    date: str,
    duration_minutes: int = 60,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Check availability for a given date.

    Args:
        date: Date to check (YYYY-MM-DD)
        duration_minutes: Desired meeting duration in minutes
        calendar_id: Calendar ID (default: primary)
    """
    service = _get_service()
    start = datetime.fromisoformat(f"{date}T08:00:00")
    end = datetime.fromisoformat(f"{date}T18:00:00")

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start.isoformat() + "Z",
        timeMax=end.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    busy_slots = []
    for e in events:
        busy_slots.append({
            "start": e.get("start", {}).get("dateTime", ""),
            "end": e.get("end", {}).get("dateTime", ""),
            "summary": e.get("summary", "Busy"),
        })

    # Calculate free slots (simple approach)
    free_slots = []
    current = start
    for slot in busy_slots:
        slot_start = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
        if (slot_start - current).total_seconds() >= duration_minutes * 60:
            free_slots.append({
                "start": current.isoformat(),
                "end": slot_start.isoformat(),
            })
        slot_end = datetime.fromisoformat(slot["end"].replace("Z", "+00:00"))
        current = max(current, slot_end)
    if (end - current).total_seconds() >= duration_minutes * 60:
        free_slots.append({"start": current.isoformat(), "end": end.isoformat()})

    return {
        "date": date,
        "busy_count": len(busy_slots),
        "busy_slots": busy_slots,
        "free_slots": free_slots,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
