# 06 Verification - 104
Verdict: FAIL (round 1)
Sent back to: I1 I2
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i3-104-r1-3wwcy8zl

Head fcf3cff (I2 commit), base 519cbc2 (I1 plan commit), branch daily-fixes/2026-11-24-b. I made the scratch dir myself with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-104-r1-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`. The full suite ran in `<scratch>/wt`, the mutants in `<scratch>/mut`. Both were made with `git worktree add --detach <dir> fcf3cff`. The PyYAML probe ran in `<scratch>/venv`. My scripts are in `<scratch>/tools` (mut.py, probe.py). `mut.py` restores the file from its in-memory copy after each mutant and ends with `git diff --quiet -- tests/` → clean. No `git stash` anywhere. The main checkout was used only to write this file and its log line. Item 100's files there were left alone.

## I1 audit (plan vs research)
- 04's Rule trace maps 03 map steps 1-7, D1-D8, Missing inputs, Removed claims and Self-check 26. I checked each one against 03. D3 is DROPPED, with 03's own reason (documented as not checked). Extra research 1 has a source (libyaml wiki) and changes nothing. Extra research 2-4 come from the code or the table escapes, and 3 corrects a number only (M64 gives VALUE(8)). No unsourced addition.
- Gap carried over from 03 (sent back, see below): 03's RI-012 list and 04's Guardrail tests name in-text negatives for COLON_RE (v5) and the comment cut's positive (v4). They name none for two other text classifiers: the comment cut needs whitespace before `#` (COMMENT_CUT_RE `[ \t]#`), and a block header is recognised only from the value's first character (`t[0] in "|>"`). No fixture has `#` inside a word of a value, or `|`/`>` inside a plain value.

## I2 audit (build vs plan)
Diff 519cbc2..fcf3cff outside work/ and logs/: only `tests/test_agent_tools.py | 121 +++++--`. I compared it line by line with 04 and 03 steps 1-6:
- Constants BLOCK_RE, ITEMS_RE, COMMENT_CUT_RE, COLON_RE, KEY_MAX are as 03 step 1, with a plain `|`. VALUE, KEY_LONG and BLOCK match the D7 texts exactly.
- `_is_open`, `_plain_colon` and `_node` match 03 step 2 statement by statement. `t[0]` is always safe: `_is_open` has already ruled out an empty or comment-only `t` and `rest`. No walrus and no `match`.
- In `_frontmatter_error`, `prev`/`block` are set before the loop. The block skip, the continuation branch and the structure-line branch come after the 096 column-0 check, and `prev_open` uses `_is_open`. This is in the planned order. `s` and `c` are not reused.
- CASES v1-v22 and TREE n13 match 03 step 4 (ids have suffixes).
- The docstring has the "Item 104:" paragraph and the 096 `hooks: # c` clause is removed. The 080/087 lists are unchanged.
- Connectivity, re-done: every new helper and constant is read (`_node` and `_plain_colon` from the loop, `_is_open` from `_node` and `prev_open`, each regex in one helper). The new errors flow `agent_tools` → `tree_problems` → real-tree assertion, pinned by n13. No TODO and no unused name.
- BUG checks: fix and guardrail are both present. The guardrail would have caught the original errors. On the old parser with the new fixtures (my BASE mutant), the F-1 to F-5 fixtures fail: 13 failed, namely v1, v2 (F-1), v6 (F-2), v13, v15, v16 (F-3), v3, v11, v12 (F-4), v18, v19, v21 (F-5) and n13. RI-002 restore-a-default: the analogue of putting a removed default back is putting back the deny-list. My BASE and M56 (`_plain_colon` → False) each fail ≥ 1 test (13 and 6). Nothing in ccbot/ changes, so no 001 rule text applies. There is no data window and no simulator (items 062/068/073 n/a).
- **RI-012 / item 059 (FAIL):** three text classifiers in the new code have no negative test with the pattern inside other text. My mutants X2 and X3 change what the classifier matches inside text, and both leave all 132 tests green:
  - X2 `COMMENT_CUT_RE = r"#"` (cut at any `#`, not only ` #`): 132 passed. `name: a#b: c` gives VALUE(2) at head, and PyYAML also raises on it ("mapping values are not allowed here"). Under X2 it would pass. That is a fail-open regression in this item's own root-cause direction (RI-002) that no test catches.
  - X3 `if "|" in t or ">" in t:` (header found anywhere in the value): 132 passed. `description: a > b` and `description: a | b` pass at head and PyYAML loads both. No fixture pins this.
  - X4 `ITEMS_RE = r"(?:-[ \t]*)*"` (`-` with no space read as an item prefix): 132 passed. This is an observation only, because I found no frontmatter shape where this changes the verdict. I1 should decide whether a pin is worth adding.

## Tests re-run (output)
`check_handoff` (I3, worktree at fcf3cff, 2026-11-25):
```
$ python3 scripts/check_handoff.py 104
sources count (unique URLs in 01-research.md): 9
fact-check rows: 65
totals line: 65 rows -> 51 as-is, 9 fixed, 5 removed
PASS
exit 0
```
Full suite at head, `<scratch>/wt`, `python3 -m pytest -q -p no:cacheprovider` tail:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 985 passed, 1 skipped in 138.91s (0:02:18)
exit 1
```
Same as 05. The one failure is item 100's I3 FAIL r1 (cbcc301), not 104. `check_pipeline.py` in the same worktree prints `I3 FAIL: 100`, `INCOMPLETE: 100 (05 Scratch dir ... (item 097))` and `SKIPPED: none`, and 104 is `in progress (FULL: next 06)`.
Oldest Python: python3.11 is on PATH and python3.10 is not. `tests/test_safety.py tests/test_agent_tools.py` → `141 passed in 1.58s`, so `test_every_py_compiles_on_oldest_python` ran and did not skip.
Real tree: `grep -cE '^(name|description|tools):.*(:[ \t]|:$|[ \t]#)'` over the 7 agent files → 0 hits in each.

Mutants: my own forms in `<scratch>/tools/mut.py`, run on `<scratch>/mut`, `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` removed before each run. M56-M68 use the 05 forms. X1-X4 are mine.
```
BASE: 13 failed, 119 passed in 0.25s | failed: v11_block_header_text, v12_block_ends, v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented, v18_comment_key_then_item, v19_spec_two_comments, v1_value_colon, v21_tools_comment_then_item, v2_value_colon_end, v3_nested_value_colon, v6_continuation_colon, n13_value_colon
M56: 6 failed, 126 passed in 0.19s | failed: v12_block_ends, v1_value_colon, v2_value_colon_end, v3_nested_value_colon, v6_continuation_colon, n13_value_colon
M57: 1 failed, 131 passed in 0.14s | failed: v4_colon_in_comment
M58: 1 failed, 131 passed in 0.14s | failed: v6_continuation_colon
M59: 3 failed, 129 passed in 0.15s | failed: v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented
M60: 2 failed, 130 passed in 0.15s | failed: v14_key_1024, v17_key_1024_indented
M61: 4 failed, 128 passed in 0.16s | failed: v18_comment_key_then_item, v19_spec_two_comments, v20_comment_key_then_map, v21_tools_comment_then_item
M62: 3 failed, 129 passed in 0.17s | failed: v10_block_folded_indicators, v12_block_ends, v9_block_literal
M63: 1 failed, 131 passed in 0.15s | failed: v22_tools_entry_colon
M64: 1 failed, 131 passed in 0.15s | failed: p13_doc_hooks_example
M65: 1 failed, 131 passed in 0.14s | failed: v12_block_ends
M66: 1 failed, 131 passed in 0.15s | failed: v11_block_header_text
M67: 1 failed, 131 passed in 0.13s | failed: v10_block_folded_indicators
M68: 1 failed, 131 passed in 0.13s | failed: v17_key_1024_indented
X1_error_ignored: 9 failed, 123 passed in 0.27s | failed: v11_block_header_text, v12_block_ends, v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented, v1_value_colon, v2_value_colon_end, v3_nested_value_colon, n13_value_colon
X2_cut_any_hash: 132 passed in 0.11s | failed:
X3_block_anywhere: 132 passed in 0.12s | failed:
X4_items_any_dash: 132 passed in 0.11s | failed:
restored, git diff tests/ quiet: True
```
BASE and M56-M68 equal 03 step 5 / 04 / 05 exactly. I did not re-run M41-M55; 05's lists for them match 096/05.

PyYAML probe, re-run (information only, D6): `<scratch>/venv`, `venv/bin/python -I tools/probe.py <scratch>/wt`, PyYAML 6.0.4, libyaml True. For v1-v22 every test result and its SafeLoader/CSafeLoader load-or-raise agree with 05's table. That includes v21 (loads, the documented `_field` false error) and v22 (raises). Extra shapes:
```
| i3a_hash_in_word_colon `name: a#b: c` | colon in unquoted value on frontmatter line 2 (item 104; quote the value) | error: mapping values are not allowed here | error: mapping values are not allowed in this context |
| i3b_gt_inside_text `description: a > b` | no error | loads {'description': 'a > b', ...} | loads {'description': 'a > b', ...} |
| i3c_bar_inside_text `description: a | b` | no error | loads {'description': 'a | b', ...} | loads {'description': 'a | b', ...} |
| i3d_tab_hash_colon `description: a\t# see: b` | no error | error: found character '\t' that cannot start any token | loads {'description': 'a', ...} |
```
i3d (information): the pure-Python and libyaml loaders disagree, and the test passes the line. This is the same tab-before-`#` family that the 087/096 docstring already lists as not checked. It is not a finding.

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py | 121 ++++++++++++++++++++++++++++++++++++++++++++--)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-012
- RI-001 (ESCALATED): re-ran the feasibility counts. 0 real lines hit, the real-tree test passes, and the 1024 cap holds at the boundary in the test and in PyYAML (v13-v17).
- RI-010 (ESCALATED): my log line is written by `check_pipeline.py --log`, and the commit goes through `commit_step.py`.
- RI-014 (OPEN): n/a. No git or clone path is touched.
- RI-002: BASE and M56 fail tests. The X2 survivor is a fail-open gap in this item's own guardrail and is sent back.
- RI-004/005: every self-check kill list was re-run, not copied.
- RI-006: pytest lines pasted as printed.
- RI-007: Scope FULL, code only at I2.
- RI-008: the oldest-Python compile test ran on 3.11.
- RI-009: mutants only in my own worktree, no stash.
- RI-012: **FAIL**. There is no in-text negative for the comment cut (`#` inside a word) or for the block header (`|`/`>` inside a value) (X2, X3).

## Pipeline line (step 2)
check_pipeline line: `104: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))`

## Sent back / sent to Audit
FAIL round 1, sent back to I1 and I2. No 07.
1. (I1) Add in-text negative fixtures to the plan (RI-012, item 059), each one pinned by a named mutant:
   - (a) `_fm("name: a#b: c", TOOLS)` → VALUE(2). The mutant `COMMENT_CUT_RE = r"#"` must fail it.
   - (b) `_fm("description: a > b", TOOLS)` and `_fm("description: a | b", TOOLS)` → {Read, Write}. The mutant "header test anywhere in the value" must fail them.
   - I1 decides whether ITEMS_RE (`-` without a space, X4) needs a pin, or a docstring line saying it is not pinned.
2. (I2) Build those fixtures, re-run the suite, and run the new mutants plus M56-M68. Update the 05 counts: 132 + new fixtures; the BASE count changes only if a new fixture fails on the old parser. (a) gives no error on the old parser, so BASE would become 14 failed.
