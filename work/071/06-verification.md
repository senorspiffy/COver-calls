# 06 Verification - 071
Verdict: PASS (round 1; earlier rounds: none)
Sent back to: none
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Build commit: ba78fb0 (base 5f3f6bb). Checked 2026-11-19 UTC in my own detached worktree of ba78fb0 at /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/wt071-i3. I removed it afterwards. Repo HEAD at check time is cf13af8: its only change after ba78fb0 is 073's A1 result (work/073/07, logs/audit). No file under scripts/ or tests/ differs.

## I1 audit (plan vs research)
- 04 Files 1a-1f, 2-6 match 03 Implementation-map steps 1-10, and the 04 Rule trace covers every 03 step, D1-D9, the Missing-inputs rows and the Self-check.
- Exact texts: the step-1 constants, the step-5 docstring, the step-6 template lines and the step-7/8 agent sentences are carried word for word. The only exceptions are the C1/C2 edits that 04 states.
- Additions to 03 (C1-C6). Each has a stated reason or source, so none is unsourced:
  - C1: PASS needs `Sent back to: none`. Reason: a stale line 3 (Extra research 3, 03 row F16 on 070's stale L2). The orchestrator also asked for it.
  - C2: the cross-check uses only a well-formed last line, with no fallback (RI-002).
  - C3: the docstring's IN PR wording matches the tuple change.
  - C4: `.match`, not `prefixmatch`. Sources: the Python re docs and RI-008.
  - C5: the T13 pin (RI-010).
  - C6: the unclosed-fence case, which pins 03's Missing-inputs row, plus m14-m17.
- C1 changes D4 ("read only when the verdict is FAIL"). 04 says so in the Rule trace (D4 row). It is stricter, never looser, so no default was added.
- No 001 rule change and no ccbot/config change, which matches the request (EFFICIENCY, check_pipeline only).

## I2 audit (build vs plan)
I read `git diff 5f3f6bb ba78fb0` line by line against 04:
- 1a: the constants sit directly after `WHOLE_DIFF_FROM = 70`, word for word with 03 (the 3 comment lines, VERDICT_FROM = 71, VERDICT_LINE, SENT_BACK_LINE).
- 1b: `i3_verdict` sits directly before `def _is_code`, with the plan's docstring.
  - It drops comments with re.S and toggles fences on `lstrip().startswith("```")`.
  - It reads the first column-0 `Verdict:` with `.match` and the first column-0 `Sent back to:` with `.fullmatch`. A line seen but unreadable stays None, and the loop stops when both are seen.
  - It uses `encoding="utf-8"`, no walrus and no `prefixmatch`.
- 1c: the I3 block sits directly before `if len(have) == len(need):` and after every SKIPPED return. The text is identical to 04.
- 1d: in incomplete(), the block sits before `return missing`, after the `< CHECKLIST_FROM` early return.
  - It makes one `i3_verdict` call. (a), (b) and (d) are gated by `>= VERDICT_FROM`, with the exact texts.
  - (c) uses the last LOG_LINE match over sorted `????-??-??.md` and then `re.fullmatch(LOG_FORMAT["I3"], ...)`. There is no fallback.
- 1e: there are 7 lists. `"I3 FAIL"` is in the IN PR tuple, the append comes after the A1 FAIL append, the print comes before `A1 FAIL:`, and `or i3_failed` is in the return.
- 1f: the docstring has the I3 FAIL entry and the IN PR wording (C3), plus the Item 071 paragraph with the C1/C2 edits and gaps (w)-(z). I2 re-wrapped the paragraph and says so in 05. The words match 04.
  - Minor, not a defect: in the C2 wording, "(logs/implementation, by file date then line order)" now follows the C2 parenthetical, so two parentheticals sit back to back. The meaning is unchanged.
- Files 2-4: template lines 2-4 match 03 step 6, and 073's sentence is intact. i3 step 5 is 03 step 7 word for word, and step 2 (073) is unchanged. The i2 step-3 sentence is appended word for word.
- Files 5-6: the `_item` parameters, test 131, the repo-test assert and T1-T8, T10-T13 match 04. The count is 10 plain + 18 (T4) + 2 (T13) = 30 ids. `_rd_item` matches.
- File count: 6 files changed, 0 new (`git diff --stat 5f3f6bb ba78fb0 -- . ':!work' ':!logs'`: 6 files). This matches the plan's 6.
- Connectivity, re-done with Grep on the built file:
  - `i3_verdict(` is called at L364 (classify) and L401 (incomplete).
  - `VERDICT_FROM` is used at L402.
  - `i3_failed` is at L855, L886, L916 (print) and L935 (exit).
  - Each new INCOMPLETE text has a fixture test.
  - The plan greps give: `I3 FAIL` 7 (≥ 4); `item 071` in i3 1, in i2 1; `^Sent back to:` in the template 1; `same dirs` 0; `item 073` in i3 1; `python3 scripts/` in the template 0. All as planned.
- Missing-data policy: the grep over the added lines in scripts/ and tests/ (05's pattern plus ` = 0\.0|: float = `) gives 0. `git diff --stat 5f3f6bb ba78fb0 -- ccbot/ config/ data/` is empty. The only `.get(...)` default is in the test fixture (it builds 06 text), as 05 says.
- 05's deviations (probe order, re-wrap, 2 existing 06 files) are stated and harmless. The 2 files are 072 and 073, both read PASS / none (below).

## Tests re-run (output)
All runs are in my worktree of ba78fb0 on Python 3.13.18:
```
$ python3 -m pytest -q
444 passed, 1 skipped in 64.00s (0:01:03)
  SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py
185 passed in 23.11s
$ python3 -m pytest -q tests/test_pipeline_check.py -k "i3_fail or later_pass or sent_back_none or i3_verdict or verdict_disagrees or old_06 or template_lines or malformed_last or item_071"
30 passed, 120 deselected in 1.97s
$ python3 -m pytest -q tests/test_safety.py::test_every_py_compiles_on_oldest_python
1 passed in 0.09s
```
- These match 05: 444 + 1 = 445 = 415 + 30 new ids.
- The oldest-Python compile test ran and was not skipped (/usr/bin/python3.11 is on PATH; python3.10 is not). The skipped test is the existing exchange_calendars import skip, not T8 (git is present, so T8 ran).

`python3 scripts/check_handoff.py 071` (exit 0):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 67
totals line: 67 rows -> 61 as-is, 6 fixed, 0 removed
PASS
```

Mutations m1-m17, run by me. Script: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/mut071.py.
- Each mutation was applied to the worktree's scripts/check_pipeline.py one at a time. Each run was `pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py`, and the original was restored after each. `git status --porcelain` in the worktree was empty afterwards.
- Every mutation fails at least its named test:
```
m1  .search in place of startswith/.match     -> 3 failed: T4 mid-line, indented, unfilled-then-FAIL
m2  lookahead removed                         -> 5 failed: T4 unfilled, **PASS**|FAIL, PASS/FAIL, unfilled-then-FAIL; T10
m3  lookahead (?![ \t]*[|/]) (no *)           -> 1 failed: T4 `Verdict: **PASS** | FAIL`
m4  re.I                                      -> 1 failed: T4 `Verdict: pass`
m5  fence + comment handling removed          -> 3 failed: T4 unclosed fence, fence, comment
m6  last Verdict line in place of the first   -> 2 failed: T2 test_later_pass_round_clears_i3_fail; T4 unfilled-then-FAIL
m7  I3 check moved after the A1 branch        -> 1 failed: T5 test_i3_fail_beats_older_a1_fail
m8  `or i3_failed` dropped                    -> 2 failed: T1 test_i3_fail_shows_and_exits_1; T5
m9  VERDICT_FROM gate removed                 -> 4 failed: T3, T6, T11, repo test
m10 cross-check (c) removed                   -> 1 failed: T7 test_06_verdict_disagrees_with_last_i3_log
m11 "FAIL"/"PASS" in line                     -> 9 failed: T4 first case + 6 more, T2, T10, repo test
m12 target defaults to I2                     -> 1 failed: T6 test_i3_fail_target_not_stated
m13 "I3 FAIL" removed from the IN PR tuple    -> 1 failed: T8 test_i3_fail_with_more_steps_on_branch_is_in_pr
m14 check (d) removed                         -> 1 failed: T11 test_pass_without_sent_back_none_is_incomplete
m15 last *well-formed* I3 line used           -> 1 failed: T12 test_malformed_last_i3_line_is_not_replaced
m16 SENT_BACK_LINE .match                     -> 1 failed: T4 `Sent back to: I2 (tests only)`
m17 I3 lines sorted by HH:MM across files     -> 1 failed: T2 test_later_pass_round_clears_i3_fail
```
(Totals per run: m1 3 failed/182 passed; m2 5/180; m3-m4 1/184; m5 3/182; m6 2/183; m7 1/184; m8 2/183; m9 4/181; m10 1/184; m11 9/176; m12-m17 1/184. Full output: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/mut071.out.)

Live probe (worktree only, then removed):
- I wrote work/071/06 with `Verdict: FAIL (round 1)` and `Sent back to: I1 I2`, then ran check_pipeline.py.
- Output: `071: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))`, `I3 FAIL: 071`, `INCOMPLETE: 071 (no log line for I3)`, exit 1. This is the request's "Done looks like" on the real tree.

Feasibility re-measured with the built code (RI-001). I ran `i3_verdict` over every `/home/claude/cover-calls/work/*/06-verification.md`:
- Result: 69 files, 69 PASS, 0 FAIL, 0 None.
- Targets read: 072 `none` and 073 `none`; every other file has no field (None, not checked below 071). This matches 05.
- 03/04 cited 67. The 2 extra are 072 and 073, written after 03.
- **072's and 073's 06 files read PASS / none with the built code**, so neither is flagged. Their lines 2-3: 072 `Verdict: PASS (round 1)` / `Sent back to: none`; 073 `Verdict: PASS (round 1; earlier rounds: none)` / `Sent back to: none`.
- The cross-check window (41+ with a 06) is in agreement: the worktree run before my 06 gives `INCOMPLETE: none`.

Real tree at ba78fb0 (worktree, before my 06), all lines except the complete/LEGACY item lines (exit 0):
```
071: in progress (FULL: next 06)
073: awaiting A1 (FULL)
074: in progress (FULL: next 05)
STUCK: none
AWAITING A1: 073
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-18 (1 days)
RULES BRANCH: none
ID CLASH: none
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (2026-11-18.md added in f103aa3; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
```

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i2-builder.md, .claude/agents/i3-verifier.md, scripts/check_pipeline.py, templates/verification.md, tests/test_pipeline_check.py, tests/test_real_data_field.py). This is the `git diff --stat 5f3f6bb ba78fb0 -- . ':!work' ':!logs'` file list. No TRIGGER or TRIGGER_DIRS path is touched, so no head run is needed (item 073).

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013
- RI-001 (ESCALATED): every window was re-measured with the built code: 69/69 readable, 69 PASS, 0 FAIL; items ≥ 71 with a 06: 2, both `none`; cross-check `INCOMPLETE: none`. The plan's 67 differs only by 072 and 073, written later.
- RI-002: no default. m12 (target → I2) fails T6. An unreadable verdict is None, never PASS (T4 None cases, m2/m11). There is no log fallback (m15 fails T12). 0 new grep hits.
- RI-003: no calendar.
- RI-004/RI-005: the T1/T6 detail strings were checked against the classify code, and the live probe printed the same shape.
- RI-006: counts come from command output (30 ids, 444+1, 6 files).
- RI-007: SKIPPED still wins: the I3 block sits after every SKIPPED return in classify. Code, tests and 05 are in one commit.
- RI-008: the compile test passed (python3.11), with no `prefixmatch`, no walrus and no possessive quantifiers.
- RI-009: all probes and mutations ran in my own detached worktree, never in the repo tree. 073's text is intact (greps).
- RI-010: the status now comes from fields a script reads, and T13 pins the agent text.
- RI-011: no branch-diff change.
- RI-012: the text match is anchored (`.match` at column 0, `.fullmatch` for the target), with negative tests that put the pattern inside other text: `see 05. Verdict: FAIL`, indented, `**PASS** | FAIL`, `I2 (tests only)`, `x Sent back to: I2`. m1/m3/m16 each fail one of them.
- RI-013: no realtest change, so no effect run.
- Item 062 (simulator pickers): not applicable, no simulator.

## Pipeline line (step 2)
check_pipeline line: `071: awaiting A1 (FULL)`
This is from the repo tree (HEAD cf13af8 = ba78fb0 + 073's A1 result), run after this 06, the 07 and the `--log` line `00:08 | I3 | 071 | PASS | sent to audit: yes` were written. Exit 0. It also printed `I3 FAIL: none`, `A1 FAIL: none`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `REAL-DATA FIELD: none`, `LOG TIME: none (not checked: 048 ...)` and `SKIPPED: none`. 071 is neither SKIPPED nor INCOMPLETE.

## Sent back / sent to Audit
Sent back: none. Sent to Audit: yes (work/071/07-audit-task.md).
