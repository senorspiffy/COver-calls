# Work item 104
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
The agent-tools frontmatter test fails closed on the remaining YAML-invalid shapes 096 left out, and stops one documented false error.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
work/096/03 follow-ups F-1 to F-5 and tests/test_agent_tools.py docstring known gaps (PR #37): `name: x: y` passes (F-1); indented `  foo: bar` under a scalar key passes (F-2); a column-0 key over 1024 characters passes (F-3); no allow-list for indented lines (F-4); `hooks: # c` then a column-0 item is a false error (F-5). No real agent file has these lines.
## Root cause and prevention guardrail (BUG only)
Root cause: indented lines and values are still deny-listed, not allow-listed (RI-002 pattern: unreadable value turned into a verdict).
Guardrail: allow-list for indented lines and value text (closes F-1, F-2), key length cap, trailing-comment fixture for F-5; PyYAML probe per fixture recorded; mutation per new check.
## Recurring issue link (RI-#, if any)
RI-002. Near miss, not counted.
## Done looks like
Each shape gives a named error (F-5 passes); real agent files still pass; mutations fail named fixtures.
