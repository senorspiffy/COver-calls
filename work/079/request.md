# Work item 079
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-19

## What we want
`check_pipeline.py` gives the same answer on a shallow clone as on a full one, or says "not checked (shallow clone; run git fetch --unshallow)". A shallow boundary must never show up as an error entry (or as a pass).

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 2026-11-19 daily audit, first run in a shallow worktree of PR #32 head e69d5bd: `UNTRACKED CHANGE: a15129c (git diff-tree failed) (item 053: ...)` and `INBOX: not checked (shallow clone; run git fetch --unshallow)`. After `git fetch --unshallow`: `UNTRACKED CHANGE: none`.
- Reproduced in a scratch full clone at e69d5bd with `git rev-parse a15129c > .git/shallow` (a15129c = shallow boundary, cutoff 694bf4d still an ancestor via another parent): exit 1, same UNTRACKED CHANGE line. Same probe at main 1a7dac6: none (a15129c is not on main's first-parent walk; same code path, scripts/check_pipeline.py `_walk` L471-490 on main).
- a15129c (Item 063: R1 research) has a step file of an open item; it is not an untracked change.

## Root cause and prevention guardrail (BUG only)
Root cause: `_walk` checks shallowness only when the cutoff is unreachable. When the cutoff is reachable but a first-parent commit after it is a shallow boundary, `diff-tree c^1 c` fails and `untracked_changes` turns the uncomputable diff into an error entry (RI-002 family: an uncomputable value turned into a verdict; here a false error, so loud, but it trains the reader to ignore UNTRACKED CHANGE). INBOX already handles shallow clones; UNTRACKED CHANGE and RESEARCH CODE don't share that check.
Guardrail: in `_walk`, if the repo is shallow and any walked commit's parent is missing (or any commit is listed in `git rev-parse --shallow-file`/`.git/shallow`), return `not checked (shallow boundary <sha>; run git fetch --unshallow)`, failed=False, never an entry. A fixture test builds a tiny repo, grafts a boundary on the first-parent walk, and pins the "not checked" text and exit 0; a mutation removing the check fails it. Also: daily-audit.md and run-item.md say to run `git fetch --unshallow` (when shallow) before `check_pipeline.py`.

## Recurring issue link (RI-#, if any)
New RI-014 (checker result depends on clone depth), 1 occurrence.

## Done looks like
Shallow-boundary fixture gives "not checked" and exit 0; full clone unchanged; mutation fails the test; daily-audit.md/run-item.md carry the unshallow line.
