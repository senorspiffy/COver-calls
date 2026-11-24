# 02 Improvements - 098
## What past logs say
- logs/audit/2026-11-22-091.md is the source for sub-asks 1-3. L10-15: all 4 helper commits of 091 were amended for trailers, with equal trees and parents. L54-58: a-resolvename, a-nocwd and a-from93 survive. L63-65: a-nocwd is still refused, but as `05.md not found`; a-from93 survives because the fixtures use 150 and 091. L70 and L78: `## Round 2 build` (076/05) is a residual, and the rule text is broader than the check. L74: N1's root cause is "04's mutant list had one row per behaviour but not one per refusal condition and per cutoff constant".
- logs/audit/2026-11-21-088.md finding 3 and 091 N6 (L79): the `not checked (unborn HEAD)` label is also printed for a corrupt or dangling HEAD. On this branch the `_anchor_env` docstring (scripts/check_pipeline.py L795-805) already says "exit 1 means HEAD names no commit: unborn, or a ref git can't resolve ... 128 measured ... the label is not accurate for the second". So only the label (L816, module text L327-328) and the missing corrupt-ref test remain, as 01 finding 4.5 says. Grep "unborn HEAD" outside work/ matches only scripts/check_pipeline.py, tests/test_pipeline_check.py and 4 audit logs. No agent or command file quotes the label.
- RI-010 (logs/recurring-issues.md L119) lists "`## Round 2 build` headings, commit_step trailer → 098" as near misses, not counted. RI-010 is ESCALATED. Its root cause (L120) is duties that exist only in agent text with no check, which bears on the "one mutant per condition" rule (AGAINST 3). RI-014 is OPEN (L153) and covers sub-ask 4.
- RI-001 (L7-17): a rule is written without measuring how many cases it hits. This bears directly on sub-ask 3 (AGAINST 1).
- The amend is not in any rule file. Grep for `amend|trailer|census|commit-tree` over run-item.md, i2-builder.md, i3-verifier.md, scripts/commit_step.py and tests/test_commit_step.py matches only commit_step.py L25 and L188. So the trailers come from the session's commit-attribution instruction, not from repo rules, and the helper must take arbitrary trailers rather than hard-code any. Removing the amend changes no run-item text (01 open question 2: there is nothing to drop). tests/test_commit_step.py has no git-call census.
- Precedent: 091/02 FOR 1 pinned undocumented git behaviour inside the test, so a git upgrade names the cause instead of failing on a changed message. 091/02 AGAINST 3: a bundle shares one I3 verdict, so build tests-only parts first.
- Parallel work in this checkout: open requests 093 (`test_pipeline_check.py`, LOG BATCH waiver) and 097 (`check_pipeline (or a test)` flags `git stash list`) touch the same files as sub-asks 2-4 (Grep of work/09[2-7]/request.md). Per RI-014's 2026-11-22/24 notes, 094/095 sit in the clone-depth code.
- Nothing was run: this R2 has no shell. Code facts come from reading scripts/commit_step.py L85-217 and scripts/check_pipeline.py L399, L434-435, L568-582, L795-817, L1231-1280 on daily-fixes/2026-11-24.

## 3 ways FOR
1. **Sub-ask 1: one extra `-m` paragraph holding every trailer, checked before anything is written, with no new git call.**
   - Design. Parse `--trailer "<Key>: <value>"` (repeatable) out of argv before the ID / subject / paths split (L209-213). Build the call as `commit-tree <tree> -p <old> -m <subject> -m "<t1>\n<t2>..."`. commit-tree makes each `-m` "its own paragraph" in order (01 finding 1.2), and the trailer block is the last paragraph (01 finding 1.5). So a single joined final `-m` gives subject, a blank line, then a block made only of trailers, which meets condition (i) "is all trailers". The subject paragraph is unchanged, so the item-082 check at L170 still compares the same text (01 finding 1.11).
   - Why not `git interpret-trailers`. It would add a process and make the output depend on `trailer.*` config (duplicate-dropping and placement, 01 finding 1.8). This repo's config was not read (UNVERIFIED), and a config-dependent message is harder to pin.
   - Refusals (exit 2, nothing written), checked before the temp index is made:
     - key not `[A-Za-z0-9-]+` (01 finding 1.4);
     - no `": "` separator;
     - empty value;
     - a value containing `\n` or `\r`, which would split the block.
   - Tests in a fixture repo:
     - (a) two trailers read back with `git log -1 --format=%(trailers:key=<k>,valueonly)` for each key, `%s` == subject, and the tree equal to a no-trailer run on the same input (01 finding 1.12);
     - (b) each refusal with `git rev-parse HEAD` unchanged;
     - (c) no `--trailer` gives the same `%B` as today.
   - Mutants:
     - each trailer in its own `-m`: (a) fails, assuming git reads only the last paragraph as the block (01 finding 1.6, UNVERIFIED until run, so I3 must run it);
     - trailers dropped;
     - each validation removed.

2. **Sub-ask 2: kill each named mutant with a test that asserts the exact result, and split the two-condition `or`.**
   - a-from93: parametrize the existing round-heading fixture over `("092", flagged)` and `("091", not flagged)` instead of only RH_ID 150. The fixture repo must have `ROUND_HEADING_FROM = ` in RULE_FILE at the commit that adds the step file. Otherwise `_rule_seen` (L977) gives RULE NOT SEEN, and the 092 case would pass for the wrong reason.
   - a-nocwd: L142 is two refusal conditions in one `or`: `topdir is None` (show-toplevel failed) and `topdir != cwd`. Under the "one mutant per refusal condition" rule they need two tests, both asserting the `not the top of a git work tree` message on stderr, exit 2 and HEAD unchanged:
     - (i) run from `work/150` with `monkeypatch.chdir` (01 finding 2.10). This kills a-nocwd, because the mutant's message is `not found` (091 audit L63).
     - (ii) a patched `run` whose `rev-parse --show-toplevel` returns exit 128. This kills a mutant that drops `topdir is None`.
   - a-resolvename: name `work/150/lnk.md -> real.md`, where `work/150/real.md` is also in the repo. Assert that `git ls-tree HEAD work/150/lnk.md` shows mode `120000` (01 finding 2.9 and its Numbers line). Under `a.resolve()` the named path becomes `work/150/real.md`, so the link is never staged and the assert fails.
   - Use a non-log target rather than a link to a log file. With a log target the mutant is refused by L159 (01 finding 2.8), so the test would only check "some refusal" and not the docstring's positive promise ("a named symlink stays a symlink", L91-92).

3. **Sub-ask 4: a neutral label, a corrupt-ref fixture, and git's exit codes pinned in the test. No new git call.**
   - `rev-parse --verify -q` documents only "non-zero" (01 finding 4.1). The branch docstring records exit 1 for both an unborn HEAD and an unresolvable ref (L801-803). So at the one HEAD read that `_anchor_env` makes, the two cases cannot be told apart.
   - Telling them apart needs extra reads (01 finding 4.4), which changes `test_git_call_census` (088). With 093/094/095/097 open in the same file, that number is likely to move under parallel edits.
   - So: change L816 to a label true for both, e.g. 088 A1's `HEAD names no commit (unborn or unresolvable)` (logs/audit/2026-11-21-088.md L98-105). Update the module text L327-328, the docstring's last sentence, and the two pins (tests/test_pipeline_check.py L2399, L2858-2879, 01 finding 4.6).
   - Add the corrupt-ref fixture 088 A1 asked for. Write garbage into `.git/refs/heads/<branch>` and assert three things: the new `RULE NOT SEEN: not checked (...)` text, UNCOMMITTED STEP failed, and exit 1.
   - Inside the same test, pin the environment: `rev-parse --verify -q HEAD` returncode == 1, and `git ls-tree HEAD` returncode != 0. 128 is expected, because the git API docs say `die` "exits with status 128" (01 finding 4.2). Assert `== 128` only as a separate pin with a message naming the git version. If git changes the code, the failure then names the cause.
   - Mutants: old label restored (pins fail); `head[1] == 1` changed to `head[1] in (1, 128)` (fixture fails if git ever returns 128 here); corrupt-ref branch dropped.

## 3 ways AGAINST
1. **Sub-ask 3 as written ("any SUMMARY_LINE outside the read sections is INCOMPLETE") may flag legitimate quoted runs, and neither cheap alternative has been measured.**
   - `_run_seconds` counts summary lines inside fences too (L1234-1235, "pytest output is usually fenced"). So "outside fences" cannot be the exemption: quoted runs in Deviations, Evidence or mutant notes are fenced the same way as real runs.
   - R1's approximate Grep found 345 summary-like lines in 78 files, with no inside/outside split (01 finding 3.4, UNVERIFIED split).
   - Items >= 092 have no 05/06 yet, so the rule's effect on its own range cannot be measured on real files, only on 076-091 retroactively (RI-001).
   - The narrower option also has a cost: widening STRAY_RUN_HEADING to any `Round N` heading. My Grep of `^#{1,6} [Rr]ound \d+` over work/*/0[56]-*.md lists 39 headings in 25 files of 13 items (061-091). Count method: Grep tool listing, counted per line.
   - These are mostly round-wrapper headings such as `## Round 2 (2026-11-21, I2)`, a normal pattern in sent-back items. Many of them likely hold read `Test output` subsections, but that is UNVERIFIED because `_section_flags` was not run on them.
   - Only 076/05 L6 `## Round 2 build` is the known case, and it is below 092.
   - Mitigation: I2 step 0 runs `_section_flags` over 076-091 under the proposed rule and pastes the flagged list before the rule is fixed. If the list holds anything other than 076/05 L6 and its runs, choose a rule that exempts named sections (Deviations, Mutations, Evidence) or one keyed on round headings that contain a SUMMARY_LINE outside a read subsection. Gate it with its own FROM, or reuse 92 only if the measured list is empty for 092-097 once they have 05/06.

2. **The bundle changes the helper this item uses to commit its own steps, and it shares check_pipeline.py / test_pipeline_check.py with 093, 097 and the clone-depth items.**
   - 098's own I2/I3 log commits go through scripts/commit_step.py (run-item rule, 091 audit L25). A bug in the new argv parsing (e.g. `--trailer` read as a path, today's behaviour per 01 finding 1.13) would make this item's own step commits fail or carry a malformed message. That is the same failure 091 exists to stop, but now in the tool itself.
   - One I3 FAIL on sub-ask 3 (the unmeasured one) also sends back sub-asks 1, 2 and 4 under the 3-loop cap (091/02 AGAINST 3).
   - Mitigations:
     - build order: sub-ask 2 first (tests only), then 4, then 1 (commit_step, tested in fixture repos only), then 3;
     - the first real `--trailer` commit of this item is checked by I3 with `%(trailers)` and `%s`;
     - rebase on any of 093/094/095/097 that merges first, and re-read line numbers and the census total before writing fixtures (run-item one-after-another rule for shared code files, 01 open question 6).
   - If sub-ask 3 fails twice, split it into its own item rather than hold the other three.

3. **"One mutant per refusal condition and per `*_FROM` boundary" is a larger scope than the three named mutants, and as a rule it is another unchecked prose duty.**
   - 01 finding 2.11 lists about 20 refusal conditions in commit_step alone (not totalled by hand), plus 8 numeric `*_FROM` constants in check_pipeline.py (01 finding 2.2).
   - Applying the rule to all of them now means writing and running mutants for each, which is far beyond "add tests for three survivors". Which constants already have FROM / FROM-1 pins was not checked (01 finding 2.2).
   - Writing the rule only into i1-planner (or R2-c) repeats RI-010's root cause: a sentence an agent can skip, with nothing to check it. It is also a RULE_PATHS edit that needs the person's OK at PR review (091 audit L18).
   - Mitigation:
     - 098 kills the three named mutants plus the second `or` condition (FOR 2);
     - I1 lists, from tests (not by hand), which of the 8 FROM constants lack a FROM / FROM-1 pin, and adds only those pins, or opens a follow-up item if more than a few lack them;
     - 05 says plainly that the planner rule is text-only and names why no script can check "a mutant was run".

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 098 is an EFFICIENCY item inside this repo's commit helper and pipeline checker: an argv option, test fixtures, a label string and a docstring. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git and Python tool behaviours, already cited by R1 to official docs (git-scm.com commit-tree, interpret-trailers, rev-parse, api-error-handling; docs.python.org os.path, pathlib; docs.pytest.org monkeypatch) and pinned in-test (FOR 1, FOR 3). Precedent: 081-091 and 093, all logged `languages: N/A` (logs/research/2026-11-20 to 2026-11-24).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no new external claims) | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |

## Holes to watch out for (summary)
- Sub-ask 1:
  - Put all trailers in one final `-m`, never one `-m` each (01 finding 1.6; I3 must run the split mutant, since git's treatment of earlier one-line paragraphs is UNVERIFIED).
  - Refuse bad keys, missing `": "`, empty values and values with CR/LF before the temp index is made. Every refusal leaves HEAD and the shared index unchanged.
  - Parse `--trailer` before the positional split, or it becomes a path refused as `not found` (01 finding 1.13).
  - Keep the reflog message `commit_step: <subject>` (L189) and the L170 subject check on the subject only.
  - Do not hard-code the attribution trailers: they come from the session's instructions, not repo rules (Grep: no `trailer` in run-item/i2/i3).
- Sub-ask 2:
  - The 092 pin needs `ROUND_HEADING_FROM = ` in RULE_FILE at the adding commit, or it reads RULE NOT SEEN and passes for the wrong reason.
  - L142 has two conditions: give each its own test and assert the exact `not the top` message, not only exit 2.
  - Use a non-log symlink target, so the a-resolvename test checks mode 120000 and not just "some refusal".
  - In-process tests need `monkeypatch.chdir`.
- Sub-ask 3:
  - Fenced lines are counted by `_run_seconds`, so fences cannot be the exemption.
  - Measure with `_section_flags` over 076-091 before fixing the rule.
  - `Round N` wrapper headings are common (39 in 25 files), so a heading-shape rule alone will over-flag unless it requires an unread SUMMARY_LINE under the heading.
  - 076 < 92: must not be flagged.
- Sub-ask 4:
  - No new git call (census).
  - Change the label in all four places: L816, module text L327-328, the docstring, and the pins at L2399 and L2858-2879.
  - The corrupt-ref fixture asserts RULE NOT SEEN text, UNCOMMITTED STEP failed and exit 1.
  - Pin git's exit codes in the test, with `== 128` as a separate, named pin.
- Build order: 2, 4, 1, 3. Rebase on 093/094/095/097 if they merge first. check_pipeline.py, i1-planner and any run-item text are RULE_PATHS, so the person's OK is needed at PR review.

Log fields: 3 for / 3 against | languages: N/A
