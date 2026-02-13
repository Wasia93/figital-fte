Generate a quality checklist for a feature. Read all artifacts in `.specify/specs/$ARGUMENTS/` and produce a checklist covering:

## Code Quality
- [ ] All functions have clear single responsibility
- [ ] Error handling covers expected failure modes
- [ ] No hardcoded values (use config)

## Testing
- [ ] Unit tests exist for all core modules
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Edge cases covered

## Constitution Compliance
- [ ] Vault-first: all state in markdown files
- [ ] HITL: all external actions require approval
- [ ] Emergency stop works
- [ ] Operations are idempotent
- [ ] Execution is logged

## Documentation
- [ ] Spec is complete and unambiguous
- [ ] Plan matches implementation
- [ ] Tasks are all checked off

Feature to check: $ARGUMENTS
