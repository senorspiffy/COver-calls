# 07 Audit task - 078
Build commit: e4c19dd (scripts/probe_guardrails.py, tests/test_probe_guardrails.py, .claude/agents/a1-auditor.md). I3: PASS round 1 (06).

What Audit should look at:
1. The 074 surviving mutant is dead. On a scratch copy of the branch head, apply `classify` `== "failed"` → `!= "passed"`. It must fail `test_skip_entry_and_json_cases` and `test_classify_missing_or_bad_junit` (I3: 2 failed, 8 passed). Also re-run a sample of mutants B-E and G/H (06 table).
2. Run `python3 scripts/probe_guardrails.py --ref origin/main` after merge. It must print `TOTAL: 9 probes, 9 hold, ...`, exit 0. Check that the `recorded` field shows the shipped values (05's pastes show `@REC_*@` placeholders because the values were taken from that run; I3's run at e4c19dd shows the final values).
3. `recorded` for the 4 check_pipeline probes holds main's counts (e.g. `1 failed, 89 passed`). On the branch, test_pipeline_check has 213 tests, so `recorded` and the live counts differ there until 076/077 merge. Decide whether `recorded` should be refreshed once 076/077 are on main (print-only, and no verdict depends on it).
4. Weak spot in the basename check: `test_shipped_probes_well_formed` checks only that the basename appears somewhere in the reason. A mutant that removes one of two occurrences survives (I2's first F and I3's F2). It is accepted per plan. Decide whether an EFFICIENCY item is worth it.
5. Deviation accepted by I3: the 4 check_pipeline entries share the `_CP_REASON` constant. Its value is byte for byte the 03 step 5 reason.
6. Runtime: a1-auditor.md now says "about 4 minutes". Measured on main: 226.7 s (I2), 244.2 s (I3, partly loaded). The HEAD branch run is longer (278-336 s) because the branch's test_pipeline_check is larger. Watch the main time grow when 076/077 merge.
7. RULES change: .claude/agents/a1-auditor.md runtime sentence. Needs the person's OK in PR review.
8. Copy the guardrail status lines in 05 (RI-002, RI-007, RI-009, RI-010, RI-011, RI-012) to recurring-issues.md on main (item 036). RI-014 stays OPEN (079). 079 must keep the N1/N4/N5/N6 anchors at count 1, or update the entries with a HOLDS in its own 05.
9. Re-run the whole suite (I3 at e4c19dd: 556 passed, 1 skipped) and the python3.11 compile test.
A1 result: PASS (2026-11-20, logs/audit/2026-11-19-078.md; worktree 32b16fb: suite 556 passed 1 skipped, python3.11 compile ok, probe_guardrails --ref origin/main 9 of 9 HOLDS exit 0, 074 surviving mutant A and mutants B-E, G plus 3 own each fail their named test; follow-up P1 recorded-label check (EFFICIENCY))
