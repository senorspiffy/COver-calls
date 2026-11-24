# Work item 095
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
A shallow clone gives clear, non-misleading output: 083's RULE NOT SEEN not-checked case is named in a1-auditor.md, and already-merged branches do not each print BRANCH ERROR.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-090.md F3: in a clone that stays shallow, 083 shows a false INCOMPLETE because RULE NOT SEEN is not checked; a1-auditor.md L22 does not list that case. A shallow clone of this repo exits 1 every time: 28 already-merged branches each give a BRANCH ERROR.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: shallow → INCOMPLETE entries that depend on RULE NOT SEEN read "not checked (shallow clone)"; merged-branch scan says one `not checked (shallow clone)` line; a1-auditor.md names both.
## Recurring issue link (RI-#, if any)
RI-014.
## Done looks like
Depth-1 fixture: no false INCOMPLETE, one not-checked branch line; full-clone output unchanged.
