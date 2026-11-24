# 05 Build report - 098
Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/i2-098-r1-o4kmhanx

Built by I2 on branch `daily-fixes/2026-11-24`, base 7eaa6767303b60691e49192666f71ac0ae7cf39f (097's I3 line; 092-097 already built). I made the scratch dir with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-098-r1-", dir="/tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad"))'`. Mutants ran in `<scratch dir>/wt` (`git worktree add --detach`), with the 5 built files copied in; each mutant file was restored from the main checkout's copy (`shutil.copyfile`), never with `git stash`. `git stash list` in the main checkout: empty, exit 0.

RULE_PATHS are touched (.claude/commands/run-item.md, scripts/check_pipeline.py, tests), so **the person's OK is needed at PR review**.

## Changes made (file: what changed)
- `scripts/commit_step.py`
  - `main(argv)`: reads leading `--trailer <value>` pairs (repeatable, only before the ID). A `--trailer` with no value prints the usage (module docstring), exit 2. The rest goes to `commit(..., trailers=trailers)`.
  - New `_trailer_ok(t)`, called first in `commit` for each trailer, before `rev-parse --show-toplevel`. Refusals (`Refused`, exit 2): CR or LF (`holds a CR or LF`); no `": "` (`no ': ' after the key`); key not `re.fullmatch(r"[A-Za-z0-9-]+")` (`key '<k>' is not ASCII letters, digits and '-'`); value empty after strip (`empty value`). Each message is `trailer <repr>: <part> (item 098)`.
  - `commit(..., trailers=())`: `msg = ["-m", subject] + (["-m", "\n".join(trailers)] if trailers else [])`, then `commit-tree tree -p old *msg`. With no trailers the argv is today's (`-m subject` only). Reflog text, subject rule and all other refusals unchanged.
  - Module docstring: Usage line with `[--trailer "<Key>: <value>"]...`; a paragraph that `--trailer` is only read before `<ID>`, only in the two-argument form (`--trailer=...` is refused as a bad ID); (i) lists the trailer refusals before any git call; (v) describes the one final trailer paragraph.
- `scripts/check_pipeline.py`
  - `_anchor_env`: rev-parse exit 1 now returns `"HEAD names no commit: unborn or unresolvable", False`. Docstring rewritten: the one label covers unborn, corrupt ref and dangling symbolic HEAD, both strict; the "label is not accurate ... follow-up" text is removed.
  - Module text: the item-088 paragraph now says `not checked (HEAD names no commit: unborn or unresolvable)` (item 098); 095's known gap says "no-commit-HEAD entries"; the cost sentence adds "9 from ROUND_BUILD_FROM on (05 and 06 ROUND_BUILD_FROM, item 098 ...)" (Deviations 2). The comment above `SHALLOW_TEXT` and the `_unsure` docstring no longer name "unborn HEAD". `grep -n "unborn HEAD" scripts/check_pipeline.py` now prints nothing.
  - New constants: `ROUND_BUILD_FROM = 99` (comment: item 098, 10th `*_FROM` cutoff), placed after `SCRATCH_FROM`; `ROUND_BUILD_HEADING = re.compile(r"#{1,6} round \d+ build\b", re.I)` next to `STRAY_RUN_HEADING`, used only via `.match`.
  - `stray_run_headings(path, opener, pattern=STRAY_RUN_HEADING)`: pattern argument, old default; the 091 call site is unchanged.
  - `incomplete()`: after the ROUND_HEADING_FROM block, `if int(item_dir.name) >= ROUND_BUILD_FROM:` for 05 and 06 calls `stray_run_headings(..., RUN_HEADING[step], ROUND_BUILD_HEADING)`. On `why` it adds nothing (the 091 block already gives `<step> round headings not checked`, C3). On headings: `fired = "<step> heading '<h>' is a build-round heading LOG BATCH does not read; put its runs under '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 098)"`, gated by `_rule_seen(item_dir, step, "ROUND_BUILD_FROM", env)`: False → not_seen `(ID, step, sha7, "ROUND_BUILD_FROM", "098", "no round-build check")`; 095's switch `unsure(step)` → `unchecked` (C1; 095 is on the branch as `_unsure(item_dir, step, env, committed)` behind the local `unsure(step)`); else `missing += [fired] + note`. `incomplete` docstring: an item-098 sentence and "build-round headings" in 095's list. Module help: an item-098 paragraph after the item-091 STRAY_RUN_HEADING text; 091's "Known gaps" no longer lists `## Round 2 build`.
- `tests/test_commit_step.py`: `_cli(r, *args, cwd=None)`. New: `test_trailers_make_one_final_paragraph` (T-a), `test_trailer_refusals_write_nothing` (T-b, 6 rows: key-space, no-colon-space, empty-value, lf, cr, no-value), `test_no_trailer_message_is_subject_only` (T-c), `test_trailer_equals_form_is_a_bad_id` (T-d), `test_subdir_cwd_is_refused` (T-e), `test_named_symlink_is_committed_as_a_link` (T-f, skips on OSError from `os.symlink`), `test_trailer_rule_text` (T-g, `TRAILER_RULE` count == 1).
- `tests/test_pipeline_check.py`: `HEAD_NONE` constant; the 088 (h) pins in `test_rule_anchor_unborn_head_is_strict` use it (RULE NOT SEEN text, `_anchor_env()`, two `_rule_seen` env strings). `test_stray_round_heading_is_incomplete` gets an `item` parameter and row `P1-at-cutoff-092` (P-a). New: `test_round_build_heading_is_incomplete` (P-b: 099, 098, 150-in-06), `test_round_build_heading_negatives` (P-c: builder word, in fence, inside read section, prose not at start; positive case fold), `test_round_build_gate_follows_rule_file_of_05_commit` (P-d, not-seen/seen), `test_round_build_shallow_goes_to_unchecked` (P-e, shallow/no-git), `test_round_build_missing_inputs` (P-f), `test_rule_anchor_corrupt_ref_is_strict` (P-g, corrupt/dangling). `GIT_CENSUS` and `test_git_call_census` unchanged (P-h).
- `.claude/commands/run-item.md`: one sentence added in the commit paragraph: "Attribution trailers go on the same call, as `--trailer \"<Key>: <value>\"` before `<ID>` (one per trailer); a step commit is never amended afterwards (item 098)." (placement: Deviations 1).

File counts (item 012), before this 05 was written:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
5
```
```
$ git diff --stat
 .claude/commands/run-item.md |   2 +-
 scripts/check_pipeline.py    |  72 +++++++++++++------
 scripts/commit_step.py       |  43 ++++++++++--
 tests/test_commit_step.py    |  92 ++++++++++++++++++++++++-
 tests/test_pipeline_check.py | 160 +++++++++++++++++++++++++++++++++++++++----
 5 files changed, 326 insertions(+), 43 deletions(-)
```
5 files changed, 0 new, matching the plan's 5 files.

## Connectivity check
- [x] every new function/rule is used: `_trailer_ok` is called by `commit`; the `trailers` argument is fed by `main` and read by the commit-tree call; `ROUND_BUILD_FROM` is read by `incomplete` and by name in `_rule_seen`; `ROUND_BUILD_HEADING` is passed to `stray_run_headings`; the `pattern` argument is read in its list comprehension; the run-item sentence has a count pin (T-g).
- [x] every input has a source, every output has a consumer: argv → trailer paragraph of the commit message (read by `git log %(trailers)`, I3 step 9); 05/06 text → INCOMPLETE / RULE NOT SEEN / INCOMPLETE NOT CHECKED and the exit code; `_anchor_env`'s label → `RULE NOT SEEN: not checked (...)`.
- [x] every branch ends in a defined result: no trailer → today's message; bad trailer → exit 2 naming the part, nothing written; `--trailer` last → usage, exit 2; `--trailer=...` → bad-ID refusal, exit 2. Build-round check: below 099 → no check; absent file → `([], None)`, no entry; unreadable → 091's one `not checked` entry; no heading → nothing; heading → not seen (RULE NOT SEEN row) / shallow-committed (INCOMPLETE NOT CHECKED) / anchor failed (entry + note) / else strict entry. HEAD exit 1 → neutral label, strict; other exits unchanged.
- [x] no leftover TODOs or unused files: `git diff | grep -c "^+.*TODO"` gives 0. Scratch files only in my scratch dir; the worktree is removed before handback.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l`): `38`, all from before this item; `git diff --stat -- ccbot/` is empty. The same pattern plus `: float = ` on the added lines of scripts/ (`git diff -U0 scripts/ | grep -E "^\+.*(or 0|else 0|is not None and|: float = )"`): no output. No dataclass added. The one new `>=` is `int(item_dir.name) >= ROUND_BUILD_FROM` (ints from an `isdigit()` name, never NaN). An absent `--trailer` adds no trailer by default (attribution is never hard-coded).
- Census (C5): `test_git_call_census` asserts `sum(seen.values()) == 51` before (base 7eaa676) and after; 098 adds no `_git`/`_git_ok` call site, and the test passes unchanged.
- py_compile: `python3.11 -m py_compile scripts/commit_step.py scripts/check_pipeline.py` → `python3.11 ok` (python3.10 not installed). Suite python is 3.13.18; git 2.43.0.

## Test output (pasted, not summarized)
Each later round's runs go under their own level-2 heading `## Test output (round N, pasted)`, never under a `###` heading or a `Round N ...` heading (item 091).

`python3 -m pytest -q` from the repo root, after every code and test edit (tail):
```
........................................................................ [ 91%]
........................................................................ [ 98%]
..........                                                               [100%]
945 passed, 1 skipped in 118.53s (0:01:58)
```
Suite: 945 passed, 1 skipped in 118.53s (0:01:58)

`python3 -m pytest -q -rs tests/test_commit_step.py tests/test_pipeline_check.py` (no skip, so T-f's symlink test ran):
```
525 passed in 66.92s (0:01:06)
```

`python3 scripts/check_pipeline.py` (exit 0), lines for this item and the checks named in run-item:
```
098: in progress (FULL: next 05)
INCOMPLETE: none
UNTRACKED CHANGE: none
STASH: none
SKIPPED: none
```
(`RULE NOT SEEN:` names only 083, as at base; `LOG TIME:` and `LOG BATCH:` name only 048/083 and the old not-computable items, as at base.)

### Mutations (scratch worktree, `python3 <scratch>/mut.py <scratch>/wt`, output as printed)
```
M1a | exit 1 | 1 failed in 0.51s | FAILED tests/test_commit_step.py::test_trailers_make_one_final_paragraph
M1b | exit 1 | 1 failed in 0.18s | FAILED tests/test_commit_step.py::test_trailers_make_one_final_paragraph
M1c-key | exit 1 | 1 failed in 0.13s | FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[key-space]
M1d-sep | exit 1 | 1 failed in 0.11s | FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[no-colon-space]
M1e-empty | exit 1 | 1 failed in 0.14s | FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[empty-value]
M1f-crlf | exit 1 | 2 failed in 0.23s | FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[lf]; FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[cr]
M1g-novalue | exit 1 | 1 failed in 0.12s | FAILED tests/test_commit_step.py::test_trailer_refusals_write_nothing[no-value]
a-nocwd | exit 1 | 1 failed in 0.11s | FAILED tests/test_commit_step.py::test_subdir_cwd_is_refused
a-nocwd-isnone(equiv) | exit 0 | 2 passed in 0.10s | 
a-resolvename | exit 1 | 1 failed in 0.20s | FAILED tests/test_commit_step.py::test_named_symlink_is_committed_as_a_link
a-from93 | exit 1 | 1 failed in 0.87s | FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P1-at-cutoff-092]
a-from91 | exit 1 | 1 failed in 0.27s | FAILED tests/test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N3-below-cutoff]
b-from100 | exit 1 | 1 failed in 0.29s | FAILED tests/test_pipeline_check.py::test_round_build_heading_is_incomplete[099-at-cutoff]
b-from98 | exit 1 | 1 failed in 0.26s | FAILED tests/test_pipeline_check.py::test_round_build_heading_is_incomplete[098-below-cutoff]
b-gate | exit 1 | 1 failed in 0.43s | FAILED tests/test_pipeline_check.py::test_round_build_gate_follows_rule_file_of_05_commit[not-seen]
b-word | exit 1 | 1 failed in 0.26s | FAILED tests/test_pipeline_check.py::test_round_build_heading_negatives[N-builder-word]
b-case | exit 1 | 1 failed in 0.30s | FAILED tests/test_pipeline_check.py::test_round_build_heading_negatives[P-case-fold]
b-search | exit 1 | 1 failed in 0.27s | FAILED tests/test_pipeline_check.py::test_round_build_heading_negatives[N-prose-not-at-start]
b-shallow | exit 1 | 1 failed in 0.19s | FAILED tests/test_pipeline_check.py::test_round_build_shallow_goes_to_unchecked[shallow]
b-unread | exit 1 | 1 failed in 0.26s | FAILED tests/test_pipeline_check.py::test_round_build_missing_inputs
h-label | exit 1 | 3 failed in 0.85s | FAILED tests/test_pipeline_check.py::test_rule_anchor_corrupt_ref_is_strict[corrupt]; FAILED tests/test_pipeline_check.py::test_rule_anchor_corrupt_ref_is_strict[dangling]; FAILED tests/test_pipeline_check.py::test_rule_anchor_unborn_head_is_strict
r-text | exit 1 | 1 failed in 0.05s | FAILED tests/test_commit_step.py::test_trailer_rule_text
```
| Mutant | Change | Result |
|---|---|---|
| M1a | each trailer in its own `-m` | killed. Not equivalent: git kept only the last paragraph's trailer. Measured: `%(trailers:key=Co-Authored-By,valueonly)` gave `'\n'` (empty) instead of `'A <a@a>\n\n'` (03 row 01 1.6: now measured) |
| M1b | trailers not passed (`*msg[:2]`) | killed |
| M1c-M1g | each of key / `": "` / empty value / CR-LF / no-value check removed | each killed by its own T-b row(s) |
| a-nocwd | drop `topdir != Path.cwd().resolve()` | killed (T-e) |
| `topdir is None or` dropped | equivalent | survives as expected: `None != Path(...)` is True, same message; pinned by `test_t3_no_git_and_not_a_repo` (passes under it) |
| a-resolvename | `a.resolve()` | killed (T-f) |
| a-from93 / a-from91 | ROUND_HEADING_FROM 93 / 91 | killed (P-a[092] / existing N3) |
| b-from100 / b-from98 | ROUND_BUILD_FROM 100 / 98 | killed (P-b[099] / P-b[098]) |
| b-gate | `_rule_seen` replaced by `(None, "")` (always strict) | killed (P-d not-seen) |
| b-word / b-case / b-search | `\b` dropped / `re.I` dropped / `.search` | killed (P-c rows) |
| b-shallow | `unsure(step)` branch removed | killed (P-e shallow) |
| b-unread | own unreadable entry added | killed (P-f count) |
| h-label | old label `unborn HEAD` | killed (P-g both rows + updated (h) pins) |
| r-text | run-item sentence removed | killed (T-g) |

## Feasibility numbers (plan Guardrail tests)
- Trailer key filter: 2 of 2 session trailers pass (T-a uses `Co-Authored-By` and `Claude-Session`; this item's own commit uses the two real session trailers), 0 of 2 negatives (`Co Authored`, `Key:value`, T-b).
- ROUND_HEADING_FROM boundary: 092 flagged (P-a), 091 not (N3).
- Round-build heading on the real tree, 2026-11-24: `grep -rniE "^#{1,6} round [0-9]+ build\b" work/*/0[56]-*.md` → 1 line (`work/076/05-build-report.md:6:## Round 2 build`, item 76 < 99). `grep -rniE "^#{1,6} round [0-9]+" work/*/0[56]-*.md | wc -l` → `40` (03 counted 39 before 092-097 were built; the extra one is below 099). Real `check_pipeline.py`: `INCOMPLETE: none`, so 0 new entries from 098 (expected 0).
- P-g env pins (git 2.43.0): `rev-parse --verify -q HEAD` exit 1 and `ls-tree HEAD` exit 128 in both the corrupt and the dangling fixture (the asserts pass).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat` lists only .claude/commands/run-item.md, scripts/check_pipeline.py, scripts/commit_step.py, tests/test_commit_step.py, tests/test_pipeline_check.py; no TRIGGER file)

## Deviations from plan
1. run-item.md placement: the plan says "right after the sentence that names `commit_step.py`". That sentence is inside the two-sentence text pinned by `COMMIT_RULE` in tests/test_commit_step.py; inserting there would break that pin (the plan does not list changing it). I put the new sentence right after the end of that pinned text ("... never in parallel (item 091).") in the same paragraph. The text is exactly the plan's.
2. Module text cost sentence: added "9 from ROUND_BUILD_FROM on" so the per-item pair count stays true after the new gate. Doc only; not in the plan's list.
3. `%B` in T-a/T-c: `git log -1 --format=%B` prints one extra newline after the body, so the asserts are `subject\n\n<t1>\n<t2>\n\n` and `subject\n\n`. T-c also asserts the raw object (`git cat-file commit HEAD` ends with `\n\n<subject>\n`), which is the byte-exact form of the plan's `subject\n`.
4. Trailer check order in `_trailer_ok`: CR/LF first, then `": "`, key, empty value. Each T-b row trips only its own check (each M1c-M1f mutant kills only its row), so the order does not change which test pins which condition.
5. P-e calls `incomplete(..., committed={"work/150/05-build-report.md"})`, because 095's `_unsure` needs `committed` (the step file in HEAD's tree) to route an entry to `unchecked`.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): every new cutoff and filter has a measured count (Feasibility) and a boundary mutant; the broad SUMMARY_LINE rule is not built.
- RI-010 (ESCALATED): every new refusal (5 trailer checks) and cutoff (99/98) has a mutant that a named test kills; the no-amend rule is rule text with a pin (T-g); this item's own commit is made with `commit_step.py --trailer`, no amend.
- RI-014 (OPEN): HEAD label changed with no new git call (census 51 before and after); the new gate takes 095's shallow route (P-e, b-shallow).
- GUARDED, also checked: RI-002 (absent trailer adds nothing; absent/unreadable 05/06 and failed anchor never pass, P-f); RI-004/005 (boundaries re-derived: 92/91, 99/98; mode 120000 asserted); RI-006 (counts from commands); RI-007 (FULL scope); RI-008 (py_compile on 3.11); RI-009 (built on the shared branch after 097; probes in a detached scratch worktree, no stash); RI-011 (no branch-diff change); RI-012 (`.match` with prose, `\b`, fence and section negatives); RI-013 (no realtest change); RI-003 (no calendar change).

RI-010: guardrail extended (098): build-round headings from 099; trailers via commit_step (no amend). Status unchanged (ESCALATED).
RI-014: OPEN, unchanged; 098 adds no git call (census 51).
