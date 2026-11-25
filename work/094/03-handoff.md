# 03 Research hand-off - 094
Status: READY

Recurring issues checked (item 013), against this file: RI-001 (ESCALATED): the coverage rule has a computed Feasibility count (4 full of 12 shapes, S1-S12) and the exit choice has a test count (3 of 3). RI-010 (ESCALATED): no log line or count typed here, and the check_handoff line is left empty for the orchestrator. RI-014 (OPEN, this item's family): a failed `git config` is an 081 error and is never "none" or "full". Also checked (GUARDED, related): RI-002 (empty output with exit 0, or an origin with no fetch key, is "not checked", never full or none), RI-009 (ID CLASH, IN PR and --next-id never answer from hidden refs), RI-012 (the not-checked text is one constant compared with `==`).

Exit-code decision (deliberate): **main check: exit unchanged** by the single-branch state alone. This follows 090's precedent that not-checked lines never change the exit (tests/test_pipeline_check.py L4450). The three plain `--depth 1` tests (L966, L1067, L2086, `code == 0`) keep their meaning. **`--next-id`: refuses with exit 2** (request). **`check_handoff.py --all`: exit 1** for an item whose 03 is not local, because its documented contract is "Exit 1 on FAIL or not checked" (scripts/check_handoff.py L110) and test h2 (L2602) pins it. A failed `git config` (exit other than 0 or 1) is not this state. It is the 081 error path, with exit 1 for main and exit 2 for --next-id.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1-1 `--single-branch` clones one tip; "Further fetches ... will only update the remote-tracking branch for the branch this option was used for" | https://git-scm.com/docs/git-clone | VERIFIED | – |
| R1-2 `--depth` "Implies `--single-branch` unless `--no-single-branch` is given"; matches F2 d1s | git-clone; logs/audit/2026-11-22-090.md L106-107 | VERIFIED | – |
| R1-3 a normal clone "creates remote-tracking branches for each branch ... (visible using git branch --remotes)" | git-clone DESCRIPTION | VERIFIED | – |
| R1-4 default `fetch = +refs/heads/*:refs/remotes/origin/*`; with no command-line refspec the fetch values "are used as the refspecs" | https://git-scm.com/docs/git-fetch (CRTB) | VERIFIED | – |
| R1-5 refspec, not depth, decides which branches appear (inference from 1 and 4; F2 L110) | git-fetch; audit L110 | VERIFIED | – |
| R1-6 `--unshallow` text is about history only; F2 still `none`/092 after unshallow | git-fetch; audit L108-109 | VERIFIED | – |
| R1-7 the single-branch refspec text is not in the git-clone docs; A1 saw `+refs/heads/main:refs/remotes/origin/main` on git 2.43.0 | git-clone (does not say); audit L30 | VERIFIED | Kept as repo evidence, not a doc claim. The step 8 fixture asserts the value. |
| R1-8 `git branch -r` lists remote-tracking branches; `--no-merged` lists tips "not reachable from <commit>"; both read local refs (L1425, L1861) | https://git-scm.com/docs/git-branch; scripts/check_pipeline.py | VERIFIED | – |
| R1-9 refspec = optional `+`, <src>, `:`, <dst>; a literal `+...` match would miss the no-`+` form | git-fetch | VERIFIED | – |
| R1-10 a pattern refspec "must have one and only one `*` in both" | git-fetch | VERIFIED | – |
| R1-11 `^` negative refspecs; "match if it matches at least one positive refspec, and does not match any negative refspec" | git-fetch | VERIFIED | – |
| R1-12 several fetch lines allowed (Pro Git master + experiment example) | https://git-scm.com/book/en/v2/Git-Internals-The-Refspec | VERIFIED | – |
| R1-13 `git remote add` writes `fetch = +refs/heads/*:refs/remotes/origin/*` | Pro Git Refspec | VERIFIED | – |
| R1-14 `git config get`: "emits the last value"; `--all` "emits all values"; "Returns error code 1 if key is not present" | https://git-scm.com/docs/git-config | VERIFIED | – |
| R1-15 2.46 deprecated mode options; `--get-all` works on 2.43 and current; "still works on current git" UNVERIFIED | RelNotes 2.46.0; git-config DEPRECATED MODES | VERIFIED | Fixed: git-config's DEPRECATED MODES section lists `--get-all <name>` as "Replaced by git config get ... --all", deprecated and not removed. The UNVERIFIED tag is dropped. |
| R1-16 `remote.<name>.fetch` is "The default set of "refspec" for git-fetch" | https://code.googlesource.com/git/+/master/Documentation/config/remote.adoc | VERIFIED | – |
| R1-17 `--mirror` "maps all refs" and "implies --bare"; out of scope (no work tree) | git-clone | VERIFIED | – |
| R1-18 `set-branches` "Change the list of branches tracked"; branches "as if specified with the -t option"; `-t` makes "a refspec to track only <branch>" "instead of the default glob refspec" | https://git-scm.com/docs/git-remote | VERIFIED | – |
| R1-19 `set-branches origin '*'` result and `git config <key> <value>` with several values: UNVERIFIED | R2's builtin/remote.c; git-config | VERIFIED | Fixed: remote.c (master) clears every fetch line (`remove_all_fetch_refspecs`, `CONFIG_FLAGS_MULTI_REPLACE`), then writes `+` + `refs/heads/%s:refs/remotes/%s/%s`, so `*` gives the glob. git-config refuses to set when several lines match (ret=5). The git 2.43 result is a fixture assertion (step 8), not a claim. |
| R1-20 `ls-remote` "Displays references available in a remote repository"; `--heads` a deprecated synonym of `--branches`; exit 0 = "successfully talked with the remote repository" | https://git-scm.com/docs/git-ls-remote | VERIFIED | Not used in this item (R2 AGAINST 2). |
| R1-21 stale refs kept until prune; prune works "as a function of the refspec"; over-report only, so --next-id gives a higher ID | git-fetch PRUNING | VERIFIED | – |
| R1-22 `open_branches()` L1414-1431 returns `[]` on empty list; main L2013-2014 prints none; `next_id()` L1856-1870; neither reads remote.origin.fetch | scripts/check_pipeline.py | VERIFIED | – |
| R1-23 check_handoff `_branch_with_handoff` L90-104; a str at L99-100 becomes `(None, why)` | scripts/check_handoff.py | VERIFIED | – |
| R1-24 plain `--depth 1` tests L958, L1062, L2082 assert exit 0; `_clone` L4415-4417 forces `--no-single-branch`; L4450 precedent | tests/test_pipeline_check.py | VERIFIED | – |
| R1-25 catch-all `_git` fakes (L4468, `("", 0)`) would answer the new config call with exit 0 and no value | tests/test_pipeline_check.py L4468 | VERIFIED | Consequence added in step 8(g): test_open_branches_default_computes_shallow asserts `== []` and must answer the config call with the glob. |
| R1-N F2 math: full clone max(091, 092) + 1 = 093; single-branch 091 + 1 = 092 (clash) | audit L103-107, L131 | VERIFIED | Re-done in Self-check. |
| R2-1 RI-009 is GUARDED (3 occurrences), and its 2026-11-22 entry names 094 | logs/recurring-issues.md L108-116 | VERIFIED | – |
| R2-2 "RI-014 ... Its 2026-11-24 entry lists 094 as a near miss" | logs/recurring-issues.md L153 | WRONG | Fixed: the 2026-11-24 entry says "no new occurrence; 092, 094, 095 run today". The near miss "single-branch clone → 094" is in the 2026-11-22 part of L153. |
| R2-3 081 family rule "failed git never none" is `_git_ok` L1401-1411; git succeeds here, so `_git_ok` cannot catch it | scripts/check_pipeline.py | VERIFIED | – |
| R2-4 F2 repro: sb2 and d1s print `none`/092, full 093; the same after unshallow; fetch shows only origin/main; A1 recovery `set-branches origin '*' && git fetch origin` | audit L102-120 | VERIFIED | – |
| R2-5 the proxy refused git-scm.com in A1's run | audit L26-27 | VERIFIED | – |
| R2-6 090/02 flagged the single-branch case as out of scope | work/090/02-improvements.md L104 | VERIFIED | – |
| R2-7 095 edits the same print block L2011-2029 and a1-auditor.md L22 | work/095/request.md; work/095/02 L5-6, L36, L60-62 | VERIFIED | – |
| R2-8 language precedent: 079, 084, 086, 090 logged `languages: N/A` | logs/research/2026-11-21.md L9 (090); work/090/02 L80 (079, 084, 086) | VERIFIED | – |
| R2-9 `set-branches` without `--add` clears all fetch lines, then writes `+refs/heads/<b>:refs/remotes/<r>/<b>`; `*` gives the glob and drops `^` and extra lines | https://raw.githubusercontent.com/git/git/master/builtin/remote.c | VERIFIED | For git master. git 2.43 is pinned by the step 8(a) assertion. |
| R2-10 git-config fails on set with several matching lines (ret=5) and "refuses to write multi-valued config options" | git-config | VERIFIED | – |
| R2-11 `git config get` came with the 2.46 deprecation, so `--get-all` is the form that works on 2.43 and later | RelNotes 2.46.0; git-config | VERIFIED | – |
| R2-12 `shallow = env == SHALLOW_TEXT` (L1958) is the equality precedent | scripts/check_pipeline.py L1958 | VERIFIED | – |
| R2-13 git config exit 1 = key absent | git-config | VERIFIED | – |
| R2-14 h1 test_open_branches_none_line L2594-2599 and d3 test_main_ahead_exact_ref_only L2547-2558 need the no-origin path | tests/test_pipeline_check.py | VERIFIED | – |
| R2-15 known gap: "with no origin fetch key, `git fetch` cannot hide or add anything" | git-fetch CRTB | WRONG | Fixed: per git-fetch, fetch values are what decide "which local refs to update". An origin with a URL but no fetch key gets no remote-tracking branch, so every open branch is hidden. Step 1: when the fetch key is absent, read `remote.origin.url`. No URL (exit 1) keeps today's path. A URL means not checked. |
| R2-16 `--next-id` returning `(None, why)` refuses with exit 2 through main L1934-1939 | scripts/check_pipeline.py | VERIFIED | – |
| R2-17 the fixed tail "Fix the clone (git fetch origin)" is the wrong recovery here | check_pipeline.py L1938; audit L110 | VERIFIED | – |
| R2-18 IN PR, RULES BRANCH, ID CLASH (L2002-2034) say `not checked (see OPEN BRANCHES)` when `branches` is a str | scripts/check_pipeline.py L2002, L2032, L2034 | VERIFIED | – |
| R2-19 check_handoff L96-100 maps a str to `(None, why)` | scripts/check_handoff.py | VERIFIED | – |
| R2-20 main L2086 has `isinstance(branches, str)` in the exit-1 test; reusing it flips L958/L1062/L2082 | scripts/check_pipeline.py L2085-2087 | VERIFIED | – |
| R2-21 h2 (L2602): a str from open_branches gives check_handoff --all `not checked` and exit 1 | tests/test_pipeline_check.py L2602-2614 | VERIFIED | – |
| R2-22 not-checked lines never change the exit (090 precedent) | tests/test_pipeline_check.py L4450 | VERIFIED | – |
| R2-23 `ls-remote --branches` arrived in 2.46 ("--branches" replaces "--heads") | RelNotes 2.46.0 | VERIFIED | – |
| R2-24 `--branches` "is probably unknown" on git 2.43 (R2's inference) | none | UNSUPPORTED | Removed: no source, and ls-remote is not used in this item. |
| R2-25 full refspec with no fetch yet leaves the refs missing, so the output is a silent `none` | git-fetch CRTB (fetch creates the refs) | VERIFIED | Known gap (Missing inputs). The rule files already say to run the checker "after git fetch origin" (a1-auditor.md L22, run-item.md L12). |
| R2-26 the UNSHALLOW sentence is pinned once in three files (L3707-3716); after unshallow it lets sb2 report `none` | tests/test_pipeline_check.py; audit L108-109 | VERIFIED | – |
| R2-27 scripts/check_pipeline.py and .claude/ are RULE_PATHS | scripts/check_pipeline.py L463 | VERIFIED | – |
| R2-28 the request says near miss, not counted | work/094/request.md L15 | VERIFIED | – |
| R2-29 `git config get --all` needs git 2.46 or later | RelNotes 2.46.0 | VERIFIED | – |
**Totals:** 55 rows checked → **50 VERIFIED as-is**, **4 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- R2-24: "`ls-remote --branches` is probably unknown on git 2.43" (R2's own inference, no source). Nothing replaces it, because ls-remote is not part of this item. If a later item adds ls-remote, it must check the option against the installed git.

## Implementation map
Build order: 094 and 095 change the same print block (L2011-2029) and a1-auditor.md L22. I1 runs `python3 scripts/check_pipeline.py` after `git fetch origin`. If 095's branch is open, 094 is built on top of it (RULES BRANCH, item 049), and 05 says so. 094 never edits the UNSHALLOW sentence. RULE_PATHS are touched, so the person's OK is needed in PR review.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: add the constant `SINGLE_TEXT = "single-branch clone; run git remote set-branches origin '*' && git fetch origin"` and `fetch_coverage()`. (a) `_git("config", "--get-all", "remote.origin.fetch")`. (b) None → "no git". (c) Exit 0: values = non-empty `splitlines()`. Full only if at least one value with one leading `+` removed equals `refs/heads/*:refs/remotes/origin/*` and no value starts with `^`; else SINGLE_TEXT (this includes exit 0 with no value). (d) Exit 1: `_git("config", "--get", "remote.origin.url")`. Exit 1 → "no origin" (today's path). Exit 0 → SINGLE_TEXT. Any other → `git config failed (exit n)`. (e) Other exit on the fetch read → `git config failed (exit n)`. Returns exactly one of "full", "no origin", "no git", SINGLE_TEXT, `git config failed (exit n)` | local git config | that string | test_fetch_coverage_shapes (step 8b) over S1-S12; unit fakes for S8/S11/S12 | 4 full of 12 shapes (S1, S2, S4a, S4b; Self-check table), evaluated by hand against this rule; re-run by test_fetch_coverage_shapes |
| 2 | `open_branches()`: after the `branch -r` read succeeds (so the 081 messages are unchanged when git dies) and before the shallow logic, call fetch_coverage. "full", "no origin" or "no git": continue as today. SINGLE_TEXT: return SINGLE_TEXT. `git config failed (...)`: return it (the 081 str path, exit 1) | step 1 | list, None, SINGLE_TEXT or error str | step 8a fixture; test_all_git_fails_no_line_says_none still says `git branch failed (exit 128)` | – |
| 3 | `next_id()`: after the branch read succeeds (why is None), call fetch_coverage. SINGLE_TEXT or `git config failed` → `(None, that)`. Other values → loop as today | step 1 | (id, None) or (None, why) | step 8a: sb, d1s and d1s+unshallow → exit 2, empty stdout; after recovery → `093` | – |
| 4 | `main()`: (a) before the 081 branch at L2011, `if branches == SINGLE_TEXT: print(f"OPEN BRANCHES: not checked ({SINGLE_TEXT})")`. (b) The exit test at L2086 becomes `(isinstance(branches, str) and branches != SINGLE_TEXT)`. (c) IN PR, RULES BRANCH and ID CLASH need no new code: `unread` already gives `not checked (see OPEN BRANCHES)` for any str. (d) `--next-id`: when why == SINGLE_TEXT, stderr is `--next-id refused: <SINGLE_TEXT>; not counting open branches would risk an ID clash (item 037). Re-run after that.`; other reasons keep today's text. All comparisons use `==` (RI-012) | steps 2-3 | printed lines, exit code | step 8a asserts the exact lines and exit 0 / exit 2; L966, L1067 and L2086 stay `code == 0` | 3 of 3 plain `--depth 1` tests keep `code == 0` (L966, L1067, L2086); their clones are single-branch (git-clone `--depth`), so each is an m4 detector |
| 5 | scripts/check_handoff.py: no code change. Docstring of check_all: the single-branch state is `not checked (open branches: <SINGLE_TEXT>)`, exit 1 (its existing contract) | open_branches | `<ID>: not checked (open branches: single-branch clone; ...)` | step 8e | – |
| 6 | Docstrings: the module docstring (L56-79 OPEN BRANCHES paragraph, L296 --next-id paragraph), open_branches, next_id and fetch_coverage name item 094, the exit choice and the known gap (full refspec, never fetched) | – | text | step 8h text pin (`"(item 094)"` in the docstring) | – |
| 7 | Rule files: add one new sentence right after the UNSHALLOW sentence (UNSHALLOW not edited) in .claude/agents/a1-auditor.md L22, .claude/commands/run-item.md L12 and .claude/commands/daily-audit.md L4: `If \`git config --get-all remote.origin.fetch\` has no \`+refs/heads/*:refs/remotes/origin/*\` line (with or without the \`+\`) or has a line starting with \`^\`, run \`git remote set-branches origin '*' && git fetch origin\`, then test again; until then report OPEN BRANCHES, IN PR, RULES BRANCH and ID CLASH as 'not checked', never 'none', and take no ID from \`--next-id\` (item 094).` | – | 3 edited files | test_single_branch_sentence_same_in_three_files: count == 1 in each; test_unshallow_sentence_same_in_three_files still passes | – |
| 8 | tests/test_pipeline_check.py. (a) test_single_branch_clone_not_checked (real git, @NO_GIT): source with main holding work/091 and a pushed `claude/probe-092` holding work/092. Clones: full (`git clone`), sb (`--single-branch`), d1s (plain `--depth 1`), d1s after `git fetch --unshallow`. Full: `--get-all` output is exactly the glob, `--next-id` → `093`, branch listed. sb, d1s, d1s+unshallow: `OPEN BRANCHES: not checked (single-branch clone; run git remote set-branches origin '*' && git fetch origin)`, `IN PR:`, `ID CLASH:` and `RULES BRANCH:` each `not checked (see OPEN BRANCHES)`, exit 0; `--next-id` exit 2, stdout "", stderr starts `--next-id refused: single-branch clone;`. Then in sb run the recovery: `--get-all` is exactly one line, the glob; `--next-id` → `093`. (b) test_fetch_coverage_shapes: real `git config --add` / `--unset-all` on a full clone for S1-S7, S9, S10; asserts fetch_coverage per the S table, including the recovery on S5 (glob + `^`) → one glob line. (c) S8 (`("", 0)`), S11, S12 via `_patched_git`. (d) S12 end to end: `main()` exit 1, `OPEN BRANCHES: git config failed (exit 128) (item 081)`; `--next-id` exit 2. (e) check_handoff --all in the sb clone: `not checked (open branches: single-branch clone; ...)`, exit 1. (f) GIT_CENSUS: add `("fetch_coverage", "_git"): (2, "...")`; total 47 → 49. (g) test_open_branches_default_computes_shallow L4468: the fake answers `("config", "--get-all", "remote.origin.fetch")` with the glob (meaning kept: shallow skip). (h) docstring/sentence pins | real git 2.43.0 | new tests | full suite green; mutation table below | S table: 12 shapes, 4 full |
| 9 | Mutations (I3), each must fail a named test: m1 fetch_coverage always "full" → test_single_branch_clone_not_checked. m2 `^` test removed → test_fetch_coverage_shapes[S5]. m3 `--get` instead of `--get-all` (S4b: glob first, named main last → reads only the named line) → test_fetch_coverage_shapes[S4b]. m4 `and branches != SINGLE_TEXT` removed → test_uncommitted_step_in_shallow_clone, test_cutoff_missing_in_shallow_clone_not_checked, test_inbox_shallow_clone_not_checked, test_single_branch_clone_not_checked. m5 url check removed (exit 1 always today's path) → test_fetch_coverage_shapes[S10]. m6 coverage call removed from next_id only → test_single_branch_clone_not_checked (`--next-id` gives `092`) | built code | failing test names in 06 | 06 lists each mutation with failed / passed counts | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `remote.origin.fetch` (fetch_coverage, step 1) | key absent (exit 1) and `remote.origin.url` absent (exit 1) | "no origin": today's path. `OPEN BRANCHES: none` only if `branch -r` lists nothing (h1, d3 stay green). No origin means no fetch can add or hide origin refs. |
| `remote.origin.fetch` | key absent, `remote.origin.url` present | `OPEN BRANCHES: not checked (SINGLE_TEXT)`, exit unchanged; `--next-id` refuses, exit 2 |
| `remote.origin.fetch` | exit 0 with no value (S8, e.g. a catch-all fake) | SINGLE_TEXT, never "full" |
| `remote.origin.fetch` / `remote.origin.url` | git exits other than 0 or 1 | `OPEN BRANCHES: git config failed (exit n) (item 081)`, exit 1; `--next-id refused: git config failed (exit n); ...`, exit 2 |
| git itself | `_git` returns None | "no git": today's no-git path (no OPEN BRANCHES line; --next-id from HEAD's work/ only). Unchanged. |
| remote's branch list (needs the network) | full refspec but never fetched | Known gap, written in the docstrings: reports local refs only. Not computable offline. The rule files already require `git fetch origin` before the run. ls-remote is left out on purpose (R2 AGAINST 2). |
| other remotes (`upstream/*` refs) | not checked for refspec | Known gap, written in the docstrings: MAIN and the coverage check are origin-only, as today. |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| F2 worked example (--next-id) | max(IDs on HEAD and on unmerged refs) + 1 | full: max(91, 92) + 1 = 93 → `093`; sb sees HEAD only: 91 + 1 = 92 → `092` = the open branch's ID → clash. With step 3, sb → refusal (exit 2), never 092 | matches audit L104-107 |
| Step 1, S1 `+refs/heads/*:refs/remotes/origin/*` | strip one `+` → equals glob; no `^` | "refs/heads/*:refs/remotes/origin/*" == glob; 0 `^` lines | full |
| S2 `refs/heads/*:refs/remotes/origin/*` (no `+`) | same | strip nothing → equals glob | full |
| S3 `+refs/heads/main:refs/remotes/origin/main` (git 2.43 single-branch, audit L30) | same | "refs/heads/main:..." ≠ glob; no other line | SINGLE_TEXT |
| S4a named main, then glob | any line equals glob | line 2 equals glob; 0 `^` | full |
| S4b glob, then named main (m3 order) | any line equals glob | line 1 equals glob → full. Under m3 `--get` reads the last line only (git-config "emits the last value") → named → SINGLE_TEXT ≠ full → test fails | full; m3 caught |
| S5 glob + `^refs/heads/claude/*` | no line starts with `^` | 1 `^` line → rule fails | SINGLE_TEXT; m2 → full → caught |
| S6 two named lines (Pro Git master + experiment) | any line equals glob | 0 of 2 equal | SINGLE_TEXT |
| S7 `+refs/heads/*:refs/remotes/upstream/*` | equals glob | dst differs | SINGLE_TEXT |
| S8 exit 0, empty output | at least one value | 0 values | SINGLE_TEXT |
| S9 fetch exit 1, url exit 1 (no origin) | url read | url exit 1 | "no origin" (today's path) |
| S10 fetch exit 1, url exit 0 | url read | url exit 0 | SINGLE_TEXT; m5 → today's path → caught |
| S11 fetch exit 0 with `++refs/heads/*:...` (two `+`) | strip one `+` only | "+refs/heads/*..." ≠ glob | SINGLE_TEXT |
| S12 fetch exit 128 | exit not in (0, 1) | 128 | `git config failed (exit 128)` |
| Feasibility count | full shapes / all shapes | S1, S2, S4a, S4b = 4; S1-S12 with S4 split = 12 | 4 of 12 (non-zero; at least one full shape, S1, is what `git clone` writes: Pro Git, git-fetch) |
| Step 4 exit choice | single-branch state alone → exit 0 | L966: clone of a main-only repo with `--depth 1` → S3 → SINGLE_TEXT → excluded from the str test → 0 == 0. Same for L1067 and L2086. m4 → str → exit 1 ≠ 0 → 3 failures | 3 of 3 stay green; m4 caught 3 times |
| Order rule (step 2) | branch read before config read | test L2446 fakes every git call as 128 → `branch -r` fails first → `git branch failed (exit 128)`, as L2456 asserts | unchanged |
| Step 8f census | old total + new `_git` calls | 47 + 2 (fetch read, url read) = 49 | 49 |
| Recovery example (step 8a) | after `set-branches origin '*'` the value is exactly the glob | remote.c: clear all lines, then add `+` + `refs/heads/*:refs/remotes/origin/*` → S1 → full; then `git fetch origin` → origin/claude/probe-092 → max(91, 92) + 1 = 93 | `093`; pinned on git 2.43 by the fixture |
| Printed line vs constant | `OPEN BRANCHES: not checked (` + SINGLE_TEXT + `)` | SINGLE_TEXT contains `'*'` quoted, so a shell does not expand it | one constant; equality test only |

`check_handoff output (run by the orchestrator 2026-11-24 18:23 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 9
fact-check rows: 55
totals line: 55 rows -> 50 as-is, 4 fixed, 1 removed
PASS
```
