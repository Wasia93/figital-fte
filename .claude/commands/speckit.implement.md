Implement a feature by following its task list. Read the tasks at `.specify/specs/$ARGUMENTS/tasks.md` and execute them in order.

Rules:
1. Read the constitution first (`.specify/memory/constitution.md`)
2. Follow the plan (`.specify/specs/$ARGUMENTS/plan.md`)
3. Execute tasks in phase order (Phase 0 → 1 → 2 → 3)
4. Respect dependencies — don't skip ahead
5. Mark tasks as complete (`[x]`) in tasks.md as you finish them
6. Run tests after implementation to verify
7. Parallelizable tasks (`[P]`) can be done in any order within their group

Feature to implement: $ARGUMENTS
