Analyze cross-artifact consistency for a feature. Read all files in `.specify/specs/$ARGUMENTS/` and verify:

1. **Spec ↔ Plan alignment**: Every requirement in spec.md has a corresponding implementation approach in plan.md
2. **Plan ↔ Tasks alignment**: Every component in plan.md has corresponding tasks in tasks.md
3. **Tasks ↔ Code alignment**: Every task in tasks.md corresponds to actual files in the codebase
4. **Constitution compliance**: All artifacts comply with `.specify/memory/constitution.md`
5. **Data model consistency**: Entities in data-model.md match the actual code

Report any gaps, inconsistencies, or violations found.

Feature to analyze: $ARGUMENTS
