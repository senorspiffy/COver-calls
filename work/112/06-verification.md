# 06 Verification - 112
Verdict: FAIL (round 1; earlier rounds: none)
Sent back to: I1
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792

Verified commit: dbefc18 (I2 commit of 112, base 7b11624). HEAD at check time is 917f522, a merge of origin/main that adds logs only (`git diff --stat dbefc18 917f522`: logs/audit/2026-11-26.md, logs/efficiency/2026-11-26.md). `git diff --stat 7b11624 917f522 -- . ':!work' ':!logs'`: tests/test_pipeline_check.py only (163 insertions, 3 deletions). All my runs were in 10 detached worktrees of 917f522 (`git worktree add --detach`) inside my scratch dir: `wt-base` (unmutated two-file run), `wt-K1` ... `wt-K8` (one mutant each, applied by my own `tools/mutate.py`), and `wt-full` (full suite). Each had its own pyc dir made with the same mkdtemp command (prefix `pyc-`), listed with the guard output below. All 10 worktrees were removed afterwards (`git worktree list | grep -c i3-112` printed `0`). I ran no `git stash`, and nothing was edited in /home/claude/fix apart from this file and the commit.

## I1 audit (plan vs research)
- 04 Files and Rule trace cover every 03 map step (0-9), the Missing inputs rows and the Fixed/Removed claims. Each DROPPED row has a reason that holds (no ticker screen; past-log grep list; removed claims).
- Additions C1-C5 each have a stated reason or source: C1/C2 (Extra research 2, pre-check B), C3 (pytest plugin docs, https://docs.pytest.org/en/9.0.x/how-to/plugins.html), C4 (tests/ prefix), C5 (pre-check B). None weakens a 03 check. The delta 20 → 21 follows from C2.
- No 001 rule, ccbot/, config/ or scripts/ change, which matches the request (EFFICIENCY, test tooling only).
- **Problem P1 (plan, for I1): K7's expected result is unreachable under the plan's own test.** 03 step 7 says "K7 must show 0 failures. Any other result sends the item back", and 04 ("Tests and checks" K7, "Expected result") carries "K7 survives with 0 failures". But 03 step 4 / 04's `test_s7_from1_same_output` asserts `src.count(">= TIMED_FROM \\\n") == 1` on the live scripts/check_pipeline.py, and K7 rewrites exactly that text in the live file. So all 4 Layer 2 rows must fail at that guard before any output is compared. I re-ran K7: `4 failed, 604 passed`, all 4 at tests/test_pipeline_check.py:6335 `assert 0 == 1` (below). The equivalence itself is not contradicted (no behaviour test fails), but the plan's stated result is wrong, and 03 sends any other result back. It also touches the census wording: SITE_ROWS[6][4] calls S7 FROM-1 `EQUIVALENT` (no test kills it), while under K7 four tests now fail. I1 has to choose and write down the K7 expectation (05 Deviation 1 lists (a) restate as "only the 4 Layer 2 rows fail, all at the count guard, 0 behaviour tests fail"; (b) let Layer 2 accept the already-shifted text; (c) run K7 with Layer 2 excluded), and say whether the EQUIVALENT row text needs to mention the guard. This is a plan decision; I2 rightly did not change the test.
- **Problem P2 (plan, for I1): 04's SITE_ROWS[6][4] text pins an id the plan never creates.** 04 sets Layer 1 ids to `<item>-<shape>` (13 rows, `075-T` ... `089-O`, plus `090-untimed`) and itself notes that "03's 076-untimed/089-untimed for Layer 1 means shape U", but its SITE_ROWS[6][4] text (copied from 03 step 5) pins `test_timed_flag_ignored_below_timed_from[089-untimed]`. Built word for word, `test_from_site_census_kill_ids` would fail. I2 pinned `[089-U]`, which is the correct id under 04's own mapping: it resolves in my base run (608 passed), and K5 shows it is really checked (`Left contains one more item: '...test_timed_flag_ignored_below_timed_from[089-U]'`). I agree with I2's choice; I1 should write `[089-U]` into the r2 plan (SITE_ROWS text, and K4's Layer 1 names `076-U`/`089-U`) so the build matches the plan text.

## I2 audit (build vs plan)
Line by line, `git diff 7b11624 dbefc18 -- tests/test_pipeline_check.py`, against 04 Files 1:
- Comment above SITE_ROWS names `test_from_site_census_kill_ids` and `test_from_names_only_in_compares` (alias rule): present.
- SITE_ROWS[6][4]: `EQUIVALENT (pinned by test_pipeline_check.py::test_timed_flag_ignored_below_timed_from[089-U], test_pipeline_check.py::test_s7_from1_same_output[089-untimed]): ` + the unchanged reason text. Differs from 04 only by `[089-U]` (P2).
- `test_from_site_census`: skip is `kill.startswith("EQUIVALENT")`; EQUIVALENT assert uses `startswith("EQUIVALENT")`, then `pins = _pins(...)`, `assert pins and len(pins) == 2` (05 Deviation 5: one assert split into two, same meaning; accepted).
- `_pins`: `re.fullmatch(r"EQUIVALENT \(pinned by ([^()]+)\): .+", text)`, split on `", "`, else None: matches 04.
- `_kill_ids`: non-EQUIVALENT kills plus pins; an unpinned EQUIVALENT asserts (stricter than 04, never looser): accepted.
- `_unresolved`: `sorted(k for k in kills if "tests/" + k not in collected)`, exact membership: matches 04.
- `_collected_ids`: command, cwd, `CENSUS_STRIP = (PYTEST_ADDOPTS, PYTHONSAFEPATH, PYTEST_PLUGINS)` (C3), PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, bytecode variables inherited, capture_output/text/utf-8/errors="replace"/timeout=300, `returncode == 0` with stdout+stderr, ids = stripped lines starting `tests/` with `::` (C4): matches 04. Returns `(ids, stdout)` so the anchor message can show 5 stdout lines (05 Deviation 3; needed by 04's own message rule; accepted).
- `test_from_site_census_unresolved_kinds`: 03 step 1 set, (i)-(iii) bad + 2 good, `_pins("EQUIVALENT: x") is None`: matches.
- `test_from_site_census_kill_ids`: self-anchor with first 5 stdout lines, then `_unresolved(_kill_ids(), ids) == []`: matches.
- `test_timed_flag_ignored_below_timed_from`: 13 rows, ids `<item>-<shape>` + `090-untimed`, `cp.TIMED_FROM == 90`, `(a == b) is same`, `(a, b) == (False, True)` for the control: matches.
- `test_s7_from1_same_output`: `@NO_GIT`, 4 rows with 04's ids and values, `_timed_repo`, `count == 1`, copy in `tmp_path/"copy"`, run with `-B`, cwd `tmp_path/"repo"`, `(copy_out == real) is same`, real-output asserts per row, C1 copy asserts on 090-control, C5 RULE NOT SEEN none on 089-untimed/089-identity: matches. `S7_SITE`/`S7_FMT` constants hold the same values as 04's literals (05 Deviation 4; accepted).
- `_from_uses_outside_compare` and its 2 tests: same code, message and synthetic source/Counter as 03 step 6.
- File count: 1 changed, 0 new (my `git diff --stat` above), as planned (Files planned: 1).
- Connectivity, re-done by Grep on the diff: `_pins` (in `_kill_ids`, `test_from_site_census`, `_unresolved_kinds`), `_kill_ids`/`_collected_ids` (kill_ids test), `_unresolved` (2 tests), `CENSUS_STRIP` (`_collected_ids`), `L1_FIELDS`/`L1_ROWS`/`L1_IDS` (Layer 1; `L1_FIELDS` also Layer 2), `S7_SITE`/`S7_FMT` (Layer 2), `_from_uses_outside_compare` (2 tests). Every new name is used.
- 05's grep reasons re-checked: the missing-data pattern on ccbot/ gives 38 lines (all existing, ccbot/ not touched); on the added diff lines (plus `: float = ` and `TODO`) grep exit 1 (no hit). Data-hole edges: n/a (no data window in this item).
- RI-012 / item 059: classification by text here is `_pins` (anchored fullmatch, negative `"EQUIVALENT: x"`), id membership (exact; negatives (ii) `test_from_cutoff_boundary` which is a prefix inside the collected `...[TIMED-FROM]`, and (iii) an added bracket), and `_pick` prefix checks. K1 (name-only compare) fails the negative test. Met.
- Item 062 (simulator pickers): n/a, no simulator. 001 rule text: no rule the person follows changes.
- 05 Deviations 6-7 (other items' check_pipeline lines; suite time under contention): noted, not defects.

## Tests re-run (output)
`python3 scripts/check_handoff.py 112` (in /home/claude/fix, exit 0):
```
sources count (unique URLs in 01-research.md): 10
fact-check rows: 78
totals line: 78 rows -> 69 as-is, 6 fixed, 3 removed
PASS
```
Bytecode guard, one line per pyc dir (`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc dir> python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'`, first line of each output file), item 107:
```
base True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-askrrpjg
K1   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-4dvdt8_g
K2   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-nfc0_hws
K3   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-2tvmw33c
K4   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-zixowvad
K5   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-ea17xlqg
K6   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-rov4qm9k
K7   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-sgkar1oj
K8   True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-5uacqcvr
full True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-112-r1-5ja97792/pyc-9_h9l_v3
```
Two-file run, unmutated (`wt-base`, `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc> python3 -B -m pytest -q -p no:cacheprovider -rs --durations=0 tests/test_pipeline_check.py tests/test_real_data_field.py`): no SKIPPED line, so the 4 Layer 2 rows ran.
```
1.82s call     tests/test_pipeline_check.py::test_from_site_census_kill_ids
0.80s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-untimed]
0.78s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-identity]
0.78s call     tests/test_pipeline_check.py::test_s7_from1_same_output[089-malformed]
0.77s call     tests/test_pipeline_check.py::test_s7_from1_same_output[090-control]
608 passed in 173.16s (0:02:53)
```
608 ids = 05's 608 (587 + 21, as 04 expects). Run times are longer than 05's because 3 mutant runs and the full suite ran in parallel on 4 CPUs.

Full suite (`wt-full`, `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc> python3 -m pytest -q -rs`):
```
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1102 passed, 1 skipped in 301.00s (0:05:00)
```
Same counts as 05 (`1102 passed, 1 skipped`). The one skip is exchange_calendars; `test_every_py_compiles_on_oldest_python` did not skip (python3.11 is on PATH at /usr/bin/python3.11; python3.10 is not) and passed.

Mutants (my own `tools/mutate.py`, one per worktree, same two-file command as the base run):

| Mutant | Change | Summary line | Failing ids (failure headers) | 04 expects | Result |
|---|---|---|---|---|---|
| K1 | `_unresolved` compares the part before `[` on both sides | `1 failed, 607 passed in 173.14s` | test_from_site_census_unresolved_kinds (`Right contains 3 more items`) | unresolved_kinds | as 04, same as 05 |
| K2 | child `-q` → `-qq` | `1 failed, 607 passed in 173.08s` | test_from_site_census_kill_ids (`census anchor not collected:`) | fails at anchor | as 04, same as 05 |
| K3 | `[TIMED-FROM-1]` → `[TIMED-FROM-l]` in SITE_ROWS | `1 failed, 607 passed in 169.14s` | test_from_site_census_kill_ids (`Left contains one more item: '...test_from_cutoff_boundary[TIMED-FROM-l]'`) | kill_ids naming it | as 04, same as 05 |
| K4 | `and int(item) >= TIMED_FROM` removed in `log_fields_ok` | `13 failed, 595 passed in 169.46s` | test_i2_summary_line_accepted[411 passed, 1 skipped], [1 passed], test_i2_tests_field_cutoff, test_batch_untimed_item_is_not_computable, test_suite_line_part_of_field_is_incomplete[S3-tail], test_log_i2_untimed_refused_from_090, test_from_cutoff_boundary[TIMED-FROM-1], test_from_site_census, test_timed_flag_ignored_below_timed_from[076-U], [089-U], test_s7_from1_same_output[089-untimed], [089-identity] | 076-U, 089-U, s7[089-untimed] | as 04, same 12 ids as 05 |
| K5 | Layer 1 test renamed `_x`, pin left | `1 failed, 607 passed in 169.75s` | test_from_site_census_kill_ids (`Left contains one more item: '...test_timed_flag_ignored_below_timed_from[089-U]'`) | kill_ids | as 04, same as 05 |
| K6 | `_c = SUITE_FROM` first statement of `late_log_lines` | `1 failed, 607 passed in 143.12s` | test_from_names_only_in_compares (`Counter({('name', 'SUITE_FROM'): 1})`); test_from_site_census passed | names_only fails, census passes | as 04, same as 05 |
| K7 | S7 site `>= TIMED_FROM \` → `>= TIMED_FROM - 1 \` | `4 failed, 604 passed in 143.22s` | test_s7_from1_same_output[089-untimed], [089-malformed], [090-control], [089-identity], all at tests/test_pipeline_check.py:6335 `assert 0 == 1` | **0 failures** | **not as 04/03** (P1); same as 05 |
| K8 | copy step writes `""` | `4 failed, 604 passed in 143.23s` | test_s7_from1_same_output[089-untimed], [089-malformed], [089-identity] at :6341; [090-control] at `_pick` :2842 (via :6346, the C1 copy asserts) | 090-control and 089-identity | as 04, same as 05 |

Full outputs: `out-<K>.txt` in my scratch dir.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 7b11624 917f522 -- . ':!work' ':!logs'`: tests/test_pipeline_check.py | 166, 1 file changed, 163 insertions(+), 3 deletions(-); no TRIGGER file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-007, RI-009, RI-010, RI-012, RI-015 (what I checked for each, below)
- RI-001 (ESCALATED): every count in 05 re-measured (608 ids, 35 ids resolved via K3/K5, `Counter()`, site count 1, every mutant line). The K7 expectation in 03/04 is the one number that was never computed before FIT (pre-check B ran the copy, not K7 on the live file); that is P1. Near miss of RI-001's kind (plan expectation not computed), caught at I2/I3 before merge.
- RI-014 (OPEN): no clone-depth dependence; Layer 2 uses `_timed_repo`'s fresh `git init`, the child runs no git, nothing in scripts/ changes.
- RI-002: nonzero child exit, empty listing (K2), unpinned EQUIVALENT, empty copy (K8) and site text found 0 times (K7) each fail; git absent would show as a skip in `-rs` (0 here).
- RI-007: Scope FULL, test code only, 01-05 present before this 06.
- RI-009: no open overlap; 113 is under the base; no `git stash` run; worktrees removed.
- RI-010: the alias case is a test (K6 kills it), not only a note.
- RI-012: anchored fullmatch, exact membership, negatives with the pattern inside other text (see I2 audit). Met.
- RI-015: every run set `PYTHONDONTWRITEBYTECODE=1` and its own `PYTHONPYCACHEPREFIX` (guard lines above); the child and the copy run with `-B` and inherit both.

## Pipeline line (step 2)
check_pipeline line: `112: I3 FAIL (FULL; sent back to I1, needs a later PASS round in 06 (item 071))`
Run in /home/claude/fix (HEAD 917f522) after this 06 and the `--log` line `00:34 | I3 | 112 | FAIL | sent to audit: no` were written; exit 1 with `I3 FAIL: 112`, which is the expected state in a FAIL round.

## Sent back / sent to Audit
Sent back to: I1 (round 1). Sent to Audit: no (no 07 in a FAIL round).
For I1 (r2 of 04):
1. P1: restate K7's expected result (and 03 step 7's "0 failures, any other result sends back") so it matches what the plan's own `count == 1` guard must do under K7, or change the Layer 2 design (05 Deviation 1 options (a)-(c)); say whether SITE_ROWS[6][4]'s EQUIVALENT text needs to name the guard. Measured: `4 failed, 604 passed`, all at the count guard; 0 behaviour tests fail.
2. P2: change the SITE_ROWS[6][4] Layer 1 pin in the plan to `test_timed_flag_ignored_below_timed_from[089-U]` (I2's built text, which I confirm resolves and is checked by K5), and K4's Layer 1 names to `076-U`/`089-U`.
Nothing for I2: the build matches 04 apart from these two plan defects; if I1's r2 keeps option (a) and `[089-U]`, the code needs no change.
