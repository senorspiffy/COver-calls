# 04 Build plan - 108
Fit verdict: FIT WITH CHANGES

Fit check: a test-only change to one file (tests/test_pipeline_check.py). It does not touch the bot, the strategy rules, any account-size limit (~$3k) or config, so nothing in 001 that the person follows changes, and no rule text update or request is needed. No conflict with existing code: `scripts/check_pipeline.py` stays the same. Items 105, 109 and 110 run today and may edit the same test file or the checker. Builds go one at a time, so every place below is named by function, test or comment text, never by line number. The changes from 03 are small. (a) One helper, `_se_fields()`, computes the timed and untimed values for both the setup and the precondition, so `f == untimed` is checked against one derivation and not two copies. (b) `re.sub` takes `count=` as a keyword (see Extra research 1). (c) The precondition's case test is `case.startswith("timed05")`.

Recurring issues checked (item 013): RI-001 (ESCALATED), RI-014 (OPEN). I also checked RI-002, RI-004, RI-005, RI-006, RI-010 and RI-012 for the same failure shapes. Details are under Guardrail tests.

## Extra research (with sources)
1. Python 3.13 deprecates passing `count` and `flags` to `re.sub` by position ("Deprecated since version 3.13: Passing count and flags as positional arguments is deprecated. In future Python versions they will be keyword-only parameters", https://docs.python.org/3/library/re.html, opened 2026-11-25). 03 already writes `count=1`. The plan makes the keyword form a requirement, so 3.13 gives no DeprecationWarning, and it still works on 3.10 (pyproject.toml `requires-python = ">=3.10"`, RI-008).
2. `_log_text(logs)` returns `(text, whys)`, the joined text of every research and implementation log, and `whys` lists unreadable files (scripts/check_pipeline.py `def _log_text`, re-read today). `LOG_LINE` is anchored `^...$` with no `re.M`, so it has to be applied per line through `splitlines()`, as 03 step 2 does. Group 3 is the agent, group 4 the ID and group 5 the fields.
3. `_item` reads `FIELDS` through `_field()` when it is called, for both the I2 log line and the 05 `Suite:` line (tests `def _field`, `def _item`, item 082 comment). So `monkeypatch.setitem(FIELDS, "I2", ...)` before `setup(...)` changes both, and the 082 Suite check stays equal. pytest undoes `setitem` when the test ends (https://docs.pytest.org/en/stable/how-to/monkeypatch.html, cited in 03), so the alternative field cannot leak into later tests.
4. Edge case R3 did not name: `_se_edit` uses `str.replace`, which replaces every match. The timed field text appears only on the I2 log line. The I1 field is `FIT | 1 files planned` and the I3 field is `PASS | sent to audit: yes`, so neither contains it, and `old in text` plus the read-back `len(own_i2) == 1` keep the edit to one line. The same holds for the alternative field `2 files changed | tests 3 passed in 0.02s`.

## Files to create/change
1. tests/test_pipeline_check.py (only file changed)
   - Under the `# Item 101 (RI-014): each shallow ...` comment: delete `SE_FIELD = ...` and its trailing comment. Add:
     ```
     def _se_fields():
         """Item 108: (timed, untimed) from the fixture's own I2 field; untimed = timed minus its ` in <s>s` time."""
         timed = _field("I2", RH_ID)
         assert " | tests " in timed, timed
         untimed = re.sub(r" in \d+\.\d+(?:s| seconds)", "", timed, count=1)
         assert untimed != timed, timed
         return timed, untimed
     ```
   - `_se_timed05`: `timed, untimed = _se_fields()`. Then `_se_edit(<logs/implementation/RH_DAY.md>, timed, untimed)` and `_se_edit(d / "05-build-report.md", "Suite: " + timed.split(" | tests ", 1)[1], "Suite: " + untimed.split(" | tests ", 1)[1])`. Return `(d, None, I2_ENTRY)` as before. `_se_edit` itself stays as it is.
   - `SE_CASES`: add `("timed05alt", "05", _se_timed05)`. `SE_PARAMS` then gives `timed05alt-shallow` and `timed05alt-nogit`.
   - Module constant next to `SE_CASES`: `SE_ALT_I2 = "2 files changed | tests 3 passed in 0.02s"  # item 108: a second I2 field, patched per test`.
   - `test_shallow_elif_branch_goes_to_unchecked`: add the `monkeypatch` argument. Before `setup(...)`: `if case == "timed05alt": monkeypatch.setitem(FIELDS, "I2", SE_ALT_I2)`. Replace the `if case == "timed05":` precondition with `if case.startswith("timed05"):` followed by the read-back:
     ```
     _, untimed = _se_fields()
     text, whys = cp._log_text(tmp_path / "logs")
     assert whys == [], whys
     own_i2 = [m for m in (cp.LOG_LINE.match(l) for l in text.splitlines()) if m and m[3] == "I2" and m[4] == RH_ID]
     assert len(own_i2) == 1, own_i2
     f = own_i2[0][5]
     assert f == untimed, (f, untimed)
     assert cp.log_fields_ok("I2", RH_ID, f, timed=False) and not cp.log_fields_ok("I2", RH_ID, f), f
     ```
     Add one docstring sentence: "Item 108: the timed05 cases read the I2 field back from the fixture log and derive their edits from FIELDS; timed05alt patches FIELDS['I2']."
   - Whitespace: exactly 2 blank lines before the `# Item 101 (RI-014)` comment (3 today) and before `def test_round_build_missing_inputs` (1 today). Find both by text.
2. No other file. scripts/, templates/, .claude/, config/ and ccbot/ are not changed.

## Tests and checks
- I2 step 1 (after the `_se_fields` and `_se_timed05` edits, before the new case): `python3 -m pytest -q tests/test_pipeline_check.py -k shallow_elif_branch` should give `14 passed`.
- I2 after all edits: the same command should give `16 passed`, and the ids should include `timed05alt-shallow` and `timed05alt-nogit`.
- One-off probe (I2, scratch copy only, record it in 05): make `_se_timed05` skip the log edit, so ` in 0.01s` stays in the log. Expected: `timed05-*` fail at `assert f == untimed` or the `log_fields_ok` precondition, by name. Restore the file and check it with `cmp`.
- Mutants (I2 in 05, re-run by I3 in 06). Run them one at a time on a scratch copy of scripts/check_pipeline.py, restore after each and check with `cmp`. Find the line by the `# item 095: anchor not read in a shallow clone` comment directly under the `# item 090: TIMED gate` line.
  - M-timed: `elif unsure("05"):` → `elif False:`
  - K-timed: `unsure("05")` → `unsure("06")`
  - Expected for each: `2 failed, 14 passed`, and the failures are exactly `timed05-shallow` and `timed05alt-shallow`. Any other result is pasted and explained.
- `grep -n SE_FIELD tests/` should give 0 hits.
- Full suite: `python3 -m pytest -q` should give base + 2 passed, with the same skips. I2 pastes the before and after lines. The base can move because 105, 109 and 110 are built today, so compare against the run just before 108's edit.
- `git diff --stat <base> HEAD -- scripts/ templates/ .claude/ config/ ccbot/` should be empty. `python3 scripts/check_pipeline.py` should be unchanged apart from 108's own item lines.
- Python 3.10 floor: `python3.11 -m py_compile tests/test_pipeline_check.py` where available (RI-008, i3 step 2). No new syntax is used.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision (1): read back and derive, delete `SE_FIELD` | Files 1: `_se_fields`, `_se_timed05`, precondition read-back, `SE_FIELD` deleted; check grep 0 hits |
| Decision (2): `cp.LOG_LINE` over `cp._log_text(...)[0]` | Files 1: precondition uses `text, whys = cp._log_text(...)` and `LOG_LINE.match` per line |
| Decision (3): Suite edit with the same split | Files 1: `_se_timed05` second `_se_edit` |
| Decision (4): blank-line nit | Files 1: whitespace bullet |
| Step 1: derive both edits from one value; `" \| tests " in timed`; `count=1` strip; `untimed != timed`; `_se_edit` keeps `old in text` | Files 1: `_se_fields` and `_se_timed05`; check `14 passed` before the new case |
| Step 2: precondition read-back (`whys == []`, `len(own_i2) == 1`, `f == untimed`, LOG_FORMAT yes / I2_TIMED no) | Files 1: precondition block, `f == untimed` against the shared `_se_fields()`; one-off probe |
| Step 3: `timed05alt` case, `monkeypatch.setitem` before setup, precondition for every `timed05*` case | Files 1: `SE_CASES`, `SE_ALT_I2`, the `monkeypatch` argument, `case.startswith("timed05")`; check `16 passed` |
| Step 4: mutants M-timed and K-timed, `2 failed, 14 passed` each | Tests and checks: Mutants |
| Step 5: 2 blank lines in both places | Files 1: whitespace bullet |
| Step 6: no change outside the test file | Files 2; check `git diff --stat` is empty |
| Missing inputs table (5 rows plus a screen n/a row) | Guardrail tests: Missing inputs |
| Person-followed rule (001: slack, tolerance, cap) | DROPPED: no rule the person follows is changed (test-only, the checker is unchanged) |

## Guardrail tests
- Feasibility: the fixture precondition, "exactly 1 I2 line for 150, 6 lines in all", is pinned by `assert len(own_i2) == 1` in `timed05-*` and `timed05alt-*`. The count is computed: 7 fixture files, 6 with an agent, 1 of them I2 (03 Self-check 7). The run is dated by I2 on 2026-11-25: `16 passed`. Each strip removes exactly 1 match, pinned by `assert untimed != timed`.
- Feasibility: the alternative field has a second dated value. `timed05alt-*` pins that the untimed form of `2 files changed | tests 3 passed in 0.02s` matches LOG_FORMAT and fails I2_TIMED (03 Self-check 4).
- Missing inputs, each with its absent-case test or assertion:
  - Fixture log unreadable: `assert whys == []`.
  - Fixture log absent, or 0 or more than 1 I2 lines: `assert len(own_i2) == 1`. Exercised by the one-off probe and never a vacuous `all()` (03 R1 F17).
  - No time in `FIELDS["I2"]`: `assert untimed != timed` in `_se_fields` (a `re.sub` no-op, 03 R1 F18).
  - No ` | tests ` separator: `assert " | tests " in timed` in `_se_fields`.
  - Edit target missing: `_se_edit`'s `assert old in text`.
  - Screen tickers: n/a, no ticker is screened.
- Recurring issues:
  - RI-001 (ESCALATED): there is no filter or window rule here, and every count above is computed and then measured by I2's run. No "always" claim is made.
  - RI-014 (OPEN): the parent issue. The shallow TIMED branch stays pinned by 2 mutants with 2 named failing ids each. Status unchanged.
  - RI-002: the empty, unchanged or absent cases all fail by name (list above).
  - RI-004/005: the field values are re-derived against the regexes in 03 Self-check 1-4. I did not compute new numbers.
  - RI-006: totals come from the pytest line as printed. Nothing is hand-counted.
  - RI-010: the log line comes from the orchestrator via `--log`. I wrote none.
  - RI-012: there is no substring classification. The read-back uses the checker's anchored `LOG_LINE` and `fullmatch`.

## Expected result
- `-k shallow_elif_branch`: `16 passed` (14 before the new case). The full suite is base + 2 passed.
- Each of M-timed and K-timed gives `2 failed, 14 passed`, and the failures are exactly `timed05-shallow` and `timed05alt-shallow`.
- `SE_FIELD` is gone. Changing `FIELDS["I2"]` to any timed field with ` | tests ` now flows through setup and precondition with no other edit, and the patched case shows it.
- The diff touches only tests/test_pipeline_check.py. The checker's output is unchanged.

Log fields: FIT WITH CHANGES | 1 files planned
