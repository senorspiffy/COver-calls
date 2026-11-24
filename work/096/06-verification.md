# 06 Verification - 096
Verdict: PASS (round 2; earlier rounds: round 1 I3 PASS, A1 FAIL)
Sent back to: none

Base 1b10d90, head af4715b (branch daily-fixes/2026-11-24; 092 and 093 done on it). I3 scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-096-r1-7a05n3mv (mkdtemp, item 091). Head tree copied there with `git archive af4715b | tar -x`; mutations run only in that copy. An earlier I3 attempt was cut off by a container restart before writing anything; this is a fresh round 1.

D4 (copied from 03 via 04 and 05): 087's q30 (`...x` / `---x`) was not valid YAML (PyYAML 6.0.3 ScannerError, work/087/06-verification.md L14); 087/04 L229 called it valid. Checked: 087/06 L14 reads `q30 ERR ScannerError while scanning a simple key`.

## I1 audit (plan vs research)
- 04 follows 03's map step by step (04 Rule trace table): step 1 → Files a (KEY_RE text identical to 03 step 1 after un-escaping the table `\|`); step 2 → Files b; step 3 → Files c; step 4 → Files d/e; step 5 → Tests 3; step 6 → D4 line at the top of 04/05. D1-D5 are carried unchanged.
- Additions beyond 03, all sourced or traced: nk11 + M51 (03 Missing-inputs row "Previous non-blank, non-comment line" had no fixture for the start state; I1 Extra research 3), nk12 + M52 (03 step 2 left open whether the comment test is on the stripped line; I1 Extra research 4, spec comment rule), and the resulting count changes (103 → 105, base 8 → 9 failed, M42/M44/M45/M49 lists extended). Each is stated as a change from 03 with a trace. No unsourced addition.
- Dropped items (PyYAML verdicts, F-1..F-5) are dropped with reasons that match 03 Removed claim 3 and the 053 follow-up rule.
- Extra research sources: two URLs, used only to back the KEY_RE first-character class and the reserved-indicator exclusion; no new rule rests on them alone.

## I2 audit (build vs plan)
`git diff 1b10d90 af4715b --stat -- . ':!work' ':!logs'` → only `tests/test_agent_tools.py | 45 +++++++-` (1 file, as planned). Line by line against 04:
- a. `KEY_RE` added right after `DOC_MARKER_RE`, text equal to 04 Files a; `NO_KEY` added after `DOC` in the message block. Match.
- b. Docstring "(items 080, 087, 096)"; `prev_open = False` before the loop; new check placed after the `if m:` block as the last check of the loop body; `prev_open` update uses `t = line.strip()` / `t.startswith("#")`; `s`/`c` not reused; no walrus. Code is character-for-character the 04 Files b block. Match.
- c. Module docstring "Item 096:" paragraph after the Item 087 one; content equals 04 Files c, including "This says nothing about what Claude Code does with such a file." and the known false errors list. Match.
- d. q30 rewritten in place to `_fm("name: x", "...x: y", "---x: z", TOOLS)`; nk1-nk12 added with the exact texts and expected results of the 04 table. Match.
- e. TREE `n12_no_key_line` equals 04 Files e. Match.
- 05 "Deviations: None" is true: every count I re-ran equals 04.

Connectivity check (re-done): `KEY_RE` is read in the new check and the `prev_open` update; `NO_KEY` is returned by `_frontmatter_error` and asserted by nk1-nk5, nk8, nk10, nk11 and n12; `prev_open` is written each meaningful line and read by the item branch. `_frontmatter_error` is called by `agent_tools`, whose error goes to `tree_problems` and then to the real-tree assertion (n12 pins that path). Every branch ends in a defined result (allowed item, NO_KEY, FLOW_KEYS left to `_field`, skipped blank/comment/indented line). No TODO in the diff (`git diff 1b10d90 af4715b -- tests/ | grep -c TODO` → 0).

BUG checks (step 3):
- Fix and guardrail both in place: the allow-list check (fix) plus fixtures nk1-nk12/n12 and mutations M41-M52 (guardrail).
- Would the guardrail have caught the original error: yes. M42 is the base (pre-096) parser with the head fixtures: 9 fixtures fail, including nk1 (`foo`), nk2 (`foo` as last line) and nk3 (`- a` after a scalar), which are exactly the 087 N1 shapes that returned a tool set.
- RI-002 restore-a-default probe (scratch copy only): the removed "assume open" default is restored as M51 (`prev_open = True` before the loop) → nk11 fails (1 failed, 104 passed); restored → 105 passed.
- RI-001 feasibility: re-run. `test_no_shell_agents_leave_commands_to_orchestrator` passes on the real tree (in both runs below); 04/05 cite 21 of 21 real frontmatter lines across 7 files, and the passing real-tree test is that count's check. Rule text cites no other number.
- Text-match negative tests (item 059, RI-012): KEY_RE classifies a line by its text, anchored with `.match`. Negatives with the pattern inside other text exist and pass: q30 (`...x: y`, `---x: z`: doc markers as a key prefix, must not be read as DOC), nk10 (`a:b: c`: colon inside the key), nk5 (`%x: y`: key text after an indicator). Present, so no FAIL on this point.
- Data-edge check: before the first value → nk11 (item as the first meaningful line, NO_KEY(2)); after the last → nk2 (`foo` as the last front line, killed alone by M43); gaps → nk9 (blank inside a `tools:` list) and nk12 (indented comment between key and item, killed alone by M52).
- Grep reasons in 05: 05's missing-data grep is over `ccbot/`, which this item does not touch (`git diff --stat 1b10d90 af4715b -- ccbot/` is empty), so its 38 pre-existing hits are unchanged. Correct reason.
- Rule the person follows (001): none changed (test-only change); nothing to update.
- Simulator/replay of the bot rule (item 062): not applicable.
- PyYAML probe, information only (04 Extra research 5, 03 Removed claim 3), PyYAML 6.0.1 in my scratch dir, `yaml.safe_load` of each fixture's front lines: nk4 ParserError, nk5 ScannerError, nk8 ParserError, nk11 ParserError, nk12 OK `{'hooks': ['a'], 'tools': 'Read, Write'}`, new q30 OK `{'name': 'x', '...x': 'y', '---x': 'z', 'tools': 'Read, Write'}`. These agree with every fixture's expected result (errors where the test errors, positives load). Version differs from 087's 6.0.3; recorded as information, not as a claim in the test.

## Tests re-run (output)
`python3 -m pytest tests/test_agent_tools.py -q` in the head-tree copy:
```
.................................                                        [100%]
105 passed in 0.09s
```
Full suite, `python3 -m pytest -q -p no:cacheprovider` from the repo root (head af4715b, clean tree), last line as printed:
```
849 passed, 1 skipped in 119.96s (0:01:59)
```
Python 3.10/3.11 compile test (items 027, 032): `python3 -m pytest -q -rs tests/test_safety.py::test_every_py_compiles_on_oldest_python` → `1 passed in 0.19s` (not skipped; python3.11 is at /usr/bin/python3.11, python3.10 is not on PATH). Default python3 is 3.13.18.

Mutations, my own script ($SCRATCH/mut.py, written independently of I2's; one mutation at a time on the scratch copy, file restored after):
```
M41: 1 failed, 104 passed in 0.13s | test_agent_tools_parser[q30_marker_prefix_text]
M42: 9 failed, 96 passed in 0.18s | test_agent_tools_parser[nk10_inner_colon_key], test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk1_plain_word], test_agent_tools_parser[nk2_plain_word_last], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk5_indicator_key], test_agent_tools_parser[nk8_item_after_nested_map], test_tree_problems[n12_no_key_line]
M43: 1 failed, 104 passed in 0.11s | test_agent_tools_parser[nk2_plain_word_last]
M44: 4 failed, 101 passed in 0.16s | test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk8_item_after_nested_map]
M45: 13 failed, 92 passed in 0.27s | test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk6_tools_col0_list], test_agent_tools_parser[nk7_item_after_empty_key], test_agent_tools_parser[nk8_item_after_nested_map], test_agent_tools_parser[nk9_tools_blank_then_item], test_agent_tools_parser[p13_doc_hooks_example], test_agent_tools_parser[p14_nested_open_quote], test_agent_tools_parser[q13_flow_next_line], test_agent_tools_parser[q15_item_open_map], test_agent_tools_parser[q18_dash_tab], test_agent_tools_parser[q23_doc_mcp_example], test_agent_tools_parser[q5_item_anchor], test_agent_tools_parser[q6_item_open_quote]
M46: 5 failed, 100 passed in 0.14s | test_agent_tools_parser[p15_quoted_key], test_agent_tools_parser[q16_explicit_key], test_agent_tools_parser[q17_colon_start], test_agent_tools_parser[q27_doc_end_marker], test_agent_tools_parser[q28_doc_start_marker]
M47: 1 failed, 104 passed in 0.16s | test_agent_tools_parser[nk5_indicator_key]
M48: 1 failed, 104 passed in 0.11s | test_agent_tools_parser[nk8_item_after_nested_map]
M49: 2 failed, 103 passed in 0.11s | test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk9_tools_blank_then_item]
M50: 1 failed, 104 passed in 0.11s | test_agent_tools_parser[s_no_space]
M51: 1 failed, 104 passed in 0.11s | test_agent_tools_parser[nk11_item_first_line]
M52: 1 failed, 104 passed in 0.10s | test_agent_tools_parser[nk12_indented_comment_then_item]
restored: 105 passed in 0.10s
```
($SCRATCH = /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-096-r1-7a05n3mv.) Mutation forms: M42 removes the new check, the `prev_open` update and its init (base parser); M43 adds `i != len(front) - 1 and`; M44 `if not prev_open:` → `if False:`; M45 lookahead `(?=[ \t])`; M46 new check moved to right after `n = i + 2`; M47 first-character class → L45's `[^\s"'#&!*\[{?:]`; M48 update only when `line[0] != " "`; M49 blank/comment sets `prev_open = False`; M50 FLOW_KEYS exemption dropped; M51 `prev_open = True`; M52 `line.startswith("#")`. Every failing-id list equals 04 Tests 3 and 05.

check_handoff (03 exists), `python3 scripts/check_handoff.py 096`, exit 0:
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 64
totals line: 64 rows -> 49 as-is, 12 fixed, 3 removed
PASS
```

## Tests re-run (round 2)
Round 2 (after A1 FAIL round 1, logs/audit/2026-11-24-096.md). Base of round 2: c810804 (round 1 I3) / a34b7eb (I1 r2); head 73fcc6f (I2 r2) on daily-fixes/2026-11-24. I3 round 2 scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-096-r2-03hq1plt (new mkdtemp, item 091); every run below was in my own `git worktree add --detach` of 73fcc6f inside it ($R2/wt), never in the main checkout. No git stash. Rules read first: branch copies of .claude/agents/i3-verifier.md and .claude/commands/run-item.md, logs/recurring-issues.md.

I1 audit (round 2): 04 `## Round 2` takes A1's finding and A1's guardrail list unchanged (R2 rule trace: key body, nk13 = A1's `name: x` / `a #b: c`, nk14 = A1's `a #b:` / `- x`, nk15 = A1's RI-012 positive `a#b: c`, M53 = A1's "mutation back to `[^:]*`", docstring rule). Additions beyond A1: the tab half (nk16 + M54) and the over-strict guard M55, both sourced (YAML 1.2.2 s6.6 "Comments must be separated from other tokens by white space characters", s-white = space | tab; rlsp-yaml-parser plain.rs) and traced. A1's suggested regex was one of two forms ("e.g."); I1's `(?:[^: \t]|[ \t](?!#))*` is equivalent for the shapes A1 named and linear (disjoint single-character alternatives). No R1/R3 re-run needed: 03 makes no claim about a `#` in a key, so no 03 row is wrong (check_handoff below still PASS). No unsourced addition.

I2 audit (round 2): `git diff a34b7eb 73fcc6f -- tests/test_agent_tools.py` is the only code change of round 2 (73fcc6f: tests/test_agent_tools.py, work/096/05, its log line; 8a6cff2 between them is 094's and does not touch this file). Line by line against 04 R2 Files:
- a. KEY_RE body `[^:]*` → `(?:[^: \t]|[ \t](?!#))*`; the whole KEY_RE line is character-for-character 04 R2 Files a. First-character class and lookahead unchanged; VALUE_START_RE unchanged. Match.
- b. Docstring "Item 096:" paragraph: the `#`-after-space-or-tab clause added where 04 says, and "a key with a tab before `#` and no value (`a\t#b:`)" added to the "Also rejected (YAML's reading not checked)" list; "This says nothing about what Claude Code does with such a file." kept. Match.
- c. CASES nk13-nk16 after nk12 with the exact texts and expected results of the 04 R2 table. Match.
- 05 "Deviations (round 2): none" is true: every count I re-ran equals 04 R2 and 05.
Connectivity (re-done): the new KEY_RE is read at both existing call sites (column-0 check, `prev_open` update), so `a #b:` no longer opens a column-0 list (nk14, nk16 pin that path); nk13-nk16 are CASES entries run by `test_agent_tools_parser`; NO_KEY goes the round 1 path to `tree_problems` (n12 still pins it). No new function, branch or file; `git diff a34b7eb 73fcc6f -- tests/test_agent_tools.py | grep -c TODO` → 0. 05's missing-data grep reason holds: `git diff --stat a34b7eb 73fcc6f -- ccbot/` is empty.

BUG checks (round 2):
- Fix and guardrail both in place: the narrowed key body (fix), fixtures nk13/nk14/nk16 + nk15 and mutations M53/M54/M55 (guardrail).
- Would the guardrail have caught A1's error: yes. M53 is exactly the round 1 build's body (`[^:]*`): with the head fixtures it fails nk13, nk14, nk16 (3 failed, 106 passed), i.e. A1's two shapes and the tab shape that returned a tool set at c810804.
- RI-002 restore-a-default (scratch worktree only): M53 puts back the removed permissive body → 3 failed; M51 (`prev_open = True`) still fails nk11; restored → 109 passed.
- RI-012 text-match negative: KEY_RE classifies by text; nk15 (`a#b: c`, `#` inside the key, not a comment) is the in-text negative and passes; M55 (every `#` refused) fails it alone. Present, so no FAIL on this point.
- Data edges: the new rule is per line; before-first and after-last cases from round 1 (nk11, nk2) still pass and still die alone under M51/M43; nk13 puts the bad line in the middle (line 3), nk14/nk16 as the first front line.
- RI-001 feasibility: real-tree test passes (in both runs below); my awk over the frontmatter of .claude/agents/*.md for a column-0 line with ` #` → 0 (agrees with A1's dated 0 and 04's 21 of 21 letter-only keys).
- Rule the person follows (001): none changed (test-only). Simulator/replay (062): not applicable.

My own probe ($R2/probe.py, `python3 -I`, `agent_tools()` of the head file vs `yaml.safe_load`, PyYAML 6.0.1), including shapes outside the fixtures:
```
['name: x', 'a #b: c', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 3 (item 096)') | yaml ERR ScannerError
['a #b:', '- x', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ParserError
['a#b: c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'a#b': 'c', 'tools': 'Read, Write'}
['a\t#b:', '- x', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ScannerError
['a\t#b: c', 'tools: Read, Write'] -> (set(), 'tab before the value on frontmatter line 2 (item 087)') | yaml ERR ScannerError
['a  #b: c', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ParserError
['a #b:', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ParserError
['a b #c: d', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ParserError
['a :', '- x', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'a': ['x'], 'tools': 'Read, Write'}
['a : c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'a': 'c', 'tools': 'Read, Write'}
['a# b: c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'a# b': 'c', 'tools': 'Read, Write'}
['a b: c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'a b': 'c', 'tools': 'Read, Write'}
['a\tb: c', 'tools: Read, Write'] -> (set(), 'tab before the value on frontmatter line 2 (item 087)') | yaml ERR ScannerError
['#a: c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'tools': 'Read, Write'}
['a #', 'tools: Read, Write'] -> (set(), 'no key on frontmatter line 2 (item 096)') | yaml ERR ParserError
['name: x', 'a\xa0#b: c', 'tools: Read, Write'] -> ({'Write', 'Read'}, None) | yaml OK {'name': 'x', 'a\xa0#b': 'c', 'tools': 'Read, Write'}
PyYAML 6.0.1
```
Every shape that returns a tool set loads in PyYAML; every PyYAML error is an error here (no new false negative found; double space, `a b #c:`, NBSP before `#` and a space before the colon all behave as YAML does). Information only, one PyYAML version.

`python3 -m pytest -q -rs -p no:cacheprovider tests/test_safety.py::test_every_py_compiles_on_oldest_python tests/test_agent_tools.py` (worktree of 73fcc6f):
```
110 passed in 0.26s
```
(109 in test_agent_tools.py = 04 R2's 109, plus the compile test, not skipped: python3.11 is /usr/bin/python3.11 and its `py_compile` of the file exits 0; python3.10 is not on PATH.)

Full suite, `python3 -m pytest -q -p no:cacheprovider` in the worktree of 73fcc6f, last two lines as printed:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 870 passed, 1 skipped in 131.56s (0:02:11)
```
The one failure is expected: its assertion output names only `096: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))` / `A1 FAIL: 096` (this item, until A1 passes round 2); `I3 FAIL: none`, `INCOMPLETE: none`, `SKIPPED: none`, `UNTRACKED CHANGE: none`.

Mutations, my own script ($R2/mut.py: my round 1 script with M45/M47 re-anchored to the new KEY_RE text and M53-M55 added; one at a time on the worktree, file restored after):
```
M41: 1 failed, 108 passed in 0.11s | test_agent_tools_parser[q30_marker_prefix_text]
M42: 12 failed, 97 passed in 0.21s | test_agent_tools_parser[nk10_inner_colon_key], test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk13_space_hash_in_key], test_agent_tools_parser[nk14_space_hash_empty_key_then_item], test_agent_tools_parser[nk16_tab_hash_empty_key_then_item], test_agent_tools_parser[nk1_plain_word], test_agent_tools_parser[nk2_plain_word_last], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk5_indicator_key], test_agent_tools_parser[nk8_item_after_nested_map], test_tree_problems[n12_no_key_line]
M43: 1 failed, 108 passed in 0.12s | test_agent_tools_parser[nk2_plain_word_last]
M44: 4 failed, 105 passed in 0.14s | test_agent_tools_parser[nk11_item_first_line], test_agent_tools_parser[nk3_item_after_scalar], test_agent_tools_parser[nk4_map_item_after_scalar], test_agent_tools_parser[nk8_item_after_nested_map]
M45: 13 failed, 96 passed in 0.23s | test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk6_tools_col0_list], test_agent_tools_parser[nk7_item_after_empty_key], test_agent_tools_parser[nk8_item_after_nested_map], test_agent_tools_parser[nk9_tools_blank_then_item], test_agent_tools_parser[p13_doc_hooks_example], test_agent_tools_parser[p14_nested_open_quote], test_agent_tools_parser[q13_flow_next_line], test_agent_tools_parser[q15_item_open_map], test_agent_tools_parser[q18_dash_tab], test_agent_tools_parser[q23_doc_mcp_example], test_agent_tools_parser[q5_item_anchor], test_agent_tools_parser[q6_item_open_quote]
M46: 5 failed, 104 passed in 0.15s | test_agent_tools_parser[p15_quoted_key], test_agent_tools_parser[q16_explicit_key], test_agent_tools_parser[q17_colon_start], test_agent_tools_parser[q27_doc_end_marker], test_agent_tools_parser[q28_doc_start_marker]
M47: 1 failed, 108 passed in 0.11s | test_agent_tools_parser[nk5_indicator_key]
M48: 1 failed, 108 passed in 0.11s | test_agent_tools_parser[nk8_item_after_nested_map]
M49: 2 failed, 107 passed in 0.14s | test_agent_tools_parser[nk12_indented_comment_then_item], test_agent_tools_parser[nk9_tools_blank_then_item]
M50: 1 failed, 108 passed in 0.14s | test_agent_tools_parser[s_no_space]
M51: 1 failed, 108 passed in 0.12s | test_agent_tools_parser[nk11_item_first_line]
M52: 1 failed, 108 passed in 0.14s | test_agent_tools_parser[nk12_indented_comment_then_item]
M53: 3 failed, 106 passed in 0.13s | test_agent_tools_parser[nk13_space_hash_in_key], test_agent_tools_parser[nk14_space_hash_empty_key_then_item], test_agent_tools_parser[nk16_tab_hash_empty_key_then_item]
M54: 1 failed, 108 passed in 0.15s | test_agent_tools_parser[nk16_tab_hash_empty_key_then_item]
M55: 1 failed, 108 passed in 0.11s | test_agent_tools_parser[nk15_hash_inside_key]
restored: 109 passed in 0.10s
```
($R2 = /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-096-r2-03hq1plt.) New forms: M53 body → `[^:]*` (round 1 build); M54 body → `(?:[^: ]|[ ](?!#))*` (tab dropped); M55 body → `[^:#]*`. Every failing-id list and count equals 04 R2 Tests 2-4 and 05 round 2.

check_handoff (03 exists), `python3 scripts/check_handoff.py 096` in the worktree, exit 0:
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 64
totals line: 64 rows -> 49 as-is, 12 fixed, 3 removed
PASS
```
Real-data effect (round 2): not required (tests/test_agent_tools.py | 13 ++++++++---); no file in TRIGGER or TRIGGER_DIRS changed in round 2 either, so no head run.

Verdict (round 2): PASS. A1's defect is fixed with the guardrail A1 asked for, and the guardrail fails on the round 1 code.

## Real-data effect (diff_reports output, pasted)
not required (tests/test_agent_tools.py | 45 +++++++++++++++++++++++++++++++++++++++++++--). No file in TRIGGER or TRIGGER_DIRS (scripts/check_pipeline.py L458-L461) changed, so no head run is needed for this item.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014 (open or ESCALATED); also RI-002, RI-012 (GUARDED, this item's pattern). RI-001: the allow-list's real-tree count is measured by the passing real-tree test, not assumed; fixtures pin each branch. RI-010: every log line for this step is written with `check_pipeline.py --log` right after this file and committed with `commit_step.py`; my 06 has its own re-run outputs, not copies. RI-014: not applicable, no git or clone-depth path touched. RI-002: unreadable column-0 line now gives NO_KEY, never a tool set; restore-a-default probe M51 fails nk11; near miss "column-0 line with no key passes the frontmatter test → 096" is closed by this item (status for A1 to copy on main: GUARDED, unchanged, near miss not counted). RI-012: in-text negatives q30, nk5, nk10 present and passing. Round 2 (same entries re-checked, RI-001, RI-010, RI-014 open or ESCALATED; RI-002, RI-012 GUARDED): RI-001: real-tree count re-measured (passing real-tree test; my awk, 0 column-0 lines with ` #`). RI-010: round 2 log line written with `--log I3 096` right after this file, committed with `commit_step.py`; all round 2 outputs above are my own runs. RI-014: not applicable. RI-002: A1's near miss (column-0 key with ` #` gives a tool set) is closed: nk13, nk14, nk16 give NO_KEY and M53 (round 1 body) fails them; status for A1 to copy on main: GUARDED, unchanged, near miss not counted. RI-012: nk15 is the in-text negative, M55 fails it alone.

## Pipeline line (step 2)
check_pipeline line: `096: awaiting A1 (FULL)` (run after this file and the I3 `--log` line were written; exit 0)
Round 2: check_pipeline line: `096: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))` (run 2026-11-24 after this file and the round 2 I3 `--log` line `19:24 | I3 | 096 | PASS | sent to audit: yes` were written; exit 1 only for `A1 FAIL: 096`, which stays until A1's round 2 result line; I3 FAIL, INCOMPLETE, SKIPPED, UNTRACKED CHANGE, LOG TIME and LOG BATCH do not name 096).

## Sent back / sent to Audit
Sent to Audit: yes. Audit task in work/096/07-audit-task.md.
Round 2: sent to Audit: yes; round 2 task under `## Audit task (round 2)` in work/096/07-audit-task.md.
