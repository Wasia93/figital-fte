# Feature Specification: Core Foundation (Bronze Tier)

**Feature Branch**: `001-core-foundation`
**Created**: 2026-02-13
**Status**: Implemented

## User Scenarios & Testing

### User Story 1 - Orchestrator processes inbox items (Priority: P1)

As a user, when emails arrive in my inbox, the system should automatically triage them into the correct category and queue them for the appropriate agent.

**Why this priority**: This is the fundamental pipeline — without triage, nothing flows.

**Independent Test**: Place a sample email TaskItem in `Inbox/Email/`, run one orchestrator iteration, verify it moves to `Needs_Action/Email/`.

**Acceptance Scenarios**:

1. **Given** an email TaskItem in `Inbox/Email/`, **When** the orchestrator runs, **Then** the item is classified and moved to `Needs_Action/{category}/`
2. **Given** a non-actionable email (newsletter), **When** triaged, **Then** it is archived directly to `Done/`
3. **Given** multiple inbox items, **When** the orchestrator runs, **Then** all are triaged in priority order

### User Story 2 - HITL approval workflow (Priority: P1)

As a user, when an agent wants to send an email or post to social media, it must create an approval request that I can review in Obsidian and approve or reject by moving the file.

**Why this priority**: Safety-critical — no external actions without human consent.

**Independent Test**: Create an approval request, move it to `Approved/`, run orchestrator, verify execution.

**Acceptance Scenarios**:

1. **Given** an agent drafts an email, **When** the action requires approval, **Then** a human-readable file appears in `Needs_Approval/`
2. **Given** a file in `Approved/`, **When** the orchestrator runs, **Then** the action is executed and the file is archived to `Done/`
3. **Given** a file in `Rejected/`, **When** the orchestrator runs, **Then** no action is taken and the file is archived

### User Story 3 - Emergency stop (Priority: P1)

As a user, I must be able to halt all operations immediately by creating a single file.

**Why this priority**: Non-negotiable safety mechanism.

**Independent Test**: Create `EMERGENCY_STOP.md`, verify orchestrator halts on next iteration.

**Acceptance Scenarios**:

1. **Given** `EMERGENCY_STOP.md` exists in vault root, **When** the orchestrator checks, **Then** it stops immediately

### User Story 4 - Dashboard visibility (Priority: P2)

As a user, I should see a live dashboard in Obsidian showing queue counts and pending items.

**Why this priority**: Visibility into system state.

**Independent Test**: Run orchestrator, open `Dashboard.md`, verify counts match actual files.

**Acceptance Scenarios**:

1. **Given** the orchestrator has run, **When** I open `Dashboard.md`, **Then** I see current queue counts
2. **Given** items in `Needs_Approval/`, **When** I view the dashboard, **Then** they are listed with titles and priorities

## Requirements

### Functional Requirements

- **FR-001**: System MUST serialize TaskItems as markdown with YAML frontmatter
- **FR-002**: System MUST support full TaskItem lifecycle (INBOX → NEEDS_ACTION → IN_PROGRESS → NEEDS_APPROVAL → APPROVED/REJECTED → DONE)
- **FR-003**: System MUST deduplicate incoming items by source_id
- **FR-004**: System MUST archive completed items to `Done/YYYY/MM/`
- **FR-005**: System MUST halt on EMERGENCY_STOP.md detection
- **FR-006**: System MUST log all agent actions to `vault/Logs/`
- **FR-007**: System MUST generate Dashboard.md after each iteration
- **FR-008**: System MUST load configuration from YAML files
- **FR-009**: System MUST support pluggable agents via config

### Key Entities

- **TaskItem**: Core work unit with id, title, source, status, priority, category, body, action plan, action params
- **VaultManager**: File operations abstraction over the markdown vault
- **ApprovalManager**: HITL workflow engine managing Needs_Approval/Approved/Rejected
- **Orchestrator**: Main dispatch loop scanning and processing vault directories
- **AgentBase**: Abstract base class all agents extend

## Success Criteria

- **SC-001**: All 38 unit tests pass
- **SC-002**: End-to-end flow from inbox to done works in under 5 seconds per item
- **SC-003**: Emergency stop halts within one iteration
- **SC-004**: Dashboard accurately reflects vault state
