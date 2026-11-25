# 03 Research hand-off - 095
Status: READY (if the orchestrator's `check_handoff.py 095` run below prints PASS; if it does not, this is BLOCKED (check_handoff not PASS) until fixed)

R3 has no shell (item 072). Every check below was made with Read/Grep on the working tree (branch daily-fixes/2026-11-24, 2026-11-24) and WebFetch (all eight cited URLs fetched today, plus code.googlesource.com merge-base.c). Line numbers are scripts/check_pipeline.py unless marked otherwise. Counts marked "A1" come from A1's real-clone probes in logs/audit/; I2 re-derives them by code. Exit-code default (orchestrator): keep current exit codes (fail closed), because the request does not ask to change them. Build order: on top of 094 if it lands first (same `open_branches`/main() printing, same UNSHALLOW sentence and its test constant); I1 re-reads line numbers on the build base.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| #1 01 G1: shallow file = pretend root commits; grafts pretend no parents | https://git-scm.com/docs/shallow (both quotes match) | VERIFIED | – |
| #2 01 G2: `--depth` implies `--single-branch` unless `--no-single-branch`; case (B) needs a no-single-branch shallow clone | https://git-scm.com/docs/git-clone (quote matches) | VERIFIED | – |
| #3 01 G3: `--no-merged` = tips not reachable from HEAD; full clone lists 1 ref, d1 lists 28, all merged | https://git-scm.com/docs/git-branch (quote matches); logs/audit/2026-11-22-090.md L74-75 | VERIFIED | – |
| #4 01 G4: `--all` / `--is-ancestor` texts; exit 1 for "no merge base" UNVERIFIED from docs | https://git-scm.com/docs/git-merge-base (quotes match; no exit text, no shallow text); https://code.googlesource.com/git/+/HEAD/builtin/merge-base.c | WRONG (source exists) | `show_merge_base`: `if (!result) return 1;` (nothing printed). Exit 1 = no merge base is sourced (same finding as work/090/03 #25) |
| #5 01 G5: shallow view only removes parent edges; "no merge base" may be merged, open-before-boundary or unrelated | derived from #1 | VERIFIED | – |
| #6 01 G6: `--unshallow` from a shallow source stays shallow | https://git-scm.com/docs/git-fetch (both quotes match) | VERIFIED | – |
| #7 01 G7: `--is-shallow-repository` text | https://git-scm.com/docs/git-rev-parse (quote matches) | VERIFIED | – |
| #8 01 G8 (quotes): "Initial commits ..." / "Root commits are compared to an empty tree" | https://git-scm.com/docs/git-log (both quotes match) | VERIFIED | – |
| #9 01 G8 (derivation): in depth 1 `--diff-filter=A -1` names the boundary commit for every file, so every rule reads "seen" | derived, not probed, no source | UNSUPPORTED | Removed. The map does not need it: 084 already skips `_rule_seen` when env is set (L827-828; docstring L325-326) |
| #10 01 G9: actions/checkout `fetch-depth` default 1, single commit; 0 = all history; CI not in repo | https://github.com/actions/checkout (quotes match); logs/recurring-issues.md L123 | VERIFIED | – |
| #11 01 A1: `_anchor_env` returns SHALLOW_TEXT when `_is_shallow()`; computed once in main | L806-817, L1828, L1957 | VERIFIED | – |
| #12 01 A2: `_rule_seen` returns `(None, "")` when env is set, before any git call | L827-828 | VERIFIED | – |
| #13 01 A3: "Five gate sites use `_rule_seen`" (then lists six); entries carry no note in shallow | L916, L922, L938, L963, L977, L994; L917, L923, L943, L967, L982, L998 | WRONG (count) | Six call lines; L977 runs in a loop over 05 and 06, so seven evaluations (as 01 Numbers says). No-note part VERIFIED |
| #14 01 A4: gated entries join `unfinished` → exit 1; RULE NOT SEEN prints `not checked ({env})` | L1994-1996, L2051, L2085 | VERIFIED | – |
| #15 01 A5: 084 docstring: shallow "keeps the numeric cutoffs" | L325-326 | VERIFIED | – |
| #16 01 A6: rule sentence in a1-auditor.md L22 and run-item.md L12; "templates/daily-audit.md has no shallow text" | a1-auditor.md L22; run-item.md L12; .claude/commands/daily-audit.md L4; tests/test_pipeline_check.py L3707-3716 | WRONG (incomplete) | The same sentence is also in .claude/commands/daily-audit.md L4 (the third file; templates/daily-audit.md is not a rule file for it). `test_unshallow_sentence_same_in_three_files` pins it byte for byte in all three files and asserts "RULE NOT SEEN" is in it. Map step 4 edits all four places together |
| #17 01 A7: d1 083 INCOMPLETE (I2 format; Sent back to: none); full clone RULE NOT SEEN 083, INCOMPLETE none | logs/audit/2026-11-22-090.md L82-87 | VERIFIED | – |
| #18 01 A8: entries not behind a gate are exact (no log line, RI line, unreadable) | L893-907 | VERIFIED | – |
| #19 01 A9: shallow can only add gated entries, never hide one | L827-828 with each gate's `seen is False` drop branch (L918-930, L939, L964, L978, L995) | VERIFIED | Refined in map step 1: the TESTS gate's entry is exact when any I2 line fails I2_BEFORE (L926-929: full clone keeps it either way) |
| #20 01 A10: the full set of items behind a gate needs a full-clone run: UNVERIFIED | logs/audit/2026-11-20.md L60, 2026-11-21.md L32, 2026-11-21-088.md L65, 2026-11-22-090.md L84 | WRONG (source exists) | Four A1 full-clone runs (2026-11-20..22) print `RULE NOT SEEN: 083` only, and 11-22 shows INCOMPLETE none. Set = {083}; I2 re-derives on today's tree |
| #21 01 A11: env is also "no git" / "unborn HEAD" with the same strict entries | L806-816 | VERIFIED | Scope decision in map step 1 (shallow only) |
| #22 01 B1: refs from `branch -r --no-merged HEAD`; shallow skips origin/main; `behind` off when shallow | L1425, L1432, L1437-1440 | VERIFIED | – |
| #23 01 B2: merge-base exit 1 → unrelated; ls-tree of checked paths; shallow error text | L1444-1456 | VERIFIED | – |
| #24 01 B3: per-ref `not checked` sub-line + per-ref BRANCH ERROR; branch_errors → exit 1; N + N lines | L2019-2021, L2041-2043, L2087 | VERIFIED | – |
| #25 01 B4: docstring known gap "refs already in main are listed" | L93-95 | VERIFIED | – |
| #26 01 B5: T18/T19 shapes; "M11 fails test_shallow_three_readers_not_checked" quoted from recurring-issues L153 | tests L4424-4459; recurring-issues.md L153; logs/audit/2026-11-22-090.md L55, L139-140 | WRONG (source line) | L153 says "Stays OPEN until merged and M11 fails on main"; the test name is in the 090 audit L55 and L139-140. Test facts VERIFIED |
| #27 01 B6: no exact per-ref merged test in the shallow view is documented | git-branch and git-merge-base pages (none documented); #5 | VERIFIED | – |
| #28 01 B7: exit precedents A (not-checked lines) and B (081/090); "under a1-auditor.md L23, every BRANCH ERROR line is an error" | L2005-2006, L2056-2057, L2085-2087; T19 docstring L4449-4450; a1-auditor.md L23 | WRONG (rule text) | L23 puts every BRANCH ERROR line at the top of the report; it calls only ID CLASH and BRANCH SKIPPED errors. The exit 1 comes from the script (L2087). Precedents VERIFIED |
| #29 01 B8: check_handoff calls `open_branches()` with no args and reads the dicts | scripts/check_handoff.py L95-103 (reads `b["ref"]`, `b["items"]` only) | VERIFIED | – |
| #30 01 B9: 094 changes `open_branches`/`--next-id` and the same rule sentence | work/094/01-research.md #22-24, Open question 1 | VERIFIED | – |
| #31 01 Numbers: 28 × (1 + 1) = 56 lines, exit 1 | A1 probe 090 audit L74-76 | VERIFIED | After the map: 2 lines (see #42) |
| #32 01 Numbers: 083 has 2 gated entries (TESTS_FORMAT_FROM, VERDICT_FROM) | 090 audit L82-84; L921-930, L983-998 | VERIFIED | – |
| #33 01 Numbers: 7 gate evaluations from 6 call lines | Grep `_rule_seen(`: L916, L922, L938, L963, L977, L994 | VERIFIED | – |
| #34 01 Numbers: fixture 2 merged + 1 open → one line naming 3 | T18 (open `origin/claude-x` is unrelated at depth 1, L4440-4442); #5 | VERIFIED | – |
| #35 01 Fit: tooling only; "These are RULE_PATHS" for check_pipeline.py, tests, rule text | L463 (RULE_PATHS = .claude/, templates/, scripts/check_pipeline.py, scripts/check_handoff.py); L465 | WRONG (tests) | tests/ is in CODE_PATHS (L465), not RULE_PATHS. The person's OK is still needed (.claude/ and check_pipeline.py are RULE_PATHS) |
| #36 02: RI-014 OPEN, 1 occurrence; near miss → 095; M11 fails T18 and T19 | recurring-issues.md L153, L157; 090 audit L55, L60 | VERIFIED | – |
| #37 02: source F3 L121-128, probe L64-87, 28-ref count from one probe | 090 audit L64-87, L121-128 | VERIFIED | – |
| #38 02: L22 "not checked" vs "is an error"; "each of the 28 refs is 'not checked' by one sentence and an error by the next" | a1-auditor.md L22-23 | WRONG (refs part) | The 083 contradiction is VERIFIED (L22 both sentences). For the refs, L23 lists BRANCH ERROR at the top but does not call it an error (#28); the tension is L22 "not checked" vs the script's exit 1 |
| #39 02: code facts L827-828, L835-836, L1449-1453, L2041-2043, L2087 | those lines | VERIFIED | – |
| #40 02: 090/02 AGAINST 1 precedent: pick the exit code on purpose and pin it | work/090/02-improvements.md L54-55 | VERIFIED | – |
| #41 02: 079/084/086/090 logged `languages: N/A` | work/090/02-improvements.md L16, L107 | VERIFIED | – |
| #42 02 FOR 1: "56 lines become 1 line" | #24; 02 AGAINST 1's own exit choice | WRONG (count) | With the exit kept (fail closed): 1 OPEN BRANCHES not-checked sub-line + 1 summary BRANCH ERROR = 2 lines (0 BRANCH ERROR lines when no folded ref holds checked paths, as T19) |
| #43 02 FOR 2: key the label on env, not on `seen is None and sha7 == ""`, because an uncommitted step file also gives `(None, "")` | L827-828, L835-836 | VERIFIED | – |
| #44 02 FOR 2: keying on `env` labels "no git" / "unborn HEAD" too, "for free" | tests/test_pipeline_check.py: 18 assertions on gated entry texts (Grep `has no 'Sent back to: none'\|wants "\|does not match its format`), many in no-git tmp fixtures | WRONG (overstated) | Not free: it would move entries in no-git fixtures. The request names shallow clones only, so the map keys on `env == SHALLOW_TEXT` (the equality main already uses, L1958). No-git and unborn stay as today (follow-up note in docstring) |
| #45 02 FOR 3: fold only in main()'s printing; check_handoff keeps its dicts | check_handoff.py L95-103; L2017-2043 | VERIFIED | One additive dict key (`held`, map step 2) is allowed: check_handoff reads only `ref` and `items` |
| #46 02 FOR 3: keep the names; T18's claude-x is open in the full clone | tests L4434 | VERIFIED | – |
| #47 02 FOR 3: 094's string state is printed at L2011-2012; the fold does not touch it | L2011-2012; work/094/01 #23 | VERIFIED | – |
| #48 02 AGAINST 1: exit-neutral fold can hide an open branch (RI-002 shape); keep exit 1 with one summary BRANCH ERROR | #5; T18 | VERIFIED | Adopted (map step 2) |
| #49 02 AGAINST 2: "In depth 1, every anchor would be the boundary commit" | rests on #9 | UNSUPPORTED | Removed with #9 |
| #50 02 AGAINST 2: option (i) vs (ii); finer boundary test via `_shallow_boundaries` (L1569) left as follow-up | L1569; derived | VERIFIED | Map uses a separate line that keeps the exit (meets "no false INCOMPLETE" and fail closed); finer test not built |
| #51 02 AGAINST 3: RULE_PATHS edits, T18 is the GUARDED probe, overlap with 094/092; re-run M11 | recurring-issues L153; 090 audit L55-61 | VERIFIED | – |
| #52 02 Holes: LOG BATCH note added only `if sha7 not in missing` | L942-943 | VERIFIED | – |
| #53 02 Holes: don't touch the `isinstance(branches, str)` path; full-clone control in T18 L4429-4434 | L2011-2012; tests L4429-4434 | VERIFIED | – |

**Totals:** 53 rows checked → **41 VERIFIED as-is**, **10 fixed**, **2 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- #9 (01 G8 derivation): in a depth-1 clone `git log --diff-filter=A -1` names the boundary commit for every file, so every rule reads "seen". Not probed, no source.
- #49 (02 AGAINST 2): "every anchor would be the boundary commit". Rests on #9.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Script, (A) `incomplete()`: new arg `unchecked` (list, like `not_seen`). When `env == SHALLOW_TEXT` (equality, never `env is not None` and never `seen is None`, #43/#44) and a gate's entry fires and the full clone could have dropped it, the entry goes to `unchecked` instead of `missing`. "Could have dropped" = the gate's `seen is False` branch would remove it: TIMED_FROM I2 (L914-920), LOG BATCH (L936-943), SUITE (L962-967), ROUND_HEADING 05 and 06 (L977-982), VERDICT (L993-998) always; TESTS (L921-930) only when every own I2 line passes I2_BEFORE (else exact, stays INCOMPLETE). In the format entry (L931-933) only I2 moves; any other agent in `bad` stays in INCOMPLETE. One helper (e.g. `_unsure(env)`) is the single switch. main() prints, right after `INCOMPLETE:` and only when `shallow` is True, `INCOMPLETE NOT CHECKED: <ID> (<entries>), ...; rule seen not checked (shallow clone; run git fetch --unshallow; item 095)` or `INCOMPLETE NOT CHECKED: none`. Exit: a non-empty list gives exit 1 (`or unchecked`), as these entries do today. No-git and unborn HEAD unchanged | env; the 7 gate evaluations; own I2 lines | INCOMPLETE and INCOMPLETE NOT CHECKED lines; exit | Fixture (a): `git clone -q --depth 1 --no-single-branch file://...` of a source where item 990's 05/06 were committed under a RULE_FILE without the constants (084's fixture shape) and 990 fires TESTS (I2 passes I2_BEFORE) + VERDICT. Full clone: `INCOMPLETE: none`, `RULE NOT SEEN: 990 ...`, no `INCOMPLETE NOT CHECKED` line, no `item 095` text. Depth 1: `INCOMPLETE: none`, `INCOMPLETE NOT CHECKED: 990 (...2 entries...)`, exit 1 pinned. Twin: 990 also has an R1 format error and a missing log line → those stay on INCOMPLETE. Twin: an I2 line failing I2_BEFORE stays on INCOMPLETE in depth 1. Full-clone twin with 05 uncommitted → entry stays on INCOMPLETE, no NOT CHECKED line. Mutations: helper returns False (fixture a fails); helper keyed on `env is not None` (a no-git fixture test fails); keyed on `seen is None` (uncommitted twin fails) | Real tree: 1 item (083) moves, 2 of 2 of its entries, from four A1 full-clone runs 2026-11-20..22 (#20); 0 other items have RULE NOT SEEN pairs. I2 re-derives on a real depth-1 `--no-single-branch` clone and records the count in 05 |
| 2 | Script, (B): `open_branches` adds one key `held` to the unrelated dict (int = number of checked-path files, None when ls-tree failed); dict otherwise unchanged. main() folds every ref with `unrelated and shallow` into one OPEN BRANCHES sub-line `  shallow clone: <n> ref(s) with no merge base not checked (<ref>, <ref>, ...); run git fetch --unshallow (item 095)` (names kept, sorted as listed; per-ref age dropped). Their shallow errors (refs with `held` an int > 0) become one `BRANCH ERROR: shallow clone; <k> of <n> ref(s) hold files on checked paths, not checked (<ref>, ...); run git fetch --unshallow (item 095)`. A ref with `held` None keeps its own `BRANCH ERROR: <ref> (git ls-tree failed ...)`. Classification by the `held` key, never by matching error text (RI-012). Exit unchanged: k ≥ 1 → exit 1 (branch_errors); k = 0 → no BRANCH ERROR (T19 stays exit 0). Full-clone path, scanned refs and the str path (L2011-2012) untouched | refs; merge-base exit; ls-tree | one sub-line; ≤ 1 shallow BRANCH ERROR | New fixture (b): source with 2 refs merged into main (each tree holds work/150) + 1 open ref with `.claude/x.md`. Full clone: only the open ref listed, `items none; merges cleanly`, 0 BRANCH ERROR. Depth 1: exactly 1 line containing `ref(s) with no merge base not checked`, naming all 3; exactly 1 `BRANCH ERROR:` line naming 3 of 3; exit 1 pinned. T18 edited: its BRANCH ERROR assertion becomes the folded form (1 of 1); its LOG TIME/MAIN AHEAD/full-clone assertions kept, so M11 (`shallow = False` in main) still fails T18 by name. T19 edited: the folded line names origin/docs; `BRANCH ERROR` absent; exit 0 kept. Unit test: an unrelated shallow ref with ls-tree failing keeps its own BRANCH ERROR. Mutations: fold removed (b fails: 3 sub-lines); fold on `unrelated` without `shallow` (full-clone 081 unrelated tests fail); M11 | A1 d1 probe 2026-11-22: 28 of 28 listed refs fold, 28 hold checked paths → 56 lines become 2 (#31, #42). Fixture (b): 3 of 3 fold, 3 of 3 held. T19: 1 of 1 fold, 0 held → 0 BRANCH ERROR. I2 re-derives on a real clone in 05 |
| 3 | Script docstrings: `incomplete()` (item 095 paragraph), RULE NOT SEEN text (L317-326: shallow entries now go to INCOMPLETE NOT CHECKED), `open_branches`/090 known gaps (L88-95: "refs already in main are listed" now folded; still cannot tell merged from open). Known gaps kept: no-git/unborn entries not labelled; finer boundary test not built | – | text | I3 reads docstrings against steps 1-2 | – |
| 4 | Rules: one new sentence, byte-identical, in .claude/agents/a1-auditor.md L22, .claude/commands/run-item.md L12 and .claude/commands/daily-audit.md L4, and the `UNSHALLOW` test constant (tests L3707-3709). Proposed: "... OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none'; `INCOMPLETE NOT CHECKED:` entries and the shallow-clone OPEN BRANCHES line with its BRANCH ERROR are 'not checked', not errors, though the run exits 1 for them: unshallow and re-run (items 079, 084, 090, 095)." If 094 lands first, merge its single-branch sentence into the same edit (one edit, #51) | rule files; test constant | 3 files + constant | `test_unshallow_sentence_same_in_three_files` passes (count == 1 in each file; "RULE NOT SEEN" still in it). Mutation: edit one file only → test fails | 3 of 3 files hold the current sentence today (Grep, 2026-11-24) |
| 5 | 05: `RI-014: ...` line (A1 copies it, item 036) with the M11 re-run (which tests fail), the real depth-1 counts from steps 1-2, and a whole-output diff of old vs new script on a full clone (must be empty) | git, clones | 05 lines | I3 re-runs M11 and the diff | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Shallow state (steps 1-2) | shallow file unreadable → `_is_shallow` True (L1600) → strict, entries go to NOT CHECKED, refs fold | `rule seen not checked (shallow clone; run git fetch --unshallow; item 095)`; never "none" or a pass |
| Rule-seen anchor (step 1) | not computable in a shallow clone (L827-828) | entry kept with the NOT CHECKED label, exit 1; never dropped, never a default "seen" |
| Own I2 lines for the TESTS exactness test (step 1) | log file unreadable → `log lines not checked` entry (L901-903), gate not reached | unchanged 089 text |
| ls-tree of a shallow ref (step 2) | git failed → `held` None | own `BRANCH ERROR: <ref> (<why>)`, exit 1; never folded as 0 files |
| merge-base exit other than 0/1 (step 2) | not unrelated; scanned path as today | unchanged (`git merge-base failed (exit <n>)`) |
| Last-commit date of a folded ref (step 2) | dropped from the folded line by design | n/a: names only; age shown again after unshallow |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 2 real line count | before: n × (1 sub-line + 1 BRANCH ERROR); after: 1 + (1 if k ≥ 1 else 0) | n = 28, k = 28: 28 × 2 = 56 → 1 + 1 = 2 | 56 → 2, exit 1 kept (k ≥ 1) |
| Step 2 fixture (b) | depth 1: refs unrelated = tips not reachable and no merge base (#5, T18) | 2 merged + 1 open = 3 fold; each tree holds a checked path (work/150 or .claude/x.md) → k = 3 ≥ 1 | 1 sub-line naming 3; 1 BRANCH ERROR "3 of 3"; exit 1 |
| Step 2 T19 | k = 0 → no BRANCH ERROR | orphan README-only: held = 0 → k = 0 | 1 sub-line, 0 BRANCH ERROR, exit 0 (unchanged) |
| Step 2 full clone | fold only when `shallow` | full: shallow False → 0 refs fold; open ref scanned (`items none; merges cleanly`) | output unchanged |
| Step 1 real tree | moved = gated entries that the full clone drops (RULE NOT SEEN pairs) | full-clone RULE NOT SEEN = {083} (#20); 083 d1 entries: TESTS (I2 passes I2_BEFORE, since full clone says "judged by I2_BEFORE") + VERDICT = 2 movable of 2 | INCOMPLETE: none for 083; NOT CHECKED: 083 (2 entries); exit 1 as today |
| Step 1 exactness of TESTS | full clone keeps the entry when an I2 line fails I2_BEFORE, seen True or False (L924-930) | seen True → entry; seen False and a line fails → `bad` keeps I2 → entry | exact: stays INCOMPLETE in depth 1 |
| Step 1 gate count | 6 call lines, L977 in a 2-step loop | 5 + 2 = 7 evaluations | matches #33 |
| Step 1 exit | `unchecked` non-empty → exit 1 | 083 today: INCOMPLETE → exit 1; after: NOT CHECKED → exit 1 | no exit change (fail closed) |
| Step 4 sentence | count(UNSHALLOW) == 1 in each of 3 files | 3 files × 1 | test passes only if all 3 + constant change together |

Recurring issues checked (item 013): RI-001 (ESCALATED): both selectors in the map have a computed count in Feasibility (step 1: 1 item / 2 of 2 entries from four A1 runs; step 2: 28 of 28 refs from A1's probe, 3 of 3 and 1 of 1 in fixtures); each has a stated empty result (`INCOMPLETE NOT CHECKED: none`; no sub-line when 0 refs fold); none says "always" without a count. RI-010 (ESCALATED): no step duty or log rule is changed; the new line and the rule sentence are pinned by tests (step 4). RI-014 (OPEN): this item; M11 must still fail T18 by name (step 2), full clone unchanged (step 5 diff). Also checked (GUARDED): RI-002, since an unknown anchor or failed ls-tree is never a pass, 0 or "none" (Missing inputs) and exits stay 1; RI-012, since folding uses the `held` key and the label uses env equality, never error-text substrings; RI-004/005, since every count in the map is re-derived above; RI-006, since totals are left to check_handoff; RI-009, since folded refs keep their names.

`check_handoff output (run by the orchestrator 2026-11-24 18:21 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 8
fact-check rows: 53
totals line: 53 rows -> 41 as-is, 10 fixed, 2 removed
PASS
```
