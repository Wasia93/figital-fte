Generate a task breakdown for a feature. Read the spec and plan at `.specify/specs/$ARGUMENTS/` and create a `tasks.md` in the same directory.

Tasks must be organized into phases:
- Phase 0: Setup (project initialization)
- Phase 1: Foundational (infrastructure that all user stories need)
- Phase 2: User Stories (grouped by story, ordered by priority)
- Phase 3: Polish (cross-cutting improvements)

Each task should:
- Use checkbox format (`- [ ]`)
- Include file paths showing what to create/modify
- Mark parallelizable tasks with `[P]`
- List dependencies at the bottom

Feature to generate tasks for: $ARGUMENTS
