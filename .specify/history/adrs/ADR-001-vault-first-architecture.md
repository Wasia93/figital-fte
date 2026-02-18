---
id: "ADR-001"
title: "Vault-First Filesystem Architecture"
status: "Accepted"
date: "2026-02-13"
feature: "001-core-foundation"
context: "Choosing the state management approach for the Digital FTE agent system"
---

# ADR-001: Vault-First Filesystem Architecture

## Decision

All system state is stored as markdown files with YAML frontmatter in an Obsidian-compatible vault. No database. No in-memory-only state. Files are moved between directories to represent state transitions. The filesystem IS the state machine.

Components:
- **Storage**: Markdown files with YAML frontmatter
- **State machine**: Directory-based (Inbox/ → Needs_Action/ → Done/)
- **GUI**: Obsidian (reads vault directly)
- **Approval**: Human moves files between folders

## Consequences

### Positive

- Obsidian provides a free, powerful GUI with no custom UI development
- Every state change is a file operation — fully auditable via git
- Human approval is as simple as drag-and-drop in a file manager
- No database dependency — system works on any machine with a filesystem
- Markdown files are human-readable and editable
- Natural backup via git commits

### Negative

- Not suitable for high-throughput (>1000 items/minute)
- No ACID transactions — concurrent writes could conflict
- File operations are slower than database queries
- No built-in indexing — search requires scanning files
- Directory listing gets slow with thousands of files

## Alternatives Considered

1. **SQLite + web UI**: More scalable but requires building a custom UI. Rejected: adds complexity, loses Obsidian integration.
2. **Redis + REST API**: Fast in-memory state with API access. Rejected: not human-readable, requires running a server.
3. **Notion/Airtable API**: Cloud-based with nice UI. Rejected: vendor lock-in, API rate limits, no offline support.

## References

- Feature Spec: `.specify/specs/001-core-foundation/spec.md`
- Implementation Plan: `.specify/specs/001-core-foundation/plan.md`
