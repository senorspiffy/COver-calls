# 04 Build plan - 071
Fit verdict: FIT WITH CHANGES

Fit check. This is a process item. It has no strategy, cost, broker or ~$3k-account effect: nothing in ccbot/, config/, data/, reports/ or rule 001 changes, and nothing places an order. No rule the person follows in 001 (slack, tolerance, cap) changes, so no 001 text update and no new request. It is a RULES change (scripts/check_pipeline.py, templates/, .claude/ are RULE_PATHS), so the person must OK the PR. It fits the built code. It copies 042's A1 FAIL pattern (anchored read, a status, a summary line, exit 1). It reads 06 with the same comment/fence rule as `_field_gap` (070). The INCOMPLETE entries use 043's `incomplete()`, and the cross-check uses 045's LOG_LINE/LOG_FORMAT. I1 re-read every code anchor below on daily-fixes/2026-11-18 (2026-11-18). Each one occurs exactly once (Grep): `WHOLE_DIFF_FROM = 70` L180, `def _is_code` L260, `if len(have) == len(need):` L315, `return missing` L347, `if status in ("STUCK", "not started", "in progress"):` L796, `if status == "A1 FAIL":` L810, `print(f"A1 FAIL:` L841, `return 1 if skipped or failed` L859.

Build order on this branch: 072 (being built), then 073, then **071**, then 074. Every edit below uses a text anchor, not a line number, so it still holds after 072's and 073's edits.

Changes against 03:
1. **C1: from 071, a PASS also needs `Sent back to: none`.** 03 D4 reads the field only on FAIL. That leaves a stale field unchecked. Example: round 1 is FAIL with `Sent back to: I2`, and round 2 rewrites line 2 to PASS but forgets line 3. The orchestrator also asked that every 06 from 071 on carries the field. New INCOMPLETE entry (d): for ID ≥ VERDICT_FROM, a readable PASS whose first `Sent back to:` line is missing, unreadable or not `none` gives `06 Verdict is PASS but has no 'Sent back to: none' line (item 071)`. So the field is always present, and a FAIL round edits a line that already exists. Fixtures for ID ≥ 71 (T2 and `_item`) get `Sent back to: none` on line 3. New test T11, new mutation m14. Today it changes 0 items (0 items ≥ 71 have a 06).
2. **C2: the cross-check uses only a well-formed last I3 line, with no fallback.** 03 D6 says "starts with PASS or FAIL". The plan reads the item's last `| I3 | <ID> |` line and takes the first word only when the whole field fullmatches `LOG_FORMAT["I3"]`. If the last line is malformed, there is no cross-check; 045's format entry reports that line from 45 on. An earlier well-formed line is never used in its place (RI-002). New test T12, new mutation m15.
3. **C3: the docstring's IN PR entry names I3 FAIL.** Step 4 adds `"I3 FAIL"` to the IN PR tuple. The docstring entry "stuck, not started or in progress here" then becomes "stuck, not started, in progress or I3 FAIL here". T8 pins the behaviour.
4. **C4: `.match`, not `re.prefixmatch`.** The Python docs now list `re.match` as soft-deprecated since 3.15 in favour of `prefixmatch()` (Extra research 2). `prefixmatch` does not exist on 3.10, which the project supports (RI-008), so the code keeps `.match`/`.fullmatch`.
5. **C5: one text-pin test for the two agent sentences (T13).** This follows the pattern 072 and 073 use for text duties (RI-010).
6. **C6: more tests and mutations.**
   - One more T4 case, the 9th None case: an unclosed ``` fence, then `Verdict: PASS`, gives None. It pins 03's Missing-inputs row "Unclosed fence", which had no test.
   - m17 pins 03 D6's "by file date, then line order" rule across UTC midnight, which T2 already sets up.
   - m16 (SENT_BACK `.match` in place of `.fullmatch`) is already covered by T4.

## Extra research (with sources)
1. **Fence rule versus CommonMark.**
   - The spec: a code fence is "a sequence of at least three consecutive backtick characters" or tildes. It may be indented up to three spaces, and "the closing code fence must be at least as long as the opening fence". An unclosed fence runs to the end of the document (https://spec.commonmark.org/0.31.2/#fenced-code-blocks, fetched 2026-11-18).
   - The planned reader copies `_field_gap`'s rule, `line.lstrip().startswith("```")`, so the script has one fence rule. That rule differs from the spec in two ways: it does not track `~~~` fences, and a line starting with three backticks inside a four-backtick fence toggles it.
   - Today's files: Grep `^\s*~~~` over work/*/06-verification.md gives 0 hits (2026-11-18). All 73 column-0 `Verdict:` lines sit outside fences, and every file's first one is on line 2, above any fence (I1 Grep, 2026-11-18: same 67 files and 73 lines as 03).
   - So the gap cannot change a status today. It is named in `i3_verdict`'s docstring.
2. **`re` semantics the regexes rely on** (https://docs.python.org/3/library/re.html, fetched 2026-11-18).
   - `\b` is "the boundary between a `\w` and a `\W` character". So `Verdict: PASSED` and `Verdict: PASS_1` do not match (D2 keeps these unreadable), while `Verdict: PASS-ish` reads PASS. Accepted: the first word is PASS.
   - `(?!...)` "matches if `...` doesn't match next". The engine tries every length of `[ \t*]*` inside the lookahead. So `**PASS** |` is rejected through any number of `*` or spaces before the bar. This confirms 03's Self-check rows.
   - `fullmatch` needs "the whole string", which is what makes `Sent back to: I2 (tests only)` unreadable.
   - The page marks `re.match` soft-deprecated since 3.15 in favour of `re.prefixmatch()` (C4).
3. **A stale field (C1).** In the recorded multi-round items, header text was not always kept current: 03 row F16 shows that 070 L2 still says "round 2" although round 3 exists. A second header line is just as likely to go stale, so it is checked on PASS too.
4. **How the new rule treats 071-074's own 06 files.** All four IDs are ≥ VERDICT_FROM (71), and their 06 files will be written after 071 is in the tree (orchestrator). For each of them:
   - **Verdict line.** The first column-0 `Verdict:` line outside fences and comments must read PASS or FAIL, case-sensitive, with `**bold**` allowed. Otherwise the entry is `06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071)`: INCOMPLETE, exit 1.
   - **Sent back field.** The first column-0 `Sent back to:` line must be `none` on PASS (C1) and `I1`, `I2` or `I1 I2` on FAIL. Otherwise the entry is (d) or (b): INCOMPLETE.
   - **Log agreement.** The item's last well-formed I3 log line must have the same first word as the verdict, or the entry is (c): INCOMPLETE.
   - **FAIL rounds.** A FAIL round shows `<ID>: I3 FAIL (FULL; sent back to <step>, needs a later PASS round in 06 (item 071))` and gives `I3 FAIL: <ID>` and exit 1 until a later round rewrites both lines to PASS / none. That is expected, and I3's own step-2 line shows it (i3 step 5 text).
   - **Template.** Written from the new template (lines 2-3: `Verdict: PASS (round 1; earlier rounds: none)` and `Sent back to: none`), a PASS round needs nothing else.
   - **06 written before 071 lands.** If a 06 for 072 or 073 is written before 071 is built, it lacks line 3, and it becomes INCOMPLETE (d) once 071 lands. That is intended: it is fixed by that item's next I3 round, never by I2 of 071 editing another item's file. I2 of 071 records `Glob work/07[1-4]/06-verification.md` before committing (expected 0) and lists any hit in 05 for the orchestrator.

## Files to create/change
Files planned: 6 (6 changed, 0 new). Not changed: .claude/commands/run-item.md (072 and 073 own their paragraphs; L14's "the step named in the file" is now the `Sent back to:` field), a1-auditor.md (074), README.md, scripts/check_handoff.py, logs/ history, 001.

1. **scripts/check_pipeline.py** (not shared: 072, 073 and 074 do not edit it).
   - a. **Constants.** Directly after the line `WHOLE_DIFF_FROM = 70`, add 03's step-1 constants word for word: the 3 comment lines, `VERDICT_FROM = 71`, VERDICT_LINE and SENT_BACK_LINE.
   - b. **`i3_verdict(path)`.** Directly before `def _is_code`, after `_build_waived`, add `i3_verdict(path) -> (verdict, target)`, as 03 "i3_verdict" describes.
     - Read with `encoding="utf-8"`. Drop `<!--.*?-->` with re.S, then `splitlines()`.
     - A line with `line.lstrip().startswith("```")` toggles the fence and is skipped, and lines inside a fence are skipped.
     - The first line with `line.startswith("Verdict:")` sets `m = VERDICT_LINE.match(line)`, `verdict = m[1] if m else None` (the file's style, no walrus). That line counts as seen even when it is unreadable, so a later Verdict line is never read.
     - The first `line.startswith("Sent back to:")` line works the same way, with `SENT_BACK_LINE.fullmatch`.
     - Stop when both are seen.
     - Docstring: "Item 071: (verdict, target) from 06; the first column-0 line of each, outside ``` fences and HTML comments, decides, never a later one; None = unreadable. Fences as in _field_gap: ``` only (~~~ is not tracked, 0 in 06 files 2026-11-18)."
   - c. **classify().** Directly before `    if len(have) == len(need):` insert:
     ```python
         if "06" in have:                                    # item 071: before A1's result (D7)
             verdict, target = i3_verdict(item_dir / STEPS["06"])
             if verdict == "FAIL":
                 where = f"sent back to {target}" if target in ("I1", "I2", "I1 I2") else "sent back to: not stated"
                 return "I3 FAIL", f"{scope}; {where}, needs a later PASS round in 06 (item 071){extra}"
     ```
   - d. **incomplete().** Directly before its final `    return missing`, add the following. Call `i3_verdict` once per item and reuse the result for (a)-(d).
     - (a) and (b) as 03 step 3 says, with their exact texts.
     - (d) (C1): for ID ≥ VERDICT_FROM, verdict "PASS" and target != "none" gives `06 Verdict is PASS but has no 'Sent back to: none' line (item 071)`.
     - (c) (C2): applies to every ID (incomplete() already returns [] below CHECKLIST_FROM) with 06 present and a readable verdict.
       - Scan `sorted((logs / "implementation").glob("????-??-??.md"))` (if the folder exists) line by line with LOG_LINE, and keep the last match with `m[3] == "I3" and m[4] == item_dir.name`.
       - If that line exists, set `w = re.fullmatch(LOG_FORMAT["I3"], m[5].strip())`. If `w` matches and `w[1] != verdict`, add `06 Verdict says {verdict}, last I3 log line says {w[1]} (item 071)`.
       - A malformed last line gives no entry here, and an earlier line is never used.
   - e. **main().**
     - In `skipped, stuck, awaiting, in_pr, failed, unfinished = [], [], [], [], [], []`, add `i3_failed` (7 lists).
     - Change `if status in ("STUCK", "not started", "in progress"):` to `if status in ("STUCK", "not started", "in progress", "I3 FAIL"):`.
     - After the 2-line `if status == "A1 FAIL": failed.append(d.name)`, add `if status == "I3 FAIL": i3_failed.append(d.name)`. This sits after the IN PR override, so an IN PR item is not listed.
     - Directly before `print(f"A1 FAIL: ...")`, add `print(f"I3 FAIL: {', '.join(i3_failed) or 'none'}")`.
     - In `return 1 if skipped or failed or unfinished ...`, insert `or i3_failed` after `failed`.
   - f. **Docstring.**
     - After the 2-line `A1 FAIL` entry (ending `later PASS line (exit 1)`), add 03's step-5 `I3 FAIL` entry word for word.
     - In the IN PR entry, change `stuck, not started or in progress here` to `stuck, not started, in progress or I3 FAIL here` (C3).
     - After the INCOMPLETE paragraph (ending `logs/research or logs/implementation.`), add 03's "Item 071" paragraph word for word, with two edits:
       - Replace `or a FAIL with no \`Sent back to: I1|I2|I1 I2\` line, is INCOMPLETE.` with `or a FAIL with no \`Sent back to: I1|I2|I1 I2\` line, or a PASS with no \`Sent back to: none\` line (a stale field), is INCOMPLETE.` (C1).
       - Replace `the first word of the item's last \`| I3 |\` log line` with `the first word of the item's last well-formed \`| I3 |\` log line (a malformed last line is 045's, never replaced by an earlier one)` (C2).
     - Gaps (w)-(z) are unchanged.
2. **templates/verification.md** (SHARED with 073, which replaces only the sentence `I3 re-runs diff_reports.py on the same dirs ...` inside the `## Real-data effect` comment).
   - Anchor: the line starting `Verdict: PASS | FAIL (round <n>` and the line after it, `<!-- On every re-verification, update this line first: it must show the latest round. -->`. Keep the Verdict line as it is.
   - Replace the comment line with 03's step-6 lines 3-4 word for word: `Sent back to: <I1 | I2 | I1 I2 | none>`, then the new comment.
   - Nothing below `## I1 audit` changes. 073's sentence and `from item 070 check_pipeline.py requires` (t7d) stay. The new text contains neither "same dirs" (073's t23 must_not) nor `python3 scripts/` (072's test).
3. **.claude/agents/i3-verifier.md** (SHARED with 073, which appends to step 2 after `run the base too (item 068).`).
   - Anchor: the whole line starting `5. On PASS, write \`work/<ID>/06-verification.md\``.
   - Replace it with 03's step-7 text word for word. Step 2, including 073's sentence, and step 4 are unchanged.
4. **.claude/agents/i2-builder.md** (not edited by 072, 073 or 074).
   - Anchor: the line starting `3. Run the tests and checks listed in the plan.` and ending `(item 068).`
   - Append, after one space, 03's step-8 sentence word for word.
5. **tests/test_pipeline_check.py** (not shared: 072 uses tests/test_agent_tools.py, 074 tests/test_probe_guardrails.py).
   - `_item` gets new parameters `verdict="PASS", sent_back="auto"`. The 06 body is, in order:
     - `Verdict: {verdict} (round 1)\n`, omitted when verdict is None;
     - `Sent back to: {t}\n`, where t is "none" for PASS and "I2" for FAIL when sent_back is "auto", and a given string as is. The line is omitted when sent_back is None, or when it is "auto" and verdict is None;
     - `x\nRecurring issues checked: RI-007\n`.
   - When verdict == "FAIL", the I3 log field is `FAIL | sent to audit: no`.
   - Test 131: replace `.write_text("x\n", ...)` with `.write_text("Verdict: PASS (round 1)\nSent back to: none\nx\n", ...)`, so its exact 043 assertion still ends `line)`.
   - Repo test: after `assert "061: complete" in out`, add `assert "I3 FAIL: none" in out  # item 071`.
   - New tests T1-T8 and T10 as in 03 (T8 uses the branch helpers and NO_GIT), plus T11-T13 below.
     - T2 (C1): each 06's line 3 is `Sent back to: none`, and the `# Round 1` section below it keeps `Verdict: FAIL (round 1)` and `Sent back to: I2`. T2 writes its own R1-R3, I1 and I2 lines (well-formed FIELDS), so `INCOMPLETE: none` holds.
     - T4 imports the module with `_cp()` (as tests/test_real_data_field.py does) and writes each case to `tmp_path / "06.md"`.
6. **tests/test_real_data_field.py** (SHARED with 073, which adds t23 after t7d).
   - Anchor: in `_rd_item`, the string `f"# 06\nRecurring issues checked: RI-007\n{body06}"`. Replace it with `f"# 06\nVerdict: PASS (round 1)\nSent back to: none\nRecurring issues checked: RI-007\n{body06}"`.
   - Nothing else changes, including 073's t23.

## Tests and checks
New tests (in tests/test_pipeline_check.py). T1-T8 and T10 are as in 03 § Tests, with the C1 fixture change in T2. T4 gets the 9th None case, the unclosed fence (C6).
- **T11** `test_pass_without_sent_back_none_is_incomplete` (C1):
  - 180: PASS with `Sent back to: I2` (stale) gives `180 (06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`.
  - 181: PASS with no field gives the same text.
  - 182: PASS with `Sent back to: none` is not in INCOMPLETE.
  - 067: below 71, PASS with `Sent back to: I2`, is not listed.
  - Exit 1.
- **T12** `test_malformed_last_i3_line_is_not_replaced` (C2): item 183, 06 PASS. Its I3 log lines are `12:00 ... FAIL | sent to audit: no` and then `12:05 ... see 06`. Expect `183 (log line for I3 does not match its format (item 045)` present, and `06 Verdict says` absent from the INCOMPLETE line.
- **T13** `test_agent_texts_name_item_071`, parametrized over 2 ids:
  - i3-verifier.md contains `On FAIL write no 07`, `Sent back to:` and `(item 071)`, and no longer contains `5. On PASS, write`.
  - i2-builder.md contains `not a defect of this build (item 071)`.

Counts: 10 plain functions (T1, T2, T3, T5, T6, T7, T8, T10, T11, T12), T4 with 18 ids (3 read + 9 None + 2 skipped + 4 targets) and T13 with 2 ids. That makes **30 new test ids**, of which T8 skips without git.

Commands (I2 pastes real output; I3 re-runs):
- Before-fix probe: write T1, T2, T5 and T11 first. `python3 -m pytest -q tests/test_pipeline_check.py -k "i3_fail or later_pass or sent_back_none"` fails before the code edits.
- `python3 -m pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py`: all pass. test_real_data_field's count is unchanged by 071 (it is the count after 073, which includes t23).
- Full suite `python3 -m pytest -q`: the base on this branch just before 071's edits (after 072 and 073; I2 pastes it), + 30 (29 passed + 1 skipped if git is missing), with no new failure. `tests/test_safety.py::test_every_py_compiles_on_oldest_python` passes (RI-008).
- `python3 scripts/check_pipeline.py` on the real tree. Expect `I3 FAIL: none`, `INCOMPLETE: none` (or only entries that existed before 071, each named), and 071 not SKIPPED. The exit code is as before. 67 06 files read, 67 PASS, 0 FAIL (re-measure, RI-001).
- Greps:
  - `grep -c "I3 FAIL" scripts/check_pipeline.py` ≥ 4 (docstring, classify, IN PR tuple, print).
  - `grep -c "item 071" .claude/agents/i3-verifier.md` = 1 and `grep -c "item 071" .claude/agents/i2-builder.md` = 1.
  - `grep -c "^Sent back to:" templates/verification.md` = 1.
  - `grep -c "same dirs" templates/verification.md` = 0 and `grep -c "item 073" .claude/agents/i3-verifier.md` = 1 (073 intact).
- `Glob work/07[1-4]/06-verification.md` before commit: expected 0. List any hit in 05 (Extra research 4).
- Mutations (I3, one at a time, in a scratch worktree of the branch head, never the repo tree; RI-009): m1-m13 as in 03, plus:

  | Mutation | Fails |
  |---|---|
  | m14: check (d) removed | T11 (180, 181) |
  | m15: cross-check uses the last *well-formed* I3 line | T12 |
  | m16: SENT_BACK_LINE `.match` in place of `.fullmatch` | T4 `Sent back to: I2 (tests only)` |
  | m17: log lines sorted by HH:MM across files instead of by file name, then line | T2 (FAIL 23:50 is taken as last, so a (c) entry appears) |

- `python3 scripts/check_handoff.py 071`: PASS.
- `check_pipeline.py` lines:
  - `LOG TIME:` does not name 071.
  - `UNTRACKED CHANGE: none`, because I2 commits the code, tests, template and agent edits together with 05 (053).
  - `REAL-DATA FIELD:` does not name 071 (no TRIGGER path), so the 05/06 Real-data section reads `not required (<git diff --stat file list>)`.
  - The RULES BRANCH / OPEN BRANCHES lines are pasted.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 1: constants + `i3_verdict` | Files 1a, 1b (C4 `.match`); T4, T10; m1-m5, m11, m16 |
| Map step 2: classify I3 FAIL before L315 | Files 1c (text anchor); T1, T2, T5, T6; m6, m7 |
| Map step 3 (a)(b)(c): INCOMPLETE entries | Files 1d; T3, T6, T7, T12 (C2); m9, m10, m15, m17 |
| Map step 4: main list, IN PR tuple, print, exit | Files 1e; T1, T2, T8, repo test; m8, m13 |
| Map step 5: docstring entry + item-071 paragraph and gaps (w)-(z) | Files 1f (plus C1/C2 wording and the C3 IN PR entry); greps |
| Map step 6: template lines 2-4 | Files 2; T10 |
| Map step 7: i3 step 5 text | Files 3; T13 |
| Map step 8: i2 step 3 sentence | Files 4; T13 |
| Map step 9: `_item`, test 131, T1-T8, T10, repo test | Files 5 (C1: `sent_back` parameter, `none` on PASS) |
| Map step 10: `_rd_item` 06 body | Files 6 (with `Sent back to: none`, C1) |
| Map step 11: verification and mutations m1-m13 | Tests and checks (m14-m17 added) |
| D1: first Verdict line decides, no last-line rule | Files 1b; T2, T4 (unfilled-then-FAIL); m6 |
| D2: case-sensitive | VERDICT_LINE; T4 `pass`; m4 |
| D3: fences and comments | Files 1b; T4 fence, comment and unclosed-fence cases; m5; the `~~~` gap is named (Extra research 1) |
| D4: target only from the `Sent back to:` line, never defaulted | Files 1b, 1c; T6; m12. Changed by C1: from 071 the field is also read on PASS |
| D5: exit 1 + agent sentences | Files 1e, 3, 4; T1, T13 |
| D6: log cross-check, no fallback | Files 1d (c) with C2; T7, T12; m17 |
| D7: precedence after SKIPPED, before A1 | Files 1c anchor; T5; m7 |
| D8: IN PR tuple, open-branches gap (x) | Files 1e, 1f; T8 |
| D9: VERDICT_FROM = 71 | Files 1a, 1d; T3, T6 (066), T11 (067) |
| Overlap with 072-074 | SHARED flags in the Files list; text anchors; build order 072 → 073 → 071 → 074; 073-intact greps |
| Missing inputs rows 1-9 | Guardrail tests, Missing inputs |
| Self-check (VERDICT_FROM, 29/29 agree, 67/73, regex walk-throughs, worked example) | Tests and checks (real-tree run); T4 cases re-use the Self-check lines |
| 071-074's own 06 files (orchestrator) | Extra research 4; Tests and checks (Glob before commit) |

No rule the person follows in 001 changes.

## Guardrail tests
- Feasibility (each filter or window has a dated count in 03 or here, and a test that pins it):
  - VERDICT_LINE, "first column-0 Verdict line": 67 of 67 06 files readable, all 67 PASS (03 F14/F16; I1 re-ran Grep `^Verdict:` 2026-11-18 and got 73 lines in 67 files, each file's first on L2). Pinned by T4 and by the repo test's `I3 FAIL: none`. I3 re-measures with the built code.
  - Cross-check window, "ID ≥ CHECKLIST_FROM with a 06": 29 items (041-056, 058-070), 29 agree (03 Self-check). Pinned by T7 (176 listed, 040 not) and by the real-tree `INCOMPLETE:` line.
  - VERDICT_FROM window, "ID ≥ 71 with a 06": 0 items today (Glob work/07[1-4]/: no 06). This window is a cutoff, so 0 is correct for it today, as WHOLE_DIFF_FROM's was at 070. Its non-zero side is fixture-pinned by T3 (173), T6 (175, 178) and T11 (180, 181), and its below-cutoff side by T3 (065), T6 (066) and T11 (067). It applies to 071-074's own 06 files as soon as they exist (Extra research 4).
  - SENT_BACK_LINE: 0 lines today (Grep `^Sent back to:`), because the field is new. Pinned by the T4 targets, T6, T10 and T11.
- Missing inputs (each has an absent-case test):
  - 06 absent → classify does not read it, and the `in progress (FULL: next 06)`-style lines are unchanged (existing `test_complete_in_progress_and_fast_scope`, 101).
  - Verdict line missing or unreadable → T3 (173 INCOMPLETE, 065 not) and the T4 None cases.
  - `Sent back to:` missing, unreadable or `none` on FAIL → T6 (175, 178, 066).
  - `Sent back to:` missing or stale on PASS (C1) → T11.
  - No I3 log line → existing `test_incomplete_06_and_missing_log_line` (130: `no log line for ... I3`); no (c) entry.
  - Malformed last I3 line → T12.
  - logs/implementation absent → the second half of existing `test_orphan_log_line_is_reported` (folders removed); the I2 check is that its run raises no error.
  - Unclosed fence before the verdict line → T4's 9th None case (C6).
  - I3 FAIL on an open branch → gap (x), docstring only. DROPPED as a test: the branch list reports only SKIPPED by design, as 042 left A1 FAIL.

## Expected result
- `check_pipeline.py` reads 06's first `Verdict:` line. A FAIL shows `<ID>: I3 FAIL (<scope>; sent back to <I1|I2|I1 I2>, needs a later PASS round in 06 (item 071))`, or `sent back to: not stated`. It prints `I3 FAIL: <ids or none>` before `A1 FAIL:` and exits 1. A later round that rewrites line 2 to PASS clears it (T2).
- From 071 on, these are INCOMPLETE: an unreadable verdict, a FAIL with no target, and a PASS without `Sent back to: none`. From 041 on, a verdict that differs from the last well-formed I3 log line is INCOMPLETE.
- On today's tree: `I3 FAIL: none`, no new INCOMPLETE entry, and the exit code unchanged (0 of 67 files FAIL, 29 of 29 agree).
- The template has `Sent back to:` on line 3. I3 writes 06 on PASS and on FAIL, and writes no 07 on FAIL. I2 records a red repo test caused only by I3 or A1 FAIL as expected.
- 30 new test ids pass (T8 skips without git). Each mutation m1-m17 fails at least its named test.
- The PR is a RULES BRANCH, so the person must approve it.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): every filter or window has a dated count: 67/67 readable, 29/29 agree, 0 items ≥ 71 (a cutoff, fixture-pinned), 0 `Sent back to:` lines. I1 re-ran the `^Verdict:` Grep (73 lines, 67 files) and the 06 Glob. I3 re-measures with the built code.
- RI-002 (GUARDED): an unreadable verdict is never PASS, a target is never defaulted, the log never fills a verdict, and a malformed last log line is never replaced by an earlier one (C2).
- RI-004/RI-005: the regex walk-throughs in 03's Self-check were re-checked against the Python `\b`/lookahead definitions (Extra research 2). The T1 detail text was re-derived from Files 1c.
- RI-006: files planned = 6 (listed). New test ids = 10 + 18 + 2 = 30.
- RI-007: Scope FULL, so I1-I3 run. SKIPPED still wins (Files 1c is anchored after the SKIPPED returns). I2 commits the code with 05.
- RI-008: no possessive quantifiers, no `prefixmatch` (C4), no walrus, `encoding="utf-8"` on reads.
- RI-009: shared files flagged, text anchors, build order stated, mutations in scratch worktrees, 073-intact greps.
- RI-010: the status now comes from fields a script reads, and the agent sentences get a pin test (T13).
- RI-011: no branch-diff change.
- RI-012: anchored first-word and fullmatch reads, with negative tests that put the pattern inside other text (T4: mid-line, indented, `**PASS** | FAIL`, `I2 (tests only)`).
- RI-013: no realtest change.
- RI-003: no calendar.

Log fields: FIT WITH CHANGES | 6 files planned
