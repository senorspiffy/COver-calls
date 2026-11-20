# 03 Research hand-off - 076
Status: READY

Type BUG, Scope FULL (not RESEARCH ONLY, so no 07-audit-task.md from R3). This is process tooling only: it does not touch trading, quotes or the $3k account's rules. The RULES change to `.claude/agents/i2-builder.md` needs the person's OK in PR review.

Decision for I1: **option B**, with A's pass ≤ total check kept for items before the cutoff. From item 076 on, the I2 `tests` field is pytest's summary line copied as printed. Items 045-075 keep `tests <pass>/<total>`, and `--log` and INCOMPLETE now also refuse pass > total there. Option C (cross-check against 05) and option D (`--log` runs pytest) are left out. C needs a fixed label in 05 to avoid RI-012, and it overlaps 077. D is about 60 s per call and recursive (01 option D). Possible follow-up for A1: C with a fixed `Suite:` label in templates/build-report.md.

Recurring issues checked (step 0): RI-014 is the only OPEN entry, and none are ESCALATED. The map does not touch `_walk` or clone depth: the new tests use tmp dirs without git, and the repo check is the existing `test_repo_pipeline_has_no_skipped_items`. Also checked against the item's own and the related GUARDED entries:
- RI-006: this item's root cause. The guardrail is in step 1.
- RI-012: a full-line `re.fullmatch` is used, never a substring.
- RI-002: an absent or unparsable summary line is refused, never defaulted.
- RI-001, RI-004, RI-005: feasibility counts, worked examples and Self-check are below.
- RI-010: the i2 text is pinned by a test.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| #1 01 R-1: LOG_FORMAT["I2"] and LOG_HINT["I2"] text; `<total>` undefined | scripts/check_pipeline.py L234, L244 (read) | VERIFIED | – |
| #2 01 R-2: i2-builder.md L25 has the same text, no definition | .claude/agents/i2-builder.md L25 | VERIFIED | – |
| #3 01 R-3: write_log refuses with exit 2 (L426-431); INCOMPLETE re-checks lines of items ≥ LOG_CHECK_FROM=45 (L190, L394-399); a tighter regex turns 045-075 red without a cutoff | check_pipeline.py L190, L394-399, L423-431 | VERIFIED | – |
| #4 01 R-4: trailing `\b.*` admits notes; 064 and 062 examples | logs/implementation/2026-11-15.md L5, 2026-11-13.md L6 | VERIFIED | – |
| #5 01 R-5: pinned hint L562/L566, example-fits test L548-550, FIELDS["I2"] L16, literal lines L380, 390, 404, 412, 428, 442-443, 533, 537, 557 | tests/test_pipeline_check.py (Grep) | VERIFIED | FIELDS is also used at L44, L446, L514, L516, L1536-1537 ("many fixtures") |
| #6 01 R-6: nothing else parses the field | Grep over scripts/ ccbot/ tests/ .claude/ templates/ | VERIFIED | – |
| #7 01 R-7: 064 316/317; 074 453/454 = 453+1; 070 1+383+1=385 and 1+403+1=405; 069 1+399+1=401; 061 1+292+1=294; 063 1+297+1=299 | work/074/05 L59; 070/05 L224, L290; 069/05 L259; 061/05 L156; 063/05 L99 | VERIFIED | – |
| #8 01 R-8: 072 411/411 for 411 passed, 1 skipped; 058 218/218 for 218 passed, 1 skipped | logs/audit/2026-11-18-072.md L72-76; logs/implementation/2026-11-12.md L13; work/058/05 L11 | VERIFIED | – |
| #9 01 R-9: 065's 49/49 was a single file | 072 audit L74 | VERIFIED | – |
| #10 01 R-10: p/t hides failures (070: 1 failed + 1 skipped) | 070/05 L224 | VERIFIED | – |
| #11 01 R-11: machine-dependent skips | tests/test_calendar.py L110; test_pipeline_check.py L48; test_probe_guardrails.py L19; test_safety.py L119 | VERIFIED | – |
| #12 01 R-12: pytest unpinned (`dev = ["pytest"]` L13, testpaths L20); installed version UNVERIFIED | pyproject.toml L13, L20; orchestrator run 2026-11-19 23:30 UTC | fixed | Installed: `pytest 9.1.1` (orchestrator's run; R3 has no shell). I2 re-runs `python3 -m pytest --version` and pastes it in 05. 9.1.1 is a real release [https://docs.pytest.org/en/stable/announce/release-9.1.1.html] |
| #13 01 P-1: summary stats line docstring `=== 12 passed, 2 errors in Xs===` | https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py | VERIFIED | The docstring example is illustrative only |
| #14 01 P-2: KNOWN_TYPES order failed, passed, skipped, deselected, xfailed, xpassed, warnings, error, then 3 subtests keys; unknown types appended | main terminal.py (`list(KNOWN_TYPES) + unknown_types`) | VERIFIED | – |
| #15 01 P-2: A1's regex (072 audit L93) refuses any run with a failure and admits failed after passed | 072 audit L93 + KNOWN_TYPES order | VERIFIED | – |
| #16 01 P-2/Q3: whether the installed pytest has the subtests keys is UNVERIFIED | https://docs.pytest.org/en/9.0.x/how-to/subtests.html ("Added in version 9.0"); https://docs.pytest.org/en/9.0.x/_modules/_pytest/terminal.html | fixed | Subtests are built in from 9.0. The keys are in 9.0.x and main, so 9.1.1 has them (inferred from the version order). The suite has 0 subtests uses (Grep tests/). |
| #17 01 P-3: pluralize only error/warnings/test; `1 error`/`2 errors`, `1 warning`/`2 warnings` | main terminal.py `pluralize` | VERIFIED | – |
| #18 01 P-4: `no tests ran` when no parts | main terminal.py `_build_normal_summary_stats_line` | VERIFIED | – |
| #19 01 P-5: deselected filled by pytest_deselected; `-k` quote | main terminal.py; https://docs.pytest.org/en/stable/how-to/usage.html | VERIFIED | The quote continues "(case-insensitive)" |
| #20 01 P-6: docs example `1 failed, 1 passed, 1 skipped, 1 xfailed, 1 xpassed, 1 error in 0.12s` | https://docs.pytest.org/en/stable/how-to/output.html | VERIFIED | The docs show it with `==` padding (not -q) |
| #21 01 P-7: skip and xfail counted separately; skip definition | https://docs.pytest.org/en/stable/how-to/skipping.html | VERIFIED | – |
| #22 01 P-8: exit codes 0, 1, 5 | https://docs.pytest.org/en/stable/reference/exit-codes.html | VERIFIED | – |
| #23 01 P-9: warnings is not a test count (inference) | P-2/P-3 | VERIFIED | Labelled as inference |
| #24 01 Numbers: 072 "411 + 1 = 412 collected and run", should be 411/412 | 072/05, 072 audit L73 | fixed | Arithmetic correct. Wording: "412 collected (411 passed, 1 skipped)". Skipped tests are not run to completion (02 Spanish row, #48) |
| #25 01 Numbers: 058 218 + 1 = 219 | 058/05 L11 | VERIFIED | – |
| #26 01 Numbers: 070 1 + 383 + 1 = 385 fits the definition but hides the failure | 070/05 L224 | VERIFIED | – |
| #27 01 Numbers: neither pass ≤ total nor an order check catches 411/411 or `411 passed` (internally consistent) | reasoning | VERIFIED | Kept as the stated limit in the i2 text (step 3) |
| #28 01 Option B: R1 regex `(\d+ failed, )?\d+ passed...`; whether an all-failed run prints `passed` UNVERIFIED (Q4) | main, 9.0.x and 7.4.x terminal.py (`if reports:`); https://www.guru99.com/fr/pytest-tutorial.html (`2 failed, 2 deselected in 0.02 seconds`) | fixed | Zero counts are never printed, so an all-failed run has no `passed` part and R1's regex would refuse it. The map uses 02 FOR 3a's "each type optional, at least one" |
| #29 01 Option D: about 60 s per run (`414 passed, 1 skipped in 64.87s`) | 072 audit L39 | VERIFIED | – |
| #30 01 Q5: no textual clash with 077 (UNVERIFIED) | work/077/request.md L8-13; check_pipeline.py L417 | fixed | 077 points 3-4 change `i3_verdict`, which reads `LOG_FORMAT["I3"]` (L417). Constraint in step 1: LOG_FORMAT values stay plain regex strings keyed by agent |
| #31 02 FOR 1: same core KNOWN_TYPES in 7.4.x, 9.0.x and main | https://pytest.org/en/7.4.x/_modules/_pytest/terminal.html; https://docs.pytest.org/en/9.0.x/_modules/_pytest/terminal.html | VERIFIED | – |
| #32 02 FOR 1: a part is added only `if reports:` | main, 9.0.x, 7.4.x terminal.py | VERIFIED | – |
| #33 02 FOR 1: `-q` has no `=` padding (`display_sep = self.verbosity >= 0`); the Japanese page shows a bare `4 passed in 0.02s` | main terminal.py; https://enu23456.hatenablog.com/entry/2022/11/08/184211 | VERIFIED | – |
| #34 02 FOR 2: French/Italian xfail quotes and translations | https://www.guru99.com/fr/pytest-tutorial.html; https://www.guru99.com/it/pytest-tutorial.html | VERIFIED | The French reads literally "the test having failed"; "(xfail)" is R2's gloss, which fits the context |
| #35 02 FOR 2: 070 would read `1 failed, 383 passed, 1 skipped` | 070/05 L224 | VERIFIED | – |
| #36 02 FOR 3a: all-failed run prints `N failed in Xs`; require ≥1 known part in order, each at most once; refuse `no tests ran` | `if reports:`; guru99 fr/it `2 failed, 1 passed in 0.05 seconds`, `2 failed, 2 deselected in 0.02 seconds` | VERIFIED | – |
| #37 02 FOR 3b: subtests keys are in 9.0.x and main, not 7.4.x; installed version UNVERIFIED | sources in #31; orchestrator fact | fixed | Installed 9.1.1 (see #12, #16). The map allows the 3 subtests keys in order |
| #38 02 FOR 3c: timing `in 0.07 seconds` (old) and `in 0.12s` (current); do not pin | guru99 fr/it; https://pytest-docs-ru.readthedocs.io/ru/latest/example/markers.html | fixed | Verified, with one gap: runs of 60 s or more print ` in 68.26s (0:01:08)` (`format_session_duration`, main and 9.0.x; 074/05 L59). The full suite runs about 60 s, so the tail must allow the ` (H:MM:SS)` suffix |
| #39 02 FOR 3d: cutoff constant keeps 045-075 valid | check_pipeline.py L394-399 | VERIFIED | – |
| #40 02 AGAINST 1: B alone cannot see an omitted skip | reasoning from #32 | VERIFIED | – |
| #41 02 AGAINST 2: text drifted; "9.x added three subtests keys" | https://docs.pytest.org/en/9.0.x/how-to/subtests.html | fixed | Added in 9.0 exactly. Absent in 7.4.x; 8.x not checked |
| #42 02 AGAINST 2: unknown and plugin types are appended at the end | main terminal.py `_set_main_color` | VERIFIED | The map refuses unknown parts (loud exit 2). Allowing `\d+ [a-z ]+` would let a misplaced `1 failed` through and undo the order check |
| #43 02 AGAINST 3: about 10 literal fixture lines + 2 pinned hints + FIELDS | test_pipeline_check.py L380, 390, 404, 412, 428, 442, 443, 533, 537, 557; L562, L566 | VERIFIED | 10 + 2 |
| #44 02 Past logs: 072 audit L72-76 and L88-95 (P2 with both options) | logs/audit/2026-11-18-072.md | VERIFIED | – |
| #45 02 Past logs: RI-006 L77-78, RI-012 L138-141 | logs/recurring-issues.md | VERIFIED | – |
| #46 02 Past logs: 073 used German/Korean/Portuguese; 072's R2 used Languages N/A | logs/research/2026-11-18.md L9; work/072/02 L43 | VERIFIED | – |
| #47 02 Mandarin row: skip reasons only with `-rs`; `1 passed, 2 skipped in 0.04s` | https://cnblogs.com/a-wyw/p/16198885.html | VERIFIED | Translation correct |
| #48 02 Spanish row: skip quote; "Deselected tests are left out of the report entirely" | https://allurereport.org/es/docs/test-statuses | fixed | Skip quote and translation correct. The deselection sentence is about Allure TestOps test plans, not pytest. pytest prints `N deselected` in its stats line (#19, #51) |
| #49 02 Japanese row | https://enu23456.hatenablog.com/entry/2022/11/08/184211 | VERIFIED | The source wraps `pytest -q` in backticks |
| #50 02 French row (gouarin): tag and filter at run time | https://gouarin.github.io/python-packaging-2023/pytest | VERIFIED | – |
| #51 02 Russian row: `-k` quote; `3 passed, 1 deselected in 0.12s`; a path subset shows no deselected | https://pytest-docs-ru.readthedocs.io/ru/latest/example/markers.html; main terminal.py (deselected only via `pytest_deselected`) | VERIFIED | The page shows it `=`-padded (not -q) |
| #52 02 Italian row: `... in 0.07 seconds`; quote | https://www.guru99.com/it/pytest-tutorial.html | VERIFIED | – |
| #53 02 Holes: `-qq` (verbosity < -1) prints no summary line | main terminal.py `summary_stats` early return | VERIFIED | – |
| #54 02 Holes: whether a `pytest_terminal_summary` hook can print after the stats line is UNVERIFIED | main and 9.0.x terminal.py `pytest_sessionfinish` | fixed | The hook runs before `summary_stats()`, so the stats line is the last summary line. The repo has no such hook (Grep tests/: 0 hits for terminal_summary, deselect, modifyitems, addopts) |

**Totals:** 54 rows checked → **44 VERIFIED as-is**, **10 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Every UNVERIFIED point in 01/02 is now settled (#12, #16, #28, #30, #37, #54) or corrected (#24, #38, #41, #48).

## Implementation map
Constraint for every step: keep `LOG_FORMAT` a dict of plain regex strings keyed by agent, because `incomplete()` L417 and 077 read `LOG_FORMAT["I3"]`. Build on 075's code (brief order).

The I2 regex (step 1). I1 may rebuild it another way, as long as every case in the Self-check gives the same result:
```python
TESTS_FORMAT_FROM = 76   # item 076: from this ID on the I2 tests field is pytest's summary line as printed
_N = r"[1-9]\d*"
_END = r"(?:, (?=[1-9])|(?=$| in | \())"          # a part is followed by ", <next part>" or the end of the stats
_STATS_PARTS = (rf"{_N} failed", rf"{_N} passed", rf"{_N} skipped", rf"{_N} xfailed", rf"{_N} xpassed",
                rf"(?:1 warning|(?!1 ){_N} warnings)", rf"(?:1 error|(?!1 ){_N} errors)",
                rf"{_N} subtests passed", rf"{_N} subtests failed", rf"{_N} subtests skipped")
# KNOWN_TYPES order (pytest main/9.0.x terminal.py), "deselected" left out on purpose: a full-suite run has none.
_STATS = r"(?=[1-9])" + "".join(f"(?:{p}{_END})?" for p in _STATS_PARTS)
_TAIL = r"(?: in \d+\.\d+(?:s| seconds)(?: \(\d+:\d{2}:\d{2}\))?)?(?: \(.*\))?"
LOG_FORMAT["I2"] = rf"\d+ files? changed \| tests {_STATS}{_TAIL}"
I2_BEFORE = r"\d+ files? changed \| tests (\d+)/(\d+)\b.*"    # items LOG_CHECK_FROM..TESTS_FORMAT_FROM-1
```

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: add `TESTS_FORMAT_FROM = 76` (comment as above), the new `LOG_FORMAT["I2"]`, and `I2_BEFORE`. Add one helper, `log_fields_ok(agent, item, fields)`: for I2 with `int(item) < TESTS_FORMAT_FROM`, fullmatch `I2_BEFORE` and require `int(pass) <= int(total)`; otherwise fullmatch `LOG_FORMAT[agent]`. Use it in `write_log` (L426-427) and in `incomplete` (L394-396) instead of the bare `re.fullmatch`. Update the module docstring L66-69: from TESTS_FORMAT_FROM the I2 tests field is the last line of `python3 -m pytest -q` from the repo root, as printed; before it, `<pass>/<total>` with total = passed + failed + skipped + errors + xfailed + xpassed (deselected and warnings are not tests) and pass ≤ total | the I2 fields string, item ID | exit 2 + hint on refusal; INCOMPLETE entry for a bad committed line | New tests T1-T3 (step 4). Mutations: (m1) `_END` → `(?:, )?` (order not enforced) → T2 order cases fail; (m2) pass ≤ total check removed → T3 `tests 10/9` case fails; (m3) `TESTS_FORMAT_FROM = 77` → T3 "076 old form refused" fails; (m4) `= 75` → T3 "075 old form accepted" fails; (m5) `deselected` added to the parts → T2 deselected case fails | Old form + pass ≤ total: 35 of 35 committed I2 lines for items 045-074 pass (logs/implementation 2026-11-05 to 2026-11-19, Grep `\| I2 \|`; the only equal cases are 058 218/218, 065 49/49, 072 411/411, so pass > total = 0). Re-checked by `test_repo_pipeline_has_no_skipped_items` (INCOMPLETE none). New form: 9 of 9 real full-suite lines fit (074/05 L38, L59; 070/05 L224, L290; 069/05 L259; 061/05 L156; 063/05 L99; 058/05 L11; 072 audit L39), worked in Self-check |
| 2 | `LOG_HINT["I2"]` = `("<n> files changed \| tests <last line of python3 -m pytest -q, as printed>", "2 files changed \| tests 9 passed, 1 skipped in 3.21s")`. Keep the old hint `("<n> files changed \| tests <pass>/<total> (pass <= total)", "2 files changed \| tests 9/9")` for items < 76, through a `log_hint(agent, item)` helper used by both refusal texts (L398, L429) | item ID | the refusal and INCOMPLETE text name the form that applies to that item | `test_log_hints_match_formats` (L543) still passes, and T5 checks the old example against `I2_BEFORE` | – |
| 3 | .claude/agents/i2-builder.md L25 (RULES, person's OK): the field is `tests <the last line of python3 -m pytest -q run from the repo root, copied as printed>`, e.g. `8 files changed \| tests 411 passed, 1 skipped in 64.87s`. It is the same line pasted in 05 Test output. It is never retyped, summed or shortened. Full suite only (no `-k`, `-m` or file paths; `deselected` is refused). Limit, written down: the field cannot prove a full-suite run or catch a dropped part; I3 and A1 compare it with 05 | – | rule text | T4: i2-builder.md contains `python3 -m pytest -q` and `as printed`, and no longer contains `<pass>/<total>` | – |
| 4 | tests/test_pipeline_check.py: FIELDS["I2"] → `"1 files changed \| tests 1 passed"`. L380/L390 → `tests 9 passed, 1 skipped in 3.21s`. L404, L412, L442, L537 → `tests 1 passed`. L428, L533, L557 stay malformed (`see 05`) on purpose. L562/L566 → the new hint text. New tests: T1 accepts each Self-check accept case for item 150; T2 refuses each refuse case for item 150 (exit 2, nothing written); T3 is the cutoff boundary: `--log I2 075 "... tests 9/9"` → 0, `075 ... tests 10/9` → 2, `076 ... tests 9/9` → 2, `076 ... tests 9 passed` → 0; the same four as committed lines give INCOMPLETE for exactly `075 (10/9)` and `076 (9/9)`; T4 is the i2 text pin (step 3); T5 checks the old hint example against `I2_BEFORE` | fixtures in tmp_path (no git) | tests | Full suite `python3 -m pytest -q` passes; mutations m1-m5 each fail ≥ 1 named test (I2 runs them in a scratch worktree, RI-009) | T1 14 accept cases, T2 14 refuse cases (Self-check) |
| 5 | Repo check and own log line. On the branch, `python3 scripts/check_pipeline.py` exit 0 with INCOMPLETE none. I2's own 076 line uses the new form, e.g. `--log I2 076 "<n> files changed \| tests <last line as printed>"` | repo logs/ and work/ | log line | `test_repo_pipeline_has_no_skipped_items` passes. I3 checks that 076's I2 field equals the full-suite line in 076/05 | 076's line is the first new-form line (0 committed today); 075's line, if still to come, uses the old form |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| pytest summary line (I2 copies it into `--log I2`, items ≥ 76) | The run was cut off, `-qq` was used (no line), `no tests ran` (exit 5), or the field is empty | `--log refused: ... does not match "<n> files changed \| tests <last line of python3 -m pytest -q, as printed>"`, exit 2, nothing written. I2 re-runs the suite. It never types, sums or defaults a count |
| `<pass>/<total>` (items 045-075) | non-numeric, missing, or pass > total | refused (exit 2) with the old hint. A committed line → `INCOMPLETE: <ID> (log line for I2 does not match its format (item 045) ...)` |
| A part pytest may print that is not in the list (a plugin type, or a future pytest) | Not printed by 9.1.1 on this suite (no plugins, 0 subtests) | Refused loudly (exit 2). The fix is a new item that adds the part in order. It is never loosened in place, and the part is never dropped from the line |
| Installed pytest version | reported 9.1.1 by the orchestrator (R3 cannot run it) | I2 pastes `python3 -m pytest --version` in 05. If it is below 9.0, the subtests parts are simply never printed (still valid) |
| Skip count (machine-dependent, 01 R-11) | differs between machines | No default. The line is as printed on the build machine. I3 compares by names in 05, not by assuming the same count |

## Self-check
Regex = step 1's `LOG_FORMAT["I2"]`, applied with `re.fullmatch` after `.strip()`. The prefix `N files changed | ` is the same in every case, so each case shows only the text after `tests `.

| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Cutoff | new form iff int(ID) ≥ 76 | 76 ≥ 76 → new; 75 < 76 → old; 45 ≤ 75 → old and checked; 44 < 45 → not checked | as in T3 |
| pass ≤ total (old) | int(p) ≤ int(t) | 218 ≤ 218 ok; 411 ≤ 411 ok; 49 ≤ 49 ok; 383 ≤ 385 ok; 10 > 9 → refuse | 35/35 committed lines ok, T3 refuses 10/9 |
| A1 `411 passed, 1 skipped in 64.87s` | passed + `, ` → skipped + END ` in ` → TAIL ` in 64.87s` | parts: passed, skipped (KNOWN order 2 < 3) | accept |
| A2 `453 passed, 1 skipped in 68.26s (0:01:08)` | TAIL `(?: \(\d+:\d{2}:\d{2}\))?` | `0:01:08` = 1 digit : 2 : 2 | accept |
| A3 `1 failed, 383 passed, 1 skipped in 58.86s` | order 1 < 2 < 3 | – | accept |
| A4 `2 failed in 0.05s` (all failed) | failed + END ` in ` | no passed part needed | accept |
| A5 `411 passed, 1 skipped` (no time) | END `(?=$)` | – | accept |
| A6 `255 passed, 1 skipped (round 2: test case added)` | END `(?= \()`, TAIL note `\(.*\)` | – | accept |
| A7 `411 passed, 1 skipped, 3 warnings in 60.00s` | warnings alt 2: lookahead `(?!1 )` on `3 ` ok, `3 warnings` | order 3 < 7 | accept |
| A8 `1 passed, 1 warning in 0.10s` | warnings alt 1 `1 warning` + END ` in ` | – | accept |
| A9 `1 error in 1.00s`; A10 `2 errors in 1.00s` | error alts | 1 → singular, 2 → plural | accept both |
| A11 `21 warnings in 1.00s` | alt 1 needs `1 ` at start: `21` no; alt 2 `(?!1 )` on `21` ok | – | accept |
| A12 `3 failed, 3 subtests passed in 0.12s` (pytest subtests doc) | `N failed` cannot match `3 subtests`; order 1 < 8 | – | accept |
| A13 `1 failed, 1 passed, 2 skipped, 1 xfailed, 1 xpassed in 0.07 seconds` (guru99) | TAIL `(?:s\| seconds)` | order 1 < 2 < 3 < 5 < 6 | accept |
| A14 hint example `9 passed, 1 skipped in 3.21s` | as A1 | – | accept (fits `test_log_hints_match_formats`) |
| R1 `no tests ran` | `(?=[1-9])` | `n` is not a digit | refuse |
| R2 `411/412` | no part matches `411/` | – | refuse (old form, item ≥ 76) |
| R3 `411 passed, 1 failed` | after passed, no later part matches `1 failed` (`N subtests failed` needs `subtests`) | order 2 > 1 | refuse |
| R4 `1 skipped, 411 passed` | order 3 > 2 | – | refuse |
| R5 `411 passed, 1 skipped, 1 skipped` | each part at most once | – | refuse |
| R6 `1 errors`; R7 `2 error` | alt 1 `1 error` then `s` fails END; alt 2 `(?!1 )` fails / needs `errors` | – | refuse both |
| R8 `1 warnings` | as R6 | – | refuse |
| R9 `3 passed, 1 deselected in 0.12s` (a `-k` run) | deselected not in the parts | – | refuse |
| R10 `0 passed` | `[1-9]` | 0 is not 1-9 | refuse |
| R11 `411 passed,` / `411 passed, ` | `, (?=[1-9])` needs a digit next | – | refuse |
| R12 `411 passed in 64.87s extra` | TAIL ends after `s`; ` extra` is not ` (...)` | – | refuse |
| R13 `411 passed garbage` | END needs `, `, end, ` in ` or ` (` | – | refuse |
| R14 empty after `tests ` | `(?=[1-9])` | – | refuse |
| Fixture `1 files changed \| tests 1 passed` | `\d+ files? changed` + A5 shape | – | accept (FIELDS["I2"]) |
| Feasibility, old lines | 35 lines for items 045-074 | 2+1+3+1+1+1+6+2+2+4+1+4+6+1 = 35 (per log date 11-05 … 11-19) | 35 of 35 pass |

check_handoff output (run by the orchestrator 2026-11-19 23:37 UTC, exit 0; must say PASS):
```
sources count (unique URLs in 01-research.md): 5
fact-check rows: 54
totals line: 54 rows -> 44 as-is, 10 fixed, 0 removed
PASS
```
Log fields: <counts from check_handoff's totals line> | READY
