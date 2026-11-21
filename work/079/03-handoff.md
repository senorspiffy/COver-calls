# 03 Research hand-off - 079
Status: READY

Scope: FULL (request L3). BUG, so the map carries the prevention guardrail (steps 2-8), corrected where F7 / 02 FOR 1 were wrong (rows 21, 33). R3 has no shell: every git behaviour below is from git's docs or source, and the fixture sets are worked out by hand from each fixture's graph. The tests in step 6 run them again. Line numbers are for this branch before 076/077; I1 re-reads them on top of 077 (brief L3).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 1. The shallow file lists commits git treats as root commits ("git log" traversal stops after showing them); one object name per line | https://git-scm.com/docs/shallow | VERIFIED | Quotes match verbatim |
| 2. "Shallow commits do have parents, but not in the shallow repo, and therefore grafts are introduced pretending that these commits have no parents." | https://git-scm.com/docs/shallow | VERIFIED | |
| 3. `--is-shallow-repository` prints "true" when shallow, else "false" | https://git-scm.com/docs/git-rev-parse | VERIFIED | |
| 4. `<rev>^<n>` is the nth parent; the docs say nothing about a missing parent; boundary `c^1` failing is shown by the request's repro | https://git-scm.com/docs/git-rev-parse; request Evidence 2 | VERIFIED | Doc text matches; the failure itself is A1's repro (request L12) |
| 5. `--shallow-file` is not a git-rev-parse option | https://git-scm.com/docs/git-rev-parse | VERIFIED | Not on the page. Dropped from the guardrail wording (step 2) |
| 6. gitrepository-layout: `shallow` "is ignored if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/shallow" will be used instead" | https://git-scm.com/docs/gitrepository-layout | VERIFIED | |
| 7. In a linked worktree `$GIT_DIR` is `.git/worktrees/<name>`, `$GIT_COMMON_DIR` is the main `.git`, and `.git` is a file | https://git-scm.com/docs/git-worktree | VERIFIED | Page: "These settings are made in a `.git` file located at the top directory of the linked worktree" |
| 8. `--git-common-dir`: "Show `$GIT_COMMON_DIR` if defined, else `$GIT_DIR`"; `--git-dir` path "when relative, is relative to the current working directory" | https://git-scm.com/docs/git-rev-parse | VERIFIED | The relative-path sentence is on `--git-dir`. `_git` runs with cwd = toplevel (check_pipeline.py L488-492), so resolve the path against cwd |
| 9. git-worktree advice to use `--git-path`; whether `--git-path shallow` maps to the common dir is UNVERIFIED | https://git-scm.com/docs/git-worktree; https://raw.githubusercontent.com/git/git/master/path.c | VERIFIED + fixed | Quote verified. The UNVERIFIED half is settled by path.c `{ 0, 0, 1, "shallow" },` (third field `is_common`), so both forms reach the common dir. Map uses `--git-common-dir` |
| 10. `fetch --unshallow` from a shallow source fetches "as much as possible", which can leave the clone shallow | https://git-scm.com/docs/git-fetch | VERIFIED | So the process line re-tests (step 7) |
| 11. `clone --depth` "Implies `--single-branch` unless `--no-single-branch` is given" | https://git-scm.com/docs/git-clone | VERIFIED | |
| 12. actions/checkout `fetch-depth` default 1, 0 = all history; the repo has no CI today | https://github.com/actions/checkout; Glob `.github/**` → none | VERIFIED | Exact text: "0 indicates all history for all branches and tags", "Default: 1" |
| 13. log.showRoot True by default; root shown "as a big creation event", "equivalent to a diff against an empty tree" | https://code.googlesource.com/git/+/7381be0d632ac41b4ffb083a8d0a8eb2ff32d834/Documentation/config/log.adoc | VERIFIED | |
| 14. diff-tree `--root` gives a creation event; with one commit given it "is compared with its parents" | https://git-scm.com/docs/git-diff-tree | VERIFIED | |
| 15. F1: L599-605 test shallowness only when the cutoff is unknown or not an ancestor; L610-612 store None on a diff-tree failure; untracked_changes turns None into `<sha7> (git diff-tree failed)`, failed=True | scripts/check_pipeline.py L594-639 | VERIFIED | The entry is at L627-628 |
| 16. F2: research_code L659 `files or []` reads a failed diff as "no files" | check_pipeline.py L658-659 | VERIFIED | |
| 17. F3: the first-parent walk stops at a boundary, so first-parent commits behind it (between the cutoff and the boundary) are never walked | https://git-scm.com/docs/shallow ("traversal stops after showing them"); L606 | VERIFIED | Follows from the doc. Fixture (a) pins it (P is hidden) |
| 18. F4: `_item_triggers` L707 logs all parents of `cutoff..HEAD`; a boundary there can show as a creation event (false trigger) or hide commits | check_pipeline.py L702-722; log.adoc above | VERIFIED | Note: if a user sets log.showRoot=false, the boundary lists no files instead. Either way the S ∩ R check (step 2) catches a boundary in the range first |
| 19. F5: main() L857-860 computes `walked` once; research_code L650-651 and real_data_field L733-734 map a `_walk` error to "not checked (see UNTRACKED CHANGE)" | check_pipeline.py L649-651, L731-734, L857-860 | VERIFIED | |
| 20. F6: a missing parent is not shallow-specific: a real root commit in the range has no `c^1` in a full clone either, and must stay a loud entry | rev-parse `^n` doc; L611-612 | VERIFIED | Pinned by fixture (c2) |
| 21. F7: if S ∩ R is empty, "the full clone's `cutoff..HEAD` is exactly R", so the answers match | R1's own reasoning; https://git-scm.com/docs/shallow | WRONG | Only half holds. **No missed commit** (proof: a commit in the full range but not the shallow one is reached only across a cut edge b→p, and the first such b is in R) is true. **Extra commits** are possible: when a boundary b is an ancestor of the cutoff, a commit behind b that HEAD also reaches another way is in R but is an ancestor of the cutoff in the full clone. Counterexample = fixture (d): the shallow walk has Z, Y, M; the full walk has only M; S ∩ R = ∅. Extras only add entries, so "none" is still exact, but an entry is unconfirmed. Step 3 turns entries into "not checked" in that case |
| 22. F8: the existing test makes a shallow fixture with `git clone -q --depth 1 file://<repo>` and asserts `--is-shallow-repository` == "true" | tests/test_pipeline_check.py L728-741 | VERIFIED | |
| 23. F8 / 02 AGAINST 3: whether a hand-written shallow file flips `--is-shallow-repository` to true is UNVERIFIED | https://raw.githubusercontent.com/git/git/master/shallow.c `is_repository_shallow` | VERIFIED + fixed | Settled from source. `is_shallow` is set to 1 once `git_path_shallow(r)` opens, and each hex line goes to `register_shallow`; an empty file still counts as shallow; a malformed line makes git `die("bad shallow line")`. Fixtures still assert it (step 6) |
| 24. Fixture shape C→P→B, side D (parent C), M = merge(B, D), B in the shallow file: shallow first-parent walk {B, M}, R = {M, B, D}, S ∩ R = {B} → not checked, exit 0 | 01 Numbers; my derivation (Self-check row 1) | VERIFIED | The side commit is renamed D, because R1's "S" clashed with the set S |
| 25. Mutation: drop the S ∩ R test → B's diff-tree fails → `<B7> (git diff-tree failed)`, exit 1 | Derivation from L611-612, L627-628 | VERIFIED | |
| 26. Request evidence: 1 false entry (a15129c), exit 1, `none` after unshallow | request L11-13; logs/audit/2026-11-19.md L32, L44 | VERIFIED | A1's numbers, not re-run (no shell) |
| 27. 02: RI-014 is OPEN, 1 occurrence, at L151-157 | logs/recurring-issues.md L151-157 | VERIFIED | |
| 28. 02: 053 only handled a missing cutoff in a shallow clone; `test_cutoff_missing_in_shallow_clone_not_checked` L728-741 | check_pipeline.py L600-605; tests L728-741 | VERIFIED | Its text must not change (step 2 goes after L605) |
| 29. 02: 069 INBOX uses the blanket rule; g4 fails a test; RI-002 held there | logs/audit/2026-11-18-069.md L147, L156; check_pipeline.py L790-794 | VERIFIED | |
| 30. 02: the 2026-11-19 audit got `none` only after unshallowing | logs/audit/2026-11-19.md L32 | VERIFIED | |
| 31. 02: precedent 066, "tests that ran in a linked worktree have hit path assumptions before" | work/066/02-improvements.md | UNSUPPORTED | 066 moved a test into a worktree. It records no path-assumption failure. Removed. The worktree fixture is still needed because of request Evidence 1 and rows 6-7 |
| 32. 02: this clone has no `shallow` file | Glob /home/claude/cover-calls/.git/shallow → none | VERIFIED | |
| 33. 02 FOR 1: if S ∩ R is empty "every hidden parent is already behind the cutoff, so the answer equals the full clone's" | as row 21 | WRONG | Same error as F7. The boundary can be behind the cutoff while a commit behind it is reached from HEAD another way. Fixed by step 3 (the "below the cutoff" rule) |
| 34. 02 FOR 2: path.c lists `"shallow"` with is_common set, so `--git-path shallow` resolves to the common dir | https://raw.githubusercontent.com/git/git/master/path.c | VERIFIED | `{ 0, 0, 1, "shallow" },`; fields are ignore_garbage, is_dir, is_common, path |
| 35. 02 AGAINST 1: `_inbox_gate` L790-794 is the blanket rule; 053 noted a `--depth 50` fetch | check_pipeline.py L790-794; work/053/01-research.md L15 | VERIFIED | 053/03 L15 adds that this clone is not shallow now. 02's wording ("noted") is right |
| 36. 02: 062, 064, 066, 074 logged `languages: N/A` | logs/research/2026-11-13.md L7, 11-14 L7, 11-15 L5, 11-18 L10 | VERIFIED | |
| 37. 01: process lines go in daily-audit.md L4 and run-item.md L12 | .claude/commands/daily-audit.md L4; run-item.md L12 | VERIFIED | Both lines run check_pipeline.py |
**Totals:** 37 rows checked → **32 VERIFIED as-is**, **4 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- Row 31: "precedent 066: worktree tests hit path assumptions before" (02 L8). No source.
- Not removed but not in the map: R1's guardrail wording `rev-parse --shallow-file` (row 5). Also "parent missing = boundary" (row 20).
- Follow-up, not in this item (not verified): with a user `log.showRoot=false`, a *real* root commit in a full clone lists no files in 070's `git log`. This happens before this item and has nothing to do with shallow clones. A1 may open an item for it.

## Implementation map
Terms: S = the boundary set (the 40-hex lines of `<git rev-parse --git-common-dir>/shallow`). R = `git rev-list <cutoff>..HEAD` (all parents, shallow view). A boundary b is "inside" if b ∈ R, and "below" if `git merge-base --is-ancestor b <cutoff>` exits 0.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: new helper `_shallow_boundaries()`. Run `rev-parse --is-shallow-repository`. If it prints "false", return "full". Otherwise (true, or any other output from an old git) read `Path(<--git-common-dir output>)/"shallow"`, resolved against cwd. Never a literal `.git/shallow`, never `--shallow-file` | git, the common dir | "full", or the set S, or "unreadable" (shallow true but the file is missing or unreadable) | Fixture (e) in a linked worktree gets S = {B}; mutation m2 (literal `.git/shallow`) fails (e) | Fixture (e): S has 1 of 1 boundary (hand-derived; test re-runs) |
| 2 | `_walk`: after the existing cutoff/ancestor check (L599-605, text unchanged) and before the diff-tree loop. If shallow: "unreadable" → `(None, ("not checked (shallow clone; run git fetch --unshallow)" + note, False))`. Else compute R; if rev-list fails, give the existing loud `cutoff <c7>: git rev-list failed`. If S ∩ R ≠ ∅ → `(None, (f"not checked (shallow boundary {b[:7]}; run git fetch --unshallow)" + note, False))`, where b is the first boundary in rev-list's output order. A boundary is defined by S membership only. A diff-tree failure on a commit not in S stays `<sha7> (git diff-tree failed)`, failed=True | cutoff, HEAD, S | not-checked tuple, or units as today | Fixtures (a), (b), (e) give the exact text, exit 0; (c1) and (c2) unchanged; `test_cutoff_missing_in_shallow_clone_not_checked` unchanged; m1 fails (a), (b) | (a): S ∩ R = {B}, 1 of 1; (b): {B2}, 1 of 1; (c1): S = ∅ (full); hand-derived, Self-check rows 1-4 |
| 3 | The "below" rule: if shallow, S ∩ R = ∅ and some b ∈ S is below the cutoff (is-ancestor exits 0; any exit other than 0 or 1 → loud `cutoff <c7>: git merge-base failed`, failed=True), then `_walk` passes b on to the three users. I1 picks the shape so that all three see it. Each user keeps "none" as is (exact: no missed commit, row 21). If it would report ≥ 1 entry, it gives `not checked (shallow boundary <b7> below the cutoff; <n> unconfirmed entries; run git fetch --unshallow)` + note, failed=False, flagged {} (so no SKIPPED from 062) | units, b | UNTRACKED CHANGE / RESEARCH CODE / REAL-DATA FIELD lines | Fixture (d): `UNTRACKED CHANGE: not checked (shallow boundary <b'7> below the cutoff; 2 unconfirmed entries; run git fetch --unshallow) (cutoff <C7> from --untracked-from)`, exit 0; the full clone of (d) → `none`; m3 fails (d) | (d): S ∩ R = 0 of 1, below = 1 of 1, entries 2 (Z diff-tree, Y scripts/y.py); full walk 1 commit (M), 0 entries. Self-check row 5 |
| 4 | research_code: a `None` diff never becomes `[]` (replace `files or []`). If any unit has `files is None`, return `("not checked (see UNTRACKED CHANGE)", {})`. 053 already reports that commit loudly | units | RESEARCH CODE line | Fixture (f): `walked` with one `(sha, None)` unit → not "none"; m4 (`files or []` restored) fails (f) | – |
| 5 | REAL-DATA FIELD (070): no separate walk. It already maps a `_walk` error to not checked (L733), and the step 3 rule applies to its entries | walked, `_item_triggers` | REAL-DATA FIELD line | (a), (b): `REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)`; (a) also `RESEARCH CODE: not checked (see UNTRACKED CHANGE)` | – |
| 6 | tests/test_pipeline_check.py fixtures, each marked `@NO_GIT`. Each shallow fixture writes the full 40-char sha + "\n" into `<git rev-parse --git-common-dir>/shallow` and asserts `--is-shallow-repository` == "true" first. (a) C→P→B, side D (parent C), M = merge(B, D); S={B}. (b) C→T, side C→Q→B2, M = merge(T, B2); S={B2} (pins the whole-range choice). (c1) (a) with no shallow file → today's answer. (c2) full repo, M = merge(U, T) with U an unrelated root as first parent (`--allow-unrelated-histories`) → line contains `<U7> (git diff-tree failed)`, exit 1 (pins F6). (d) Z root; Y (parent Z, adds scripts/y.py); b' (parent Y, notes only); C (parent b'); T (parent C, notes only); M = merge(first parent Y, second T); S={b'}; cutoff C. (e) `git worktree add --detach` of (a)'s M, run in the worktree → same text as (a). (f) unit test from step 4. Every non-code change uses a notes/ path | fixture repos in tmp_path | 7 new tests | `pytest tests/test_pipeline_check.py` passes; the 053 shallow test still passes | Each fixture's sets are in Self-check rows 1-6 |
| 7 | Mutations, done by I3 in a scratch copy: m1 drop the S ∩ R test → (a), (b), (e) fail (`(git diff-tree failed)`, exit 1). m2 read `.git/shallow` literally → (e) fails (in a worktree `.git` is a file). m3 drop the below rule → (d) fails (`<Z7> (git diff-tree failed); <Y7> scripts/y.py ...`, exit 1). m4 restore `files or []` → (f) fails | step 6 tests | failures listed in 06 | each mutation makes ≥ 1 named test fail | – |
| 8 | Process: daily-audit.md L4 and run-item.md L12, before `check_pipeline.py`: "If `git rev-parse --is-shallow-repository` prints true, run `git fetch --unshallow`, then test again. If it is still true, report UNTRACKED CHANGE, RESEARCH CODE and REAL-DATA FIELD as 'not checked', never 'none'." | the two command files | 2 edited lines | grep both files for `fetch --unshallow`; additions only in `git diff` | – |
| 9 | RI-014 guardrail status in 05/06 (A1 copies it): "GUARDED when 079 is merged and m1 fails fixture (a) on main" | 06 | status line | A1 runs the probe on main | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `--is-shallow-repository` output (step 1) | rev-parse fails or prints neither true nor false (old git) | Read the shallow file anyway: present → shallow; absent → full, today's path (a boundary then gives the loud diff-tree entry, never a pass) |
| `<common-dir>/shallow` (step 1) | missing or unreadable while shallow is true | `not checked (shallow clone; run git fetch --unshallow)`, failed=False |
| `<common-dir>/shallow` empty (step 1) | git registers no grafts (shallow.c) | S = ∅, so the history is complete: today's answer |
| R = `rev-list cutoff..HEAD` (step 2) | git fails | `cutoff <c7>: git rev-list failed` + note, failed=True (existing text) |
| `merge-base --is-ancestor b cutoff` (step 3) | exit not 0 or 1 | `cutoff <c7>: git merge-base failed` + note, failed=True |
| diff-tree of a commit not in S (L611) | fails | `<sha7> (git diff-tree failed)`, failed=True (unchanged); RESEARCH CODE `not checked (see UNTRACKED CHANGE)` (step 4) |
| Commits hidden behind an inside boundary (F3) | not in the shallow repo | `not checked (shallow boundary <b7>; ...)`. Never "none" |
| Full-clone status of entries when a boundary is below the cutoff (step 3) | cannot be computed without the hidden history | `not checked (shallow boundary <b7> below the cutoff; <n> unconfirmed entries; ...)`. Never an error entry, never a pass |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 2, fixture (a) | inside ⇔ S ∩ rev-list(C..M) ≠ ∅ | Shallow edges: M→B, M→D, D→C, (B→P cut). Ancestors of C: {C}. From M: {M, B, D, C}. R = {M, B, D}. S ∩ R = {B} → not checked. Is C an ancestor of M (L600)? Yes, via D → the 053 text does not fire. Full first-parent walk {P, B, M}; shallow walk {B, M} (P hidden, F3) | consistent with the map |
| Step 2, fixture (b) | same | Edges M→T, M→B2, T→C, (B2→Q cut). R = {M, T, B2}. S ∩ R = {B2} → not checked. The full first-parent walk {T, M} contains no boundary, so a first-parent-only check would have passed it: this pins the whole-range choice | consistent |
| Step 2, fixture (c1)/(c2) | not shallow → today's path | (c1) S = ∅. (c2) first-parent walk C..M = {U, M}; `U^1` does not exist → `<U7> (git diff-tree failed)`, failed=True → exit 1. U ∉ S because there is no shallow file | consistent (F6 kept loud) |
| Step 2, mutation m1 on (a) | no S ∩ R → diff-tree B^1 | B^1 cut → diff fails → entry `<B7> (git diff-tree failed)` → failed → exit 1 ≠ the pinned exit 0 | test fails, as required |
| Step 3, fixture (d) | below ⇔ S ∩ R = ∅ and is-ancestor(b', C) | Shallow edges: M→Y, M→T, T→C, C→b', Y→Z, (b'→Y cut). Ancestors of C: {C, b'}. From M: {M, Y, Z, T, C, b'}. R = {M, Y, Z, T}. S ∩ R = ∅; b' is an ancestor of C → below. Shallow first-parent walk C..M: M→Y→Z, none in {C, b'} → {Z, Y, M}. Entries: Z (root, diff-tree fails) = 1; Y adds scripts/y.py, no step file = 2; M vs Y adds only notes/ (from b', C, T) = 0. n = 2. Full: ancestors of C = {C, b', Y, Z}; first-parent walk = {M}; 0 entries → `none` | n = 2 in the expected text; full = none, so "same answer or not checked" holds. m3 gives 2 entries, exit 1 |
| Step 3, "none is exact" | full range ⊆ shallow range when S ∩ R = ∅ | Take X in the full range but not the shallow one. X is not an ancestor of C in the shallow view (the shallow ancestor set ⊆ the full one), so X is unreachable from HEAD there. The first cut edge b→p on a full path HEAD→X has b reachable in the shallow view, and b is not an ancestor of C (else X would be). So b ∈ R ∩ S, a contradiction. A commit in both walks has the same first parent and diff, so shallow entries ⊇ full entries | holds, so "none" stays exact |
| Step 1, fixture (e) | S read via `--git-common-dir` | In the worktree, `--git-common-dir` = the main `.git`; the file there holds B → S = {B}, same as (a). A literal `<wt>/.git/shallow` read fails because `.git` is a file (row 7) → S unreadable or empty → m2 changes the line | consistent |
| Message format | the 053 text (L603) puts `+ note` after the closing paren | New texts end `...; run git fetch --unshallow)` + note, e.g. `(cutoff <C7> from --untracked-from)` as at tests L740-741 | consistent |

Recurring issues checked (logs/recurring-issues.md, open/ESCALATED and related):
- RI-001 (ESCALATED): every rule step's Feasibility cell holds a computed set or count per fixture (steps 1-3). None says "always".
- RI-014 (OPEN, this item): the guardrail is in steps 2-9, corrected for the below-cutoff case (rows 21, 33).
- RI-002 (GUARDED): no uncomputable value becomes "none" or an error entry. See Missing inputs and step 4.
- RI-004/RI-005: the fixture examples are checked against their rule (Self-check rows 1-5), not only the arithmetic.
- RI-006: Totals is for check_handoff to confirm. The counts are not to be copied by hand.
- RI-007: a "not checked" must never be reported as "none" (step 8).

check_handoff output (run by the orchestrator 2026-11-19 23:35 UTC, exit 0; must say PASS):
```
sources count (unique URLs in 01-research.md): 9
fact-check rows: 37
totals line: 37 rows -> 32 as-is, 4 fixed, 1 removed
PASS
```