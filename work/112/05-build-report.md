# 05 Build report - 112
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1

Base: 7b11624 (daily-fixes/2026-11-26, after 113 I2 and 111 I2). Everything I made is inside the scratch dir above: 9 pyc dirs made with the same mkdtemp command (prefix `pyc-`: `pyc-0781oye9` for the unmutated runs, and one per mutant, K1-K8, listed in "Mutants"), and 8 worktrees `wt-K1` ... `wt-K8` made with `git worktree add --detach` at 7b11624. I copied the built tests/test_pipeline_check.py into each worktree and applied one mutant per worktree with `mutate.py` (in the scratch dir). Each mutant ran only in its own worktree. Afterwards I removed all 8 with `git worktree remove --force` (`git worktree list | grep -c i2-112` printed `0`), so there was nothing to restore in place. I ran no `git stash`, and nothing was mutated in /home/claude/fix.

**Two plan problems for I1 (see Deviations 1 and 2). K7 does not give 0 failures. The Layer 1 pin id in SITE_ROWS[6][4] had to be `[089-U]`, not `[089-untimed]`.**

Recurring issues checked (item 013): RI-001 (ESCALATED), RI-014 (OPEN), and the GUARDED entries RI-002, RI-007, RI-009, RI-010, RI-012, RI-015 (see "Recurring issues" at the end).

## Pre-check
I did not re-run it (04 "Tests and checks"). This is the orchestrator's output, pasted from /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i1-112-r1-oqa2zfb6/precheck-out.txt (at 8529267):
```
== A. Layer 1 values: item shape timed=True timed=False
TIMED_FROM 90
L1 075 T False False
L1 075 U False False
L1 075 M False False
L1 075 O True True
L1 076 T True True
L1 076 U True True
L1 076 M False False
L1 076 O False False
L1 089 T True True
L1 089 U True True
L1 089 M False False
L1 089 O False False
L1 090 T True True
L1 090 U False True
L1 090 M False False
L1 090 O False False
== B. Layer 2 differential; site count 1
089-untimed SAME copy exit 0
  real INCOMPLETE: none
  copy INCOMPLETE: none
  real RULE NOT SEEN: none
  copy RULE NOT SEEN: none
089-malformed SAME copy exit 1
  real INCOMPLETE: 089 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>")
  copy INCOMPLETE: 089 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>")
  real RULE NOT SEEN: none
  copy RULE NOT SEEN: none
090-control DIFF copy exit 1
  real INCOMPLETE: none
  copy INCOMPLETE: 090 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` time>")
  real RULE NOT SEEN: 090 (05 added in 2c57725 without TIMED_FROM (090): judged by untimed I2 form; item 084)
  copy RULE NOT SEEN: none
--- real
+++ copy
@@ -10,2 +10,2 @@
-INCOMPLETE: none
-RULE NOT SEEN: 090 (05 added in 2c57725 without TIMED_FROM (090): judged by untimed I2 form; item 084)
+INCOMPLETE: 090 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` time>")
+RULE NOT SEEN: none

089-identity SAME copy exit 0
  real INCOMPLETE: none
  copy INCOMPLETE: none
  real RULE NOT SEEN: none
  copy RULE NOT SEEN: none
== C. child collection
exit 0 | wall 1.56s | :: lines 587 | unique 587
first ['tests/test_pipeline_check.py::test_build_without_research_is_skipped'] | last stdout line ['587 tests collected in 0.80s']
not starting tests/: []
anchor present True
kills 33 bracketed 23 unresolved []
== D. *_FROM uses outside Compare in scripts/check_pipeline.py
outside-compare uses {}
== E. pytest version
pytest 9.1.1
```
`python3 -m pytest --version` at the build printed `pytest 9.1.1`.

## Changes made (file: what changed)
- tests/test_pipeline_check.py (the only file):
  - A comment above SITE_ROWS names `test_from_site_census_kill_ids` and the alias rule `test_from_names_only_in_compares`.
  - SITE_ROWS[6][4] is now `EQUIVALENT (pinned by test_pipeline_check.py::test_timed_flag_ignored_below_timed_from[089-U], test_pipeline_check.py::test_s7_from1_same_output[089-untimed]): at 089 "I2" in bad means ...` (reason text unchanged; see Deviation 2 for `089-U`).
  - `test_from_site_census`: the skip is now `kill.startswith("EQUIVALENT")`. The EQUIVALENT assert is now `startswith("EQUIVALENT")`, followed by `pins = _pins(SITE_ROWS[6][4]); assert pins and len(pins) == 2`.
  - New helpers:
    - `_pins`: anchored `re.fullmatch`.
    - `_kill_ids`: an EQUIVALENT kill with no pin fails an assert. It is never dropped.
    - `_unresolved`: exact set membership.
    - `CENSUS_STRIP` and `_collected_ids`: the child as in 04, with PYTEST_ADDOPTS, PYTHONSAFEPATH and PYTEST_PLUGINS removed, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, `-B`, `timeout=300`, `returncode == 0` asserted, and only `tests/...::` lines kept. It returns `(ids, stdout)` (see Deviation 3).
    - `L1_FIELDS`, `L1_ROWS`, `L1_IDS`, `S7_SITE`, `S7_FMT`.
    - `_from_uses_outside_compare`.
  - New tests:
    - `test_from_site_census_unresolved_kinds`.
    - `test_from_site_census_kill_ids`.
    - `test_timed_flag_ignored_below_timed_from`: 13 rows, `075-T` ... `089-O`, plus `090-untimed`.
    - `test_s7_from1_same_output`: `@NO_GIT`, 4 rows `089-untimed`, `089-malformed`, `090-control` and `089-identity`, with the C1 copy asserts on 090-control and the C5 asserts on 089-untimed and 089-identity.
    - `test_from_names_only_in_compares`.
    - `test_from_names_only_in_compares_catches_alias`.

File counts (from commands):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` printed `0` (new).
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` printed `1` (changed).

## Connectivity check
- [x] Every new function or rule is used:
  - `_pins` is used by `_kill_ids`, `test_from_site_census` and `test_from_site_census_unresolved_kinds`.
  - `_kill_ids`, `_unresolved` and `_collected_ids` are used by `test_from_site_census_kill_ids`. `_unresolved` is also used by `_unresolved_kinds`.
  - `CENSUS_STRIP` is used by `_collected_ids`.
  - `L1_*` are used by both new parametrized tests. `S7_SITE` and `S7_FMT` are used by `test_s7_from1_same_output`.
  - `_from_uses_outside_compare` is used by the 2 new tests.
  - Both pin ids resolve in the child collection (the unmutated two-file run passes `test_from_site_census_kill_ids`, and K5 shows the pin is really checked).
- [x] Every input has a source and every output has a consumer. Inputs are SITE_ROWS, the child's stdout, scripts/check_pipeline.py's source and the `_timed_repo` fixture output. Outputs are test asserts, which pytest reports.
- [x] Every branch ends in a defined result:
  - A child exit that is not 0 fails an assert with stdout and stderr.
  - A listing with no node ids fails at the self-anchor (K2).
  - A timeout raises TimeoutExpired, so the test errors.
  - An EQUIVALENT kill with no pin fails in `_kill_ids` and in `test_from_site_census`.
  - Site text found 0 or 2+ times fails `count == 1` (seen under K7).
  - An empty or crashed copy fails `_pick`'s one-line assert or the `same` assert (K8).
  - Git absent gives a `@NO_GIT` skip, shown by `-rs`. There were 0 skips in this run.
- [x] There are no leftover TODOs or unused files. A grep of the added lines for `TODO` gave no hit. The scratch worktrees were removed.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 lines, all existing. This item does not touch ccbot/. The same pattern on the added lines of the diff (`git diff -U0 tests/test_pipeline_check.py | grep '^+' | grep -nE ...`, plus `: float = ` and `TODO`) gave no hit (grep exit 1). There is no new dataclass, and no new `>`/`<` test on a value that can be NaN. `assert pins and len(pins) == 2` fails on None or empty, so it never passes.
- Feasibility numbers, measured at the build:
  - The child collected 608 ids (the two-file `--collect-only` printed `608 tests collected in 0.79s`). Before the build it was `587 tests collected in 0.85s`, so the delta is 21, as planned.
  - 35 ids resolve (33 kills + 2 pins): `test_from_site_census_kill_ids` passes, and K3 and K5 show that one bad id fails.
  - `_from_uses_outside_compare` on the real script gives `Counter()` (the test passes). The synthetic source gives `{name SUITE_FROM: 2, attr SUITE_FROM: 1}` (the test passes).
  - The S7 site count is 1 (the 4 Layer 2 rows pass).

## Test output (pasted, not summarized)
Two-file run before the build (7b11624, unmutated, `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc-0781oye9 python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py`), last lines:
```
........................................................................ [ 98%]
...........                                                              [100%]
587 passed in 136.84s (0:02:16)
```
Two-file run after the build (same command plus `--durations=0`). It shows no skipped test and no `SKIPPED` line, so the 4 `test_s7_from1_same_output` ids ran. Last lines, and the duration lines for the new subprocess tests:
```
(1407 durations < 0.005s hidden.  Use -vv to show these durations.)
608 passed in 132.25s (0:02:12)
1.75s call     tests/test_pipeline_check.py::test_from_site_census_kill_ids
0.68s call     tests/test_pipeline_check.py::test_s7_from1_same_output[090-control]
0.68s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-untimed]
0.62s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-malformed]
0.61s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-identity]
```
Costs: the child collection adds 1.75 s inside pytest (pre-check wall: 1.56 s), and the 4 Layer 2 rows add 2.59 s. Collected ids went from 587 to 608 (+21).

Full suite (`python3 -m pytest -q` from the repo root), last lines:
```
.......................                                                  [100%]
1102 passed, 1 skipped in 160.01s (0:02:40)
```
Suite: 1102 passed, 1 skipped in 160.01s (0:02:40)

### Mutants
Bytecode guard check for each pyc dir (item 107):
```
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-0781oye9
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-a5dadoi0
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-xb9kam2y
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-wqzz5qn5
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-8ua0h41e
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-clrpa840
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-faojnl5y
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-kp5f8c6l
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-112-r1-kozg0qc1/pyc-kxpbwniv
```
How each mutant ran: in `wt-K<n>` with `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<line n of pycdirs.txt> python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py`. The pyc dirs map K1 to K8 in the order listed after `pyc-0781oye9`. The failing ids come from the failure headers. Full outputs are in `<scratch>/mut-K<n>.txt`.

| Mutant | Change | Summary line | Failing ids | Expected (04) | Result |
|---|---|---|---|---|---|
| K1 | `_unresolved` compares the part before `[` only | `1 failed, 607 passed in 148.31s (0:02:28)` | test_from_site_census_unresolved_kinds (`assert [] == [...]`, "Right contains 3 more items") | kills unresolved_kinds | as expected |
| K2 | child `-q` becomes `-qq` | `1 failed, 607 passed in 140.27s (0:02:20)` | test_from_site_census_kill_ids (`census anchor not collected:` / `tests/test_pipeline_check.py: 569` / `tests/test_real_data_field.py: 39` ... `in set()`) | fails at the anchor | as expected |
| K3 | S2 FROM-1 kill `[TIMED-FROM-1]` becomes `[TIMED-FROM-l]` | `1 failed, 607 passed in 133.98s (0:02:13)` | test_from_site_census_kill_ids (`Left contains one more item: 'test_pipeline_check.py::test_from_cutoff_boundary[TIMED-FROM-l]'`) | kill_ids, naming it | as expected |
| K4 | `and int(item) >= TIMED_FROM` removed from the timed branch of `log_fields_ok` | `13 failed, 595 passed in 133.97s (0:02:13)` | test_i2_summary_line_accepted[411 passed, 1 skipped], test_i2_summary_line_accepted[1 passed], test_i2_tests_field_cutoff, test_batch_untimed_item_is_not_computable, test_suite_line_part_of_field_is_incomplete[S3-tail], test_log_i2_untimed_refused_from_090, test_from_cutoff_boundary[TIMED-FROM-1], test_from_site_census, **test_timed_flag_ignored_below_timed_from[076-U]**, **[089-U]**, **test_s7_from1_same_output[089-untimed]**, test_s7_from1_same_output[089-identity] | 076-U, 089-U, s7[089-untimed] | as expected (the named 3 plus 9 existing tests and 089-identity, whose real output is now `INCOMPLETE: 089`) |
| K5 | `test_timed_flag_ignored_below_timed_from` renamed to `..._x`, pin left | `1 failed, 607 passed in 150.90s (0:02:30)` | test_from_site_census_kill_ids (`Left contains one more item: '...test_timed_flag_ignored_below_timed_from[089-U]'`) | kill_ids | as expected |
| K6 | `_c = SUITE_FROM` is the first statement after `late_log_lines`' docstring | `1 failed, 607 passed in 150.83s (0:02:30)` | test_from_names_only_in_compares (`Counter({('name', 'SUITE_FROM'): 1})`). test_from_site_census passed | names_only fails, census passes | as expected |
| K7 | S7 site `>= TIMED_FROM \` becomes `>= TIMED_FROM - 1 \` | `4 failed, 604 passed in 155.91s (0:02:35)` | test_s7_from1_same_output[089-untimed], [089-malformed], [090-control], [089-identity], all at tests/test_pipeline_check.py:6335 `assert 0 == 1` (`src.count('>= TIMED_FROM \\\n')`) | **0 failures** | **NOT as planned** (Deviation 1). Every other test passed, so 0 behavior tests fail |
| K8 | the test's copy step writes `""` | `4 failed, 604 passed in 155.99s (0:02:35)` | test_s7_from1_same_output[089-untimed], [089-malformed], [089-identity] (`assert ('' == '089: complet...`) at :6341, and **[090-control]** at `_pick`'s one-line assert (:2842, the C1 copy asserts) | 090-control and 089-identity | as expected |

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_pipeline_check.py | 166 +++-, 1 file changed, 163 insertions(+), 3 deletions(-))

## Deviations from plan
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).

1. **K7 cannot give 0 failures with this plan (plan problem, for I1).** 04 and 03 step 7 expect K7 to survive with 0 failures. But `test_s7_from1_same_output` asserts `src.count(">= TIMED_FROM \\\n") == 1` on the live scripts/check_pipeline.py, and K7 rewrites exactly that text. So all 4 Layer 2 rows fail at the count guard (line 6335) before any output is compared. The other 604 tests pass, so no behavior test kills K7. The equivalence itself holds, but the planned expectation "0 failures" is wrong. I did not change the test to make K7 pass. I1 must choose one of these:
   - (a) restate K7's expectation as "only the 4 `test_s7_from1_same_output` rows fail, all at the `count == 1` guard, and 0 behavior tests fail" (this is the measured result);
   - (b) let the Layer 2 test also accept the already-shifted text;
   - (c) run K7 with the Layer 2 test excluded.
   03 says any other result sends the item back, so this needs I1's decision.
2. **The Layer 1 pin id in SITE_ROWS[6][4] is `[089-U]`, not `[089-untimed]` (plan inconsistency).** 04 sets Layer 1 ids to `<item>-<shape>` and says that "03's 076-untimed/089-untimed for Layer 1 means shape U". But its SITE_ROWS[6][4] text, copied from 03, pins `test_timed_flag_ignored_below_timed_from[089-untimed]`, an id that does not exist (only `090-untimed` does). With the text as written, `test_from_site_census_kill_ids` would fail. I applied 04's own mapping and pinned `[089-U]`. The Layer 2 pin stays `test_s7_from1_same_output[089-untimed]`, which exists. I1 should confirm this.
3. `_collected_ids()` returns `(ids, stdout)` instead of just the set. 04 asks for the self-anchor message to show "the first 5 lines of stdout", and under `-qq` (K2) the id set is empty. So the test needs the stdout (the K2 output above shows those lines).
4. The replaced text and the format phrase are module constants (`S7_SITE`, `S7_FMT`) instead of inline literals. They have the same values.
5. The census's last assert is split into 2 asserts: `[...] == [SITE_ROWS[6][4]]`, then `pins and len(pins) == 2`. This implements "and `_pins(...)` ... with 2 ids".
6. `check_pipeline.py` (run during the build) printed lines that are not about this item:
   - `MAIN AHEAD: origin/main has 1 commits not in HEAD` (edfa114, a daily audit commit);
   - `INCOMPLETE: 113 (no log line for I3; 06 Scratch dir ... is not the mkdtemp form ...)`;
   - `UNCOMMITTED STEP: 113 06-verification.md`.
   These come from 113's I3, which is running at the same time, and the branch base. They are not defects of this build. I did not touch them.
7. The full suite ran while the K1-K8 mutant runs were going on in the scratch worktrees, so its time (160.01 s) includes CPU contention.

## Recurring issues
- RI-001 (ESCALATED): every count was measured at the build: 587 → 608 ids, 35 ids resolved, `Counter()`, site count 1, and each mutant summary line. RI-001: holds
- RI-014 (OPEN): no clone-depth dependence. Layer 2 uses `_timed_repo`'s fresh `git init`, the child runs no git, and nothing is added to scripts/. RI-014: holds
- RI-002: a nonzero child exit, an empty listing (K2), a missing pin, an empty copy (K8) and the site text found 0 times (K7) each fail. A git-less run would show as skipped in `-rs` (0 skips here). RI-002: holds
- RI-007: Scope FULL, test code only. RI-007: holds
- RI-009: 113 is committed under the base. The mutants ran only in scratch worktrees, and no `git stash` was run. RI-009: holds
- RI-010: the alias case is checked by tests (K6 kills it). RI-010: holds
- RI-012: anchored fullmatch for pins, exact set membership for ids (K1 shows the name-only form is caught), and prefix checks on `_pick` lines. RI-012: holds
- RI-015: the child and the copy run with `-B` and inherit the bytecode variables. Every mutant ran with both variables set and its own pyc dir (guard lines above). RI-015: holds
