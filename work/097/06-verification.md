# 06 Verification - 097
Verdict: PASS (round 1)
Sent back to: none
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/i3-097-r1-c4bgygg5

Base 762c8ec, head 1f27ce7 (branch daily-fixes/2026-11-24; 092-096 complete). I made the scratch dir myself with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-097-r1-", dir="/tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad"))'`. Mutants ran in `<scratch dir>/wt`, made with `git worktree add --detach <scratch dir>/wt 1f27ce7`; each edited file was restored from an in-memory copy by the driver (`<scratch dir>/mutants.py`), `git status --short` in wt was empty afterwards, and the worktree was then removed (`git worktree list` shows only the main checkout). No `git stash` was run anywhere. `git stash list` in the main checkout, at start and at end: no lines, exit 0.

## I1 audit (plan vs research)
- 04's Rule trace maps every 03 map step (0-5), the Fact check correction rows, Missing inputs and the removed claim to a plan line or a DROPPED reason. I checked each step against 03's Implementation map: step 1 sentence, step 1 i2 phrase, step 2 clause, step 3 STASH outcomes / census / GIT_LINES / repo test, step 4 templates / SCRATCH_FROM / `_rule_seen` gate / fixtures, step 5 close. The step 1 sentence in 03 is the same text as the `SCRATCH` constant in the tests (I parsed it out of the tests file with `ast` for mutants A1/A2, and it is found once in each of the 4 files).
- Changes from 03, each stated and sourced in 04 Extra research: (1) basename fullmatch instead of the `/scratchpad/` segment (Python tempfile docs: mkdtemp's name is the last component under `dir`; re-derived 3 pass / 5 fail over 03's 8 dirs, same as 03 Self-check row 1); (2) `STASH:` in GIT_LINES, shallow (b) case measured rather than assumed (stash.c list_stash source); (3) N9 unfilled placeholder; (4) 098 note. Added fixtures P2, P3, N9-N12 and the 06-i2 case extend 03's list and are traced. No unsourced addition.
- Option (i) (reading of "the orchestrator never names a scratch path") is flagged for the person at PR review in 03, 04 and 05, not decided silently.

## I2 audit (build vs plan)
`git diff --stat 762c8ec 1f27ce7 -- . ':!work' ':!logs'`: 9 files (a1-auditor.md, i2-builder.md, i3-verifier.md, run-item.md, scripts/check_pipeline.py, templates/build-report.md, templates/verification.md, tests/test_pipeline_check.py, tests/test_real_data_field.py). Line by line against 04:
- A: the 091 sentence is replaced in all 4 files (count new = 1, old = 0, by test and by my A1/A2 mutants); i2 phrase now "(a `git worktree add --detach` worktree or a copied folder)"; run-item end-of-item clause added after "(item 086)"; the `Scratch dir:` duty sentence is in i2 and i3 right after SCRATCH. Match.
- B: `_git_ok("stash", "list")` right after the UNCOMMITTED STEP print; four outcomes exactly as 04 (no git -> not checked, exit unchanged; other reason -> not checked + `stash_bad`; exit 0 and empty -> none; else n + first line + `stash_bad`); `or stash_bad` in the return; docstring STASH entry. GIT_CENSUS new key `("main", "_git_ok")` count 1; total 50 -> 51 (the base value, read in 05, not typed). Match. `_git_ok` passes stdout through on failure (L1579-1580), so "stdout not read" is a real property of the branch order, pinned by fixture (c).
- C: `SCRATCH_FROM = 97` after ROUND_HEADING_FROM; `SCRATCH_NAME` used with `.fullmatch`; `scratch_dir_problems` reads column-0 `_md_lines` "out" rows; basename with one trailing `/` stripped; `is_absolute`; agent tied to step, ID tied to item; `none (<non-blank>)`. `incomplete()` block placed after ROUND_HEADING_FROM, absent file skipped, `_read` failure -> `scratch dir not checked`, `_rule_seen` gate with not_seen row. Templates carry the line with nothing after the placeholder. Match.
- Deviation 3 (the 095 `unsure` branch in the Scratch block) follows the current shape of the ROUND_HEADING_FROM block the plan says to copy; correct. Deviation 4 (`test_non_utf8_shallow_line_no_traceback` STASH exemption) has the same measured reason as (b); the exemption asserts `lines == ["STASH: none"]`, so it is exact, not a skip. Deviation 1 (partial 05 in A and B) is forced by 053 + 043 and is noted for I1.
- **Deviation 2 (9th file, `_scratch_line` in fixture helpers): hides no existing check.** The helper adds one line only for IDs >= 97 and only to 05/06 files the helpers already wrote; it never removes or replaces content. Proof by mutant H in my scratch worktree: with the check switched off (`SCRATCH_FROM = 10**9`) *and* `_scratch_line` returning `""` for every ID, `tests/test_pipeline_check.py tests/test_real_data_field.py` gave `21 failed, 487 passed`, and all 21 are the new 097 scratch tests or the 3 tests whose expected string now names a scratch entry (`test_unfilled_template_suite_line_is_incomplete`, `test_unreadable_06`, `test_unreadable_05_at_suite_check`). No test in test_real_data_field.py failed, and no other pre-097 test changed result. So every pre-097 assertion holds with and without the line: the line changes no other check's outcome. The 3 changed expected strings only gained the scratch entry; their earlier parts are unchanged (diff read).
- Grep reasons in 05: `ccbot/` and `config/` untouched (`git diff --stat 762c8ec 1f27ce7 -- ccbot/ config/ data/` empty); the 5 hits in check_pipeline.py are 4 docstring/comment text and the existing `else 0` exit expression. Agreed.
- Connectivity re-done: `scratch_dir_problems` called by `incomplete`; `SCRATCH_FROM` read by `incomplete` and by name in `_rule_seen`; `SCRATCH_NAME` and `SCRATCH_AGENT` read by `scratch_dir_problems`; `stash_bad` read by the return; the STASH line printed in the repo run below. No TODO added.
- BUG item: fix and guardrail both in place. The fix is the rule text (A); the guardrails are STASH (exit 1 on any entry) and the Scratch dir INCOMPLETE check. Would they have caught 091? 091's I2 dropped its 3 stash entries, so STASH alone would not (residual stated in 04/05); but the orchestrator-typed dirs `/tmp/claude-0/scratch/i3-091/wt`, `.../i2-091/`, `.../i2-091b/` fail the Scratch dir check (fixture N1 is that shape and gives an entry; boundary fixture ID 097 + N1 -> entry), so an 091-style 05/06 would be INCOMPLETE. A stash left behind is caught by fixtures (a) and (d).
- RI-012: STASH is decided by exit code and empty stdout only, no text is classified. The Scratch dir value is matched with an anchored fullmatch on the basename, with negatives where the pattern sits inside other text: N12 (valid path + trailing text), N7 (valid prefix + extra char), N10 (wrong ID), N8 (relative), N11 (only in a fence). Present.
- RI-002: no default was removed by this item, so there is none to put back; the fail-open analogue (B2: a failed read mapped to `none`) fails 3 tests.
- Rule the person follows (001): not touched.
- Simulator rule (062): no simulator or replay. Real-data head run: not needed (no TRIGGER / TRIGGER_DIRS file changed).

## Tests re-run (output)
Full suite, main checkout at 1f27ce7 (clean), Python 3.13.18, git 2.43.0:
```
$ python3 -m pytest -q -p no:cacheprovider
917 passed, 1 skipped in 128.31s (0:02:08)
```
Suite: 917 passed, 1 skipped in 128.31s (0:02:08)

The skip (second run with `-rs`, `917 passed, 1 skipped in 119.31s (0:01:59)`): `tests/test_calendar.py:110: could not import 'exchange_calendars'`. `test_every_py_compiles_on_oldest_python` ran (python3.11 is on PATH; python3.10 is not). `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py tests/test_real_data_field.py`: exit 0, no output. 05's 1 failure (`test_repo_pipeline_has_no_skipped_items`, 097 without its I2 line at 13fb139) is gone at 1f27ce7, as 05 predicted.

`python3 scripts/check_handoff.py 097`:
```
sources count (unique URLs in 01-research.md): 5
fact-check rows: 53
totals line: 53 rows -> 39 as-is, 13 fixed, 1 removed
PASS
exit 0
```

Mutants, `<scratch dir>/wt` (detached worktree of 1f27ce7), `python3 -m pytest -q -p no:cacheprovider -rf tests/test_pipeline_check.py` per mutant (H also runs tests/test_real_data_field.py), output as printed by `<scratch dir>/mutants.py`:
```
A1: 1 failed, 468 passed in 65.30s (0:01:05) | other than repo test: 1 ['test_scratch_sentence_same_in_four_files']
A2: 1 failed, 468 passed in 58.76s | other than repo test: 1 ['test_scratch_sentence_same_in_four_files']
A3: 1 failed, 468 passed in 61.81s (0:01:01) | other than repo test: 1 ['test_i2_detach_phrase']
A4: 1 failed, 468 passed in 60.08s (0:01:00) | other than repo test: 1 ['test_run_item_stash_clause']
B1: 3 failed, 466 passed in 58.47s | other than repo test: 3 ['test_stash_entry_is_listed_then_none_after_drop', 'test_stash_failed_read_is_not_checked', 'test_stash_in_detached_worktree_is_seen_by_main_checkout']
B2: 3 failed, 466 passed in 62.55s (0:01:02) | other than repo test: 3 ['test_all_git_fails_no_line_says_none', 'test_stash_failed_read_is_not_checked', 'test_stash_entry_with_bad_shallow_is_never_none']
B3: 2 failed, 467 passed in 61.56s (0:01:01) | other than repo test: 2 ['test_all_git_fails_no_line_says_none', 'test_stash_entry_with_bad_shallow_is_never_none']
C1: 21 failed, 448 passed in 62.62s (0:01:02) | other than repo test: 21 ['test_unfilled_template_suite_line_is_incomplete', 'test_unreadable_06', 'test_unreadable_05_at_suite_check']
C2: 2 failed, 467 passed in 61.65s (0:01:01) | other than repo test: 2 ['test_scratch_dir_bad_lines[N7-9-chars]', 'test_scratch_dir_bad_lines[N12-trailing-text]']
C3: 2 failed, 467 passed in 62.20s (0:01:02) | other than repo test: 2 ['test_scratch_dir_bad_lines[N3-agent-not-i2]', 'test_scratch_dir_06_is_tied_to_i3']
C4: 1 failed, 468 passed in 63.92s (0:01:03) | other than repo test: 1 ['test_scratch_dir_bad_lines[N10-wrong-id]']
C5: 1 failed, 468 passed in 65.42s (0:01:05) | other than repo test: 1 ['test_scratch_dir_cutoff_boundary[FROM]']
C6: 2 failed, 467 passed in 64.28s (0:01:04) | other than repo test: 2 ['test_scratch_dir_good_lines[P2-no-scratchpad-trailing-slash]', 'test_scratch_dir_real_mkdtemp_name']
C7: 1 failed, 468 passed in 61.90s (0:01:01) | other than repo test: 1 ['test_scratch_dir_bad_lines[N5-empty-reason]']
C8: 1 failed, 468 passed in 61.76s (0:01:01) | other than repo test: 1 ['test_scratch_dir_bad_lines[N8-relative]']
C9: 3 failed, 466 passed in 59.67s | other than repo test: 3 ['test_unreadable_06', 'test_unreadable_05_at_suite_check', 'test_scratch_dir_unreadable_05_not_checked']
H: 21 failed, 487 passed in 71.62s (0:01:11) | other than repo test: 21 ['test_unfilled_template_suite_line_is_incomplete', 'test_unreadable_06', 'test_unreadable_05_at_suite_check', 'test_scratch_dir_bad_lines[N1-fixed-path]', 'test_scratch_dir_bad_lines[N2-mktemp-shape]', 'test_scratch_dir_bad_lines[N3-agent-not-i2]', 'test_scratch_dir_bad_lines[N4-no-line]', 'test_scratch_dir_bad_lines[N5-empty-reason]', 'test_scratch_dir_bad_lines[N7-9-chars]', 'test_scratch_dir_bad_lines[N8-relative]', 'test_scratch_dir_bad_lines[N9-template-placeholder]', 'test_scratch_dir_bad_lines[N10-wrong-id]', 'test_scratch_dir_bad_lines[N11-only-in-fence]', 'test_scratch_dir_bad_lines[N12-trailing-text]', 'test_scratch_dir_bad_lines[one-bad-of-two]', 'test_scratch_dir_06_is_tied_to_i3', 'test_scratch_dir_cutoff_boundary[FROM]', 'test_scratch_dir_unreadable_05_not_checked', 'test_scratch_dir_no_anchor_env_is_strict', 'test_scratch_dir_gate_follows_rule_file_of_05_commit[G-not-seen]', 'test_scratch_dir_gate_follows_rule_file_of_05_commit[G-seen]']
```
At 1f27ce7 the repo test passes in the unmutated tree, so the counts are one lower than 05's (05 ran at 13fb139, where the repo test failed every time). A1-A4, B1-B2, C1-C6 are the plan's mutants, written by me from 04's descriptions (not copied from I2's driver); all 13 fail >= 1 test. My B3 maps only an empty-stdout failure to none (stdout tested first), so it is caught by (e) and the all-fail test rather than (c); I2's B3 form is caught by (c). C7 (blank `none ()` reason accepted), C8 (`is_absolute` dropped), C9 (unreadable file skipped silently) are my own extras, each caught. H is the Deviation 2 check above.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 762c8ec 1f27ce7 -- ccbot/ config/ data/` is empty; files changed: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/agents/i3-verifier.md, .claude/commands/run-item.md, scripts/check_pipeline.py, templates/build-report.md, templates/verification.md, tests/test_pipeline_check.py, tests/test_real_data_field.py; none is in TRIGGER or TRIGGER_DIRS)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-009, RI-012 (RI-001 ESCALATED: feasibility re-run, STASH 0 entries here today and fixtures 1/0/fail/1 pass; the 3-of-8 shape count re-derived with the basename rule; census 50 -> 51 matches the test; SCRATCH_FROM touches 0 earlier items (check_pipeline shows no new INCOMPLETE). RI-010 ESCALATED: the new duties are in the agent text (pinned, A2/A4 killed) and enforced where a check can exist; this 06 carries its own Scratch dir line. RI-014 OPEN: the one new git read goes through `_git_ok`, a failed read is never none (B2 killed), the shallow cases are measured fixtures. RI-002: no default added or removed; B2 is the fail-open probe. RI-009: this item; scratch dir from mkdtemp, `--detach` worktree inside it, no stash. RI-012: decided by exit code; anchored fullmatch with in-text negatives N7/N12)
RI-009: guardrail built (097), STASH line + Scratch dir INCOMPLETE check; all plan mutants killed on I3's re-run. RI-010: guardrail extended (097); status unchanged (its own GUARDED condition is 086 on main).

## Pipeline line (step 2)
check_pipeline line: `097: awaiting A1 (FULL)`

## Sent back / sent to Audit
Sent to Audit: work/097/07-audit-task.md. Person's OK needed at PR review (RULE_PATHS touched; option (i) reading).
