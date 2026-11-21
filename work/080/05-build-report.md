# 05 Build report - 080
Built on HEAD ceb00ce (daily-fixes/2026-11-20). Uncommitted; the orchestrator commits.

## Changes made (file: what changed)
- tests/test_agent_tools.py (the only file, as 04 plans):
  - Module docstring: new "Item 080" paragraph. A frontmatter line the test cannot read on its own is an error, because the test cannot tell which tools that file grants. It names the three cases (tab in leading whitespace; a quoted value at line start, after `- `, or after `key: ` not closed on its line; text after the closing quote other than spaces or ` #...`), says nothing about what Claude Code does with such a file (D8), and names the two known fail-closed false errors (a tab at the start of block-scalar content, a whitespace-only line with a tab; 04 research 2).
  - New constants `QUOTE_START_RE` and `AFTER_CLOSE_RE`, regex text exactly as in 04.
  - New `_quote_end(line, start)`: `"` with `\` skipping the next character, `'` with `''` as a literal; returns the index past the close or None.
  - New `_frontmatter_error(front)`: rules (a) tab in `lead`, (b) unclosed quote, (c) text after close, in that order per line, first line wins, `n = i + 2`.
  - `agent_tools`: right after `front = lines[1:end]`, `error = _frontmatter_error(front)` / `if error: return set(), error`. `_field`, `tree_problems`, `ENTRY_RE`, the allow-list and `_field`'s `" \t"` check are unchanged.
  - New text constants `UNCLOSED`, `TAB`, `AFTER` (next to `NO_TOOLS`) used by the fixtures.
  - CASES: p1-p15 as in the 04 table. TREE: n8_quoted_description, n9_tab_list as in 03 step 3.

File counts:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
$ git diff --stat
 tests/test_agent_tools.py | 94 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 94 insertions(+)
```

## Connectivity check
- [x] every new function/rule is used: `_frontmatter_error` is called from `agent_tools` (so from `tree_problems` and the real-tree test); `_quote_end` is called from `_frontmatter_error`; `QUOTE_START_RE` and `AFTER_CLOSE_RE` are used there; `UNCLOSED`/`TAB`/`AFTER` are used by p1-p15, n8, n9.
- [x] every input has a source, every output has a consumer: input is `front` (the frontmatter lines, from `agent_tools`); the output error goes to `agent_tools`' `(set(), error)` return, so to the parser assertions and to `tree_problems`' `"<label>: <error>"` problem list, which the real-tree test asserts empty.
- [x] every branch ends in a defined result: tab → named error; quote match with no close → named error; close followed by other text → named error; close followed by spaces/comment → next line; no quote match → next line; all lines read → None, then the existing `_field` path. `_quote_end` returns an index or None (a trailing `\` steps past the end and returns None, so the value is open: p5).
- [x] no leftover TODOs or unused files: `grep -n "TODO\|FIXME" tests/test_agent_tools.py` → no output. No new file.
- Missing-data policy: `grep -rnE "<the I2 pattern>" ccbot/ | wc -l` → 38, all pre-existing (no ccbot/ change: `git diff --stat -- ccbot/` empty). No hit in the changed file. No dataclass, no numeric default. The only `<` in new code is `while i < len(line)` (ints, never NaN). An unreadable line is never a tool set: it blocks with a named error.
- Feasibility (the plan's named count): the real-tree test `test_no_shell_agents_leave_commands_to_orchestrator` passes on today's 7 agent files with the new rule (21 of 21 frontmatter lines read, 59 passed below). The 33 + 7 existing parametrized cases all still pass (40 of 40). Positives p9-p13 pass (5 of 5).

## Test output (pasted, not summarized)
Base (HEAD ceb00ce, before the edit):
```
$ python3 -m pytest -q tests/test_agent_tools.py
42 passed in 0.03s
$ python3 -m pytest -q
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 572 passed, 1 skipped in 78.18s (0:01:18)
```
After the edit:
```
$ python3 -m pytest -q tests/test_agent_tools.py
...........................................................              [100%]
59 passed in 0.04s
$ python3 -m pytest -q
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 589 passed, 1 skipped in 77.88s (0:01:17)
$ python3.11 -m py_compile tests/test_agent_tools.py; echo rc=$?
rc=0
```
589 = 572 + 17, skips unchanged (1), as 04 expects. The one failure is pre-existing on this branch (fails on the base run above too): 083 under PR #33's rules plus in-progress items; not caused by this change.

Probes and mutations, scratch copy only (`tests/` and `.claude/` copied fresh per run into `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/c080/run`, scripts `.../c080/tools/mut.py` and `probe.py`; each replacement anchor asserted to occur once; repo never edited). `pytest -q tests/test_agent_tools.py`, failing test ids as printed:
```
M14 | 1 failed, 58 passed in 0.05s | test_agent_tools_parser[p4_bare_dash]
M15 | 11 failed, 48 passed in 0.12s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p1_dq_multiline] test_agent_tools_parser[p2_sq_multiline] test_agent_tools_parser[p3_tab_block_list] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p7_open_quote_last_line] test_agent_tools_parser[p8_text_after_close] test_tree_problems[n8_quoted_description] test_tree_problems[n9_tab_list]
M16 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p3_tab_block_list] test_tree_problems[n9_tab_list]
M17 | 7 failed, 52 passed in 0.09s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p1_dq_multiline] test_agent_tools_parser[p2_sq_multiline] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p7_open_quote_last_line] test_tree_problems[n8_quoted_description]
M18 | 5 failed, 54 passed in 0.06s | test_agent_tools_parser[p10_closed_sq_comment] test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p8_text_after_close]
M19 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p10_closed_sq_comment] test_agent_tools_parser[p6_sq_doubled_end]
M20 | 1 failed, 58 passed in 0.06s | test_agent_tools_parser[p5_dq_escaped_end]
M21 | 2 failed, 57 passed in 0.09s | test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p8_text_after_close]
M22 | 1 failed, 58 passed in 0.05s | test_agent_tools_parser[p11_tab_after_colon]
M23 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p12_plain_inner_quote] test_no_shell_agents_leave_commands_to_orchestrator
M24 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p15_quoted_key]
```
Mutation texts: M14 `_is_item` → `return s.startswith("- ")`; M15 the 3-line call removed; M16 `if "\t" in lead:` → `if False:`; M17 `end is None` → `end = len(line)` (no error); M18 the `_quote_end` call and rules (b)/(c) replaced by exactly `v = line[m.start(1):]` / `if not (len(v) > 1 and v.rstrip().endswith(v[0])): return <unclosed text>`; M19 the `''` skip removed; M20 the `\` skip removed; M21 rule (c) removed; M22 `"\t" in lead` → `"\t" in line`; M23 `QUOTE_START_RE.match(line)` → `re.search(r"([\"'])", line)`; M24 `QUOTE_START_RE.match` → `re.match(r"""(?:[^\s"'#][^:]*:[ \t]+)(["'])""", line)` (column-0 `key: ` only). Every mutation fails all its named cases; none leaves the suite green. Extras beyond the named targets: M23 also fails the real-tree test (`.claude/agents/r2-improver.md: unclosed quoted value on frontmatter line 3 (item 080)`: r2's plain `description:` value holds a mid-line quote with no partner on the line, which the anchored rule correctly ignores), M24 also fails p15.

Base behaviour of the new fixtures: the base parser plus the new fixtures is exactly M15 (the call is the only code path change), which fails p1, p2, p3, p5, p6, p7, p8, p14, p15, n8, n9 (11) and passes p4, p9-p13, as 04 "Expected result" says.

A1 probes on the real r1-researcher.md (scratch copy):
```
a1-n1 dq head | 1 failed, 58 passed in 0.05s | test_no_shell_agents_leave_commands_to_orchestrator | ['E       AssertionError: .claude/agents/r1-researcher.md: unclosed quoted value on frontmatter line 3 (item 080)']
a1-n1 sq head | 1 failed, 58 passed in 0.06s | test_no_shell_agents_leave_commands_to_orchestrator | ['E       AssertionError: .claude/agents/r1-researcher.md: unclosed quoted value on frontmatter line 3 (item 080)']
a1-n2 head | 1 failed, 58 passed in 0.06s | test_no_shell_agents_leave_commands_to_orchestrator | ['E       AssertionError: .claude/agents/r1-researcher.md: tab in indentation on frontmatter line 5 (item 080)']
a1-n1 dq base | 42 passed in 0.04s | NONE
a1-n1 sq base | 42 passed in 0.05s | NONE
a1-n2 base | 42 passed in 0.04s | NONE
```
(a1-n1: `"`/`'` inserted after `description: ` on L3 and `end"`/`end'` added after the `tools:` line; a1-n2: L4 replaced by `tools:` plus six `\t- <name>` lines. Base = `git show HEAD:tests/test_agent_tools.py`.)

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py)

## Deviations from plan
- None in code or fixtures. One addition the plan leaves to the builder: three text constants `UNCLOSED`, `TAB`, `AFTER` so the 17 fixtures share the exact 080 strings; the function returns its own f-strings, so a wording change in either place fails the fixtures.

## Recurring issues checked (item 013)
RI-001: ESCALATED, unchanged (counts measured: 21 of 21 real frontmatter lines, 40 of 40 existing cases, 5 of 5 positives)
RI-002: GUARDED, unchanged (080 near miss fixed: an unreadable frontmatter line is a named error, never a tool set; M15-M24 fail)
RI-006: GUARDED, unchanged (counts copied from pytest's last line)
RI-008: GUARDED, unchanged (python3.11 py_compile rc=0)
RI-009: GUARDED, unchanged (mutations and probes in a scratch copy; no file shared with 085)
RI-010: ESCALATED, unchanged (I2 line written by --log)
RI-012: GUARDED, unchanged (quote rule anchored with `.match`; M23 fails p12)
RI-014: OPEN, unchanged (no check_pipeline.py change)
Not applicable: RI-003, RI-004/RI-005 (no worked example; fixtures traced by running them), RI-007 (FULL scope, no `.claude/` or `templates/` edit), RI-011, RI-013 (no realtest change).
