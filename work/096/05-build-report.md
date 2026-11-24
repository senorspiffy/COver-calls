# 05 Build report - 096
Base commit: 1b10d90 (branch daily-fixes/2026-11-24, after 092 and 093). I2 scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-096-r1-ahn6umpv (mkdtemp, item 091).

D4 (copied from 03 via 04): 087's q30 (`...x` / `---x`) was not valid YAML (PyYAML 6.0.3 ScannerError, work/087/06-verification.md L14); 087/04 L229 called it valid.

## Changes made (file: what changed)
- tests/test_agent_tools.py (the only file, as planned):
  - a. `KEY_RE` added right after `DOC_MARKER_RE`, text exactly as in 04 Files a; `NO_KEY = "no key on frontmatter line {} (item 096)"` added after `DOC`.
  - b. `_frontmatter_error`: docstring now "(items 080, 087, 096)"; `prev_open = False` before the loop; the new column-0 check is the last check in the loop body (after the `if m:` block), followed by the `prev_open` update, with the comment test on the stripped line (`t.startswith("#")`). Names `s`/`c` not reused, no walrus.
  - c. Module docstring: "Item 096:" paragraph after the Item 087 one, with the 03 step 3 / 04 Files c content, keeping "This says nothing about what Claude Code does with such a file."
  - d. CASES: q30 rewritten in place to `_fm("name: x", "...x: y", "---x: z", TOOLS)`; nk1-nk12 added as in the 04 table.
  - e. TREE: `n12_no_key_line` added.

File counts (commands, item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 1 changed

## Connectivity check
- [x] every new function/rule is used: `KEY_RE` is used in the new check and the `prev_open` update; `NO_KEY` is returned by `_frontmatter_error` and used by nk1-nk5, nk8, nk10, nk11 and n12; `prev_open` is read by the item branch.
- [x] every input has a source, every output has a consumer: input is `front` from `agent_tools`; the NO_KEY error goes to `agent_tools` → `tree_problems` → the real-tree test assertion (n12 pins the tree path).
- [x] every branch ends in a defined result: column-0 item with P open → allowed, continue; item with P closed (including no previous meaningful line, nk11) → NO_KEY; non-item without key shape → NO_KEY; FLOW_KEYS lines → left to `_field`; blank/comment/indented lines → skipped by the check, comments/blanks keep P.
- [x] no leftover TODOs or unused files: none added (grep of the diff for TODO: none). The mutation script lives only in the scratch dir.

Missing-data policy: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 38 hits, all pre-existing; `git diff --stat -- ccbot/` is empty, so no new or changed hit. No dataclass field was added; no `>`/`<` numeric test was added. The absent previous line starts closed (`prev_open = False`, nk11 + M51); a line with no key shape blocks with NO_KEY, never a tool set.

Feasibility (04 Tests 4): `test_no_shell_agents_leave_commands_to_orchestrator` passes on the real tree (in the 105-passed run below), i.e. all 21 real frontmatter lines in the 7 agent files pass the new check.

PyYAML verdicts on nk4, nk5, nk8, nk11, nk12: not probed by I2; 05 makes no claim that they are YAML-invalid (04 Extra research 5).

## Test output (pasted, not summarized)
`python3 -m pytest tests/test_agent_tools.py -q` (repo, build tree):
```
........................................................................ [ 68%]
.................................                                        [100%]
105 passed in 0.09s
```
`python3.11 -m py_compile tests/test_agent_tools.py` → no output, exit 0 (RI-008).

Base-failure check and mutations (04 Tests 2-3), each run one at a time on the scratch copy (`python3 mut.py <scratch>`; M42 is the base parser: new check, `prev_open` update and init removed):
```
M41: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[q30_marker_prefix_text]
M42: 9 failed, 96 passed in 0.20s | failed: test_agent_tools_parser[nk10_inner_colon_key], test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk1_plain_word], test_agent_tools_parser[nk2_plain_word_last], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk5_indicator_key], test_agent_tools_parser[nk8_item_after_nested_map], test_tree_problems[n12_no_key_line]
M43: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[nk2_plain_word_last]
M44: 4 failed, 101 passed in 0.18s | failed: test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk8_item_after_nested_map]
M45: 13 failed, 92 passed in 0.21s | failed: test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk6_tools_col0_list], test_agent_tools_parser[nk7_item_after_empty_key], test_agent_tools_parser[nk8_item_after_nested_map], test_agent_tools_parser[nk9_tools_blank_then_item], test_agent_tools_parser[p13_doc_hooks_example], test_agent_tools_parser[p14_nested_open_quote], test_agent_tools_parser[q13_flow_next_line], test_agent_tools_parser[q15_item_open_map], test_agent_tools_parser[q18_dash_tab], test_agent_tools_parser[q23_doc_mcp_example], test_agent_tools_parser[q5_item_anchor], test_agent_tools_parser[q6_item_open_quote]
M46: 5 failed, 100 passed in 0.14s | failed: test_agent_tools_parser[p15_quoted_key], test_agent_tools_parser[q16_explicit_key], test_agent_tools_parser[q17_colon_start], test_agent_tools_parser[q27_doc_end_marker], test_agent_tools_parser[q28_doc_start_marker]
M47: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[nk5_indicator_key]
M48: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[nk8_item_after_nested_map]
M49: 2 failed, 103 passed in 0.12s | failed: test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk9_tools_blank_then_item]
M50: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[s_no_space]
M51: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[nk11_item_first_line]
M52: 1 failed, 104 passed in 0.11s | failed: test_agent_tools_parser[nk12_indented_comment_then_item]
```
Each failing-id list equals its 04 list. Mutation forms used: M41 DOC_MARKER_RE without `(?:[ \t]|$)`; M43 `i < len(front) - 1 and` added to the check; M44 `if not prev_open:` → `if False:`; M45 KEY_RE lookahead `(?=[ \t])`; M46 check moved to right after `n = i + 2`; M47 KEY_RE first-character part replaced by L45's `[^\s"'#&!*\[{?:]`; M48 update only when `line[0] != " "`; M49 update runs on every line and blank/comment gives False; M50 `and not line.startswith(FLOW_KEYS)` dropped; M51 `prev_open = True`; M52 `line.startswith("#")`. The scratch copy's test file was restored after the run: 105 passed.

Full suite, `python3 -m pytest -q` from the repo root, last line as printed:

Suite: 849 passed, 1 skipped in 118.24s (0:01:58)

`python3 scripts/check_pipeline.py` (before this 05 was written) exit 0; SKIPPED none, INCOMPLETE none, I3 FAIL none, A1 FAIL none, UNTRACKED CHANGE none; 096 "in progress (FULL: next 05)".

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py | 45 +++++++++++++++++++++++++++++++++++++++++++--)

## Deviations from plan
None. Every count matched 04: 105 passed; base 9 failed / 96 passed; M41-M52 failing ids equal their lists.

## Recurring issues checked
logs/recurring-issues.md read first. Open or ESCALATED entries checked: RI-001, RI-010, RI-014; GUARDED entries also checked: RI-002, RI-004, RI-005, RI-006, RI-007, RI-008, RI-012.
RI-001: ESCALATED, unchanged. The allow-list filter's dated count is measured: the real-tree test passes on 7 files (21 frontmatter lines), 2026-11-24.
RI-002: GUARDED, unchanged. This item closes the near miss "column-0 line with no key passes the frontmatter test → 096": such a line now gives NO_KEY; absent previous line starts closed (nk11, M51 fails nk11).
RI-004: GUARDED, unchanged. Every expected count in 04 was re-run, not copied.
RI-005: GUARDED, unchanged. Same as RI-004.
RI-006: GUARDED, unchanged. All counts above are pytest output as printed; the `Suite:` line is copied unchanged into the I2 log field.
RI-007: GUARDED, unchanged. Scope FULL; code written only at I2.
RI-008: GUARDED, unchanged. python3.11 py_compile of tests/test_agent_tools.py passes.
RI-010: ESCALATED, unchanged. The I2 log line is written by `check_pipeline.py --log` right after this file; commit via `scripts/commit_step.py`.
RI-012: GUARDED, unchanged. KEY_RE is anchored with `.match`; in-text negatives q30, nk5, nk10 pass.
RI-014: OPEN, unchanged. Not applicable (no git or clone-depth path touched).
