# 06 Verification - 108
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-108-r1-1ie7lgty

Everything was verified in `git worktree add --detach <scratch>/wt 4619802`. All runs used PYTHONDONTWRITEBYTECODE=1, `-p no:cacheprovider` and `__pycache__` cleared before each mutant. No git stash was used (`git stash list | wc -l` → `0`). No test ran in the main checkout.

## I1 audit (plan vs research)
- 04 follows 03's map steps 1-6 and decisions (1)-(4). Every step appears in the Rule trace, and only the person-rule row is DROPPED, for a stated reason (test-only, and the checker is unchanged).
- The three plan changes are all sourced or neutral. (a) A shared `_se_fields()` helper means `f == untimed` is checked against one derivation; 03 step 2 allows "recomputing it the same way". (b) `count=` as a keyword is sourced (docs.python.org re.html, 3.13 deprecation). (c) `case.startswith("timed05")` puts 03 step 3's "precondition for every timed05* case" into code. Extra research 4 (`str.replace` replaces every match, and neither the I1 nor the I3 field holds the I2 text) is correct: FIELDS line 19 has I1 `FIT | 1 files planned` and I3 `PASS | sent to audit: yes`.
- No unsourced additions. Fit check: no rule the person follows changes (test file only), so no 001 text change or request is needed.

## I2 audit (build vs plan)
`git diff --stat f4f55a7 4619802 -- scripts templates .claude config ccbot tests` → `tests/test_pipeline_check.py | 38 +++++++++++++++++++++++++++++---------`, 1 file. I checked the build against the plan line by line:
- `SE_FIELD` and its comment are deleted, and `grep -rn SE_FIELD tests/ | wc -l` → `0`. `_se_fields()` matches the plan text exactly: the `" | tests "` assert, `re.sub(..., count=1)` and `untimed != timed`. `re` is imported (line 3).
- `_se_timed05`: both `_se_edit` calls are derived (log `timed → untimed`, and Suite through the same `split(" | tests ", 1)[1]`). It returns `(d, None, I2_ENTRY)`, and `_se_edit` is unchanged.
- `SE_CASES` has `("timed05alt", "05", _se_timed05)`. `SE_ALT_I2` comes right after `SE_CASES`, with the planned value.
- The test takes `monkeypatch`, and `setitem(FIELDS, "I2", SE_ALT_I2)` runs before `setup(...)`. The precondition is `case.startswith("timed05")` with the read-back block word for word as planned. The docstring sentence was added.
- Whitespace: 2 blank lines before `# Item 101 (RI-014)` (one removed) and before `def test_round_build_missing_inputs` (one added).
- The deviation in 05 (the probe also fails `timed05alt-*`) is the expected effect of the shared setup. My probe B below confirms it.
- Connectivity, re-done: `_se_fields` has 2 callers (`_se_timed05` and the precondition). `SE_ALT_I2` has 1 user (`setitem`). The new case is collected (ids below). Every new assert ends in a named failure (probes B and C). The grep reasons in 05 hold: ccbot/ is unchanged, so the 38 missing-data grep hits are all pre-existing, and the build adds no `>`/`<` comparison and no dataclass.
- Data-hole edges: the only "data" is the fixture log. I checked all three cases. No I2 line, or 2+ lines: `len(own_i2) == 1`. An unreadable file: `whys == []`. A field with no time to strip: probe C. None of them passes vacuously.
- RI-012: no new text classification. The read-back filters on `LOG_LINE` groups by equality (`m[3] == "I2" and m[4] == RH_ID`), and `" | tests " in timed` is a fixture assert, not a classifier. No negative test is needed.
- Item 062 (simulator calling pickers): n/a, since no simulator or replay is touched.
- Not a BUG item, so there is no fix or guardrail pair to confirm. RI-001: no rule cites a number. RI-002: no default was removed, so the restore-a-default mutation does not apply.

## Tests re-run (output)
`python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k shallow_elif_branch` at 4619802:
```
16 passed, 504 deselected in 0.80s
```
Collected timed05 ids:
```
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-nogit]
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-nogit]
```
Full suite, `python3 -m pytest -q -p no:cacheprovider` at 4619802 (05: base 1011 passed, 1 skipped, head 1013 passed, 1 skipped):
```
1013 passed, 1 skipped in 130.61s (0:02:10)
```
The 1 skip is `SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'` (from `-rs`). `test_every_py_compiles_on_oldest_python` ran (python3.11 is on PATH at /usr/bin/python3.11, python3.10 is not) and passed. Also `python3.11 -m py_compile tests/test_pipeline_check.py && echo py311 ok` → `py311 ok`.

Mutants, one at a time on scripts/check_pipeline.py L1073 (`elif unsure("05"):   # item 095: anchor not read in a shallow clone`, under the L1067 `# item 090: TIMED gate`). Each was restored with `git checkout HEAD -- scripts/check_pipeline.py` and checked with `cmp` against a copy:
```
== elif False:
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
2 failed, 14 passed, 504 deselected in 1.00s
restored
== elif unsure("06"):
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
2 failed, 14 passed, 504 deselected in 4.21s
restored
```
Both match the plan's `2 failed, 14 passed` with exactly the named ids.

Done (a), probe A (my own, not in 05): I edited the shared constant `FIELDS["I2"]` itself (tests line 19) to `"4 files changed | tests 7 passed, 2 skipped in 3.25s"` and made no other edit:
```
== probe A (FIELDS changed, base code)
16 passed, 504 deselected in 3.90s
== probe A + M-timed
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
2 failed, 14 passed, 504 deselected in 1.06s
restored
== same probe on base f4f55a7 test file
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-nogit]
2 failed, 12 passed, 504 deselected in 1.22s
restored
```
So both halves of Done hold. A changed field passes with no other edit (it failed at base), and the TIMED mutant still fails.

Probe B (I2's one-off, re-run): the log `_se_edit` line (5357) is deleted from `_se_timed05`:
```
4 failed, 12 passed, 504 deselected in 1.30s
E           AssertionError: ('1 files changed | tests 1 passed in 0.01s', '1 files changed | tests 1 passed')   (x2)
E           AssertionError: ('2 files changed | tests 3 passed in 0.02s', '2 files changed | tests 3 passed')   (x2)
FAILED ...[timed05-nogit]  FAILED ...[timed05-shallow]  FAILED ...[timed05alt-nogit]  FAILED ...[timed05alt-shallow]
restored
```
Probe C (my own): `FIELDS["I2"]` is set to the untimed `"1 files changed | tests 1 passed"`, run with `-k "shallow_elif_branch and timed05-"`:
```
E       assert '1 files changed | tests 1 passed' != '1 files changed | tests 1 passed'
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-nogit]
2 failed, 518 deselected in 1.17s
restored
```
After all probes, `git status --short` in the worktree printed nothing.

`python3 scripts/check_handoff.py 108` (main checkout, exit 0):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 32
totals line: 32 rows -> 30 as-is, 2 fixed, 0 removed
PASS
```

## Real-data effect (diff_reports output, pasted)
not required (tests/test_pipeline_check.py only; `git diff --stat f4f55a7 4619802` lists `tests/test_pipeline_check.py | 38 +++++++++++++++++++++++++++++---------`, no TRIGGER or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-006, RI-008, RI-009, RI-010, RI-012
- RI-001 (ESCALATED): no filter or window rule is added. The fixture counts (1 I2 line for 150, 16 ids) are pinned by asserts and measured by my runs.
- RI-014 (OPEN): the parent issue. The shallow TIMED branch is still pinned by M-timed and K-timed (2 named ids each), also with a changed FIELDS value (probe A). OPEN, unchanged.
- RI-002: absent, unchanged or duplicated fixture data fails by name (probes B and C, `len(own_i2) == 1`, `whys == []`).
- RI-006: every count above is pasted from a command's output.
- RI-008: python3.11 compile ok, and the oldest-Python test ran and passed.
- RI-009 / item 097: own mkdtemp dir and a detached worktree; no stash.
- RI-010: the log line is written with `check_pipeline.py --log`, after this file.
- RI-012: no text classification is added (see I2 audit).

## Pipeline line (step 2)
check_pipeline line: `108: awaiting A1 (FULL)` (full output exit 0; INCOMPLETE none, UNTRACKED CHANGE none, STASH none)

## Sent back / sent to Audit
Sent to Audit: work/108/07-audit-task.md.
