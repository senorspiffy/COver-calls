# 04 Build plan - 078
Fit verdict: FIT WITH CHANGES

Input: work/078/03-handoff.md, Status READY. check_handoff output pasted by the orchestrator (2026-11-19 23:37 UTC, exit 0): `50 rows -> 40 as-is, 6 fixed, 4 removed`, PASS.

Fit check. This is process tooling only. Nothing in ccbot/, config/, data/ or reports/ changes. The probes mutate those files only inside the detached scratch worktree, never in the repo (RI-009). Nothing connects to a brokerage, and no trading, sizing or capital rule changes, so the ~$3k account and the 001 strategy rules are not affected. The item fits the code 074 built: `PROBES`, `REQUIRED`, `_run_probe`, `_probe_all` and `classify` in scripts/probe_guardrails.py, and the fixture helpers `FILES`, `_probe` and `_line` in tests/test_probe_guardrails.py. No other item today edits these two files. 075 edits tests/test_agent_tools.py. 076, 077 and 079 edit scripts/check_pipeline.py and tests/test_pipeline_check.py, which 078 only reads as probe targets. The .claude/agents/a1-auditor.md edit (runtime text) is a RULES BRANCH file, so the person must OK it in PR review.

Changes to 03. Each one is explained under Extra research or in the Rule trace:
- C1 (corrects F4/F38). Current pytest writes a strict-xfail XPASS as a `<failure>` ("[XPASS(strict)]", no `wasxfail`), not as `<skipped>` (Research 1). It can still never give a false HOLDS: in the baseline that test is already "failed", so the baseline-red check gives ERROR. New fixture file `tests/test_xfail.py` and probe s3 pin this. Classify case (ii) stays, but it is described as the `append_failure`-with-`wasxfail` shape, not as "strict XPASS".
- C2. The JSON check catches `ValueError as e` and reads `getattr(e, "msg", str(e))` and `getattr(e, "lineno", "?")`. The docs define `msg`/`lineno` only on `JSONDecodeError`, and a bare ValueError then cannot raise AttributeError out of `main` (Research 2).
- C3. `recorded` for the 6 new entries uses the UTC date of I2's measured run (`<YYYY-MM-DD> (078/05): <n> failed, <m> passed`), not a fixed `2026-11-19`. The hand-off was finished at 23:37 UTC, so I2 may well run on 2026-11-20.
- C4 (RI-014, missed by R3). tests/test_pipeline_check.py `test_repo_pipeline_has_no_skipped_items` runs check_pipeline.py on a `_run_head` worktree of the probe worktree's HEAD. On a shallow clone (before 079) that run can give `UNTRACKED CHANGE ... (git diff-tree failed)` and exit 1. The test_pipeline_check baseline is then red, and all 4 check_pipeline probes (N1, N4, N5, N6) print `ERROR (baseline: exit 1, ...)`. This is loud, never a false HOLDS, so the design stands. I2 pastes `git rev-parse --is-shallow-repository` in 05 before the step 7 runs and runs `git fetch --unshallow` first if it says true. 079 adds the unshallow line to daily-audit.md, which covers A1's daily run.
- C5. 077 point 2 edits `open_branches` next to the N4 anchor (`clashes.append(item)`, 16 spaces; 077/01 F6 cites `skipped.append` a few lines below). The anchor must still count 1 on the 077-built branch. Step 7(a) measures this. If 077 re-indented or duplicated it, I2 stops and reports, and does not loosen the anchor.
- C6. `--ref HEAD` in step 7(b) is the last orchestrator commit. 078's own code is not committed yet, so `HEAD` = the 077-built tree. That is the "branch" state the gate wants for the check_pipeline anchors. 05 says so.
- C7. `_probe`'s default `no_module_reason` is set only when `"module"` is not in its kwargs, so `module` and the default never both appear. `no_module_reason=None` drops the key through the existing `v is not None` filter (r0).
- C8. Targets are written out in full below. 03 step 5 abbreviates them as `::name`.

## Extra research (with sources)
1. **Strict XPASS is a failure, not a skip.** pytest's `pytest_runtest_makereport` (src/_pytest/skipping.py, main) has, for a passing xfail-marked test in the call phase: `if xfailed.strict: rep.outcome = "failed"; rep.longrepr = "[XPASS(strict)] " + xfailed.reason`, else `rep.outcome = "passed"; rep.wasxfail = xfailed.reason`. Source: https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/skipping.py (fetched 2026-11-19). junitxml sends a failed call-phase report to `append_failure`, which writes `<skipped>` "xfail-marked test passes unexpectedly" only when the report has `wasxfail`. Otherwise it writes `<failure>`. Source: https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html (fetched 2026-11-19). The strict branch sets no `wasxfail`, so a strict XPASS is `<failure>`, read as "failed". F4/F38's claim that a strict XPASS is written as `<skipped>` is wrong for current pytest (9.1.1 installed, 076/03 #12). Consequences:
   - A strict-xfail target can never reach the mutated run: its baseline is "failed", so the result is `ERROR (baseline: exit 1, ...)`.
   - A non-strict xfail target that passes reads "passed" (append_pass). If the mutation makes it fail, it becomes xfailed, which is `<skipped type="pytest.xfail">`, so NOT HELD. That is safe.
   - The shipped targets have 0 xfail marks (F4, Grep). So no code change is needed, only the s3 pin (C1).
2. **JSONDecodeError fields.** "Subclass of ValueError with the following additional attributes: msg, doc, pos, lineno, colno". Only `JSONDecodeError` documents these fields. Source: https://docs.python.org/3/library/json.html (fetched 2026-11-19). → C2. j1's `{"a": }` raises JSONDecodeError with msg `Expecting value`, so the pinned text is unchanged.
3. **The webull module check works offline.** ccbot/broker/webull_sandbox.py imports only stdlib and ccbot at module level. The SDK is loaded lazily in `load_sdk()`. So `module_file(wt, "ccbot.broker.webull_sandbox")` can import it without the Webull SDK, and N2 gets a real code check (`code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree`). Read 2026-11-19.
4. **Anchors re-read 2026-11-19 (this tree, before 076/077):**
   - check_pipeline.py `_is_code` return line: 1 hit
   - `tree = merge[0]...` in `open_branches`: 1 hit
   - `rules = changed(*RULE_PATHS)`: 1 hit
   - `clashes.append(item)` at 16 spaces: 1 hit
   - webull_sandbox.py `_rate_limited` return line: 1 hit
   - tickers.json `"F": {` followed by `    "asset_type": "stock",`: 1 hit

   The test helpers that the reason text names exist: tests/test_pipeline_check.py `_run` and `_cp` (`sys.path.insert(0, str(REPO / "scripts"))`), tests/test_diff_reports.py `SCRIPT = REPO / "scripts" / "diff_reports.py"`, tests/conftest.py `REPO = Path(__file__).resolve().parents[1]`. This matches F14-F17.

## Files to create/change
Three files. Edits are given by function or constant name, not by line number. 076 and 077 change check_pipeline.py first, and 079 changes it after.

1. **scripts/probe_guardrails.py**
   - `import json` (stdlib).
   - `PROBES`:
     - Update the comment above it: strings are byte for byte from 074/03 step 1 and 078/03 step 5.
     - RI-013-067-1b gains `"no_module_reason": "tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py"`.
     - The two RI-002 entries keep `module`.
     - Append 6 entries in this order, with every string byte for byte from 03 step 5 (`\n` = newline). Each has `ri`, `file`, `anchor`, `replacement`, `test_file`, `target`, `recorded` (C3), and either `module` or `no_module_reason`:
       - `RI-002-046-tickers-key`: target `tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code`, no_module_reason (tickers.json text from 03 step 5).
       - `RI-007-064-work-py`: target `tests/test_pipeline_check.py::test_research_only_work_py_is_research_code`.
       - `RI-009-037-clash-line`: target `tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash`.
       - `RI-010-049-rules-line`: target `tests/test_pipeline_check.py::test_rules_branch_is_reported`.
       - `RI-011-052-merge-tree`: target `tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes`.
       - `RI-012-059-bare-429`: target `tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried`, `module: "ccbot.broker.webull_sandbox"`, no reason.
     - The 4 check_pipeline entries share the 03 step 5 reason, which names `_run` and `_cp`.
   - `REQUIRED`: unchanged.
   - `_run_probe`:
     - With no `module`, the code text is `f"code check: n/a ({p['no_module_reason']})"`. The fixed `... tests/conftest.py REPO, conftest L7` text is deleted.
     - New check, right after the existing `.py` compile check: `if p["file"].endswith(".json"):` try `json.loads(mutated)`. On `except ValueError as e`, return `(f"ERROR (mutation is not valid JSON: {getattr(e, 'msg', str(e))}, line {getattr(e, 'lineno', '?')})", None, code, False)`. The file is not written and pytest does not run. Use no same-quote f-string (RI-008).
   - `_probe_all`: right after the `missing` (REQUIRED) check, an entry with neither a truthy `module` nor a truthy `no_module_reason` gets `ERROR (probe entry lacks module or no_module_reason)`, `wrote=False`, and code text `""`. It prints `pytest not run` through the existing branch. If both keys are set, `module` wins (the `_run_probe` order is already module-first).
   - `classify`, `read_junit`, `_baseline`: no change. The shipped logic is right (F1, F2). This item adds the tests that kill the surviving mutants.
2. **tests/test_probe_guardrails.py**
   - Module docstring: "(about 2 minutes)" becomes the measured total from 05 (e.g. "about N minutes"). The RI list gains RI-007 and RI-011.
   - `FILES` gains three entries:
     - `"tests/test_skip.py"`, byte for byte from 03 step 1.
     - `"tests/test_xfail.py": 'import pytest\n\n\n@pytest.mark.xfail(strict=True, reason="x")\ndef test_x():\n    pass\n\n\ndef test_ok():\n    assert True\n'` (C1).
     - `"pkg/data.json": '{"a": 1}\n'`.
   - `_probe`: add `"no_module_reason": "fixture: tests/test_mod.py imports pkg/mod.py from the worktree root"` to the defaults only when `"module" not in kw` (C7).
   - `test_mixed_run_reports_every_probe`: one change only. The `code check: n/a` assert on b becomes `code check: n/a (fixture: tests/test_mod.py imports pkg/mod.py` in b's line. The probe list and the `TOTAL: 13 probes, 1 hold, 2 not held, 3 anchor missing, 7 error` line stay unchanged.
   - NEW `@NO_GIT test_skip_entry_and_json_cases(tmp_path, capsys)`: one `main()` call with probes, in this order:
     - s1 = `_probe("s1", replacement='import pytest; pytest.skip("x")')`. Its line contains `0 failed, 1 passed, 0 errors, 1 skipped`, `target tests/test_mod.py::test_f failed: no` and `NOT HELD`.
     - s2 = `_probe("s2", test_file="tests/test_skip.py", target="tests/test_skip.py::test_s")`. Its line contains `ERROR (baseline: target skipped)`.
     - s3 = `_probe("s3", test_file="tests/test_xfail.py", target="tests/test_xfail.py::test_x")`. Its line contains `ERROR (baseline: exit 1, 1 failed, 1 passed, 0 errors, 0 skipped)` (C1: a strict XPASS is a failure).
     - r0 = `_probe("r0", no_module_reason=None)`. Its line contains `ERROR (probe entry lacks module or no_module_reason)` and `pytest not run`.
     - j1 = `_probe("j1", file="pkg/data.json", anchor='"a": 1', replacement='"a": ')`. Its line contains `ERROR (mutation is not valid JSON: Expecting value, line 1)` and `pytest not run`.

     Also asserted: `TOTAL: 5 probes, 0 hold, 1 not held, 0 anchor missing, 4 error`, exit 1, and `_worktrees(root) == 1`.
   - `test_classify_missing_or_bad_junit` (git-free) gets two more asserts:
     - (i) `<testcase classname="tests.test_mod" name="test_f"><skipped type="pytest.skip" message="x"/></testcase>` with `classify(0, ...)` → `"NOT HELD"`.
     - (ii) `<skipped message="xfail-marked test passes unexpectedly"/>` with `classify(1, ...)` → `"NOT HELD"` (the `append_failure` + `wasxfail` shape).
   - `test_shipped_probes_well_formed`:
     - `len == 9`, with 9 unique ids.
     - The targets are the 3 existing ones, then the 6 in the Files 1 order.
     - For every entry: all REQUIRED keys present, anchor count 1 in REPO, `def <name>(` present in its test file, and exactly one of `module` / `no_module_reason` set.
     - For reason entries: `Path(p["file"]).name in p["no_module_reason"]`, and that basename is in the test file's text.
     - For `.json` entries: `json.loads(text.replace(anchor, replacement, 1))` succeeds.
     - Imports `json` and `pathlib.Path`.
3. **.claude/agents/a1-auditor.md**: in the probe_guardrails paragraph, "Takes about 2 minutes (item 074)." becomes "Takes about <measured> minutes (items 074, 078)." The value is taken from I2's `--ref origin/main` TOTAL seconds. This is a RULES BRANCH file and needs the person's OK.

Not changed: README.md (its probe_guardrails line has no count), logs/recurring-issues.md (item 036), scripts/check_pipeline.py and every tests/ file other than test_probe_guardrails.py.

## Tests and checks
- `python3 -m pytest -q tests/test_probe_guardrails.py tests/test_safety.py`: all pass. test_safety's utf-8, f-string and 3.10-compile checks cover both edited files (RI-008).
- Mutants. I2 runs them on a scratch copy under the scratchpad (RI-009) and pastes each run in 05. Each must fail `tests/test_probe_guardrails.py`:
  - A: `classify` `== "failed"` → `!= "passed"`. s1 gives HOLDS, and classify case (i) fails (git-free).
  - B: in `_run_probe`, the `elif status != "passed"` baseline branch is removed. s2 then prints NOT HELD.
  - C: the fixed `conftest REPO` code text is restored. The b assert in the mixed test fails.
  - D: the neither-key check in `_probe_all` is removed. r0 then reaches `p['no_module_reason']` and `main` raises KeyError, or prints no ERROR line. Either way the test fails.
  - E: the `.json` check is removed. j1 runs pytest and prints NOT HELD.
  - F: one shipped reason has its basename removed (e.g. `check_pipeline.py` → `checker`) → `test_shipped_probes_well_formed` fails.
  - G: one shipped entry gets both `module` and `no_module_reason` → `test_shipped_probes_well_formed` fails.
- Step 7 measurement gate (03 step 7, with C3-C6). I2 pastes into 05:
  - (0) `git rev-parse --is-shallow-repository`. If it prints true, I2 runs `git fetch --unshallow` before (b).
  - (a) For each of the 9 anchors, its count in `git show origin/main:<file>` and in the HEAD (077-built) file. All 18 counts must be 1. If one is not, I2 stops and reports.
  - (b) The full output of `python3 scripts/probe_guardrails.py --ref origin/main` and of `--ref HEAD`.
  - (c) `recorded` set from the origin/main per-file counts.
  - (d) The a1-auditor.md and docstring runtime set from (b).
  - (e) The well-formed test passing (it covers the N3 JSON parse).
- Full suite `python3 -m pytest -q` on the built tree: green.
- Greps (I3):
  - `conftest L7` in scripts/probe_guardrails.py: 0 hits.
  - `no_module_reason` in scripts/probe_guardrails.py: ≥ 6 hits (5 entries + code).
  - `about 2 minutes` in .claude/agents/a1-auditor.md and tests/test_probe_guardrails.py: 0 hits.
  - Every `read_text`/`write_text` names utf-8.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 skip fixtures s1, s2; mutants A, B | Files 2 `FILES["tests/test_skip.py"]`, `test_skip_entry_and_json_cases` (s1, s2); mutants A, B |
| Step 2 git-free classify cases (i), (ii) | Files 2 `test_classify_missing_or_bad_junit`. Case (ii) is relabelled (C1, Research 1) |
| Step 3 per-entry `no_module_reason`, neither-key ERROR, module wins, `_probe` default, r0, b's assert, RI-013 reason, names not lines | Files 1 `_run_probe`, `_probe_all`, PROBES RI-013 entry. Files 2 `_probe` (C7), r0, mixed-test b assert. Mutants C, D |
| Step 4 JSON validity check, j1, mutant E | Files 1 `_run_probe` `.json` check with getattr fallback (C2); Files 2 j1; mutant E |
| Step 4 step-1 test TOTAL `4 probes ... 3 error` | Changed to `5 probes, 0 hold, 1 not held, 0 anchor missing, 4 error` by adding s3 (C1) |
| Step 5 six PROBES entries, byte for byte, order, reasons, N2 module | Files 1 PROBES (full targets, C8) |
| Step 6 well-formed test: 9, ids, targets, exactly one key, basename, JSON parses, docstring | Files 2 `test_shipped_probes_well_formed` + docstring; mutants F, G |
| Step 7 (a) anchor counts on origin/main and on the branch, stop if not 1 | Tests and checks, gate (a); C5 (077 near N4); C6 (HEAD = 077 tree) |
| Step 7 (b) both refs `TOTAL: 9 probes, 9 hold, ...`, exit 0, full output | Gate (b), plus the shallow pre-check (0) (C4) |
| Step 7 (c) `recorded` from main counts, keep 3 old | Gate (c), with the run's UTC date (C3) |
| Step 7 (d) a1-auditor.md runtime | Files 3 |
| Step 7 (e) the mutated tickers.json parses | Gate (e) via the well-formed test |
| Step 7 note: 079 keeps 078 green | Expected result, note for 079 |
| Step 8 full suite | Tests and checks |
| Missing inputs table (8 rows) | Guardrail tests, one line per row |
| Decisions OQ1-OQ6 (N6 only, coarse N4, JSON check, measured recorded, key name, step 7) | Files 1 and the gate follow each one. The RI-010 `--log` probe is DROPPED: removed in 03 (F25), out of scope |
| Correction F30/F45 (079 comes after 078) | Fit check; Expected result note for 079 |
| Correction F43 (RI-002 count grew because MISSING_POLICY grew) | Gate (c): `recorded` is measured, never copied |
| Correction F14 (functions, not line numbers, in reasons) | Files 1 reasons name `_run`, `_cp`, `SCRIPT`; the old `conftest L7` text is deleted (grep 0) |
| Removed F8, F41, F47 | Not built (no only-skipped fixture file, no `module_path`, coarse N4) |
| I1 additions C1-C8 | Listed at the top; each maps to a test or a gate line |
| Rule the person follows (001 slack, tolerance, cap) | n/a: no strategy rule changes. The a1-auditor.md text is a process rule and goes to the person in PR review |

## Guardrail tests
- Feasibility: anchor occurs exactly once. 6 of 6 new anchors count 1 (03 F17, Grep 2026-11-19, re-read here). → `test_shipped_probes_well_formed` pins count == 1 for all 9 on every suite run. Gate (a) re-measures on origin/main and HEAD.
- Feasibility: target def exists, 6 of 6 (03 F18-F24). → `test_shipped_probes_well_formed` (`def <name>(`).
- Feasibility: reason basename appears in the reason and in the test file, 5 of 5 reason entries (F40: 58 / 1 / 2 hits). → `test_shipped_probes_well_formed`.
- Feasibility: baseline green. Main was 342 passed, 1 skipped (03 F29, audit 2026-11-19). → gate (b). A red shared file shows as ERROR (fixture f, existing), never HOLDS.
- Missing inputs: neither `module` nor `no_module_reason` → r0 (`ERROR (probe entry lacks module or no_module_reason)`, `pytest not run`).
- Missing inputs: baseline target skipped → s2. Baseline target failed (strict XPASS) → s3. Baseline target not found → existing e.
- Missing inputs: mutated target skipped → s1 (git) and classify case (i) (git-free). The `wasxfail` failure shape → classify case (ii).
- Missing inputs: target not run in the mutated junit → existing classify "other.xml" case.
- Missing inputs: anchor count 0 / 2+ → existing c1, c2.
- Missing inputs: invalid JSON after a `.json` mutation → j1.
- Missing inputs: `recorded` missing → existing b assert `recorded: none`.
- Missing inputs: per-probe runtime → n/a, measured in gate (b). 84 s is a labelled estimate only.

## Expected result
- `python3 -m pytest -q tests/test_probe_guardrails.py`: 10 passed (the 9 from 074 + `test_skip_entry_and_json_cases`). With no git, the 2 git-free tests (`test_classify_missing_or_bad_junit`, `test_shipped_probes_well_formed`) pass and the rest skip.
- Full suite: the 077-built base count + 1 passed, with no new failure or skip. 05 states the base it measured.
- Mutants A-G: each fails at least one named test (05).
- Real runs, `--ref origin/main` and `--ref HEAD`: 9 probe lines, all `HOLDS`, then `TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; <s> s`, exit 0.
  - Baselines for 5 test files.
  - 14 pytest runs (5 baselines + 9 mutated).
  - Estimated total about 3.5-4 min: 104-128 s for the 3 old probes, plus about 84 s for test_pipeline_check ×5, plus the webull and missing_inputs runs. This is an estimate, not a limit; 05 has the measured value.
  - N2's line reads `code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree`. N3, N4-N6, N1 and RI-013 show `code check: n/a (<their reason>)`.
  - Any line that is not HOLDS blocks the merge.
- Git state: one worktree in `git worktree list`, and the repo tree unchanged apart from the 3 planned files.
- Note for 079 (built next): its run of `test_shipped_probes_well_formed` and `tests/test_probe_guardrails.py` must stay green. If 079 moves the N1/N4/N5/N6 anchor lines, it updates the entry in its own item, with a HOLDS shown in its 05.

Recurring issues checked (item 013), against this plan:
- RI-014 (OPEN, the only open entry): C4. A shallow clone can turn test_pipeline_check's baseline red through `test_repo_pipeline_has_no_skipped_items`, not only through `test_untracked_from_is_fixed`. The effect is 4 loud ERRORs, never a false HOLDS. The gate pre-check (0) handles it until 079 lands.
- RI-001 (its header text reads ESCALATED; 03 treats it as GUARDED, so checked either way): the selection rules have dated non-zero counts (6/6 anchors, 6/6 targets, 5/5 reason basenames) and a suite test that pins them.
- RI-002 (request link): skipped, XPASS-shaped and strict-XPASS targets never read as HOLDS (s1, s2, s3, classify i/ii). Invalid JSON never runs pytest (j1). `recorded` is measured.
- RI-004/RI-005: step-1 TOTAL re-derived: s1 NOT HELD + s2, s3, r0, j1 ERROR → 0 + 1 + 0 + 4 = 5. The mixed run is unchanged: 1 + 2 + 3 + 7 = 13.
- RI-006: no hand totals. The log counts come from the scripts.
- RI-007: Scope FULL. I1 wrote no code.
- RI-008: no 3.11+ syntax, no same-quote f-strings; test_safety covers both files.
- RI-009: probes stay in the detached worktree. I2's mutants run in the scratchpad.
- RI-010 (request link): the per-entry reason is pinned structurally by the well-formed test. The a1-auditor.md text goes to the person.
- RI-011, RI-012, RI-013: each has a probe (N1, N2, existing 067-1b with its reason key). Verdicts still come from the exit code and junit only.
- RI-003: n/a (no calendar).

Log fields: FIT WITH CHANGES | 3 files planned
