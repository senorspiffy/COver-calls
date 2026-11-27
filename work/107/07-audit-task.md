# 07 Audit task - 107
Audit should look at:
1. The diff at a522c5d, which has 4 rule files plus 3 test files:
   - The BYTECODE sentence appears once in each of .claude/commands/run-item.md, .claude/agents/i2-builder.md, .claude/agents/i3-verifier.md and .claude/agents/a1-auditor.md, directly after SCRATCH. I3 checked the text against 03 step 1 with a script (06 I2 audit).
   - tests/test_pipeline_check.py: `BYTECODE`, `test_bytecode_sentence_same_in_four_files`, `_tracked_bytecode` and `test_tracked_bytecode_helper`.
   - tests/test_probe_guardrails.py: `test_child_env_disables_bytecode_writes`.
   - New tests/test_stale_bytecode.py.
   I3 re-ran m0-m4 under the guard in its own worktree, and every mutant was killed (m3 on 3 of 3 runs).
2. FLAG: the 4 agent and rule files need the person's OK in PR review (request.md L13, 04). Check that the PR description asks for it.
3. Placement is not pinned. `test_bytecode_sentence_same_in_four_files` checks `count(BYTECODE) == 1`, not that the sentence comes right after SCRATCH. I3 checked placement by hand (`count(anchor + BYTECODE) == 1` in all 4 files). Decide whether that is enough.
4. Residuals kept on purpose (04):
   - (1) No script checks that later 05/06/audit files paste the `True <pyc dir>` env-check line. A1 watches the next 3 items with mutants, and opens a check_pipeline item if one is missing.
   - (2) The 10 `[sys.executable, ...]` test subprocess sites have no pin against a future `env=` that drops the guard.
5. The stale case depends on Python/pytest behaviour. It reproduces on 3.13.18 with pytest 9.1.1. If a later Python moves imports to hash pycs, control (a) fails loudly with "stale case not reproduced on this Python (item 107)", and it is not skipped. It was not run on 3.11, because python3.11 has no pytest. It only compiles there.
6. RULES BRANCH reads `none` from the branch's own checkout (05 Deviation 2). This is the same finding as 105/07 point 3.
7. Guardrail status on main for recurring-issues.md: the RI-013 family. 101/103/085 each caught a stale-pyc false result by hand. The rule text and the deterministic stale test are now in place, so look at whether the A1 watch (Residual 1) needs an RI-013 note.
A1 result: PASS (2026-11-26, logs/audit/2026-11-26-107.md)
