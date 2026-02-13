# Tasks: Core Foundation (Bronze Tier)

## Phase 0: Setup
- [x] Task 0.1: Create project scaffolding — `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
- [x] Task 0.2: Create vault directory structure — `scripts/setup_vault.py`
- [x] Task 0.3: Create all `__init__.py` files

## Phase 1: Foundational
- [x] Task 1.1: Create YAML config files — `config/settings.yaml`, `config/agents.yaml`, `config/watchers.yaml`, `config/mcp_servers.yaml`, `config/safety_rules.yaml`
- [x] Task 1.2: Implement config loader — `src/core/config_loader.py`
- [x] Task 1.3: Implement TaskItem model with YAML frontmatter serialization — `src/core/task_item.py`
- [x] Task 1.4: Implement VaultManager — `src/core/vault_manager.py`
- [x] Task 1.5: Implement Logger — `src/core/logger.py`
- [x] Task 1.6: Implement AgentBase — `src/core/agent_base.py`
- [x] Task 1.7: Implement SkillRegistry — `src/core/skill_registry.py`
- [x] Task 1.8: Implement ApprovalManager — `src/core/approval_manager.py`

## Phase 2: User Stories

### User Story 1 (P1): Orchestrator processes inbox items
- [x] Task 2.1: Implement TriageAgent — `src/agents/triage_agent.py`
- [x] Task 2.2: Implement Orchestrator (Ralph Wiggum loop) — `src/core/orchestrator.py`
- [x] Task 2.3: Write orchestrator tests — `tests/test_orchestrator.py`

### User Story 2 (P1): HITL approval workflow
- [x] Task 2.4: Write approval manager tests — `tests/test_approval_manager.py`
- [x] Task 2.5: Verify full approval flow (create → approve → execute → archive)

### User Story 3 (P1): Emergency stop
- [x] Task 2.6: Test emergency stop detection — `tests/test_orchestrator.py::test_emergency_stop`

### User Story 4 (P2): Dashboard visibility
- [x] Task 2.7: Implement DashboardGenerator — `src/dashboard/dashboard_generator.py`
- [x] Task 2.8: Implement BriefingGenerator — `src/dashboard/briefing_generator.py`
- [x] Task 2.9: Test dashboard generation — `tests/test_orchestrator.py::test_dashboard_generated`

### User Story 5 (P2): Specialized agents
- [x] Task 2.10: Implement EmailAgent — `src/agents/email_agent.py`
- [x] Task 2.11: Implement SocialAgent — `src/agents/social_agent.py`
- [x] Task 2.12: Implement FinanceAgent — `src/agents/finance_agent.py`
- [x] Task 2.13: Implement SchedulerAgent — `src/agents/scheduler_agent.py`
- [x] Task 2.14: Implement CEOBriefingAgent — `src/agents/ceo_briefing_agent.py`

### User Story 6 (P2): Skills
- [x] [P] Task 2.15: Implement email_skills — `src/skills/email_skills.py`
- [x] [P] Task 2.16: Implement social_skills — `src/skills/social_skills.py`
- [x] [P] Task 2.17: Implement finance_skills — `src/skills/finance_skills.py`
- [x] [P] Task 2.18: Implement document_skills — `src/skills/document_skills.py`
- [x] [P] Task 2.19: Implement communication_skills — `src/skills/communication_skills.py`
- [x] [P] Task 2.20: Implement vault_skills — `src/skills/vault_skills.py`

### User Story 7 (P3): Watchers
- [x] Task 2.21: Implement BaseWatcher — `src/watchers/base_watcher.py`
- [x] [P] Task 2.22: Implement GmailWatcher — `src/watchers/gmail_watcher.py`
- [x] [P] Task 2.23: Implement WhatsAppWatcher — `src/watchers/whatsapp_watcher.py`
- [x] [P] Task 2.24: Implement BankingWatcher — `src/watchers/banking_watcher.py`
- [x] [P] Task 2.25: Implement FilesystemWatcher — `src/watchers/filesystem_watcher.py`
- [x] Task 2.26: Implement WatcherRunner — `src/watchers/watcher_runner.py`

### User Story 8 (P3): MCP Servers
- [x] [P] Task 2.27: Implement gmail_mcp — `src/mcp_servers/gmail_mcp.py`
- [x] [P] Task 2.28: Implement linkedin_mcp — `src/mcp_servers/linkedin_mcp.py`
- [x] [P] Task 2.29: Implement whatsapp_mcp — `src/mcp_servers/whatsapp_mcp.py`
- [x] [P] Task 2.30: Implement odoo_mcp — `src/mcp_servers/odoo_mcp.py`
- [x] [P] Task 2.31: Implement calendar_mcp — `src/mcp_servers/calendar_mcp.py`
- [x] [P] Task 2.32: Implement filesystem_mcp — `src/mcp_servers/filesystem_mcp.py`

## Phase 3: Polish
- [x] Task 3.1: Create vault content — `vault/Company_Handbook.md`, `vault/Templates/*.md`
- [x] Task 3.2: Create CLAUDE.md project instructions
- [x] Task 3.3: Create startup scripts — `scripts/ralph_loop.bat`, `scripts/start_watchers.bat`
- [x] Task 3.4: Write TaskItem tests — `tests/test_task_item.py`
- [x] Task 3.5: Write VaultManager tests — `tests/test_vault_manager.py`
- [x] Task 3.6: Create test fixtures — `tests/fixtures/`
- [x] Task 3.7: Create README.md
- [x] Task 3.8: Integrate Spec Kit — `.specify/`

## Dependencies

- Phase 1 must complete before Phase 2
- Task 2.1 (TriageAgent) depends on Task 1.6 (AgentBase) and Task 1.7 (SkillRegistry)
- Task 2.2 (Orchestrator) depends on all Phase 1 tasks
- Tasks marked [P] can run in parallel
