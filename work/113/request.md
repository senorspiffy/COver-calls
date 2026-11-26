# Work item 113
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-26
## What we want
Small cleanups from 105/107/110 audits: (a) build-plan/build-report templates say `RULES BRANCH:` lists only branches not merged into HEAD (so a branch never shows its own rule change; check from origin/main); (b) `who` from parse_request has no reader in scripts/ after 105: remove it or document why it stays; (c) 110's docstring figures are dated 4404a28: say "re-run the script, don't copy the numbers".
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-26-105.md (04 Tests 5 and 05 both misread RULES BRANCH; 107/05 the same), logs/audit/2026-11-26-105.md (`who` unused), logs/audit/2026-11-25-110.md (figures dated). All PR #39.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).
## Recurring issue link (RI-#, if any)
RI-009 (branch visibility wording), RI-010.
## Done looks like
Template lines added and pinned; `who` removed with tests green or kept with a comment; 110 docstring says to re-run.
