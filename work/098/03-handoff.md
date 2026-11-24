# 03 Research hand-off - 098
Status: READY
Scope note: sub-ask 3 is **narrowed**. 098 will not build the broad "any SUMMARY_LINE outside a read section is INCOMPLETE" rule, because nobody can measure it safely here. Measuring it needs `_section_flags` run over the 076-091 05/06 files, and R3 has no shell. There are 345 summary-like lines in 78 files, and 076/05 alone has 14, many of them outside read sections. 098 instead builds a heading rule for `## Round N build`, with its own cutoff (step 6). That rule's hit count was measured (Feasibility). The broad rule is a follow-up item (Residuals).

Recurring issues checked (item 013): RI-001 (ESCALATED) is covered by the Feasibility column: the heading rule matches 1 line in the whole repo, and that line is below the cutoff; the trailer key filter passes both of the session's trailers. RI-010 (ESCALATED): N2 and N5 are this item's near misses. Every new refusal and cutoff gets its own mutant (steps 1-7), and the "no amend" check runs on 098's own commits (step 9). RI-014 (OPEN): the HEAD label is fixed in step 5 with no new git call, so the census sum stays 47. GUARDED entries were also checked:
- RI-002: an absent or bad input is never filled in (Missing inputs).
- RI-004/005: Self-check below.
- RI-006: counts are left to check_handoff.
- RI-007: Scope is FULL and code is allowed.
- RI-009: build in a scratch worktree; rebase on 093/094/095/097 if they merge first.
- RI-012: anchored `.match`/`fullmatch` with negative tests in steps 6 and 1.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 1.1 commit-tree synopsis has no `--trailer` | https://git-scm.com/docs/git-commit-tree | VERIFIED | |
| 01 1.2 each `-m` is its own paragraph; -m/-F any number, any order, composed in order | https://git-scm.com/docs/git-commit-tree | VERIFIED | |
| 01 1.3 message from stdin unless -m/-F; `-F -` reads stdin; each -F own paragraph | https://git-scm.com/docs/git-commit-tree | VERIFIED | |
| 01 1.4 trailer = key-value with colon; key ASCII alnum + `-`; block preceded by blank line | https://git-scm.com/docs/git-interpret-trailers | VERIFIED | |
| 01 1.5 block at end of message; (i) all trailers or (ii) >=25% with a git/configured trailer | https://git-scm.com/docs/git-interpret-trailers | VERIFIED | |
| 01 1.6 one `-m` per trailer leaves only the last in the block (inference, part UNVERIFIED) | git-commit-tree + git-interpret-trailers docs | UNSUPPORTED (the "earlier paragraphs" part) | Kept only what the docs say: each -m is a paragraph, and the block is at the end. The design does not rely on the unverified part. The split-`-m` mutant (step 1 M1a) must be run, and its result goes in 05 |
| 01 1.7 interpret-trailers `--trailer` repeatable, appended after existing; stdin when no file; `fix=42` example | https://git-scm.com/docs/git-interpret-trailers | VERIFIED | |
| 01 1.8 only `:` by default, `=` always on command line; `trailer.*` config controls dedupe/placement | https://git-scm.com/docs/git-interpret-trailers, https://git-scm.com/docs/git-commit | VERIFIED | |
| 01 1.9 `git commit --trailer` exists; commit_step uses temp index + commit-tree + update-ref (L172-189) | https://git-scm.com/docs/git-commit; scripts/commit_step.py L172-189 | VERIFIED | |
| 01 1.10 `--only` with `--amend` needs no paths; 091 A1 tree-equal reflog pairs | https://git-scm.com/docs/git-commit; logs/audit/2026-11-22-091.md L10-15 | VERIFIED | |
| 01 1.11 text up to first blank line is the title, so L170 subject check unchanged | https://git-scm.com/docs/git-commit; commit_step.py L170 | VERIFIED | |
| 01 1.12 `%(trailers:key=..,valueonly)` (case-insensitive key), `%s`, `%B` | https://git-scm.com/docs/pretty-formats | VERIFIED | |
| 01 1.13 commit-tree call at L188; main argv split L209-213; `--trailer` would be a path refused at L161 | scripts/commit_step.py L161, L188, L209-213 | VERIFIED | |
| 01 2.1 round-heading fixtures use RH_ID 150 and 091; ROUND_HEADING_FROM = 92 (L399, L968); 092 unpinned | tests/test_pipeline_check.py L4511, L4561; scripts/check_pipeline.py L399, L968 | VERIFIED | |
| 01 2.2 FROM constants 41/45/76/87/90/92/70/71 + UNTRACKED_FROM SHA | Grep `^[A-Z_]+_FROM = ` check_pipeline.py L385-467 | VERIFIED | |
| 01 2.3 a-nocwd: run from work/150 refused as `not found`; no test asserts `not the top` from a subdir | logs/audit/2026-11-22-091.md L42, L55, L63; commit_step.py L142, L161 | VERIFIED | |
| 01 2.4 lexists true for broken links; isdir follows links | https://docs.python.org/3/library/os.path.html | VERIFIED | |
| 01 2.5 abspath = normpath(join(getcwd, path)) on most platforms; normpath may change symlink meaning | https://docs.python.org/3/library/os.path.html | VERIFIED | |
| 01 2.6 resolve() resolves symlinks, non-strict "as far as possible"; relative_to raises ValueError | https://docs.python.org/3/library/pathlib.html | VERIFIED | |
| 01 2.7 repo_relative resolves only the parent (L95); no test; P1 shows mode 120000 staged | commit_step.py L95; logs/audit/2026-11-22-091.md L32-34, L44, L65 | VERIFIED | |
| 01 2.8 under a-resolvename a link to a log file hits L159 (inference, not run) | commit_step.py L95, L159 | UNSUPPORTED | Removed: not run. The map uses a non-log target (step 4), so the map does not need this claim |
| 01 2.9 index object type 1010 = symlink, permission 0 | https://git-scm.com/docs/gitformat-index | VERIFIED | |
| 01 2.10 monkeypatch undoes changes after the test; chdir changes cwd during a test; fixture uses it L55 | https://docs.pytest.org/en/stable/how-to/monkeypatch.html; tests/test_commit_step.py L55 | VERIFIED | |
| 01 2.11 refusal conditions list, incl. "topdir None and topdir != cwd: two conditions" | scripts/commit_step.py L71-195 | WRONG (in part) | L142 has two conditions, but dropping `topdir is None or` gives an equivalent mutant: `None != Path(...)` is True, so the refusal and its message are the same. The case is already pinned by test_t3_no_git_and_not_a_repo L194-196. The HEAD-moved refusal is at L194 (L193 is the `if`). Recorded as an equivalent mutant (step 3) |
| 01 3.1 STRAY_RUN_HEADING (L434, .match, re.I) misses `## Round 2 build`; `#{1,2} ` closes a section (L1261) | scripts/check_pipeline.py L433-434, L1252-1266 | VERIFIED | |
| 01 3.2 076/05 L6 is the only `## Round 2 build` line in work/; 076 < 92 | Grep `^#{1,6} round \d+ build\b` -i, whole repo: 1 line | VERIFIED | |
| 01 3.3 reuse ROUND_HEADING_FROM or a new FROM: open | 091 audit L78; check_pipeline.py L977 | UNSUPPORTED (left open) | Decided: a new constant `ROUND_BUILD_FROM = 99` gated by `_rule_seen`, so an item built in parallel before 098 merges is never judged by a rule it could not see (item 084). The broad SUMMARY_LINE rule is dropped from 098 (scope note) |
| 01 3.4 approx SUMMARY_LINE grep: 345 lines in 78 files; in/out split unmeasured | Grep count over work/*/0[56]-*.md (re-run by R3: 345 in 78) | VERIFIED | |
| 01 4.1 rev-parse `-q` "exit with non-zero status silently"; no number given | https://git-scm.com/docs/git-rev-parse | VERIFIED | |
| 01 4.2 die exits 128, usage 129; fits 088 A1's measured 128 | https://git-scm.com/docs/api-error-handling; logs/audit/2026-11-21-088.md L71-78 | VERIFIED | |
| 01 4.3 symbolic-ref exit 0/1/128; nothing on a dangling target | https://git-scm.com/docs/git-symbolic-ref | VERIFIED | |
| 01 4.4 unborn and dangling/corrupt HEAD look the same at the one HEAD read (inference) | logs/audit/2026-11-21-088.md L71 | UNSUPPORTED (as inference) | 088 A1 measured it: a corrupt `refs/heads/main` and a dangling symbolic HEAD both make `rev-parse --verify -q HEAD` exit 1. Now a measured fact, and step 5 pins it in-test |
| 01 4.5 `_anchor_env` docstring already fixed in 091; label L816 and module text L327-328 remain | scripts/check_pipeline.py L795-817, L327-329 | VERIFIED | |
| 01 4.6 tests pinning the label: L2858-2879 and "the parametrize row at L2399" | tests/test_pipeline_check.py L2398-2399, L2874-2879 | WRONG (in part) | L2398-2399 is a GIT_CENSUS reason string, not a label pin; it may stay. The pins are L2874 (RULE NOT SEEN text) and L2877 (`_anchor_env()`). L2878-2879 pass the old string as `env`. The comment at check_pipeline.py L1827 also names it (step 5) |
| 01 Numbers: mode 120000 = 0b1010 << 12 = 40960 = octal 120000 | gitformat-index; Self-check | VERIFIED | |
| 01 Numbers: boundary pins F and F-1 → 92 and 91 | check_pipeline.py L399 | VERIFIED | |
| 01 Numbers: 345 / 78 are Grep tool counts | Grep count (R3 re-run) | VERIFIED | |
| 02 past logs: 091 audit L10-15, L54-58, L63-65, L70, L74, L78 say what R2 cites | logs/audit/2026-11-22-091.md | VERIFIED | |
| 02 past logs: docstring state; "unborn HEAD" outside work/ only in check_pipeline, its test and 4 audit logs | Grep `unborn HEAD` !work/**: check_pipeline.py, test_pipeline_check.py, logs/audit 2026-11-20, -21-084, -21-088, -22-091 | VERIFIED | |
| 02 RI-010 ESCALATED with 098 near misses; RI-014 OPEN | logs/recurring-issues.md L109-158 | VERIFIED | |
| 02 amend/trailer absent from run-item, i2, i3, commit_step tests; only commit_step L25, L188 | Grep `amend|trailer|commit-tree` over those 5 files | VERIFIED | |
| 02 093 (test_pipeline_check.py) and 097 (check_pipeline) touch the same files | work/093/request.md L9; work/097/request.md L12 | VERIFIED | |
| 02 FOR 1: one final joined `-m` gives an all-trailer last paragraph (condition (i)); subject unchanged | git-commit-tree, git-interpret-trailers, git-commit docs | VERIFIED | |
| 02 FOR 1: interpret-trailers output depends on `trailer.*` config | https://git-scm.com/docs/git-commit (--trailer text) | VERIFIED | |
| 02 FOR 1: refusals (bad key, no `": "`, empty value, CR/LF) before the temp index | design; commit_step.py L152-171 (refusals before L172) | VERIFIED | Step 1 adds one more refusal: `--trailer` with no value. Options come only before the ID |
| 02 FOR 1: tests (a)-(c) and mutants (split -m, dropped, each validation removed) | pretty-formats; design | VERIFIED | The split-`-m` result must be run (row 01 1.6) |
| 02 FOR 2: 092 pin needs `ROUND_HEADING_FROM = ` in fixture RULE_FILE, else RULE NOT SEEN | tests/test_pipeline_check.py L4590-4607; check_pipeline.py L977-980 | VERIFIED | |
| 02 FOR 2 (i): subdir-cwd test asserting `not the top` kills a-nocwd | 091 audit L42, L63 | VERIFIED | |
| 02 FOR 2 (ii): patched show-toplevel exit 128 test "kills a mutant that drops `topdir is None`" | commit_step.py L141-143; tests/test_commit_step.py L189-196 | WRONG | That mutant is equivalent (`None != Path` is True; same message), so no test can kill it. The existing L194-196 already asserts the message. 05 records it as equivalent, with no new test |
| 02 FOR 2: a-resolvename via `work/150/lnk.md -> real.md`, assert mode 120000; non-log target | gitformat-index; commit_step.py L89-97 | VERIFIED | |
| 02 FOR 3: separating cases needs extra git reads, which changes the census | tests/test_pipeline_check.py L2419-2436 (static call-site count, sum 47) | VERIFIED | |
| 02 FOR 3: change the label in L816, L327-328, docstring, pins L2399 and L2858-2879 | check_pipeline.py L328, L799, L805, L816, L1827; tests L2874-2879 | WRONG (in part) | The list is L328, L799/L805 docstring, L816, L1827 comment, tests L2874, L2877-2879. L2399 is a census reason, not a pin (row 01 4.6) |
| 02 FOR 3: corrupt-ref fixture; pin rev-parse returncode 1, ls-tree != 0, `== 128` as a separate named pin | api-error-handling; 088 audit L71-78 | VERIFIED | |
| 02 FOR 3 mutant: `head[1] == 1` → `in (1, 128)` "fails the fixture" | 088 audit L71 (git returns 1 here) | WRONG | Removed: it cannot fail while git returns 1, so it is an equivalent mutant, not a kill. The env pin (row above) covers a git change |
| 02 FOR 3 mutant: "corrupt-ref branch dropped" | step 5 design (label only, no branch) | UNSUPPORTED | Removed: the neutral-label design adds no corrupt-ref branch to drop |
| 02 AGAINST 1: `_run_seconds` counts summary lines inside fences too, so fences can't be the exemption | check_pipeline.py L1231-1249 | VERIFIED | |
| 02 AGAINST 1: 39 `Round N` headings in 25 files of 13 items (061-091) | Grep `^#{1,6} [Rr]ound \d+` over work/*/0[56]-*.md (R3 re-run: 39 lines; 2+1+4+4+4+3+3+2+2+8+2+2+2) | VERIFIED | |
| 02 AGAINST 1: items >= 092 have no 05/06 yet | Glob work/09[2-9]/*: only request, 01, 02, 093/03 | VERIFIED | |
| 02 AGAINST 2: 098's own step commits go through commit_step; build order 2, 4, 1, 3 | run-item rule (091 audit L25, L68) | VERIFIED | |
| 02 AGAINST 3: the rule over all ~20 commit_step refusals and 8 FROM constants is a larger scope | commit_step.py; check_pipeline.py L385-441 | VERIFIED | Map narrows it: the rule applies to the conditions and cutoffs 098 adds or touches. The rest is a follow-up |
| 02 Languages N/A: only official English tool docs | the 10 URLs above | VERIFIED | |
**Totals:** 61 rows checked → **51 VERIFIED as-is**, **7 fixed**, **3 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
1. 01 finding 2.8: "under a-resolvename a symlink to a log file hits the L159 refusal". Not run, and not needed, because step 4 uses a non-log target.
2. 02 FOR 3 mutant `head[1] in (1, 128)`. It is equivalent while git exits 1, so it cannot fail a test.
3. 02 FOR 3 mutant "corrupt-ref branch dropped". The design adds no such branch.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/commit_step.py: leading `--trailer "<Key>: <value>"` options (repeatable, only before `<ID>`) are parsed in `main` before the positional split. They are validated before `rev-parse` and the temp index: key `fullmatch [A-Za-z0-9-]+`, separator `": "` (first occurrence), value non-empty after strip, no `\r`/`\n`. A `--trailer` with no next argument gets usage and exit 2. When valid, `commit-tree ... -m <subject> -m "<t1>\n<t2>..."` (one final paragraph). With no trailer, the call is byte-identical to today's. Usage line and module docstring (v) updated. Reflog `commit_step: <subject>` and the L170 subject check stay unchanged | argv; fixture repo of tests/test_commit_step.py | commit message `<subject>\n\n<t1>\n<t2>\n` | tests/test_commit_step.py: (a) 2 trailers → `git log -1 --format=%(trailers:key=<k>,valueonly)` gives each value; `%s` == subject; tree == a no-trailer run's tree. (b) each of the 5 refusals: exit 2, reason in stderr, `_state` (HEAD + .git/index bytes) unchanged; negative key `Co Authored` (space) and `Key:value` (no space) refused. (c) no `--trailer`: `%B` == `subject\n` as today. Mutants, one per condition: M1a each trailer in its own `-m` (expected: (a) fails, result pasted in 05), M1b trailers dropped, M1c-M1g each of the 5 validations removed | Trailer key filter: 2 of 2 session trailers pass (`Co-Authored-By`, `Claude-Session`, Self-check row 3); 0 of 2 negative fixtures pass |
| 2 | tests/test_pipeline_check.py: parametrize the round-heading INCOMPLETE fixture over item `092` (flagged) and `091` (not flagged). The fixture RULE_FILE holds `ROUND_HEADING_FROM = 92` at the adding commit, as at L4596 | `_rh_item(item=...)` | INCOMPLETE line for 092, none for 091 | Mutant a-from93 (`ROUND_HEADING_FROM = 93`) fails the 092 case; a-from91 fails the 091 case | 2 boundary IDs (92, 91) from L399 |
| 3 | tests/test_commit_step.py: run `_cli` with `cwd=repo/work/150` and path `work/150/05-build-report.md` | `repo` fixture | exit 2; stderr has `not the top of a git work tree`; `_state` unchanged | Mutant a-nocwd (drop `topdir != Path.cwd().resolve()`) fails it, because the mutant's reason is `not found`. 05 records the `topdir is None` drop as an equivalent mutant, with the reason (Self-check row 5) and the existing pin L194-196 | – |
| 4 | tests/test_commit_step.py: `work/150/real.md` committed, then `work/150/lnk.md -> real.md` (relative symlink) named | `repo` fixture | HEAD has `lnk.md` as a link | `git ls-tree HEAD work/150/lnk.md` mode `120000`, `git cat-file -p HEAD:work/150/lnk.md` == `real.md`. Mutant a-resolvename (`a.resolve()`) fails it, because the link is never staged | – |
| 5 | scripts/check_pipeline.py: L816 returns `"HEAD names no commit: unborn or unresolvable"`. Update the module text L328, the docstring L799 and L805 (last sentence now: the label covers both), and the comment L1827. No new git call | `_anchor_env` | `RULE NOT SEEN: not checked (HEAD names no commit: unborn or unresolvable)` | tests: update L2874 and L2877-2879 to the new text. New `test_rule_anchor_corrupt_ref_is_strict`, parametrized `corrupt` (assert loose `.git/refs/heads/main` exists, then write `garbage\n`) and `dangling` (`git symbolic-ref HEAD refs/heads/nope` after a commit). Env pins: `rev-parse --verify -q HEAD` returncode == 1; `ls-tree HEAD` returncode != 0; a separate `== 128` assert with a message naming `git --version`. Output: the new RULE NOT SEEN text, `UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)`, exit 1. A text pin that the module docstring holds the new label and not `not checked (unborn HEAD)`. `test_git_call_census` unchanged (sum 47). Mutant: old label restored → the pins fail | – |
| 6 | scripts/check_pipeline.py: `ROUND_BUILD_FROM = 99`; `ROUND_BUILD_HEADING = re.compile(r"#{1,6} round \d+ build\b", re.I)` with `.match`. In the L968 loop, from ROUND_BUILD_FROM on, each 05/06 "out" row that matches, is outside the read section (`_section_flags` with RUN_HEADING) and is not inside a fence gives INCOMPLETE `<step> heading '<h>' holds runs LOG BATCH does not read; use '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 098)`. Gated by `_rule_seen(item_dir, step, "ROUND_BUILD_FROM", env)`, so not seen → RULE NOT SEEN `(..., "ROUND_BUILD_FROM", "098", "no round-build check")`. The module help (L184 area) names it | 05/06 text; RULE_FILE at the adding commit | INCOMPLETE entry or RULE NOT SEEN entry | Fixtures: `## Round 2 build` + a summary line at 099 → flagged; the same at 098 → not flagged; 099 with RULE_FILE lacking `ROUND_BUILD_FROM = ` → RULE NOT SEEN, no INCOMPLETE. Negatives (RI-012): `## Round 2 builder notes`, `## Round 2 build` inside a fence, `### Round 2 build` inside `## Test output` → not flagged. Mutants: FROM 100 (099 case fails), FROM 98 (098 case fails), gate removed (RULE NOT SEEN case fails), `\b` dropped (builder case fails), re.I dropped (fixture `## round 2 Build` fails) | Heading rule: 1 of 39 `Round N` headings in work/*/0[56] match (076/05 L6, item 76 < 99, not flagged). 0 of 0 05/06 files at items >= 99 today (Glob work/09[2-9]/*). Whole repo: 1 line (Grep `^#{1,6} round \d+ build\b` -i). Fixture: 1 flagged at 099, 0 at 098 |
| 7 | 05 lists, for each refusal condition and `*_FROM` cutoff 098 adds or touches, its mutant and result: trailer refusals (5), L142 (2 conditions, 1 equivalent), ROUND_HEADING_FROM (92/91), ROUND_BUILD_FROM (99/98). The other 7 FROM constants are out of scope (Residuals) | 04 mutant list | 05 Mutations table | I3 re-runs each mutant listed; every non-equivalent one fails a named test | – |
| 8 | Build order and parallel work: steps 2, 3, 4 (tests only), then 5, then 1, then 6. Re-read line numbers and the census sum after rebasing on any of 093/094/095/097 that merges first | branch state | – | `git log` shows the order. `test_git_call_census` passes after rebase | – |
| 9 | "Commits need no amend": every 098 step commit made after step 1 is built uses `commit_step.py --trailer ...` | 098's own commits | – | I3: for each 098 commit, `git log -1 --format=%(trailers)` holds the session trailers and `%s` == subject; `git reflog --format=%gs` shows `commit_step: <subject>` for it and no `commit (amend)` entry | – |

Residuals (follow-up items for the daily review, not built here):
- (a) The broad N5 rule (a SUMMARY_LINE under any unread heading, e.g. a `## Round 2 (2026-11-21, I2)` wrapper). It needs `_section_flags` run over 076-091 with a shell before its rule is fixed (RI-001).
- (b) FROM / FROM-1 pins for CHECKLIST_FROM, LOG_CHECK_FROM, TESTS_FORMAT_FROM, SUITE_FROM, TIMED_FROM, WHOLE_DIFF_FROM and VERDICT_FROM.
- (c) The "one mutant per refusal condition and per `*_FROM` boundary" sentence in i1-planner. It is a RULE_PATHS edit, needs the person's OK, and is text-only (RI-010 root cause).

check_pipeline.py and the tests are RULE_PATHS, so the person's OK is needed at PR review.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `--trailer` options (commit_step argv) | none given | No trailer paragraph. The message is exactly today's `subject\n`. Nothing is added by default (attribution trailers are never hard-coded) |
| `--trailer` value (argv) | flag last, or value empty/malformed | exit 2, `commit_step refused: trailer ...` naming the bad part; nothing written |
| git `trailer.*` config | not read | Not an input: commit-tree does not apply it, and interpret-trailers is not used |
| RULE_FILE anchor for ROUND_BUILD_FROM (`_rule_seen`) | no git / shallow / unborn or unresolvable HEAD / 05 uncommitted | `(None, "")`: strict, so the numeric cutoff applies and the existing `RULE NOT SEEN: not checked (...)` line is printed |
| same, git call fails | log/ls-tree/show fails | `<step> anchor: git failed (item 084)` entry, exit 1 |
| 05/06 file (stray / round-build check) | absent | no entry (the step's own missing-file checks apply) |
| 05/06 file | unreadable | `<step> round headings not checked (<why>; item 091)`, never `none` |
| HEAD (`_anchor_env`) | rev-parse exit 1 | `HEAD names no commit: unborn or unresolvable`: strict, cutoffs kept |
| HEAD | rev-parse other non-zero | `git rev-parse --verify HEAD failed (exit <n>)`, exit 1 (unchanged) |
| ls-tree exit code in the step 5 env pin | git returns something other than 128 | the separate `== 128` assert fails with `git --version` in its message; never skipped |
| Screen tickers (`ccbot/screen.TESTS`, `MISSING_POLICY`) | n/a | n/a: there is no ticker screen in this item (pipeline scripts only) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 2 boundary pins | flagged iff int(ID) >= ROUND_HEADING_FROM | 92 >= 92 true (flagged); 91 >= 92 false. a-from93: 92 >= 93 false → the 092 pin fails; a-from91: 91 >= 91 true → the 091 pin fails | pass |
| Step 6 boundary pins | flagged iff int(ID) >= ROUND_BUILD_FROM (99) | 99 >= 99 true; 98 >= 99 false. FROM 100: 99 >= 100 false → the 099 case fails; FROM 98: 98 >= 98 true → the 098 case fails | pass |
| Step 1 worked example: session trailer 1 | key fullmatch `[A-Za-z0-9-]+`; `": "` present; value non-empty; no CR/LF | `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`: split at the first `": "` → key `Co-Authored-By` (letters and 2 hyphens) passes; value `Claude Opus 5.5 <noreply@anthropic.com>` is non-empty with no newline | pass |
| Step 1 worked example: session trailer 2 | same | `Claude-Session: https://claude.ai/code/session_...`: first `": "` is after `Claude-Session` (the `:` in `https:` has no following space, and it comes later anyway) → key passes; value is the URL | pass |
| Step 1 message shape | title = text to the first blank line; block = last paragraph, (i) all trailers | `Item 098: <line>\n\n<t1>\n<t2>\n`: title = `Item 098: <line>` = subject, so the L170 check holds; last paragraph = 2 lines, 2 trailers = 100% ≥ condition (i) | pass |
| Step 1 negative keys | the same fullmatch | `Co Authored` has a space, not in the class → refused; `Key:value` has no `": "` → refused | pass |
| Step 3 equivalent mutant | drop `topdir is None or` → `topdir != cwd` | topdir None: `None != Path(...)` → Python falls back to identity → True → same Refused text. So the mutant is equivalent, and L194-196 still pins the text | pass (recorded, no new test) |
| Step 3 kill | real code from work/150: topdir (repo) != cwd (repo/work/150) → `not the top`; mutant: `work/150/05-build-report.md` from the subdir → abspath repo/work/150/work/150/05..., relative `work/150/work/150/05...`, lexists from the subdir false → `not found` | the assert on `not the top` fails under the mutant | pass |
| Step 4 mode | type 1010 in bits 15-12, permission 0 | 0b1010 << 12 = 10 × 4096 = 40960. 40960 = 1 × 32768 + 2 × 4096 → octal 120000 | pass |
| Step 6 feasibility count | sum of `Round N` headings per item | 061:2 062:1 069:4 070:4 076:4 077:3 079:3 081:2 082:2 084:8 086:2 087:2 091:2 = 39; `round N build` matches 1 (076/05 L6) | pass |
| Step 6 negatives | `.match` of `#{1,6} round \d+ build\b`, re.I | `## Round 2 builder notes`: `build` followed by `e`, no word boundary → no match. `## round 2 Build` matches with re.I. A fenced row has state "in", and the check reads only "out" rows | pass |
| Step 5 env pins | git die → 128; rev-parse -q → non-zero (measured 1) | 088 A1 measured: corrupt ref and dangling HEAD → rev-parse 1, ls-tree 128 (088 audit L71-76); api-error-handling: die = 128 | pass |
| Step 5 census | static `_git`/`_git_ok` call sites | label-only change: `("_anchor_env","_git")` stays 2; sum stays 47 (L2398, L2436). Step 6 reuses `_rule_seen`, so no new call site | pass |
| Totals | as-is + fixed + removed = rows | 51 + 7 + 3 = 61 | pass |

`check_handoff output (run by the orchestrator 2026-11-24 18:22 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 61
totals line: 61 rows -> 51 as-is, 7 fixed, 3 removed
PASS
```
