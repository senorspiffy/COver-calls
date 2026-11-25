# Work item 106
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
Agent-tools frontmatter test fails closed on the 3 shapes 104 left open.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-25-104.md (PR #38) follow-ups: (1) a tab before `#` (`description: a\t# see: b`) passes, and the two YAML loaders disagree on it; (2) D3 has no check of sibling indent levels; (3) a continuation line under a closed `tools:` line reports VALUE, not `_field`'s message. No real agent file has these lines.
## Root cause and prevention guardrail (BUG only)
Root cause: whitespace before a comment and indent levels are still not allow-listed (RI-002 pattern: unreadable value turned into a verdict).
Guardrail: treat tab+`#` like space+`#` or refuse it; sibling-indent check; named error for continuation under `tools:`; PyYAML probe per fixture; mutation per new check.
## Recurring issue link (RI-#, if any)
RI-002. Near miss, not counted.
## Done looks like
Each shape gives a named error or a documented pass; real agent files still pass; mutations fail named fixtures.
