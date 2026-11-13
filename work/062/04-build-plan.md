# 04 Build plan - 062
Fit verdict: FIT WITH CHANGES

Changes from 03 (simplifications, no rule dropped):
- (a) Do not re-implement the waiver parse. Split `read_request(path)` (L150–159) into `parse_request(text)` plus a one-line `read_request(path)` wrapper, so the branch side can pass `git show` text and `_build_waived` reuses the same steps/who parse.
- (b) Both HEAD checks share one walk. `_walk(cutoff)` returns `(units, None)` or `(None, (text, failed))`. Because 062 reuses 053's error result, it adds no second error path and no second exit-1 source for a bad cutoff.
- (c) One pure function, `_research_code(files, request_text_of)`, serves HEAD and branches. It is tested with plain lists and no git.
- (d) Edge case R3 missed: `Waived: 04 05 06 (I2, ...)` on a RESEARCH ONLY item already makes `classify` return SKIPPED, because 06 is in PERSON_ONLY (L100, L168–170). Fixture (2b) must therefore assert that the RESEARCH text is present, not just that a `BRANCH SKIPPED: 160` line exists.
- (e) Edge case: on HEAD, a flagged ID whose `work/<ID>/request.md` is gone from the working tree is never printed by the main loop (L456 iterates only dirs with request.md). Print it on its own `<ID>: SKIPPED (...)` line after the loop.

Recurring issues checked (I1): RI-001 ESCALATED (Feasibility: HEAD 0 flags is pinned by the real-repo test; branch 1 flag is a run-time count that I2 pastes in 05; each fixture has one expected result). RI-007 ESCALATED (this item). RI-011 OPEN (the branch side uses `changed()` from merge-tree, not `HEAD...ref`, except the existing fallback). RI-012 OPEN (items come from paths only; negative waiver test (2b) puts "person" inside another who's text). RI-002 GUARDED (Missing inputs rows each map to a test or a named result below). RI-010 GUARDED (I1 log line is written by the orchestrator with `--log`). RI-008 GUARDED (no 3.12-only syntax; test_safety compiles). RI-003/004/005/006/009 are not affected.

## Extra research (with sources)
Line numbers confirmed against the real code on this branch:
- `scripts/check_pipeline.py`: REQUIRED L96–98; PERSON_ONLY L100; CODE_PATHS L120; UNTRACKED_FROM L122; STEP_FILE L123–124; read_request L150–159 (Waived regex L154, who L155); classify L162–194 (need L171); `open_branches` L295–363 (merge-tree L310, `changed()` L318–322 with the `HEAD...ref` fallback L321, `touched` L325, `files` L327–334, `theirs` L342, LEGACY skip and temp-dir classify L348–357); `untracked_changes` L379–410 (walk L391–406); main loop L456–478; BRANCH SKIPPED print L499–501; UNTRACKED print L509–510; exit L514. All 03 citations hold. One drift: 03 cites `changed()` as L316–325, but it is really L318–322, with `tree` at L316 and `touched` at L325. This makes no difference to the plan.
- `tests/test_pipeline_check.py`: `_item` L19; `test_repo_pipeline_has_no_skipped_items` L139; `_branch_adds` L225 (writes only work/ files, with every file's body `A1 result: PASS`); 038 exit-0 pin L263–271; `_history` and `_commit` L604–622; 053 fixtures L630–792.
- Rules text: run-item.md L8; r3-fact-checker.md L22; i3-verifier.md step 3 = L14.
- No outside source was needed. The method is internal, and the git behaviour reused (first-parent walk, `diff-tree <c>^1 <c>`, merge-tree) is already pinned by the 052/053 tests.

## Files to create/change
Do these steps in order.
1. **scripts/check_pipeline.py: constants and parsing.**
   - Add `RESEARCH_CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/")` and `WAIVE_BUILD = {"04", "05", "06"}`. Leave `.claude/` and `templates/` out (gap h).
   - Refactor `read_request(path)` into `parse_request(text)` with the same return value, plus `read_request(path) = parse_request(path.read_text(encoding="utf-8"))`.
   - Add `_build_waived(text) -> bool`. It is True only when `WAIVE_BUILD <= set(steps)`, `who == "person"`, and the first `Waived:` line (`waived_line`) matches `\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:`.
2. **`_research_code(files, request_text_of)`.** Returns a list of `(ID, detail)`.
   - `files` is the unit's paths. `request_text_of(ID)` returns the tip request.md text, or None.
   - `code` = the files that start with RESEARCH_CODE_PATHS. If `code` is empty, return [].
   - `items` = the STEP_FILE IDs in `files`.
   - Covered → []: some item has `work/<ID>/04-build-plan.md` or `05-build-report.md` in `files`, and its tip Scope (via `parse_request`) is FULL or FAST.
   - Otherwise, for each item not in LEGACY:
     - Text is None → flag `RESEARCH ONLY check: no request.md at the tip, item 062`.
     - Scope is RESEARCH ONLY and `_build_waived` is False → flag `RESEARCH ONLY: changes <code> with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062)`.
   - Never read commit messages.
3. **HEAD side.**
   - Move L391–399 into `_walk(cutoff)`. It returns `(list of (sha, files), None)`, or `(None, (text, failed))` for the not-checked or error cases at L384–393.
   - `untracked_changes` keeps its output byte-for-byte (the 053 fixtures stay unchanged). A diff-tree failure stays a 053 entry. `_walk` yields `(sha, None)` for it, and `research_code` skips it.
   - Add `research_code(cutoff)`. Without git it returns None. If `_walk` fails, it returns `("not checked (see UNTRACKED CHANGE)", {})`. Otherwise it returns `(summary, {ID: (sha7, detail)})`, with `request_text_of` reading `work/<ID>/request.md` in the working tree.
   - In `main()`, after classify and the LEGACY override (L457–459) and before the IN PR block, a flagged ID gets `status, detail = "SKIPPED", f"{sha7} {detail}"`.
   - Flagged IDs that have no request.md dir are printed after the loop as `<ID>: SKIPPED (...)` and added to `skipped`.
   - Print `RESEARCH CODE: <IDs> | none | not checked (no git) | not checked (see UNTRACKED CHANGE)` right after the UNTRACKED CHANGE line.
   - Exit code: these items go through `skipped` only (L514 is unchanged).
4. **Branch side, in `open_branches`.**
   - Per ref: `code = changed(*RESEARCH_CODE_PATHS)`.
   - Unit = `code + [f"work/{i}/{f}" for i in touched for f in files[i]]`.
   - `request_text_of(i)` = `theirs[0]` when `theirs[1] == 0`, else None. Cache `theirs` per item in the existing loop (L340–342).
   - Run `_research_code` once per ref, after the loop. For each flag, if `skipped` already has that item, replace its detail with `f"{old}; {detail}"`. Otherwise append. The print at L499–501 is unchanged, and the exit code is unchanged.
5. **Docstring.** Add an item-062 paragraph after UNTRACKED CHANGE: the RESEARCH CODE line, the SKIPPED and BRANCH SKIPPED text, the waiver form, and gaps (g) a FULL/FAST 04/05 in the same unit covers, (h) `.claude/` and `templates/` are 053's only, (i) branch code committed without the research step file is 053's on HEAD, (j) only the first `Waived:` line is read.
6. **tests/test_pipeline_check.py.**
   - Add an `extra=()` parameter to `_branch_adds`. The paths it names are written with `_write` before the commit, and the default leaves existing callers unchanged.
   - Add the tests listed below.
   - In `test_repo_pipeline_has_no_skipped_items` (L139), add `assert "RESEARCH CODE: none" in out`.
7. **Rules text.** Use the exact sentences in 03 map step 7:
   - `.claude/commands/run-item.md` L8: append the sentence.
   - `.claude/agents/r3-fact-checker.md` L22: append the sentence.
   - `.claude/agents/i3-verifier.md` step 3 (L14): append the simulator/pickers sentence.
8. **work/062/05-build-report.md.** Include 03 map step 8 notes (a)–(d) for the person, the run on this HEAD (the `RESEARCH CODE:` line and the `BRANCH SKIPPED: 061 ...` line if origin/claude/project-thread-ltyppm is fetched), and the RI-007 guardrail status line.

Files planned: 5 (scripts/check_pipeline.py, tests/test_pipeline_check.py, .claude/commands/run-item.md, .claude/agents/r3-fact-checker.md, .claude/agents/i3-verifier.md). I2's own 05 is not counted.

## Tests and checks
Unit tests (no git):
- `test_build_waiver_needs_person_date_and_all_three`, parametrized over the 6 Self-check strings: `04 05 06 (person, 2026-11-13: ok)` → True; `02 04 05 06 (person, 2026-11-13: ok)` → True; `04 (person, 2026-11-13: x)` → False; `04 05 06 (I2, 2026-11-13: person said ok)` → False; `04 05 06 (person: ok)` → False; 023 shape `Waived: 02 (A1, 2026-10-31: x)\nWaived: 04 05 06 (person, 2026-11-13: ok)` → False.
- `test_research_code_rules`, plain lists:
  - 061 shape (`ccbot/x.py`, `work/160/01-research.md`, RESEARCH ONLY text) → 1 flag.
  - Add `work/161/05-build-report.md` with 161 FULL → [] (gap g).
  - A FULL item with 01 + code and no 04/05 → [] (pins the Scope test).
  - Only work/ files → [].
  - LEGACY `001` → [].
  - Person waiver → [].
  - `request_text_of` → None → flagged with "no request.md".

Git fixtures (`@NO_GIT` or the skipif already used):
- (1) `test_research_only_branch_with_code_is_branch_skipped`: `_branch_adds(repo, "res", "160", 01 02 03 07, RESEARCH ONLY text, extra=["ccbot/x.py"])`. Expect `BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes ccbot/x.py` and code == 0.
- (2a) The same branch with `Waived: 04 05 06 (person, 2026-11-13: ok)` → no `BRANCH SKIPPED: 160` line. (2b) With `(I2, 2026-11-13: person said ok)` → a `BRANCH SKIPPED: 160` line containing both `can be waived only by the person` and `RESEARCH ONLY: changes ccbot/x.py` (edge case d).
- (3) `test_research_only_head_commit_with_code_is_skipped`: `_history`, then `_item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")` + `ccbot/x.py` in one commit. Expect code == 1, `160: SKIPPED (<sha7> RESEARCH ONLY: changes ccbot/x.py`, `160:` printed exactly once, `RESEARCH CODE: 160`, `UNTRACKED CHANGE: none`.
- (4) A RESEARCH ONLY item with only work/ changes → `RESEARCH CODE: none`, code == 0.
- (5) The 160 01 + 161 FULL 05 + code in one commit → not flagged (gap g pinned).
- (6) The 023-shape two Waived lines → still flagged (gap j).
- (7) 160 re-scoped to FULL with 01 02 03 07 → no RESEARCH flag; `160: SKIPPED (FULL: missing 04 05 06 before 07`.
- (8) LEGACY `001` RESEARCH ONLY + code in one commit → not flagged.
- (9) No git (plain tmp_path) → `RESEARCH CODE: not checked (no git)`, exit unchanged.
- (10) Cutoff missing (reuse the `test_cutoff_missing_in_full_repo_fails` setup) → `RESEARCH CODE: not checked (see UNTRACKED CHANGE)`.

Regression: the whole of `tests/test_pipeline_check.py` passes, including the 038 pin L263–271 and every 053 fixture L630–792 unchanged; then the full suite.

Mutations (I3, in a scratch copy):
- Drop the Scope test in `_research_code` → (7) and the "FULL item with 01 + code" unit case fail.
- Drop the `WAIVE_BUILD <=` test → the `04 (person, ...)` case fails.
- Drop the who check → the unit case `Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")` fails (the date regex also matches a copied person bracket, so only the who check stops it; (2b) is caught by the regex too). Corrected after I3 round 1.

Run: `python3 scripts/check_pipeline.py` on this HEAD. Expect `RESEARCH CODE: none`, plus `BRANCH SKIPPED: 061 (origin/claude/project-thread-ltyppm: ... RESEARCH ONLY: changes ccbot/realtest.py scripts/fetch_real_data.py tests/test_realtest.py ...)` when that ref is present locally. `python3.11 -m py_compile scripts/check_pipeline.py`.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1: RESEARCH_CODE_PATHS, WAIVE_BUILD, `_build_waived` (steps ⊇ 04 05 06, who person, date regex) | Files step 1; test `test_build_waiver_needs_person_date_and_all_three` |
| Map 2: `_research_code`, coverage by FULL/FAST 04/05, LEGACY skip, missing request.md → flag, paths only | Files step 2; `test_research_code_rules`; fixtures (5), (8) |
| Map 3: HEAD walk shared with 053, SKIPPED replaces classify line, RESEARCH CODE summary, exit 1 | Files step 3 (as `_walk`, change b); fixtures (3), (4), (9), (10); 053 fixtures unchanged |
| Map 4: branch via `changed()`, `theirs`, merged detail on one line, exit unchanged | Files step 4; fixtures (1), (2a), (2b) |
| Map 5: docstring with gaps (g)–(j) | Files step 5; `grep -n "062" scripts/check_pipeline.py` |
| Map 6: fixtures (1)–(8) + mutations | Tests and checks (1)–(8), plus (9)/(10) for missing inputs |
| Map 7: run-item, r3, i3 rule lines | Files step 7; `grep -n "062"` → 1 line in each of the 3 files |
| Map 8: 05 notes (a)–(d) for the person | Files step 8 |
| Missing inputs: git, cutoff, request.md at tip, Scope, waiver date/who, second Waived line, merge-tree failure | Guardrail tests below |
| Fact-check fix "01 design D" (regex checked only 04) | Superseded by `_build_waived` in step 1; the `04 (person, ...)` case |
| Fact-check fix "01 design A" (Scope at the tip, not at `<c>`) | Steps 3/4 read the working tree or `git show <ref>:` |
| Rule the person follows (001: slack, tolerance, cap) | Not changed: this item touches no trading rule. The i3 line names the bot's pickers and config keys and does not alter them |

## Guardrail tests
- Feasibility: HEAD flag rule → 0 flags on this HEAD (057 changes 0 code files) → `test_repo_pipeline_has_no_skipped_items` asserts `RESEARCH CODE: none`.
- Feasibility: branch flag rule → 1 expected (061 on origin/claude/project-thread-ltyppm). The remote can't be pinned in a test, so I2 pastes the line in 05. The 061 shape is pinned by fixture (1).
- Feasibility: waiver rule → 2 of 6 strings count → `test_build_waiver_needs_person_date_and_all_three`.
- Missing inputs: git absent → fixture (9).
- Missing inputs: cutoff missing → fixture (10) (the shallow case stays covered by the 053 test at L683; no new test).
- Missing inputs: request.md at tip absent → `test_research_code_rules` None case.
- Missing inputs: Scope line absent → treated as FULL by `parse_request`. Fixture (7) shows FULL is not a silent pass.
- Missing inputs: waiver who not `person` / no date → (2b) and the unit cases `(I2, ...)` and `(person: ok)`.
- Missing inputs: second Waived line → fixture (6) and unit case 6.
- Missing inputs: merge-tree failure → the existing `changed()` fallback (L320–321). No new test; the 052 criss-cross test covers `changed()`.

## Expected result
- RESEARCH ONLY items whose commits change ccbot/, config/, scripts/ or tests/ are reported, unless covered or waived by the person: `<ID>: SKIPPED (...)` with exit 1 on HEAD, and `BRANCH SKIPPED: <ID> (...)` with exit 0 on open branches.
- On this HEAD: `RESEARCH CODE: none`, and 061 is shown as BRANCH SKIPPED when its ref is present.
- All existing pipeline tests pass unchanged; the new tests pass; each mutation fails at least one test.
- The three rule files carry the 062 sentences.
- RI-007 moves to GUARDED when merged, if a RESEARCH ONLY fixture with a ccbot/ file gives SKIPPED (fixture 3).
