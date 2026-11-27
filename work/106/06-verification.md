# 06 Verification - 106
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-106-r1-i6b5z964

Everything ran inside the scratch dir above. I made three worktrees there with `git worktree add --detach`: `wt` at de08401 (I2's build, unmodified: full suite and probe), `wt2` at de08401 (mutants only) and `wtb` at a522c5d (base check, restored with `git checkout HEAD -- tests/test_agent_tools.py`). The pyc dir `pyc-i2neal4x` was made inside it with mkdtemp. Every pytest run had `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc-i2neal4x`. I ran no test in the main checkout and used no `git stash`. My own `tools/mut.py`, `tools/base.py` and `probe/p.py` are in the scratch dir. I did not reuse I2's dir or scripts.

## I1 audit (plan vs research)
- 04 follows 03 step by step. Its Rule trace maps steps 1-7, D1-D8, Removed claims, Missing inputs and the guardrail to plan lines, and drops nothing. The constants, `_ends_field`, the `_field` `first`/`lead` check, the `_frontmatter_error` keep/cut, tab check, `in_flow` and stack, and the 29 CASES all match 03 steps 1-4 text for text.
- One addition, and it has sources: Extra research 1 (`hooks:` / `  - x` / `  a: v`). It cites PyYAML's test data `no-block-collection-end.loader-error` and a CircleCI thread, and it calls the indented form a prediction. It changes only the docstring ("Not checked"), with no code and no test count. Its tools form is shown to fail closed in `_field`. My probe of that shape agrees (see 05, er1).
- Extra research 3 (use PyYAML instead) is turned down for 03's reasons (rows 1, 4, 46, 71, 24).
- No 001 rule changes. The change is test-only, so no rule-text update or request is needed.
- Fit verdict FIT WITH CHANGES, "1 files planned". Both are correct.

## I2 audit (build vs plan)
- `git diff a522c5d de08401 --stat`: `tests/test_agent_tools.py` (+101/-6), plus 05 and log lines. The diff for `ccbot config scripts docs .claude` is empty. That is 1 code file, as planned.
- I read the diff against 04 Files 1, line by line:
  - `TAB_PLAIN` and `INDENT` have the exact D1/D7 texts.
  - `_ends_field` has the planned body.
  - The `_field` stop test now uses `_ends_field`. `first = None` comes before the loop, and the lead check comes after `if gap:`, with the D7 text.
  - The `_frontmatter_error` docstring says "(..., 104, 106)". `stack = []` and `in_flow = False` are set before the loop, and `keep = cut = 0` before `VALUE_START_RE`. The quoted branch sets `keep, cut = s, end` after AFTER_CLOSE_RE, and the flow branch sets `keep = cut = end` after FLOW_AFTER. The tab check is the first statement under `if t and not t.startswith("#"):`. It is followed by the `in_flow` set/clear and `not in_flow and` in the continuation branch. The stack pop, INDENT, equal-level replace and dash-level extend come after `if error: return error` and before `prev = (col, op)`.
  - There is no walrus and no `match`. `s`, `c` and `end` are used only in their branches.
- CASES: there are 29 new ids, each with 03 step 4's input and expectation. None clashes with an existing id (D8).
- The module docstring follows 03 step 6. "sibling indentation levels; " is removed, and the `- ` continuation is limited to fields other than `tools:`/`disallowedTools:`. The Item 106 paragraph is added with "measured on PyYAML 6.0.1 and 6.0.4" and the runtime disclaimer, and Extra research 1 is listed under "Not checked". Under D4, the "s5 if PyYAML loads it" clause is left out because PyYAML raises on s5 (05's probe, and mine below). The `\t` in the docstring is an escape in the source (`grep -c $'\t' tests/test_agent_tools.py` = 0), as in the existing L47.
- Connectivity, re-done:
  - `_ends_field` is called from `_field` (stop) and from `_frontmatter_error` (`in_flow` clear). M77 and M78 show both call sites matter.
  - `TAB_PLAIN` and `INDENT` are returned and expected by the CASES.
  - `stack`, `in_flow`, `keep`, `cut` and `first` are each read in the function that sets them.
  - The parametrized `test_agent_tools_parser` reads all 165 CASES.
  - `grep -n TODO tests/test_agent_tools.py` gives nothing.
- Grep reasons in 05, re-checked:
  - The missing-data grep on `ccbot/` gives `38`, the same as 05, and ccbot/ is unchanged.
  - The same pattern on tests/test_agent_tools.py gives `0`.
  - `grep -c $'\t' .claude/agents/*.md` gives 0 in each of the 7 files.
- Data-hole edges for the stack (RI-002 style):
  - Before the first value: s5, an indented first line, gives INDENT(3). My mutant E2 (`stack = [0]`, so column 0 is assumed) fails s5.
  - After the last value: nothing is checked, and no tool set depends on it.
  - Interior gaps: s1, s2 and s4.
  - `_field` with no item: `first` is never defaulted. My mutant E1 (`first = 0`) fails 7 existing cases.

## Tests re-run (output)
check_handoff (main checkout, and again in `wt`, both exit 0):
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 78
totals line: 78 rows -> 57 as-is, 16 fixed, 5 removed
PASS
```
Env check: `True /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-106-r1-i6b5z964/pyc-i2neal4x`

Test file (`wt2`, before mutants): `165 passed in 0.13s`

Full suite (`wt`, de08401, `python3 -m pytest -q -p no:cacheprovider`), last lines:
```
........................................................................ [ 94%]
..............................................................           [100%]
1069 passed, 1 skipped in 279.16s (0:04:39)
```
This matches 05 (1069 passed, 1 skipped; base 1040 + 29).

Oldest Python: python3.11 (3.11.18) is on PATH and python3.10 is not. `tests/test_safety.py -k oldest` gives `1 passed, 8 deselected`, so `test_every_py_compiles_on_oldest_python` ran and did not skip. `python3.11 -m py_compile tests/test_agent_tools.py` exits 0.

Base check (`wtb` = a522c5d plus head's 2 constants and 29 CASES only, made by my `tools/base.py`):
```
FAILED ...[c1_tools_continuation_key]
FAILED ...[c2_tools_item_continuation_key]
FAILED ...[c3_disallowed_continuation_key]
FAILED ...[c5_tools_col0_item_continuation]
FAILED ...[f1_tools_item_indents]
FAILED ...[s1_map_dedent_between]
FAILED ...[s2_tools_list_dedent]
FAILED ...[s4_dedent_off_level]
FAILED ...[s5_indented_first_line]
FAILED ...[tb1_tools_comma_tab]
FAILED ...[tb2_tools_trailing_tab]
FAILED ...[tb3_tools_flow_tab]
FAILED ...[w10_tab_in_empty_key]
FAILED ...[w13_tab_in_flow_after_quoted_hash]
FAILED ...[w1_tab_before_hash_colon]
FAILED ...[w2_tab_before_hash]
FAILED ...[w3_tab_in_plain]
FAILED ...[w4_tab_in_continuation]
FAILED ...[w5_tab_in_item]
FAILED ...[w6_tab_in_block_header]
FAILED ...[w9_tab_after_bare_hash]
21 failed, 144 passed in 0.39s
```
(I shortened the `tests/test_agent_tools.py::test_agent_tools_parser` prefix to `...`.) This is exactly the 21 ids in 03/04. It shows that the guardrail catches the original error: s2, tb1, tb3 and w1, the four tool sets from YAML the pure loader rejects, fail on the old parser.

Mutants (my `tools/mut.py`, one at a time in `wt2`, each replacement asserted to match exactly once, file restored from memory after each one):
```
HEAD: 165 passed in 0.13s | failed: -
M69: 12 failed, 153 passed in 0.29s | failed: tb1_tools_comma_tab, tb2_tools_trailing_tab, tb3_tools_flow_tab, w10_tab_in_empty_key, w13_tab_in_flow_after_quoted_hash, w1_tab_before_hash_colon, w2_tab_before_hash, w3_tab_in_plain, w4_tab_in_continuation, w5_tab_in_item, w6_tab_in_block_header, w9_tab_after_bare_hash
M70: 1 failed, 164 passed in 0.14s | failed: w8_tab_in_comment
M71: 1 failed, 164 passed in 0.16s | failed: w7_tab_in_quote
M72: 1 failed, 164 passed in 0.14s | failed: w9_tab_after_bare_hash
M73: 4 failed, 161 passed in 0.20s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level, s5_indented_first_line
M74: 1 failed, 164 passed in 0.14s | failed: s7_nested_dash_levels
M75: 3 failed, 162 passed in 0.17s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level
M76: 4 failed, 161 passed in 0.17s | failed: c1_tools_continuation_key, c2_tools_item_continuation_key, c3_disallowed_continuation_key, c5_tools_col0_item_continuation
M77: 1 failed, 164 passed in 0.13s | failed: c4_flag_cleared_by_key
M78: 4 failed, 161 passed in 0.22s | failed: c5_tools_col0_item_continuation, nk6_tools_col0_list, nk9_tools_blank_then_item, v21_tools_comment_then_item
M79: 1 failed, 164 passed in 0.24s | failed: f1_tools_item_indents
M80: 2 failed, 163 passed in 0.17s | failed: w11_tab_in_block_content, w12_tab_in_comment_line
M81: 1 failed, 164 passed in 0.18s | failed: w13_tab_in_flow_after_quoted_hash
E1_first_default_0: 7 failed, 158 passed in 0.27s | failed: c2_tools_item_continuation_key, d_yaml_list, i2_block_single_quoted, p4_bare_dash, y2_blank_in_list, y4_indented_plain, y7_disallowed_blank
E2_stack_assumes_col0: 1 failed, 164 passed in 0.16s | failed: s5_indented_first_line
E3_no_replace_equal: 165 passed in 0.13s | failed: -
E4_in_flow_never_set: 4 failed, 161 passed in 0.21s | failed: c1_tools_continuation_key, c2_tools_item_continuation_key, c3_disallowed_continuation_key, c5_tools_col0_item_continuation
E5_split_tab_hash: 6 failed, 159 passed in 0.23s | failed: w1_tab_before_hash_colon, w2_tab_before_hash, w4_tab_in_continuation, w5_tab_in_item, w6_tab_in_block_header, w8_tab_in_comment
M56: 9 failed, 156 passed in 0.27s | failed: c4_flag_cleared_by_key, n13_value_colon, v12_block_ends, v1_value_colon, v23_hash_in_word_colon, v26_dash_key_continuation, v2_value_colon_end, v3_nested_value_colon, v6_continuation_colon
M57: 1 failed, 164 passed in 0.16s | failed: v4_colon_in_comment
M58: 3 failed, 162 passed in 0.19s | failed: c4_flag_cleared_by_key, v26_dash_key_continuation, v6_continuation_colon
M59: 3 failed, 162 passed in 0.20s | failed: v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented
M60: 2 failed, 163 passed in 0.19s | failed: v14_key_1024, v17_key_1024_indented
M62: 4 failed, 161 passed in 0.21s | failed: v10_block_folded_indicators, v12_block_ends, v9_block_literal, w11_tab_in_block_content
M63: 1 failed, 164 passed in 0.16s | failed: v22_tools_entry_colon
M64: 2 failed, 163 passed in 0.16s | failed: p13_doc_hooks_example, s3_compact_map_in_list
M68: 1 failed, 164 passed in 0.18s | failed: v17_key_1024_indented
X2: 1 failed, 164 passed in 0.18s | failed: v23_hash_in_word_colon
X4: 1 failed, 164 passed in 0.18s | failed: v26_dash_key_continuation
restored: True
```
- M69 to M81 each fail exactly their 03 step 5 / 04 Tests 5 list, and the lists are the same as 05's.
- The 104 mutants I re-ran (M56-M60, M62-M64, M68, X2, X4) fail the same ids as 05, including the new ids 05 recorded (M56 +c4, M58 +c4, M62 +w11, M64 +s3). Each still fails every id in its 104/06 list. I did not re-run M61, M65-M67, X1 or X3 (05 ran them).
- E1-E5 are my own mutants:
  - E1 and E2 are the RI-002 "put a default back" probe. E1 defaults `first` to 0, and E2 assumes column 0 on the stack. Both fail tests.
  - E4 (`in_flow` never set) fails the c cases.
  - E5 (comment cut at `\t#` instead of ` #`) fails 6 cases.
  - E3 survives: it drops the pop of a level equal to `ind` before `extend`. It is an equivalent mutant. Each pushed set starts with `ind` itself, so the only effect is a duplicate `ind` on the stack. Every later test reads only `stack[-1]` after popping the levels greater than `ind`, so a duplicate cannot change a result. This is not a gap.

Unchanged cases: 05 Tests 6's 30 named cases are all among the 165 passing CASES, each with its own expectation.

PyYAML probe (my own `probe/p.py`, information only and not a claim about Claude Code; `python3 -I` = PyYAML 6.0.1 pure, and `python3` with the user site = 6.0.3 with libyaml). Agent_tools result on de08401, then the loaders:
```
PyYAML 6.0.3 libyaml True
w1 -> ([], 'tab outside quotes and comments on frontmatter line 2 (item 106)') | Safe: ScannerError; CSafe: loads {'description': 'a', 'tools': 'Read, Write'}
tb1 -> ([], 'tab outside quotes and comments on frontmatter line 2 (item 106)') | Safe: ScannerError; CSafe: loads {'tools': 'Read,\tWrite'}
tb3 -> ([], 'tab outside quotes and comments on frontmatter line 2 (item 106)') | Safe: ScannerError; CSafe: loads {'tools': ['Read', 'Write']}
s2 -> ([], 'indent matches no open level on frontmatter line 4 (item 106)') | Safe: ParserError; CSafe: ParserError
s5 -> ([], 'indent matches no open level on frontmatter line 3 (item 106)') | Safe: ParserError; CSafe: ParserError
f1 -> ([], 'tools: list items at different indents (item 106)') | Safe: loads {'tools': ['Read - Bash']}; CSafe: loads {'tools': ['Read - Bash']}
x1_lead_2_3 -> ([], 'indent matches no open level on frontmatter line 4 (item 106)') | Safe: loads {'tools': ['Read - Write']}; CSafe: loads {'tools': ['Read - Write']}
x2_trailing_tab_item -> ([], 'tab outside quotes and comments on frontmatter line 3 (item 106)') | Safe: ScannerError; CSafe: loads {'tools': ['Read']}
x3_tab_in_comment -> ([], "unparsed tools: entry 'Read # c\tx' (item 075)") | Safe: loads {'tools': 'Read'}; CSafe: loads {'tools': 'Read'}
x4_tab_hash_tools -> ([], 'tab outside quotes and comments on frontmatter line 2 (item 106)') | Safe: ScannerError; CSafe: loads {'tools': 'Read'}
x5_col0_then_indented -> ([], 'tools: list items at different indents (item 106)') | Safe: loads {'tools': ['Read - Write']}; CSafe: loads {'tools': ['Read - Write']}
x6_equal_lead4 -> (['Read', 'Write'], None) | Safe: loads {'name': 'x', 'tools': ['Read', 'Write']}; CSafe: loads {'name': 'x', 'tools': ['Read', 'Write']}
x7_tab_after_dash -> ([], 'tab before the value on frontmatter line 3 (item 087)') | Safe: ScannerError; CSafe: ScannerError
x8_disallowed_tab -> ([], 'tab outside quotes and comments on frontmatter line 3 (item 106)') | Safe: ScannerError; CSafe: loads {'tools': 'Read, Bash', 'disallowedTools': 'Bash,\tRead'}
```
The 6.0.1 pure run gives the same SafeLoader column (CSafeLoader absent). I added x1 to x8 to look for holes on the tools path:
- None of them gives a tool set that differs from YAML. The only pass, x6 (equal indents of 4), loads the same set in both loaders.
- x1 and x5 are tool lists whose items have unequal indents. YAML folds them into one entry, `Read - Write`, and the test refuses them, so they fail closed.
- x3 (a tab inside a ` #` comment on `tools:`) is refused by the existing `_field` entry check. That is a known fail-closed false error from before this item, not one this item added.
- 05's probe table for w1, tb1, tb3, s2, s5 and f1 agrees with mine.

## Real-data effect (diff_reports output, pasted)
not required (`git diff a522c5d de08401 --stat`: tests/test_agent_tools.py, work/106/05-build-report.md, logs/implementation/2026-11-26.md, work/107/*; no ccbot/realtest.py or TRIGGER/TRIGGER_DIRS file)

## BUG checks (step 3)
- Fix and guardrail are both in place:
  - The three open shapes from 104's audit now fail closed with named errors. Tab before `#` (w1, w2) gives TAB_PLAIN. Sibling indent (s1, s2, s4, s5) gives INDENT. A continuation under `tools:` (c1, c2, c3, c5) gives `_field`'s item 075 text.
  - The five extra tab paths in 03 row 6 also fail closed: w10, tb1, tb2, tb3 and w13.
  - The guardrail is one fixture per branch, each failed by a named mutant (M69-M81, all reproduced above). The real-tree test still passes, with 0 tabs in the 7 agent files.
- The guardrail would have caught the original error. The base check above shows w1, s2, tb1, tb3, c1-c3, c5 and f1 failing on the old parser. Those are the shapes A1 found (or that 03 measured) passing or giving the wrong message at a522c5d.
- RI-001 feasibility, re-run:
  - Tab rule: real tree 0 of 21 lines (0 tabs in each of the 7 files). Fixture selection is 12 (M69 list), as 04 cites.
  - INDENT rule: fixture selection is 4 (M73 list).
  - `in_flow` skip: fixture selection is 4 (M76 list).
  - `_field` lead check: fixture selection is 1 (M79).
  - Each number in 04 and 05 matches its run above.
- RI-002 default probe: E1 (`first = 0`) and E2 (`stack = [0]`) were put back in the scratch worktree `wt2` only. They fail 7 tests and 1 test (s5). The file was then restored ("restored: True").
- RI-012 text classification: the tab rule and the ` #` cut match text.
  - In-text negatives: w7 (a tab inside a quote, with `#` in the quote), w8 (a tab inside a ` #` comment), w11 (a tab in block content) and w12 (a tab in a comment line). Each passes, and each is failed by its own mutant: M71, M70, M80 and M80.
  - Edges: w9 (`#` without a space) and w13 (a quoted ` #` inside a flow collection) are failed by M72 and M81.
  - My E5 shows that the cut must be ` #` and not `\t#`.
- 001 rule text: not affected (test-only).
- Simulator or replay (item 062): not applicable.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013, RI-014
- RI-001 (ESCALATED): every selection count was re-run above (0/21 real lines; 12, 4, 4 and 1 fixtures), and each matches 04/05. Nothing is claimed as "always".
- RI-014 (OPEN): not applicable. There is no git, clone-depth or history logic. `check_pipeline.py` ran in a full clone.
- RI-002 (GUARDED, this item's root cause): holds. s2, tb1, tb3 and w1 no longer give tool sets. `first` and `stack` are never defaulted (E1 and E2 fail tests). My x1-x8 probes found no new tool-set path. The missing-data grep is unchanged (38 in ccbot/, 0 in the test file).
- RI-004/005: I re-traced 03 Self-check rules 26-40 by running them as the base check and the mutants, and every list matched.
- RI-006: every count in this file was copied from command output.
- RI-007: Scope FULL. 01-05 exist, and this is the I3 step.
- RI-008: holds. `test_every_py_compiles_on_oldest_python` ran on 3.11 and passed, and `python3.11 -m py_compile` exits 0.
- RI-009: holds. I used my own mkdtemp dir, made the worktrees with `--detach`, used no stash, and ran no test in the main checkout.
- RI-010: the log line is written with `--log` right after this file, and the env-check line is pasted above.
- RI-012 (GUARDED): holds (see BUG checks).
- RI-003, RI-011, RI-013: not applicable. There is no calendar, merge-base or realtest/diff_reports path.

## Pipeline line (step 2)
check_pipeline line: `106: awaiting A1 (FULL)`

## Sent back / sent to Audit
Sent to Audit. See work/106/07-audit-task.md. Nothing is sent back.
