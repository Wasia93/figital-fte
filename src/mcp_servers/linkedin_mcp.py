"""LinkedIn MCP Server - post/comment/stats via FastMCP + stdio."""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("linkedin")

API_BASE = "https://api.linkedin.com/v2"


def _headers() -> dict[str, str]:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _get_person_urn() -> str:
    """Get the authenticated user's LinkedIn URN."""
    resp = httpx.get(f"{API_BASE}/me", headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    return f"urn:li:person:{data['id']}"


@mcp.tool()
def create_post(content: str, visibility: str = "PUBLIC") -> dict[str, str]:
    """Create a LinkedIn post.

    Args:
        content: The text content of the post
        visibility: Post visibility (PUBLIC or CONNECTIONS)
    """
    author = _get_person_urn()
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }
    resp = httpx.post(f"{API_BASE}/ugcPosts", json=payload, headers=_headers())
    resp.raise_for_status()
    return {"status": "posted", "post_id": resp.headers.get("x-restli-id", "")}


@mcp.tool()
def create_comment(post_urn: str, comment: str) -> dict[str, str]:
    """Comment on a LinkedIn post.

    Args:
        post_urn: The URN of the post to comment on
        comment: The comment text
    """
    author = _get_person_urn()
    payload = {
        "actor": author,
        "message": {"text": comment},
    }
    resp = httpx.post(
        f"{API_BASE}/socialActions/{post_urn}/comments",
        json=payload,
        headers=_headers(),
    )
    resp.raise_for_status()
    return {"status": "commented", "comment_id": resp.json().get("id", "")}


@mcp.tool()
def get_profile_stats() -> dict[str, Any]:
    """Get LinkedIn profile statistics."""
    resp = httpx.get(f"{API_BASE}/me", headers=_headers())
    resp.raise_for_status()
    profile = resp.json()
    return {
        "id": profile.get("id", ""),
        "first_name": profile.get("localizedFirstName", ""),
        "last_name": profile.get("localizedLastName", ""),
    }


@mcp.tool()
def get_recent_posts(count: int = 10) -> list[dict[str, Any]]:
    """Get recent LinkedIn posts.

    Args:
        count: Number of recent posts to retrieve
    """
    author = _get_person_urn()
    params = {"q": "authors", "authors": f"List({author})", "count": count}
    resp = httpx.get(f"{API_BASE}/ugcPosts", params=params, headers=_headers())
    resp.raise_for_status()
    posts = resp.json().get("elements", [])
    return [
        {
            "id": p.get("id", ""),
            "text": p.get("specificContent", {})
            .get("com.linkedin.ugc.ShareContent", {})
            .get("shareCommentary", {})
            .get("text", ""),
            "created": p.get("created", {}).get("time", ""),
        }
        for p in posts
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
