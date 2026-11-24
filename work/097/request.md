# Work item 097
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
Scratch isolation holds for every agent and the orchestrator: scratch dirs come from the rule's mkdtemp form, and no agent uses `git stash` in a scratch worktree.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-091.md N3/N4, work/091/06 follow-ups 2-3: the orchestrator handed I2/I3 fixed or `mktemp -d` paths under /tmp/claude-0/scratch, outside 091's new mkdtemp rule; I2 (091) made 3 `git stash` entries from a scratch worktree, visible in the main checkout (refs/stash is shared), then dropped them (05 Deviations 5).
## Root cause and prevention guardrail (BUG only)
Root cause: 091's scratch rule binds agents, not the orchestrator; git shares refs/stash across worktrees and no rule says so.
Guardrail: run-item.md: orchestrator never names a scratch path, agents with a shell make their own (rule's mkdtemp form); i2/i3/a1 text: no `git stash`, use a separate worktree or copy; check_pipeline (or a test) flags a non-empty `git stash list` at end of run.
## Recurring issue link (RI-#, if any)
RI-009 (scratch clobbering, 032/06). Found by A1 before merge; near miss, not counted.
## Done looks like
Rule text pinned by tests; stash check fixture fails with a stash entry.
