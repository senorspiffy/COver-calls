# 06 Verification - 080
Verdict: PASS (round 1)
Sent back to: none

## I1 audit (plan vs research)
04 follows 03's Implementation map step by step (04 Rule trace, checked row by row against 03 steps 1-5, D1-D8 and Missing inputs):
- Step 1 (a)/(b)/(c): the regex texts in 04 (`QUOTE_START_RE`, `AFTER_CLOSE_RE`), the scanner semantics (`\` skips the next character, `''` is a literal), the error texts and `n = i + 2` are identical to 03 step 1. The call placement (after `front = lines[1:end]`, before `_field`) matches.
- Step 2 (no other code change), step 3 (p1-p14, n8, n9 with the same lines and expected texts), step 4 (M14-M24 with the same targets) and step 5 (whole suite plus 3.11 compile) are all carried over.
- D5 (open `[`/`{`) is DROPPED with 03's own reason (outside the request). D7 (no PyYAML) and D8 (no runtime claim) are kept.
- The additions all have sources, and none is outside the request:
  1. p15_quoted_key: the shape is A1's 075 probe (logs/audit/2026-11-19-075.md, 01 F10). 04 research 5 traces it through 03's rules. I confirmed the trace: PyYAML 6.0.3 reads `"tools": Read, Bash` as `{'tools': 'Read, Bash'}`, and the test now gives the 080 error (fails closed).
  2. The M18 replacement text is pinned, and 04 adds p8, p10 and p15 as its targets. That follows 03 S5, whose Self-check already added p8 and p10.
  3. The docstring sentence on the two known fail-closed false errors: 04 research 2, sourced to PyYAML's spec-05-12.error test data.
  4. The suite delta is written as base + 17 (16 from 03 plus p15).
- Two research items are recorded without being acted on, which is correct. Research 3 (`tools:\t` under PyYAML) is marked UNVERIFIED for the D5 follow-up. Research 4 (`claude plugin validate`) is suggested as an optional A1 manual probe.
No unsourced additions.

## I2 audit (build vs plan)
`git diff 42b0378~1 42b0378 -- tests/` (read in the scratch worktree /tmp/claude-0/wt080) matches 04's "Files to create/change" line by line:
- Docstring: the "Item 080" paragraph has the three cases, no claim about what Claude Code does (D8), and the two false errors (research 2).
- `QUOTE_START_RE = re.compile(r"""[ ]*(?:-[ ]+)*(?:[^\s"'#][^:]*:[ \t]+)?(["'])""")` and `AFTER_CLOSE_RE = re.compile(r"( +#.*)? *")` are character-for-character the 04/03 text.
- `_quote_end`: `"` with `\` skipping 2 (a trailing `\` steps past the end and returns None); `'` with `''` skipping 2 and a lone `'` closing. This is as planned.
- `_frontmatter_error`: rule (a) on `lead`, then (b), then (c), with the first line winning and `n = i + 2`. The f-string texts match 04.
- `agent_tools`: the 3-line call sits directly after `front = lines[1:end]`. `_field`, `tree_problems`, `ENTRY_RE`, the allow-list and `_field`'s `" \t"` check are untouched (the diff has no other hunks in them).
- CASES p1-p15 and TREE n8/n9: each front line and expected value matches the 04 table and 03 step 3. p5's source is `'description: "abc\\"'`, as 04 specifies.
- Declared deviation: the text constants `UNCLOSED`, `TAB` and `AFTER` are used only by the fixtures, and the function keeps its own f-strings. So a wording drift on either side fails a fixture. This is acceptable: it changes no behaviour.
- `git show --stat 42b0378`: tests/test_agent_tools.py (+94), work/080/05-build-report.md, logs/implementation/2026-11-20.md. No other code file. The commits after 42b0378 on the branch (f976a05, d29efba) touch only work/ and logs/ (`git diff --stat 42b0378 HEAD`).

Connectivity re-done: `_frontmatter_error` is called from `agent_tools`, which `test_agent_tools_parser`, `tree_problems` (so `test_tree_problems`) and the real-tree test `test_no_shell_agents_leave_commands_to_orchestrator` use. `_quote_end`, `QUOTE_START_RE` and `AFTER_CLOSE_RE` are used only inside `_frontmatter_error`. The three text constants are used by p1-p8, p14, p15, n8 and n9. Every branch ends in a named error string or falls through to the existing `_field` path. Nothing is left unused (each mutation that removes a piece fails a test, below). `grep -n "TODO\|FIXME" tests/test_agent_tools.py` gives no output.

BUG checks (step 3):
- The fix and the guardrail are both in place. The guardrail is the error path plus fixtures p1-p15, n8 and n9, with each mutation failing a named test.
- The guardrail would have caught the original error. A1's probes on the real r1-researcher.md (scratch worktree) pass silently on the base test file (`git show 42b0378~1:tests/test_agent_tools.py`, 42 passed) and fail loudly at head. Table under Tests re-run.
- RI-001 feasibility re-run: the real-tree test passes on today's 7 agent files (21 of 21 frontmatter lines read). This matches the count 04 cites. All 40 existing cases (33 parser + 7 tree) and the 5 positives (p9-p13) pass in the 59 passed below.
- RI-002 "put back a removed default": no default was removed (test file only, no numeric or dataclass default). The equivalent here is removing the guardrail (M15), and that fails 11 tests.
- Data-window edges: an open quote on the first frontmatter line (p1, p15, and my probe `description: "abc` alone → line 2 error), on the last line (p7) and in the interior (p14) are all pinned.
- Text-matching negative test (item 059, RI-012): the quote rule is anchored at value start. p12 (`description: Use "this`, a quote inside other text) is the negative test, and M23 (search anywhere) fails it.
- Simulator rule (item 062): N/A, no simulator or replay.
- Rule text the person follows (001): not touched (test-only change).
- The grep reasons in 05 (missing-data pattern, 38 hits, all pre-existing, none in the changed file): consistent. `git diff --stat 42b0378~1 42b0378 -- ccbot/` is empty.

## Tests re-run (output)
All run in the scratch worktree /tmp/claude-0/wt080 (clean checkout of 42b0378), Python 3.13.18. No run, mutation or probe was made in /home/claude/cover-calls.
```
$ python3 -m pytest -q tests/test_agent_tools.py
...........................................................              [100%]
59 passed in 0.05s
$ python3 -m pytest -q
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 589 passed, 1 skipped in 79.00s (0:01:19)
$ python3.11 -m py_compile tests/test_agent_tools.py; echo rc=$?
rc=0
$ python3 -m pytest -q tests/test_safety.py -k oldest -rs
1 passed, 8 deselected in 0.16s
```
Same as 05 (589 = 05's base 572 + 17, 1 skip). `test_every_py_compiles_on_oldest_python` ran (not skipped): python3.11 is on PATH, python3.10 is not. The one failure is pre-existing. Its message names only `INCOMPLETE: 083 (log line for I2 does not match its format (item 045) ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))` and `SKIPPED: none`, so it is not 080's (fixed later by 084).

Mutations M14-M24 (04's texts), run with my own script /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3_080/mut.py. Each replacement anchor is asserted to occur exactly once, and the file is restored after each run (`git status --short` in the worktree is empty afterwards). `pytest -q tests/test_agent_tools.py`:
```
M14 | 1 failed, 58 passed in 0.08s | test_agent_tools_parser[p4_bare_dash]
M15 | 11 failed, 48 passed in 0.10s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p1_dq_multiline] test_agent_tools_parser[p2_sq_multiline] test_agent_tools_parser[p3_tab_block_list] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p7_open_quote_last_line] test_agent_tools_parser[p8_text_after_close] test_tree_problems[n8_quoted_description] test_tree_problems[n9_tab_list]
M16 | 2 failed, 57 passed in 0.06s | test_agent_tools_parser[p3_tab_block_list] test_tree_problems[n9_tab_list]
M17 | 7 failed, 52 passed in 0.08s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p1_dq_multiline] test_agent_tools_parser[p2_sq_multiline] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p7_open_quote_last_line] test_tree_problems[n8_quoted_description]
M18 | 5 failed, 54 passed in 0.07s | test_agent_tools_parser[p10_closed_sq_comment] test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p5_dq_escaped_end] test_agent_tools_parser[p6_sq_doubled_end] test_agent_tools_parser[p8_text_after_close]
M19 | 2 failed, 57 passed in 0.06s | test_agent_tools_parser[p10_closed_sq_comment] test_agent_tools_parser[p6_sq_doubled_end]
M20 | 1 failed, 58 passed in 0.05s | test_agent_tools_parser[p5_dq_escaped_end]
M21 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p15_quoted_key] test_agent_tools_parser[p8_text_after_close]
M22 | 1 failed, 58 passed in 0.06s | test_agent_tools_parser[p11_tab_after_colon]
M23 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p12_plain_inner_quote] test_no_shell_agents_leave_commands_to_orchestrator
M24 | 2 failed, 57 passed in 0.07s | test_agent_tools_parser[p14_nested_open_quote] test_agent_tools_parser[p15_quoted_key]
```
Mutation texts: M14 `return s.startswith("- ")`. M15: the 3-line call removed. M16 `if False:`. M17 `end is None` → `end = len(line)`. M18: the `_quote_end` call plus (b)/(c) replaced by exactly `v = line[m.start(1):]` / `if not (len(v) > 1 and v.rstrip().endswith(v[0])): return <unclosed text>`. M19: the `''` skip removed. M20: the `\` skip removed. M21: rule (c) removed. M22 `"\t" in line`. M23 `re.search(r"([\"'])", line)`. M24 `re.match(r"""(?:[^\s"'#][^:]*:[ \t]+)(["'])""", line)`.

Every mutation fails all of its 04-named targets, and none leaves the suite green. Results are identical to 05's table, failing ids included. Re-run once more with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1 python3 -B` (M22 is a same-size edit; the stale-.pyc lesson from 085): the same 11 counts. Extras beyond the targets: M23 also fails the real-tree test (r2-improver.md's plain description holds a mid-line quote), and M24 also fails p15. Both are as 05 reports.

A1 probes on the real .claude/agents/r1-researcher.md (scratch worktree, restored after; script /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3_080/probe.py). For a1-n1, a quote is inserted after `description: ` on L3 and `end"`/`end'` after the tools line. For a1-n2, L4 becomes `tools:` plus six `\t- <name>` lines. Base = 42b0378~1's test file:
```
a1-n1 dq head | 1 failed, 58 passed in 0.06s | ['test_no_shell_agents_leave_commands_to_orchestrator'] | ['E       AssertionError: .claude/agents/r1-researcher.md: unclosed quoted value on frontmatter line 3 (item 080)']
a1-n1 sq head | 1 failed, 58 passed in 0.05s | ['test_no_shell_agents_leave_commands_to_orchestrator'] | ['E       AssertionError: .claude/agents/r1-researcher.md: unclosed quoted value on frontmatter line 3 (item 080)']
a1-n2 head | 1 failed, 58 passed in 0.05s | ['test_no_shell_agents_leave_commands_to_orchestrator'] | ['E       AssertionError: .claude/agents/r1-researcher.md: tab in indentation on frontmatter line 5 (item 080)']
a1-n1 dq base | 42 passed in 0.03s | NONE | []
a1-n1 sq base | 42 passed in 0.02s | NONE | []
a1-n2 base | 42 passed in 0.03s | NONE | []
```
Extra I3 edge probes (`agent_tools` called directly at head; PyYAML 6.0.3 shown where I compared):
```
description: "abc\\"  (escaped backslash, then close) -> ({'Read'}, None)
tools: / '  - "Read' / '  - Write'                    -> unclosed quoted value on frontmatter line 3 (item 080)
tools: / "  - - 'Read"                                -> unclosed quoted value on frontmatter line 3 (item 080)
description: "a"<TAB>                                 -> text after closing quote on frontmatter line 2 (item 080)   (D3: trailing tab rejected)
# "open (comment line)                                -> ({'Read'}, None)
description: "abc  (only line)                        -> unclosed quoted value on frontmatter line 2 (item 080)
tools: / ' \t- Read' (space then tab)                 -> tab in indentation on frontmatter line 3 (item 080)
tools: ["Read", "Write"]                              -> ({'Read', 'Write'}, None)
a1-n1 dq shape  | test: unclosed ..., line 2 | yaml: {'description': 'Research team, tools: Read, Write end'}  (no tools key; the original bug)
"tools": Read, Bash | test: text after closing quote ..., line 2 | yaml: {'tools': 'Read, Bash'}  (fails closed)
tools: ["Read, Bash"] | test: unparsed tools: entry '"Read' (item 075) | yaml: {'tools': ['Read, Bash']}  (fails closed, D5 area, pre-existing 075 path)
tools: ["Read, Bash]  | test: unparsed tools: entry '"Read' (item 075) | yaml: ScannerError  (fails closed)
```
None of these shapes gives a tool set YAML would not give.

check_handoff (re-run by I3 in /home/claude/cover-calls, read-only, exit 0):
```
$ python3 scripts/check_handoff.py 080
sources count (unique URLs in 01-research.md): 2
fact-check rows: 68
totals line: 68 rows -> 60 as-is, 7 fixed, 1 removed
PASS
```
This matches the output pasted in 03.

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-006, RI-008, RI-009, RI-010, RI-012, RI-014. Open or ESCALATED entries: RI-001, RI-010, RI-014.
- RI-001 (ESCALATED): the only filter is the new per-line rule. I re-ran its count: 21 of 21 real lines pass, and the real-tree test is green at head. 40 of 40 existing cases and 5 of 5 positives pass. 04 makes no uncounted "every" claim.
- RI-002 (GUARDED; 080 is the near-miss fix): an unreadable line is a named error, never a tool set. M15-M24 each fail a test. The A1 probes pass on base and fail at head. My PyYAML cross-check shows no shape yields extra tools.
- RI-006: every count in this file is copied from pytest's last line as printed.
- RI-008: python3.11 py_compile rc=0, and `test_every_py_compiles_on_oldest_python` ran and passed (python3.10 is not on PATH).
- RI-009/RI-011: the build touches one test file. No file overlap with 081 (check_pipeline.py) or 082/085/086.
- RI-010 (ESCALATED): this step's log line is written with `--log` right after this file and 07. There are no batched lines.
- RI-012: anchored `.match`, with negative test p12 pinned by M23.
- RI-014 (OPEN): not touched (no check_pipeline.py change in 080).
- Not applicable: RI-003 (no calendar), RI-004/RI-005 (no worked example; fixtures traced by running them), RI-007 (FULL scope; I1-I3 ran; no `.claude/` or `templates/` edit), RI-013 (no realtest change).

## Pipeline line (step 2)
check_pipeline line: `080: awaiting A1 (FULL)`

Run in /home/claude/cover-calls with both the committed script (`git show HEAD:scripts/check_pipeline.py`, HEAD d29efba, whose commits after 42b0378 touch only work/ and logs/) and the working-tree script (being edited by 081's I2). Both print the same lines. Before the I3 log line existed they also printed `INCOMPLETE: 080 (no log line for I3), 083 (...)`. The I3 line is written with `--log` right after this file, and the post-log re-run is recorded below.

Post-log re-run (after `23:53 | I3 | 080 | PASS | sent to audit: yes`, both script versions): `080: awaiting A1 (FULL)`. 080 is no longer listed under INCOMPLETE. The only INCOMPLETE is the pre-existing 083, and `SKIPPED: none`.

## Sent back / sent to Audit
Sent back: none. Sent to Audit: yes, work/080/07-audit-task.md.
