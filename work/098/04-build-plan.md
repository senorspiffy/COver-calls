# 04 Build plan - 098
Fit verdict: FIT WITH CHANGES

Fit check. The account (~$3k), the strategy rules (001) and ccbot/ are not touched. Only pipeline tooling changes (scripts/commit_step.py, scripts/check_pipeline.py, their tests, one sentence in run-item.md). No trading rule the person follows changes, so there is no 001 text to update. 098 is built last on daily-fixes/2026-11-24, after 092, 093, 096, 094, 095 and 097. Four of those touch the same two files, so every anchor below is a function or constant name, never a line number. I2 re-reads each one on the branch as it is when 098 starts. There are five changes to 03:
- C1 (interaction with 095). 095 adds an `unchecked` list to `incomplete()` and one switch helper (03 of 095 names it `_unsure(env)`, keyed on `env == SHALLOW_TEXT`). It routes the gated entries to `INCOMPLETE NOT CHECKED` in a shallow clone, and that includes ROUND_HEADING 05/06. 098's new ROUND_BUILD_FROM gate has the same `seen is False` drop, so it must take the same route, or a shallow clone prints a hard INCOMPLETE that a full clone would drop. That is the 095 bug again, for the new gate. R3 did not see this, because 095 was not built when 03 was written. If 095 was dropped or built under other names, I2 follows what is on the branch and says so in 05.
- C2 (simpler step 2). The no-git fixture path (`_rh_item` in a plain tmp_path, env "no git", strict) already applies the numeric cutoff. `test_read_or_unnamed_heading_is_not_stray[N3-below-cutoff]` already pins 091 as not flagged, so it already kills a-from91. Step 2 therefore only adds a `092` row to `test_stray_round_heading_is_incomplete`, which kills a-from93. No git fixture and no RULE_FILE edit are needed.
- C3 (step 6 wording and reuse). The new check calls `stray_run_headings` with a pattern argument, so the code reads the file the same way as the 091 check (_read, fences, _section_flags). The 03 message says "holds runs", which is not true for a heading with no run under it. The new text says only what is measured. On an unreadable file the new check adds nothing, because the 091 check (ROUND_HEADING_FROM 92 < 99) already gives `<step> round headings not checked`. That keeps it to one entry, not two.
- C4 (rule text for sub-ask 1). "Commits need no amend" holds only if the people who commit know about the option. run-item.md's commit sentence (the one naming `commit_step.py`) gets one sentence about `--trailer`, with a text pin. This is a RULE_PATHS edit and needs the person's OK at PR review, like the script edits.
- C5 (census). 094 and 097 may add git call sites, so the census sum on the branch may no longer be 47 when 098 starts. 098 adds no `_git`/`_git_ok` call site. I2 records the census sum before and after 098 in 05, and the two must be equal.

## Extra research (with sources)
1. `%(trailers:key=<K>,valueonly)` is in the git 2.23.0 pretty-formats doc: "only show trailers with specified key. Matching is done case-insensitively", and valueonly "skip[s] over the key part" ([v2.23.0 pretty-formats.txt](https://code.googlesource.com/git/+/refs/tags/v2.23.0/Documentation/pretty-formats.txt); also [git-scm 2.24.0](https://git-scm.com/docs/pretty-formats/2.24.0)). So the step 1 test (a) and the step 9 I3 check work on any git from 2019 on. No version skip is needed. The test still asserts on `%B` too, so an older git that ignores the placeholder cannot pass silently.
2. commit-tree builds each `-m` as its own paragraph ([git-commit-tree](https://git-scm.com/docs/git-commit-tree)), and the trailer block is the last paragraph ([git-interpret-trailers](https://git-scm.com/docs/git-interpret-trailers)). The single joined final `-m` (03 step 1) is the only shape the docs guarantee. M1a (one `-m` per trailer) is run and its result goes in 05, not assumed (03 row 01 1.6).
3. Edge R3 missed: `--trailer=Key: v` (the `=` form) is not parsed as an option. It becomes argv[0] and is refused by the existing bad-ID check (`ID '--trailer=...' is not 3 digits`, exit 2, nothing written). The module docstring says the two-argument form is the only form. One test pins that refusal. It adds no new refusal condition, so it needs no new mutant.
4. Edge R3 missed: in the step 5 corrupt-ref fixture, 097's stash check (`git stash list`) and 094's refspec read may also fail or print a line. So step 5 asserts the named lines with `_pick` and the exit code, never the whole output.
5. Symlinks: `os.symlink` can fail where the OS or the user may not create links ([Python os.symlink](https://docs.python.org/3/library/os.html#os.symlink)). The step 4 test skips with that reason when `os.symlink` raises OSError, never passes silently. The CI host is Linux, so it runs there.

## Files to create/change
1. scripts/commit_step.py
   - `main(argv)`: before the existing `len(argv) < 3` check, read the leading `--trailer <value>` pairs (repeatable, only before the ID). A `--trailer` that is the last argument → usage text, exit 2. The rest goes to `commit(item, subject, paths, trailers=...)`.
   - New `_trailer_ok(t)` (or inline in `commit`), run first in `commit`, before `rev-parse --show-toplevel`. The five refusal conditions, each a `Refused("trailer <repr>: <part> (item 098)")`: (1) no `": "`; (2) key (text before the first `": "`) not `re.fullmatch(r"[A-Za-z0-9-]+")`; (3) value empty after strip; (4) `\r` or `\n` anywhere; (5) the flag with no value, which is `main`'s usage exit 2.
   - `commit`: when trailers are given, the commit-tree call becomes `["commit-tree", tree, "-p", old, "-m", subject, "-m", "\n".join(trailers)]`. With no trailers the argv is byte-identical to today's. The reflog `-m f"commit_step: {subject}"`, the `Item <ID>: ` subject rule and every other refusal stay as they are.
   - Module docstring: Usage line `python3 scripts/commit_step.py [--trailer "<Key>: <value>"]... <ID> "<subject>" <path>...`. In (i), the trailer refusals (before any git call). In (v), the message is `subject`, a blank line, then one trailer paragraph. Only the two-argument form is read (`--trailer=...` is refused as a bad ID).
2. scripts/check_pipeline.py
   - `_anchor_env`: the `head[1] == 1` return becomes `"HEAD names no commit: unborn or unresolvable", False`. Rewrite the docstring's last sentences: the label covers both cases, both strict; a corrupt ref also fails UNCOMMITTED STEP's ls-tree (128 measured, 088 audit). Remove "the label is not accurate ... follow-up". Also update the item-088 module text paragraph (`not checked (unborn HEAD)`), the comment above `SHALLOW_TEXT` (`"unborn HEAD"` → the new label), and 095's docstring "known gaps" text if it names the old label. No new git call.
   - New constants next to `ROUND_HEADING_FROM`/`STRAY_RUN_HEADING`: `ROUND_BUILD_FROM = 99` (comment: item 098) and `ROUND_BUILD_HEADING = re.compile(r"#{1,6} round \d+ build\b", re.I)`, used only with `.match` (RI-012).
   - `stray_run_headings(path, opener, pattern=STRAY_RUN_HEADING)`: a pattern argument with the old default. The 091 call site is unchanged.
   - `incomplete()`: after the ROUND_HEADING_FROM block, add `if int(item_dir.name) >= ROUND_BUILD_FROM:`. For 05 and 06, call `stray_run_headings(..., RUN_HEADING[step], ROUND_BUILD_HEADING)`. On `why`, add nothing (C3). When headings are found, `fired = f"{step} heading '{named}' is a build-round heading LOG BATCH does not read; put its runs under '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 098)"`. Gate with `_rule_seen(item_dir, step, "ROUND_BUILD_FROM", env)` exactly as in the ROUND_HEADING block: `False` → not_seen `(ID, step, sha7, "ROUND_BUILD_FROM", "098", "no round-build check")`; 095's shallow switch → `unchecked` (C1); else `missing += [fired] + note`. Add a sentence on item 098 to the `incomplete` docstring and one to the module help next to the STRAY_RUN_HEADING text.
3. tests/test_commit_step.py: the tests in "Tests and checks" T-a to T-g.
4. tests/test_pipeline_check.py: the tests in "Tests and checks" P-a to P-h. Also update the 088 (h) pins in the unborn-HEAD test (`RULE NOT SEEN: not checked (...)`, `cp._anchor_env() == (...)`, the two `_rule_seen(..., "unborn HEAD")` env strings) to the new label. Edit only the `("_anchor_env", "_git")` census reason string if its text names the label; its count stays.
5. .claude/commands/run-item.md: in the commit paragraph, right after the sentence that names `python3 scripts/commit_step.py <ID> "<subject>" <paths>...`, add exactly: "Attribution trailers go on the same call, as `--trailer \"<Key>: <value>\"` before `<ID>` (one per trailer); a step commit is never amended afterwards (item 098)." (C4)

05 (I2) and 06 (I3) are step files and are not counted.

## Tests and checks
commit_step (tests/test_commit_step.py, `repo` fixture):
- T-a (03 step 1 a): `_cli(repo, "--trailer", "Co-Authored-By: A <a@a>", "--trailer", "Claude-Session: https://x/y", "150", f"Item 150: {L150}", R05)` → exit 0. `%(trailers:key=Co-Authored-By,valueonly)` == `A <a@a>` and the same for Claude-Session. `%s` == subject. `%B` == `subject\n\nCo-Authored-By: A <a@a>\nClaude-Session: https://x/y\n`. The tree equals the tree of a no-trailer run of the same item on a fresh copy of the fixture. The reflog `%gs` == `commit_step: <subject>`.
- T-b (03 step 1 b): parametrized over the five refusals. Each has exit 2, the named part in stderr, and `_state` unchanged: `Co Authored: x` (key with a space), `Key:value` (no `": "`), `Key:   ` (empty value), `Key: a\nb` (newline), `Key: a\rb` (CR), and `--trailer` as the last argument (usage). The \r and \n cases are one condition with two rows.
- T-c (03 step 1 c): no `--trailer` → `%B` == `subject\n` (today's message, byte for byte).
- T-d (research 3): `--trailer=K: v` first → exit 2, `ID '--trailer=K: v' is not 3 digits`, `_state` unchanged.
- T-e (03 step 3): `_cli` with `cwd=repo / "work" / "150"` and path `work/150/05-build-report.md` → exit 2, `not the top of a git work tree` in stderr, `_state` unchanged. `_cli` gets an optional `cwd` argument, default `r`.
- T-f (03 step 4): commit `work/150/real.md`, then `os.symlink("real.md", repo/"work/150/lnk.md")` (skip on OSError, research 5). Commit it through commit_step → `git ls-tree HEAD work/150/lnk.md` mode `120000`, `git cat-file -p HEAD:work/150/lnk.md` == `real.md`.
- T-g (C4): `run-item.md` text count of the step 5 sentence == 1.

check_pipeline (tests/test_pipeline_check.py):
- P-a (03 step 2, C2): add `("05", RH_P1, "### Test output (round 2, pasted)", "092")` to `test_stray_round_heading_is_incomplete` through a new `item` parameter. The expected INCOMPLETE line uses that item. The existing rows use RH_ID.
- P-b (03 step 6): no-git fixture `_rh_item(tmp_path, body05="## Round 2 build\n```\n2 passed in 1.50s\n```\n", item=...)` parametrized over `099` (one INCOMPLETE entry with the new text, exit 1) and `098` (INCOMPLETE: none, exit 0). Also `150` with the heading in 06 (`## Round 2 build`).
- P-c (03 step 6 negatives, RI-012): at 150, `## Round 2 builder notes`, `## Round 2 build` inside a fence, `### Round 2 build` inside `## Test output (pasted)`, and `Round 2 build` as prose not at the line start → `INCOMPLETE: none`. Positive case-fold row: `## round 2 Build` → flagged.
- P-d (03 step 6 gate): a git fixture like `test_round_heading_gate_follows_rule_file_of_05_commit`, parametrized seen/not seen. The RULE_FILE holds `ROUND_HEADING_FROM = 92` always and `ROUND_BUILD_FROM = 99` only when seen. Not seen → `RULE NOT SEEN: 150 (05 added in <sha7> without ROUND_BUILD_FROM (098): judged by no round-build check; item 084)` and `INCOMPLETE: none`. Seen → the entry and `RULE NOT SEEN: none`.
- P-e (C1): with 095's switch built, call `cp.incomplete(d, env=cp.SHALLOW_TEXT, not_seen=[], unchecked=u)` (using 095's argument name) on a no-git 150 item with `## Round 2 build`. The new entry is in `u` and not in the return value. Twin with env `"no git"`: the entry is in the return value.
- P-f (missing inputs): an unreadable 05 at 150 gives exactly one `05 round headings not checked` entry (count == 1). `stray_run_headings(<absent path>, RUN_HEADING["05"], cp.ROUND_BUILD_HEADING)` == `([], None)`. With `_rule_seen` monkeypatched to return `(None, "05 anchor: git failed (item 084)")` for ROUND_BUILD_FROM, the entry and that note are both in INCOMPLETE.
- P-g (03 step 5): `test_rule_anchor_corrupt_ref_is_strict`, parametrized `corrupt` (assert the loose `.git/refs/heads/main` exists, then write `garbage\n`) and `dangling` (`git symbolic-ref HEAD refs/heads/nope` after a commit). Env pins: `rev-parse --verify -q HEAD` returncode == 1; `ls-tree HEAD` returncode != 0; then a separate `== 128` assert whose message names `git --version`. `_pick` lines: `RULE NOT SEEN: not checked (HEAD names no commit: unborn or unresolvable)`, `UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)` (as it is on the branch), exit 1. Text pin: `cp.__doc__` and `cp._anchor_env.__doc__` hold the new label, and neither holds `not checked (unborn HEAD)`.
- P-h: `test_git_call_census` passes unchanged after 098 (C5).

Mutants (I2 runs each one and records it in the 05 Mutations table; I3 re-runs them, 03 step 7). Each must fail the named test:
- M1a: each trailer in its own `-m` → T-a. The result is recorded either way, per 03 row 1.6. If git still makes both trailers, it is recorded as equivalent with the `%B` output.
- M1b: trailers not passed to commit-tree → T-a.
- M1c to M1g: each of the five checks removed in turn → T-b's matching row. For the flag with no value, removing it in `main` → an IndexError or a wrong exit, so the row fails.
- a-nocwd: drop `topdir != Path.cwd().resolve()` → T-e. The `topdir is None or` drop is recorded as equivalent, with the existing pin `test_t3_no_git_and_not_a_repo` (03 step 3).
- a-resolvename: `a.resolve()` in `repo_relative` → T-f.
- a-from93: `ROUND_HEADING_FROM = 93` → P-a[092]. a-from91 → N3-below-cutoff (existing).
- b-from100: `ROUND_BUILD_FROM = 100` → P-b[099]. b-from98 → P-b[098].
- b-gate: gate removed (always strict) → P-d not seen.
- b-word: `\b` dropped → P-c builder notes. b-case: `re.I` dropped → P-c `## round 2 Build`. b-search: `.match` → `.search` → P-c prose row.
- b-shallow: the new block skips 095's switch → P-e.
- b-unread: the new block adds its own unreadable entry → P-f count.
- h-label: old label restored → P-g and the updated (h) pins.
- r-text: the run-item sentence removed → T-g.

Full suite: `python3 -m pytest -q` passes, and `python3 scripts/check_pipeline.py` shows nothing new for 098 beyond the steps still to run.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Scope note: broad SUMMARY_LINE rule not built; heading rule with its own cutoff | Files 2 (`ROUND_BUILD_FROM`, `ROUND_BUILD_HEADING`); broad rule DROPPED: residual (a), unmeasured (RI-001) |
| Step 1 trailer option, validation, single final `-m`, byte-identical when absent, docstring | Files 1; T-a, T-b, T-c, T-d; M1a-M1g |
| Step 2 092/091 boundary pins | Files 4 P-a (C2: no-git path, no RULE_FILE edit); a-from93, a-from91 (existing N3) |
| Step 3 subdir cwd refusal; `topdir is None` equivalent | T-e; a-nocwd; the equivalent is recorded in 05 |
| Step 4 symlink staged as a link | T-f; a-resolvename |
| Step 5 neutral HEAD label, docstring, module text, comment, pins, corrupt/dangling fixture, census | Files 2 `_anchor_env` text; Files 4 (h) pins; P-g; P-h; h-label |
| Step 6 ROUND_BUILD_FROM, heading regex `.match` re.I, gate, fences, read section, module help | Files 2; P-b, P-c, P-d; b-from100, b-from98, b-gate, b-word, b-case, b-search. Message reworded (C3) |
| Step 7 mutation list in 05 | Tests and checks "Mutants" list, all recorded in the 05 Mutations table |
| Step 8 build order 2, 3, 4, then 5, 1, 6; re-read after rebase | Kept: I2 builds T-e, T-f and P-a first, then step 5, then step 1 (then T-g/run-item), then step 6. Anchors by name; census before and after (C5) |
| Step 9 no amend on 098's own commits | Files 5 sentence (C4); I3 checks `%(trailers)`, `%s` and the reflog `commit_step: <subject>` with no `commit (amend)` for each 098 commit made after step 1 is built |
| Residual (a) broad N5 rule | DROPPED: follow-up item for the daily review (needs a shell measurement) |
| Residual (b) FROM pins for the other 7 constants | DROPPED: follow-up item, out of scope (03) |
| Residual (c) mutant-rule sentence in i1 text | DROPPED: follow-up, a RULE_PATHS edit that needs the person's OK |
| Missing inputs: `--trailer` absent | T-c |
| Missing inputs: `--trailer` value missing or malformed | T-b (all five), T-d |
| Missing inputs: git `trailer.*` config | DROPPED as a test: not an input (commit-tree does not apply it; interpret-trailers is not called). The test fixture sets GIT_CONFIG_GLOBAL=devnull |
| Missing inputs: RULE_FILE anchor absent (env set, uncommitted) | P-e (shallow env), P-b (no git, strict); existing 088 uncommitted tests cover the shared `_rule_seen` path |
| Missing inputs: anchor git call fails | P-f (monkeypatched `_rule_seen`) |
| Missing inputs: 05/06 absent | P-f (`([], None)`) |
| Missing inputs: 05/06 unreadable | P-f (one entry, from 091) (C3) |
| Missing inputs: HEAD rev-parse exit 1 | P-g |
| Missing inputs: HEAD other non-zero | existing `_anchor_env` monkeypatch test (exit 128 → failed True), unchanged |
| Missing inputs: ls-tree not 128 | P-g separate `== 128` assert with `git --version` |
| Missing inputs: screen tickers n/a | n/a: no ticker screen in this item |
| Self-check rows (boundaries, trailers, message shape, negatives, mode 120000, feasibility, env pins, census, totals) | Each maps to the test above it in the list; census row changed to "unchanged by 098" (C5) |

## Guardrail tests
- Feasibility: trailer key filter (2 of 2 session trailers pass, 0 of 2 negatives) → T-a (both keys) and T-b (`Co Authored`, `Key:value`).
- Feasibility: ROUND_HEADING_FROM boundary 92/91 → P-a[092] and N3-below-cutoff[091].
- Feasibility: round-build heading (1 of 39 `Round N` headings in work/*/0[56], 076/05 L6, item 76 < 99; 0 files at items >= 99 on 2026-11-24) → P-b[099] flagged, P-b[098] not flagged. I2 also runs the real tree: `check_pipeline.py` shows no new INCOMPLETE entry from item 098 (expected count 0), and records that in 05.
- Missing inputs: `--trailer` absent → T-c; malformed → T-b, T-d.
- Missing inputs: anchor not read (shallow / no git / git failed) → P-e, P-b, P-f.
- Missing inputs: 05/06 absent or unreadable → P-f.
- Missing inputs: HEAD names no commit → P-g.

## Expected result
- A step commit made as `commit_step.py --trailer "Co-Authored-By: ..." --trailer "Claude-Session: ..." <ID> "<subject>" <paths>` has the message `<subject>\n\n<t1>\n<t2>\n`. `git log --format=%(trailers)` shows both, and no `git commit --amend --only` follows. With no trailers, commits are byte-identical to today's.
- `## Round 2 build` (any level, any case) outside a read section of an item >= 099's 05/06 is one INCOMPLETE entry per file. It is RULE NOT SEEN when the 05/06 commit predates the constant, and INCOMPLETE NOT CHECKED in a shallow clone (095). Items <= 098 and the real tree today: no change.
- An unborn, corrupt or dangling HEAD prints `RULE NOT SEEN: not checked (HEAD names no commit: unborn or unresolvable)`. The corrupt and dangling cases also give the UNCOMMITTED STEP ls-tree error (exit 1).
- 15+ new or edited tests pass. Every non-equivalent mutant listed fails its named test. Equivalent mutants (`topdir is None or`, M1a if git keeps both trailers) are recorded with the reason. The census sum is unchanged by 098.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): every filter and window has a dated count (Feasibility above) and a pinning test. The broad rule with no count is dropped.
- RI-010 (ESCALATED): sub-asks 1 and 3 are its near misses. Every new refusal and cutoff has a mutant. The no-amend rule is now rule text with a pin (C4), and I3 checks it on 098's own commits.
- RI-014 (OPEN): the HEAD label changes with no new git call (census, C5). The shallow route for the new gate is planned (C1).
- GUARDED entries, also checked: RI-002 (absent inputs are never filled; P-e, P-f, P-g); RI-004/005 (Self-check rows re-derived: 92/91, 99/98, octal 120000); RI-006 (no hand totals here); RI-007 (FULL scope, code allowed); RI-009 (built on the shared branch after 097; anchors by name); RI-011 (no branch-diff change); RI-012 (`.match` with a prose negative and a `\b` negative); RI-013 (no realtest change); RI-003 and RI-008 (no calendar change; no new f-string nesting, and I2 runs py_compile on 3.10/3.11 where available).

Log fields: FIT WITH CHANGES | 5 files planned
