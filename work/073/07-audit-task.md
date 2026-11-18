# 07 Audit task - 073
Item: 073 (IDEA, Scope FULL, RULES change). Build commit 5f3f6bb on daily-fixes/2026-11-18; I3 PASS (06, round 1).

What Audit should look at:
1. Person's OK: .claude/agents/i3-verifier.md, .claude/commands/run-item.md and templates/verification.md are RULE_PATHS. Confirm the PR shows as RULES BRANCH once pushed and the person approves it.
2. Text matches the person's choice ("Always own run", request.md): the i3 step-2 sentence and the run-item sentence both say I3's head run is its own, in a new `--out`, never 05's head run (I2's or the orchestrator's), re-run if cut off, only the base reusable. Check the wider scope (TRIGGER + TRIGGER_DIRS, D1) is what the person wants. The person asked only about "full realtest run" items.
3. Merge with 071: 071 (built after 073 on the same branch) edits i3-verifier.md step 5 and templates/verification.md (`Sent back to:` line) and check_pipeline.py. Check that 073's three sentences survive 071's build intact: `python3 -m pytest -q tests/test_real_data_field.py -k t23` = 3 passed at the branch head, and the 9 greps in 06 still give the same counts.
4. Mutation spot-check: re-run one of m1-m3 (06) on a scratch worktree of the branch head and confirm t23 fails.
5. Follow-ups for the efficiency list (05 `Follow-ups for A1`): (a) a check_pipeline check that 06's head-run `--out` dir differs from 05's and the run was logged after 05's commit (D3, after 071 lands); (b) G1, widen I2's full-run trigger from ccbot/realtest.py to TRIGGER/TRIGGER_DIRS so 05 and 06 TOTALs are comparable for non-realtest trigger items. Copy both to logs/efficiency/ on main.
6. RI-010: this is still a text-only duty enforced only by a text-pin test (t23 proves the sentence exists, not that I3 follows it). On the first future TRIGGER item, check that its 06 names an I3-own `--out` dir, worktree, log file and wall time different from 05's.
7. Minor: 05 marks RI-004/RI-005 "not applicable" though 04 replayed the 068 worked example; no effect on the build.
