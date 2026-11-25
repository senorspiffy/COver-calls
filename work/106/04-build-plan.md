# 04 Build plan - 106
Fit verdict: FIT WITH CHANGES

The change is to the test only (tests/test_agent_tools.py). It touches no strategy rule, order path, cap or $3k limit, and no rule the person follows (001 is unchanged). It does not conflict with anything built: the 104 parser is extended in place, and every existing case keeps its result (03 Self-check 1). Other items today change scripts/check_pipeline.py and tests/test_pipeline_check.py. This item touches neither, so there is no file clash. The one change from 03 is a docstring addition (Extra research 1). It changes no code and no test count.

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED), RI-014 (OPEN), and the GUARDED entries RI-002 to RI-013.
- RI-001: every new rule is a reject filter. 03 gives dated counts for each: 0 of 21 real frontmatter lines (R3 Grep 2026-11-25) and a non-zero fixture selection (12 TAB_PLAIN, 4 INDENT, 4 `_field` 075 text, 1 `_field` 106 text). Both are pinned by tests (Guardrail tests). Nothing is asserted as "always".
- RI-002 (this item's root cause): every unreadable shape gives a named error, never a tool set. The one new shape I found (Extra research 1) returns an error on the tools path (`_field`), and outside the tools path it is documented as not checked. 05 names s2, tb1, tb3 and w1 as tool sets from YAML that will not load (03 step 7).
- RI-004/005: I re-traced w4, w6, w10, w13, tb2, s2, f1, q23, nk7 and nk6 by hand against the current `_frontmatter_error`, `_node` and `_field`. Each matches 03 Self-check.
- RI-006: I counted no totals by hand beyond adding up 03's fixture list (13 w + 3 tb + 7 s + 5 c + 1 f = 29). Pass/fail numbers come from I2's pytest output.
- RI-007: Scope FULL. I1 to I3 run, and this plan has no code in it.
- RI-008: no walrus and no `match`. I2 runs the python3.11 compile.
- RI-010: the log line is the last line below. The orchestrator writes it.
- RI-012: the tab rule classifies by text. 03 has in-text negatives (w7, w8, w11, w12) and edges (w9, w13), each killed by its own mutation. This plan keeps all of them.
- RI-003, RI-009, RI-011, RI-013, RI-014: not applicable. There is no calendar, git, branch, merge-base, clone or realtest path.

## Extra research (with sources)
1. An edge case R3 missed: a key after an indented `- ` item, at the item's own indent (`hooks:` / `  - x` / `  a: v`). With 03's stack: `[0]`, then `  - x` gives `[0,2,4]`, then `  a: v` pops 4 and lands on 2 = 2, so there is no INDENT and the file passes. In YAML the sequence at indent 2 is a real block sequence (not the indentless form), so a mapping key at its indent cannot continue it. PyYAML's own test suite keeps the top-level form of this shape as a loader error: `tests/data/no-block-collection-end.loader-error` is `- foo` / `- bar` / `baz: bar` ([PyYAML test data](https://flutter.googlesource.com/third_party/pyyaml.git/+/refs/heads/main/tests/data/no-block-collection-end.loader-error)). The common error text for it is "expected <block end>, but found '?'" ([CircleCI thread](https://discuss.circleci.com/t/expected-block-end-but-found/37328)). For the indented form inside our frontmatter, this is a prediction, not a measurement. I2 probes it as information only.
   - Tools path: it is safe already. `tools:` / `  - Read` / `  Bash: x` stops in `_field` with `unparsed tools: line 'Bash: x' (item 075)` (value empty, line not an item), both today and after this item (R3-style hand trace). So no tool set comes from this shape.
   - Change: catching it would need the stack to know which levels are sequences. That is outside the request and would need new state (the 104/02 AGAINST 2 risk). So it is not built. It is added to the "Item 106" docstring under "Not checked (YAML's reading not checked)", next to D3's `  a: v` / `  - x`. This is the "WITH CHANGES".
2. The YAML 1.2.2 rules 03 relies on (tabs are separation white space, §6.1 "tab characters must not be used in indentation", "All sibling nodes must use the exact same indentation level") were fact-checked in 03 (rows 17, 18, 25). I did not re-fetch them. The PyYAML test above is the only new source.
3. Simpler method considered: replacing the hand parser with PyYAML. Rejected: PyYAML is not a dependency (pyproject.toml, 03 row 1), the two loaders disagree on the very shapes in this item (03 rows 4, 46, 71), and Claude Code's reader is not named (03 row 24). 03's single line-level tab check is already the simplest form: one statement covers every path in 03 row 6.

## Files to create/change
1. `tests/test_agent_tools.py` (the only file).
   - Constants, next to `BLOCK = ...`: `TAB_PLAIN = "tab outside quotes and comments on frontmatter line {} (item 106)"` and `INDENT = "indent matches no open level on frontmatter line {} (item 106)"` (03 D1, D7).
   - New helper `_ends_field(line)`, placed after `_is_item`: `return line[:1] not in ("", " ", "\t") and not _is_item(line.strip())`.
   - `_field`: the loop's stop test (`if line[0] not in " \t" and not _is_item(s): break`) becomes `if _ends_field(line): break`. Set `first = None` before the loop. After the `if gap:` return and before `items.append(...)`, compute `lead = len(line) - len(line.lstrip(" "))`. If `first is None`, set `first = lead`. Otherwise, if `lead != first`, return `False, [], f"{key}: list items at different indents (item 106)"` (03 step 2).
   - `_frontmatter_error`: the docstring becomes "(items 080, 087, 096, 104, 106)". Before the loop, set `stack = []` and `in_flow = False`. On each line, before `m = VALUE_START_RE.match(line)`, set `keep = cut = 0`. In the quoted branch, after the AFTER_CLOSE_RE check, set `keep, cut = s, end`. In the flow branch, after the FLOW_AFTER check, set `keep = cut = end`. The first statement inside `if t and not t.startswith("#"):` is the tab check: `if "\t" in line[:keep] + line[cut:].split(" #", 1)[0]: return TAB_PLAIN.format(n)`. Then `if line.startswith(FLOW_KEYS): in_flow = True` / `elif _ends_field(line): in_flow = False`. In the continuation branch the test becomes `if not in_flow and _plain_colon(t):`. In the structure branch, after `if error: return error`, add the stack pop/INDENT/replace/extend exactly as in 03 step 3, then the existing `prev = (col, op)` and block lines. No walrus. Do not reuse `s`, `c` or `end` outside their branch.
   - CASES: add the 29 cases of 03 step 4, with their exact inputs and expectations. Use the ids w1 to w13, tb1 to tb3, s1 to s7, c1 to c5 and f1, each with a short suffix in the file's style (for example `w1_tab_before_hash_colon`, `s2_tools_list_dedent`, `f1_tools_item_indents`). The prefix is what 05 and the mutation lists cite. The new ids must not clash with `s_no_space`, `t1_unbalanced`, `t2_two_parens`, `c_empty_tools`, `w_miscased_disallowed` or `f_bash_specifier` (D8).
   - Module docstring: 03 step 6 word for word in substance. Remove "sibling indentation levels; " from the Item 104 "Not checked" list. Change "a continuation that starts with `- `" to "... outside `tools:`/`disallowedTools:`". Add the "Item 106:" paragraph with its known fail-closed false errors. In its "Not checked" sentence, also list (Extra research 1) "a key after an indented `- ` item at the item's indent (`  - x` / `  a: v`); on `tools:`/`disallowedTools:` `_field` refuses it". Keep "This says nothing about what Claude Code does with such a file."
2. `work/106/05-build-report.md` (I2's report, not code). It holds the PyYAML probe table for the 29 cases plus the Extra research 1 shape (`_fm("hooks:", "  - x", "  a: v", TOOLS)`) and its tools form (`_fm("tools:", "  - Read", "  Bash: x")`), as information only, with version and loader. CSafeLoader is "not measured" where it is absent. It applies D4 to s3, s5, s6 and s7, and names s2, tb1, tb3 and w1 as RI-002 tool-set paths.

## Tests and checks
I2 runs these in order. Each output goes into 05 as printed.
1. Base check: add only the constants and the 29 CASES to the current parser, on a scratch copy. Run `python3 -m pytest tests/test_agent_tools.py`. Expect exactly these 21 to fail: w1, w2, w3, w4, w5, w6, w9, w10, w13, tb1, tb2, tb3, s1, s2, s4, s5, c1, c2, c3, c5 and f1. The result is 21 failed, 144 passed. Any other list is a Deviation, with its output.
2. After the build: `python3 -m pytest tests/test_agent_tools.py` → 165 passed. `test_no_shell_agents_leave_commands_to_orchestrator` passes, so the 7 real files still read with 0 of 21 lines selected.
3. Full suite: `python3 -m pytest`. The base is 990 passed, 1 skipped plus whatever items built earlier today added. 05 states the base count it measured first, then base + 29.
4. `python3.11 -m py_compile tests/test_agent_tools.py` (RI-008), if python3.11 is present. Otherwise 05 says it is absent.
5. Mutations, one at a time, on a scratch copy (never in the repo). Each must fail exactly the ids in 03 step 5: M69 (12 ids), M70 w8, M71 w7, M72 w9, M73 s1/s2/s4/s5, M74 s7, M75 s1/s2/s4, M76 c1/c2/c3/c5, M77 c4, M78 c5/nk6/nk9/v21, M79 f1, M80 w11/w12, M81 w13. The 104 mutations M56 to M68 and X1 to X4 must still fail every id in their 104/06 lists. New ids in those lists are recorded and are not a Deviation.
6. Unchanged cases named in 05 with their results: p13, q23, d, y1 to y7, p4, i2, v3, v8, v9, v10, v16 to v21, v23 to v26, nk6, nk7, nk8, nk12.
7. PyYAML probe (scratch venv, information only), as in Files to create/change 2.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: TAB_PLAIN and INDENT constants | Files 1, constants |
| Step 2: `_ends_field`; `_field` stop uses it; `first` item-indent check | Files 1, `_ends_field` and `_field`; pinned by f1 (M79), c5/nk6/nk9/v21 (M78) |
| Step 3: tab check with keep/cut | Files 1, `_frontmatter_error`; pinned by M69, M70, M71, M72, M80, M81 |
| Step 3: `in_flow` set/cleared, continuation skip | Files 1, `_frontmatter_error`; pinned by M76, M77 |
| Step 3: stack pop / INDENT / replace / dash levels | Files 1, `_frontmatter_error`; pinned by M73, M74, M75 |
| Step 4: 29 CASES | Files 1, CASES; Tests 1, 2 |
| Step 5: mutations M69-M81, plus 104's M56-M68 and X1-X4 still kill | Tests 5 |
| Step 6: module docstring | Files 1, module docstring (plus the Extra research 1 line) |
| Step 7: PyYAML probe, D4, RI-002 naming in 05 | Files 2; Tests 7 |
| D1: rule B widened, text names item, docstring wording "the loaders disagree (measured on PyYAML 6.0.1 and 6.0.4)" | Files 1, constants and docstring |
| D2: tab in a key is covered by D1 | Files 1 (no separate rule); pinned by w10 |
| D3: `  a: v` / `  - x` not checked, documented | Files 1, docstring "Not checked" |
| D4: s5 refused; PyYAML differences go to 05/docstring, not a Deviation | Files 2; Tests 7 |
| D5: tools-path continuation handled in `_field` | Files 1, `_field`; pinned by f1 |
| D6: `in_flow` cleared by `_ends_field` | Files 1; pinned by c4 (M77), c5 (M78) |
| D7: error texts, `n = i + 2`, never PyYAML's mark | Files 1, constants and `_field` text |
| D8: ids tb1-tb3, no clash | Files 1, CASES ids |
| Removed claims 1-5: none appear as a YAML fact | Files 2 (PyYAML verdicts only next to a probe output); this plan states none as fact |
| Missing inputs table (8 rows) | Guardrail tests, Missing inputs |
| Prevention guardrail (steps 2-5) | Tests 2, 5 |
| Rules the person follows (001: slack, tolerance, cap) | None changed. The change is test-only, so no 001 text update and no request are needed |

## Guardrail tests
- Feasibility: tab rule → real tree 0 of 21 lines (R3 Grep 2026-11-25, `\t` 0 hits in .claude/agents), pinned by `test_no_shell_agents_leave_commands_to_orchestrator`. Fixture selection is 12 (w1-w6, w9, w10, w13, tb1-tb3), pinned by the base check (Tests 1) and M69.
- Feasibility: INDENT rule → real tree 0 of 21 (every line at column 0), same real-tree test. Fixture selection is 4 (s1, s2, s4, s5), pinned by the base check and M73. The 3 positives that must not be selected (s3, s6, s7) are pinned by M74 (s7) and by passing.
- Feasibility: `in_flow` continuation skip → real tree 0 of 21 (no continuation lines). Fixture selection is 4 (c1, c2, c3, c5), pinned by the base check and M76. The flag clear (c4) is pinned by M77.
- Feasibility: `_field` item-indent rule → real tree 0 of 7 files with a block list. Fixture selection is 1 (f1), pinned by the base check and M79. Equal-lead lists d, y2, y7 and nk6 stay unchanged (Tests 6).
- Missing inputs: `prev` absent (first line) → every case's first line. s5 shows a first indented line is pushed, not assumed column 0.
- Missing inputs: `stack` empty after a dedent → s5 gives INDENT(3). M75 shows s5 is the case that separates "empty" from "mismatch".
- Missing inputs: `keep`/`cut` absent (plain value) → w1, w2, w3 (whole line checked up to ` #`).
- Missing inputs: `in_flow` absent (no FLOW line yet) → v6_continuation_colon keeps VALUE(3).
- Missing inputs: `first` absent (no item yet) → c_empty_tools (no items, check never runs) and i2/p4 (one item).
- Missing inputs: PyYAML verdict, CSafeLoader, Claude Code's reader → not claimed. 05 shows the probe as information, and CSafeLoader is "not measured" where absent (Tests 7).

## Expected result
- `tests/test_agent_tools.py`: 165 passed. The base check gives exactly 21 failed and 144 passed, with the 21 ids listed in Tests 1.
- The real agent tree still passes with no problems, and NO_SHELL is unchanged.
- Each mutation M69 to M81 fails exactly its 03 step 5 ids. The 104 mutations still fail their lists.
- Full suite: the measured base plus 29, with 1 skipped.
- s2, tb1, tb3 and w1 (tool sets from YAML the pure loader rejects, measured) now fail closed with TAB_PLAIN or INDENT. The docstring lists the spec-valid tab shapes as known fail-closed false errors, and lists D3 and the Extra research 1 shape as not checked.

Log fields: FIT WITH CHANGES | 1 files planned
