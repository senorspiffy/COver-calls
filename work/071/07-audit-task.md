# 07 Audit task - 071
Item: 071 (EFFICIENCY, Scope FULL, RULES change). Build commit ba78fb0 on daily-fixes/2026-11-18. I3 PASS (06, round 1).

What Audit should look at:
1. Person's OK: scripts/check_pipeline.py, templates/verification.md, .claude/agents/i3-verifier.md and .claude/agents/i2-builder.md are RULE_PATHS. Confirm that the PR shows as RULES BRANCH once pushed and that the person approves it.
2. Request met ("Done looks like"):
   - A 06 whose first Verdict line is FAIL gives `<ID>: I3 FAIL (<scope>; sent back to <t>, needs a later PASS round in 06 (item 071))`, `I3 FAIL: <ID>` and exit 1.
   - A later PASS round clears it (T2).
   - Old 06 files without round headers are unchanged (T3).
   - Re-run on main after merge: `python3 -m pytest -q tests/test_pipeline_check.py -k "i3_fail or later_pass or sent_back_none or i3_verdict or verdict_disagrees or old_06 or template_lines or malformed_last or item_071"` should give 30 passed.
3. Mutation spot-check on a scratch worktree of main after merge: re-run one of m12 (target defaults to I2, T6 should fail), m15 (last well-formed line, T12) or m17 (HH:MM sort, T2). My script: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/mut071.py (scratch, may be gone). All 17 failed their named tests at ba78fb0 (06).
4. C1 strictness (04's addition beyond 03): from 071, every 06 PASS needs `Sent back to: none`. 072, 073 and 071 itself comply. Check that 074's 06, when written, also does. Otherwise it shows INCOMPLETE (intended, fixed by 074's own I3, never by editing 074's file from another item).
5. Interaction with 073's text: i3-verifier.md step 2 (073) and step 5 (071), and the template's `## Real-data effect` sentence (073) plus lines 2-4 (071), are all intact at ba78fb0. Greps: `item 073` in i3 1, `same dirs` in the template 0, and t23 passes in the full suite.
6. Known gaps named in the docstring, for the efficiency list:
   - (w) 06 FAIL with a 07 A1 PASS: _open_at treats the item as closed.
   - (x) open branches report only SKIPPED, not I3 FAIL.
   - (y) below 071 an unreadable verdict is not checked.
   - (z) the line proves what I3 wrote, not that I3 ran.
   - The fence rule does not track `~~~` (0 such fences in 06 files today).
   - Decide whether any of these needs an item.
7. RI-010: T13 pins the i3 step-5 and i2 step-3 sentences. On the first real I3 FAIL round after merge, check that its 06 lines 2-3 were updated and that check_pipeline showed `I3 FAIL: <ID>`, not `in progress (next 07)`.
8. RI-001 counts for the record: 69 06 files at check time, 69 PASS, 0 FAIL, 0 unreadable. 03/04's 67 plus 072 and 073.
9. Minor wording: in the check_pipeline.py docstring, the C2 parenthetical and "(logs/implementation, by file date then line order)" sit back to back. The meaning is unchanged, so this is cosmetic only.
