# Digital FTE - Claude Code Instructions

## Project Overview

This is a "Digital FTE" (Full-Time Equivalent) AI agent system that autonomously manages personal and business affairs using an orchestrator loop, specialized agents, and a filesystem-based HITL approval workflow.

## Architecture

- **Orchestrator** (`src/core/orchestrator.py`): The "Ralph Wiggum" loop that scans vault directories, triages items, dispatches agents, and processes approvals.
- **Vault** (`vault/`): Obsidian-compatible markdown vault where all state is stored as markdown files with YAML frontmatter.
- **Agents** (`src/agents/`): Specialized processors (email, social, finance, scheduler, CEO briefing).
- **Watchers** (`src/watchers/`): Poll external sources (Gmail, WhatsApp, banking, filesystem) and create TaskItems.
- **Skills** (`src/skills/`): Reusable functions registered in a SkillRegistry.
- **MCP Servers** (`src/mcp_servers/`): FastMCP servers for external actions (Gmail, LinkedIn, WhatsApp, Odoo, Calendar, Filesystem).

## Key Patterns

### TaskItem Flow
```
Inbox -> Needs_Action -> In_Progress -> Needs_Approval -> Approved -> Done
                                                       -> Rejected -> Done
```

### HITL Approval
- Actions defined in `config/safety_rules.yaml` determine what needs approval
- Approval requests are human-readable markdown files in `vault/Needs_Approval/`
- Human moves files to `Approved/` or `Rejected/` in Obsidian
- Orchestrator picks up moved files on next iteration

### Emergency Stop
Create `vault/EMERGENCY_STOP.md` to halt all operations immediately.

## Running

```bash
# Start orchestrator
python -m src.core.orchestrator

# Start watchers
python -m src.watchers.watcher_runner

# Run tests
pytest tests/
```

## Config Files
- `config/settings.yaml` - Master settings
- `config/agents.yaml` - Agent definitions and routing
- `config/watchers.yaml` - Watcher configurations
- `config/mcp_servers.yaml` - MCP server registry
- `config/safety_rules.yaml` - HITL approval rules
