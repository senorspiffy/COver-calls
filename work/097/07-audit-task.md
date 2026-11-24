# 07 Audit task - 097
Item: 097 (BUG, FULL). Scratch isolation: new SCRATCH rule text (orchestrator names no path to shell agents, mkdtemp only, `--detach` worktrees, no `git stash`), a `STASH:` line in check_pipeline (exit 1 on any entry or failed read), and a `Scratch dir:` INCOMPLETE check on 05/06 from SCRATCH_FROM = 97. Head 1f27ce7 (+ the I3 commit) on daily-fixes/2026-11-24, base 762c8ec. I3 PASS round 1.

What A1 should look at:
1. `scripts/check_pipeline.py` `scratch_dir_problems` and the SCRATCH_FROM block in `incomplete()`: basename fullmatch (one trailing `/` stripped), `is_absolute`, agent tied to step (i2/05, i3/06), ID tied to item, `none (<non-blank>)`. Note `none \((.*)\)` is greedy: `none (a) b (c)` passes as a reason; decide if that matters.
2. STASH in `main()`: four outcomes, `or stash_bad` in the return, stdout never read on a failed read (`_git_ok` passes stdout through, fixture (c) pins it). Known residual: a push and drop in one run is invisible (091's own pattern), and the no-stash rule at the moment of use is text-only.
3. Deviation 2 (9th file): `_scratch_line` added to fixture helpers for IDs >= 97. I3 mutant H (check off + helper line removed) left every pre-097 test result unchanged (06). Re-probe if you doubt it.
4. Re-run any of the mutants A1-A4, B1-B3, C1-C9 (06 lists each with its failing tests; I3's own extras C7-C9 included).
5. Option (i) reading of "the orchestrator never names a scratch path" (R1-R3/I1 still get a mkdtemp-printed path from the orchestrator), and RULE_PATHS touched: both need the person's OK at PR review.
6. 098 is built after 097 and has an ID >= SCRATCH_FROM: its 05/06 must carry `Scratch dir:` lines (05 "Next item").
7. RI status to copy on main: RI-009 near miss "orchestrator scratch paths outside 091's rule; `git stash` in a scratch worktree" closed by 097 (not counted), guardrail built; RI-010 extended, stays ESCALATED; RI-001, RI-014 unchanged.
A1 result: PASS (2026-11-24, logs/audit/2026-11-24-097.md)
