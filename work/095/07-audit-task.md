# 07 Audit task - 095
Item: 095 (EFFICIENCY, FULL). In a shallow clone, check_pipeline.py now does two things:
- Entries whose rule-seen anchor can't be read go to `INCOMPLETE NOT CHECKED:` and no longer to INCOMPLETE. The exit stays 1.
- Unrelated refs fold into one `shallow clone:` sub-line and at most one summary BRANCH ERROR.

A full clone is unchanged. Build: ed7b80c on daily-fixes/2026-11-24 (base 5bc02ca). I3 round 1 PASS.

What A1 should look at:
1. `_unsure` / `_head_work_files` / `incomplete(..., unchecked, committed)` in scripts/check_pipeline.py:
   - the equality on SHALLOW_TEXT;
   - C1 (an uncommitted step file stays INCOMPLETE);
   - `committed is None` gives not checked, exit 1;
   - only I2 moves out of a format entry;
   - TESTS moves only when every own I2 line passes I2_BEFORE.
2. `main()`:
   - the NOT CHECKED line is printed only when shallow;
   - `or unchecked` in the exit;
   - `folded`, and the per-ref error filter on `isinstance(held, int)`;
   - the summary when k >= 1;
   - a ref with `held` None keeps its own BRANCH ERROR.
3. Re-run mutations M1-M8, M11 and RI002 (06 lists each with its failing test).
4. Coverage gap I3 found (06 I2 audit): the TIMED, LOG BATCH, Suite and round-heading `elif unsure` branches have no test of their own. Replacing the TIMED branch with `elif False` left tests/test_pipeline_check.py green (431 passed, 2 skipped). This fails closed: the entry goes back to INCOMPLETE, exit 1 either way. The plan did not ask for these tests. Decide whether this needs a follow-up item.
5. The new UNSHALLOW sentence, byte for byte, in .claude/agents/a1-auditor.md, .claude/commands/run-item.md and .claude/commands/daily-audit.md. These are RULE_PATHS, so they need the person's OK on merge. 094's single-branch sentence is untouched.
6. Real clone counts (06 step 5, 2026-11-24): depth-1 `--no-single-branch` gives 29 of 29 refs folded and k = 29, so 58 lines become 2. 083 goes to NOT CHECKED with 2 entries. The full-clone old/new diff is empty. Re-check these on a real shallow clone of origin if one is available.
7. Expected repo noise: `test_repo_pipeline_has_no_skipped_items`-style checks may show 097 and 098 as in progress. They are not built yet.
8. RI status to copy on main (05):
   - RI-014: 095 built. M11 still fails T18. It stays OPEN until merged and the probes fail on main.
   - RI-001 and RI-010: unchanged (ESCALATED).
   - RI-002, RI-012 and RI-009: unchanged (GUARDED).
