# Work item 107
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
Mutation probes by I2/I3/A1 never read stale bytecode: run with `python3 -B` / `PYTHONDONTWRITEBYTECODE=1` and clear `__pycache__` in the scratch worktree.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
work/101/05 (I2: first mutant run reused stale bytecode, re-ran) and work/103/06 (I3: one mutant first passed only because Python reused a cached compiled file). Both caught by hand.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: one sentence in i2/i3/a1 agent files + run-item; optional helper or pytest flag `-p no:cacheprovider` plus -B.
## Recurring issue link (RI-#, if any)
RI-013 family (results from a wrong run). Rule files change: person's review in the PR.
## Done looks like
Agent text names the flag; a probe with a stale .pyc shows the mutant killed.
