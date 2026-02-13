# Digital FTE

AI agent system that autonomously manages personal and business affairs 24/7 using an orchestrator loop, specialized agents, and a filesystem-based human-in-the-loop (HITL) approval workflow — all backed by an Obsidian-compatible markdown vault.

## Architecture

```
EXTERNAL SOURCES (Gmail, WhatsApp, Bank, Filesystem)
        |
        v
   [WATCHERS] ── poll & create TaskItem markdown files
        |
        v
   vault/Inbox/{source}/
        |
        v
   [TRIAGE AGENT] ── classifies, prioritizes, routes
        |
        v
   vault/Needs_Action/{type}/
        |
        v
   [ORCHESTRATOR - Ralph Wiggum Loop] ── dispatches agents
        |
        v
   [SPECIALIZED AGENTS] (Email, Social, Finance, Scheduler, CEO Briefing)
        |
        +──> Safe action ──> vault/Done/
        +──> Needs approval ──> vault/Needs_Approval/
                  |
                  +──> Human moves to vault/Approved/ ──> Executed ──> Done/
                  +──> Human moves to vault/Rejected/ ──> Logged
```

## Components

| Component | Description |
|-----------|-------------|
| **Orchestrator** | Ralph Wiggum loop — scans vault, triages inbox, dispatches agents, processes approvals |
| **Agents** | Email, Social, Finance, Scheduler, CEO Briefing — each extends `AgentBase` |
| **Watchers** | Gmail, WhatsApp, Banking (Odoo), Filesystem — poll external sources |
| **Skills** | Reusable functions (classify email, draft reply, categorize transaction, generate post, etc.) |
| **MCP Servers** | FastMCP + stdio servers for Gmail, LinkedIn, WhatsApp, Odoo, Calendar, Filesystem |
| **Approval Manager** | HITL workflow — risky actions require human approval via file moves in Obsidian |
| **Vault** | Obsidian-compatible markdown vault where all state lives as frontmatter + markdown |

## TaskItem Flow

```
INBOX → NEEDS_ACTION → IN_PROGRESS → NEEDS_APPROVAL → APPROVED → DONE
                                                     → REJECTED → DONE
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Initialize vault

```bash
python scripts/setup_vault.py
```

### 4. Start the orchestrator

```bash
python -m src.core.orchestrator
```

### 5. Start watchers (separate terminal)

```bash
python -m src.watchers.watcher_runner
```

### Windows

```batch
scripts\ralph_loop.bat
scripts\start_watchers.bat
```

## HITL Approval Workflow

Actions defined in `config/safety_rules.yaml` determine what needs human approval:

- **All outgoing emails** — draft is generated, human reviews and approves
- **All social posts** — content is generated, human reviews and approves
- **All financial operations** — transactions categorized, human approves recording
- **Calendar events** — details extracted, human approves creation

To approve or reject in Obsidian:
- **Approve**: Move the file from `Needs_Approval/` to `Approved/`
- **Reject**: Move the file from `Needs_Approval/` to `Rejected/`

## Emergency Stop

Create `vault/EMERGENCY_STOP.md` to halt all operations immediately.

## Project Structure

```
config/          — YAML configuration (settings, agents, watchers, safety rules)
src/core/        — Orchestrator, vault manager, task model, approval engine, logger
src/agents/      — Triage, email, social, finance, scheduler, CEO briefing agents
src/watchers/    — Gmail, WhatsApp, banking, filesystem watchers
src/skills/      — Email, social, finance, document, communication, vault skills
src/mcp_servers/ — FastMCP servers (Gmail, LinkedIn, WhatsApp, Odoo, Calendar, Filesystem)
src/dashboard/   — Dashboard and weekly briefing generators
vault/           — Obsidian-compatible markdown vault (all state stored here)
tests/           — Unit tests (38 tests)
scripts/         — Setup and startup scripts
```

## Running Tests

```bash
pytest tests/ -v
```

## Configuration

| File | Purpose |
|------|---------|
| `config/settings.yaml` | Master settings (vault path, intervals, logging) |
| `config/agents.yaml` | Agent definitions and routing rules |
| `config/watchers.yaml` | Watcher poll intervals and credentials |
| `config/mcp_servers.yaml` | MCP server registry |
| `config/safety_rules.yaml` | HITL approval rules per action type |

## License

MIT
