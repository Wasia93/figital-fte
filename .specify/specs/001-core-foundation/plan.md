# Implementation Plan: Core Foundation (Bronze Tier)

**Branch**: `001-core-foundation`
**Date**: 2026-02-13
**Spec**: [spec.md](spec.md)
**Status**: Implemented

## Summary

Build the foundational pipeline: TaskItem model, vault manager, approval workflow, orchestrator loop, triage agent, dashboard generation, and all supporting infrastructure.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: pydantic, pyyaml, python-dotenv, watchdog
- **Storage**: Filesystem (Obsidian-compatible markdown vault)
- **Testing Framework**: pytest
- **Target Platform**: Windows 10+
- **Project Type**: Agent orchestration system

## Constitution Check

- [x] Vault-First: All state stored as markdown files
- [x] HITL Safety: Approval workflow implemented
- [x] Agent Specialization: Each agent has single responsibility
- [x] Emergency Stop: EMERGENCY_STOP.md detection implemented
- [x] Idempotent: Deduplication in watchers, safe re-runs
- [x] Observable: Logging to vault/Logs/, Dashboard.md
- [x] Progressive: Bronze tier fully functional standalone
- [x] Config-driven: All behavior in YAML config files
- [x] Test-first: 38 unit tests passing

## Project Structure

### Source Code
```
src/
├── core/
│   ├── orchestrator.py        # Ralph Wiggum main loop
│   ├── vault_manager.py       # Vault CRUD operations
│   ├── config_loader.py       # YAML config loading
│   ├── task_item.py           # TaskItem model + serialization
│   ├── approval_manager.py    # HITL approval engine
│   ├── agent_base.py          # Abstract agent base class
│   ├── skill_registry.py      # Skill function registry
│   └── logger.py              # Dual console + vault logging
├── watchers/
│   ├── base_watcher.py        # Abstract polling loop
│   ├── gmail_watcher.py       # Gmail API polling
│   ├── whatsapp_watcher.py    # WhatsApp Business API
│   ├── banking_watcher.py     # Odoo transaction polling
│   ├── filesystem_watcher.py  # Watchdog-based file watching
│   └── watcher_runner.py      # Async watcher manager
├── agents/
│   ├── triage_agent.py        # Inbox classification + routing
│   ├── email_agent.py         # Email processing
│   ├── social_agent.py        # Social media content
│   ├── finance_agent.py       # Financial operations
│   ├── scheduler_agent.py     # Calendar management
│   └── ceo_briefing_agent.py  # Weekly briefing generation
├── skills/
│   ├── email_skills.py        # Email classification, drafting
│   ├── social_skills.py       # Post generation, engagement
│   ├── finance_skills.py      # Transaction categorization
│   ├── document_skills.py     # Summarization, entity extraction
│   ├── communication_skills.py # Brand voice, formatting
│   └── vault_skills.py        # Vault search, dashboard update
├── mcp_servers/
│   ├── gmail_mcp.py           # Gmail FastMCP server
│   ├── linkedin_mcp.py        # LinkedIn FastMCP server
│   ├── whatsapp_mcp.py        # WhatsApp FastMCP server
│   ├── odoo_mcp.py            # Odoo ERP FastMCP server
│   ├── calendar_mcp.py        # Google Calendar FastMCP server
│   └── filesystem_mcp.py      # Filesystem FastMCP server
└── dashboard/
    ├── dashboard_generator.py  # Dashboard.md generation
    └── briefing_generator.py   # Weekly_Briefing.md generation
```

## Architecture Overview

```
Watchers → Inbox/ → Triage Agent → Needs_Action/ → Specialized Agents
    → Needs_Approval/ → Human approval → Approved/ → MCP execution → Done/
```

The orchestrator runs a continuous loop (Ralph Wiggum Loop) that:
1. Checks emergency stop
2. Processes approved items
3. Processes rejected items
4. Triages inbox items
5. Dispatches agents for needs_action items
6. Updates dashboard
7. Sleeps for configured interval

## Implementation Strategy

**Phase 1** (Bronze): Core pipeline — TaskItem, VaultManager, ApprovalManager, Orchestrator, TriageAgent, Dashboard
**Phase 2** (Silver): Integrations — Gmail/WhatsApp watchers, Email/Social agents, MCP servers, approval processing
**Phase 3** (Gold): Business — Odoo integration, Finance agent, CEO Briefing, cross-agent coordination
**Phase 4** (Platinum): Cloud — Docker, webhooks, web UI, monitoring
