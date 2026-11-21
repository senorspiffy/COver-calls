# 05 Build report - 078
Built on `daily-fixes/2026-11-19` at 62f0cc0 (077 I3 PASS round 2; 075-077 built). During the build the orchestrator committed 6a2ca0c "Item 077: A1 result PASS". It adds only logs/audit/2026-11-19-077.md and work/077/07-audit-task.md: `git diff --stat 62f0cc0 6a2ca0c -- ccbot/ config/ scripts/ tests/ | wc -l` → `0`. So every code result below is the same at 6a2ca0c. Not committed (the orchestrator commits).

## Changes made (file: what changed)
File counts (commands, run after the build, A1's 077 files already committed and excluded by `':!work' ':!logs'`):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0` new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `3` changed

```
$ git diff --stat
 .claude/agents/a1-auditor.md   |  2 +-
 scripts/probe_guardrails.py    | 62 ++++++++++++++++++++++++++++++++--
 tests/test_probe_guardrails.py | 75 +++++++++++++++++++++++++++++++++++++-----
 3 files changed, 127 insertions(+), 12 deletions(-)
```

- **scripts/probe_guardrails.py**
  - `import json`.
  - The comment above `PROBES` now says strings are byte for byte from 074/03 step 1 and 078/03 step 5, and that an entry with no `module` names how its test reaches the file in `no_module_reason`.
  - The RI-013-067-1b entry gains its `no_module_reason` (03 step 3 text). The two RI-002 realtest entries keep `module`.
  - 6 new entries, in plan order: RI-002-046-tickers-key, RI-007-064-work-py, RI-009-037-clash-line, RI-010-049-rules-line, RI-011-052-merge-tree, RI-012-059-bare-429. Their anchor, replacement, target and reason strings are byte for byte from 03 step 5.
  - The 4 check_pipeline entries share the module constant `_CP_REASON`, which holds the 03 step 5 reason string (see Deviations).
  - N2 has `module: "ccbot.broker.webull_sandbox"` and no reason.
  - The `recorded` values come from the origin/main run below, in the C3 form `2026-11-20 (078/05): <n> failed, <m> passed`. The 3 old values are kept.
  - `_run_probe`: when there is no module, the code text is `f"code check: n/a ({p['no_module_reason']})"`. The fixed `conftest L7` text is deleted.
  - `_run_probe`: a new `.json` check comes right after the `.py` compile check. It runs `json.loads(mutated)` and catches `ValueError as e`. It reads `msg`/`lineno` with `getattr`, falling back to `str(e)` and `"?"` (C2). It returns `ERROR (mutation is not valid JSON: <msg>, line <lineno>)`, does not write the file and does not run pytest.
  - `_probe_all`: right after the REQUIRED check, an entry with no truthy `module` and no truthy `no_module_reason` gets `ERROR (probe entry lacks module or no_module_reason)`, code `""` and `wrote=False`, so the line prints `pytest not run`. When both keys are set, `module` wins (the existing module-first order in `_run_probe`).
  - `REQUIRED`, `classify`, `read_junit` and `_baseline` are unchanged.
- **tests/test_probe_guardrails.py**
  - The docstring now names items 074 and 078 and RI-007/RI-011, and gives the runtime as "about 4 minutes, 226.7 s on origin/main in 078/05".
  - `import json` and `from pathlib import Path`.
  - `FILES` gains `tests/test_skip.py` (03 step 1, byte for byte), `tests/test_xfail.py` (C1) and `pkg/data.json`.
  - `_probe` adds the default `no_module_reason` only when `"module" not in kw` (C7). `no_module_reason=None` drops the key through the existing filter.
  - The mixed test: b's assert is now `code check: n/a (fixture: tests/test_mod.py imports pkg/mod.py`. The probe list and the TOTAL line are unchanged.
  - New `@NO_GIT test_skip_entry_and_json_cases`: probes s1, s2, s3, r0 and j1, each with the asserts from the plan. It also asserts `TOTAL: 5 probes, 0 hold, 1 not held, 0 anchor missing, 4 error`, exit 1, and 1 worktree.
  - `test_classify_missing_or_bad_junit` gains classify cases (i) skip → NOT HELD and (ii) the `wasxfail` `<skipped>` shape with `classify(1, ...)` → NOT HELD.
  - `test_shipped_probes_well_formed` checks:
    - 9 entries with 9 unique ids;
    - REQUIRED keys, anchor count 1 and the target def, for every entry;
    - exactly one of `module` / `no_module_reason` per entry;
    - for reason entries, the basename is in the reason and in the test file text;
    - for `.json` entries, the mutated text passes `json.loads`;
    - the 9 targets in plan order.
- **.claude/agents/a1-auditor.md** (RULES BRANCH file, needs the person's OK in PR review): "Takes about 2 minutes (item 074)." becomes "Takes about 4 minutes (items 074, 078)." The new value comes from the origin/main TOTAL of 226.7 s.

## Connectivity check
- [x] every new function/rule is used.
  - `json` is used by the `.json` check. `_CP_REASON` is used by 4 entries.
  - The neither-key branch is hit by r0. The `.json` branch is hit by j1 and checked by mutant E.
  - The 6 new PROBES entries are run by `main()` (the real runs below) and checked by `test_shipped_probes_well_formed`.
  - The new FILES entries are used by s2, s3 and j1.
- [x] every input has a source, every output has a consumer.
  - Each entry's `no_module_reason` is printed in its `code check: n/a (...)` field, which A1 pastes into the daily audit (a1-auditor.md L36).
  - The JSON error line and the neither-key line are counted in the TOTAL `error` tally, so the run exits 1.
  - `recorded` is printed on every probe line.
- [x] every branch ends in a defined result.
  - Invalid JSON gives an ERROR line, the file is not written and pytest is not run.
  - An entry missing both keys gives an ERROR line and pytest is not run.
  - A target skipped in the baseline gives `ERROR (baseline: target skipped)` (s2).
  - A strict XPASS in the baseline gives `ERROR (baseline: exit 1, ...)` (s3).
  - A target skipped in the mutated run gives NOT HELD (s1, classify i). The wasxfail shape gives NOT HELD (classify ii).
  - A ValueError with no `msg`/`lineno` falls back to `str(e)` / `?` and never raises out of `main`.
- [x] no leftover TODOs or unused files.
  - The `@REC_*@` and `@RUNTIME@` placeholders I used while measuring are all replaced: `grep -rn "@REC\|@RUNTIME@" scripts/ tests/` → no hits.
  - `git diff --check` is clean. No scratch file is in the repo (mutants ran in a copied folder under the scratchpad).
- Missing-data policy:
  - `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `37`. ccbot/ is not changed (`git diff --stat -- ccbot/` is empty), so none of the 37 hits is new or changed.
  - The same grep over the 2 edited .py files gives 1 hit: `scripts/probe_guardrails.py:81: "anchor": "        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None",`. That is the RI-011 anchor string, quoted as data from check_pipeline.py and never run as logic.
  - No numeric dataclass default was added (`git diff -U0 ... | grep -E '^\+.*(: float = |: int = | > | < )'` → no hits).
  - No `>`/`<` test was added.
  - The neither-key and JSON checks block with a reason. They never default to a pass.
- Feasibility numbers measured (gate a, b): 18 of 18 anchor counts are 1, and both refs hold 9 of 9 (pasted below).

## Test output (pasted, not summarized)
Targeted run (plan line 1), from the repo root:
```
$ python3 -m pytest -q tests/test_probe_guardrails.py tests/test_safety.py
...................                                                      [100%]
19 passed in 7.11s
```
tests/test_probe_guardrails.py has 10 tests (9 from 074 plus `test_skip_entry_and_json_cases`), as the plan expects.

Full suite on the built tree (repo root, Python 3.13.18, pytest 9.1.1):
```
$ python3 -m pytest -q
...
556 passed, 1 skipped in 92.66s (0:01:32)
```
Base measured on a scratch worktree of HEAD under the scratchpad (077-built tree, code identical at 62f0cc0 and 6a2ca0c), removed afterwards: `555 passed, 1 skipped in 100.14s (0:01:40)`. The build adds 1 passed (the new test), with no new failure or skip.

`python3 scripts/check_pipeline.py` on the built tree gives exit 0, with `I3 FAIL: none`, `A1 FAIL: none`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `UNCOMMITTED STEP: none`, `SKIPPED: none` and `RULES BRANCH: none`. (The working-tree change to a1-auditor.md is not committed yet. RULES BRANCH appears after the commit, for the person's review.)

Mutants A-G ran on a copy of the repo (`tar --exclude=.git --exclude=data`) at /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/078-I2/copy, never in the repo (RI-009). The script /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/078-I2/mut.py applies one exact replacement (count asserted 1), runs `pytest -q tests/test_probe_guardrails.py` and restores the file. Output (failure lines, cut to 230 characters by the script):
```
mutant A: exit 1        (classify == "failed" -> != "passed")
  E       AssertionError: assert ('target tests/test_mod.py::test_f failed: no' in 's1 (RI-T): 0 failed, 1 passed, 0 errors, 1 skipped; target tests/test_mod.py::test_f failed: no; HOLDS; recorded: none; code check: n/a (fixture: te
  FAILED tests/test_probe_guardrails.py::test_skip_entry_and_json_cases - Asser...
  FAILED tests/test_probe_guardrails.py::test_classify_missing_or_bad_junit - A...
  2 failed, 8 passed in 6.27s
mutant B: exit 1        (baseline `elif status != "passed"` branch removed)
  E       AssertionError: assert 'ERROR (baseline: target skipped)' in 's2 (RI-T): 0 failed, 1 passed, 0 errors, 1 skipped; target tests/test_skip.py::test_s failed: no; NOT HELD; recorded: none; code check: n/a (fixture: tests/test
  FAILED tests/test_probe_guardrails.py::test_skip_entry_and_json_cases - Asser...
  1 failed, 9 passed in 9.59s
mutant C: exit 1        (fixed "conftest REPO, conftest L7" code text restored)
  E        +  where 'b (RI-T): 0 failed, 2 passed, 0 errors, 0 skipped; target tests/test_mod.py::test_f failed: no; NOT HELD; recorded: none; code check: n/a (no module; tests run pkg/mod.py by path via tests/conftest.py REPO, conf
  FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
  1 failed, 9 passed in 6.27s
mutant D: exit 1        (neither-key check removed)
  FAILED tests/test_probe_guardrails.py::test_skip_entry_and_json_cases - KeyEr...
  1 failed, 9 passed in 6.43s
mutant E: exit 1        (.json check removed)
  E       AssertionError: assert ('ERROR (mutation is not valid JSON: Expecting value, line 1)' in 'j1 (RI-T): 0 failed, 2 passed, 0 errors, 0 skipped; target tests/test_mod.py::test_f failed: no; NOT HELD; recorded: none; code chec
  FAILED tests/test_probe_guardrails.py::test_skip_entry_and_json_cases - Asser...
  1 failed, 9 passed in 6.37s
mutant F: exit 1        (_CP_REASON: both "check_pipeline.py" -> "checker")
  FAILED tests/test_probe_guardrails.py::test_shipped_probes_well_formed - Asse...
  1 failed, 9 passed in 5.88s
mutant G: exit 1        (N2 gets both module and no_module_reason)
  FAILED tests/test_probe_guardrails.py::test_shipped_probes_well_formed - Asse...
  1 failed, 9 passed in 6.97s
```
Note on F. My first F replaced only the first `check_pipeline.py` in `_CP_REASON`. The second one (`REPO/scripts/check_pipeline.py`) stayed, so the basename was still in the reason, and the run gave `mutant F: exit 0, 10 passed in 6.15s`. That was a wrong mutant, not a surviving one: the plan's F removes the basename from the reason. The re-run above replaces both, and the test fails. Each mutant was restored afterwards (`diff -q` copy vs repo → identical).

Greps (I3 list):
- `grep -c "conftest L7" scripts/probe_guardrails.py` → `0`
- `grep -c "no_module_reason" scripts/probe_guardrails.py` → `10` (6 entries: 4 of them through `_CP_REASON`; the constant counts once, RI-013 and N3 are written out. Plus the code and comments.)
- `grep -n "about 2 minutes" .claude/agents/a1-auditor.md tests/test_probe_guardrails.py` → no hits.
- `grep -nE "read_text|write_text" scripts/probe_guardrails.py tests/test_probe_guardrails.py` → no hits. Both files use `read_bytes().decode("utf-8")` / `write_bytes(... .encode("utf-8"))`. test_safety's utf-8, f-string and 3.10-compile checks pass (19 passed above).

### Step 7 measurement gate
(0) Shallow pre-check (C4), before (b): `git rev-parse --is-shallow-repository` → `false`. No unshallow was needed. I ran `git fetch origin` first; origin/main stays `00e5ab65230fa23bce001047b6ec6d47748c8c99` (2026-11-19 23:21:45 +0000, "Daily audit 2026-11-19: report, efficiency list, RI-014, item 079").

(a) Anchor counts. This uses `git show <ref>:<file>` and `str.count`, with the anchor strings exactly as in PROBES, via /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/078-I2/anchors.py. HEAD = 62f0cc0, the 077-built tree (C6: 078's own edits are uncommitted, so HEAD is the "branch" state for the check_pipeline anchors).
```
origin/main ccbot/realtest.py 'if i == 0:': 1
origin/main ccbot/realtest.py 'if _is_gap(td.earnings[i - 1], td.earnings[i]):': 1
origin/main scripts/diff_reports.py 'out.extend(diff_json(a[k], b[k], p))': 1
origin/main config/tickers.json '"F": {': 1
origin/main scripts/check_pipeline.py 'return f.startswith(paths) or WORK_CODE.fullmatch(f) is not ': 1
origin/main scripts/check_pipeline.py 'clashes.append(item)': 1
origin/main scripts/check_pipeline.py 'rules = changed(*RULE_PATHS)': 1
origin/main scripts/check_pipeline.py 'tree = merge[0].split()[0] if conflicts is not None and merg': 1
origin/main ccbot/broker/webull_sandbox.py 'return bool(_HTTP_429.search(low)) or "too many requests" in': 1
HEAD ccbot/realtest.py 'if i == 0:': 1
HEAD ccbot/realtest.py 'if _is_gap(td.earnings[i - 1], td.earnings[i]):': 1
HEAD scripts/diff_reports.py 'out.extend(diff_json(a[k], b[k], p))': 1
HEAD config/tickers.json '"F": {': 1
HEAD scripts/check_pipeline.py 'return f.startswith(paths) or WORK_CODE.fullmatch(f) is not ': 1
HEAD scripts/check_pipeline.py 'clashes.append(item)': 1
HEAD scripts/check_pipeline.py 'rules = changed(*RULE_PATHS)': 1
HEAD scripts/check_pipeline.py 'tree = merge[0].split()[0] if conflicts is not None and merg': 1
HEAD ccbot/broker/webull_sandbox.py 'return bool(_HTTP_429.search(low)) or "too many requests" in': 1
```
18 of 18 are 1. C5: 077's `open_branches` edit left the N4 anchor `                clashes.append(item)` (16 spaces) at count 1, so nothing was loosened. A re-count at 6a2ca0c gives `9 1` (9 anchors, each 1).

(b) Real runs, each one sequential, with nothing else running. UTC 2026-11-20 01:14 → 01:22. Each run's output follows its `exit` line.

`python3 scripts/probe_guardrails.py --ref origin/main` (exit 0). The 6 new entries printed placeholder `recorded` values during this run because those values were taken from it. That field is print-only.
```
$ python3 scripts/probe_guardrails.py --ref origin/main; echo "exit $?"
ref origin/main = 00e5ab65230fa23bce001047b6ec6d47748c8c99
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 34.9 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 100.6 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 33.7 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.1 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 2.4 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.8 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded @REC_N3@; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 3.7 s
    FAILED tests.test_missing_inputs::test_ticker_fields_cover_file_and_code
baseline tests/test_pipeline_check.py: 0 failed, 90 passed, 0 errors, 0 skipped; 17.2 s
RI-007-064-work-py (RI-007): 8 failed, 82 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 34.0 s
    FAILED tests.test_pipeline_check::test_is_code_examples
    FAILED tests.test_pipeline_check::test_py_added_to_completed_item_is_untracked
    FAILED tests.test_pipeline_check::test_research_code_rules
    FAILED tests.test_pipeline_check::test_research_only_branch_nested_py_is_seen
    FAILED tests.test_pipeline_check::test_research_only_branch_work_py_is_branch_skipped
    FAILED tests.test_pipeline_check::test_research_only_work_py_is_research_code
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/061/diag_keep.py-True]
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/160/sub/x.py-True]
RI-009-037-clash-line (RI-009): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 15.9 s
    FAILED tests.test_pipeline_check::test_same_id_on_main_and_open_branch_is_a_clash
RI-010-049-rules-line (RI-010): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 18.0 s
    FAILED tests.test_pipeline_check::test_rules_branch_is_reported
RI-011-052-merge-tree (RI-011): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 15.1 s
    FAILED tests.test_pipeline_check::test_criss_cross_branch_lists_only_its_own_changes
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 1.4 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded @REC_N2@; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 3.0 s
    FAILED tests.test_webull_sandbox::test_429_inside_other_text_is_not_retried
TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; 226.7 s
exit 0
```

`python3 scripts/probe_guardrails.py --ref HEAD` (HEAD = 62f0cc0, exit 0):
```
$ python3 scripts/probe_guardrails.py --ref HEAD; echo "exit $?"
ref HEAD = 62f0cc05fab7a0b464d6e14567f16c6b6784442c
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 32.3 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 92.1 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 32.7 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.4 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 2.8 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.8 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded @REC_N3@; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 3.6 s
    FAILED tests.test_missing_inputs::test_ticker_fields_cover_file_and_code
baseline tests/test_pipeline_check.py: 0 failed, 213 passed, 0 errors, 0 skipped; 30.2 s
RI-007-064-work-py (RI-007): 8 failed, 205 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 56.3 s
    FAILED tests.test_pipeline_check::test_is_code_examples
    FAILED tests.test_pipeline_check::test_py_added_to_completed_item_is_untracked
    FAILED tests.test_pipeline_check::test_research_code_rules
    FAILED tests.test_pipeline_check::test_research_only_branch_nested_py_is_seen
    FAILED tests.test_pipeline_check::test_research_only_branch_work_py_is_branch_skipped
    FAILED tests.test_pipeline_check::test_research_only_work_py_is_research_code
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/061/diag_keep.py-True]
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/160/sub/x.py-True]
RI-009-037-clash-line (RI-009): 1 failed, 212 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 28.0 s
    FAILED tests.test_pipeline_check::test_same_id_on_main_and_open_branch_is_a_clash
RI-010-049-rules-line (RI-010): 1 failed, 212 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 29.6 s
    FAILED tests.test_pipeline_check::test_rules_branch_is_reported
RI-011-052-merge-tree (RI-011): 1 failed, 212 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded @REC_CP@; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 29.3 s
    FAILED tests.test_pipeline_check::test_criss_cross_branch_lists_only_its_own_changes
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 1.7 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded @REC_N2@; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 3.6 s
    FAILED tests.test_webull_sandbox::test_429_inside_other_text_is_not_retried
TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; 278.3 s
exit 0
```
Both runs print `TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error` and exit 0.
- Measured totals: 226.7 s (main) and 278.3 s (HEAD). The plan estimated 3.5-4 min.
- HEAD has a larger test_pipeline_check (213 tests vs 90 on main), so its 5 pipeline-file runs take longer.
- N2 reads `code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree`. N3, N5, N4, N6, N1 and RI-013 show their own reasons.
- There were 5 baselines and 14 pytest runs per ref. No worktree was left: `git worktree list` shows only the repo and another agent's `scratchpad/wt32`, which is not mine.

(c) `recorded` for the 6 new entries, from the origin/main per-entry counts above:
| entry | recorded |
|---|---|
| RI-002-046-tickers-key | `2026-11-20 (078/05): 1 failed, 22 passed` |
| RI-007-064-work-py | `2026-11-20 (078/05): 8 failed, 82 passed` |
| RI-009-037-clash-line | `2026-11-20 (078/05): 1 failed, 89 passed` |
| RI-010-049-rules-line | `2026-11-20 (078/05): 1 failed, 89 passed` |
| RI-011-052-merge-tree | `2026-11-20 (078/05): 1 failed, 89 passed` |
| RI-012-059-bare-429 | `2026-11-20 (078/05): 1 failed, 17 passed` |
The date is the UTC date of the run (C3). The 3 old values are unchanged.

(d) Runtime: the origin/main TOTAL is 226.7 s = 3.78 min, so a1-auditor.md says "about 4 minutes (items 074, 078)". The test docstring says "about 4 minutes, 226.7 s on origin/main in 078/05".

(e) The mutated tickers.json parses: `test_shipped_probes_well_formed` runs `json.loads(text.replace(anchor, replacement, 1))` for N3 and passes (part of the 19 passed and 556 passed above). Mutant G shows the test is live.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/agents/a1-auditor.md, scripts/probe_guardrails.py, tests/test_probe_guardrails.py; none is ccbot/realtest.py or a TRIGGER file/dir)

## Deviations from plan
- The 4 check_pipeline entries hold the shared 03 step 5 reason through the module constant `_CP_REASON` instead of 4 copies of the literal. The string is the same byte for byte, and the plan says they "share" it. The well-formed test checks the value, not the spelling.
- Placeholders were used while measuring: `recorded` and the runtime were filled in after gate (b), as step 7(c)/(d) require. So the origin/main output above shows `@REC_N3@`/`@REC_CP@`/`@REC_N2@` in the print-only recorded field.
- HEAD moved from 62f0cc0 to 6a2ca0c during the build (077 A1 PASS commit, audit files only, 0 code lines). I did not re-run gate (b) at 6a2ca0c because the probed files are identical. The anchors were re-counted (9 of 9 = 1).
- Mutant F first run was set up wrong (one of two basename occurrences replaced) and was redone. Both runs are recorded above.
- No other deviation. README.md, logs/recurring-issues.md, scripts/check_pipeline.py and the other tests/ files are untouched.

## Recurring issues checked (item 013)
Checked against every entry in logs/recurring-issues.md:
- RI-014: OPEN, unchanged by 078. The shallow pre-check gave `false`, so test_pipeline_check's baseline was green on both refs (90 and 213 passed) and N1/N4/N5/N6 hold. On a shallow clone those 4 would print loud ERRORs, never a false HOLDS. 079 carries the fix.
- RI-001: ESCALATED (header), checked. The 078 selection rules have dated, measured counts: 18/18 anchors = 1, 9/9 targets present, 5/5 reasons carry their basename, 9/9 HOLDS on both refs. `test_shipped_probes_well_formed` pins these on every suite run.
- RI-002: GUARDED, guardrail extended (078). A skipped, wasxfail-shaped or strict-XPASS target never reads HOLDS (s1, s2, s3, classify i/ii; mutants A, B). An invalid JSON mutation never runs pytest (j1, mutant E). The tickers.json probe N3 holds on main: 1 failed, 22 passed.
- RI-003: n/a (no calendar).
- RI-004/RI-005: TOTAL lines re-derived. New test: 0 + 1 + 0 + 4 = 5. Mixed test unchanged: 1 + 2 + 3 + 7 = 13. Real runs: 9 hold of 9.
- RI-006: every count above was pasted from a command (file counts, pytest, probes). None was typed by hand.
- RI-007: GUARDED, probe added (N5 `RI-007-064-work-py` HOLDS on main: 8 failed, 82 passed).
- RI-008: no 3.11+ syntax and no same-quote f-string. test_safety passes on both edited files.
- RI-009: GUARDED, probe added (N4 HOLDS on main: 1 failed, 89 passed). Mutants ran in a copied folder under the scratchpad. The base suite ran in a scratch `git worktree`, which was removed. The probes use their own detached worktree.
- RI-010: GUARDED, probe added (N6 HOLDS on main: 1 failed, 89 passed). The a1-auditor.md runtime text is a RULES BRANCH change for the person. My --log line is written with `check_pipeline.py --log`.
- RI-011: GUARDED, probe added (N1 HOLDS on main: 1 failed, 89 passed).
- RI-012: GUARDED, probe added (N2 HOLDS on main: 1 failed, 17 passed, with a real module check). Verdicts still come from the exit code and junit only.
- RI-013: GUARDED, unchanged. 067-1b still HOLDS on main (1 failed, 16 passed) and now prints its own `no_module_reason`.

Guardrail status lines for A1 to copy on main (item 036):
- RI-002: probe set extended (078); GUARDED, unchanged; N3 tickers-key holds on origin/main 00e5ab6 (1 failed, 22 passed).
- RI-007: probe added (078); GUARDED, unchanged; N5 holds on origin/main (8 failed, 82 passed).
- RI-009: probe added (078); GUARDED, unchanged; N4 holds on origin/main (1 failed, 89 passed).
- RI-010: probe added (078); GUARDED, unchanged; N6 holds on origin/main (1 failed, 89 passed).
- RI-011: probe added (078); GUARDED, unchanged; N1 holds on origin/main (1 failed, 89 passed).
- RI-012: probe added (078); GUARDED, unchanged; N2 holds on origin/main (1 failed, 17 passed).
- RI-014: OPEN, unchanged (079).
