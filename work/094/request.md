# Work item 094
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
A single-branch clone never reports `OPEN BRANCHES: none` or a wrong `--next-id`.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-090.md F2: in a single-branch clone (plain `--depth 1`, also after `git fetch --unshallow`) output is `OPEN BRANCHES: none` and `--next-id` 092 while 092 exists on an open branch (full clone: 093).
## Root cause and prevention guardrail (BUG only)
Root cause: the checker lists remote branches but never asks whether the fetch refspec covers them.
Guardrail: detect a single-branch refspec (`remote.origin.fetch` not `+refs/heads/*`); print `OPEN BRANCHES: not checked (single-branch clone; run git config remote.origin.fetch ... && git fetch)`; `--next-id` refuses (exit 2); real-clone fixture.
## Recurring issue link (RI-#, if any)
RI-009, RI-014 family. Near miss, not counted.
## Done looks like
Single-branch fixture gives the not-checked line and refusal; mutation fails a named test.
