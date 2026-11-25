# 05 Build report - 073
Base commit: bb5a32e (daily-fixes/2026-11-18, after 072's I2 build). Built from work/073/04-build-plan.md.

## Changes made (file: what changed)
- `.claude/agents/i3-verifier.md`: step 2, the 04 Files-1 sentence appended on the same line directly after "run the base too (item 068)." (I3's head run is always its own full run, new scratch `--out`, TRIGGER + TRIGGER_DIRS scope, never 05's head run, re-run if cut off, only the base may be reused; item 073). Nothing else changed.
- `.claude/commands/run-item.md`: the realtest paragraph (now L20 after 072), the 04 Files-2 sentence appended after "come only from the full run (item 068).". 072's "Before each step" text is intact (grep below).
- `templates/verification.md`: in the `## Real-data effect` comment, the sentence "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's." replaced with the 04 Files-3 (C2) wording. The comment still ends ` -->` and still holds `from item 070 check_pipeline.py requires`.
- `tests/test_real_data_field.py`: `test_t23_own_head_run_text` (3 parametrized ids: i3, run-item, template) added after `test_t7d_cutoff_constant_matches_template_comment`, text exactly as in 04.

File counts (restricted to this item's paths, because I3 for 072 and I1 for 071/074 write in the same tree in parallel; the unrestricted command gives the same numbers at this moment):
```
$ P=".claude/agents/i3-verifier.md .claude/commands/run-item.md templates/verification.md tests/test_real_data_field.py"
$ git status --porcelain -uall -- $P | grep -c '^??'
0
$ git status --porcelain -uall -- $P | grep -c '^ M'
4
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
4
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
```
New: 0. Changed: 4. Matches 04 "Files planned: 4 (4 changed, 0 new)".

## Connectivity check
- [x] every new function/rule is used: t23 is collected by pytest (3 ids run below). The three new rule sentences are read by I3 (i3-verifier step 2, verification.md template comment) and by the orchestrator (run-item.md), and each is pinned by a t23 id.
- [x] every input has a source, every output has a consumer: the I3 head run's inputs (head commit worktree, data, new `--out`) are named in the text; its outputs (TOTAL line, `--out` dir, worktree, log, wall time, `cmp` result) go into 06's Real-data effect section, which check_pipeline reads for TOTAL (item 070).
- [x] every branch ends in a defined result: run cut off -> run again; base gone or inputs differ -> run base (item 068 text, kept); 05's saved output file gone -> line compare with 05's pasted lines, said in 06; `cmp`: identical or differs (the differing lines). Other missing inputs (05 used `--tickers`, `--max-rows` not stated, log/wall time not captured) are I3 06 texts per 04 Missing inputs; no script branch was added.
- [x] no leftover TODOs or unused files: `git diff` adds no TODO; no new file.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits, all pre-existing; `git diff --stat -- ccbot/` is empty, so no new or changed hit. No dataclass field or `>`/`<` test added (only rules text and one substring test).
- Feasibility number named in 04: the scope set TRIGGER + TRIGGER_DIRS = 9 paths, pinned by the existing test_t9 (passes in the full suite below). No new feasibility test.

## Test output (pasted, not summarized)
Base suite on the branch at bb5a32e, before any 073 edit:
```
$ python3 -m pytest -q
411 passed, 1 skipped in 59.19s
```
Before-fix probe (t23 added, the three text edits not yet made):
```
$ python3 -m pytest -q tests/test_real_data_field.py -k t23
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[i3] - Assert...
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[run-item] - ...
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[template] - ...
3 failed, 32 deselected in 0.07s
```
After the edits:
```
$ python3 -m pytest -q tests/test_real_data_field.py -k t23
3 passed, 32 deselected in 0.02s
$ python3 -m pytest -q tests/test_real_data_field.py -k "t7d or t23"
5 passed, 30 deselected in 0.02s
$ python3 -m pytest -q
414 passed, 1 skipped in 60.40s (0:01:00)
```
414 = 411 + 3, no new failure (Python 3.13.18).

Greps:
```
grep -c "item 073" .claude/agents/i3-verifier.md = 1
grep -c "(item 068)" .claude/agents/i3-verifier.md = 1
grep -c "make one full run at the head commit" .claude/agents/i3-verifier.md = 1
grep -c "item 073" .claude/commands/run-item.md = 1
grep -c "counts as the base only if" .claude/commands/run-item.md = 1
grep -c "the orchestrator runs their commands" .claude/commands/run-item.md = 1
grep -c "same dirs" templates/verification.md = 0
grep -c "item 073" templates/verification.md = 1
grep -c "from item 070 check_pipeline.py requires" templates/verification.md = 1
```
Diff stat (uncommitted, against base bb5a32e):
```
$ git diff --stat -- . ':!work' ':!logs'
 .claude/agents/i3-verifier.md |  2 +-
 .claude/commands/run-item.md  |  2 +-
 templates/verification.md     |  2 +-
 tests/test_real_data_field.py | 16 ++++++++++++++++
 4 files changed, 19 insertions(+), 3 deletions(-)
```
check_handoff:
```
$ python3 scripts/check_handoff.py 073
sources count (unique URLs in 01-research.md): 0
fact-check rows: 70
totals line: 70 rows -> 59 as-is, 10 fixed, 1 removed
PASS
```
check_pipeline (before 05 existed; exit 1 comes from 071, whose I1 is running in parallel, not from 073):
```
073: in progress (FULL: next 05)
AWAITING A1: none
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-18 (0 days)
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: 071 (no log line for I1)
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (2026-11-18.md added in f103aa3; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
exit 1
```
073 is not SKIPPED or INCOMPLETE; REAL-DATA FIELD and LOG TIME do not name 073. RULES BRANCH shows none because daily-fixes/2026-11-18 is not pushed yet; it will show once the branch is on origin (I3/A1 re-check).

Mutations m1-m3 are I3's per 04 (scratch worktree); I2 did not run them. The before-fix probe above shows all three t23 ids fail when the texts are absent.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i3-verifier.md, .claude/commands/run-item.md, templates/verification.md, tests/test_real_data_field.py). No TRIGGER or TRIGGER_DIRS path changes; 0 full runs.

## Deviations from plan
- 04 says build after 071 and 072. 072 is built (bb5a32e); 071 is not built yet (its I1 is running in parallel). The orchestrator directed building 073 now. All edits use text anchors 071 is not planned to touch, so 071 can apply its i3 step 5 / step-2-end / `Sent back to:` edits on top. No other deviation.

## Follow-ups for A1
- (a) 03 map step 6 (a): a check_pipeline check that 06's head dir differs from 05's (D3, dropped here because 071 edits check_pipeline.py in parallel, and a name check proves only that the names differ).
- (b) 03 map step 6 (b): G1, widen I2's full-run trigger / the `--tickers` gap (05 used `--tickers` -> I3 writes "TOTAL compare: n/a").

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): checked; the one scope rule has a dated non-zero count (9 paths), pinned by t9 and t23. No filter added.
- RI-002: checked; no value defaulted, no ccbot/ change; every absent I3 input has a stated text.
- RI-006: checked; file counts from commands above.
- RI-007: checked; rule and test edits committed together with 05.
- RI-009: checked; shared files edited by anchor, neighbours' text kept (072 grep = 1); no `git add -A`, stash or reset.
- RI-010: checked; the text duty has a check (t23).
- RI-012, RI-013: checked; t23 is a fixed-string presence test; the template asks for TOTAL and whole-output compare on the same `--max-rows`.
- RI-003, RI-004, RI-005, RI-008, RI-011: not applicable (no calendar, no worked example, no hand-off numbers changed, no new syntax, no branch diff).

RI-001: ESCALATED, unchanged (no new occurrence).
RI-010: GUARDED, unchanged; 073 adds a text-pin test (t23) to a text-only duty.
RI-013: GUARDED, unchanged; template now asks for I3's own head dir and same `--max-rows`.
