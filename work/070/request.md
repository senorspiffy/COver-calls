# Work item 070
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-17

## What we want
`scripts/check_pipeline.py` checks that the whole-output diff field added by item 067 is filled in 05 and 06 whenever an item changes realtest's decision path, instead of relying on agents to remember it.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- work/067/04-build-plan.md L123: "Follow-up (not built, RI-010 pattern): nothing checks that the new field is filled when the trigger files change. A check_pipeline check is a candidate item."
- work/067/06-verification.md: "RI-010: still a gap. Nothing checks that the new field is filled when the trigger files change (04's follow-up). It is passed on to A1."
- logs/audit/2026-11-16-067.md L55: "Field fill not checked (RI-010) ... Candidate check_pipeline item for the daily review."
- Field lives in templates/build-report.md and templates/verification.md on branch daily-fixes/2026-11-16 (PR #30).

## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Pattern is RI-010: a step duty that only the agent text asks for, with no script to check it.

## Recurring issue link (RI-#, if any)
RI-010, RI-013 (no new occurrence; preventive).

## Done looks like
For items from 070 on (or a named cutoff), when the item's commits change the trigger files 067 names (realtest decision path: ccbot/realtest.py and what it imports, config/), `check_pipeline.py` reports INCOMPLETE if 05 or 06 lacks a filled whole-output diff field (not blank, not a placeholder). Fixture tests: filled → no line; empty → INCOMPLETE; non-trigger change → no line. Existing items 001-069 unaffected. Built on top of PR #30's branch.
