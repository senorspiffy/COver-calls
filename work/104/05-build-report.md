# 05 Build report - 104
Base commit: 519cbc2 (branch daily-fixes/2026-11-24-b, I1 FIT). Build tree = 519cbc2 + tests/test_agent_tools.py; cbcc301 (item 100 I3, work/100 + log only) landed on the branch during the build.
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-104-r1-re6j7rnt

## Changes made (file: what changed)
- tests/test_agent_tools.py (the only code file, as planned):
  - Constants next to KEY_RE: `BLOCK_RE`, `ITEMS_RE`, `COMMENT_CUT_RE`, `COLON_RE`, `KEY_MAX = 1024`, texts exactly as 03 step 1 with a plain `|` (04 Extra research 4). Error texts `VALUE`, `KEY_LONG`, `BLOCK` after `NO_KEY`, verbatim D7.
  - Helpers before `_frontmatter_error`: `_is_open(rest)`, `_plain_colon(text)`, `_node(line, n, check)` returning `(error, col, is_open, starts_block)`, as 03 step 2. Python 3.10 syntax (no walrus, no `match`).
  - `_frontmatter_error`: docstring "(items 080, 087, 096, 104)"; `prev = None`, `block = None` before the loop; block-skip, continuation and structure-line branches after the column-0 (096) check and before the `prev_open` update; `prev_open` now uses `_is_open(line[k.end():])` (F-5). `s`, `c` not reused.
  - CASES v1-v22 (ids with descriptive suffixes, e.g. `v1_value_colon`), fixtures exactly as 03 step 4; TREE `n13_value_colon`.
  - Module docstring: "Item 104:" paragraph (03 step 6 content); in "Item 096" the clause "a column-0 item after an empty-valued key that carries a comment (`hooks: # c`);" removed. 080/087 false-error lists unchanged (D2).

File counts (commands, item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> 0 new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> 1 changed
- `git diff --stat`: ` tests/test_agent_tools.py | 121 ++++++++++++++++++++++++++++++++++++++++++++--` / ` 1 file changed, 117 insertions(+), 4 deletions(-)`

## Connectivity check
- [x] every new function/rule is used: `_node` and `_plain_colon` are called from `_frontmatter_error` (`_plain_colon` also from `_node`); `_is_open` from `_node` and the `prev_open` update; `BLOCK_RE`/`ITEMS_RE`/`COMMENT_CUT_RE`/`COLON_RE`/`KEY_MAX` each read in a helper; `VALUE`, `KEY_LONG`, `BLOCK` returned and used by fixtures (v1-v3, v6, v12, n13 / v13, v15, v16 / v11).
- [x] every input has a source, every output has a consumer: input is `front` from `agent_tools`; the new errors go `agent_tools` -> `tree_problems` -> the real-tree test assertion (n13 pins the tree path).
- [x] every branch ends in a defined result: blank/comment -> skipped; block content -> skipped (104 checks only), block end -> `block = None` then normal handling (v12); continuation -> VALUE or pass (v6/v7); structure line -> open, closed, block start, VALUE, BLOCK or KEY_LONG; FLOW_KEYS lines -> `check=False`, left to `_field` (v21/v22). No previous structure line (`prev = None`) -> structure line, never a continuation (v1, v13).
- [x] no leftover TODOs or unused files: none added. The mutation script, probe script and venv live only in the scratch dir.

Missing-data policy: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` -> 38, all pre-existing; `git diff --stat -- ccbot/` is empty, so no new or changed hit. No dataclass field added. The one new `>` test (`k.end() - 1 > KEY_MAX`) compares two ints, never NaN. An unreadable value, header or key gives VALUE/BLOCK/KEY_LONG with its line number, never a tool set.

Feasibility numbers (04 Guardrail tests), re-measured 2026-11-25:
- Real tree: 7 files, 21 frontmatter lines (awk between the `---` lines); `grep -cE '^(name|description|tools):.*(:[ \t]|:$| #)'` over them -> 0. `test_no_shell_agents_leave_commands_to_orchestrator` -> `1 passed, 131 deselected in 0.02s` (targeted run, then in the full suite).
- Existing fixtures: 109 of 109 keep their result (132 passed below; BASE run shows only the 13 new ids fail on the old parser).
- Key cap: longest real key 11 (`description`); boundary in v13-v17 and the probe below.

## Test output (pasted, not summarized)
`python3 -m pytest tests/test_agent_tools.py -q` (repo, build tree):
```
........................................................................ [ 54%]
............................................................             [100%]
132 passed in 0.11s
```
`python3.11 -m py_compile tests/test_agent_tools.py` -> no output, exit 0 (RI-008; `python3.10` not installed, Python 3.13.18 default).

Base check and mutations, one at a time on the scratch worktree `/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-104-r1-re6j7rnt/wt` (detached at 519cbc2, test file replaced by the build file, each mutation applied by `mut.py`, file restored after; `python3 mut.py <scratch>`). BASE = the 519cbc2 loop body (104 branches removed, old `prev_open` line) with the new fixtures:
```
BASE: 13 failed, 119 passed in 0.12s | failed: test_agent_tools_parser[v11_block_header_text], test_agent_tools_parser[v12_block_ends], test_agent_tools_parser[v13_key_1025], test_agent_tools_parser[v15_key_1025_after_key], test_agent_tools_parser[v16_key_1025_indented], test_agent_tools_parser[v18_comment_key_then_item], test_agent_tools_parser[v19_spec_two_comments], test_agent_tools_parser[v1_value_colon], test_agent_tools_parser[v21_tools_comment_then_item], test_agent_tools_parser[v2_value_colon_end], test_agent_tools_parser[v3_nested_value_colon], test_agent_tools_parser[v6_continuation_colon], test_tree_problems[n13_value_colon]
M41: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[q30_marker_prefix_text]
M42: 12 failed, 120 passed in 0.13s | failed: test_agent_tools_parser[nk10_inner_colon_key], test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk13_space_hash_in_key], test_agent_tools_parser[nk14_space_hash_empty_key_then_item], test_agent_tools_parser[nk16_tab_hash_empty_key_then_item], test_agent_tools_parser[nk1_plain_word], test_agent_tools_parser[nk2_plain_word_last], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk5_indicator_key], test_agent_tools_parser[nk8_item_after_nested_map], test_tree_problems[n12_no_key_line]
M43: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[nk2_plain_word_last]
M44: 4 failed, 128 passed in 0.14s | failed: test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk8_item_after_nested_map]
M45: 18 failed, 114 passed in 0.13s | failed: test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk6_tools_col0_list], test_agent_tools_parser[nk7_item_after_empty_key], test_agent_tools_parser[nk8_item_after_nested_map], test_agent_tools_parser[nk9_tools_blank_then_item], test_agent_tools_parser[p13_doc_hooks_example], test_agent_tools_parser[p14_nested_open_quote], test_agent_tools_parser[q13_flow_next_line], test_agent_tools_parser[q15_item_open_map], test_agent_tools_parser[q18_dash_tab], test_agent_tools_parser[q23_doc_mcp_example], test_agent_tools_parser[q5_item_anchor], test_agent_tools_parser[q6_item_open_quote], test_agent_tools_parser[v16_key_1025_indented], test_agent_tools_parser[v17_key_1024_indented], test_agent_tools_parser[v19_spec_two_comments], test_agent_tools_parser[v3_nested_value_colon], test_agent_tools_parser[v8_open_parent_plain]
M46: 5 failed, 127 passed in 0.11s | failed: test_agent_tools_parser[p15_quoted_key], test_agent_tools_parser[q16_explicit_key], test_agent_tools_parser[q17_colon_start], test_agent_tools_parser[q27_doc_end_marker], test_agent_tools_parser[q28_doc_start_marker]
M47: 1 failed, 131 passed in 0.11s | failed: test_agent_tools_parser[nk5_indicator_key]
M48: 1 failed, 131 passed in 0.10s | failed: test_agent_tools_parser[nk8_item_after_nested_map]
M49: 2 failed, 130 passed in 0.11s | failed: test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk9_tools_blank_then_item]
M50: 1 failed, 131 passed in 0.15s | failed: test_agent_tools_parser[s_no_space]
M51: 1 failed, 131 passed in 0.13s | failed: test_agent_tools_parser[nk11_item_first_line]
M52: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[nk12_indented_comment_then_item]
M53: 3 failed, 129 passed in 0.11s | failed: test_agent_tools_parser[nk13_space_hash_in_key], test_agent_tools_parser[nk14_space_hash_empty_key_then_item], test_agent_tools_parser[nk16_tab_hash_empty_key_then_item]
M54: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[nk16_tab_hash_empty_key_then_item]
M55: 1 failed, 131 passed in 0.11s | failed: test_agent_tools_parser[nk15_hash_inside_key]
M56: 6 failed, 126 passed in 0.11s | failed: test_agent_tools_parser[v12_block_ends], test_agent_tools_parser[v1_value_colon], test_agent_tools_parser[v2_value_colon_end], test_agent_tools_parser[v3_nested_value_colon], test_agent_tools_parser[v6_continuation_colon], test_tree_problems[n13_value_colon]
M57: 1 failed, 131 passed in 0.14s | failed: test_agent_tools_parser[v4_colon_in_comment]
M58: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[v6_continuation_colon]
M59: 3 failed, 129 passed in 0.13s | failed: test_agent_tools_parser[v13_key_1025], test_agent_tools_parser[v15_key_1025_after_key], test_agent_tools_parser[v16_key_1025_indented]
M60: 2 failed, 130 passed in 0.13s | failed: test_agent_tools_parser[v14_key_1024], test_agent_tools_parser[v17_key_1024_indented]
M61: 4 failed, 128 passed in 0.11s | failed: test_agent_tools_parser[v18_comment_key_then_item], test_agent_tools_parser[v19_spec_two_comments], test_agent_tools_parser[v20_comment_key_then_map], test_agent_tools_parser[v21_tools_comment_then_item]
M62: 3 failed, 129 passed in 0.11s | failed: test_agent_tools_parser[v10_block_folded_indicators], test_agent_tools_parser[v12_block_ends], test_agent_tools_parser[v9_block_literal]
M63: 1 failed, 131 passed in 0.13s | failed: test_agent_tools_parser[v22_tools_entry_colon]
M64: 1 failed, 131 passed in 0.11s | failed: test_agent_tools_parser[p13_doc_hooks_example]
M65: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[v12_block_ends]
M66: 1 failed, 131 passed in 0.11s | failed: test_agent_tools_parser[v11_block_header_text]
M67: 1 failed, 131 passed in 0.12s | failed: test_agent_tools_parser[v10_block_folded_indicators]
M68: 1 failed, 131 passed in 0.11s | failed: test_agent_tools_parser[v17_key_1024_indented]
```
Every list equals 03 step 5 / 04: BASE 13 failed, 119 passed (v1, v2, v3, v6, v11, v12, v13, v15, v16, v18, v19, v21, n13); M56-M68 each fail exactly their listed ids; M41-M55 fail every id of their 096/05 round 2 lists, and M45 adds exactly v3, v8, v16, v17, v19 (as 03 predicted). M64 prints `colon in unquoted value on frontmatter line 8 (item 104; quote the value)` for p13, i.e. VALUE(8) as corrected in 04 Extra research 3.
Mutation forms: M41-M55 as in 096/05 (M42 = 096 column-0 check, `prev_open` init and update removed; M49 = `else: prev_open = False` on blank/comment lines; M52 = `line.startswith("#")` in the shared `if`). M56 `_plain_colon` returns False; M57 comment cut removed; M58 continuation test `if False:`; M59 cap `if False:`; M60 `>=`; M61 `_is_open` = `not rest.strip()`; M62 `block = col` -> `pass`; M63 `_node(line, n, True)`; M64 `prev = (ind, op)`; M65 block-content test `if True:` (block never ends: every later line is content); M66 header branch -> `if t[0] in "|>" and BLOCK_RE.fullmatch(t): return None, col, False, True` (a non-header `|`/`>` value falls through to `_plain_colon`); M67 `BLOCK_RE = r"[|>][ \t]*"`; M68 `col + k.end() - 1 > KEY_MAX`.
Note: my first M66 form (`if t[0] in "|>":` -> `if False:`) also disabled block detection and failed v9, v10, v11, v12 (4 failed, 128 passed); that is not the 03 mutation ("non-header value sent to `_plain_colon`"), so it was replaced by the form above, which fails v11 alone.

Extra research 2 edge (information): `_fm("tools: Read, Write", "  foo: bar")` -> `colon in unquoted value on frontmatter line 3 (item 104; quote the value)` (continuation branch, fails closed; before 104 it was `_field`'s `unparsed tools:` error). No fixture added, as planned.

PyYAML probe (03 step 7, information only, D6: not used by the test), scratch venv `/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-104-r1-re6j7rnt/venv`, `pip install pyyaml`, run `venv/bin/python -I probe.py <scratch>`; frontmatter text between the `---` lines fed to `yaml.load` with SafeLoader and CSafeLoader; `k...` = the 1024/1025-character key shortened in the paste:
```
PyYAML 6.0.4 libyaml True
| case | test result | SafeLoader | CSafeLoader |
|---|---|---|---|
| v1_value_colon | colon in unquoted value on frontmatter line 2 (item 104; quote the value) | error: mapping values are not allowed here (line 1) | error: mapping values are not allowed in this context (line 1) |
| v2_value_colon_end | colon in unquoted value on frontmatter line 2 (item 104; quote the value) | error: mapping values are not allowed here (line 1) | error: mapping values are not allowed in this context (line 1) |
| v3_nested_value_colon | colon in unquoted value on frontmatter line 3 (item 104; quote the value) | error: mapping values are not allowed here (line 2) | error: mapping values are not allowed in this context (line 2) |
| v4_colon_in_comment | tools Read,Write | loads {'description': 'a', 'tools': 'Read, Write'} | loads {'description': 'a', 'tools': 'Read, Write'} |
| v5_url_colon | tools Read,Write | loads {'description': 'see https://x', 'tools': 'Read, Write'} | loads {'description': 'see https://x', 'tools': 'Read, Write'} |
| v6_continuation_colon | colon in unquoted value on frontmatter line 3 (item 104; quote the value) | error: mapping values are not allowed here (line 2) | error: mapping values are not allowed in this context (line 2) |
| v7_continuation_plain | tools Read,Write | loads {'description': 'x more text', 'tools': 'Read, Write'} | loads {'description': 'x more text', 'tools': 'Read, Write'} |
| v8_open_parent_plain | tools Read,Write | loads {'description': 'plain text', 'tools': 'Read, Write'} | loads {'description': 'plain text', 'tools': 'Read, Write'} |
| v9_block_literal | tools Read,Write | loads {'description': 'a: b\n', 'tools': 'Read, Write'} | loads {'description': 'a: b\n', 'tools': 'Read, Write'} |
| v10_block_folded_indicators | tools Read,Write | loads {'description': 'x: y', 'tools': 'Read, Write'} | loads {'description': 'x: y', 'tools': 'Read, Write'} |
| v11_block_header_text | unreadable block scalar header on frontmatter line 2 (item 104) | error: expected a comment or a line break, but found 'f' (line 1) | error: did not find expected comment or line break (line 1) |
| v12_block_ends | colon in unquoted value on frontmatter line 4 (item 104; quote the value) | error: mapping values are not allowed here (line 3) | error: mapping values are not allowed in this context (line 3) |
| v13_key_1025 | key longer than 1024 characters on frontmatter line 2 (item 104) | error: mapping values are not allowed here (line 1) | error: mapping values are not allowed in this context (line 1) |
| v14_key_1024 | tools Read,Write | loads {'k...... | loads {'k...... |
| v15_key_1025_after_key | key longer than 1024 characters on frontmatter line 3 (item 104) | error: could not find expected ':' (line 2) | error: could not find expected ':' (line 2) |
| v16_key_1025_indented | key longer than 1024 characters on frontmatter line 3 (item 104) | error: mapping values are not allowed here (line 2) | error: mapping values are not allowed in this context (line 2) |
| v17_key_1024_indented | tools Read,Write | loads {'hooks': {'k...... | loads {'hooks': {'k...... |
| v18_comment_key_then_item | tools Read,Write | loads {'hooks': ['a'], 'tools': 'Read, Write'} | loads {'hooks': ['a'], 'tools': 'Read, Write'} |
| v19_spec_two_comments | tools Read,Write | loads {'hr': ['Mark McGwire', 'Sammy Sosa'], 'rbi': ['Sammy Sosa', 'Ken G... | loads {'hr': ['Mark McGwire', 'Sammy Sosa'], 'rbi': ['Sammy Sosa', 'Ken G... |
| v20_comment_key_then_map | tools Read,Write | loads {'hooks': {'a': 'b'}, 'tools': 'Read, Write'} | loads {'hooks': {'a': 'b'}, 'tools': 'Read, Write'} |
| v21_tools_comment_then_item | unparsed tools: line '- Read' (item 075) | loads {'tools': ['Read']} | loads {'tools': ['Read']} |
| v22_tools_entry_colon | unparsed tools: entry 'Bash: x' (item 075) | error: mapping values are not allowed here (line 1) | error: mapping values are not allowed in this context (line 1) |
| e1 name: x / '  - a' | tools Read,Write | loads {'name': 'x - a'} | loads {'name': 'x - a'} |
| e2 hooks: / '    a: b' / '  c: d' | tools Read,Write | error: expected <block end>, but found '<block mapping start>' (line 3) | error: did not find expected key (line 3) |
| b1024 first line | tools Read,Write | loads {'k...... | loads {'k...... |
| b1024 after name: x | tools Read,Write | loads {'name': 'x', 'k...... | loads {'name': 'x', 'k...... |
| b1024 indented under hooks: | tools Read,Write | loads {'hooks': {'k...... | loads {'hooks': {'k...... |
| b1025 first line | key longer than 1024 characters on frontmatter line 2 (item 104) | error: mapping values are not allowed here (line 1) | error: mapping values are not allowed in this context (line 1) |
| b1025 after name: x | key longer than 1024 characters on frontmatter line 3 (item 104) | error: could not find expected ':' (line 2) | error: could not find expected ':' (line 2) |
| b1025 indented under hooks: | key longer than 1024 characters on frontmatter line 3 (item 104) | error: mapping values are not allowed here (line 2) | error: mapping values are not allowed in this context (line 2) |
```
- D8: v2 (`name: x:`) and v11 (`description: > foo`) both raise in PyYAML 6.0.4 (pure and libyaml), so no docstring change.
- D5: PyYAML loads a 1024-character key and raises on 1025 in all three positions (first line, after `name: x`, indented under `hooks:`), same as the test's cap. No change.
- Disagreements, both already documented: v21 (`tools: # c` / `- Read`) loads in PyYAML (the documented `_field` fail-closed false error, D4); e2 (`hooks:` / `    a: b` / `  c: d`) raises in PyYAML while the test passes it (sibling indentation, D3 "not checked" in the docstring). Every other v-case's test result agrees with PyYAML's load/raise.

Full suite, `python3 -m pytest -q` from the repo root, last lines as printed:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 985 passed, 1 skipped in 131.10s (0:02:11)
```
Suite: 1 failed, 985 passed, 1 skipped in 131.10s (0:02:11)

Expected, not a defect of this build (item 071): the one failure is `test_repo_pipeline_has_no_skipped_items`, caused by item 100's I3 FAIL r1 committed in cbcc301 during this build (100's 05 Scratch dir name broke the 097 rule; orchestrator's note). `python3 scripts/check_pipeline.py` -> exit 1; its non-`none` failure lines are only `I3 FAIL: 100` and `INCOMPLETE: 100 (05 Scratch dir '.../i2-100-r1b-twin92si' is not the mkdtemp form (item 097))`; 104 shows `in progress (FULL: next 05)`. Base suite at cc91abb (I2 100): `963 passed, 1 skipped`; 963 + 23 new = 986 = 985 passed + 1 failed.

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py | 121 ++++++++++++++++++++++++++++++++++++++++++++--)

## Deviations from plan
None. Every count matched 04: 132 passed; base 13 failed / 119 passed with the 13 listed ids; full suite +23 tests; M56-M68 and M41-M55 lists as planned; M64 VALUE(8).

## Recurring issues checked
logs/recurring-issues.md read first. Open or ESCALATED entries checked: RI-001, RI-010, RI-014; GUARDED entries also checked: RI-002, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-012.
RI-001: ESCALATED, unchanged. Each new filter's count is measured: 21 of 21 real frontmatter lines pass (real-tree test), 0 grep hits, 2026-11-25.
RI-002: GUARDED, unchanged. Near miss F-1 to F-5 → 104 closed: each unreadable shape gives VALUE/BLOCK/KEY_LONG (v1-v3, v6, v11-v13, v15, v16, n13); restore-a-default probes M56, M59, M62 fail their fixtures.
RI-004: GUARDED, unchanged. Every self-check row was re-run, not copied (M64 line number confirmed as 8).
RI-005: GUARDED, unchanged. Same as RI-004.
RI-006: GUARDED, unchanged. All counts are pytest output as printed; the `Suite:` line is copied unchanged into the I2 log field.
RI-007: GUARDED, unchanged. Scope FULL; code written only at I2.
RI-008: GUARDED, unchanged. python3.11 py_compile passes; no 3.11+ syntax.
RI-009: GUARDED, unchanged. Mutations and probe only in my own mkdtemp scratch worktree; no `git stash`; main checkout untouched by probes.
RI-010: ESCALATED, unchanged. The I2 log line is written by `check_pipeline.py --log` right after this file; commit via `scripts/commit_step.py`.
RI-012: GUARDED, unchanged. In-text negatives v4, v5, v7, v8, v9, v10, v14, v17 pass; M57, M60 and M68 fail them.
RI-014: OPEN, unchanged. Not applicable (no git or clone-depth path touched).
