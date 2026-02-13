# Data Model: Core Foundation

## Entities

### TaskItem
The core work unit flowing through the pipeline.

| Field | Type | Description |
|-------|------|-------------|
| id | string (12 hex chars) | Unique identifier |
| title | string | Human-readable title |
| source | string | Origin: Email, WhatsApp, Banking, Filesystem, Manual |
| source_id | string | Deduplication key from source system |
| status | TaskStatus enum | Current lifecycle stage |
| priority | Priority enum | critical, high, medium, low |
| assigned_agent | string | Name of the agent processing this item |
| category | string | Routing category: Email, Social, Finance, General |
| tags | list[string] | Freeform tags for filtering |
| created_at | ISO 8601 string | Creation timestamp |
| updated_at | ISO 8601 string | Last modification timestamp |
| source_data | dict | Raw metadata from source (e.g., Gmail headers) |
| body | string | Markdown body content |
| approval_required | boolean | Whether this item needs HITL approval |
| action_plan | string | Description of planned action |
| action_type | string | MCP tool to invoke (e.g., send_email) |
| action_params | dict | Parameters for the MCP tool call |
| result | string | Outcome after execution |
| error | string | Error message if failed |

### TaskStatus (Enum)
```
INBOX → NEEDS_ACTION → IN_PROGRESS → NEEDS_APPROVAL → APPROVED → DONE
                                                     → REJECTED → DONE
```

### Priority (Enum)
```
CRITICAL > HIGH > MEDIUM > LOW
```

## Storage Format

TaskItems are stored as markdown files with YAML frontmatter:

```markdown
---
id: abc123def456
title: Invoice from Acme Corp
source: Email
status: needs_action
priority: high
...
---

(markdown body content)

## Action Plan

(action plan content)
```

## File Naming Convention

```
{YYYY-MM-DD}_{HHMM}_{id}_{title-slug}.md
```

Example: `2026-02-13_1430_abc123def456_invoice-from-acme-corp.md`

## Directory Mapping

| Status | Directory |
|--------|-----------|
| INBOX | `vault/Inbox/{source}/` |
| NEEDS_ACTION | `vault/Needs_Action/{category}/` |
| IN_PROGRESS | `vault/In_Progress/{category}/` |
| NEEDS_APPROVAL | `vault/Needs_Approval/` |
| APPROVED | `vault/Approved/` |
| REJECTED | `vault/Rejected/` |
| DONE | `vault/Done/{YYYY}/{MM}/` |
