# 06 Verification - 090
Verdict: PASS (round 1)
Sent back to: none

Verified by I3 on 2026-11-22 in my own worktree of the head commit 8caffda (`git worktree add /tmp/claude-0/scratch/i3-090/wt 8caffda`, `--is-shallow-repository` false), base d3aa031. All tests, mutations and probes ran there, never in the main checkout (087's I2 was editing tests/test_agent_tools.py there; its commit 7389962 changes no file of 090). Rules: i3-verifier.md is not changed by 090, so the rules in force at the base and at the head are the same for I3. The new run-item rules hold for this step: the clone is full (L12 shallow sentence not triggered), and 090 was never sent back, so rule D applies to my `--log` line (no later step file than 06; 07 does not count) (L17).

## I1 audit (plan vs research)
- 04's Rule trace covers every row of 03's map (steps 1-7), the corrections #10, #13/#43, #22, #25, #33, #41, #46, #48, #49, #51, #53, #56 and the removed claims #20, #21, #26. No dropped rule lacks a reason. Open Q3 (I3 time) and Q5 (single-branch clone) are dropped as out of scope and named in the docstring for A1.
- Fit changes 1-6 are sourced. 1 (FIELDS["I2"] blast radius), 3 (orphan branch for exit 0), 4 (unfilled template lookahead), 5 (equality with one SHALLOW_TEXT; env before open_branches) and 6 (rule text) come from code reading that I re-checked in the head tree. Change 2 (skip origin/main when shallow) rests on the git-branch `--no-merged` text plus 03 #15/#16. Without it, every shallow run would exit 1. M14 shows this: with the skip removed, test_shallow_docs_only_orphan_exit_0 fails (05 table).
- Unsourced additions: none. The run-item L17 and i2-builder L25 edits are the rule-text change for code that changes a rule an agent follows. That is right (001 principle). No rule the person follows (strategy rules) changes.
- One plan error, found by I2 (05 Deviations 4). 03 #56 and 04 say "no line before I2" is impossible for every Scope. A person's `Waived: 01 02 03 04` (item 024's shape) makes it possible. See the I2 audit.

## I2 audit (build vs plan)
I compared the diff `git diff d3aa031 8caffda` with 04's file list line by line.
- scripts/check_pipeline.py has everything 04 lists:
  - the constants TIMED_FROM = 90, I2_TIMED, LOG_HINT_TIMED, SHALLOW_TEXT, VERDICT_OF (03/04 with the lookahead, 06 = VERDICT_LINE) and BATCH_STRICT (equality);
  - `log_fields_ok`/`log_hint` `timed=True`, which write_log does not pass;
  - the `incomplete` TIMED gate on 05 and step 2 `batch_nc`;
  - the per-round bound, placed after the `r[0] is None` check and before `first, last_i2`, skipped for excepted items;
  - `_first_verdict` and `_round_refusal` (a)/(b)/(c), and write_log's `elif sent:`;
  - `_is_shallow`, used by `_anchor_env`;
  - `late_log_lines(shallow)` → False, `main_ahead(shallow)` → None (ref present), and `open_branches(today, shallow=None)` with the MAIN skip, `"shallow"` key and shallow error text;
  - main: env moved above open_branches, batch moved above the item loop, three new print lines, and the exit expression unchanged;
  - the docstring paragraphs for rule D/round, LOG BATCH (x)/(y), LOG TIME, MAIN AHEAD and OPEN BRANCHES.
  `_TAIL`, LOG_FORMAT, the EXCEPT tables, SUITE_FROM and `_rule_seen` are unchanged, as planned.
- The .claude/ files match 04 Files 3-6 word for word (run-item L12 + L17, daily-audit, a1-auditor, i2-builder L25). The UNSHALLOW sentence is the same in all three files (test passes).
- tests/test_pipeline_check.py has the B0 sweep and T1-T20 plus the text pin, as mapped in 05. I read the bodies of T1, T3-T10, T12, T14-T20.
- How I judged the deviations in 05:
  1. **7th file, tests/test_real_data_field.py.** Accepted. It is a mechanical result of B0 (`FIELDS["I2"]` is timed, and this file imports `_item` and hard-coded `Suite: 1 passed`). The diff is 1 import, 1 `SUITE` constant and 2 literals, and no assertion changed. B0 told I2 to sweep the fixtures for the timed field. 04 only missed that a second file imports them.
  2. **Waiver gap.** A person's `Waived: 01 02 03 04` item numbered 090 or higher now shows INCOMPLETE `LOG BATCH not computable: no line before I2 (item 090)`, and no waiver excuses it. **Not a FAIL. It goes to a follow-up item:**
     - It fails loud: a false INCOMPLETE, never a silent pass, so it is on the RI-002-safe side.
     - It is named in the LOG BATCH docstring and pinned by `test_batch_no_line_before_i2_strict_from_090[990]`, which uses exactly that waiver.
     - It touches no real item: 0 items numbered 090 or higher have such a waiver, and the whole-output diff is 0 lines.
     - Excusing it needs a design choice, which this item's map does not contain: which waived steps excuse which reason, and whether a waiver of 01-04 should also lift the per-round bound and the round rule. An I2 patch would be an unsourced addition.
     - Precedent: 024's waiver was the person's, and it is < 090, so it is not affected.
     - Cost of waiting: if the person waives 01-04 on a new item before the follow-up lands, that item stays INCOMPLETE. The person sees this in review.
  3. **Suite guard `timed=False`.** Accepted. Without it, a RULE NOT SEEN TIMED_FROM item would skip its Suite check silently (RI-002). It is pinned by `test_timed_gate_not_seen_keeps_suite_check`.
  4. **`flagged_ids` de-duplicated for the whole-item rule too.** Accepted. It changes no text, only avoids a double ID.
  5. **Unreadable request.md refuses.** Accepted. Defaulting the Scope would break the missing-data policy.
  6. **T2 is a new function.** Accepted. M2 is still killed by `test_i2_tests_field_cutoff`.
  7. **Re-derivation counts 31/15 instead of 30/14.** Accepted. 087's round-2 I1 line (f52ad15) was added during the build.
  8. **Single-branch clone.** Left for A1 (out of scope).
- **Expected failure:** `test_repo_pipeline_has_no_skipped_items`. It fails because of 087's open I3 FAIL round: `087: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))`, `I3 FAIL: 087`. That is the item-071 state, and the base script prints it too (whole-output diff below, 0 lines). 090 shows `in progress (FULL: next 06)` in that same output, and `INCOMPLETE: none`. It is not caused by this build.
- **Connectivity, re-done:**
  - Every new name has a caller (grep counts in the head tree): `_is_shallow` 4, `_first_verdict` 3, `_round_refusal` 4, I2_TIMED 6, LOG_HINT_TIMED 4, BATCH_STRICT 4, VERDICT_OF 6, SHALLOW_TEXT 10, TIMED_FROM 23, batch_nc 5.
  - `scripts/check_handoff.py` L95-96 calls `open_branches()` with no args, and the default computes `_is_shallow` (T20). `python3 scripts/check_handoff.py --all` → `091: PASS`, `no new failures`, exit 0.
  - TODO count: 0.
- **Missing-data grep reasons in 05:**
  - `(batch_nc or {})`: main always passes the dict.
  - `if last is not None and log_fields_ok(..., timed=False)`: the existing guard; a missing line is reported by 043/045.
  - `start = marks[-1] if marks else 0`: the stricter start, as 04 says.
  - My check: the only numeric comparison on data is `round(t - BATCH_ROUND, 3) >= limit`, with t parsed from a matched `\d+\.\d+`. A round with no time `continue`s before it, so a missing time is never read as 0 s.

`python3 scripts/check_handoff.py 090` (run by I3 in the worktree, 2026-11-22, exit 0):
```
sources count (unique URLs in 01-research.md): 10
fact-check rows: 57
totals line: 57 rows -> 42 as-is, 12 fixed, 3 removed
PASS
```

## Tests re-run (output)
Full suite, my own run: `python3 -m pytest -q -rs` in /tmp/claude-0/scratch/i3-090/wt at 8caffda, made after 05 existed. Last lines:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1 failed, 758 passed, 1 skipped in 85.68s (0:01:25)
```
These are the same counts as 05's Suite line (`1 failed, 758 passed, 1 skipped in 83.34s`). The one failure is the 087 item-071 state explained above.

Oldest Python: `tests/test_safety.py::test_every_py_compiles_on_oldest_python` → `1 passed` (python3.11 is on PATH, python3.10 is not). It did not skip.

**Whole-output diff (RI-013), in the worktree:** `python3 <d3aa031 check_pipeline.py>` (exit 1) against `python3 scripts/check_pipeline.py` (exit 1), on the same tree. `diff` exit 0, 0 lines of a 112-line output.

**Guardrail would have caught the original errors.** I put d3aa031's scripts/check_pipeline.py in the worktree, ran 14 of the new tests, then restored it with `git checkout` (status clean). Result: `13 failed, 1 passed`. The one that passed is the 089 twin, which expects no change. Among the failures:
- test_log_i2_untimed_refused_from_090: the base writes an untimed 990 line (086 audit finding 2).
- test_batch_not_computable_strict_from_090[990-True]: "not computable" exits 0 on the base.
- test_round_bound_round2_batch: a Δ0 round-2 I2 is not flagged, because the base has no per-round bound (gap y).
- test_round_content_refusal (all 7 cases) and test_round_069_shape: rule D is off after a send-back.
- test_shallow_three_readers_not_checked and test_shallow_docs_only_orphan_exit_0: on the base, the depth-1 output is `LOG TIME: none`, a false MAIN AHEAD count and "no common history". That is A1's 081 F2.

**Mutations (my own driver, `/tmp/claude-0/scratch/i3-090/mutate.py`):** each one edits the worktree's scripts/check_pipeline.py, runs `-k <targets>` and restores the file. Final `git status --porcelain` in the worktree: clean.
```
Morig_late: 2 failed, 359 deselected in 2.64s | failed: test_shallow_three_readers_not_checked, test_shallow_docs_only_orphan_exit_0
Morig_ahead: 2 failed, 359 deselected in 2.62s | failed: test_shallow_three_readers_not_checked, test_shallow_docs_only_orphan_exit_0
M1_untimed_ok: 2 failed, 1 passed, 358 deselected in 0.59s | failed: test_log_i2_untimed_refused_from_090, test_timed_gate
RI002_D_off_restored: 10 failed, 9 passed, 342 deselected in 1.57s | failed: test_round_content_refusal[06-pass], [03-ready], [04-fit], [04-unfilled], [06-earlier-fail], [06-unreadable], [06-absent], test_round_open_refuses_later_step, test_round_069_shape, test_round_unreadable_log_refused
RI002_nc_text_only: 2 failed, 2 passed, 357 deselected in 0.51s | failed: test_batch_not_computable_strict_from_090[990-True], test_batch_no_line_before_i2_strict_from_090[990-...]
M8_no_round_close: 1 failed, 360 deselected in 0.21s | failed: test_round_069_shape
M10_unreadable_ok: 3 failed, 4 passed, 354 deselected in 0.69s | failed: test_round_content_refusal[04-unfilled], [06-unreadable], [06-absent]
M16_no_c: 1 failed, 360 deselected in 0.35s | failed: test_round_069_shape
M6_prev_first: 2 failed, 6 passed, 353 deselected in 0.32s | failed: test_round_bound_round2_batch, test_round_bound_end_to_end
M_bound_gt: 1 failed, 1 passed, 359 deselected in 0.16s | failed: test_round_bound_delta0_boundary[60.01-True]
```
The mutations work like this:
- Morig_late and Morig_ahead put back the original bug (blame and the HEAD..main count run in a shallow clone).
- RI002_D_off_restored puts back the removed "D is off after a send-back" pass (`elif sent:` → `elif False:`).
- RI002_nc_text_only puts back "not computable is text only".
- M1_untimed_ok accepts an untimed field from 090.

Each mutation fails at least one named test.

**Edge and RI-012 probes** (my own file `/tmp/claude-0/scratch/i3-090/probe/test_i3_probe.py`, outside the repo, imports the worktree's helpers): `5 passed in 1.92s`.
- After the last value: an I2 at Δ0 with 70.00 s and no I3 after it (an in-progress item) is flagged. The bound runs before the in-progress skip.
- Before the first value: an I2 that is the item's first line, with 999.00 s, gets no round flag and is `not computable: no line before I2`, never read as 0.
- Midnight: I1 at 11-20 23:59 and I2 at 11-21 00:00 give Δ1 and limit 120. 119.00 s is not flagged; 120.01 s is flagged.
- RI-012:
  - `tests 5 passed (rerun in 3.21s)` for 090 is refused: the time is inside the note.
  - A 03 with `<!-- Status: BLOCKED -->` and then `Status: READY (was BLOCKED)` reads READY. `--log R1` is refused with `no longer says BLOCKED (READY)`.
  - In the repo, `test_round_content_refusal[06-earlier-fail]` (`Verdict: PASS (round 2; earlier rounds: FAIL)`) is the negative test with the pattern inside other text, and it passes.

**BUG checks:**
- The fix and its guardrail tests are both in place (above).
- RI-001: I re-ran the feasibility counts.
  - `test_round_bound_on_repo_data` passes: 0 of the real rounds get an `item 090)` flag.
  - The whole-output diff is 0 lines: 0 items numbered 090 or higher with an I2 line, and 0 of 7 not-computable items numbered 090 or higher.
  - 05's re-derivation numbers match 03's Self-check: 17 rounds with max ratio 0.3066 (077 r2, 91.97/300). The 31 and 15 replay lines include 087's new line.
  - The rule text (docstring and run-item) says "with today's 74-93 s runs, same-minute (Δ0) batches". That matches the 17-round range 74.44-92.66 s.
- RI-002 mutation: done above (D-off restored → 10 failed; text-only restored → 2 failed).
- Data-hole edges: done above (before the first line, after the last, across midnight).
- The rule an agent follows changed in the same item (run-item L12/L17, i2-builder L25, daily-audit, a1-auditor; text pin `test_i2_and_run_item_texts_name_item_090`). No 001 strategy rule changed.
- Item 062 (simulator/pickers): not applicable. No simulator or replay of the bot's rule.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat d3aa031 8caffda`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, logs/implementation/2026-11-22.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py, work/090/05-build-report.md; no TRIGGER or TRIGGER_DIRS path)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-012, RI-013, RI-008. What I checked for each:
- **RI-001 (ESCALATED).** Every filter, window and refusal has a re-run count: the repo bound test passes, the diff is 0 lines, and there are 0 strict items. The rule text's "74-93 s, Δ0" matches the 17 rounds. Nothing says "always".
- **RI-010 (ESCALATED).** This item. Δ0 rounds are flagged after a send-back, the untimed field from 090 is refused, not computable from 090 is INCOMPLETE, and the round rule (a)/(b)/(c) is in place. Each part is killed by a mutation. Known open (docstring): I3 is untimed, a repeat FAIL, A1 FAIL rounds get (c) only, Δ ≥ 1 batches, and the person-waiver gap (follow-up). Guardrail status for A1 to copy on main: as 05's RI-010 line. It stays ESCALATED until 090 is merged and an A1 probe on main flags test_round_bound_round2_batch's shape.
- **RI-014 (OPEN).** This item. In a depth-1 clone the three not-checked lines are printed, origin/main is not listed, and the exit is pinned at 0 and 1. The full-clone control is unchanged. Morig_late and Morig_ahead fail both shallow tests. Guardrail status: as 05's RI-014 line (GUARDED when 079, 081 and 090 are merged and M11 fails on main).
- **Also checked (GUARDED):**
  - RI-002: the two restore-the-default mutations above.
  - RI-012: verdicts are fullmatched or taken from their group with the lookahead, and the negative probes above pass. BATCH_STRICT and SHALLOW_TEXT are equality checks on the script's own fixed strings.
  - RI-013: the whole-output diff is 0 lines.
  - RI-008: the compile test passed on python3.11.

## Pipeline line (step 2)
check_pipeline line: `090: awaiting A1 (FULL)`

Run in the main checkout at 01:01 UTC, after this file and my `--log` line were written. The script exits 1 only because of `I3 FAIL: 087` (item 071, another item). For 090 it shows `INCOMPLETE: none`, `SKIPPED: none`, `LOG TIME: none` and `LOG BATCH: none` (090 is not named), and `UNTRACKED CHANGE: none`.

## Sent back / sent to Audit
Sent to Audit (07-audit-task.md). Proposed follow-up item (for A1 to open, BUG/EFFICIENCY, not part of 090): **a person's `Waived: 01 02 03 04` on an item numbered 090 or higher gives INCOMPLETE `LOG BATCH not computable: no line before I2 (item 090)` with no excuse.** Decide whether a person's waiver of the steps before I2 excuses that reason, and whether it also lifts the per-round bound and the round rule for that item. Then pin it with the `test_batch_no_line_before_i2_strict_from_090[990]` fixture flipped. 03 #56 / 04's "impossible for every Scope" was wrong for waivers.
