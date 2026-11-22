# 07 Audit task - 091
I3 PASS (round 2; round 1 FAIL) on 2026-11-22. Head 1293415, base 7e537c2 (087 A1 PASS). EFFICIENCY item (RI-010, RI-014). Changed files outside work/ and logs/: the 12 files in 04's table, round 2 adds no new file (scripts/commit_step.py, tests/test_commit_step.py). Some are RULE_PATHS (run-item.md, agent files, templates), so the person's OK is needed at PR review.

What Audit should look at:
1. **commit_step path handling (06 F1, round 2).** `repo_relative` resolves the parent and not the name. Probe on main after merge:
   - an absolute log path, `./`, `../<repo>/` and a symlinked dir to logs/ are all refused;
   - an absolute non-log path is committed relative;
   - a path outside the top is refused.
   Also try a path whose name component is itself a symlink to a log file (staged as a symlink, not its content: confirm that is acceptable). Also try a case-variant path on a case-insensitive filesystem, if any agent runs on one.
2. **filter_log owner match (06 F2, RI-012).** `test_filter_log_pattern_inside_other_text` kills the substring and unanchored mutants. `.search` is equivalent only while LOG_LINE keeps its `^` and has no `re.M`, so confirm that is still true on main.
3. **Trailers are added outside the helper.** Every 091 commit so far was made by commit_step and then changed with `git commit --amend --only` for the trailers. Each time the tree is unchanged (reflog: 66f0fcf/4990002, 8b5f93d/d39d811, c01d0d5/1293415, and this I3 commit). No rule names this step, and a plain `--amend` would take the shared index. Decide on follow-up 1 (a `--trailer` option in commit_step).
4. **Scratch-dir rule vs orchestrator practice (follow-up 2).** The orchestrator gave I2 and I3 `mktemp -d /tmp/claude-0/scratch/<agent>-091r2-XXXX`: unique, but not step 3's `tempfile.mkdtemp(prefix=..., dir=<scratchpad>)`. Decide whether run-item should allow it or the orchestrator should change.
5. **No `git stash` in scratch worktrees (follow-up 3, RI-009).** refs/stash is shared across worktrees (I2 round-1 incident, 05 Deviations 5).
6. **088's unborn-HEAD label (follow-up 4, 05 Deviations 4).**
7. **Round-heading check (5b) on main.** ROUND_HEADING_FROM = 92: the first item at or after 092 with a stray `### Test output` / `Round N` heading must be INCOMPLETE. Also check the residuals in 05: runs with no heading, and indented headings.
8. **Expected red test.** At 1293415, `test_repo_pipeline_has_no_skipped_items` fails only on `091: I3 FAIL` (item 071). After this PASS commit it should be green: confirm.
9. Copy 05's `RI-010:` and `RI-014:` guardrail lines into logs/recurring-issues.md on main (item 036).

Evidence: I3 round-2 dir `/tmp/claude-0/-home-claude/6b779538-e393-5b21-a85a-072369e659f6/scratchpad/i3-091-r2-mz28r6tf` holds:
- suite.txt (full suite at head);
- mut.py and mut.txt (F1/F2 mutants);
- probe_repo (F1 probe);
- cp_before.txt and cp_after.txt (check_pipeline output).

Round 1: `.../scratchpad/i3-091-r1-dpe6hf15`. The worktrees under `/tmp/claude-0/scratch/i3-091r2-UxQ8` were removed after the runs.
