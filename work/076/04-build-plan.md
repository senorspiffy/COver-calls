# 04 Build plan - 076
Fit verdict: FIT WITH CHANGES

Round 2 (after I3 FAIL round 1, work/076/06-verification.md). Two plan defects fixed, the rest is unchanged:
- P1: m1's expected result was wrong. `_END` does not enforce the order of parts; the fixed sequence of optional groups in `_STATS` does (I3's m8). `_END`'s job is to require the `, ` separator between parts, and no case covered it. Two refuse cases are added to the Self-check list and T2 (R15, R16 below), m1 now names them, and m8 is added for order.
- P2: `log_hint` had an unguarded `int(item)`, so T6 would fail as planned. The `re.fullmatch(r"\d{3}", item)` guard that I2 built (I2 Deviation 1, accepted by I3) is now in the plan (change 5), pinned by T6 and mutation m9.

Fit check: this is process tooling only. It does not touch the bot, quotes or the ~$3k account rules (001 is unchanged). It fits the existing checker: `LOG_FORMAT` stays a dict of plain regex strings keyed by agent, so `incomplete()` (L417, `LOG_FORMAT["I3"]`) and 077's `i3_verdict` work keep reading it unchanged. Build on 075's code (brief order 075 -> 076 -> 077). 075 changes tests/test_agent_tools.py only, so there is no file overlap. 077 and 079 change check_pipeline.py after this item.

Changes against 03 (why "WITH CHANGES"):
1. **Fixture IDs below the cutoff (03 step 4 gap).** 03 sets `FIELDS["I2"]` to the new form for every fixture. But `_item()` (tests/test_pipeline_check.py L44) writes FIELDS for every ID, and fixtures use IDs below 76: 048 (L505-516), 050 (L274), 060 and 065 (L1559-1565, which asserts `INCOMPLETE: none` and exit 0), 066 (L1619), 067 (L1676), and 069/070 in tests/test_real_data_field.py L139 (via the imported `_item`). With the new form only, those items would get `INCOMPLETE` for I2, and at least `test_old_06_without_round_headers_unchanged` would fail. Fix: add a helper `_field(agent, item)` that returns the old-form I2 field for IDs below 76. Use it at L44 and L516. L446, L514 and L1536-1537 are R1-R3/I1 fields or IDs of 150 and up, so they keep `FIELDS[a]`.
2. **The i2 text must not claim checks no agent runs (RI-010).** 03 step 3's limit sentence says "I3 and A1 compare it with 05". Neither i3-verifier.md nor a1-auditor.md has that duty (Grep `log line` in i3-verifier.md: only its own L18). The sentence is reworded so it states only the limit, and the I3/A1 cross-check goes to a follow-up (below).
3. **Old-form hint kept as data, not a second dict shape.** `LOG_HINT` keeps one entry per agent, so `test_log_hints_match_formats` L548 is unchanged. The old I2 hint goes in a separate `LOG_HINT_BEFORE = {"I2": (...)}`, read through `log_hint(agent, item)`.
4. **Order inside `write_log`.** The `\d{3}` item check must run before `log_fields_ok` calls `int(item)`. The existing `or` chain short-circuits, so keep the order as `agent not in LOG_FORMAT or not re.fullmatch(r"\d{3}", item) or not log_fields_ok(agent, item, fields)`. A test pins it (T6).
5. **`log_hint` guards its own `int(item)` (round 2, P2).** `write_log` calls `log_hint(agent, item)` inside the refusal text, which is built for exactly the IDs that change 4 refuses, including a non-numeric one. So `log_hint` checks `re.fullmatch(r"\d{3}", item)` before `int(item)`; an ID that is not 3 digits gets the current hint (`LOG_HINT[agent][0]`), never a traceback. This is the code I2 built in 266a6a2 (scripts/check_pipeline.py L410-415), unchanged. Pinned by T6 and m9.

## Extra research (with sources)
- **Environment can change the line (an edge R3 missed).** `PYTEST_ADDOPTS` "will be prepended to the command line given by the user". `PY_COLORS=1` or `FORCE_COLOR` turns colour on (pytest 8.2 reference.rst, https://gitverse.ru/niceSOFT/python3-pytest/tag/8.2.0/doc/en/reference/reference.rst; the same variables are listed in https://huohuoren4.github.io/python/pytest/reference_guides/api_reference/env_variables). Three cases:
  - `PYTEST_ADDOPTS=-v` cancels `-q`, so the line is `=`-padded.
  - `PYTEST_ADDOPTS=-k x` adds `N deselected`.
  - Colour adds ANSI escapes.
  The 03 regex refuses all three loudly (exit 2), because `=`, `deselected` and `\x1b` match no part. No code change is needed. The i2 text says to re-run from a clean environment (`env -u PYTEST_ADDOPTS PY_COLORS=0 python3 -m pytest -q`) if `--log` refuses a line that was copied as printed. The repo itself sets no addopts (03 #54: 0 hits).
- **Collection errors.** A run that fails at collection prints e.g. `1 error in 0.50s`, which A9 accepts. That is correct: the failure stays visible in the field. It is not a loophole.
- **Notes stay allowed.** `(?: \(.*\))?` keeps a free-text note such as 062's `(round 2: test case added)`. That note could also hold `(1 failed)`. This is a known limit: the stats part before the note is still checked in full, so no failure can be dropped from it. Written in the docstring.
- **Feasibility re-checked (Grep `\| I2 \| 0(4[5-9]|[5-7]\d) \|` over logs/implementation).** 35 committed I2 lines for items 045-074, all in the old form, none with pass > total. The equal cases are 058 218/218, 065 49/49 and 072 411/411, matching 03 step 1. (I3 round 1 re-ran it with 075 `488/489` and 076's own line included: 37 lines, 0 refused.)
- **Which regex part holds which rule (round 2, from I3's mutations in 06).** Order of parts: the fixed sequence of optional groups in `_STATS` (m8 fails R3 and A3/A13). Separator between parts: `_END` (m1, killed only by a case where two parts touch with no `, `). At most once: each part is one optional group. So each of these three rules needs its own refuse case, and R15/R16 are the separator cases.

## Files to create/change
3 files.

1. **scripts/check_pipeline.py**
   - Next to `LOG_CHECK_FROM` (L190), add:
     - `TESTS_FORMAT_FROM = 76`, with 03's comment.
     - `_N`, `_END`, `_STATS_PARTS`, `_STATS`, `_TAIL`, exactly as in 03's code block. They are defined above `LOG_FORMAT` so the dict entry can use them inline.
     - `I2_BEFORE = r"\d+ files? changed \| tests (\d+)/(\d+)\b.*"`.
   - In the dict (L234): `"I2": rf"\d+ files? changed \| tests {_STATS}{_TAIL}"`. It stays a plain string in the dict, with no assignment after the dict.
   - `LOG_HINT["I2"] = ("<n> files changed | tests <last line of python3 -m pytest -q, as printed>", "2 files changed | tests 9 passed, 1 skipped in 3.21s")`.
   - New `LOG_HINT_BEFORE = {"I2": ("<n> files changed | tests <pass>/<total> (pass <= total)", "2 files changed | tests 9/9")}`.
   - New `def log_fields_ok(agent, item, fields) -> bool`. For `agent == "I2" and int(item) < TESTS_FORMAT_FROM`: `m = re.fullmatch(I2_BEFORE, fields.strip())`, then return `bool(m) and int(m[1]) <= int(m[2])`. Otherwise return `bool(re.fullmatch(LOG_FORMAT[agent], fields.strip()))`. Callers pass only 3-digit IDs (change 4; `incomplete()` reads IDs from log lines already matched by `\d{3}`).
   - New `def log_hint(agent, item) -> str` (change 5). Returns `LOG_HINT_BEFORE[agent][0]` when `agent in LOG_HINT_BEFORE and re.fullmatch(r"\d{3}", item) and int(item) < TESTS_FORMAT_FROM`, else `LOG_HINT[agent][0]`. The `\d{3}` test comes before `int(item)` in the `and` chain. Docstring says an ID that is not 3 digits gets the current form, never a traceback.
   - `incomplete()` L396: `not log_fields_ok(m[3], m[4], m[5])` replaces the bare `re.fullmatch`. L398: `log_hint(a, item_dir.name)`.
   - `write_log()` L426-429: `log_fields_ok` (order as in change 4), and the refusal text uses `log_hint(agent, item)` when the agent is in LOG_HINT. The unknown-agent text is unchanged.
   - Module docstring L66-69, add: from TESTS_FORMAT_FROM the I2 tests field is the last line of `python3 -m pytest -q` run from the repo root, as printed (parts in pytest's KNOWN_TYPES order, each at most once, separated by `, `, `deselected` refused, unknown parts refused). Before it, `<pass>/<total>` with total = passed + failed + skipped + errors + xfailed + xpassed (deselected and warnings are not tests) and pass <= total. Also state the note limit above.
2. **.claude/agents/i2-builder.md** L25 (a RULES change, needs the person's OK in PR review). New text:
   > Append to `logs/implementation/<YYYY-MM-DD>.md`: `<UTC HH:MM> | I2 | <ID> | <n> files changed | tests <summary line>`. Write it with `python3 scripts/check_pipeline.py --log I2 <ID> "<n> files changed | tests <summary line>"` right after writing your step file, where `<summary line>` is the last line of `python3 -m pytest -q` run from the repo root, copied as printed (item 076), e.g. `8 files changed | tests 411 passed, 1 skipped in 64.87s`. It is the same line you paste in 05 Test output: never retyped, summed or shortened. Full suite only (no `-k`, `-m` or file paths; `deselected` is refused). If `--log` refuses a line copied as printed, re-run as `env -u PYTEST_ADDOPTS PY_COLORS=0 python3 -m pytest -q`. Limit: the field cannot prove the run was the full suite; 05's pasted Test output is the record. `--log` adds the UTC time and refuses a line not in this format. Never type a log line by hand (item 045).

   The sentence pinned by `test_agent_texts_name_item_071` (L20) is untouched. (Built word for word in 266a6a2; no change in round 2.)
3. **tests/test_pipeline_check.py**
   - `FIELDS["I2"] = "1 files changed | tests 1 passed"`. Add `I2_BEFORE_FIELD = "1 files changed | tests 1/1"` and `def _field(agent, item): return I2_BEFORE_FIELD if agent == "I2" and int(item) < 76 else FIELDS[agent]`. L44 uses `_field(agent, item)`. L516 uses `_field(a, item)`.
   - L380 and L390: `2 files changed | tests 9 passed, 1 skipped in 3.21s`.
   - L404, L412, L442, L537: `tests 1 passed`. These are IDs 999 and 150, so the new form applies.
   - L428, L443, L533, L557 stay malformed (`see 05`) on purpose.
   - L562 and L566: the new hint text (item 150).
   - New tests T1-T6 (next section).
   - **Round 2 code change (the only one):** add the two refuse cases R15 `411 passed1 skipped` and R16 `1 failed1 passed in 1.00s` to the T2 parameter list (`I2_REFUSE`). Nothing else in the code changes in round 2.

## Tests and checks
All tests are in tests/test_pipeline_check.py and use tmp_path without git, so the RI-014 path is not touched.
- **Self-check refuse cases added in round 2** (03's list had R1-R14; these join it):
  - R15 `411 passed1 skipped`: two parts with no `, ` between them. Refused (exit 2). Only `_END` refuses it.
  - R16 `1 failed1 passed in 1.00s`: same, with a timing part after. Refused (exit 2). Only `_END` refuses it.
- **T1** `test_i2_summary_line_accepted` (parametrized over the 14 Self-check accept cases A1-A14 plus the FIELDS fixture): `--log I2 150 "1 files changed | tests <case>"` gives exit 0 and the line is written.
- **T2** `test_i2_summary_line_refused` (the refuse cases R1-R16, R6/R7 as two cases, plus `\x1b[32m411 passed\x1b[0m` and `===== 411 passed in 1.00s =====` from Extra research: 19 cases): exit 2 and no logs/ dir. R15 and R16 are new in round 2.
- **T3** `test_i2_tests_field_cutoff`:
  - `--log`: `075 "... tests 9/9"` gives 0, `075 "... tests 10/9"` gives 2, `076 "... tests 9/9"` gives 2, `076 "... tests 9 passed"` gives 0. The 075 refusal text names `<pass>/<total> (pass <= total)`. The 076 refusal text names `as printed`.
  - INCOMPLETE: `_item` makes items 074, 075, 076 and 077 (the fixture lines are good, through `_field`). Then append `075 ... tests 10/9` and `076 ... tests 9/9`. The INCOMPLETE line contains `075 (log line for I2` and `076 (log line for I2`, and contains no `074 (` and no `077 (`. Exit 1.
- **T4** `test_i2_text_defines_tests_field`: i2-builder.md contains `python3 -m pytest -q`, `as printed` and `(item 076)`, and does not contain `<pass>/<total>`.
- **T5** `test_old_i2_hint_fits_old_format`: `LOG_HINT_BEFORE["I2"][1]` fullmatches `I2_BEFORE`, and `log_fields_ok("I2", "075", example)` is True. `test_log_hints_match_formats` is unchanged and covers the new example.
- **T6** `test_log_refuses_non_numeric_id_without_crash`: `--log I2 abc "1 files changed | tests 1 passed"` gives exit 2 with the `--log refused` text and no traceback in stderr. It pins both change 4 (order in `write_log`) and change 5 (guard in `log_hint`).
- **Mutations (I2 runs them in a scratch worktree under the scratchpad, RI-009).** Each must fail at least the named test:
  - m1: `_END` changed to `(?:, )?`. Fails T2 R15 and R16 (separator missing). (Round 1 wrongly named R3/R4: order is not held by `_END`, see m8.)
  - m2: the pass <= total check removed. Fails T3 (`075 10/9`).
  - m3: `TESTS_FORMAT_FROM = 77`. Fails T3 (`076 9/9` accepted).
  - m4: `TESTS_FORMAT_FROM = 75`. Fails T3 (`075 9/9` refused).
  - m5: `deselected` added to `_STATS_PARTS`. Fails T2 (R9).
  - m6: `incomplete()` back to the bare `re.fullmatch(LOG_FORMAT[...])`. Fails T3 (074 flagged) and `test_old_06_without_round_headers_unchanged`.
  - m7: the `\d{3}` check moved after `log_fields_ok` in `write_log`. Fails T6.
  - m8 (round 2, order): `failed` and `passed` swapped in `_STATS_PARTS`. Fails T2 R3 and T1 A3/A13 (I3 round 1 result: 3 failed).
  - m9 (round 2, change 5): the `re.fullmatch(r"\d{3}", item)` guard removed from `log_hint`. Fails T6 (I3 round 1 result: 1 failed, 185 passed).
- **Full suite:** `python3 -m pytest -q` from the repo root passes. Paste its last line in 05 and use it, as printed, in I2's own 076 log line (round 2: a new run, so a new line; the round 1 line is not reused). Paste `python3 -m pytest --version` in 05.
- **Repo check:** `python3 scripts/check_pipeline.py` gives exit 0 and `INCOMPLETE: none`. `test_repo_pipeline_has_no_skipped_items` passes. The 35 committed old-form lines (045-074) stay valid.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision: option B from 076 on, A's pass <= total before | Files 1 (`TESTS_FORMAT_FROM`, `log_fields_ok`); T1-T3 |
| Options C and D left out | DROPPED: as 03 decided (C needs a fixed 05 label, RI-012, and overlaps 077; D takes about 60 s per call and is recursive). Follow-up for A1 below |
| Constraint: LOG_FORMAT stays plain strings keyed by agent | Files 1 (inline dict entry); `test_log_hints_match_formats` |
| Step 1 regex: parts in order | Files 1 (`_STATS` group sequence); T2 R3/R4, T1 A3/A13; m8 |
| Step 1 regex: parts separated by `, ` | Files 1 (`_END`); T2 R15/R16 (round 2); m1 |
| Step 1 regex: each part at most once, no deselected, timing with optional H:MM:SS, optional note | Files 1; T1/T2 (A1-A14, R1-R14); m5 |
| Step 1 `log_fields_ok` in write_log and incomplete | Files 1; T3; m6, m7 (+ change 4 order, T6) |
| Step 1 docstring (definition of total, deselected/warnings not tests) | Files 1 docstring; the note limit and the `, ` separator added |
| Step 2 hints per item (`log_hint`) | Files 1 (`LOG_HINT_BEFORE`, change 3; `\d{3}` guard, change 5); T3 refusal texts; T5; T6; m9; L562/L566 |
| Step 3 i2-builder.md text | Files 2; T4. Limit sentence reworded (change 2) |
| Step 4 test edits and T1-T5 | Files 3; FIELDS by ID via `_field` (change 1); T6 added; R15/R16 added to T2 (round 2) |
| Step 5 repo check, I2's own 076 line in the new form | Tests and checks: Repo check, Full suite |
| Missing input: summary line absent, `-qq`, `no tests ran`, empty | T2 (R1, R14) refused, exit 2 |
| Missing input: `<pass>/<total>` non-numeric, missing or pass > total (045-075) | T3 (`075 10/9`, INCOMPLETE); `test_malformed_log_line_is_incomplete` (`see 05`) |
| Missing input: unknown or plugin part | T2 (R9 `deselected`, ANSI, padded) refused; the fix is a new item |
| Missing input: item ID not 3 digits | T6 (exit 2, no traceback); changes 4 and 5; m7, m9 |
| Missing input: pytest version | Full suite: `--version` pasted in 05 (no code) |
| Missing input: machine-dependent skip count | No default; the line is as printed (i2 text); not testable in code |
| Self-check, cutoff 76/75/45/44 | T3 (75/76); `test_malformed_log_line_is_incomplete` (044 not checked) |
| I3 round 1 send-back 1 (P1: m1, separator cases, order claim) | Round 2 note; Self-check R15/R16; T2; m1 corrected; m8 added |
| I3 round 1 send-back 2 (P2: `log_hint` guard) | Change 5; Files 1 `log_hint`; T6; m9 |
| Rule the person follows (001) | None changed (process only). The i2-builder.md RULES text is in this plan and goes to PR review |

## Guardrail tests
- Feasibility:
  - Old form plus pass <= total: 35 of 35 committed lines, items 045-074 (Grep 2026-11-19), stay valid; I3 round 1 re-ran with 075/076 included: 37 of 37. Pinned by `test_repo_pipeline_has_no_skipped_items` (INCOMPLETE none) and T3 (075 accepted).
  - New form: 9 of 9 real full-suite lines fit (03 step 1). Pinned by T1 A1-A3, which are the real 072 (A1), 074 (A2) and 070 (A3) lines. The real lines always have `, ` between parts, so R15/R16 refuse nothing real.
- Missing inputs:
  - Summary line absent or empty, or `no tests ran`: T2 R14, R1.
  - pass > total (old form): T3 `075 10/9`.
  - Unknown part: T2 R9 plus the ANSI and padded cases.
  - Parts with no separator: T2 R15, R16.
  - Non-numeric ID: T6 (both `write_log` order and `log_hint` guard).

## Expected result
- `--log I2` refuses an ill-formed field (exit 2, nothing written). From item 076 the field is pytest's summary line as printed; for 045-075 it is `<pass>/<total>` with pass <= total.
- INCOMPLETE applies the same rule per item.
- The i2 text defines the field.
- T1-T6 and the updated tests pass (T2 now 19 cases), and m1-m9 each fail at least one named test; m1 fails R15 and R16 (I3's scratch check: 2 failed).
- A non-numeric ID is refused with exit 2 and the refusal text, no traceback.
- The full suite is green. `check_pipeline.py` gives exit 0 and INCOMPLETE none.
- I2's 076 line is the first new-form line, rewritten with the round 2 full-suite line as printed. 075's I2 line uses the old form.

Follow-up for A1 (not in this item): option C, or an I3 duty that compares I2's log field with 05 Test output, using a fixed `Suite:` label in templates/build-report.md.

Notes for later items:
- 077 and 079 build on this code. Any new reader of I2 log lines must call `log_fields_ok`, not `re.fullmatch(LOG_FORMAT["I2"], ...)`. Any new caller of `log_hint` or `log_fields_ok` with an ID from user input must check `\d{3}` first, or rely on `log_hint`'s own guard.
- 077's and 079's own I2 lines use the new form.

Recurring issues checked:
- RI-014 is the only OPEN entry. RI-001 is ESCALATED: checked, no rule window here; feasibility counts re-grepped (35 lines) and re-run by I3 (37 lines, 0 refused). The plan does not touch `_walk`, and the new tests use tmp dirs without git (RI-014).
- Also checked: RI-006 (root cause; the field is copied, not counted), RI-012 (fullmatch only; R15/R16 are whole-field cases), RI-002 (absent line refused, never defaulted; non-numeric ID refused, not turned into a hint by a crash), RI-010 (the text is pinned by T4; no claimed I3/A1 check without a duty), RI-009 (mutations in a scratch worktree).

Log fields: FIT WITH CHANGES | 3 files planned
