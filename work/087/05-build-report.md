# 05 Build report - 087
Base: daily-fixes/2026-11-21 at 0ad4d62 (089 I2). `git rev-parse --is-shallow-repository` → `false`. `check_pipeline.py` before the build: `RULES BRANCH: none`, `IN PR: none`. The one open branch (origin/claude/project-thread-f64g3k) has items none and touches no file of this item.

## Changes made (file: what changed)
- tests/test_agent_tools.py (only file, as 04 says)
  - Module docstring: new "Item 087" paragraph (04 Files 4). It covers the `&!*?:` starts, a tab before the value, an open `[`/`{` or text after it, and document markers. It says `tools:`/`disallowedTools:` are left to `_field` and keeps the "This says nothing about what Claude Code does" sentence. It lists the known fail-closed false errors, including block-scalar content lines (C2).
  - Constants: QUOTE_START_RE is replaced by `VALUE_START_RE` (04 text, byte for byte). New `DOC_MARKER_RE = re.compile(r"(?:---|\.\.\.)(?:[ \t]|$)")` and `FLOW_KEYS = ("tools:", "disallowedTools:")`. AFTER_CLOSE_RE and ENTRY_RE are unchanged.
  - New `_flow_end(line, start)`, as in 03 step 1. It uses a closer stack, skips quotes via `_quote_end`, and returns None in four cases: an unclosed quote, ` #`/`\t#`, a mismatched closer, or end of line. It has no return annotation.
  - `_frontmatter_error`: the docstring now says "(items 080, 087)". The rule order is:
    - 0: DOC
    - 1: leading tab (080 text unchanged)
    - 2: VALUE_START_RE → TAB_BEFORE / START / 080 quote logic (unchanged texts, `s` as the quote position) / flow rule (not on FLOW_KEYS lines) → FLOW_OPEN / FLOW_AFTER

    `_field`, `agent_tools`, `tree_problems`, ENTRY_RE and NO_SHELL_ALLOWED are untouched. L49's `:\t` branch is kept.
  - Error texts START, FLOW_OPEN, FLOW_AFTER, TAB_BEFORE and DOC are module constants next to UNCLOSED/TAB/AFTER, with the 04 texts.
  - Fixtures:
    - p11 is now `(None, TAB_BEFORE.format(2))`.
    - q1_anchor_dq … q28_doc_start_marker are added with the 04 ids and texts.
    - TREE n10_anchor_description and n11_open_flow are added.
    - New helper constant `TOOLS = "tools: Read, Write"` (see Deviations 2).

File counts:
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0`
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `1`

## Connectivity check
- [x] Every new function and rule is used.
  - `_flow_end` is called by `_frontmatter_error` (flow rule).
  - VALUE_START_RE, DOC_MARKER_RE and FLOW_KEYS are used in `_frontmatter_error`.
  - START, FLOW_OPEN, FLOW_AFTER, TAB_BEFORE and DOC are returned by `_frontmatter_error` and asserted by fixtures.
  - TOOLS is used by the q fixtures.
  - QUOTE_START_RE has no remaining use: `grep -rn QUOTE_START_RE --include=*.py .` gives no output.
- [x] Every input has a source and every output has a consumer. The input is the frontmatter lines from `agent_tools`. Every error string goes to `agent_tools` → `tree_problems` → the real-tree test assertion.
- [x] Every branch ends in a defined result. Each `_flow_end` path returns an index or None, and None → FLOW_OPEN. Each start character has exactly one result: TAB_BEFORE, START, the quote checks, the flow checks, or fall through to `_field`, which keeps its own 075 errors. FLOW_KEYS lines go to `_field` (j3, q26). An empty line has no VALUE_START_RE match → `_field`'s blank-line rules (unchanged).
- [x] No leftover TODOs or unused files. `git diff HEAD -- tests/test_agent_tools.py | grep -nE "TODO|fillna|or 0|else 0|is not None and|: float = "` gives no output. No new files.

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all pre-existing. `git diff --stat HEAD -- ccbot/` is empty, so there is no new or changed hit. The same pattern over my diff gives no hit (above). No dataclass and no numeric default were added. No `>`/`<` test was added; the only comparisons are `i < len(line)` (int loop bound) and `want.pop() != ch` (str).

Feasibility numbers (04 Guardrail tests):
- Real tree at the build: `test_no_shell_agents_leave_commands_to_orchestrator` passes, so 0 of the 21 real frontmatter lines (7 files x L2-L4) fire a rule.
- Probe "unchanged" below: `1 passed`.
- Each firing side is pinned by a fixture. All are in the 89 passing tests, and each is named in the mutation table below.

Base-failure check (04 Checks 2). Scratch worktree at 0ad4d62. The base's parser (everything above `def _fm(`) was joined to the head's fixtures (everything from `def _fm(`). Run with `python3 -B -m pytest -q -p no:cacheprovider tests/test_agent_tools.py`:
```
FAILED tests/test_agent_tools.py::test_agent_tools_parser[p11_tab_after_colon]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q10_comment_closer]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q11_wrong_closer]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q12_text_after_flow]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q13_flow_next_line]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q14_anchor_alone]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q15_item_open_map]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q16_explicit_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q17_colon_start]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q18_dash_tab]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q19_alias]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q1_anchor_dq]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q20_tag_on_tools]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q25_open_flow_last_line]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q27_doc_end_marker]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q28_doc_start_marker]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q2_tag_dq]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q3_tag_sq]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q4_anchor_tag_dq]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q5_item_anchor]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q7_open_seq]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q8_open_map]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[q9_quoted_closer]
FAILED tests/test_agent_tools.py::test_tree_problems[n10_anchor_description]
FAILED tests/test_agent_tools.py::test_tree_problems[n11_open_flow]
25 failed, 64 passed in 0.22s
```
The failing set is exactly 04's named list: q1-q5, q7-q20, q25, q27, q28, n10, n11 and p11. q6, q21-q24 and q26 pass on the base, as 04 says. The count differs from 04's "28 / 61"; see Deviations 1.

## Test output (pasted, not summarized)
Full suite, repo root, 2026-11-22 ~00:17 UTC, after the last edit:
```
$ python3 -m pytest -q
........................................................................ [ 98%]
.........                                                                [100%]
728 passed, 1 skipped in 84.11s (0:01:24)
```
Suite: 728 passed, 1 skipped in 84.11s (0:01:24)

The base (089's 05 at 0ad4d62) has `698 passed, 1 skipped`. 728 − 698 = +30, which matches 04's expected delta (28 parser + 2 tree).

Other checks:
```
$ python3 -m pytest -q tests/test_agent_tools.py
89 passed in 0.06s
$ python3.11 -m py_compile tests/test_agent_tools.py && echo compile311 ok
compile311 ok
```

Mutations. Scratch worktree /tmp/claude-0/scratch/i2-087/wt (`git worktree add --detach` at 0ad4d62 plus my test file). The script /tmp/claude-0/scratch/i2-087/tools/mut.py asserts each anchor occurs exactly once, applies one mutation at a time, and runs `python3 -B -m pytest -q -p no:cacheprovider tests/test_agent_tools.py` with `PYTHONDONTWRITEBYTECODE=1`. The file was restored afterwards and the worktree removed (`git worktree list` no longer shows it). Output, as printed:

| ID | Result | Failing tests |
|---|---|---|
| M25 `&!*` dropped from START set | 9 failed, 80 passed in 0.13s | q14_anchor_alone q19_alias q1_anchor_dq q20_tag_on_tools q2_tag_dq q3_tag_sq q4_anchor_tag_dq q5_item_anchor n10_anchor_description |
| M26 `&!*` searched anywhere in line | 5 failed, 84 passed in 0.10s | e_disallowed_bash f_bash_specifier q21_mid_value_amp q22_quoted_amp test_no_shell_agents_leave_commands_to_orchestrator |
| M27 `(?:-[ \t]+)*` dropped | 4 failed, 85 passed in 0.10s | q15_item_open_map q18_dash_tab q5_item_anchor q6_item_open_quote |
| M28 no quote skip in `_flow_end` | 2 failed, 87 passed in 0.08s | q24_closed_flow_comment q9_quoted_closer |
| M29 no ` #` comment in `_flow_end` | 1 failed, 88 passed in 0.08s | q10_comment_closer |
| M30 closer type not compared | 1 failed, 88 passed in 0.08s | q11_wrong_closer |
| M31 flow after-close check removed | 1 failed, 88 passed in 0.08s | q12_text_after_flow |
| M32 FLOW_KEYS exemption removed | 2 failed, 87 passed in 0.09s | j3_unclosed q26_disallowed_open |
| M33 key-start class `[^\s"'#]` | 1 failed, 88 passed in 0.08s | q15_item_open_map |
| M34 `?`/`:` dropped from START set | 2 failed, 87 passed in 0.09s | q16_explicit_key q17_colon_start |
| M35 TAB_BEFORE rule removed | 2 failed, 87 passed in 0.10s | p11_tab_after_colon q18_dash_tab |
| M36 `{` dropped from flow starts | 2 failed, 87 passed in 0.08s | q15_item_open_map q8_open_map |
| M37 flow rule removed | 10 failed, 79 passed in 0.13s | q10_comment_closer q11_wrong_closer q12_text_after_flow q13_flow_next_line q15_item_open_map q25_open_flow_last_line q7_open_seq q8_open_map q9_quoted_closer n11_open_flow |
| M38 doc-marker rule removed | 2 failed, 87 passed in 0.08s | q27_doc_end_marker q28_doc_start_marker |
| M38b `\|$` alternative dropped | 1 failed, 88 passed in 0.08s | q27_doc_end_marker |
| M14 | 1 failed, 88 passed in 0.08s | p4_bare_dash |
| M15 | 37 failed, 52 passed in 0.30s | p11 p14 p15 p1 p2 p3 p5 p6 p7 p8 (080's 11 incl. n8 n9) + q1-q5 q6 q7-q20 q25 q27 q28 n10 n11 |
| M16 | 2 failed, 87 passed in 0.08s | p3_tab_block_list n9_tab_list |
| M17 | 8 failed, 81 passed in 0.12s | p14 p1 p2 p5 p6 p7 n8 (080's 7) + q6_item_open_quote |
| M18 | 5 failed, 84 passed in 0.11s | p10_closed_sq_comment p15_quoted_key p5_dq_escaped_end p6_sq_doubled_end p8_text_after_close |
| M19 | 2 failed, 87 passed in 0.08s | p10_closed_sq_comment p6_sq_doubled_end |
| M20 | 1 failed, 88 passed in 0.07s | p5_dq_escaped_end |
| M21 | 2 failed, 87 passed in 0.08s | p15_quoted_key p8_text_after_close |
| M22 `"\t" in line` | 2 failed, 87 passed in 0.08s | p11_tab_after_colon q18_dash_tab |
| M23 `re.search(r"([\"'])", line)` | 26 failed, 63 passed in 0.24s | p12_plain_inner_quote test_no_shell_agents_leave_commands_to_orchestrator (080's targets) + p11 q1-q5 q7-q17 q19 q20 q23 q24 q25 n10 n11 |
| M24 key-required quote regex | 26 failed, 63 passed in 0.23s | p14_nested_open_quote p15_quoted_key (080's targets) + p11 q1-q20 (not q21-q24) q25 n10 n11 |
| A1-m1 n = i + 1 | 37 failed, 52 passed in 0.31s | every line-number fixture (080's 11 + 26 new) |
| A1-m2 lstrip(" ") | 2 failed, 87 passed in 0.08s | p3_tab_block_list n9_tab_list |
| A1-m4 AFTER_CLOSE_RE `.*` | 3 failed, 86 passed in 0.13s | p15_quoted_key p8_text_after_close q12_text_after_flow |

Every mutation fails all of its 04/080-named targets, and none leaves the file green. M22 still fails p11, now by text (03 #72). Mutation texts not given verbatim in 04/03:
- M26: `if c in "&!*?:":` → `if c in "?:" or re.search(r"[&!*]", line):` plus `c = c if c in "?:" else re.search(r"[&!*]", line).group(0)`.
- M23 and M24 replace `m = VALUE_START_RE.match(line)` (their 080 targets were QUOTE_START_RE, which is now gone).
- M17 and M18 are applied at the 087 quote branch, with `s` as the start.

Probes (04 Probes). The real r1-researcher.md in the same scratch worktree, run with `pytest -q tests/test_agent_tools.py::test_no_shell_agents_leave_commands_to_orchestrator`. The file was restored after each probe (`cmp` → identical):
```
A1-1 &d " | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: value starts with '&' on frontmatter line 3 (item 087)
A1-2 !!str " | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: value starts with '!' on frontmatter line 3 (item 087)
A1-3 !!str ' | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: value starts with '!' on frontmatter line 3 (item 087)
A1-4 &a !!str " | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: value starts with '&' on frontmatter line 3 (item 087)
hooks - &a | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: value starts with '&' on frontmatter line 6 (item 087)
flow [a, | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: unclosed flow collection on frontmatter line 3 (item 087)
doc ... | 1 failed in 0.03s | E       AssertionError: .claude/agents/r1-researcher.md: document marker on frontmatter line 4 (item 087)
unchanged | 1 passed in 0.02s | -
```
How each shape was built:
- A1-1 to A1-4: the description line (L3) gets the shape's prefix, and a closing quote line is put after L4 `tools:`.
- hooks: `hooks:` / `  - &a "x,` / `y"` inserted after L4, so the `- &a` line is file line 6.
- flow: L3 becomes `description: [a,`, with `]` after `tools:`.
- doc: `...` is inserted after L3.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD`: tests/test_agent_tools.py only; no ccbot/, config/ or data/ file)

## Deviations from plan
1. 04 Checks 2's tally is mis-summed. The named list (q1-q5, q7-q20, q25, q27, q28 = 22 parser cases; n10, n11; p11) is 25 tests, not "25 parser + 2 tree + p11 = 28". 89 − 25 = 64 pass on the base, not 61. The real run matches the named list exactly, so no code change follows. I3 should check against the list, not the number 28.
2. Added `TOOLS = "tools: Read, Write"` next to NO_TOOLS. It stands for 04's "tools" shorthand in the fixture texts and does not change any fixture text.
3. The 080 error texts inside `_frontmatter_error` stay as their original f-strings (04: "the 080 quote logic, unchanged"). The new texts use the new constants.

Recurring issues checked (item 013), against this build:
- RI-001: ESCALATED, checked. Each new rule is counted on today's tree (0 of 21 real lines fire, real-tree test passes at the build, 2026-11-22), and each firing side is pinned by a fixture and a mutation (table above).
- RI-010: ESCALATED, checked. Log line written with `check_pipeline.py --log` right after this file; `Suite:` line above is the pytest last line as printed.
- RI-014: OPEN, checked; not touched (no git-depth logic; repo not shallow).
- RI-002: GUARDED, near miss closed: every unreadable start (incl. document markers) is a named error, never a tool set (M15, M25, M37, M38).
- RI-006: totals copied from pytest output; file counts from the commands above.
- RI-008: python3.11 py_compile OK.
- RI-009/011: mutations and probes only in a scratch worktree; only my own files are staged.
- RI-012: START anchored at the value start; M26 (search anywhere) fails q21, q22, e, f and the real tree.
