# 04 Build plan - 097
Fit verdict: FIT WITH CHANGES

Fit check. This is a pipeline item with no trading code, so the ~$3k account and the 001 strategy rules are not touched (no ccbot/, config/ or data/ file; RI-013 diff_reports not required). It fits the existing code: the new git read goes through `_git_ok` (081), the new INCOMPLETE reason uses the same `_rule_seen` gate as `ROUND_HEADING_FROM` (084/091), and files are read through `_read` / `_md_lines` (089/082). Possible conflicts: items run one after another on this branch (092, 093, 096, 094, 095, 097, 098), so 097 is built on top of 094/095. 094 adds its own git read (GIT_CENSUS), and 095 changes check_pipeline.py and a1-auditor.md. Line numbers in 03 have already moved (03 says `SCRATCH` is at tests L4618; on 2026-11-24 it was at L4779), so I2 anchors every edit by function or constant name, never by a line number from 03. RULE_PATHS are touched (.claude/, templates/, scripts/check_pipeline.py), so RULES BRANCH shows and **the person's OK is needed at PR review**. That review also covers: option (i), the reading of the request's "orchestrator never names a scratch path" (03 Fact check, open question 1), and the change to step 4 below.

Changes to 03 (the reasons are under Extra research):
1. Step 4 shape check: match the **basename** of the named path (one trailing `/` stripped), not the segment after a literal `/scratchpad/`. The scratchpad dir is "<absolute scratchpad path>" in SCRATCH, and nothing requires it to be named `scratchpad`. All 8 known 091 dirs still give the same result: 3 pass, 5 fail.
2. Step 3: add `"STASH:"` to `GIT_LINES`. `test_malformed_shallow_real_git_nothing_none` (b) must then be measured, not assumed (see Extra research 2).
3. Step 4: a template placeholder copied without being filled in is flagged (fixture N9). The template line carries no trailing text after the placeholder, so a filled-in line is exactly `Scratch dir: <path>`.
4. 098 is built after 097 and its ID is ≥ SCRATCH_FROM, so 098's own 05/06 must carry `Scratch dir:` lines. 05 tells 098's I1/I2 this in a short "Next item" note.

## Extra research (with sources)
1. **The scratch dir name is not fixed.** SCRATCH says `dir="<absolute scratchpad path>"`, and Python's `tempfile.mkdtemp` puts the name (prefix + 8 random chars) as the **last** component under `dir` (https://docs.python.org/3/library/tempfile.html: "The directory name is ... prefix ... suffix", "Changed in version 3.12: mkdtemp() now always returns an absolute path"). So the basename is the one part mkdtemp controls. The parent's name depends on the harness: here it is `.../scratchpad`, but another run or the person's machine may use another name. If the check is keyed on `/scratchpad/`, a correct mkdtemp dir elsewhere would be flagged. Re-checked over 03's 8 dirs with the basename rule: `i3-091-r1-dpe6hf15`, `i3-091-r2-mz28r6tf`, `a1-091-r1-46dt4kc_` pass; `i3-091r2-UxQ8`, `i2-091r2-LpYi`, `/tmp/claude-0/scratch/i3-091/wt` (basename `wt`), `.../i2-091/` (basename `i2-091`), `.../i2-091b/` (basename `i2-091b`) fail. That is 3 pass + 5 fail = 8, the same as 03 Self-check row 1. This item's own dir, `i1-097-r1-rti7e4v7` (made by the orchestrator with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i1-097-r1-", dir="<scratchpad>"))'`, the fact the caller gave), has the shape: `rti7e4v7` = r,t,i,7,e,4,v,7 = 8 chars in `[a-z0-9_]`.
2. **`git stash list` with no refs/stash reads no history.** builtin/stash.c `list_stash` returns 0 before running `git log` when refs/stash is absent (03 row FOR 3, https://raw.githubusercontent.com/git/git/master/builtin/stash.c). So in `test_malformed_shallow_real_git_nothing_none` (bad `.git/shallow`, no stash), STASH probably prints `none`, which is a true answer. That would break (b)'s "no line ends with : none" assertion once STASH is in GIT_LINES. Not measured: no shell (item 072). I2 runs (b) and pins what it sees: if `STASH: none`, (b) exempts only `STASH:` from the none ban and asserts `STASH: none`, with the reason "no refs/stash, so no history read (stash.c list_stash)". I2 also adds fixture (e): a stash entry made before the shallow file is corrupted, then I2 records the exit of `git stash list` (it runs `git log -g`). If that is non-zero, pin `STASH: not checked (git stash failed (exit <n>)) (item 097)`. If it is 0, pin `STASH: 1 ...`. Either way the line is never `none` when an entry exists.
3. **`list` passes its options to `git log`.** "The command takes options applicable to the *git log* command to control what is shown and how" (https://git-scm.com/docs/git-stash, `list [<log-options>]`). User log config can add output lines to a log listing. So the decision is: exit 0 and `out.strip() == ""` gives none, and any other exit-0 output gives entries (exit 1). `n` is the number of non-empty lines and is only shown, never used to decide. Residual, stated in 05: a config that adds lines can raise `n`, but it can never turn entries into `none`. No line is classified by its text (RI-012).
4. Confirmed in the code (Read, 2026-11-24): `_git_ok` gives `(None, "no git")` when `_git` is None, which covers a tmp_path that is not a repo top. So every fixture run outside a repo prints `STASH: not checked (no git)` and its exit code does not change. `test_git_call_census` counts only direct `_git`/`_git_ok` calls by their innermost function. The new `_rule_seen(..., "SCRATCH_FROM", ...)` call adds no census entry, because `_rule_seen`'s own 3 calls are already counted. The `main` stash read adds the key `("main", "_git_ok")`: today `main` has only `("main", "_git")`, so this is a **new key** with count 1, not a bump.

## Files to create/change
Commit order: A (text + pins), then B (stash line), then C (Scratch dir check). Each commit leaves the suite green.

**A. Rule text (03 steps 1-2)**
- `.claude/commands/run-item.md`, `.claude/agents/i2-builder.md`, `.claude/agents/i3-verifier.md`, `.claude/agents/a1-auditor.md`: replace the 091 SCRATCH sentence (one copy in each) with the 03 step 1 sentence, copied exactly from 03 (beginning "Every agent works in its own new scratch dir and never reuses ..." and ending "... never in the main checkout (items 091, 097)."). Same commit as the test constant.
- `.claude/agents/i2-builder.md`: "(`git worktree add` or a copied folder)" → "(a `git worktree add --detach` worktree or a copied folder)".
- `.claude/commands/run-item.md`: in the end-of-item check_pipeline sentence (the one ending "and `LOG BATCH:` must not name it (item 086)"), add the 03 step 2 clause: "and `STASH:` must be `none`; only the person drops or clears a stash entry, and an agent never drops one it did not make (item 097)".
- `.claude/agents/i2-builder.md` and `i3-verifier.md`: add one sentence after SCRATCH: "05 (I2) / 06 (I3) has one column-0 `Scratch dir: <path mkdtemp printed>` line per dir used, or `Scratch dir: none (<reason>)` (item 097)." This tells the agents about the step C check (RI-010: a duty that a check enforces must be written in the agent text).

**B. Stash line (03 step 3), scripts/check_pipeline.py `main`**
- After the `UNCOMMITTED STEP:` print: `stash_out, stash_why = _git_ok("stash", "list")`.
  - `stash_why == "no git"` → `STASH: not checked (no git)`, exit unchanged.
  - any other `stash_why` → `STASH: not checked (<stash_why>) (item 097)`, `stash_bad = True`. stdout is not read.
  - exit 0 with `stash_out.strip() == ""` → `STASH: none`.
  - otherwise → `STASH: <n> (first: <first non-empty line>); local to this checkout; only the person drops an entry (item 097)`, `stash_bad = True`.
- Add `or stash_bad` to the final `return 1 if ...` expression.
- Update the module docstring's output list with one `STASH` line (item 097, RI-009, exit 1).

**C. Scratch dir check (03 step 4, changed)**
- `scripts/check_pipeline.py`: add `SCRATCH_FROM = 97` next to `ROUND_HEADING_FROM`, with a comment in the same style ("the 9th `*_FROM` cutoff ...").
- Add `SCRATCH_NAME = re.compile(r"(i2|i3)-(\d{3})-r\d+-[a-z0-9_]{8}")`, used with `.fullmatch`.
- New helper `scratch_dir_problems(text, step, item)` returns a list of entry strings:
  - It reads the column-0 lines starting `Scratch dir:` with `_md_lines(text)[0]` and state "out", the same way `_suite_lines` does.
  - No such line → `<step> has no Scratch dir: line (item 097)`.
  - For each line, the value is the whole text after `Scratch dir:`, stripped. It is OK if it is `none (` + a non-blank reason + `)`, or if it is absolute (`PurePosixPath(v).is_absolute()`) and `PurePosixPath(v.rstrip("/")).name` fullmatches SCRATCH_NAME, with group 1 == `i2` for 05 or `i3` for 06 and group 2 == the item ID.
  - Otherwise → `<step> Scratch dir '<value>' is not the mkdtemp form (item 097)`.
- In `incomplete()`, right after the `ROUND_HEADING_FROM` block: `if int(item_dir.name) >= SCRATCH_FROM:` loop over 05 and 06. Skip a step file that does not exist (classify reports missing files). Read it with `_read`; a read failure → `<step> scratch dir not checked (<why>; item 097)`. If the helper's list is not empty, call `_rule_seen(item_dir, step, "SCRATCH_FROM", env)`. False → not_seen row `(ID, step, sha7, "SCRATCH_FROM", "097", "no Scratch dir check")`. Otherwise → `missing += problems + ([sha7] if seen is None and sha7 else [])`, as the ROUND_HEADING_FROM block does. Add one sentence about it to the `incomplete` docstring.
- `templates/build-report.md`: add the column-0 line `Scratch dir: <absolute path printed by mkdtemp; one line per dir used, or none (<reason>)>` right after the `# 05` title. Nothing follows the placeholder on that line (change 3).
- `templates/verification.md`: the same line after the `Sent back to:` comment block.

**Tests, tests/test_pipeline_check.py**
- Keep 091's text as `OLD_SCRATCH`, and set `SCRATCH` to the new sentence.
- `test_scratch_sentence_same_in_four_files` asserts `count(SCRATCH) == 1` and `count(OLD_SCRATCH) == 0` in each of the 4 files, plus `"git stash" in SCRATCH` and `"--detach" in SCRATCH`.
- New pins, each `count(...) == 1`:
  - `test_run_item_stash_clause`: the step-2 clause in run-item.md.
  - `test_i2_detach_phrase`: the phrase in i2-builder.md.
  - `test_scratch_dir_line_in_agent_texts`: the sentence in i2 and i3.
  - the template line in both templates.
- `GIT_CENSUS`: new key `("main", "_git_ok"): (1, "097: stash list; no git -> not checked, other failure -> not checked + exit 1, entries -> exit 1")`. In `test_git_call_census`, the total becomes the **base value + 1**: I2 reads the asserted number in the base before editing (after 094/095) and writes it in 05. It is never typed as 48.
- `GIT_LINES`: add `"STASH:"`.
- `test_repo_pipeline_has_no_skipped_items`: first run `git stash list` in REPO (the worktree shares refs/stash). If its output is non-empty, the expected exit is 1, and the test checks `STASH: <n> (first: ...` instead of `code == 0` and asserts the rest unchanged. Else assert `"STASH: none" in lines`.
- Stash fixtures, real tmp repo, `@NO_GIT`:
  - (a) `git stash push` → `STASH: 1 (first: stash@{0}: WIP on <branch>: <sha7> <subject>); local to this checkout; ...`, exit 1.
  - (b) after `git stash drop` → `STASH: none`, exit 0.
  - (d) stash pushed inside a `git worktree add --detach` worktree → seen by the main fixture checkout as `STASH: 1 ...`.
  - (e) per Extra research 2.
- Monkeypatch fixture (c): `_git` returns `("", 128)` for `("stash","list")` and passes through otherwise → `STASH: not checked (git stash failed (exit 128)) (item 097)`, exit 1.
- Scratch fixtures, built with `_item`/`_commit` helpers like the round-heading fixtures, with `SCRATCH_FROM = 97` in the fixture RULE_FILE at the adding commit. 05 has these lines:
  - P1 `Scratch dir: /tmp/x/scratchpad/i2-150-r1-ab_cd123` → no entry.
  - P2 `Scratch dir: /home/u/elsewhere/i2-150-r2-ab_cd123/` (no `scratchpad`, trailing slash) → no entry. This pins change 1.
  - P3 two lines r1 + r2, both valid → no entry.
  - N1 `/tmp/claude-0/scratch/i2-150/` → entry.
  - N2 `/tmp/x/scratchpad/i2-150r2-UxQ8` → entry.
  - N3 05 with an `i3-150-r1-…` basename → entry.
  - N4 no line → entry.
  - N5 `none ()` → entry.
  - N6 `none (text-only item)` → no entry.
  - N7 9-char suffix `ab_cd1234` → entry.
  - N8 `scratchpad/i2-150-r1-ab_cd123` (relative) → entry.
  - N9 the template placeholder line unchanged → entry.
  - N10 a valid basename with the wrong ID `i2-151-r1-ab_cd123` → entry.
  - N11 a valid line only inside a code fence → `has no Scratch dir: line`.
  - N12 a valid path followed by trailing text (`... (round 1)`) → entry.
  - 06 with an `i2-` basename → entry (agent tied to file).
  - Boundary: ID 097 with N1 → entry; ID 096 with N1 → none.
  - Gate: fixture RULE_FILE without `SCRATCH_FROM = ` at the adding commit → no entry, and `RULE NOT SEEN` names `SCRATCH_FROM (097)`.
  - Real mkdtemp: `tempfile.mkdtemp(prefix="i2-150-r1-", dir=tmp_path/"any")` used as the 05 value → no entry.

## Tests and checks
1. Base (03 step 0): head sha. Run `git stash list; echo "exit $?"` in the orchestrator checkout and paste the output. Note the census total and GIT_LINES as read. If the stash list is non-empty, stop and report to I1 and the person, and never drop an entry. 05 also records I2's own `Scratch dir:` line(s).
2. After each commit A/B/C: `python3 -m pytest -q`, green.
3. Mutants, run in I2's mkdtemp scratch worktree. A file is restored with `git checkout HEAD -- <file>` there, or from a copy, never with stash and never in the main checkout. Each mutant must fail at least one test:
   - (A1) the old SCRATCH is left in one file.
   - (A2) the new SCRATCH is missing from one file.
   - (A3) the i2 phrase is reverted.
   - (A4) the run-item clause is removed.
   - (B1) `or stash_bad` is removed from the return.
   - (B2) a non-zero exit is mapped to `none`.
   - (B3) stdout is read before the exit check (`if stash_out.strip()` first).
   - (C1) the Scratch check block is removed.
   - (C2) `.fullmatch` → `.match`.
   - (C3) the agent is not tied to the step.
   - (C4) the ID is not tied to the item.
   - (C5) `SCRATCH_FROM = 98`.
   - (C6) the basename is replaced by the `/scratchpad/` segment (P2 fails).
4. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` (RI-008), if available. Otherwise say so.
5. `python3 scripts/check_pipeline.py` in the orchestrator checkout. Expected: 097 has no INCOMPLETE and no SKIPPED, LOG TIME / LOG BATCH do not name it, and the line is `STASH: none`.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 0 base check, build after 093/094/095/098 that touch same files | Tests and checks 1; built in branch order after 094/095 (Fit check). 098 comes after 097, see change 4 |
| Step 0 stash non-empty → stop, never drop | Tests and checks 1 |
| Step 1 new SCRATCH sentence in 4 files | Files A, bullet 1; tests `SCRATCH`/`OLD_SCRATCH` pins; mutants A1/A2 |
| Step 1 i2 `--detach` phrase | Files A, bullet 2; `test_i2_detach_phrase`; mutant A3 |
| Step 1 05 states text-only residuals | Expected result, residuals |
| Step 2 run-item STASH clause | Files A, bullet 3; `test_run_item_stash_clause`; mutant A4 |
| Step 3 `_git_ok("stash","list")` line, 4 outcomes, exit | Files B; fixtures a-e; mutants B1-B3 |
| Step 3 census + 1 from base | Tests: GIT_CENSUS new key `("main","_git_ok")`, total = base + 1 |
| Step 3 STASH in `test_all_git_fails_no_line_says_none` | Tests: `GIT_LINES` + `"STASH:"` (that test iterates GIT_LINES); (b) measured per Extra research 2 |
| Step 3 `test_repo_pipeline_has_no_skipped_items` reads stash first | Tests bullet on that test |
| Step 4 template lines | Files C, templates; fixture N9; template pin |
| Step 4 `SCRATCH_FROM = 97`, `_rule_seen` gate, not_seen row | Files C; boundary 097/096; gate fixture; mutant C5 |
| Step 4 `SCRATCH_DIR` regex on `/scratchpad/` segment | Changed: basename fullmatch `SCRATCH_NAME` (change 1, Extra research 1); P2 + mutant C6 |
| Step 4 agent tied to file, fullmatch, 8 chars | N3, 06-i2 case, N7; mutants C2/C3 |
| Step 4 fixtures P1, N1-N8, real mkdtemp | Tests, Scratch fixtures (all kept; N9-N12, P2-P3 added) |
| Step 4 "No git call added" | Kept: census unchanged by C (Extra research 4) |
| Step 4 read through 089's reader | Files C: `_read`, failure entry `scratch dir not checked` |
| Step 5 close: suite, py_compile, check_pipeline | Tests and checks 2, 4, 5 |
| Step 5 I3 re-runs every mutant in own mkdtemp dir | Tests and checks 3 (I3 repeats it) |
| Correction row 1 (sentence must name the orchestrator) | Files A bullet 1 (the new sentence names it) |
| Correction open question 1 / option (i) | Fit check: flagged for the person at PR review; option (ii) not built |
| Correction C8 `--detach` preventive only | Files A bullets 1-2 (as preventive, not claimed as fix) |
| Removed claim (Write for tool input) | DROPPED: removed in 03, no plan line rests on it |
| Missing inputs rows (stash ×4, 05/06 ×2, Scratch line ×2, anchor ×2, census) | Guardrail tests, Missing inputs |
| Rule the person follows (001 slack/tolerance/cap) | DROPPED: none changed; no 001 text affected |

## Guardrail tests
- Feasibility: the STASH line has dated counts. On 2026-11-24 this checkout had 0 entries (R3 read of .git: no refs/stash, no logs/refs/stash, no packed-refs, no reftable), and I2's base run is the count of record. Fixtures pin (a) 1 entry → exit 1, (b) 0 → none, exit 0, (c) a failed read, (d) 1 entry seen across worktrees.
- Feasibility: the Scratch dir shape over the 8 known 091 dirs gives 3 pass / 5 fail (03 Self-check, re-derived with the basename rule in Extra research 1). P1/P2/P3 and the real mkdtemp fixture pin passing cases, and N1-N12 pin failing cases.
- Feasibility: SCRATCH_FROM covers 0 of 7 current items with a 05 or 06 at ≥ 097 (work/092-098, Glob 2026-11-24). The boundary fixtures 097 (entry) and 096 (none) pin the window.
- Missing inputs: `git stash list` without git → `STASH: not checked (no git)`, exit unchanged. Any fixture outside a repo hits this; `test_all_git_fails_no_line_says_none` covers the 128 case.
- Missing inputs: `git stash list` exit ≠ 0 → fixture (c), `not checked (...)`, exit 1, stdout not read (mutant B3).
- Missing inputs: `git stash list` exit 0 and empty → fixture (b), `STASH: none`.
- Missing inputs: a stash entry plus a bad shallow file → fixture (e), measured and pinned, never none.
- Missing inputs: a 05/06 file that is absent → no Scratch entry (an absent-file fixture: an item with 04 only gives no `Scratch dir` entry).
- Missing inputs: a 05/06 that is unreadable or not UTF-8 → a fixture with a non-UTF-8 byte in 05 gives `05 scratch dir not checked (... unreadable; item 097)` and the path in UNREADABLE.
- Missing inputs: `Scratch dir:` line absent → N4 (and N11 for a line in a fence).
- Missing inputs: empty `none ()` reason → N5.
- Missing inputs: `_rule_seen` env set (no git or shallow) → the strict rule applies. A fixture with `env="no git"` passed to `incomplete` and N1 gives an entry.
- Missing inputs: a step file added without `SCRATCH_FROM` → the gate fixture's RULE NOT SEEN row.
- Missing inputs: the census total at base → read from the base, written in 05.

## Expected result
- The suite is green after A, B and C, with every mutant in Tests and checks 3 failing at least one test.
- `check_pipeline.py` on the branch prints `STASH: none` with no exit change today, and 097 has no INCOMPLETE entry (its own 05/06 carry valid `Scratch dir:` lines).
- No item before 097 changes status (SCRATCH_FROM covers 0 of them). 098 must carry the lines (05 note).
- Census = base + 1.

05 states these residuals, which no check can see:
- STASH sees only entries left behind, so 091's run of 3 entries made and 3 dropped would still pass.
- The no-stash rule at the moment of use is text-only.
- The orchestrator's hand-outs to R1-R3/I1 are text-only (their files have no Scratch dir field). This plan's own dir is `/tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/i1-097-r1-rti7e4v7` (made by the orchestrator with mkdtemp, per the caller; not used, as no files were needed).
- A1's own dir is text-only.
- `n` in the STASH line may count lines added by user log config, which is cosmetic.
- The Scratch dir field shows that a path of the mkdtemp shape was written, not that mkdtemp made it.

Recurring issues checked (item 013): RI-001 (ESCALATED: every filter/window has a dated count, see Guardrail tests Feasibility; no "always" claim), RI-010 (ESCALATED: new duties are in the agent text, Files A bullet 4, and enforced by INCOMPLETE/STASH where a check can exist; text-only parts are named), RI-014 (OPEN: one new git read via `_git_ok`, a failed read never says none, the shallow case is measured in fixture e). Also checked: RI-002 (nothing defaulted; Missing inputs), RI-004/005 (3-of-8 re-derived with the changed rule; the P1/N7 counts re-checked: `ab_cd123` = 8, `ab_cd1234` = 9), RI-006 (census taken from the base, not typed), RI-007 (FULL scope, code only in I2), RI-008 (py_compile 3.11), RI-009 (this item; build order; stash shared across worktrees pinned by fixture d), RI-012 (decided by exit code and empty stdout, anchored fullmatch, negative fixtures N1-N12), RI-013 (no realtest path change).

Log fields: FIT WITH CHANGES | 8 files planned
