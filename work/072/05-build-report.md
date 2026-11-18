# 05 Build report - 072
Branch daily-fixes/2026-11-18, built on HEAD bbd48c8 (Item 071: R3 hand-off). 071's I2 build is not on the branch yet, so the suite base below is before 071's tests. work/071 and work/074 files that show up in git status belong to parallel items, not this one.

File counts (commands as the agent file gives them; `work` and `logs` excluded, and the output holds only this item's paths):
- new = `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → **1**
- changed = `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → **7**
- Same numbers when restricted to this item's paths: `git status --porcelain -uall -- .claude templates README.md tests | grep -c '^??'` → 1, `... | grep -c '^ M'` → 7.
- Total 8, which matches the plan (7 changed, 1 new).

## Changes made (file: what changed)
- .claude/commands/run-item.md:
  - Anchor A: the end-of-run sentence now says "(every log line is written with `check_pipeline.py --log` as soon as its step's file exists, never in a batch at the end, item 045; ...". The rest is unchanged.
  - Anchor B: a new paragraph "Log lines and check_handoff (item 072)" sits between that paragraph and "A follow-up to a completed item". It is map step 1's text with the plan's three edits: "run from the repo root (both scripts use paths relative to it)"; "After R1, take only the `sources count` line; its exit code does not gate R1 (an old 03 from an earlier loop is R3's to fix)"; and "from the text after `Log fields: ` on the last line of 02/04, unchanged".
  - The 073 realtest paragraph is untouched.
- .claude/agents/r1-researcher.md: the "Finish by appending" line is replaced with map step 2's text, as one line.
- .claude/agents/r2-improver.md: the "Append to ... R2" line is replaced with map step 3's text plus "a last line, plain text, no backticks:".
- .claude/agents/r3-fact-checker.md: the step-7 line is replaced with map step 4's first text, and the "Append to ... R3" line with its second text. The RESEARCH ONLY / 07 paragraph is unchanged.
- .claude/agents/i1-reviewer.md: the "Append to ... I1" line is replaced with map step 5's text plus "a last line, plain text, no backticks:".
- templates/research-handoff.md: the last line is now "`check_handoff output (run by the orchestrator <YYYY-MM-DD> <HH:MM> UTC, exit <n>; must say PASS):`". `## Self-check` stays.
- README.md: in the check_handoff.py line, "(run by R3, I3, A1)" becomes "(run by the orchestrator after R1 and R3, and by I3 and A1; item 072)".
- tests/test_agent_tools.py (NEW):
  - Helper `agent_tools(text) -> (set, error|None)`. It parses the comma-string and YAML-list forms of `tools:` and `disallowedTools:`, and takes each name before any `(`. It returns the error "no frontmatter", "no tools: line (inherits every tool incl. Bash, item 072)" or "empty tools: (item 072)".
  - `test_agent_tools_parser` runs fixture cases a-f.
  - `test_no_shell_agents_leave_commands_to_orchestrator` checks three things: every body line of a no-Bash file that holds `python3 scripts/` must also hold "orchestrator"; the no-Bash set must be {r1, r2, r3, i1}; and run-item.md must contain both pinned strings.

## Connectivity check
- [x] every new function/rule is used. `agent_tools` is called by both tests. `_field` is called by `agent_tools` for `tools` and `disallowedTools`. The new run-item paragraph is pinned by the tree test (2 strings). The template label quoted in run-item (2) is the same text as templates/research-handoff.md's last line, and r3 step 7 points to it as "the template's check_handoff output line".
- [x] every input has a source, every output has a consumer. The inputs are the 7 agent files (sorted glob) and run-item.md. The output is the pytest result, recorded here and checked by I3. The `Log fields:` line that r2/i1 write is read by the orchestrator per run-item (4) and checked by `--log`'s LOG_FORMAT regex. This plan's own last line, "FIT WITH CHANGES | 8 files planned", is in that format.
- [x] every branch ends in a defined result:
  - In the parser, frontmatter missing or unclosed → "no frontmatter"; no `tools:` → the no-tools error; empty value with no items → the empty error. None of these is ever read as "no Bash". `disallowedTools` absent → nothing removed.
  - In the tree test, an error fails and names the file; a Bash file is skipped by design; a no-Bash file is checked line by line.
  - In run-item, FAIL → no log line, no commit, back to R3; `sources count` absent → no R1 line (INCOMPLETE stays visible); `--log` exit 2 → back to the step.
- [x] no leftover TODOs or unused files. `grep -n TODO tests/test_agent_tools.py | wc -l` → 0. Docs: the README's actor list matches the run-item paragraph, and these old phrases are gone:
  - "each step's agent writes its log line": 0 hits in .claude/
  - "must say PASS before you set READY": 0 hits in r3
  - "Write it with": 0 hits in r1
  - "run by R3, I3, A1": 0 hits in README.md

Missing-data policy:
- `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → 37 hits. All of them are existing code: `git diff --stat HEAD -- ccbot/ | wc -l` → 0, so this item has no new or changed hit.
- The same pattern plus `: float = 0|: int = 0` on tests/test_agent_tools.py → 0 hits.
- The new code has no dataclass and no `>`/`<` comparison on data.

Feasibility test named in the plan (before-fix probe), real output: on the tree before the agent-file edits, the tree test failed and named exactly 5 lines. This matches 03/04's count (r1 1, r2 1, r3 2, i1 1).
```
E       AssertionError: .claude/agents/i1-reviewer.md:18: runs a script with no shell (item 072)
E         .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072)
E         .claude/agents/r2-improver.md:22: runs a script with no shell (item 072)
E         .claude/agents/r3-fact-checker.md:20: runs a script with no shell (item 072)
E         .claude/agents/r3-fact-checker.md:24: runs a script with no shell (item 072)
FAILED tests/test_agent_tools.py::test_no_shell_agents_leave_commands_to_orchestrator
1 failed, 6 passed in 0.02s
```
After the edits, 5 of 5 lines hold "orchestrator" (the test passes, below).

## Test output (pasted, not summarized)
`python3 -m pytest -q tests/test_agent_tools.py`:
```
.......                                                                  [100%]
7 passed in 0.01s
```
Full suite before the change (base, HEAD ea6ebb9 tree; 071 not built yet): `404 passed, 1 skipped in 60.01s (0:01:00)`.
Full suite after the change, `python3 -m pytest -q`:
```
....................................................                     [100%]
411 passed, 1 skipped in 59.45s
```
That is base + 7, with no new failures.

Mutations, run on a scratch worktree (`git worktree add --detach <scratchpad>/wt072 HEAD` plus copies of the 8 changed files; removed afterwards). The repo tree was never touched.
```
== m0 clean
7 passed in 0.01s
== m1 old r1 line
E       AssertionError: .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072)
1 failed, 6 passed in 0.02s
== m2 delete r2 tools
E       AssertionError: .claude/agents/r2-improver.md: no tools: line (inherits every tool incl. Bash, item 072)
1 failed, 6 passed in 0.02s
== m3 Bash to i1
tools: Read, Write, Glob, Grep, WebSearch, WebFetch, Bash
E       AssertionError: no-shell agents changed (RULES decision, item 072): ['r1-researcher', 'r2-improver', 'r3-fact-checker']
== m4 remove run-item paragraph
E           AssertionError: run-item.md lacks 'the orchestrator runs their commands' (item 072)
1 failed, 6 passed in 0.02s
== m5 disallowedTools Bash on i2
tools: Read, Write, Edit, Glob, Grep, Bash
disallowedTools: Bash
E       AssertionError: .claude/agents/i2-builder.md:26: runs a script with no shell (item 072)
1 failed, 6 passed in 0.02s
== m6 i1 yaml list
tools:
  - Read
  ... (Write, Glob, Grep, WebSearch, WebFetch)
7 passed in 0.01s
== after reset
7 passed in 0.01s
```

Greps:
- "each step's agent writes its log line" in .claude/ → 0
- "the orchestrator runs their commands" in run-item.md → 1
- "Log fields:" → r2 1, i1 1
- "run by R3, I3, A1" in README.md → 0
- "must say PASS before you set READY" in r3 → 0
- "run by the orchestrator" in the template → 1
- "never writes to logs/" in run-item.md → 1

`python3 scripts/check_handoff.py 072`:
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 52
totals line: 52 rows -> 46 as-is, 6 fixed, 0 removed
PASS
exit 0
```
`python3 scripts/check_pipeline.py` (exit 0), relevant lines, run before this file existed:
```
072: in progress (FULL: next 05)
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-18 (0 days)
RULES BRANCH: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
SKIPPED: none
```
The test and rules files are committed together with this 05 (053). I3 re-runs check_pipeline after the commit.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD`: .claude/agents/i1-reviewer.md, .claude/agents/r1-researcher.md, .claude/agents/r2-improver.md, .claude/agents/r3-fact-checker.md, .claude/commands/run-item.md, README.md, templates/research-handoff.md; plus new tests/test_agent_tools.py. No ccbot/, config/ or data/ file.)

## Deviations from plan
1. In run-item.md (2), the template label is quoted as `check_handoff output (run by the orchestrator <YYYY-MM-DD> <HH:MM> UTC, exit <n>; must say PASS):`, not as 03's `<YYYY-MM-DD>, exit <n>` text. The reason: plan Files 6 changes the template label to carry the time, and Files 1 says to keep 03's text apart from three edits. Followed literally, run-item would quote a label the template no longer has, which is a broken link between docs. The fix is one token, and no pinned string is affected. I1/I3 should confirm it.
2. Mutation m5 fails on the line check (i2-builder.md:26), not on the set assert as the plan expected. The tree test checks lines before it checks the set, and i2 has `python3 scripts/` lines with no "orchestrator". It still fails, and it still shows that `disallowedTools` is read: without that, i2 would be skipped as Bash-capable.
3. The plan expected the full suite base "after 071 is built". 071's I2 build is not on the branch yet, so the base here is 404 passed, 1 skipped (pre-071).

Recurring issues checked (item 013):
- RI-001 (ESCALATED): checked. The one selector's count was re-measured: 5 failing lines before the fix, 5 of 5 passing after, and the no-Bash set has exactly 4.
- RI-002 (GUARDED): checked. A missing or empty `tools:` and a missing frontmatter each give a named error, never "no Bash". There are no new ccbot/ grep hits.
- RI-007 (GUARDED): checked. The test and rules changes are committed with this 05.
- RI-009 (GUARDED): checked. run-item.md is shared with 073, and only the anchor A sentence plus the new paragraph were touched. The test is in its own file, apart from 071's test_pipeline_check.py. The mutations ran in a scratch worktree.
- RI-010 (GUARDED): checked. The text duty now has a script check (the tree test).
- RI-004/RI-005: checked. The I1 field "FIT WITH CHANGES | 8 files planned" fits the I1 format.
- RI-006: checked. Counts come from commands.
- Not applicable: RI-003, RI-008 (stdlib only, no new syntax), RI-011, RI-012, RI-013 (no real-data change).

RI-001: ESCALATED, unchanged (072 adds a dated, test-pinned selector count; no new occurrence).
RI-010: GUARDED, unchanged; 072 adds tests/test_agent_tools.py, so a no-shell agent told to run a script fails a test (mutations m1-m5 fail).
RI-002: GUARDED, unchanged (no ccbot/ change).
