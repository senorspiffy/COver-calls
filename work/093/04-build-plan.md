# 04 Build plan - 093
Fit verdict: FIT WITH CHANGES

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN); GUARDED entries RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-011, RI-012, RI-013. How this plan meets each:
- RI-001: the excuse has a measured real count, not only fixtures. Under the excuse rule, 1 real item has the shape: work/024 (dated 2026-10-31; `Waived: 01 02 03 04 (person, 2026-10-31: ...)`, Scope FULL, no 01-04 files, Glob 2026-11-24). 024 is below LOG_CHECK_FROM, so it never reaches batch_log_items, but the helper is pinned on its real text (T-real). 0 of the 9 items numbered 090-098 have a Waived line (03 Self-check row 5), so no real output changes.
- RI-010: no item that is not waived gets weaker. Only the exact person-dated, all-pre-05, files-absent shape changes. Every other shape keeps the strict entry and has a negative test with a mutation that kills it (N-a to N-j, M1-M9).
- RI-014: the helper reads work/ files only (via `_read`), no git. The `_rule_seen(TIMED_FROM)` gate in `incomplete()` is unchanged.
- RI-002: a missing or unreadable request.md, a missing Scope line and a second Waived line each fall back to the strict reason. Each has an absent-case test (N-g, N-h, N-i, N-j). The excused item is still listed on the LOG BATCH line and is never silently dropped.
- RI-004/RI-005: I re-derived 03's Self-check rows 1-3, 6-14 from the code read below (REQUIRED L373-375, parse_request L545-554, batch_log_items L1353-1356, BATCH_STRICT L428). They hold.
- RI-006: no hand totals here. The file count in the last line counts the Files section.
- RI-007: the excuse needs `(person, YYYY-MM-DD:` at the first parenthesis. classify's SKIPPED for non-person 03 waivers is unchanged.
- RI-008: `re.match` (3.10+), not `prefixmatch` (3.15+). No new syntax. I2 runs `python3.11 -m py_compile` on both files.
- RI-012: anchored `.match` on the text after the step numbers. In-text negatives N-c and N-d have the quoted person form inside other text.
- RI-003, RI-009, RI-011 and RI-013 do not apply: there is no calendar, branch, merge-base or realtest path here.

## Extra research (with sources)
1. Anchoring. `re.match` checks only at the start of the string, and MULTILINE does not change that (`^` with MULTILINE matches after each newline only in `search`). `match` is still the right call for a single line's group 2. Sources: https://docs.python.org/3/library/re.html ("search() vs. match()"), https://docs.python.org/2.3/lib/matching-searching.html (the same rule since 2.x, so it is not version-dependent within >= 3.10).
2. Simpler method, one source for the pattern. `WAIVE_BUILD_BY_PERSON` (L476) is `\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:`, and 03's PERSON_DATED is the same with a leading `\s*`. Build it as `PERSON_DATED = re.compile(r"\s*" + WAIVE_BUILD_BY_PERSON.pattern)`, so the person-with-date shape is written once. The 062 hole (R2 FOR1) is in how `_build_waived` uses that pattern (`.search` on the whole line), not in the pattern itself, so sharing the pattern does not import the hole.
3. Edge cases R3 left untested (code read, check_pipeline.py on daily-fixes/2026-11-24):
   - (a) A missing request.md is listed in 03's Missing inputs but has no fixture. Added as N-h.
   - (b) A missing Scope line defaults to FULL (parse_request L551) but has no fixture. Added as N-i: with no Scope line, a FAST-shaped waiver `01 03` must stay strict.
   - (c) Gap j (only the first Waived line is read) is documented but not pinned. Added as N-j plus mutation M9.
   - (d) Case. parse_request lower-cases `who`, but PERSON_DATED is case-sensitive, so `(Person, 2026-11-20: x)` passes classify and stays strict here. This fails safe. It is consistent with FAST_BY_PERSON and WAIVE_BUILD_BY_PERSON, so it is recorded in the docstring, not changed.
   - (e) Dates are not validated: `\d{4}-\d{2}-\d{2}` accepts 2026-13-45. This is the same as the other two person patterns. Recorded as a known gap and not changed (no item has hit it).
4. Line shift. 092 (built first) changes scripts/check_handoff.py. 094, 095, 097 and 098 later change the same two files as 093. Every anchor below is a function or constant name. The line numbers are today's, for reading only.

## Files to create/change
1. scripts/check_pipeline.py
   - Constants, next to `WAIVE_BUILD_BY_PERSON`:
     - `WAIVED_LINE = re.compile(r"^Waived:\s*([0-9 ,]+)(.*)$", re.M)`
     - `PERSON_DATED = re.compile(r"\s*" + WAIVE_BUILD_BY_PERSON.pattern)`, used only with `.match` on `WAIVED_LINE` group 2. Comment: item 093, RI-012/RI-008.
   - `parse_request`: replace its inline `^Waived:` regex with `WAIVED_LINE.search(text)`. Behaviour is unchanged (the existing parse_request, classify and `_build_waived` tests stay green). `_build_waived` itself is not changed: the 062 hole is a follow-up for A1 to open.
   - New `_person_waived_before_i2(req_text, item_dir)`, defined after `_build_waived`:
     - `scope, _, (waived, _, _) = parse_request(req_text)`, `m = WAIVED_LINE.search(req_text)`, `pre = [s for s in REQUIRED[scope] if s < "05"]`.
     - It returns `pre` only if `m` is found, `PERSON_DATED.match(m.group(2))` matches, `pre` is not empty, `set(pre) <= set(waived)`, and `not any((item_dir / STEPS[s]).exists() for s in pre)`. Otherwise it returns None.
     - Docstring covers: first Waived line only (gap j); the case-sensitive `person` (3d); undated-format dates not validated (3e).
   - `batch_log_items`, at the `if not before:` branch:
     - `text, why = _read(d / "request.md", missing_ok=True)` and `pre = _person_waived_before_i2(text, d) if why is None and text is not None else None`.
     - Reason: `f"no line before I2 ({' '.join(pre)} waived by the person, first I2 round not bounded, item 093)"` if pre, else exactly `"no line before I2"`. Then `continue` as today.
     - The reason must contain no `;` (LOG BATCH joins with "; ").
   - `incomplete()`: no code change. The new reason is not in BATCH_STRICT, and the check is by equality.
   - Docstrings:
     - Module docstring (today L162-165 and L171-175): replace "no waiver excuses it". New text: a person-dated `Waived:` (first line) covering every pre-05 step of the Scope, with those step files absent, is excused (item 093). It is listed as `not computable: <ID>: no line before I2 (<steps> waived by the person, first I2 round not bounded, item 093)` and is not INCOMPLETE. Any other waiver stays strict.
     - `batch_log_items` docstring (L1292-1300): the first I2 round of an excused item has no prev, so nothing in LOG BATCH evaluates it (LOG TIME still applies). Gap j applies.
2. tests/test_pipeline_check.py (next to `test_batch_no_line_before_i2_strict_from_090`, reusing `_batch_item`, `_bl`, `_run`, `_pick`, `STEP_NAMES`, `BATCH_DAY`)
   - Add a local helper `_waived_item(root, item, req, drop=("01","02","03","04"), research=())`. It builds the L4190-4197 shape (I2 10:00, I3 10:05, `full=True`), deletes the `drop` step files, and writes `req` as request.md.
   - Flip `[990]` of `test_batch_no_line_before_i2_strict_from_090` to `INCOMPLETE: none`. Keep its LOG BATCH substring assert, which still holds. Rename the docstring to say 093 excuses the person-dated shape. `[089]` is unchanged.
   - Add the tests listed under Tests and checks.

## Tests and checks
New and changed tests. Item 990 unless noted. An "integration" test runs `_run(... "--today", "2026-11-21")`. For the strict-integration tests, the INCOMPLETE line contains `990 (` and `LOG BATCH not computable: no line before I2 (item 090)`.
- F (pass, parametrized): `test_batch_person_waiver_before_i2_excused[scope]`
  - `scope` is taken from `[s for s in cp.REQUIRED if "05" in cp.REQUIRED[s]]`, so it runs FULL and FAST now, and any new Scope with an I2 step is added automatically.
  - FULL request: `Scope: FULL` + `Waived: 01 02 03 04 (person, 2026-11-20: test)`.
  - FAST request: `Scope: FAST (person, 2026-11-20)` + `Waived: 01 03 (person, 2026-11-20: test)`.
  - Asserts:
    - `INCOMPLETE: none`.
    - LOG BATCH contains `not computable: 990: no line before I2 (<pre> waived by the person, first I2 round not bounded, item 093)`.
    - The exit code equals what the [089] twin gives (I2 records it in 05).
- Unit: `test_person_dated_anchor`. `cp.PERSON_DATED.match` is truthy for `(person, 2026-11-20: x)` and ` (person , 2026-11-20 : x)`. It is None for:
  - `(person: x)`
  - `(I2, 2026-11-20: "(person, 2026-11-19: ok)")`
  - `(person: x "(person, 2026-11-19: ok)")`
  - `(Person, 2026-11-20: x)` (pins 3d as fail-safe)
- Unit: `test_excused_reason_not_strict`.
  - Build the item with `_bl` and take the reason.
  - Assert `reason not in cp.BATCH_STRICT`, `reason.startswith("no line before I2 (")` and `";" not in reason`.
- T-real: `test_person_waiver_helper_on_item_024`.
  - Read the repo's work/024/request.md (path from `Path(__file__).resolve().parents[1]`).
  - Assert `cp._person_waived_before_i2(text, that_dir) == ["01","02","03","04"]`.
  - This is the non-zero real count (1 item, 2026-10-31).
- Strict negatives, integration (each also checks the SKIPPED shown where noted):
  - N-a: `(A1, 2026-11-20: test)` also gives `990: SKIPPED`.
  - N-b: `(person: test)`.
  - N-c: `(I2, 2026-11-20: copied "(person, 2026-11-19: ok)")` also gives SKIPPED.
  - N-d: `(person: x "(person, 2026-11-19: ok)")`.
  - N-e: `Waived: 01 02 04 (person, 2026-11-20: test)` with 03 absent also gives SKIPPED (missing 03 before 05).
  - N-f: person-dated `01 02 03 04`, 01-research.md kept, R1 research line 10:10 after I2 10:00.
- Strict negatives, unit via `_bl` (exactly `[("990", "no line before I2")]`):
  - N-g: request.md written as `b"\xff"`. Also assert `"work/990/request.md"` (rendered) is in `cp._UNREAD`, and clear it first.
  - N-h: request.md deleted.
  - N-i: no Scope line, `Waived: 01 03 (person, 2026-11-20: test)`. FULL default, so 02 and 04 are not waived.
  - N-j: first line `Waived: 01 02 03 04 (person: no date)`, second line `Waived: 01 02 03 04 (person, 2026-11-20: x)`.
- Mutations. I2 runs them on a scratch copy (scratch dir only, never in the repo) and I3 re-runs them. 05 and 06 name the failing test for each:

| Mutation | Change | Killed by |
|---|---|---|
| M1 | helper always returns None | F[FULL], F[FAST], T-real |
| M2 | `PERSON_DATED.match(g2)` replaced by `who == "person" and WAIVE_BUILD_BY_PERSON.search(line)` | N-d |
| M3 | bare `WAIVE_BUILD_BY_PERSON.search(line)` | N-c, N-d |
| M4 | PERSON_DATED = `\s*\(\s*person\b` (date dropped) | N-b, test_person_dated_anchor |
| M5 | subset check dropped | N-e |
| M6 | `pre` always from `REQUIRED["FULL"]` | F[FAST] |
| M7 | file-absent check dropped | N-f |
| M8 | unreadable request.md read as text and excused | N-g |
| M9 | every Waived line read (findall), any person-dated one counts | N-j |

  The `who` check has no mutation of its own: the anchored match implies it (an equivalent mutant, 03 row R1/R2 mutation).
- Commands:
  - `python3 -m pytest -q` (whole suite, time kept in the I2 field).
  - `python3 -m pytest -q tests/test_pipeline_check.py -k "waiv or no_line_before or person_dated or excused"`.
  - `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`.
  - `python3 scripts/check_pipeline.py` on the branch, where `INCOMPLETE:` must not newly name any real item.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: WAIVED_LINE constant, parse_request uses it | Files 1, constants + parse_request |
| Step 1: PERSON_DATED, `.match` on group 2 | Files 1, constants (built from WAIVE_BUILD_BY_PERSON.pattern, Extra research 2); test_person_dated_anchor |
| Step 1: `_build_waived` unchanged, 062 hole is a follow-up | Files 1, parse_request bullet; Expected result follow-up |
| Step 2: helper with (a)-(d), first Waived line only | Files 1, `_person_waived_before_i2`; F, T-real, N-a to N-j |
| Step 3: batch_log_items reads request.md with `_read(missing_ok=True)`, excused reason text, no ";" | Files 1, batch_log_items bullet; test_excused_reason_not_strict, N-g, N-h |
| Step 4: incomplete() unchanged; docstrings L162-175 and L1292-1300; gap j noted | Files 1, incomplete() and docstring bullets |
| Step 5: flip [990]; parametrized pass test over REQUIRED with "05"; FAST request text | Files 2, flip + F |
| Step 6: N-a to N-g | Tests and checks, strict negatives |
| Step 7: M1-M8, I2 runs, I3 re-runs, named failing test | Tests and checks, mutation table (+ M9) |
| Removed claim 1: I3-only bound | DROPPED: UNSUPPORTED order assumption (03 Removed claims 1); recorded in the batch_log_items docstring as "first I2 round not bounded" |
| Missing inputs: request.md missing / unreadable | N-h / N-g |
| Missing inputs: no Waived line | existing `test_batch_*` at L3150-3160 (no Waived line → exact strict reason), unchanged |
| Missing inputs: not person-dated / partial set / file present / second line / no Scope | N-a to N-d / N-e / N-f / N-j / N-i |
| Rule the person follows (001 slack/tolerance/cap) | No change: no strategy rule is touched. The INCOMPLETE rule text appears only in check_pipeline.py docstrings (Grep of .claude/, templates/: no "no line before I2"), updated in the same plan |

## Guardrail tests
- Feasibility: excuse rule → T-real `test_person_waiver_helper_on_item_024` (1 real item, 024, 2026-10-31, returns 01-04); fixture counts F 2 excused of 2, strict 10 of 10 (N-a to N-j); real items 090-098 excused 0 of 9 (03 row 5), checked by the branch `check_pipeline.py` run, where INCOMPLETE is unchanged for real items.
- Feasibility: Scope set → F parametrized over `cp.REQUIRED` entries containing "05" (2 today: FULL, FAST); a new Scope with I2 gets a case automatically.
- Missing inputs: request.md missing → N-h; unreadable → N-g (+ `_UNREAD` entry); Waived line absent → existing L3150-3160 test; person-dated prefix absent → N-a to N-d; Scope line absent → N-i; second Waived line → N-j; pre-05 file present → N-f.

## Expected result
- A person-dated `Waived:` covering every pre-05 step of the Scope, with those files absent, on an item >= 090, behaves as follows:
  - It is listed on LOG BATCH as `not computable: <ID>: no line before I2 (<steps> waived by the person, first I2 round not bounded, item 093)`.
  - It is not INCOMPLETE.
  - The flipped [990] and F[FULL], F[FAST] pass.
- Every other waiver shape keeps `INCOMPLETE: <ID> (LOG BATCH not computable: no line before I2 (item 090))`.
- Each of M1-M9 fails at least one named test.
- No real item's check_pipeline output changes.
- The full suite is green, with only the tests added or flipped here as differences.
- Follow-up for A1 to open (not built here): `_build_waived` (062) accepts `(person: x "(person, <date>: ...)")` because it uses `.search` on the whole line (R2 FOR1). I3 probes it on this branch.

Log fields: FIT WITH CHANGES | 2 files planned
