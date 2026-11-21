# 07 Audit task - 082
Build commits: daa5d22 (round 1: scripts/check_pipeline.py, scripts/probe_guardrails.py, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_real_data_field.py, templates/build-report.md, .claude/agents/i2-builder.md, .claude/agents/a1-auditor.md, .claude/commands/run-item.md) and 85bf4c4 (round 2: tests/test_pipeline_check.py +11, fixture S14). I3 verdicts: FAIL in round 1 (finding 1: no negative test for `Suite:` inside other text), PASS in round 2 (06).

What Audit should look at:
1. The guardrail. After merge, in a scratch worktree of main, apply the RI-006-082-suite probe (`elif suites[0] != field:` compare removed). `test_suite_line_dropped_middle_is_incomplete` must fail. I3 measured 5 failed at the scratch commit: see 06 Probes. Run `python3 scripts/probe_guardrails.py --ref origin/main` and expect 10 of 10 to hold, with no `(live differs)` and no `(recorded unreadable)` marker.
2. RI-012 / item 059, the round-1 finding. Put back `"Suite:" in line` and, separately, `line.lstrip().startswith("Suite:")` in `_suite_lines`. `test_suite_inside_other_text_is_not_read` (S14) must fail under each. I3: 2 failed, 303 passed each, against ctl 1 failed, 304 passed, where the 1 was the then-expected repo test.
3. The plan's equivalent mutant `state != "in"` survives (05 deviation 2, confirmed by I3 in round 1). Decide whether that needs anything. I3's view: no, because a fence line never starts with `Suite:`.
4. SUITE_FROM = 87, so the check applies from item 087 on. Check that the first 087+ item's 05 has exactly one column-0 `Suite:` line equal to its I2 tests field. Also check that the 084 gate (`_rule_seen(..., "SUITE_FROM", ...)`) gives RULE NOT SEEN for an 087+ 05 added under a rule file without SUITE_FROM (S13).
5. Process text (RULES change, needs the person's OK in PR review), additions only:
   - .claude/commands/run-item.md: the commit-subject rule `Item <ID>: ` + the step's `--log` line. The round-2 commit 85bf4c4 follows it, and daa5d22 predates it.
   - .claude/agents/i2-builder.md: the Suite sentence.
   - .claude/agents/a1-auditor.md: the marker clause and the unshallow sentences, pinned in 3 files by `test_unshallow_sentence_same_in_three_files`.
   - templates/build-report.md: the Suite line.
6. probe_guardrails.py `recorded` markers: they are information, never a verdict (a1-auditor.md text). The test_pipeline_check `recorded` values from 078 (`89 passed`) differ from live totals (303/304) in their passed count only, so no marker is printed. Confirm that the failed counts still match on main.
7. RI-006 status: 05 says "RI-006: guardrail built (082); the Suite compare is probed by RI-006-082-suite (HOLDS, run 2)." Copy it to logs/recurring-issues.md on main (item 036) once the probe holds on main. RI-012: no new occurrence. The 082 gap was caught by I3 before merge, so it is a near miss and not counted.
8. Re-run the whole suite. I3 at 85bf4c4: `1 failed, 672 passed, 1 skipped`, where the 1 is `test_repo_pipeline_has_no_skipped_items` from 082's then-open FAIL, which this PASS clears. Also re-run the python3.11 compile test (python3.10 absent).
A1 result: PASS (2026-11-21, logs/audit/2026-11-21-082.md)
