---
id: "ADR-002"
title: "Filesystem-Based HITL Approval Workflow"
status: "Accepted"
date: "2026-02-13"
feature: "001-core-foundation"
context: "Choosing the human-in-the-loop approval mechanism for agent actions"
---

# ADR-002: Filesystem-Based HITL Approval Workflow

## Decision

Human approval is implemented by moving markdown files between vault directories:
- Agent writes approval request to `Needs_Approval/`
- Human reviews in Obsidian and moves to `Approved/` or `Rejected/`
- Orchestrator detects moved files and acts accordingly

Safety rules in `config/safety_rules.yaml` define which actions require approval.

## Consequences

### Positive

- Zero custom UI needed — works in any file manager or Obsidian
- Approval requests are human-readable markdown with full context
- Naturally asynchronous — human approves when ready
- Audit trail via git (file moves are tracked)
- Works offline

### Negative

- No notification mechanism (human must check the folder)
- No mobile approval without file sync (e.g., Obsidian Sync)
- Risk of accidental file moves
- No approval delegation or multi-approver support

## Alternatives Considered

1. **Slack bot approval**: Interactive buttons in Slack. Rejected: requires Slack dependency, doesn't work offline.
2. **Web dashboard with buttons**: Custom approval UI. Rejected: significant development effort for Platinum tier.
3. **Email-based approval**: Reply to approve. Rejected: unreliable, hard to parse responses.

## References

- Feature Spec: `.specify/specs/001-core-foundation/spec.md`
- Safety Rules: `config/safety_rules.yaml`
