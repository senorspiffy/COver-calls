# 04 Build plan - 112
Fit verdict: FIT WITH CHANGES

Recurring issues checked (item 013): RI-001 (ESCALATED), RI-014 (OPEN), and the GUARDED entries RI-002, RI-007, RI-009, RI-010, RI-012, RI-015 (see "Recurring issues" below).

## Fit check
- Account and strategy: this is test tooling only, with no trading rule, ticker screen or $3k account effect. Nothing in 001 changes, and no rule text the person follows changes.
- Existing code: every change is in tests/test_pipeline_check.py. No change to scripts/, ccbot/, config/, templates/ or .claude/. The item is built on 113's committed I2 work (8529267), which touched the same file and is clean now. That removes 03 step 9's rebase condition.
- Line numbers: 03 cites lines from before 113. They have moved: the S7 site is now in `incomplete` at the `if "I2" in bad and int(item_dir.name) >= TIMED_FROM \` line, the id term is in `log_fields_ok`, and SITE_ROWS is near the end of the test file. The plan names functions and text only. The replaced text `>= TIMED_FROM \` followed by a newline occurs exactly once (pre-check B: "site count 1").
- Conflict: none. The existing `test_from_site_census` (function-name check) and `test_from_site_census_catches_new_site` stay. The census's EQUIVALENT filter and its assert change together (03 step 5).

## Pre-check (03 step 0, RI-001): run before this verdict
The orchestrator ran it on 2026-11-26 at 8529267 from /home/claude/fix with PYTHONDONTWRITEBYTECODE=1, a fresh PYTHONPYCACHEPREFIX and `python3 -B`, exit 0. Script: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i1-112-r1-oqa2zfb6/precheck_112.py. Full output: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i1-112-r1-oqa2zfb6/precheck-out.txt (57 lines). Results:
- A (Layer 1, `log_fields_ok` timed=True / timed=False): 075 T F/F, U F/F, M F/F, O T/T. 076 and 089 T T/T, U T/T, M F/F, O F/F. 090 U False/True, and T True/True. All 13 planned rows match 03 Self-check rows 1-2. The 090 timed field T is equal for both flags, which confirms 03's correction: the control must use U.
- B (Layer 2, real script vs edited copy, `_timed_repo(..., TIMED_RULES, item, i2)`):
  - 089-untimed (`- 1`): same output. INCOMPLETE none and RULE NOT SEEN none in both.
  - 089-malformed (`- 1`): same output. Both scripts print `INCOMPLETE: 089 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>")` and RULE NOT SEEN none.
  - 090-control (`+ 1`): different output, in exactly 2 lines. Real: `INCOMPLETE: none`, `RULE NOT SEEN: 090 (05 added in <sha7> without TIMED_FROM (090): judged by untimed I2 form; item 084)`. Copy: `INCOMPLETE: 090 (... I2 wants "... with its ` in <s>s` time>")`, `RULE NOT SEEN: none`.
  - 089-identity (unedited copy, added by I1): same output. So running from a copy, from another path and a second later does not change the output.
  - This matches 03 Self-check rows 3-4.
- C (child collection, 03 step 2 command with PYTEST_PLUGINS also removed): exit 0, wall 1.56 s, 587 `::` lines (587 unique), 0 not starting `tests/`. The first line is `tests/test_pipeline_check.py::test_build_without_research_is_skipped`, the anchor is present, and 33 kills (23 bracketed) give 0 unresolved. Pytest's own `in 0.80s` is about half the wall time, which confirms 03's correction of the 4.11 s "bound" (row 63).
- D (`*_FROM` Load Names outside a Compare, UNTRACKED_FROM excluded, plus `*_FROM` attributes): `{}`.
- E: pytest 9.1.1.

Each traced value in 03 holds when run. No expected text in steps 2/4 needs correcting. The changes below add strength. None of them fixes a wrong result.

## Extra research (with sources)
1. PYTEST_PLUGINS gets through 03's child env. The pytest docs describe `PYTEST_PLUGINS` as "a comma-separated list of Python modules that are imported and registered as plugins during startup". They list `PYTEST_DISABLE_PLUGIN_AUTOLOAD` separately, as the switch that stops plugins from loading automatically, "instead of requiring you to manually specify each plugin" (https://docs.pytest.org/en/9.0.x/how-to/plugins.html). So disabling autoload does not stop an explicitly named PYTEST_PLUGINS module. A plugin that changes collection, such as one that deselects or renames items, would reach the child. Change C3 removes the variable too. The pre-check ran this way: exit 0, 587 ids.
2. The control has to prove the copy's own output. 03's 090-control asserts only on the real output and on `copy != real`. If the copy failed for an unrelated reason (a crash, empty stdout, a path effect), that row would still pass. Pre-check B shows the exact copy lines, so change C1 pins them. Change C2 adds the unedited-copy row (089-identity, measured same). It separates "the harness changes output" from "the mutant is equivalent".
3. Measured cost: the child adds 1.56 s wall (pre-check C) on top of a 2-file suite. 109/05 measured that suite at about 125.83 s, so the child adds about 1.2% (1.56 / 125.83 = 0.0124). This is the I1 measurement. I2 still records the in-suite `--durations` numbers (03 step 8), because the time inside pytest can differ.

## Files to create/change
1. `tests/test_pipeline_check.py`, the only file:
   - New helpers next to SITE_ROWS:
     - `_pins(text)`: anchored `re.fullmatch(r"EQUIVALENT \(pinned by ([^()]+)\): .+", text)`. Returns the list of ids split on `", "`, or None.
     - `_kill_ids()`: every non-EQUIVALENT kill in SITE_ROWS plus the `_pins` ids of the EQUIVALENT row.
     - `_unresolved(kills, collected)`: returns, sorted, each `k` with `"tests/" + k` not in `collected`. Exact set membership, never a split or a substring (RI-012).
     - `_collected_ids()`: the child collection. Command: `[sys.executable, "-B", "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", f"--rootdir={REPO}", "tests/test_pipeline_check.py", "tests/test_real_data_field.py"]`, cwd=REPO. Env: os.environ minus PYTEST_ADDOPTS, PYTHONSAFEPATH and **PYTEST_PLUGINS** (C3), plus PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, with the bytecode variables inherited (03 row 76). Also capture_output, text, encoding utf-8, errors="replace", timeout=300. It asserts `returncode == 0`, with stdout + stderr as the message. It returns `{l.strip() for l in stdout.splitlines() if l.strip().startswith("tests/") and "::" in l}` (C4).
     - `_from_uses_outside_compare(source)`: as in 03 step 6.
   - New tests:
     - `test_from_site_census_unresolved_kinds` (03 step 1): fixed set with negative cases (i)-(iii), plus `_pins("EQUIVALENT: x") is None`.
     - `test_from_site_census_kill_ids` (03 step 2): first the self-anchor `"tests/test_pipeline_check.py::test_from_site_census" in ids` (message: the first 5 lines of stdout), then `_unresolved(_kill_ids(), ids) == []`.
     - `test_timed_flag_ignored_below_timed_from` (03 step 3): 13 rows, ids `<item>-<shape>` over 075/076/089 x T/U/M/O, plus `090-untimed`. It asserts `cp.TIMED_FROM == 90` and `(a == b) is same`. For 090-untimed it also asserts `(a, b) == (False, True)`.
     - `test_s7_from1_same_output`, `@NO_GIT` (03 step 4, with C1/C2): 4 rows, `item, i2, mutant, same`:
       - `089-untimed` (089, U, `"- 1"`, True)
       - `089-malformed` (089, M, `"- 1"`, True)
       - `090-control` (090, U, `"+ 1"`, False)
       - `089-identity` (089, U, None, True), new (C2): the copy is the unedited source.
       
       The body follows 03 step 4. The copy goes in `tmp_path/"copy"/"check_pipeline.py"` and runs with `[sys.executable, "-B", copy, "--untracked-from", sha, "--today", SUITE_DAY]`, cwd `tmp_path/"repo"`. It asserts `src.count(">= TIMED_FROM \\\n") == 1` and `(copy_out == real) is same`.
       
       Required asserts on the real output:
       - 089-untimed and 089-identity: `INCOMPLETE: none` and `RULE NOT SEEN: none` (C5).
       - 089-malformed: INCOMPLETE starts `INCOMPLETE: 089 (` and contains `log line for I2 does not match its format (item 045)`.
       - 090-control: `INCOMPLETE: none` and RULE NOT SEEN starts `RULE NOT SEEN: 090 (` and contains `without TIMED_FROM (090)`.
       
       **C1:** for 090-control, also on the copy: INCOMPLETE starts `INCOMPLETE: 090 (` and contains `log line for I2 does not match its format (item 045)`, and `RULE NOT SEEN: none`.
     - `test_from_names_only_in_compares` and `test_from_names_only_in_compares_catches_alias` (03 step 6, synthetic source and Counter as written there).
   - Edits:
     - SITE_ROWS[6][4] becomes `EQUIVALENT (pinned by test_pipeline_check.py::test_timed_flag_ignored_below_timed_from[089-untimed], test_pipeline_check.py::test_s7_from1_same_output[089-untimed]): at 089 "I2" in bad means an I2 line fails LOG_FORMAT, so all(timed=False) is False and the gate is never entered`.
     - In `test_from_site_census` the skip becomes `kill.startswith("EQUIVALENT")`, and the last EQUIVALENT assert becomes `[k for k in kills if k.startswith("EQUIVALENT")] == [SITE_ROWS[6][4]] and _pins(SITE_ROWS[6][4])`, with 2 ids (03 step 5).
     - A comment above SITE_ROWS names the alias rule (`test_from_names_only_in_compares`).

Files planned: 1.

## Tests and checks
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).

- I2 pastes the orchestrator's pre-check output (the file above) into 05 under "Pre-check". I2 does not have to re-run it.
- Run: `python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py` with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX (item 107). `-rs` must show 0 skips for the 4 `test_s7_from1_same_output` ids. Then the full suite.
- Mutants, as in 03 step 7. Each runs in a scratch worktree with the bytecode guards and is restored afterwards. 05 pastes each summary line and the failing ids.
  - K1: `_unresolved` compares function names only. Kills `test_from_site_census_unresolved_kinds`.
  - K2: child `-q` becomes `-qq`. Kills `test_from_site_census_kill_ids` at the anchor. With C4, `file: count` lines have no `::`, so the set is empty.
  - K3: S2 FROM-1 kill `[TIMED-FROM-1]` becomes `[TIMED-FROM-l]`. Kills `test_from_site_census_kill_ids`, naming that id.
  - K4: the `and int(item) >= TIMED_FROM` term is removed from the timed branch of `log_fields_ok`. Kills `test_timed_flag_ignored_below_timed_from[076-U]` and `[089-U]`, and `test_s7_from1_same_output[089-untimed]`. Row ids follow the `<item>-<shape>` naming. 03's "076-untimed/089-untimed" for Layer 1 means shape U.
  - K5: the Layer 1 test is renamed and the pin is left. Kills `test_from_site_census_kill_ids`.
  - K6: `_c = SUITE_FROM` is added as the first body statement of `late_log_lines`, after its docstring. Kills `test_from_names_only_in_compares`, while `test_from_site_census` passes.
  - K7: S7 FROM-1 (`>= TIMED_FROM - 1 \` at the gate) gives 0 failures (documented equivalent).
  - K8 (new, C1): in the test's copy step, write an empty file instead of the mutated source. That kills `test_s7_from1_same_output[090-control]` on the C1 copy asserts, and `[089-identity]`. It proves that a copy which does not run cannot pass the control.
- Measure (03 step 8): the before and after two-file summary lines, `--durations=0` for `test_from_site_census_kill_ids` and the 4 Layer 2 rows, and the collected-id delta. The delta is now 13 + 4 + 1 + 1 + 2 = **21** (03's 20 plus the 089-identity row). The expected count is 587 → 608 ids at the build commit, if nothing else is added.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 0 pre-check (a) 089 fixture U/M, (b) child run, (c) pytest version | Done before FIT by the orchestrator, 2026-11-26 at 8529267 ("Pre-check" above). I2 pastes it into 05 |
| Step 1 `_pins`, `_kill_ids`, `_unresolved`, negative kinds (i)-(iii) | Files: helpers and `test_from_site_census_unresolved_kinds`. Mutant K1 |
| Step 2 child collection: env, `-B`, `-q`, rootdir, `returncode == 0`, `::` lines, self-anchor, exact membership | Files: `_collected_ids` (with C3 PYTEST_PLUGINS removed, C4 `tests/` prefix) and `test_from_site_census_kill_ids`. K2, K3 |
| Step 3 Layer 1, 13 rows, 090 control on U | Files: `test_timed_flag_ignored_below_timed_from`. Pre-check A. K4 |
| Step 4 Layer 2, `@NO_GIT`, `count == 1`, copy outside the fixture, real-output asserts | Files: `test_s7_from1_same_output` with C1 (copy asserts), C2 (089-identity), C5 (089-untimed RULE NOT SEEN none). Pre-check B. K4, K8 |
| Step 5 EQUIVALENT `(pinned by ...)` text and census assert | Files: SITE_ROWS[6][4] and `test_from_site_census` edits. K5 |
| Step 6 `_from_uses_outside_compare` and the 2 tests | Files: helper and 2 tests. Pre-check D `{}`. K6 |
| Step 7 mutants K1-K7 | Tests and checks: K1-K7, plus K8 |
| Step 8 measurements and delta 20 | Tests and checks: "Measure". Delta corrected to 21 (C2). Child wall time measured at 1.56 s (pre-check C) |
| Step 9 rebase on 113, re-read the sites | 113 is committed at 8529267 and this item builds on it. Sites named by function and text; `count == 1` asserted in the test |
| Missing inputs: child exit code not 0 | `_collected_ids` assert `returncode == 0` |
| Missing inputs: listing with no node ids / `-qq` | Self-anchor in `test_from_site_census_kill_ids`. K2 |
| Missing inputs: child time > 300 s | `timeout=300` → TimeoutExpired, so the test errors |
| Missing inputs: kill or pin id not collected | `_unresolved`, tested by unresolved_kinds and kill_ids. K3, K5 |
| Missing inputs: EQUIVALENT with no `(pinned by ...)` | `_pins` None → census assert fails. Tested in unresolved_kinds |
| Missing inputs: git binary absent | `@NO_GIT` skip, shown in `-rs`. 05 must show 0 skips. Layer 1 runs without git |
| Missing inputs: replaced text found 0 or 2+ times | `assert src.count(...) == 1` in Layer 2 |
| Missing inputs: wall time and pytest version unmeasured | Measured by the pre-check (1.56 s, pytest 9.1.1). I2 adds the in-suite durations |
| Missing inputs: screen tickers | DROPPED: no ticker screen in this item (03 says n/a) |
| Fixed claims: 4.11 s bound / 3% (01, 02) | Replaced by the measurement: 1.56 s, about 1.2% of 125.83 s (Extra research 3) |
| Fixed claim: STRIP copy would drop the bytecode guards | Files: `_collected_ids` env keeps the bytecode variables |
| Fixed claim: 090 control uses U, not T | Step 3 row `090-untimed`. Pre-check A: 090 T True/True, U False/True |
| Fixed claim: 02 Grep list | DROPPED: about past logs only, no code effect |
| Removed claims (exit 2, option (d), deselected listing) | DROPPED: removed in 03, nothing to build |

## Guardrail tests
- Feasibility: 33 kills (23 bracketed + 10 plain) resolve in 587 collected ids (pre-check C, 2026-11-26, 8529267) → `test_from_site_census_kill_ids`. 3 bad of 5 → `test_from_site_census_unresolved_kinds`.
- Feasibility: 17 comparison sites, 1 S7 site text (pre-check B count 1) → existing `test_from_site_census` plus the `count == 1` assert in `test_s7_from1_same_output`.
- Feasibility: 0 `*_FROM` uses outside a Compare (pre-check D) → `test_from_names_only_in_compares`. Synthetic: 3 reported of 6 → `_catches_alias`.
- Feasibility: 13 Layer 1 rows (pre-check A) and 4 Layer 2 rows (pre-check B: 3 same, 1 different) → `test_timed_flag_ignored_below_timed_from`, `test_s7_from1_same_output`.
- Missing inputs: child nonzero exit, empty listing and timeout → the asserts in `_collected_ids` and the self-anchor (K2). Missing pin → `_pins` None case. Git absent → `-rs` 0 skips in 05. Site text 0 or 2+ → `count == 1`.

## Recurring issues
- RI-001 (ESCALATED): every new fixture and the child run were run once before FIT (pre-check, cited). Every count above is measured, not asserted.
- RI-014 (OPEN): no clone-depth dependence. Layer 2 uses a fresh `git init`, the child runs no git, and nothing is added to scripts/.
- RI-002: a failed child, an empty listing, a skipped git row, an unrun copy (K8) and a missing pin each fail or show as skipped, never pass.
- RI-007: Scope FULL, test code only.
- RI-009: 113 is committed under the base, so there is no open overlap.
- RI-010: the alias case is checked by a test, not documented.
- RI-012: anchored fullmatch for pins, exact set membership for ids, and prefix checks on `_pick` lines.
- RI-015: the child and the copy run with `-B` and the bytecode variables inherited, and mutants follow item 107.

## Expected result
- The two-file run passes with 21 more collected ids than before (expected 608 if nothing else is added) and 0 skips for the Layer 2 rows.
- The full suite passes.
- K1-K6 and K8 each fail their named tests, and K7 survives with 0 failures.
- The child adds about 1.5 s wall.
- "Done looks like" is met:
  - A misspelled param id fails `test_from_site_census_kill_ids`.
  - S7 FROM-1 has two named pin tests that the census resolves.
  - The alias/attribute case is checked by `test_from_names_only_in_compares`.

Log fields: FIT WITH CHANGES | 1 files planned
