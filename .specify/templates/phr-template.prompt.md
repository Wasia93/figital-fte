---
id: "PHR-{{ID}}"
title: "{{TITLE}}"
stage: "{{STAGE}}"  # constitution | specify | clarify | plan | tasks | implement | analyze | checklist
date: "{{DATE_ISO}}"
surface: "{{SURFACE}}"  # claude-code | cursor | copilot | terminal
model: "{{MODEL}}"  # claude-opus-4-6 | claude-sonnet-4-5 | etc.
feature: "{{FEATURE_NAME}}"
branch: "{{BRANCH_NAME}}"
user: "{{USER}}"
command: "{{COMMAND}}"  # /speckit.specify | /speckit.plan | etc.
labels:
  - "{{LABEL}}"
links:
  spec: "{{SPEC_LINK}}"
  plan: "{{PLAN_LINK}}"
  tasks: "{{TASKS_LINK}}"
---

## Prompt

```
{{PROMPT_TEXT}}
```

## Response Snapshot

{{RESPONSE_SUMMARY}}

## Outcome

- **Result**: {{SUCCESS | PARTIAL | FAILURE}}
- **Files created/modified**: {{FILE_LIST}}
- **Tests passing**: {{YES | NO | N/A}}

## Evaluation

### Failure Modes
{{FAILURE_MODES_IF_ANY}}

### Grader Results
{{GRADER_RESULTS_IF_ANY}}

### Prompt Variants Tried
{{VARIANTS_IF_ANY}}

### Next Experiment
{{NEXT_STEPS}}
