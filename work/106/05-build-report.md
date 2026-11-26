# 05 Build report - 106
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-106-r1-9bz7fki9

Base: a522c5d (daily-fixes/2026-11-25, after 108, 110, 105, 109 and 107). Inside the scratch dir above I made two worktrees with `git worktree add --detach` at a522c5d: `wt` (the baseline full suite, unmodified) and `wt2` (the base check and every mutant). The pyc dir `pyc-_zfzovfv` was made inside the scratch dir with the same mkdtemp command (prefix `pyc-`). It was used on every command in `wt` and `wt2`. `venv` (PyYAML 6.0.1 pure, for the probe), `probe/probe.py`, `tools/mut.py` and `new.py` (a copy of the build file, which mut.py restores from) are also there. Mutants ran only in `wt2`. In the main checkout I ran only the unmutated test file and the full suite. No `git stash` was used.

## Changes made (file: what changed)
- `tests/test_agent_tools.py` (the only file, as in 04 Files 1):
  - Constants `TAB_PLAIN` and `INDENT` go after `BLOCK`, with the exact 03 D1/D7 texts.
  - New helper `_ends_field(line)` goes after `_is_item`, with the 04 body and a one-line docstring.
  - `_field`: the stop test is now `if _ends_field(line): break`. It sets `first = None` before the loop and adds the `lead`/`first` check after the `if gap:` return. That check returns `f"{key}: list items at different indents (item 106)"`.
  - `_frontmatter_error`: the docstring now says "(items 080, 087, 096, 104, 106)". `stack = []` and `in_flow = False` are set before the loop, and `keep = cut = 0` is set before `m = VALUE_START_RE.match(line)`. The quoted branch sets `keep, cut = s, end` and the flow branch sets `keep = cut = end`. The first statement under `if t and not t.startswith("#"):` is the tab check. It is followed by the `in_flow` set/clear and `not in_flow and` in the continuation branch. In the structure branch, after `if error: return error`, come the stack pop, INDENT, replace and extend exactly as in 03 step 3, then the existing `prev = (col, op)`. There is no walrus. `s`, `c` and `end` are used only inside their branches.
  - CASES: 29 new cases with 03 step 4's exact inputs and expectations: `w1_tab_before_hash_colon` ... `w13_tab_in_flow_after_quoted_hash`, `tb1_tools_comma_tab`, `tb2_tools_trailing_tab`, `tb3_tools_flow_tab`, `s1_map_dedent_between` ... `s7_nested_dash_levels`, `c1_tools_continuation_key` ... `c5_tools_col0_item_continuation`, `f1_tools_item_indents`. No id clashes with `s_no_space`, `t1_unbalanced`, `t2_two_parens`, `c_empty_tools`, `w_miscased_disallowed` or `f_bash_specifier` (D8).
  - Module docstring: "sibling indentation levels; " is removed from Item 104's "Not checked". "a continuation that starts with `- `" becomes "... outside `tools:`/`disallowedTools:`". The "Item 106:" paragraph is added (03 step 6), with the Extra research 1 shape under "Not checked" next to D3's shape. The runtime disclaimer is kept. On s5, D4 applied: PyYAML raises on s5 (probe below), so s5 is not listed as a fail-closed false error. s3, s6 and s7 load, so no extra "Not checked" line is needed.
- No change to ccbot/, config/ or scripts/ (`git diff --stat -- ccbot/ config/ scripts/` is empty).

File counts (from commands, before commit):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
```
That is 1 file, matching 04's "1 files planned".

## Connectivity check
- [x] every new function/rule is used: `_ends_field` is called by `_field` (stop test) and by `_frontmatter_error` (`in_flow` clear). `TAB_PLAIN` and `INDENT` are returned by `_frontmatter_error` and used in the CASES expectations. `stack`, `in_flow`, `keep`, `cut` and `first` are each read in the same function that sets them. Each of the 29 cases is read by `test_agent_tools_parser` (parametrized over CASES).
- [x] every input has a source, every output has a consumer: inputs are the frontmatter lines (from `agent_tools`). The outputs are an error string or a tool set, consumed by `tree_problems` (real tree) and by the parser test.
- [x] every branch ends in a defined result: a tab outside the allowed spans returns TAB_PLAIN(n). A dedent that misses every open level, or empties the stack, returns INDENT(n) (s5 is the empty-stack case). A changed item indent returns the `_field` 106 text. A continuation inside a tools field is left to `_field`, which returns its item 075 text (c1, c2, c3, c5). Otherwise, existing behaviour is kept.
- [x] no leftover TODOs or unused files: `grep -n TODO tests/test_agent_tools.py` gives nothing. No new file.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` gives `38`, all pre-existing (ccbot/ is not changed). The same pattern on tests/test_agent_tools.py gives 0 hits. The new code has no dataclass field and no numeric default. `first = None` is never defaulted: it is set by the first item. The `>` tests are on ints (`stack[-1] > ind`) and cannot be NaN.
- Feasibility numbers (04 Guardrail tests), measured: the real tree has `grep -c $'\t' .claude/agents/*.md` = 0 in each of the 7 files, and `test_no_shell_agents_leave_commands_to_orchestrator` passes. The fixture selection from the base check below is TAB_PLAIN 12 (w1-w6, w9, w10, w13, tb1-tb3), INDENT 4 (s1, s2, s4, s5), `_field` 075 text 4 (c1, c2, c3, c5) and `_field` 106 text 1 (f1).

## Test output (pasted, not summarized)
Tests 1, base check (`wt2`, a522c5d test file plus the 2 constants and the 29 CASES only, the old parser): `python3 -m pytest -q -p no:cacheprovider tests/test_agent_tools.py`
```
FAILED tests/test_agent_tools.py::test_agent_tools_parser[c1_tools_continuation_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[c2_tools_item_continuation_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[c3_disallowed_continuation_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[c5_tools_col0_item_continuation]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[f1_tools_item_indents]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[s1_map_dedent_between]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[s2_tools_list_dedent]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[s4_dedent_off_level]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[s5_indented_first_line]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[tb1_tools_comma_tab]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[tb2_tools_trailing_tab]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[tb3_tools_flow_tab]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w10_tab_in_empty_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w13_tab_in_flow_after_quoted_hash]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w1_tab_before_hash_colon]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w2_tab_before_hash]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w3_tab_in_plain]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w4_tab_in_continuation]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w5_tab_in_item]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w6_tab_in_block_header]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[w9_tab_after_bare_hash]
21 failed, 144 passed in 0.35s
```
That is exactly the 21 ids in 04 Tests 1.

What the old parser returns on the new cases (`agent_tools(text)` in `wt2`, with the guard set). These confirm 03 Self-check 2 and 27:
```
c1_tools_continuation_key -> (set(), 'colon in unquoted value on frontmatter line 3 (item 104; quote the value)')
c2_tools_item_continuation_key -> (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
c3_disallowed_continuation_key -> (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
c4_flag_cleared_by_key -> (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
c5_tools_col0_item_continuation -> (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
f1_tools_item_indents -> ({'Read', 'Bash'}, None)
s1_map_dedent_between -> ({'Read', 'Write'}, None)
s2_tools_list_dedent -> ({'Read', 'Write'}, None)
s3_compact_map_in_list -> ({'Read', 'Write'}, None)
s4_dedent_off_level -> ({'Read', 'Write'}, None)
s5_indented_first_line -> ({'Read', 'Write'}, None)
s6_list_at_key_indent -> ({'Read', 'Write'}, None)
s7_nested_dash_levels -> ({'Read', 'Write'}, None)
tb1_tools_comma_tab -> ({'Read', 'Write'}, None)
tb2_tools_trailing_tab -> ({'Read'}, None)
tb3_tools_flow_tab -> ({'Read', 'Write'}, None)
w10_tab_in_empty_key -> ({'Read', 'Write'}, None)
w11_tab_in_block_content -> ({'Read', 'Write'}, None)
w12_tab_in_comment_line -> ({'Read', 'Write'}, None)
w13_tab_in_flow_after_quoted_hash -> ({'Read', 'Write'}, None)
w1_tab_before_hash_colon -> ({'Read', 'Write'}, None)
w2_tab_before_hash -> ({'Read', 'Write'}, None)
w3_tab_in_plain -> ({'Read', 'Write'}, None)
w4_tab_in_continuation -> ({'Read', 'Write'}, None)
w5_tab_in_item -> ({'Read', 'Write'}, None)
w6_tab_in_block_header -> ({'Read', 'Write'}, None)
w7_tab_in_quote -> ({'Read', 'Write'}, None)
w8_tab_in_comment -> ({'Read', 'Write'}, None)
w9_tab_after_bare_hash -> ({'Read', 'Write'}, None)
```
RI-002 tool-set paths (03 step 7): s2, tb1, tb3 and w1 each returned a tool set ({Read, Write}) at a522c5d from YAML that the pure loader rejects (measured below: ParserError, ScannerError, ScannerError, ScannerError). After this build they fail closed: s2 gives INDENT(4), and tb1, tb3 and w1 give TAB_PLAIN(2).

Tests 2, after the build (main checkout): `python3 -m pytest -q -p no:cacheprovider tests/test_agent_tools.py`
```
........................................................................ [ 43%]
........................................................................ [ 87%]
.....................                                                    [100%]
165 passed in 0.13s
```
`test_no_shell_agents_leave_commands_to_orchestrator` is among the 165. The 7 real files pass and NO_SHELL is unchanged.

Tests 3, full suite. First the base, measured at a522c5d in `wt` (`python3 -m pytest -q -p no:cacheprovider`, with the guard set):
```
1040 passed, 1 skipped in 218.92s (0:03:38)
```
Then after the build, in the main checkout from the repo root (`python3 -m pytest -q`), last lines as printed:
```
........................................................................ [ 87%]
........................................................................ [ 94%]
..............................................................           [100%]
1069 passed, 1 skipped in 128.99s (0:02:08)
```
1069 = 1040 + 29, with 1 skipped, as 04 expects.

Suite: 1069 passed, 1 skipped in 128.99s (0:02:08)

Tests 4: `python3.11 -m py_compile` on a copy of the build file in the scratch dir gives `py_compile 3.11 OK exit 0` (python3.11 is 3.11.18).

Tests 6, the unchanged cases (main checkout, build file, `agent_tools(text)` against each case's own expectation):
```
p13_doc_hooks_example -> (['Bash'], None) OK
q23_doc_mcp_example -> (['Read'], None) OK
d_yaml_list -> (['Read', 'Write'], None) OK
y1_continuation -> ([], "unparsed tools: line ', Bash' (item 075)") OK
y2_blank_in_list -> ([], 'blank or comment line inside tools: list (item 075)') OK
y3_comment_first -> ([], 'blank or comment line inside tools: list (item 075)') OK
y4_indented_plain -> ([], "unparsed tools: line 'Bash' (item 075)") OK
y5_inline_then_item -> ([], "unparsed tools: line '- Bash' (item 075)") OK
y6_blank_comment_then_key -> (['Read', 'Write'], None) OK
y7_disallowed_blank -> ([], 'blank or comment line inside disallowedTools: list (item 075)') OK
p4_bare_dash -> ([], "unparsed tools: entry '' (item 075)") OK
i2_block_single_quoted -> (['Bash'], None) OK
v3_nested_value_colon -> ([], 'colon in unquoted value on frontmatter line 3 (item 104; quote the value)') OK
v8_open_parent_plain -> (['Read', 'Write'], None) OK
v9_block_literal -> (['Read', 'Write'], None) OK
v10_block_folded_indicators -> (['Read', 'Write'], None) OK
v16_key_1025_indented -> ([], 'key longer than 1024 characters on frontmatter line 3 (item 104)') OK
v17_key_1024_indented -> (['Read', 'Write'], None) OK
v18_comment_key_then_item -> (['Read', 'Write'], None) OK
v19_spec_two_comments -> (['Read', 'Write'], None) OK
v20_comment_key_then_map -> (['Read', 'Write'], None) OK
v21_tools_comment_then_item -> ([], "unparsed tools: line '- Read' (item 075)") OK
v23_hash_in_word_colon -> ([], 'colon in unquoted value on frontmatter line 2 (item 104; quote the value)') OK
v24_gt_inside_value -> (['Read', 'Write'], None) OK
v25_bar_inside_value -> (['Read', 'Write'], None) OK
v26_dash_key_continuation -> ([], 'colon in unquoted value on frontmatter line 3 (item 104; quote the value)') OK
nk6_tools_col0_list -> (['Read', 'Write'], None) OK
nk7_item_after_empty_key -> (['Read', 'Write'], None) OK
nk8_item_after_nested_map -> ([], 'no key on frontmatter line 4 (item 096)') OK
nk12_indented_comment_then_item -> (['Read', 'Write'], None) OK
```
(04 Tests 6 has "v16 to v21". All six are listed above. `d` is `d_yaml_list`.)

Extra research 1 shape on the build (main checkout):
```
er1 ({'Read', 'Write'}, None)
er1_tools (set(), "unparsed tools: line 'Bash: x' (item 075)")
D3 ({'Read', 'Write'}, None)
```
At a522c5d (`wt2`) the result is the same: `base er1 ({'Read', 'Write'}, None)`, `base er1_tools (set(), "unparsed tools: line 'Bash: x' (item 075)")`. As 04 predicted, the tools form fails closed in `_field`. The non-tools form passes and is documented under "Not checked".

## Mutations (04 Tests 5)
`tools/mut.py <scratch>` applies one mutation at a time to `wt2/tests/test_agent_tools.py`, starting from `new.py` (the build file). It runs `python3 -m pytest -q -p no:cacheprovider tests/test_agent_tools.py` in `wt2` and asserts that both env vars are set. At the end it writes the build file back. Env check, as printed:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-106-r1-9bz7fki9/pyc-_zfzovfv python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-106-r1-9bz7fki9/pyc-_zfzovfv
```
Output (`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<that dir> python3 tools/mut.py <scratch>`):
```
BUILD: 165 passed in 0.12s | failed: -
M69: 12 failed, 153 passed in 0.28s | failed: tb1_tools_comma_tab, tb2_tools_trailing_tab, tb3_tools_flow_tab, w10_tab_in_empty_key, w13_tab_in_flow_after_quoted_hash, w1_tab_before_hash_colon, w2_tab_before_hash, w3_tab_in_plain, w4_tab_in_continuation, w5_tab_in_item, w6_tab_in_block_header, w9_tab_after_bare_hash
M70: 1 failed, 164 passed in 0.14s | failed: w8_tab_in_comment
M71: 1 failed, 164 passed in 0.21s | failed: w7_tab_in_quote
M72: 1 failed, 164 passed in 0.15s | failed: w9_tab_after_bare_hash
M73: 4 failed, 161 passed in 0.18s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level, s5_indented_first_line
M74: 1 failed, 164 passed in 0.14s | failed: s7_nested_dash_levels
M75: 3 failed, 162 passed in 0.18s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level
M76: 4 failed, 161 passed in 0.17s | failed: c1_tools_continuation_key, c2_tools_item_continuation_key, c3_disallowed_continuation_key, c5_tools_col0_item_continuation
M77: 1 failed, 164 passed in 0.14s | failed: c4_flag_cleared_by_key
M78: 4 failed, 161 passed in 0.18s | failed: c5_tools_col0_item_continuation, nk6_tools_col0_list, nk9_tools_blank_then_item, v21_tools_comment_then_item
M79: 1 failed, 164 passed in 0.14s | failed: f1_tools_item_indents
M80: 2 failed, 163 passed in 0.15s | failed: w11_tab_in_block_content, w12_tab_in_comment_line
M81: 1 failed, 164 passed in 0.14s | failed: w13_tab_in_flow_after_quoted_hash
M56: 9 failed, 156 passed in 0.23s | failed: c4_flag_cleared_by_key, n13_value_colon, v12_block_ends, v1_value_colon, v23_hash_in_word_colon, v26_dash_key_continuation, v2_value_colon_end, v3_nested_value_colon, v6_continuation_colon
M57: 1 failed, 164 passed in 0.15s | failed: v4_colon_in_comment
M58: 3 failed, 162 passed in 0.17s | failed: c4_flag_cleared_by_key, v26_dash_key_continuation, v6_continuation_colon
M59: 3 failed, 162 passed in 0.18s | failed: v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented
M60: 2 failed, 163 passed in 0.16s | failed: v14_key_1024, v17_key_1024_indented
M61: 4 failed, 161 passed in 0.19s | failed: v18_comment_key_then_item, v19_spec_two_comments, v20_comment_key_then_map, v21_tools_comment_then_item
M62: 4 failed, 161 passed in 0.20s | failed: v10_block_folded_indicators, v12_block_ends, v9_block_literal, w11_tab_in_block_content
M63: 1 failed, 164 passed in 0.15s | failed: v22_tools_entry_colon
M64: 2 failed, 163 passed in 0.15s | failed: p13_doc_hooks_example, s3_compact_map_in_list
M65: 1 failed, 164 passed in 0.15s | failed: v12_block_ends
M66: 1 failed, 164 passed in 0.14s | failed: v11_block_header_text
M67: 1 failed, 164 passed in 0.15s | failed: v10_block_folded_indicators
M68: 1 failed, 164 passed in 0.14s | failed: v17_key_1024_indented
X1: 10 failed, 155 passed in 0.25s | failed: n13_value_colon, v11_block_header_text, v12_block_ends, v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented, v1_value_colon, v23_hash_in_word_colon, v2_value_colon_end, v3_nested_value_colon
X2: 1 failed, 164 passed in 0.16s | failed: v23_hash_in_word_colon
X3: 2 failed, 163 passed in 0.17s | failed: v24_gt_inside_value, v25_bar_inside_value
X4: 1 failed, 164 passed in 0.15s | failed: v26_dash_key_continuation
```
After the run: `cmp new.py wt2/tests/test_agent_tools.py` printed "wt2 file = build file", and `cmp new.py <repo>/tests/test_agent_tools.py` printed "repo file = build file".

- M69 to M81 each fail exactly their 03 step 5 ids.
- M56 to M68 and X1 to X4 each still fail every id in their 104/06 round 2 list (L145-L162). New ids, recorded and not a Deviation (04 Tests 5): M56 +c4, M58 +c4, M62 +w11 and M64 +s3.
- Mutation forms: M69 to M81 follow 03 step 5, and M80 moves the tab check to just after `t = line.strip()`. M56 to M68 use the 104/05 L74 forms. X1 (an I3 form, which 104/06 describes as "VALUE/BLOCK/KEY_LONG errors ignored") is the structure branch's `if error:` changed to `if False:`. X2 to X4 use the 104/04 L113-L115 forms.

## PyYAML probe (04 Tests 7; information only, not a claim about Claude Code)
`probe/probe.py` loads each shape's frontmatter lines (no `---`) with `yaml.load(..., Loader=L)`. Run 1 is `venv/bin/python -I probe.py` in the scratch venv (PyYAML 6.0.1, `__with_libyaml__` False, so CSafeLoader is absent). It matches the system `python3 -I` (/usr/lib/python3/dist-packages, also 6.0.1 pure, the orchestrator's measurement). Run 2 is `python3 probe.py` with the user site (~/.local, PyYAML 6.0.3, libyaml True), so CSafeLoader is measured there.

| case | test (build) | 6.0.1 SafeLoader | 6.0.3 SafeLoader | 6.0.3 CSafeLoader |
|---|---|---|---|---|
| w1 | TAB_PLAIN(2) | ScannerError (found character '\t' that cannot start any token) | same | loads description 'a' |
| w2 | TAB_PLAIN(2) | ScannerError (same text) | same | loads 'a' |
| w3 | TAB_PLAIN(2) | ScannerError (same text) | same | loads 'a\tb' |
| w4 | TAB_PLAIN(3) | ScannerError (same text) | same | loads 'x more' |
| w5 | TAB_PLAIN(3) | ScannerError (same text) | same | loads hooks ['a'] |
| w6 | TAB_PLAIN(2) | ScannerError (expected chomping or indentation indicators, but found '\t') | same | loads 'a\n' |
| w7 | {Read, Write} | loads 'a\t# b' | same | loads 'a\t# b' |
| w8 | {Read, Write} | loads 'a' | same | loads 'a' |
| w9 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads 'a#\tb' |
| w10 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads {'a\tb': {'c': 'd'}} |
| w11 | {Read, Write} | loads 'a\tb\n' | same | loads 'a\tb\n' |
| w12 | {Read, Write} | loads | same | loads |
| w13 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads ['a #', 'b\tc'] |
| tb1 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads tools 'Read,\tWrite' |
| tb2 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads tools ['Read'] |
| tb3 | TAB_PLAIN(2) | ScannerError (found character '\t' ...) | same | loads tools ['Read', 'Write'] |
| s1 | INDENT(4) | ParserError (expected <block end>, but found '<block mapping start>') | same | ParserError (did not find expected key) |
| s2 | INDENT(4) | ParserError (expected <block end>, but found '<block sequence start>') | same | ParserError (did not find expected key) |
| s3 | {Read, Write} | loads hooks [{'a': 'b', 'c': 'd'}, {'e': 'f'}] | same | same |
| s4 | INDENT(4) | ParserError (expected <block end>, but found '<block mapping start>') | same | ParserError (did not find expected key) |
| s5 | INDENT(3) | ParserError (expected '<document start>', but found '<block mapping start>') | same | ParserError (did not find expected <document start>) |
| s6 | {Read, Write} | loads hooks {'a': ['x'], 'b': 'c'} | same | same |
| s7 | {Read, Write} | loads hooks [['a', 'b']] | same | same |
| c1 | 075 text 'Bash: x' | ScannerError (mapping values are not allowed here) | same | ScannerError (mapping values are not allowed in this context) |
| c2 | 075 text 'Bash: x' | ScannerError (same) | same | ScannerError (same) |
| c3 | 075 text 'Read: x' | ScannerError (same) | same | ScannerError (same) |
| c4 | VALUE(4) | ScannerError (same) | same | ScannerError (same) |
| c5 | 075 text 'Bash: x' | ScannerError (same) | same | ScannerError (same) |
| f1 | 106 `_field` text | loads tools ['Read - Bash'] | same | loads tools ['Read - Bash'] |
| er1 `hooks:`/`  - x`/`  a: v` | {Read, Write} (Not checked) | ParserError (expected <block end>, but found '?') | same | ParserError (did not find expected '-' indicator) |
| er1 tools `tools:`/`  - Read`/`  Bash: x` | 075 text 'Bash: x' | ParserError (expected <block end>, but found '?') | same | ParserError (did not find expected '-' indicator) |

D4 applied:
- s5: PyYAML raises in both loaders, so it is not a fail-closed false error, and the docstring does not list it.
- s3, s6, s7: they load in both loaders, so no "Not checked" line is added.
- f1: both loaders load `['Read - Bash']` (one entry that is not a tool name). The test refuses it, which fails closed.
- er1: both loaders raise, as 04 Extra research 1 predicted for the indented form. The test passes the non-tools form, and the docstring lists it under "Not checked".
- The tab rows show the loader split that the docstring states: the pure loader raises, and libyaml loads on 12 of the 12 TAB_PLAIN shapes. The docstring keeps "measured on PyYAML 6.0.1 and 6.0.4" as 03 D1 words it. 6.0.3 (measured here) agrees.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_agent_tools.py only; no ccbot/realtest.py or TRIGGER file)

## Deviations from plan
None. Every count matched 04: base check 21 failed / 144 passed with the 21 listed ids; 165 passed after the build; full suite 1040 -> 1069 with 1 skipped; M69-M81 exactly their lists; the 104 mutations still kill every listed id (new ids recorded above). The docstring follows 03 step 6 plus the Extra research 1 line. Under D4, the conditional "s5 if PyYAML loads it" clause is left out because the probe shows that PyYAML raises on s5.

`check_pipeline.py` before commit (main checkout): exit 0, `INCOMPLETE: none`, `SKIPPED: none`, `STASH: none`, `UNTRACKED CHANGE: none`, `LOG TIME: none`.

## Recurring issues checked (item 013)
RI-001: ESCALATED, unchanged. Every count here comes from a command: 0 tabs in 7 agent files, 21/144 base, 165, 1040 -> 1069, and the per-mutation lists. Nothing is claimed as "always".
RI-014: OPEN, unchanged. This item does not touch git, clones or history.
RI-002: GUARDED, holds (this item's root cause; near miss closed). s2, tb1, tb3 and w1 each gave a tool set from YAML the pure loader rejects. They now give INDENT/TAB_PLAIN, and tb2, s1, s4, s5 and f1 also fail closed. `first` is never defaulted. The missing-data grep shows no new hits.
RI-004/005: GUARDED, holds. Every 03 Self-check trace was re-run as a test or a mutant, and all matched.
RI-006: GUARDED, holds. File counts, the Suite line and the mutant counts were copied from command output.
RI-007: GUARDED, holds. Scope FULL. This is the I2 step after 04.
RI-008: GUARDED, holds. `python3.11 -m py_compile` exit 0. There is no walrus and no `match`.
RI-009: GUARDED, holds. Mutants ran only in `wt2` inside my own mkdtemp dir, with the guard on every command. The file was restored from `new.py`, and no stash was used.
RI-010: GUARDED, holds. The log line is written with `--log` right after this file, and the env-check line is pasted above the mutant output.
RI-012: GUARDED, holds. The in-text negatives w7, w8, w11 and w12 and the edges w9 and w13 each fail under their own mutant (M71, M70, M80, M72, M81).
RI-003, RI-011, RI-013: not applicable (no calendar, merge-base or realtest path).
