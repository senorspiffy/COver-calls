# 05 Build report - 093
Base commit: 66e07b921ff61d7f78b446cd686d582be0026486 (branch daily-fixes/2026-11-24, 092 built and I3 PASS on it). `git rev-parse --is-shallow-repository`: false. `check_pipeline.py` after `git fetch origin`: `RULES BRANCH: none`, `IN PR: none`; the one open branch (origin/claude/project-thread-f64g3k) has items none. Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-093-r1-wgz_9ejl (made with `tempfile.mkdtemp(prefix="I2-093-r1-", ...)`).

## Changes made (file: what changed)
- scripts/check_pipeline.py
  - New constants after `WAIVE_BUILD_BY_PERSON`: `WAIVED_LINE = re.compile(r"^Waived:\s*([0-9 ,]+)(.*)$", re.M)` and `PERSON_DATED = re.compile(r"\s*" + WAIVE_BUILD_BY_PERSON.pattern)`, with a comment for item 093, RI-012 and RI-008.
  - `parse_request`: the inline `^Waived:` regex is replaced by `WAIVED_LINE.search(text)`. Behaviour is unchanged.
  - New `_person_waived_before_i2(req_text, item_dir)`, defined after `_build_waived`. It returns the Scope's pre-05 steps only when all of these hold:
    - the first Waived line exists;
    - `PERSON_DATED.match(group 2)` matches;
    - `pre` is not empty;
    - `set(pre) <= set(waived)`;
    - none of those step files exists.
    Otherwise it returns None. The docstring records gap j, the case-sensitive `person` (3d) and the unvalidated date (3e).
  - `batch_log_items`, `if not before:` branch: reads request.md with `_read(..., missing_ok=True)`. If the helper returns steps, the reason is `no line before I2 (<steps> waived by the person, first I2 round not bounded, item 093)`. Otherwise it is exactly `no line before I2`. Then `continue` as before. The docstring now has an item 093 paragraph.
  - Module docstring: "no waiver excuses it" is replaced by the 093 excuse text.
  - `incomplete()` and `_build_waived` are unchanged.
- tests/test_pipeline_check.py
  - `[990]` of `test_batch_no_line_before_i2_strict_from_090` is flipped to `INCOMPLETE: none`, with a new docstring. `[089]` is unchanged, and its LOG BATCH substring assert still holds.
  - New: `WAIVE_IMPL`, `WAIVE_STRICT`, `REQ_FULL_093`, helper `_waived_item`.
  - New tests:
    - `test_batch_person_waiver_before_i2_excused[FULL|FAST]` (F, parametrized over `cp.REQUIRED` entries with "05")
    - `test_person_dated_anchor`
    - `test_excused_reason_not_strict`
    - `test_person_waiver_helper_on_item_024` (T-real)
    - `test_batch_waiver_not_excused_stays_strict[N-a..N-f]` (integration)
    - `test_batch_waiver_missing_inputs_strict[N-g..N-j]` (unit via `_bl`)

File counts (from commands):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 (new)
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 2 (changed)

## Connectivity check
- [x] Every new function and rule is used:
  - `WAIVED_LINE` is used in `parse_request` and `_person_waived_before_i2`.
  - `PERSON_DATED` is used in `_person_waived_before_i2`.
  - The helper is called from `batch_log_items`.
  - The new reason reaches the LOG BATCH line through `not_computable`, which `main()` prints.
- [x] Every input has a source and every output has a consumer:
  - Input: work/<ID>/request.md, read through `_read`. An unreadable file is recorded in `_UNREAD`, which goes to the UNREADABLE line.
  - Output: the reason goes to LOG BATCH's `not computable:` list. `incomplete()` compares it by equality with BATCH_STRICT. The excused text is not in that list, so it is not INCOMPLETE. The strict text is, so it is INCOMPLETE.
- [x] Every branch ends in a defined result. A missing, unreadable or non-person request.md, a partial set, a present file, no Scope line, or a second Waived line each give the strict `no line before I2` reason (N-a to N-j). The excused shape gives the 093 reason and is still listed, never dropped.
- [x] No leftover TODOs or unused files. Grep of .claude/ and templates/ for "waiver excuses": no hits. The only rule text is in check_pipeline.py docstrings, which are updated.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 hits, all existing. ccbot/ is not touched. The same pattern on this build's added lines (`git diff -U0 | grep '^+'`) gives 0 hits. The one near-form, `if why is None and text is not None else None`, falls back to None, which means strict. It fails safe and never passes on absent data.
- Patterns the grep can't see (014): no dataclass fields were added, and no numeric `>`/`<` test was added. The new checks are set inclusion and regex match.
- Feasibility (real numbers):
  - T-real: `_person_waived_before_i2` on work/024 returns `["01","02","03","04"]`. That is 1 real item, dated 2026-10-31, and the test passes.
  - Fixtures: 2 of 2 F cases are excused (FULL, FAST). 10 of 10 strict negatives stay strict (N-a to N-j).
  - Real items: the branch `check_pipeline.py` output is byte-identical to the base script's on this repo (`diff` exit 0, below). The result is `INCOMPLETE: none` in both, so 0 real items change.
- F exit codes (recorded, the plan asks for them):
  - FULL: 990 exit 0, [089] twin exit 0.
  - FAST: 990 exit 0, [089] twin exit 0.
  - The 089 twin also shows the 093 reason text. 089 >= LOG_CHECK_FROM, so this is a text-only change below TIMED_FROM.

## Test output (pasted, not summarized)
`python3 -m pytest -q` (repo root, Python 3.13.18):
```
........................................................................ [ 77%]
........................................................................ [ 86%]
........................................................................ [ 94%]
.............................................                            [100%]
836 passed, 1 skipped in 154.88s (0:02:34)
```
Suite: 836 passed, 1 skipped in 154.88s (0:02:34)

`python3 -m pytest -q tests/test_pipeline_check.py -k "waiv or no_line_before or person_dated or excused"`:
```
..............................                                           [100%]
30 passed, 375 deselected in 3.67s
```
`python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → `py_compile exit 0`.

`python3 scripts/check_pipeline.py` on the branch: exit 0. Key lines:
```
INCOMPLETE: none
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line
SKIPPED: none
```
Base comparison: I ran `git show HEAD:scripts/check_pipeline.py` (base 66e07b9) from the repo root and diffed it with the branch run. `diff cp_base.txt cp_head.txt` printed nothing (`diff exit 0`, base exit 0). The whole output is identical, so no real item's output changes.

Mutation probes. They ran on a tar copy of the working tree in the scratch dir (`.../I2-093-r1-wgz_9ejl/copy`, script `.../I2-093-r1-wgz_9ejl/mut.py`), never in the repo. Each ran `pytest -q tests/test_pipeline_check.py -k "waiv or no_line_before or person_dated or excused or 024"`:
```
M1: 5 failed, 25 passed, 375 deselected in 3.50s | test_batch_no_line_before_i2_strict_from_090[990-INCOMPLETE: none], test_batch_person_waiver_before_i2_excused[FAST], test_batch_person_waiver_before_i2_excused[FULL], test_excused_reason_not_strict, test_person_waiver_helper_on_item_024
M2: 1 failed, 29 passed, 375 deselected in 2.70s | test_batch_waiver_not_excused_stays_strict[N-d]
M3: 2 failed, 28 passed, 375 deselected in 2.91s | test_batch_waiver_not_excused_stays_strict[N-c], test_batch_waiver_not_excused_stays_strict[N-d]
M4: 4 failed, 26 passed, 375 deselected in 3.13s | test_batch_waiver_missing_inputs_strict[N-j], test_batch_waiver_not_excused_stays_strict[N-b], test_batch_waiver_not_excused_stays_strict[N-d], test_person_dated_anchor
M5: 2 failed, 28 passed, 375 deselected in 2.99s | test_batch_waiver_missing_inputs_strict[N-i], test_batch_waiver_not_excused_stays_strict[N-e]
M6: 1 failed, 29 passed, 375 deselected in 2.93s | test_batch_person_waiver_before_i2_excused[FAST]
M7: 1 failed, 29 passed, 375 deselected in 3.20s | test_batch_waiver_not_excused_stays_strict[N-f]
M8: 1 failed, 29 passed, 375 deselected in 3.09s | test_batch_waiver_missing_inputs_strict[N-g]
M9: 1 failed, 29 passed, 375 deselected in 3.05s | test_batch_waiver_missing_inputs_strict[N-j]
restored: 30 passed, 375 deselected in 2.82s
```
Each mutation's change:
- M1: helper `if False:`
- M2: `who == 'person' and WAIVE_BUILD_BY_PERSON.search(whole line)`
- M3: bare `WAIVE_BUILD_BY_PERSON.search(whole line)`
- M4: PERSON_DATED = `\s*\(\s*person\b`
- M5: subset check dropped
- M6: `REQUIRED["FULL"]`
- M7: file-absent check dropped
- M8: request.md read as latin-1, bypassing `_read`
- M9: first person-dated Waived line of any line, steps from that line

Every mutation fails at least one named test, and each test the plan names in the "Killed by" column is among the failures.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: scripts/check_pipeline.py, tests/test_pipeline_check.py; no ccbot/, config/ or data/ file)

## Deviations from plan
- None in code. Notes:
  - The N-g `_UNREAD` assert uses the path as `_read` renders it for this call, which is the absolute `tmp_path/work/990/request.md` because `_bl` passes `root / "work"`. The plan wrote `"work/990/request.md"`.
  - The mutation `-k` adds `or 024` so that T-real is in the probe set (M1 names it).
- Follow-up for A1 to open (not built here, per plan): `_build_waived` (062) still uses `.search` on the whole Waived line, so it accepts `(person: x "(person, <date>: ...)")` (R2 FOR1).

## Recurring issues checked
- RI-001 (ESCALATED): checked. Real count measured: T-real on 024 (1 item), 0 of the real items >= 090 change (identical checker output).
- RI-010 (ESCALATED): checked. Only the exact person-dated, all-pre-05, files-absent shape is excused. Ten strict negatives and nine killed mutations cover the rest. The log line is written with `--log` right after this file.
- RI-014 (OPEN): checked. The helper reads only work/ files through `_read`, with no git. `incomplete()` is unchanged.
- GUARDED, checked:
  - RI-002: absent or unreadable inputs give the strict reason (N-g, N-h, N-i, N-j).
  - RI-004/005: no worked numbers here.
  - RI-006: counts are from commands.
  - RI-007: the person-dated anchor is required.
  - RI-008: `python3.11 -m py_compile` exit 0, and `re.match` is used.
  - RI-009: probes ran in the scratch copy only.
  - RI-012: anchored `.match`, with in-text negatives N-c and N-d.
- Not applicable: RI-003, RI-011, RI-013.

RI-001: ESCALATED (unchanged; 093 measured its excuse rule on 1 real item, 024)
RI-010: ESCALATED (unchanged; near miss closed by 093, not counted)
RI-014: OPEN (unchanged; no git read added)
