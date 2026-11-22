# 07 Audit task - 090
I3 PASS (round 1) on 2026-11-22. Head 8caffda, base d3aa031. Process-only BUG (RI-010, RI-014). Changed files: scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py, .claude/commands/run-item.md, .claude/commands/daily-audit.md, .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md. These are RULE_PATHS, so the person's OK is needed at PR review.

What Audit should look at:
1. **The person-waiver gap (05 Deviations 4, 06 I2 audit).** A `Waived: 01 02 03 04 (person, ...)` item numbered 090 or higher is INCOMPLETE `LOG BATCH not computable: no line before I2 (item 090)`, and no waiver excuses it. I3 judged this a follow-up item, not a FAIL. Decide whether to open it, and what a person's waiver should excuse (that reason only, or also the per-round bound and the round rule).
2. **Round rule (a)/(b)/(c) in `_round_refusal`, on real histories.** Re-run a 069/070-shaped replay on main after merge. Also probe the gaps the docstring names: an I3 that FAILs twice (06 stays FAIL), A1 FAIL rounds (only (c)), and an I1 NOT A FIT whose sender file is rewritten by a later round.
3. **Per-round bound.** It catches only Δ0 rounds at today's 74-93 s runs, and Δ ≥ 1 batches pass. Check the RI-010 GUARDED condition: on main, a Δ0 round-2 I2 (test_round_bound_round2_batch's shape) is flagged.
4. **Shallow readers (RI-014).** In a real `git clone --depth 1 --no-single-branch` of the merged main:
   - LOG TIME, MAIN AHEAD and any unrelated branch say `not checked (shallow clone; run git fetch --unshallow)`;
   - origin/main is not listed;
   - the exit is 0 when no branch holds checked paths.
   Also check that refs already in main, listed in the shallow view, are loud and never silent (04 Extra research). GUARDED condition: M11 (shallow forced False) fails test_shallow_three_readers_not_checked on main.
5. **TIMED_FROM = 90 and the RULE NOT SEEN gate.** 091 or later items built before 090 lands should show `judged by untimed I2 form` and never INCOMPLETE. Check that every I2 line numbered 090 or higher on main is timed.
6. **7th file.** tests/test_real_data_field.py now reads `Suite:` from `FIELDS["I2"]`. Confirm that no assertion's meaning changed (24 tests reach it).
7. **Expected red test.** `test_repo_pipeline_has_no_skipped_items` fails at 8caffda only because of 087's open I3 FAIL round (item 071). Confirm that it is green once 087 has a PASS round.
8. **Single-branch clone hides branches** (Open Q5, RI-009). It is named in the docstring and is a possible new item.
9. Copy 05's `RI-010:` and `RI-014:` guardrail lines into logs/recurring-issues.md on main (item 036).

Evidence locations: I3 worktree `/tmp/claude-0/scratch/i3-090/wt` (removed after this step), mutation driver `/tmp/claude-0/scratch/i3-090/mutate.py`, probes `/tmp/claude-0/scratch/i3-090/probe/test_i3_probe.py`, full-suite output `/tmp/claude-0/scratch/i3-090/full_head.txt`.
A1 result: PASS (2026-11-22, logs/audit/2026-11-22-090.md)
