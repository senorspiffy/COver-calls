# 04 Build plan - 082
Fit verdict: FIT WITH CHANGES

I1 had no shell in this run, so I1 ran no git command, no pytest, no `--next-id` and no `check_pipeline.py`. Code facts come from reading `scripts/check_pipeline.py`, `scripts/probe_guardrails.py`, `tests/test_pipeline_check.py`, `tests/test_probe_guardrails.py` and `tests/test_real_data_field.py` on daily-fixes/2026-11-20. When I read them, **081, 084 and 086 were not built yet**: there was no `_rule_seen`, `_git_ok`, `batch_log_items` or `RULE NOT SEEN` in check_pipeline.py, and work/081 and work/086 had no 04 yet. So this plan names functions and quoted text, never line numbers, and it uses 084/04 (written) and 081/03 and 086/03 (READY) for what those items will change. 082 is built after all three. I2 re-reads every function named here in their built code before editing.

The two shell duties that 03 gave I1 move to I2 for that reason (rule trace rows F9 and F34). The `--next-id` value 087 used below was supplied by the orchestrator. I1 did not compute it.

Recurring issues checked (item 013), every open or ESCALATED entry in logs/recurring-issues.md:
- **RI-001** (ESCALATED). The plan adds one selecting rule, the Suite rule. It has a dated real-data count in 03: 4 of 4 items 076-079 already have their last I2 field as a whole line in 05 (R3 Grep, 2026-11-20). Its in-scope count today is 0 of 77 05 files, on purpose (cutoff 87). That empty set is named, and it is pinned by the repo self-test staying green. The two new shallow lines are counted in the self-check: 0 of 2 pass `fullmatch`, 2 of 2 pass `.match`. `RECORDED` is counted as 9 of 9 shipped values. Nothing in the plan says "always".
- **RI-010** (ESCALATED). Points 1 and 3 turn text duties into checks (the Suite compare and the `recorded` format assert plus marker). Points 4b and 5 are text pins and are labelled partial guards here and in 05. I1 writes no log line: it ends with `Log fields:` for the orchestrator.
- **RI-014** (OPEN). The unshallow sentence goes into a1-auditor.md job B and is pinned byte-for-byte in all three files. The two new `.git/shallow` cases keep "unreadable" loud. 082 adds no git call, so 081's call-site census is unaffected.
- Also checked (GUARDED, related):
  - RI-002: an absent Suite line, I2 line, `recorded` value or live count each has a named result and an absent-case test (Guardrail tests).
  - RI-004/RI-005: every fixture string was re-checked against `_STATS`/`_TAIL` and against the mutant it must kill. See Extra research 3 and 4 for two of R3's fixtures that needed changes.
  - RI-006: Suite, `recorded` and every count are copied from command output.
  - RI-007: Scope FULL, nothing skipped.
  - RI-009: mutations run in a scratch worktree.
  - RI-012: whole-string `!=`, `RECORDED.fullmatch`, and no reader of commit text.

## Fit check
- **~$3k account and strategy rules.** This is process-only. No ccbot/, config/ or data/ change, no trade, price, option, ticker or broker input, and nothing connects to a brokerage. No 001 rule the person follows changes (no slack, tolerance or cap), so no rule-text update or new request is needed.
- **Existing code.**
  - The Suite check sits in `incomplete()` beside the 071 verdict block and uses the same readers: `_md_lines` "out" rows, as in `i3_verdict`, and the last log line by file date then line order, as in the 071 I3 cross-check.
  - It conflicts with nothing built, as long as the fixture helpers change (change 1 below).
- **Order today (081 → 084 → 086 → 082).**
  - 081 rewrites `_git` failure handling and adds an AST census of `_git(`/`_git_ok(` calls per function. 082 adds no git call, so the census is unchanged. 082's only git-touching code is the optional call to 084's `_rule_seen`, which is not a `_git` call.
  - 084 gives `incomplete(item_dir, logs, env=None, not_seen=None)` and `_rule_seen(item_dir, step, const, env)`. These are generic per constant, and the call sites are hard-wired per gate (084/04 Files 1). So registering SUITE_FROM is **one call**, the same shape as 084's VERDICT gate (03 row FOR 1(b), "one call" branch).
  - 086 adds `LOG BATCH:` (rule C reads pytest times in 05 `## Test output` and the I2 field) and rule D in `write_log`. Under rule C a `Suite:` line repeats the I2 field's value, so whichever way 086 parses it, the max t05 does not change. Rule D refuses `--log` when later step files exist, which does not touch 082's tests: they call `check_pipeline.py` without `--log`, apart from none new.
  - 084 also adds a run-item.md line after the RULES BRANCH sentence, and 086 edits run-item.md's "At the end, run" paragraph and step list. 082's run-item.md edits are found by quoted text (step (5) and "I2 commits each code change"), so they apply on top of either.
- **Changes to 03 (why "WITH CHANGES"):**
  1. **Fixture helpers must write a Suite line (R3 missed this).**
     - `tests/test_pipeline_check.py::_item` writes every 05 as `"x\n"` and every I2 line as `1 files changed | tests 1 passed`. Grep counts 74 `_item(` calls with IDs ≥ 087 in test_pipeline_check.py and 4 in test_real_data_field.py.
     - With SUITE_FROM = 87, every such fixture with a 05 and an I2 line becomes INCOMPLETE `05 has no 'Suite:' line`. That breaks tests that assert `INCOMPLETE: none` or exit 0, e.g. `test_uncommitted_but_logged_steps_are_quiet` (152), `test_commits_before_cutoff_ignored` (rewrites 150's 05, asserts exit 0) and `test_real_data_field.py::test_t1_filled_field_passes` (`_rd_item` replaces 05).
     - Fix: `_item` always writes 05 as `"x\nSuite: <tests part of _field('I2', item)>\n"`. That is `Suite: 1 passed` from 76 on. Below 76 it is `Suite: 1/1`, which is harmless because it is not checked below SUITE_FROM.
     - `_rd_item` writes `# 05\nSuite: 1 passed\n{body05}`.
     - The direct 05 rewrites for items ≥ 87 keep a Suite line in their new body: `_write(repo, "work/150/05-build-report.md", "x\n## Follow-up\n")` (3 sites), the two `work/153/05-build-report.md` rework writes, and `work/162/05-build-report.md` in test_real_data_field.py.
     - No existing assertion changes. Fixture text only.
  2. **S2 is its own test function**, `test_suite_line_dropped_middle_is_incomplete`, not a parametrize case. `test_shipped_probes_well_formed` checks `def <name>(` from the probe target, and a `[id]` target would not match it.
  3. **One more absent-case fixture each:**
     - S0: 05 with no Suite line at all, and no fence. This is the plain missing-input case. 03's S5 covers only the line inside a fence.
     - W: a probe with a valid `recorded` and no live results gives `(live n/a)`. 03 has no test for that branch.
  4. **Marker order is fixed:**
     - `recorded` absent: no marker, the line prints `recorded: none` as today.
     - Present and not fitting `RECORDED`: `(recorded unreadable)`.
     - Else, no live results: `(live n/a)`.
     - Else, failed differs: `(live differs)`.
     - Else nothing.
     - `test_holds_exits_0`'s `"99 failed"` gives `(recorded unreadable)`.
  5. **SUITE_FROM value.** I1 could not run `--next-id`. The orchestrator gave 087.
     - I2 runs `python3 scripts/check_pipeline.py --next-id` right before writing the constant and sets `SUITE_FROM = max(87, <that output>)`, pasting both in 05.
     - If `--next-id` refuses (081 makes it exit 2 on git failure), I2 stops and reports to I1. It never guesses.
     - If the value is above 87, an item opened since then would otherwise reach the rule, and under 084's gate it would break the RULE NOT SEEN {083} pin.
  6. **Point 5 is scoped to the commit that adds a step's log line.**
     - This covers the orchestrator's step (5) and I2's commit of code + 05 + its log line.
     - An intermediate I2 code commit made before `--log` has no `--log` line to copy. It is named as a gap in the same sentence, not given an invented subject.
  7. **e813e1f subject.** I1 cannot read packed git objects. I2 runs `git log -1 --format=%s e813e1f` and pastes the output in 05. The design does not depend on its wording (03 row F34).

## Extra research (with sources)
1. **`%s` is the subject.** git pretty-formats lists "`%s` subject" and "`%B` raw body (unwrapped subject and body)" [https://git-scm.com/docs/pretty-formats]. So `git log -1 --format=%s <sha>` is the right command for I2's e813e1f check and for any A1 spot-check of point 5. git-commit says the title is the text up to the first blank line (03 row F36, https://git-scm.com/docs/git-commit). A `--log` line is one line, so the subject is that line in full. Log lines run about 80-95 characters, above git's "about 50" suggestion. The docs say that limit is "not required", so no truncation, since truncating would reword.
2. **Probe target naming.** `junit_key` in probe_guardrails.py takes a `[params]` suffix, but `test_shipped_probes_well_formed` asserts `f"def {name}(" in tests` with `name = target.split("::")[-1]`. A parametrized target therefore fails the well-formed test before the probe ever runs. That is why change 2 makes S2 a standalone function (repo code, read).
3. **Fixture-helper breakage (change 1).** This is an edge case R3 missed, found by reading `_item`, `_rd_item` and the 05 rewrite sites (Grep `05-build-report.md".*_write` → 7 sites, 5 of them for IDs ≥ 87). R3's Feasibility counted real 05 files (0 of 77 in scope) but not fixture 05 files, which mostly use IDs 100-199.
4. **Probe baseline.** The new probe's test file is tests/test_pipeline_check.py, whose baseline must be fully green (`_baseline` turns any failed test into `ERROR (baseline: ...)` for every check_pipeline probe). With change 1 in place the baseline stays green. Without it, all 5 check_pipeline probes (4 old + 1 new) would print ERROR. That is one more reason change 1 is required, not optional (probe_guardrails.py `_baseline`, `_run_probe`).
5. **Python `str.splitlines`/`str.strip`.** I tried to quote the stdtypes page (https://docs.python.org/3/library/stdtypes.html). The fetch was cut before those entries, so I make no claim from it. The plan relies only on `_md_lines`' existing `splitlines()` and on `.strip()` of an ASCII line, both already used by `i3_verdict` and `log_fields_ok`.

## Files to create/change
9 files, plus I2's own work/082/05-build-report.md.

1. `scripts/check_pipeline.py`
   - New constant next to `TESTS_FORMAT_FROM`: `SUITE_FROM = <max(87, --next-id at build time)>`, with comment "item 082: from this ID on 05 has exactly one column-0 `Suite:` line equal to the last I2 log tests field; numeric floor above every in-flight item (080-086)". If 084's `_rule_seen` is not present as planned, the comment also names the gap: "an item whose 05 was committed before this constant is judged strictly".
   - New helper `_last_log_line(logs, agent, item)`: the item's last `LOG_LINE` match for `agent` in `logs/implementation/????-??-??.md`, by sorted file name then line order, or None. Used by the Suite block only. The 071 I3 block is not refactored, so 084's anchors and the scope lock stay put.
   - New helper `_suite_lines(text)`: `[line[len("Suite:"):].strip() for line, state in _md_lines(text)[0] if state == "out" and line.startswith("Suite:")]`.
   - In `incomplete()`, after the log-format block (the `if int(item_dir.name) >= LOG_CHECK_FROM:` block, and after 084's TESTS gate if present), add a new block when `int(item_dir.name) >= SUITE_FROM` and 05 exists:
     - `last = _last_log_line(logs, "I2", item_dir.name)`. If None, or `not log_fields_ok("I2", item_dir.name, last[5])`, add no Suite entry (043/045 already report it; never an earlier line).
     - Else `field = last[5].strip().split(" | tests ", 1)[1]` and `suites = _suite_lines(<05 text>)`. Then:
       - `if not suites:` → `05 has no 'Suite:' line (item 082)`
       - `elif len(suites) > 1:` → `05 has <n> 'Suite:' lines, needs exactly 1 (item 082)`
       - `elif suites[0] != field:` → `05 Suite line does not equal the last I2 log tests field (item 082): '<value>' vs '<field>'`
     - The `elif suites[0] != field:` line is the probe anchor. Keep it on one line, and I2 copies it byte-for-byte with its indentation.
     - **084 gate (one call):** only when one of those three reasons would be added, call `_rule_seen(item_dir, "05", "SUITE_FROM", env)`.
       - False: do not add the reason, and append `(ID, "05", sha7, "SUITE_FROM", "082", "no Suite check")` to `not_seen`.
       - True or None: add it, plus any non-empty note as its own entry, as 084's VERDICT gate does.
       - If 084's built helper differs from 084/04, use its built shape. If there is no helper, skip the gate and write the comment gap above.
   - Module docstring: one paragraph after the item-076 `--log` paragraph covering the Suite rule, SUITE_FROM, "no I2 line or a malformed last one: no Suite entry", and "compared as a whole string, ` (note)` included".
   - Do not change `log_fields_ok`, `log_hint`, `write_log`, `_logged`, `_md_lines`, `SHALLOW_LINE`, `FENCE_OPEN` or any 081/084/086 code. Points 2 and 4a are tests only.
2. `tests/test_pipeline_check.py`
   - Helpers: `_item` writes the Suite line (change 1), and the direct ≥ 87 05 rewrites keep one.
   - New tests: S0-S12 (S2 standalone), S13 (if 084's gate is built), T4 `longer-close`, the P5a2 `XR1` line, 2 shallow cases, `test_unshallow_sentence_same_in_three_files`, `test_suite_label_in_template_and_i2_text` and `test_run_item_commit_subject_rule`. Details are under Tests and checks.
3. `tests/test_real_data_field.py`: `_rd_item` writes `Suite: 1 passed` after `# 05`, and the `work/162/05-build-report.md` write keeps a Suite line. No assertion changes.
4. `scripts/probe_guardrails.py`
   - `RECORDED = re.compile(r"\d{4}-\d{2}-\d{2}( \(\d{3}/05\))?: (\d+) failed, (\d+) passed")` (used with `.fullmatch`).
   - `_recorded_marker(p, results) -> str` with the order from change 4. Live failed = `sum(1 for v in results.values() if v == "failed")`, the same count `_counts` prints.
   - In `_probe_all`, `rec` becomes `f"recorded {p['recorded']}{_recorded_marker(p, results)}"` when `recorded` is present. Exit code, verdict and tally are unchanged.
   - The comment "`recorded` is printed only" becomes "`recorded` is printed and compared on its failed count only (item 082: information, never a verdict)".
   - New PROBES entry, appended last: `{"id": "RI-006-082-suite", "ri": "RI-006", "file": "scripts/check_pipeline.py", "anchor": "<the elif line, byte for byte>", "replacement": "<same indent>elif False:", "test_file": "tests/test_pipeline_check.py", "target": "tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete", "no_module_reason": _CP_REASON, "recorded": "<date> (082/05): <f> failed, <p> passed"}`. The value comes from I2's first `--ref HEAD` run.
   - Refresh `recorded` only on entries that print `(live differs)` in that run, copied from it.
5. `tests/test_probe_guardrails.py`
   - `test_shipped_probes_well_formed`: change 9 → 10 in both asserts, add `assert pg.RECORDED.fullmatch(p.get("recorded", "")), p["id"]`, and append the new target to the list.
   - New tests X, Y and W. `test_holds_exits_0` additionally asserts `(recorded unreadable)`. `test_mixed_run_reports_every_probe` additionally asserts that "b"'s line has none of the three markers. A text test pins the a1 clause.
6. `templates/build-report.md`: directly under `## Test output (pasted, not summarized)`, one column-0 line outside any comment: `Suite: <last line of python3 -m pytest -q, as printed; copy it unchanged into the I2 log tests field>`.
7. `.claude/agents/i2-builder.md`: after the sentence "It is the same line you paste in 05 Test output: never retyped, summed or shortened.", add: "05 has exactly one column-0 `Suite:` line, outside code fences and comments, rewritten each round (an earlier round's goes inside a fence or is removed); the log `tests` field is that line's text after `Suite: `, copied unchanged, no backticks (item 082). Write the label inline in backticks elsewhere in 05."
8. `.claude/agents/a1-auditor.md`
   - Job B bullet "Run `python3 scripts/check_pipeline.py` after `git fetch origin`.": directly after that first sentence, insert run-item.md's two unshallow sentences byte-for-byte, from "If `git rev-parse --is-shallow-repository` prints true" through "never 'none' (item 079)." Copy them from run-item.md as it is after 081/084/086.
   - Guardrails paragraph (the one with "Every NOT HELD, ANCHOR MISSING or ERROR line is a finding"): after that sentence, add "`(live differs)`, `(recorded unreadable)` and `(live n/a)` are information, not findings; the verdict word decides (item 082)."
9. `.claude/commands/run-item.md`
   - After "(5) commit the step file and its log line.", add: "The commit that adds a step's log line has the subject `Item <ID>: ` followed by the line `--log` printed for that step, copied unchanged, never reworded (item 082); a commit made before that step's `--log` line has no such subject rule."
   - After "I2 commits each code change together with its 05 change.", add: "Its commit that adds the I2 log line follows the same subject rule (item 082)."
   - The unshallow sentences stay byte-identical.

## Tests and checks
**Step 0 (I2, read-only, before any edit):**
- `python3 scripts/check_pipeline.py --next-id`, which sets SUITE_FROM (change 5).
- `git log -1 --format=%s e813e1f` (change 7).
- `git rev-parse --is-shallow-repository` must print false.
- Grep that `_rule_seen`, `incomplete(... env ..., not_seen ...)` and 084's `RULE NOT SEEN` print exist, to pick the gate branch.
- `python3 -m pytest -q` baseline.
- Paste all of these in 05.

**Order of edits:** first the fixture helpers (change 1) on their own, with the suite green. Then the check. Then the full suite again. A pre-existing test that fails only because a fixture 05 has no Suite line gets the line in its fixture text, and 05 lists each one. Any other failure: stop and report to I1.

**Point 1 fixtures** (plain tmp_path, no git; `_item(root, ID, ALL)` then 05 and the I2 lines overwritten; read the `INCOMPLETE:` line; ID 151 unless stated, `SF = cp.SUITE_FROM`):
- S0: 05 `x\n` (no Suite line) → `05 has no 'Suite:' line (item 082)`.
- S1: Suite `411 passed, 1 skipped in 1.00s`, field the same, ID SF → no Suite entry (151 not in INCOMPLETE).
- **S2** `test_suite_line_dropped_middle_is_incomplete`: Suite `411 passed, 1 skipped in 1.00s`, field `411 passed in 1.00s`, ID SF → mismatch entry with both values quoted.
- S3: field `411 passed, 1 skipped` (dropped tail) → mismatch.
- S4: field `411 passed, 1 skipped in 1.00s (note)` → mismatch.
- S5: the Suite line only inside a ``` fence → `no 'Suite:' line`.
- S6: two identical Suite lines equal to the field → `05 has 2 'Suite:' lines, needs exactly 1 (item 082)`.
- S7: the Suite line read from templates/build-report.md (unfilled placeholder) → mismatch.
- S8: no I2 line (logged files except 05's line) → `no log line for I2`, no Suite text.
- S9: two I2 lines, the earlier `... | tests 410 passed` (well-formed, ≠ Suite `411 passed`) and the last `... | tests 411/411` (malformed) → only the 045 entry, no Suite text.
- S10: ID SF − 1 with a mismatch → no Suite entry.
- S11: two I2 lines, the last equals Suite → none.
- S12: two I2 lines, only the first equals Suite → mismatch.
- S13 (only if 084's gate is built): a git tmp repo in 084 test (a)'s shape. `scripts/check_pipeline.py` = `TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\n` in the commit that adds item 151 (05 with no Suite line, I2 line well-formed) → INCOMPLETE does not name 151, and `RULE NOT SEEN:` names `151 (05 added in <sha7> without SUITE_FROM (082): judged by no Suite check; item 084)`. Control S13b: the same, with `SUITE_FROM = 87\n` in that tree → `151 (05 has no 'Suite:' line (item 082))`. Use `--untracked-from <root sha>`.
- `test_suite_label_in_template_and_i2_text`: the template has exactly one `_md_lines` "out" line starting `Suite: <`, and i2-builder.md contains `Suite:` and `(item 082)`.

**Point 2:**
- T4 gains `pytest.param("```\nVerdict: FAIL (pasted)\n`````\nVerdict: PASS (round 1)\n", ("PASS", None), id="longer-close")`.
- `test_uncommitted_step_with_lookalike_log_lines_is_listed` (P5a2): the log text gains `12:00 | XR1 | 151 | x\n`.

**Point 3:**
- X: `_probe("x", recorded="2026-01-01: 2 failed, 1 passed")` → the line holds `recorded 2026-01-01: 2 failed, 1 passed (live differs)`.
- Y: recorded `2026-01-01: 1 failed, 99 passed` → HOLDS, no marker.
- W: `_probe("w", anchor="nosuch", replacement="x", recorded="2026-01-01: 1 failed, 1 passed")` → ANCHOR MISSING and `(live n/a)`.
- `test_holds_exits_0`: `(recorded unreadable)`.
- `test_mixed_run_reports_every_probe` "b": no marker.
- Exit codes are asserted unchanged: X and Y exit 0, W exit 1 (as today for ANCHOR MISSING).
- Shipped format assert as in Files 5.
- `test_a1_text_marks_probe_markers_as_information`: a1-auditor.md contains the new clause.

**Point 4:**
- `test_shallow_file_unreadable_not_checked` gains `.git/shallow` = `c + "\n" + c + "x\n"` → "unreadable", and `= c + "\n" + "a" * 41 + "\n"` → "unreadable".
- `test_unshallow_sentence_same_in_three_files`: SENT = the two sentences as one string constant, and `count(SENT) == 1` in run-item.md, daily-audit.md and a1-auditor.md.

**Point 5:** `test_run_item_commit_subject_rule`: run-item.md contains the step-(5) sentence once and the I2 sentence once. 05 says in plain words that this is a partial guard: no check reads commit text (062, RI-012).

**Mutations** (I2 runs them in a scratch worktree and pastes the real fail counts; I3 re-runs). Each must fail the named test:
- Compare removed → S2.
- `field in suite` → S3.
- `suite in field` → S4.
- First-wins or last-wins instead of exactly one → S6.
- Fence ignored (`state != "in"` instead of `== "out"`) → S5.
- Fallback to an earlier I2 line when the last is malformed → S9.
- First I2 line instead of the last → S12.
- `>=` → `>` on SUITE_FROM → S2.
- Cutoff removed → S10.
- 084 gate call removed → S13.
- `{n,}` → `{n}` in `_md_lines` → `longer-close`.
- `_logged` without the left `\|` → P5a2.
- `SHALLOW_LINE.fullmatch` → `.match` → shallow case 1, and `.search` → case 1.
- `{40}` → `{40,}` → case 2.
- `recorded` deleted from one shipped entry → `test_shipped_probes_well_formed`.
- Marker branch removed → X.
- Compare on failed+passed or on the full string → Y.
- `(live n/a)` branch removed → W.
- The a1 clause, the a1 unshallow sentences or the run-item sentence deleted → the matching text test.
- Template Suite line deleted → `test_suite_label_in_template_and_i2_text`.

**Checks (I2, pasted in 05):**
- The full suite `python3 -m pytest -q`. Its last line goes, unchanged, in 05's own column-0 `Suite:` line and in the I2 log field (082 < SUITE_FROM, so this is voluntary, and it shows the rule in use).
- `python3 scripts/probe_guardrails.py --ref HEAD`, whole output.
  - Refresh every `(live differs)` entry and fill the new entry's `recorded` from it.
  - Commit, re-run, and paste the second output. Expect `TOTAL: 10 probes, 10 hold`, no `(live differs)` and no `(recorded unreadable)`.
  - If an old anchor prints ANCHOR MISSING after 081/084/086, fix that anchor in this item and show it HOLDS.
- `python3 scripts/check_pipeline.py`: 082 not INCOMPLETE. No item gains a Suite entry, since none is ≥ SUITE_FROM. If 084 is built, `RULE NOT SEEN:` is still exactly 083's line.
- `python3.11 -m py_compile scripts/check_pipeline.py scripts/probe_guardrails.py` where available (RI-008).
- The new-file and changed-file counts by the i2 commands.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 1: template Suite line + i2 sentence | Files 6, 7; `test_suite_label_in_template_and_i2_text`; template-deletion mutation |
| Map step 2: SUITE_FROM, reader, 3 messages, whole-string `!=`, no I2 / malformed → no entry | Files 1: `SUITE_FROM`, `_last_log_line`, `_suite_lines`, the `incomplete()` block |
| Map step 2: 084 gate registration (row FOR 1(b)) | Files 1, the one `_rule_seen(..., "SUITE_FROM", ...)` call; S13/S13b; gate-removed mutation. Fallback if there is no helper: a named gap in the comment and 05 |
| Map step 3: fixtures S1-S12 and their mutations | Tests, Point 1 fixtures S1-S12 (S2 standalone, change 2); Mutations list |
| Map step 4: probe RI-006-082-suite, PROBES 9 → 10, target list | Files 4, 5; Checks (`10 probes, 10 hold`) |
| Map step 5: `longer-close`, XR1 line | Tests, Point 2; the `{n}` and left-pipe mutations |
| Map step 6: `RECORDED`, markers, a1 clause, format assert, X/Y, `(recorded unreadable)` | Files 4, 5, 8; X, Y, W (W added, change 3); marker order (change 4) |
| Map step 7: 2 shallow cases, a1 sentence, three-file pin | Files 2, 8; Point 4 tests; `.match`/`.search`/`{40,}` mutations |
| Map step 8: run-item subject sentence + pin; partial guard named in 05 | Files 9 (scoped to the log-line commit, change 6); `test_run_item_commit_subject_rule` |
| Map step 9: I2 runs (suite, probes twice, check_pipeline, py_compile) | Checks |
| Map step 10: I3 re-runs the mutations, Suite = field, RULE_PATHS diffs additions only | Mutations list; I3 duty (no plan code) |
| Row F9 / Numbers F9: SUITE_FROM = `--next-id` at I1 time, ≥ 87 | Changed: I1 has no shell. Value 087 from the orchestrator; I2 sets `max(87, --next-id at build time)` and pastes both (change 5) |
| Row F34: I1 pastes `git log -1 --format=%s e813e1f` | Changed: I1 has no shell, so I2 pastes it in 05 (change 7) |
| Row M1a: S3/S4 added to kill `in` | S3, S4 |
| Row M1b: S6 with two identical lines | S6 |
| Row M1c: m2 not added; PROBES 9 → 10 | Files 4 (one new entry only) |
| Row FOR 1(e): replacement makes the mismatch unreachable, target S2 | Files 4: `elif False:`, target S2 |
| Row FOR 2(b): marker on failed count only, live results only | `_recorded_marker` (change 4) |
| Row 086 (02 past logs): Suite helps 086 via the I2 field | Fit check, 086 bullet; no code |
| Row 081 (02 past logs): copy the sentence as it is after 081 | Files 8 (copied from run-item.md after 081/084/086) |
| Row F19 / 02 FOR 3(e): 077 P1 I1-template suggestion | DROPPED: outside request point 2 (R3 decision) |
| 02 AGAINST 3(a): probe in this item, not a follow-up | Kept in this item (03 For the person). Listed for the person in 05 |
| 03 For the person: RULE_PATHS edits need the person's OK | 05 lists Files 1, 6, 7, 8, 9 for PR review |
| Missing inputs table (every row) | Guardrail tests, Missing inputs |

## Guardrail tests
- Feasibility:
  - Suite rule, real-data fit 4 of 4 (076-079, R3 2026-11-20) → S1 pins the whole-line-equal pass case. In-scope count 0 of 77 today (cutoff) → `test_repo_pipeline_has_no_skipped_items` stays green on HEAD, and the Checks line shows no Suite entry.
  - Cutoff boundary at SF and SF − 1 → S2, S10.
  - `RECORDED` 9 of 9 shipped values → the format assert in `test_shipped_probes_well_formed`.
  - Shallow lines 0 of 2 `fullmatch`, 2 of 2 `.match` → the two shallow cases.
- Missing inputs:
  - 05 Suite line absent → S0. Only inside a fence → S5. More than one → S6.
  - I2 line absent → S8. Last I2 line malformed → S9.
  - 05 committed before SUITE_FROM existed (084 gate) → S13.
  - `--next-id` refuses → I2 stops (step 0, process; no test).
  - 084 helper absent → named gap in the comment and 05.
  - `recorded` absent (fixture) → `test_mixed_run_reports_every_probe` "b": `recorded: none`, no marker. Absent on a shipped entry → format assert.
  - `recorded` unparsable → `test_holds_exits_0`. Live counts absent → W.
  - `.git/shallow` malformed lines → the 2 new cases plus the existing `zz` case.
  - e813e1f subject → I2 step 0 paste (the design does not depend on it).

## Expected result
- 9 files changed (counted by the i2 commands), plus work/082/05.
- The full suite passes, with the count as printed by pytest: today's count plus about 22 new tests or cases. No existing assertion is edited; only the fixture texts listed in change 1 change.
- `probe_guardrails.py --ref HEAD` prints `RI-006-082-suite (RI-006): ... HOLDS` and `TOTAL: 10 probes, 10 hold, 0 not held, 0 anchor missing, 0 error`, with no marker on the second run.
- `check_pipeline.py` on this branch: no new INCOMPLETE entry, 082 not INCOMPLETE, and `RULE NOT SEEN:` unchanged from 084's 083 line.
- Every mutation listed fails at least one named test.
- Known limits, stated in 05:
  - Points 4b and 5 are text pins only.
  - The unshallow sentence's list (UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD) does not name 084's `RULE NOT SEEN` "not checked" form. Changing it would have to change all three copies, which is a separate item if wanted.
  - No real item reaches the Suite rule until SUITE_FROM, so on this branch only the fixtures prove it.
- RI lines for 05:
  - "RI-006: guardrail built (082); the Suite compare is probed by RI-006-082-suite."
  - "RI-010: 082 turns two text duties into checks (Suite, recorded); 4b and 5 are text pins."
  - "RI-014: unshallow sentence pinned in three files (082)."

Log fields: FIT WITH CHANGES | 9 files planned
