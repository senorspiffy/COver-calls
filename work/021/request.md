# Work item 021
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Support research-only items in the pipeline so they still get a per-item audit.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/001/request.md` adds a free-text line "Scope: RESEARCH TEAM ONLY (R1 -> R2 -> R3)". `templates/request.md` has no Scope field, and `.claude/commands/run-item.md` always runs all seven steps.
- A1's per-item audit only starts "when `work/<ID>/07-audit-task.md` exists", and only I3 writes that file. So a research-only item like 001 never gets a per-item audit; today it was caught only by the daily review.

## Done looks like
`templates/request.md` has `Scope: FULL | RESEARCH ONLY`; `run-item.md` stops after R3 for research-only items; R3 writes `07-audit-task.md` for those items so A1 audits them.
