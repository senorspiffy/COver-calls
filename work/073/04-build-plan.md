# 04 Build plan - 073
Fit verdict: FIT WITH CHANGES

Fit check. This is a rules-text item. It has no strategy, cost, broker or $3k-account effect: nothing in ccbot/, config/, data/, reports/ or scripts/ changes, and no rule the person follows in 001 (slack, tolerance, cap) changes. It writes down the person's fixed choice, "Always own run" (request.md L11). It does not reopen that choice. .claude/ and templates/ are RULE_PATHS (scripts/check_pipeline.py `RULE_PATHS`), so this is a RULES change and the person must OK the PR. It does not conflict with built code:
- check_pipeline's Real-data reader strips HTML comments (tests/test_real_data_field.py t22), so editing the template comment cannot change any 05/06 TOTAL check.
- `test_t7d_cutoff_constant_matches_template_comment` needs the substring `from item 070 check_pipeline.py requires`, which stays.
- 072's new tests/test_agent_tools.py checks only no-Bash agents for `python3 scripts/` lines. i3 has Bash, and the new sentences contain no `python3 scripts/`.

Changes against 03:
1. **C1, a text-pin test (RI-010).** 03 adds no test (map step 5: "no test added or removed"). RI-010's root cause is "text-only duties with no field and no check" (logs/recurring-issues.md, RI-010 root cause), and 072 settles the same kind of duty with a fixed-string drift test. So this plan adds one parametrized test, `test_t23_own_head_run_text`, in tests/test_real_data_field.py next to t7d. It pins the three new texts and the removal of "same dirs". The cost is 3 test ids. Files planned go from 3 to 4.
2. **C2, compare on the same `--max-rows`, and fall back to 05's pasted lines.** 03 step 3 says "`cmp` of this output with 05's diff output". 05 does not always keep a whole saved copy. In 068, 05 pasted only "per-file headers and the TOTAL line" and kept the whole output in a scratchpad file (work/068/05-build-report.md L100), and scratchpad files are cleared between sessions. A `cmp` across different `--max-rows` values also differs for no real reason (Extra research 1). The template sentence therefore says: use the same `--max-rows` as 05's command; `cmp` against 05's saved file; if that file is gone, compare line by line with the lines pasted in 05 and say so.
3. **C3, text anchors instead of line numbers.** I2 builds 071 → 072 → 073 → 074 on this branch, so line numbers move. Each edit below uses a text anchor. Shared files are flagged.

## Extra research (with sources)
1. **`--max-rows` changes the output but not TOTAL.** In scripts/diff_reports.py `diff_csv`, the counters (`rows_changed`, `rows_added`, `rows_removed`) go up for every row. Only the printed row lines are cut to `max_rows`, followed by `  ... <n> more` (L236-241). The TOTAL line is built from the counters (L289-292). So TOTAL can be compared across any `--max-rows` value, but a whole-output `cmp` only means something if both runs used the same `--max-rows`. 068 used `--max-rows 0` in both 05 and 06 (068/05 L100, 068/06 L90), so its `cmp` held. The default is 20 (L308). An I3 that leaves the flag out against a `--max-rows 0` paste in 05 would get a false "differs". → C2, and Missing inputs row 6.
2. **What `cmp` and `diff_reports` exit codes mean.** GNU diffutils: "An exit status of 0 means no differences were found, 1 means some differences were found, and 2 means trouble" (https://www.gnu.org/software/diffutils/manual/html_node/Invoking-cmp.html, fetched 2026-11-18). diff_reports uses the same convention: 1 when `_has_change`, 2 on DiffError or a bad argument (scripts/diff_reports.py L304-319). So for both commands, exit 1 is a result, not an error. Only exit 2 means I3's compare was not made. This fits Missing inputs row 5. No text change is needed, because the template asks for the result (identical / differing lines), not the exit code.
3. **R3's determinism finding re-checked for anything a run would stamp.** Grep over ccbot/realtest.py for `datetime.now|time.time|perf_counter|utcnow|generated|args.out|getpid|platform|__version__` gives 0 hits. Grep over ccbot/ for `date.today|os.environ|hash(` hits only ccbot/__main__.py L30 (the bot's `--asof` default) and ccbot/broker/webull_sandbox.py L117/L146. realtest reaches neither. So there is no timestamp, out-path or hash-order field in realtest's outputs that would make I3's own head run differ from 05's by itself. A "differs" result is a real finding. This confirms 03 rows 13 and 49.
4. **The 072 and 071 overlaps, read from their files.**
   - 072/04 (written) edits run-item.md at anchor A (the "Before each step" paragraph) and anchor B (a new paragraph after it), and states it "does not touch" the realtest paragraph. 073 appends only to the realtest paragraph.
   - 071 has no 04 yet. Its 02 (FOR 3, Holes "Agent text") proposes changing i3 step 5 ("write 06 on PASS and on FAIL"), adding a `Sent back to:` line under `## Sent back / sent to Audit` in templates/verification.md, and maybe adding a step-2 sentence about I3's own pasted `I3 FAIL` line (AGAINST 1 (i)). The 073 anchors below are sentences 071 is not planned to edit. If 071 appends a sentence to the end of step 2, 073's sentence still goes directly after the item-068 sentence, so the realtest rules stay together.

## Files to create/change
SHARED-file flags: i3-verifier.md (071 may edit step 5 and maybe the end of step 2); run-item.md (072 edits the "Before each step" paragraph and adds one after it); templates/verification.md (071 may add a `Sent back to:` line under the last heading). Build this item after 071 and 072 on daily-fixes/2026-11-18 and resolve by anchor. Never revert a neighbour's text.

1. **.claude/agents/i3-verifier.md** (SHARED with 071).
   - Anchor: in step 2, the sentence ending `run the base too (item 068).`
   - Insert directly after that sentence, on the same line, R3 map step 1's text word for word, starting with a single space: " Your head run is always your own: one full run made by you after 05 exists, in your own worktree of the head commit, with a new scratch `--out` that is not 05's, for every item whose 06 needs the Real-data TOTAL line (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py, not only ccbot/realtest.py); never use the head run made for 05, whoever made it (I2 or the orchestrator), even if the same-inputs check passes; if your run is cut off, run it again; only the base run may be reused, under the check above. It shows that 06's numbers come from the head commit, data and environment, not that the logic is right (item 073)."
   - Nothing else in the file changes.
2. **.claude/commands/run-item.md** (SHARED with 072).
   - Anchor: the paragraph starting "When an item changes `ccbot/realtest.py`", at its last sentence ending `come only from the full run (item 068).`
   - Append on the same line R3 map step 2's text word for word: " I3's head run is always its own full run, made for 06 with its own scratch `--out`, for every item whose 06 needs the Real-data TOTAL line (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py): never give I3 the head run made for 05, even when the same-inputs check passes, and if I3's run is cut off, I3 runs it again; only a base run may be reused (item 073)."
   - 072's anchor A/B edits stay as 072 built them.
3. **templates/verification.md** (SHARED with 071).
   - Anchor: in the `## Real-data effect` comment, the sentence `I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's.`
   - Replace only that sentence (C2 wording). The comment still ends ` -->`:
     "I3 runs diff_reports.py, with the same `--max-rows` as 05, on 05's base dir (or its own base run) and its own full head-run dir, never 05's head dir (item 073), and compares its TOTAL line with 05's. Also paste the head run's `--out` dir, worktree, log file and wall time, and `cmp` of this output with 05's saved output file: identical, or differs (the differing lines); if that file is gone, compare with the lines pasted in 05 and say so."
   - The rest of the comment is unchanged, including `from item 070 check_pipeline.py requires`.
4. **tests/test_real_data_field.py** (not shared: 071 edits tests/test_pipeline_check.py, 072 adds tests/test_agent_tools.py, and 074 adds its own probe tests).
   - Add after `test_t7d_cutoff_constant_matches_template_comment`. It uses the file's existing `REPO` and `pytest`.
   ```python
   @pytest.mark.parametrize("path, must, must_not", [
       (".claude/agents/i3-verifier.md",
        ["Your head run is always your own", "never use the head run made for 05", "(item 073)"], []),
       (".claude/commands/run-item.md",
        ["I3's head run is always its own full run", "never give I3 the head run made for 05", "(item 073)"], []),
       ("templates/verification.md",
        ["never 05's head dir (item 073)", "same `--max-rows` as 05"], ["same dirs"]),
   ], ids=["i3", "run-item", "template"])
   def test_t23_own_head_run_text(path, must, must_not):
       """073: I3's head run is its own (person's choice 2026-11-18); RI-010, a text duty with a check."""
       text = (REPO / path).read_text(encoding="utf-8")
       for s in must:
           assert s in text, f"{path}: missing {s!r}"
       for s in must_not:
           assert s not in text, f"{path}: still has {s!r}"
   ```

Files planned: 4 (4 changed, 0 new). Not changed: .claude/agents/i2-builder.md, templates/build-report.md, scripts/check_pipeline.py, scripts/diff_reports.py, logs/ history, 001.

## Tests and checks
- **Before-fix probe (I2).** Add the test first, before the three text edits: `python3 -m pytest -q tests/test_real_data_field.py -k t23` gives 3 failed. After the edits it gives 3 passed.
- `python3 -m pytest -q tests/test_real_data_field.py -k "t7d or t23"`: 5 passed (2 t7d + 3 t23).
- **Full suite.** `python3 -m pytest -q` = the base total after 071 and 072 are built, + 3, with no new failure. I2 pastes the base count taken on the branch just before 073's edits.
- **Greps (I2 records, I3 re-runs):**
  - `grep -c "item 073" .claude/agents/i3-verifier.md` = 1
  - `grep -c "(item 068)" .claude/agents/i3-verifier.md` = 1
  - `grep -c "make one full run at the head commit" .claude/agents/i3-verifier.md` = 1
  - `grep -c "item 073" .claude/commands/run-item.md` = 1
  - `grep -c "counts as the base only if" .claude/commands/run-item.md` = 1
  - `grep -c "the orchestrator runs their commands" .claude/commands/run-item.md` = 1 (072's text is intact)
  - `grep -c "same dirs" templates/verification.md` = 0
  - `grep -c "item 073" templates/verification.md` = 1
  - `grep -c "from item 070 check_pipeline.py requires" templates/verification.md` = 1
- **Mutations (I3, on a scratch worktree of the branch head, never the repo tree).** Each must make t23 fail:
  - m1: delete the 073 sentence from i3-verifier.md → `t23[i3]` fails.
  - m2: put back the old "same dirs" sentence → `t23[template]` fails on must_not.
  - m3: drop "never give I3 the head run made for 05" from run-item.md → `t23[run-item]` fails.
- `git diff --stat <073 base>..HEAD -- . ':!work' ':!logs'` lists exactly the 4 files above. I2 takes the count from the command, never by hand.
- `python3 scripts/check_handoff.py 073`: PASS.
- `python3 scripts/check_pipeline.py`:
  - 073 is not SKIPPED or INCOMPLETE.
  - `REAL-DATA FIELD:` does not name 073 (no TRIGGER path changes).
  - `LOG TIME:` does not name 073.
  - `UNTRACKED CHANGE:` none (I2 commits the .claude/, templates/ and tests/ edits together with 05, item 053).
  - The RULES BRANCH / OPEN BRANCHES lines are pasted.
- **05/06 Real-data section:** `not required (<git diff --stat file list>)`. This item costs 0 full runs (D4).
- **05 `Follow-ups for A1`** lists 03 map step 6 (a) and (b).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 1, i3 step 2 sentence | Files 1 (anchor after "run the base too (item 068)."); pinned by t23[i3] |
| Map step 2, run-item realtest paragraph sentence | Files 2 (anchor "come only from the full run (item 068)."); pinned by t23[run-item] |
| Map step 3, templates/verification.md sentence | Files 3, with C2 wording (same `--max-rows`, fallback to 05's pasted lines); pinned by t23[template] and t7d |
| Map step 4, no change to i2-builder, build-report, check_pipeline, logs | Files "Not changed" list; the `git diff --stat` check lists 4 files (3 in 03 + the C1 test file) |
| Map step 5, pipeline and suite checks | Tests and checks. The suite total is base + 3, not "equal to base" (C1) |
| Map step 6, follow-ups (a) head-dir check, (b) G1 widening | Tests and checks, last bullet (05 `Follow-ups for A1`); not built here |
| D1, scope = TRIGGER + TRIGGER_DIRS | Files 1, 2 (text names both); the 9-path set is pinned by the existing test_t9 |
| D1, I2's full-run trigger stays ccbot/realtest.py | Not changed (i2-builder.md, first half of run-item realtest paragraph) |
| D1, known gap G1 | Missing inputs row 4 (below); follow-up (b) |
| D2, verification.md in scope; t7d substring stays | Files 3; Tests (t7d still passes) |
| D3, no head-dir check in check_pipeline | DROPPED: 071 is editing check_pipeline.py in parallel, and a name check proves only that the names differ (03 row 16). It goes to the follow-up (a) |
| D4, 073 costs 0 full runs; non-trigger items unchanged | Tests and checks, 05/06 `not required` |
| Out of scope: base reuse, A1 re-run duty | Not changed |
| Missing inputs rows 1-7 | Guardrail tests, Missing inputs |
| Self-check numbers (13.71 min, 2-4 runs, 9 paths) | Expected result (cost line); the 9-path count is pinned by test_t9 |

No rule the person follows in 001 changes, so no 001 text update and no new request.

## Guardrail tests
- Feasibility: the scope rule "every item whose 06 needs the Real-data TOTAL line". Dated count in 03 (2026-11-18): 9 paths (8 TRIGGER + 1 TRIGGER_DIRS, scripts/check_pipeline.py `TRIGGER`/`TRIGGER_DIRS`, re-read by I1). It applies to 0 of 071-074 today. Pinned by the existing `test_t9_trigger_matches_realtest_imports_and_config_reads` (the set equals realtest's imports and config reads) and by `test_t23_own_head_run_text` (both rule texts name the set).
- Missing inputs (these are I3 actions, not script inputs; each has a stated 06 text, never a copied or defaulted value; the text side is pinned by t23):
  - 05's base dir gone or its inputs differ → unchanged item-068 rule: I3 runs the base too. Existing text, kept by the "(item 068)" grep = 1.
  - I3's own head run cut off → I3 runs again. If it cannot finish, FAIL "own head run not made (<why>)". Text in Files 1 and 2; t23 pins "never use / never give I3 the head run made for 05".
  - 05's TOTAL line missing → INCOMPLETE from item 070 (existing tests t17, t21).
  - 05 used `--tickers` (G1) → "TOTAL compare: n/a (05 used `--tickers <list>`)" plus I3's own full TOTALs, never "equal". Text-only; I3 checks it in 06.
  - 05's saved output file gone → line compare with the lines pasted in 05, and the 06 note says so (C2 text, pinned by t23[template] through "same `--max-rows` as 05" in the same sentence).
  - 05's `--max-rows` not stated → I3 compares TOTAL only and writes "whole-output compare: n/a (05's --max-rows not stated)". TOTAL does not depend on `--max-rows` (Extra research 1).
  - Log file, wall time, data hash or versions not captured → "unknown (<why>)", never copied from 05.
  - DROPPED as new script tests: these are I3's own actions, with no script to run them. The automated part is follow-up (a).

## Expected result
- i3-verifier.md and run-item.md each say in one sentence that I3's head run is always its own full run, in a new `--out`, for every TRIGGER/TRIGGER_DIRS item. I3 never uses 05's head run (I2's or the orchestrator's), even when the same-inputs check passes, and re-runs if cut off. Only the base may be reused.
- templates/verification.md no longer sends I3 to "the same dirs". It asks for I3's own head dir, the same `--max-rows`, the run's out dir, worktree, log and wall time, and a `cmp` (or line compare) with 05's output.
- tests/test_real_data_field.py: t23 gives 3 passed, and fails if any of the three texts is removed or the old sentence returns.
- Cost per future trigger item: +1 full run (13.71 min) over 068's practice; 2-3 runs typical (27.42 / 41.14 min), 4 at most (54.85 min). This item costs 0 full runs.
- The PR is a RULES BRANCH, so the person must approve it.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): the one scope rule has a dated non-zero count (9 paths), and I1 re-read it from check_pipeline.py. It is pinned by t9 and t23. No market filter is added.
- RI-002 (GUARDED): every absent I3 input gets a stated n/a or unknown text, or a re-run or FAIL. None is copied from 05. The new `--max-rows` row does the same.
- RI-004 / RI-005 (GUARDED): the 068 worked example was replayed on the new text: 05 L96's `068-after` is "the head run made for 05", so the rule fires. Cost numbers were re-derived: 3 x 822.704 s = 2468.1 s = 41.14 min.
- RI-006 (GUARDED): the file count is from the list (4). The suite delta is +3, from the 3 parametrize ids.
- RI-007 (GUARDED): Scope FULL, so I1-I3 run. I2 commits the tests/ and rule edits with 05.
- RI-009 (GUARDED): the shared files with 071 and 072 are flagged, the anchors are text, and the build order is 071 → 072 → 073 → 074.
- RI-010 (GUARDED): the text duty gets a check (C1, t23). The concrete 06 fields allow A1 spot-checks.
- RI-012 (GUARDED): no classifier is added. t23 is a plain substring presence test on fixed rule sentences, not a classifier of free text.
- RI-013 (GUARDED): I3's own diff is compared with 05's by TOTAL and by whole output, with the same `--max-rows`.
- Not applicable: RI-003 (no calendar), RI-008 (no new syntax; the test uses only features already in the file), RI-011 (no branch diff).

Log fields: FIT WITH CHANGES | 4 files planned
