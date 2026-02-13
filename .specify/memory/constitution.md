# Digital FTE Constitution

## Core Principles

### I. Vault-First Architecture
Every piece of state lives as a markdown file with YAML frontmatter in the Obsidian vault. No hidden databases, no in-memory-only state. If it's not in the vault, it doesn't exist. Files are the single source of truth — agents read from and write to the vault.

### II. Human-In-The-Loop Safety
No agent may take an externally-visible action (send email, post to social media, record a payment, create a calendar event) without explicit human approval. Safe actions (reading, classifying, drafting, moving files within the vault) may proceed autonomously. The approval workflow is filesystem-based: humans move files between `Needs_Approval/`, `Approved/`, and `Rejected/` folders.

### III. Agent Specialization
Each agent has a single responsibility and a clearly defined scope. Agents are stateless processors — they read a TaskItem, perform their work, and write the result back. Cross-agent coordination happens through the vault (one agent's output becomes another's input), never through direct agent-to-agent communication.

### IV. Emergency Stop (NON-NEGOTIABLE)
Creating `EMERGENCY_STOP.md` in the vault root MUST halt all operations within one orchestrator cycle. No exceptions. No agent may bypass or ignore the emergency stop. This is the ultimate safety mechanism.

### V. Idempotent Operations
Every watcher must deduplicate. Every agent must be safe to re-run on the same TaskItem. Moving a file that's already been moved must not crash. The system must tolerate restarts, partial failures, and duplicate events gracefully.

### VI. Observable Execution
Every agent action is logged to `vault/Logs/`. Every TaskItem records its full lifecycle in frontmatter (status changes, assigned agent, timestamps). The Dashboard and Weekly Briefing provide human-readable summaries. The system is auditable — you can reconstruct what happened by reading the vault.

### VII. Progressive Enhancement
The system is built in tiers (Bronze → Silver → Gold → Platinum). Each tier is fully functional on its own. Higher tiers add integrations and capabilities but never break lower tiers. A Bronze-only deployment must work correctly.

### VIII. Configuration Over Code
Behavior is controlled through YAML config files (`config/*.yaml`), not hardcoded values. Adding a new watcher, agent, or safety rule should require config changes, not code changes. The system is designed for extensibility without modification.

### IX. Test-First Verification
Every core module (TaskItem, VaultManager, ApprovalManager, Orchestrator) must have unit tests. The test suite must pass before any deployment. Integration tests verify end-to-end flows (inbox → triage → agent → approval → execution → archive).

## Development Workflow

1. Specs are written before implementation
2. Plans are reviewed before coding begins
3. Tests are written alongside implementation
4. All changes go through git with descriptive commits
5. The vault structure is the contract — changing it requires a spec update

## Governance

This constitution supersedes all other development practices for the Digital FTE project. Amendments require:
1. A written spec documenting the change and rationale
2. Verification that existing tests still pass
3. Update to this constitution document

**Version**: 1.0.0 | **Ratified**: 2026-02-13 | **Last Amended**: 2026-02-13
