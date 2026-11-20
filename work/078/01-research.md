# 01 Research brief - 078

## Question
Item 078 has three parts, all for `scripts/probe_guardrails.py` (074):
1. Which fixture tests kill the surviving `== "failed"` -> `!= "passed"` mutant (a skipped target read as HOLDS) and pin `ERROR (baseline: target skipped)`?
2. How should the `code check: n/a` reason move out of `_run_probe` and into each probe entry?
3. What are the exact anchor, replacement and target test for the six new probes: RI-002 046, RI-007 064, RI-009 037, RI-010 049, RI-011 052 and RI-012 059?

Inputs read:
- work/078/request.md and the scratchpad brief.md
- logs/recurring-issues.md (RI-002, RI-007, RI-009 to RI-014)
- logs/audit/2026-11-18-074.md (P1-P3), logs/audit/2026-11-19.md, logs/efficiency/2026-11-19.md
- work/074/01-research.md, and work/075, 076, 077 request.md
- scripts/probe_guardrails.py (whole file), tests/test_probe_guardrails.py (whole file)
- scripts/check_pipeline.py L200-334, L455-578
- tests/test_pipeline_check.py L1-60, L255-314, L455-627, L862-909, L1040-1076
- ccbot/broker/webull_sandbox.py L1-77, L163-183; tests/test_webull_sandbox.py L1-50, L225-264
- tests/test_missing_inputs.py L225-274; config/tickers.json L1-11

All line numbers and anchor counts below come from this branch's working tree (daily-fixes/2026-11-19 before 075-077 are built). I have no shell, so none of them were checked on origin/main. Every "will fail" below is a prediction from reading the code. None is a measured run.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### A. Part 1: the skipped-target gap
1. `classify` returns HOLDS only when `results[key] == "failed"` (L100-102). Every other status, skipped included, gives NOT HELD. The mutant `!= "passed"` would turn a skipped target into HOLDS, and it survives all 9 tests [repo: scripts/probe_guardrails.py L100-102; logs/audit/2026-11-18-074.md L60].
2. `_baseline` flags only failed/error results or rc != 0. `_run_probe` then needs the target's baseline status to be "passed", or it returns `ERROR (baseline: target <status>)`. So a baseline skip already gives `ERROR (baseline: target skipped)`, but nothing pins it (mutant "baseline target-status check removed": 9 passed) [repo: scripts/probe_guardrails.py L178-181, L224-231; logs/audit/2026-11-18-074.md L61].
3. In pytest's junit writer, `report.skipped` gives a `<skipped>` child (`type="pytest.skip"`, or `type="pytest.xfail"` for xfail). A failure in the `call` phase gives `<failure>`. A failure in setup or teardown gives `<error>` [https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html]. `read_junit` maps these tags to skipped, failed and error [repo: scripts/probe_guardrails.py L73-76].
4. A strict-xfail XPASS takes the failure path, and the writer adds a `<skipped>` element ("xfail-marked test passes unexpectedly") instead of `<failure>` [https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html]. So `read_junit` reads it as skipped, which gives NOT HELD. That is fail-safe. No shipped target is xfail-marked (Grep of the 4 target test files for `xfail`: not run, UNVERIFIED).
5. `pytest.skip()` skips a test while it runs. `@pytest.mark.skip` and `skipif` skip it at collection [https://docs.pytest.org/en/stable/how-to/skipping.html].
6. A1 already ran the mutated-skip case on the fixture repo. Replacing `return 1` with `import pytest; pytest.skip("x")` gave `0 failed, 1 passed, 0 errors, 1 skipped; target ... failed: no; NOT HELD`, exit 1 [repo: logs/audit/2026-11-18-074.md L63].
7. Exit code 0 means "All tests were collected and passed successfully", and 5 means "No tests were collected". The page does not say which code a run with skips gets [https://docs.pytest.org/en/stable/reference/exit-codes.html]. A file with only skipped tests exits 0, not 5: UNVERIFIED. To keep the baseline-skip fixture away from that question, the skip test file should also hold one passing test (see 8).
8. Proposed fixtures (for I1 to fix the exact form):
   - (a) **Mutated run skips the target.** `_probe("s1", replacement='import pytest; pytest.skip("x")')`. Expected line: `NOT HELD`, `1 skipped`, `target tests/test_mod.py::test_f failed: no`; exit 1. This kills `!= "passed"`, because that mutant would print HOLDS.
   - (b) **Baseline skips the target.** Add a new FILES entry, for example `tests/test_skip.py` = `import pytest\n\n\n@pytest.mark.skip(reason="x")\ndef test_s():\n    pass\n\n\ndef test_ok():\n    assert True\n`. The probe is `_probe("s2", test_file="tests/test_skip.py", target="tests/test_skip.py::test_s")`. Expected: `ERROR (baseline: target skipped)`, exit 1. This kills "baseline status check removed", because with the check removed the mutated run still skips and prints NOT HELD.
   - Put (a) and (b) in a new test rather than in `test_mixed_run_reports_every_probe`. That keeps its `TOTAL: 13 probes, ...` line (L130) unchanged.
   - A new FILES entry doesn't change the other tests' counts. Each probe runs only its own `test_file`. `test_holds_exits_0` asserts `1 failed, 1 passed` for tests/test_mod.py only [repo: tests/test_probe_guardrails.py L21-29, L85-87].

### B. Part 2: the fixed `code check: n/a` text
9. For every entry without `module`, `_run_probe` prints `code check: n/a (no module; tests run <file> by path via tests/conftest.py REPO, conftest L7)`. That text is true only for RI-013. On the fixture it printed "tests run pkg/mod.py by path via tests/conftest.py REPO", which is false [repo: scripts/probe_guardrails.py L191-195; logs/audit/2026-11-18-074.md L83].
10. A1's proposed fix: a per-entry key (for example `no_module_reason`), required when `module` is absent [repo: logs/audit/2026-11-18-074.md L83]. Consequences:
    - (i) `REQUIRED` cannot simply gain the key, because module entries don't need it. The check is "`module` or the reason key", and an entry with neither gives `ERROR (probe entry lacks module or no_module_reason)`.
    - (ii) The fixture helper `_probe` (L51-56) has no `module`, so all 13 mixed-run probes would become entry errors unless `_probe` gets a default reason. A fixture test should print a known reason verbatim, and one entry with neither key should give the ERROR.
    - (iii) `test_shipped_probes_well_formed` should require one of the two keys on every shipped entry.
    - (iv) The test `assert "code check: n/a" in _line(out, "b")` (L119) has to follow the new wording.
    [repo: tests/test_probe_guardrails.py L51-56, L119, L203-217]
11. A reason is true only if it names how the test reaches the worktree's file. Reasons read from the tests (I1 to copy them, or shorten them while keeping the line refs):
    - RI-013 067-1b: tests/test_diff_reports.py runs `REPO / "scripts" / "diff_reports.py"` in a subprocess, with REPO from tests/conftest.py L7 [repo: work/074/01-research.md finding 5].
    - RI-002 046: config/tickers.json is data. `test_ticker_fields_cover_file_and_code` reads it and ccbot/tickers.py as text from `Path(__file__).resolve().parents[1]` [repo: tests/test_missing_inputs.py L254-257].
    - check_pipeline probes (RI-007, 009, 010, 011): `_run` runs `REPO / "scripts" / "check_pipeline.py"` in a subprocess, and `_cp()` imports it after `sys.path.insert(0, REPO/"scripts")` [repo: tests/test_pipeline_check.py L51-54, L862-865].
    - RI-012 059 needs no reason: it has a module (`ccbot.broker.webull_sandbox`, imported by the test at L9) [repo: tests/test_webull_sandbox.py L9].
12. Option, not required: a module check for scripts/check_pipeline.py. `module_file` imports by name from `cwd=wt`, and scripts/ has no `__init__.py` (UNVERIFIED, no Glob run), so `scripts.check_pipeline` would load as a namespace package. That name differs from the `check_pipeline` the tests import, so it would prove less than the reason text. I recommend the reason key.

### C. Part 3: the six new probes (exact strings; `\n` = newline; leading spaces as in the file)
13. Anchor counts, Grep over this working tree: the 6 check_pipeline/webull patterns below give 6 hits in total, 1 each (lines named). The tickers.json two-line anchor gives 1 hit [repo: scripts/check_pipeline.py L215, L224, L311, L519, L539, L551; ccbot/broker/webull_sandbox.py L77; config/tickers.json L3-4].

| # | id (proposed) | file | anchor (count 1) | replacement | test file | target | module / reason | recorded |
|---|---|---|---|---|---|---|---|---|
| N1 | RI-011-052-merge-tree | scripts/check_pipeline.py | `        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None` (8 sp, L519) | `        tree = None` | tests/test_pipeline_check.py | `::test_criss_cross_branch_lists_only_its_own_changes` (L592) | reason: check_pipeline | 2026-11-14: 1 failed, 69 passed |
| N2 | RI-012-059-bare-429 | ccbot/broker/webull_sandbox.py | `    return bool(_HTTP_429.search(low)) or "too many requests" in low or "too_many_requests" in low` (4 sp, L77) | `    return "429" in low or "too many requests" in low or "too_many_requests" in low` | tests/test_webull_sandbox.py | `::test_429_inside_other_text_is_not_retried` (L242) | module `ccbot.broker.webull_sandbox` | 2026-11-14: 1 failed, 292 passed (whole suite, not this file) |
| N3 | RI-002-046-tickers-key | config/tickers.json | `"F": {\n    "asset_type": "stock",` | `"F": {\n    "foo_date": null,\n    "asset_type": "stock",` | tests/test_missing_inputs.py | `::test_ticker_fields_cover_file_and_code` (L251) | reason: data file | 2026-11-07..11: 1 failed, 22 passed |
| N4 | RI-009-037-id-clash | scripts/check_pipeline.py | `                clashes.append(item)` (16 sp, L551) | `                pass` | tests/test_pipeline_check.py | `::test_same_id_on_main_and_open_branch_is_a_clash` (L270) | reason: check_pipeline | none |
| N5 | RI-007-064-work-py | scripts/check_pipeline.py | `    return f.startswith(paths) or WORK_CODE.fullmatch(f) is not None` (4 sp, L311) | `    return f.startswith(paths)` | tests/test_pipeline_check.py | `::test_research_only_work_py_is_research_code` (L1063) | reason: check_pipeline | none |
| N6 | RI-010-049-rules-branch | scripts/check_pipeline.py | `        rules = changed(*RULE_PATHS)` (8 sp, L539) | `        rules = []` | tests/test_pipeline_check.py | `::test_rules_branch_is_reported` (L470) | reason: check_pipeline | none |

Why each mutation hits its RI's failure mode (all from reading the code; UNVERIFIED until I2 runs them):
14. **N1 (RI-011).** With `tree = None`, `changed()` falls back to `git diff HEAD...ref` (L522-525). That is the "HEAD...ref only" mutation the RI-011 text names. The test asserts `origin/next: items 041;` and `RULES BRANCH: none` (L623-624), and the single-base diff credits PR #15's 040 and `.claude/rule.md` to the branch [repo: scripts/check_pipeline.py L517-525; tests/test_pipeline_check.py L592-626; logs/recurring-issues.md RI-011 L132].
15. **N2 (RI-012).** This restores the pre-059 form named in 059's request (`return "429" in low or ...`). The test's first case has `http_status=500`, so the status branch returns False before any text match (L69-73) and that case stays green. The second case, `RuntimeError("Msg: order 7a4291c failed")`, has no status attribute. It reaches the text match, `"429" in low` is True, `_call` retries via `retry_sleep` (L172-175), and `assert waits == []` (L253) fails [repo: work/059/request.md L11; ccbot/broker/webull_sandbox.py L64-77, L163-176; tests/test_webull_sandbox.py L242-253]. The SDK is lazy-loaded (`load_sdk`) and the tests use `FakeSDK`, so the file should not skip for lack of the SDK [repo: ccbot/broker/webull_sandbox.py L38-44; tests/test_webull_sandbox.py L24-25]. The recorded "292 passed" is a whole-suite count. The `recorded` text should say so, or hold the per-file count I2 measures.
16. **N3 (RI-002).** This is the RI-002 text's probe (`"foo_date": null` added to F). `foo_date` is not in TICKER_FIELDS, so `(in_file | in_code) - set(TICKER_NOTES) <= set(TICKER_FIELDS)` fails [repo: tests/test_missing_inputs.py L251-260; logs/recurring-issues.md RI-002 2026-11-07]. Other tests in the file that load tickers.json may also fail. The counts will differ from "1 failed, 22 passed" because the file has grown (`test_drop_each_input` is parametrized over MISSING_POLICY, L238).
17. **N4 (RI-009).** Clashes are never recorded, so the assert `ID CLASH: 050 (origin/pr5)` (L278) fails [repo: scripts/check_pipeline.py L542-551; tests/test_pipeline_check.py L270-280]. Alternative: target the merge-base test `all(... cat-file -e ... != 0 for b in bases)` (L549). That is a finer mutation, but it needs a test that fails when a shared item is reported (L280 already asserts `040 (origin/fix)` is not a clash).
18. **N5 (RI-007).** `_is_code` is the single place the HEAD path and the branch path send their files through. The branch path builds `unit` with WORK_CODE (L565) and then filters it through `_is_code` again in `_research_code` (L319). Dropping the WORK_CODE term means 160's `diag.py` is no longer code, so `160: SKIPPED (... RESEARCH ONLY: changes work/160/diag.py` (L1071) and `RESEARCH CODE: 160` (L1074) are not printed [repo: scripts/check_pipeline.py L308-319, L565; tests/test_pipeline_check.py L1063-1075]. `test_is_code_examples` (L1044-1049) and the branch test (L1127-1133) should fail too. That matches the RI-007 064 GUARDED condition ("RESEARCH ONLY item with 01 plus work/<ID>/diag.py in one commit gives RESEARCH CODE: <ID>") [repo: logs/recurring-issues.md RI-007 2026-11-15].
19. **N6 (RI-010).** 049's guardrail is the `RULES BRANCH:` line, which reports a branch that changes the rules a new item is built under (048's cause). With `rules = []`, the line stays `none` and the assert at L486 fails [repo: scripts/check_pipeline.py L214-215, L539, L910; tests/test_pipeline_check.py L470-487; logs/recurring-issues.md RI-010 L119, L123].
    - Second 049 guardrail, if R2/R3 want it too: `LOG_TIME_EXCEPT`. A widened set is caught by `test_log_time_exception_is_named_and_closed` (L504, `== {"048"}`), but that test only pins a constant.
    - The RI-010 probe A1 recorded (`--log I2 999 "x"` -> refused, exit 2) is a CLI probe. Its anchor-shaped stand-in would mutate the `--log` refusal and target `test_malformed_log_line_names_expected_format` (L563-566). I did not look up that code path.
20. "Anchor-shaped first" (request point 3): all six above are single-file text edits with an existing named target. The 074 brief listed RI-007 and RI-010 as not anchor-shaped because their recorded probes were fixture commits or CLI runs. The fixture tests 064 and 049 added since then make anchor probes possible for both [repo: work/074/01-research.md section C].

### D. Traps for the new entries
21. **A non-.py target file has no compile check.** `_run_probe` compiles only `.py` files (L207-211). A broken JSON replacement in N3 would make `json.loads` raise `JSONDecodeError` (a ValueError) [https://docs.python.org/3/library/json.html]. Raised in the test body, that is a call-phase failure, written as `<failure>`, not `<error>` [https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html]. So the target "fails" for the wrong reason and prints HOLDS. Proposal: parse `.json` mutations with `json.loads` before pytest, with `ERROR (mutation is not valid JSON: ...)`, plus a fixture case. The N3 replacement as written is valid JSON (a key added before an existing key in the same object; read, not run).
22. **Skips in the real targets.** All four check_pipeline targets carry `skipif(shutil.which("git") is None)` / `NO_GIT` [repo: tests/test_pipeline_check.py L48, L269, L469, L591, L1062]. They can't skip during a probe run, because the script itself needs git (exit 2 otherwise). Part 1's tests keep it that way: a skip is never HOLDS.
23. **Baseline must be fully green.** `_baseline` marks every probe on a test file ERROR if any test in that file fails or errors at the ref (L178-181). Four probes share tests/test_pipeline_check.py, so one red test there turns all four into ERROR. A1 reports main green (342 passed, 1 skipped) [repo: scripts/probe_guardrails.py L178-181; logs/audit/2026-11-19.md L33]. Whether the file passes inside a detached worktree of origin/main is UNVERIFIED (some tests run check_pipeline against REPO).
24. **Anchors on main and on today's branch.** The daily run is `--ref origin/main`, so the anchors must be on main. The lines come from items 052, 059, 062, 064 and 037, which are all merged per recurring-issues.md, but I read them only on this branch [repo: logs/recurring-issues.md RI-007, RI-009, RI-011, RI-012]. There is a second exposure: 076, 077 and 079 change scripts/check_pipeline.py before 078 is built (brief.md L3). 077 point 2 (`BRANCH FAIL:` for open branches) is likely to edit `open_branches`, next to N1, N4 and N6 [repo: work/077/request.md L10]. `test_shipped_probes_well_formed` checks anchors against the working tree, so I2 must re-Grep N1-N6 on top of 077/079. If an anchor moves on the branch but not on main, the probe must still match main, and the well-formed test will show the difference.
25. **`test_shipped_probes_well_formed` hard-codes the list.** It asserts `len(pg.PROBES) == 3` and the exact list of 3 targets (L205-217), so it must be updated to 9 [repo: tests/test_probe_guardrails.py L203-217].

## Numbers used (show the math)
- Probe count after 078: 3 existing + 6 new (N1-N6) = 9. Distinct test files: test_realtest, test_diff_reports, test_pipeline_check, test_webull_sandbox, test_missing_inputs = 5 baselines.
- Pytest runs per daily audit: 5 baselines + 9 mutated runs = 14.
- Runtime: the 074 output measured 104.5-127.7 s for 3 probes [repo: logs/audit/2026-11-18-074.md L43; logs/audit/2026-11-19.md L47]. test_pipeline_check.py took 7.77 s for 52 tests at item 062 [repo: work/062/05-build-report.md L56]. Today's size and time are UNVERIFIED. With 4 mutated runs plus 1 baseline, at about 5 times a run of unknown length, the added time is UNVERIFIED: I2 to measure and record.
- Anchor counts: 1 each for N1-N6 (finding 13).

## Fit for a ~$3k account
- Tooling only. No change to trade decisions, sizing, cash buffer or reject codes. Nothing touches a broker.
- N3 protects the RI-002 rule that an unlisted tickers.json fact can't slip in as a value, which feeds EARNINGS_UNKNOWN / DIVIDEND_UNKNOWN for a small account's earnings and early-assignment risk. N2 protects the sandbox broker from retrying a real server error as if it were a rate limit [repo: logs/recurring-issues.md RI-002, RI-012].
- Cost: a few more minutes of local CPU per daily audit at most (UNVERIFIED). No fees.

## Open questions
1. RI-010: should 078 ship N6 only (RULES BRANCH), or also a LOG_TIME_EXCEPT probe, or a `--log` refusal anchor probe (finding 19)? The request names only "049".
2. RI-009: should N4 be the coarse `clashes.append` -> `pass`, or the finer merge-base mutation, which may need a new assertion (finding 17)?
3. Should 078 add the JSON-validity check for non-.py probes (finding 21)? It is needed for N3 to be trustworthy, but it is outside the request's 3 points.
4. `recorded` values: keep the historical RI-text counts (N2's is a whole-suite count), or record the per-file counts I2 measures on main?
5. Key name and wording for the per-entry reason (`no_module_reason` was A1's example). It is R3's call.
6. I2 must confirm every anchor on origin/main and on top of 077/079 before 05 (finding 24).
