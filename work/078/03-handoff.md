# 03 Research hand-off - 078
Status: READY (R3 has no shell. The orchestrator runs `python3 scripts/check_handoff.py 078` and pastes its output in Self-check. If it does not say PASS, 03 comes back to R3.)

Recurring issues checked (item 013), against this file:
- RI-014 (OPEN, the only open entry): 078 adds no git history walk. The probe baselines run fixture repos. The one REPO-history test, `test_untracked_from_is_fixed`, already returns early on a shallow repo (tests/test_pipeline_check.py L849-852). So a shallow clone cannot turn a 078 baseline red through `_walk`. 079 (RI-014's fix) is built after 078 (brief L3) and must keep 078's anchors (step 7).
- RI-001 (GUARDED): the only selection rules are "the anchor occurs exactly once" and "the target passes in the baseline". Feasibility gives the counts (6 of 6 anchors, 6 of 6 target defs). Nothing says "always" without a count.
- RI-002 (GUARDED, the request's link): a skipped target never reads as HOLDS. Steps 1-2 pin that in the mutated run and in the baseline, both with git and without it. Step 4 stops an unparseable JSON mutation from showing a false HOLDS. `recorded` holds counts measured on main and is not copied from old text (step 7).
- RI-004 / RI-005: every expected output line in the map is re-derived in Self-check.
- RI-006: the Totals come from the table. The orchestrator copies the log counts from check_handoff's output.
- RI-007: Scope FULL, and I1-I3 run. R3 wrote no code.
- RI-009: unchanged. Probes still run in a detached worktree outside the repo.
- RI-010 (the request's link): the fixed `code check` text becomes a per-entry claim, and step 6 tests that claim structurally.
- RI-011 / RI-012 / RI-013: this item adds a probe for each (N1, N2) or keeps one (RI-013 gets its reason key). Verdicts still come from the exit code and junit only.
- RI-003, RI-008: RI-003 does not apply (no calendar). For RI-008, the map uses no 3.11+ syntax, and test_safety's compile tests cover the edited files.

Sources:
- Repo working tree, branch daily-fixes/2026-11-19 before 075-077 are built, read 2026-11-19. No git was run by R3. Grep counts are quoted per row.
- Fetched 2026-11-19: https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html, https://docs.pytest.org/en/stable/reference/exit-codes.html, https://docs.pytest.org/en/stable/how-to/skipping.html, https://docs.python.org/3/library/json.html

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 (01 A1): `classify` gives HOLDS only for `results[key] == "failed"`. The `!= "passed"` mutant survives the test file (9 passed) | scripts/probe_guardrails.py L100-102; logs/audit/2026-11-18-074.md L60 | VERIFIED | - |
| F2 (01 A2): a baseline skip already gives `ERROR (baseline: target skipped)`. The "status check removed" mutant survives (9 passed) | probe_guardrails.py L178-181, L224-231; audit 074 L61 | VERIFIED | - |
| F3 (01 A3): junit writes a skip as `<skipped>`, a call-phase failure as `<failure>` and a setup/teardown failure as `<error>`. `read_junit` maps these tags | junitxml source (fetched); probe_guardrails.py L73-76 | VERIFIED | - |
| F4 (01 A4): strict-xfail XPASS is written as `<skipped>` ("xfail-marked test passes unexpectedly") and reads as NOT HELD. "No target is xfail-marked" was UNVERIFIED | junitxml source (`append_failure` with `wasxfail`); Grep `xfail` over the 5 probe test files → 0 hits | VERIFIED | Fixed: R3's Grep found 0 hits, so the second half is now measured. |
| F5 (01 A5): `pytest.skip()` skips while the test runs. `mark.skip` / `skipif` skip it at collection | how-to/skipping.html | VERIFIED | - |
| F6 (01 A6): A1's `pytest.skip("x")` replacement gave `0 failed, 1 passed, 0 errors, 1 skipped; ... failed: no; NOT HELD`, exit 1 | audit 074 L63 | VERIFIED | - |
| F7 (01 A7): exit 0 = "All tests were collected and passed successfully", 5 = "No tests were collected". The page says nothing about skips | exit-codes.html (fetched) | VERIFIED | - |
| F8 (01 A7): a file with only skipped tests exits 0, not 5 | no source (the page is silent) | UNSUPPORTED | Removed. The fixture holds a passing `test_ok`, so the map does not depend on this. |
| F9 (01 A8a): fixture (a) gives `NOT HELD`, `0 failed, 1 passed, 0 errors, 1 skipped`, `failed: no`, exit 1, and kills `!= "passed"` | trace of L204-238 and L100-102; audit 074 L63 | VERIFIED | - |
| F10 (01 A8b): fixture (b) gives `ERROR (baseline: target skipped)`. With the check removed, the mutated run skips and prints NOT HELD, so the mutant dies | trace of L224-231 | VERIFIED | - |
| F11 (01 A8): a new FILES entry changes no other test's counts, because each probe runs only its own test_file | tests/test_probe_guardrails.py L21-29, L85-87; probe_guardrails.py L220-235 | VERIFIED | - |
| F12 (01 B9): the fixed `code check: n/a (... conftest REPO ...)` text is printed for every entry without a module, and it is false on the fixture | probe_guardrails.py L191-195; audit 074 L83 | VERIFIED | - |
| F13 (01 B10 i-iv): REQUIRED can't simply gain the key. `_probe` has no module. L119 asserts `code check: n/a`. The well-formed test hard-codes the list | tests/test_probe_guardrails.py L51-56, L119, L203-217; probe_guardrails.py L47 | VERIFIED | - |
| F14 (01 B11): reason texts that cite tests/test_pipeline_check.py by line (L51-54, L862-865) | tests/test_pipeline_check.py L51-54 `_run`, L862-865 `_cp` | VERIFIED | Fixed: the lines are right today, but 076/077 edit check_pipeline and its tests before 078 is built. Reasons name functions (`_run`, `_cp`), not line numbers (step 3). |
| F15 (01 B11): RI-012 059 needs no reason, because tests/test_webull_sandbox.py L8-9 imports `ccbot.broker.webull_sandbox` | tests/test_webull_sandbox.py L9 | VERIFIED | - |
| F16 (01 B12): scripts/ has no `__init__.py` (UNVERIFIED), so `scripts.check_pipeline` would load as a namespace package | Glob `scripts/__init__.py` → no files | VERIFIED | Fixed: now measured by Glob. The map uses the reason key (no module check for check_pipeline). |
| F17 (01 C13): the 6 new anchors count 1 each in this working tree | Grep: check_pipeline.py L311, L519, L539, L551 (1 hit each); webull_sandbox.py L77 (1); tickers.json `"F": {` 1 hit, followed by `    "asset_type": "stock",` at L4 | VERIFIED | Counts on origin/main and on the built branch are I2's gate (step 7). |
| F18 (01 C14): with `tree = None`, `changed()` falls back to `HEAD...ref`, the RI-011 mutation. The criss-cross test fails | check_pipeline.py L517-525; tests/test_pipeline_check.py L592-626; recurring-issues.md L132 (1 failed, 69 passed) | VERIFIED | - |
| F19 (01 C15): with the bare `"429" in low`, the `http_status=500` case still raises at once. `RuntimeError("Msg: order 7a4291c failed")` is retried 5 times, so `waits == []` (L253) fails | webull_sandbox.py L64-77, L163-176; tests/test_webull_sandbox.py L242-253; RI-012 L139 | VERIFIED | `"7a4291c"` holds `429` (characters 3-5). |
| F20 (01 C15): RI-012's "1 failed, 292 passed" is a whole-suite count | RI-002 text 2026-11-14 "suite 293 passed" and RI-012 L139 the same day: 1 + 292 = 293 | VERIFIED | - |
| F21 (01 C16): `"foo_date": null` on F fails `(in_file \| in_code) - set(TICKER_NOTES) <= set(TICKER_FIELDS)`. The count will differ from 22 passed because the file has grown | tests/test_missing_inputs.py L238, L251-260 | VERIFIED | - |
| F22 (01 C17): `clashes.append(item)` → `pass` means `ID CLASH: 050 (origin/pr5)` (L278) is never printed | check_pipeline.py L542-551; tests/test_pipeline_check.py L270-280 | VERIFIED | - |
| F23 (01 C18): dropping the WORK_CODE term from `_is_code` removes `diag.py` on both paths. L1071/L1074, `test_is_code_examples` (L1047) and the branch test (L1127-1133) fail | check_pipeline.py L308-319, L565, L630; tests/test_pipeline_check.py L1044-1049, L1063-1075, L1127-1134 | VERIFIED | - |
| F24 (01 C19): with `rules = []`, the RULES BRANCH line stays `none` and the L486 equality fails. `test_log_time_exception_is_named_and_closed` pins `{"048"}` at L504 | check_pipeline.py L215, L539, L910; tests/test_pipeline_check.py L470-487, L499-504 | VERIFIED | - |
| F25 (01 C19): a `--log` refusal anchor probe as RI-010's stand-in (the code path was not looked up) | no source (R1 says not traced) | UNSUPPORTED | Removed. Out of scope: the request names 049 only, and N6 covers it. |
| F26 (01 C20): the 064 and 049 fixture tests now make anchor-shaped probes possible for RI-007 and RI-010 | tests/test_pipeline_check.py L1063, L470 | VERIFIED | - |
| F27 (01 D21): a malformed JSON mutation raises `JSONDecodeError` (a ValueError) in the test body, which is written as `<failure>` and gives a false HOLDS. Only `.py` is compiled today | json.html ("Subclass of ValueError"); junitxml source (`when == "call"` → `append_failure`); probe_guardrails.py L207-211 | VERIFIED | - |
| F28 (01 D22): all four check_pipeline targets are `skipif(git is None)` / `NO_GIT` | tests/test_pipeline_check.py L48, L269, L469, L591, L1062 | VERIFIED | - |
| F29 (01 D23): one red test in a shared file turns all of its probes into ERROR. Main had 342 passed, 1 skipped | probe_guardrails.py L178-181, L221-223; logs/audit/2026-11-19.md L33 | VERIFIED | - |
| F30 (01 D24): "076, 077 and 079 change scripts/check_pipeline.py before 078 is built" | brief.md L3: builds go 075 → 076 → 077 → 078 → 079 | WRONG | Fixed: only 076 and 077 are built before 078. 079 is built after 078 on top of it, so 079's own `test_shipped_probes_well_formed` run catches any 078 anchor that 079 moves (step 7). |
| F31 (01 D25): `test_shipped_probes_well_formed` asserts `len == 3` and the 3 targets | tests/test_probe_guardrails.py L205-217 | VERIFIED | - |
| F32 (01 Numbers): 3 + 6 = 9 probes, 5 distinct test files, 5 + 9 = 14 pytest runs | PROBES L25-45; table N1-N6 | VERIFIED | - |
| F33 (01 Numbers): 104.5-127.7 s for 3 probes; test_pipeline_check took 7.77 s for 52 tests at 062 | audit 074 L43; audit 2026-11-19 L47; work/062/05-build-report.md L56 | VERIFIED | - |
| F34 (02 past logs): 064 is on main, because merging #30 merged #28 | logs/audit/2026-11-17.md L8, L52 | VERIFIED | I2 still greps origin/main (step 7). |
| F35 (02 past logs): probe_guardrails.py is not on main. It runs from PR #32 head with `--ref origin/main` | logs/audit/2026-11-18.md L60; 2026-11-19.md L47 | VERIFIED | - |
| F36 (02 past logs): only N1-N3 reproduce a recorded A1 probe. RI-007 L85 is a positive probe, RI-009 L109 records no mutation, RI-010 L119 is a CLI probe | logs/recurring-issues.md L85, L109, L119, L132, L139, L25 | VERIFIED | - |
| F37 (02 FOR 1): every fixture test is `@NO_GIT` (L80, L95, L139, L150, L191). `test_classify_missing_or_bad_junit` is git-free | tests/test_probe_guardrails.py | VERIFIED | - |
| F38 (02 FOR 1): `append_skipped` writes `type="pytest.skip"`. `append_failure` with `wasxfail` writes `skipped` "xfail-marked test passes unexpectedly" | junitxml source (fetched) | VERIFIED | - |
| F39 (02 FOR 1): only a git fixture can kill the "baseline status check removed" mutant, and without git the script exits 2 | probe_guardrails.py L224-231, L251-253 | VERIFIED | - |
| F40 (02 FOR 2): `check_pipeline.py"` occurs 58 times in tests/test_pipeline_check.py, `diff_reports.py"` once in test_diff_reports.py, `tickers.json` twice in test_missing_inputs.py | Grep counts 58 / 1 (L8) / 2 | VERIFIED | - |
| F41 (02 FOR 2): an optional `module_path` key would give a real code check for check_pipeline | reasoning only, not run (R2 says so) | UNSUPPORTED | Removed: not in the map. The reason text must not claim a load check (step 3). |
| F42 (02 FOR 3): a malformed tickers.json mutation fails as `<failure>` in the call phase and gives a false HOLDS | junitxml source; tests/test_missing_inputs.py L255 | VERIFIED | - |
| F43 (02 FOR 3): RI-002's "22 passed" is from before `test_drop_each_input` was parametrized over MISSING_POLICY | recurring-issues.md L31: `test_drop_each_input[9]` has been parametrized since 005 | WRONG | Fixed: it was already parametrized. The count changed because MISSING_POLICY gained rows (9 at 005, then broker.*, tickers.* and others; test_missing_inputs.py L229-235) and tests were added. The conclusion stands: record measured counts. |
| F44 (02 AGAINST 1): 112 `def test_` in test_pipeline_check.py. 7.77 / 52 × 112 × 5 ≈ 84 s (labelled a linear guess) | Grep `^def test_` → 112; arithmetic in Self-check | VERIFIED | An estimate only, not a threshold. I2 measures it. |
| F45 (02 AGAINST 2): "Before 078 is built, 076, 077 and 079 all change scripts/check_pipeline.py" | brief.md L3 | WRONG | Fixed as in F30: 079 comes after 078. |
| F46 (02 AGAINST 2): PR #28 waited 3 days | logs/audit/2026-11-17.md L8 | VERIFIED | - |
| F47 (02 AGAINST 3): a finer N4 (drop the merge-base term at L549) is killed via L280 (UNVERIFIED) | no trace (R2 says so) | UNSUPPORTED | Removed: not in the map. N4 stays coarse and its id says so (`clash-line`). |
| F48 (02 Holes 5): the shallow REPO test L849-854 returns early when shallow | tests/test_pipeline_check.py L847-852 | VERIFIED | - |
| F49 (02 Languages): 074 logged `languages: N/A` | logs/research/2026-11-18.md L10 | VERIFIED | - |
| F50 (02 Holes 4): the N3 anchor spans two lines, and data edits do happen in F's entry (3ba835e) | config/tickers.json L3-4; recurring-issues.md L98 | VERIFIED | - |

**Totals:** 50 rows checked → **40 VERIFIED as-is**, **6 fixed**, **4 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- F8: "an only-skipped file exits 0, not 5". No source. The fixture avoids the question.
- F25: the `--log` refusal anchor probe for RI-010. Not traced, and out of scope.
- F41: the `module_path` option. Not run, so it is not built and no reason text may claim a load check.
- F47: the finer N4 mutation. Its kill was not traced.

## Implementation map
Decisions on the open questions (R3's call): R1 OQ1, ship N6 only. OQ2, coarse N4. OQ3, yes: the JSON check is step 4. OQ4, `recorded` holds counts measured on main (step 7). OQ5, the key is `no_module_reason`. OQ6, step 7.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | **tests/test_probe_guardrails.py: skip fixtures.** Add `FILES["tests/test_skip.py"] = 'import pytest\n\n\n@pytest.mark.skip(reason="x")\ndef test_s():\n    pass\n\n\ndef test_ok():\n    assert True\n'`. Add a new `@NO_GIT` test (for example `test_skip_entry_and_json_cases`, which also holds steps 3-4's probes) with probe s1 = `_probe("s1", replacement='import pytest; pytest.skip("x")')` and probe s2 = `_probe("s2", test_file="tests/test_skip.py", target="tests/test_skip.py::test_s")`. Assert s1's line contains `0 failed, 1 passed, 0 errors, 1 skipped`, `target tests/test_mod.py::test_f failed: no` and `NOT HELD`. Assert s2's line contains `ERROR (baseline: target skipped)`. Leave `test_mixed_run_reports_every_probe` unchanged. | fixture repo | new test | It passes on the shipped classify. Mutant A (`== "failed"` → `!= "passed"`, L100) fails it. Mutant B (L228-229 `elif status != "passed"` branch removed) fails it (s2 prints NOT HELD). Paste both mutant runs in 05. | – |
| 2 | **Git-free classify cases** in `test_classify_missing_or_bad_junit`: (i) a `<testcase classname="tests.test_mod" name="test_f"><skipped type="pytest.skip" message="x"/></testcase>` file, `classify(0, ...)` → `"NOT HELD"`; (ii) `<skipped message="xfail-marked test passes unexpectedly"/>`, `classify(1, ...)` → `"NOT HELD"`. | hand-built junit | 2 more asserts | `pytest tests/test_probe_guardrails.py -k classify` with mutant A fails (case i gives HOLDS). This works even where git is missing. | – |
| 3 | **Per-entry reason.** In `_run_probe`, replace the fixed text with `code check: n/a ({p['no_module_reason']})` when there is no `module`. In `_probe_all`, after the REQUIRED check, an entry with neither `module` nor `no_module_reason` gets `ERROR (probe entry lacks module or no_module_reason)` and pytest is not run. REQUIRED itself stays unchanged. If both keys are set, `module` wins. Give `_probe` a default `no_module_reason="fixture: tests/test_mod.py imports pkg/mod.py from the worktree root"` (it is dropped when `module` is passed). Add probe r0 = `_probe("r0", no_module_reason=None)` to step 1's test. Change L119 to assert `code check: n/a (fixture: tests/test_mod.py imports pkg/mod.py` in b's line. Add RI-013's reason: `"tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py"`. Reasons name functions or constants, never line numbers. | PROBES; fixture | new print text; entry error | b's line shows the fixture reason verbatim. r0's line shows `ERROR (probe entry lacks module or no_module_reason)` and `pytest not run`. Mutant C (fixed text restored) fails the b assert. Mutant D (neither-key check removed) fails r0. Mixed run still `TOTAL: 13 probes, 1 hold, 2 not held, 3 anchor missing, 7 error`. | – |
| 4 | **JSON validity.** Next to the `.py` compile check (L207-211): if `p["file"].endswith(".json")`, then `json.loads(mutated)` and, on `ValueError as e`, return `ERROR (mutation is not valid JSON: <e.msg>, line <e.lineno>)` with pytest not run. Add `FILES["pkg/data.json"] = '{"a": 1}\n'` and probe j1 = `_probe("j1", file="pkg/data.json", anchor='"a": 1', replacement='"a": ')` to step 1's test. | mutated text | ERROR line | j1's line contains `ERROR (mutation is not valid JSON: Expecting value`. Mutant E (check removed) fails it (j1 then gives NOT HELD). Step 1's test asserts `TOTAL: 4 probes, 0 hold, 1 not held, 0 anchor missing, 3 error` and exit 1. | – |
| 5 | **Six PROBES entries**, appended in request order after the 3 existing ones. Strings are byte for byte (`\n` = newline). Every entry gets `ri`, `test_file` and `recorded` (step 7).<br>N3 `RI-002-046-tickers-key`: file `config/tickers.json`, anchor `"F": {\n    "asset_type": "stock",`, replacement `"F": {\n    "foo_date": null,\n    "asset_type": "stock",`, test `tests/test_missing_inputs.py`, target `::test_ticker_fields_cover_file_and_code`, reason `"config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]"`.<br>N5 `RI-007-064-work-py`: `scripts/check_pipeline.py`, anchor `    return f.startswith(paths) or WORK_CODE.fullmatch(f) is not None`, replacement `    return f.startswith(paths)`, target `tests/test_pipeline_check.py::test_research_only_work_py_is_research_code`.<br>N4 `RI-009-037-clash-line`: anchor `                clashes.append(item)` (16 sp), replacement `                pass`, target `::test_same_id_on_main_and_open_branch_is_a_clash`.<br>N6 `RI-010-049-rules-line`: anchor `        rules = changed(*RULE_PATHS)` (8 sp), replacement `        rules = []`, target `::test_rules_branch_is_reported`.<br>N1 `RI-011-052-merge-tree`: anchor `        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None`, replacement `        tree = None`, target `::test_criss_cross_branch_lists_only_its_own_changes`.<br>The reason for N5/N4/N6/N1 is `"tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py"`.<br>N2 `RI-012-059-bare-429`: `ccbot/broker/webull_sandbox.py`, anchor `    return bool(_HTTP_429.search(low)) or "too many requests" in low or "too_many_requests" in low`, replacement `    return "429" in low or "too many requests" in low or "too_many_requests" in low`, test `tests/test_webull_sandbox.py`, target `::test_429_inside_other_text_is_not_retried`, `module: "ccbot.broker.webull_sandbox"` (no reason). | 4 committed files | 9 PROBES | Step 6 and step 7. | 6 of 6 anchors count 1 in this tree (Grep 2026-11-19, F17); 6 of 6 target defs present (Grep, lines in F18-F24). Main: step 7. |
| 6 | **`test_shipped_probes_well_formed`**: `len == 9`, 9 unique ids, the target list in step 5 order after the 3 existing ones. Every entry has exactly one of `module` / `no_module_reason`. A reason contains `Path(p["file"]).name`. For reason entries, the test file's text contains that basename. For `.json` entries, `json.loads(text.replace(anchor, replacement, 1))` succeeds. Also update the docstrings ("about 2 minutes", test file L4). | working tree | updated test | Passes on the built branch. Mutants: a reason without the basename, or an entry with both keys removed, each fails it (I2 shows one). | 5 of 5 reason entries pass the basename check today (F40: 58 / 1 / 2 hits; the 4 check_pipeline entries share one file). |
| 7 | **I2 measurement gate (05).** (a) For each of the 9 anchors, count it in `git show origin/main:<file>` and in the built branch file, and paste both counts. Both must be 1, and the branch is built on 076 and 077. (b) Run `python3 scripts/probe_guardrails.py --ref origin/main` and `--ref HEAD`. Both must print `TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error` and exit 0. Paste the full output, with per-probe seconds. (c) Set each new entry's `recorded` to `2026-11-19 (078/05): <n> failed, <m> passed` from the origin/main run (the per-file counts). Keep the 3 old values. (d) Set a1-auditor.md L36's "about 2 minutes" to the measured total. (e) Show that the mutated tickers.json parses (step 6 covers this in the suite). If any anchor is missing on main, I2 stops and reports. It does not loosen the anchor. | origin/main, built branch | 05 evidence | The pasted outputs. Note for 079 (built next): its run of `test_shipped_probes_well_formed` must stay green. | 9 of 9 hold is required. R3 did not measure it (no shell), which is why this step is a gate. |
| 8 | **Full suite** on the built branch. | – | pytest totals | `pytest -q` green. Shows the new FILES entries and the step 3 default reason broke no other test. | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `module` and `no_module_reason` (probe entry) | neither given | `ERROR (probe entry lacks module or no_module_reason)`; pytest not run; exit 1 |
| target status in the baseline junit | not in results / skipped / failed | `ERROR (baseline: target not found)` / `ERROR (baseline: target skipped)` / `ERROR (baseline: target failed)` |
| target status in the mutated junit | skipped (incl. XPASS shape) | `NOT HELD`, `failed: no`; never HOLDS |
| target in the mutated junit | not run | `ERROR (target not run)` (unchanged) |
| anchor on `--ref` | count 0 or 2+ | `ANCHOR MISSING (count n)` (unchanged); I2 must not loosen it |
| valid JSON after a `.json` mutation | parse fails | `ERROR (mutation is not valid JSON: <msg>, line <n>)`; pytest not run |
| `recorded` | missing | `recorded: none` (print only; never fills in a count) |
| per-probe runtime | not measured by R3 | n/a here: I2 measures it in step 7. The 84 s figure is a labelled estimate, not a limit |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Probe count | 3 existing + new | 3 + 6 = 9 | well-formed `len == 9` ✓ |
| Daily pytest runs | distinct test files + probes | 5 (realtest, diff_reports, pipeline_check, webull_sandbox, missing_inputs) + 9 = 14 | ✓ |
| Daily `--ref` line | hold = probes for exit 0 (L325) | 9 hold of 9 → `TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error` | ✓ |
| Mixed run unchanged | 1 + 2 + 3 + 7 | = 13. b now carries the default reason, and i1/i2/a have a module (module wins). No verdict changes | `TOTAL: 13 probes, 1 hold, 2 not held, 3 anchor missing, 7 error` ✓ |
| Step 1 test TOTAL | s1 NOT HELD, s2 ERROR, r0 ERROR, j1 ERROR | hold 0 + not held 1 + anchor 0 + error 3 = 4; 0 ≠ 4 → exit 1 | ✓ |
| s1 counts | test_mod has 2 tests: test_f skipped (f() calls skip), test_g passes | 0 failed + 1 passed + 0 errors + 1 skipped = 2 | matches A1 L63 ✓ |
| s1 under mutant A | `"skipped" != "passed"` is True → HOLDS | the assert `NOT HELD` fails | killed ✓ |
| s2 baseline | test_skip.py: test_s skipped, test_ok passes; bad = 0 → problem None → status "skipped" ≠ "passed" | → `ERROR (baseline: target skipped)` | ✓ (rc 0 for a pass + skip run is what I2's run confirms. A1's s1-shape run returned rc 0 or 1, since classify gave NOT HELD, not `pytest exit`) |
| s2 under mutant B | baseline accepted → the mutated run (pkg/mod.py return 2) leaves test_s skipped → NOT HELD | the `ERROR (baseline: target skipped)` assert fails | killed ✓ |
| Classify case (ii) | rc 1 ∈ (0, 1), no error tag, key present, status skipped | → NOT HELD | ✓ |
| j1 anchor | `'"a": 1'` in `'{"a": 1}\n'` | count 1; mutated `{"a": }` ≠ original; json.loads → "Expecting value" | ✓ |
| N3 replacement is JSON | key added before an existing key in the same object, comma kept | `"foo_date": null,` then `"asset_type": "stock",` | valid ✓ (step 6 asserts it) |
| N2 hits the text path | first case http_status 500 → `int(500) == 429` False → raise, waits [] | second case `"msg: order 7a4291c failed"` contains "429" → retried, waits = [2, 4, 8, 16, 32] ≠ [] | target fails ✓ |
| N1/N4/N5/N6 compile | `tree = None`; `pass` as an if body; `return f.startswith(paths)`; `rules = []` | all valid at the same indent | ✓ |
| Reason basename check | `Path(file).name` in reason | "check_pipeline.py" ×4, "tickers.json", "diff_reports.py" each appear in their reason text in step 3/5 | 6 of 6 reason entries ✓ |
| Runtime estimate (F44) | 7.77 / 52 × 112 × 5 | 0.1494 × 112 = 16.73; × 5 = 83.7 ≈ 84 s | estimate only ✓ |
| Totals | verified + fixed + removed | 40 + 6 + 4 = 50 rows | ✓ |

check_handoff output (run by the orchestrator 2026-11-19 23:37 UTC, exit 0; must say PASS):
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 50
totals line: 50 rows -> 40 as-is, 6 fixed, 4 removed
PASS
```