# 04 Build plan - 080
Fit verdict: FIT WITH CHANGES

Fit check: this is process tooling only. It does not touch the bot, quotes, the ~$3k account rules or 001, so no rule text the person follows changes (no 001 slack, tolerance or cap is involved). One file changes: tests/test_agent_tools.py (075's drift test, on PR #33 under this branch). Nothing else imports it. Grep `test_agent_tools|\.claude/agents|conftest` in work/081-089/*.md: hits only in 082/01 and 086/01, and those cite .claude/agents/i2-builder.md, i3-verifier.md and a1-auditor.md body lines as sources. Neither changes an agent file's frontmatter, so the real-tree test is not affected, and there is no file clash with the check_pipeline.py items. Stdlib `re` only (03 D7). 03's map is adopted as written, step by step. The changes are small:
1. Add one parser fixture, **p15_quoted_key** (`"tools": Read, Bash` → text-after-close error). Reason: under D1 a quoted key, which A1 probed in 075 (01 F10, "fails closed"), changes from `no tools: line ...` to the new 080 text. 03 does not list that change, so the plan pins it in the open. It also gives M15, M18 and M21 a second target.
2. Pin M18's exact replacement text, so I2 and I3 run the same mutation.
3. Add a docstring sentence naming the two known fail-closed false errors that the extra research found (research 2). No code change for them.
4. State the suite delta as "I2's base run + 17" instead of an absolute total. Other items run in parallel on this branch, so the base total moves.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): the one filter is the new per-line rule. Its count is dated: 21 of 21 frontmatter lines pass (7 files x L2-L4, 03 S1, branch daily-fixes/2026-11-20, 2026-11-20). I1 re-read r1-researcher.md L1-L5 the same day and the result matches: unquoted values, no leading whitespace. That count is pinned by `test_no_shell_agents_leave_commands_to_orchestrator`. "Existing CASES unchanged" is a count too, 40 of 40 (03 S2), pinned by the 33 + 7 parametrized cases. The plan has no "always" or "every" without a count.
- RI-002 (GUARDED; 080 is a near miss): this is the fix. Each unreadable line is a named error and never a tool set. The Missing inputs rows each have an absent-case fixture (Guardrail tests).
- RI-010 (ESCALATED): I1 has no shell, so the orchestrator writes this step's log line with `--log` right after this file. No agent-text duty is added.
- RI-012: the quote rule is anchored at a value-start position (QUOTE_START_RE with `.match`), not a substring search. M23 pins it.
- RI-014 (OPEN): not touched (no check_pipeline.py change).
- RI-008: no syntax newer than 3.10. I3 runs `python3.11 -m py_compile`.
- RI-006: I2 and I3 copy counts from pytest's last line.
- RI-004/RI-005: every fixture, p15 included, is traced through its rule below and in 03 S3-S6.
- RI-009/RI-011: no file overlap (Grep above).
- Not applicable: RI-003 (no calendar), RI-007 (FULL scope; I1-I3 run; no `.claude/` or `templates/` edit), RI-013 (no realtest change).

## Extra research (with sources)
1. **03's p13 fixture is the docs' example verbatim.** I re-fetched https://code.claude.com/docs/en/sub-agents (2026-11-20). The db-reader frontmatter reads `name: db-reader` / `description: Execute read-only database queries` / `tools: Bash` / `hooks:` / `  PreToolUse:` / `    - matcher: "Bash"` / `      hooks:` / `        - type: command` / `          command: "./scripts/validate-readonly-query.sh"`, which is exactly 03's p13, indents included. The same page says: "Claude Code ignores a field it doesn't recognize without reporting an error". That is consistent with 075's `q_capital_key` and `w_miscased_disallowed` (a miscased key is not read).
2. **Tabs inside block-scalar content are valid YAML, so rule (a) can give a false error.** PyYAML's spec test data `spec-05-12.error` says: "Tabs may appear inside comments and quoted or block scalar content." and "Tabs must not appear elsewhere, such as in indentation and separation spaces." (https://flutter.googlesource.com/third_party/pyyaml/+/961ce9dcf53dcef41f6268bbbb7c6a685a46c899/tests/data/spec-05-12.error, WebFetch summary, tab positions not visible). Rule (a) looks at leading whitespace only, so a `description: |` block whose content line starts `  <TAB>text` would be flagged, although YAML reads the tab as content. So would a line holding only whitespace with a tab in it. Both fail closed, and today 0 lines have either (03 #5: 0 leading-tab hits). Decision: keep rule (a) as 03 states it, and name both cases in the docstring so a future false alarm is expected, not a surprise. Fixing them would need block-scalar state, which is a fourth YAML reading (02 AGAINST 2).
3. **Tab after the colon (p11) is valid in YAML 1.2.2 but may not be in PyYAML.** The same PyYAML data file lists tabs in "separation spaces" as an error. That test data dates from the YAML 1.1 era. YAML 1.2.2 §6.2 allows tabs as separation (03 #11). Whether PyYAML 6 or Claude Code's reader accepts `tools:\tRead` is UNVERIFIED (no run). If one of them rejects it, the result is a skipped agent file, not extra tools (03 #20). That is not the Bash-grant failure this item guards, so D4 stands and p11 stays positive. This is recorded for the D5 follow-up (an A1 PyYAML probe), together with the open `[`/`{` case.
4. **A runtime check exists but is not used here.** The docs say: "To find files in an `agents` directory whose frontmatter doesn't parse, run `claude plugin validate` against the directory, for example `.claude/agents`" (same fetch). It needs the Claude Code CLI, which is not a test dependency, and it only says whether the frontmatter parses, not what `tools` resolves to. Using it in tests would bring back the skip-path problem A1 rejected for PyYAML (03 D7). Suggested to A1 as an optional manual probe on a1-n1 and a1-n2, not part of 080.
5. **The quoted key shape (p15).** `"tools": Read, Bash` is the shape A1 probed in 075 (logs/audit/2026-11-19-075.md, 01 F10). I traced it through 03's rules. There is no leading whitespace. QUOTE_START_RE cannot take a key (the first key character excludes `"`), so group 1 matches the `"` at column 0. The scanner closes on the `"` after `tools`, and the rest `: Read, Bash` fails `( +#.*)? *`, so the result is `text after closing quote on frontmatter line 2 (item 080)`. On the base (no 080) the result is `no tools: line (inherits every tool incl. Bash, item 072)`. Both are errors, but the text changes, so a fixture pins it.

## Files to create/change
1. **tests/test_agent_tools.py** (the only file):
   - Module docstring: add an "Item 080" paragraph. A frontmatter line the test cannot read on its own is an error, because the test cannot tell which tools that file grants. The three cases are a tab in the leading whitespace, a quoted value (at line start, after `- `, or after `key: `) not closed on its line, and text after the closing quote other than spaces or ` #...`. The paragraph makes no claim about what Claude Code does with such a file (D8). Known fail-closed false errors: a tab at the start of block-scalar content and a whitespace-only line containing a tab (research 2).
   - New module constant `QUOTE_START_RE = re.compile(r"""[ ]*(?:-[ ]+)*(?:[^\s"'#][^:]*:[ \t]+)?(["'])""")` and `AFTER_CLOSE_RE = re.compile(r"( +#.*)? *")`.
   - New function `_quote_end(line, start)`: returns the index just past the closing quote, or None if the line ends first. `q = line[start]`. For `"`: walk from `start + 1`; a `\` skips the next character (a `\` as the last character reaches the end, so the value is open); the first other `"` closes. For `'`: `''` is a literal (skip 2); a lone `'` closes.
   - New function `_frontmatter_error(front)`: for `i, line in enumerate(front)`, with `n = i + 2`: (a) `lead = line[:len(line) - len(line.lstrip(" \t"))]`; if `"\t" in lead` → `f"tab in indentation on frontmatter line {n} (item 080)"`. (b) `m = QUOTE_START_RE.match(line)`; if m: `end = _quote_end(line, m.start(1))`; None → `f"unclosed quoted value on frontmatter line {n} (item 080)"`. (c) Else if not `AFTER_CLOSE_RE.fullmatch(line[end:])` → `f"text after closing quote on frontmatter line {n} (item 080)"`. The function returns the first error in line order (tab rule before quote rule within a line, D1), or None.
   - `agent_tools`: right after `front = lines[1:end]` (L109), add `error = _frontmatter_error(front)` / `if error: return set(), error`. Nothing else changes: `_field`, `tree_problems`, ENTRY_RE, the allow-list and L54's `" \t"` stay as they are (03 step 2, D4, D5).
   - CASES: add p1-p15 (03 step 3 plus p15 below). TREE: add n8, n9 (03 step 3).

## Tests and checks
New parser CASES (text built with `_fm(...)` unless noted; expected tools, expected error):
| Case | Front lines | Expected |
|---|---|---|
| p1_dq_multiline | `description: "Research team,` / `tools: Read, Write` / `end"` | unclosed quoted value on frontmatter line 2 (item 080) |
| p2_sq_multiline | same with `'` | unclosed ..., line 2 |
| p3_tab_block_list | `tools:` / `\t- Read` / `\t- Write` | tab in indentation on frontmatter line 3 (item 080) |
| p4_bare_dash | `tools:` / `  -` | unparsed tools: entry '' (item 075) |
| p5_dq_escaped_end | `description: "abc\"` (source `'description: "abc\\"'`) / `tools: Read` / `x"` | unclosed ..., line 2 |
| p6_sq_doubled_end | `description: 'it''` / `tools: Read` / `x'` | unclosed ..., line 2 |
| p7_open_quote_last_line | `tools: Read, Write` / `description: "abc` | unclosed ..., line 3 |
| p8_text_after_close | `description: "a" "b` / `tools: Read, Write` | text after closing quote on frontmatter line 2 (item 080) |
| p9_closed_quoted_colon | `description: "a: b"` / `tools: Read, Write` | {Read, Write} |
| p10_closed_sq_comment | `description: 'it''s' # c` / `tools: Read, Write` | {Read, Write} |
| p11_tab_after_colon | `tools:\tRead, Write` | {Read, Write} |
| p12_plain_inner_quote | `description: Use "this` / `tools: Read, Write` | {Read, Write} |
| p13_doc_hooks_example | the 9 docs lines (research 1) | {Bash} |
| p14_nested_open_quote | `hooks:` / `  - matcher: "Bash` / `tools: Read` / `x"` | unclosed ..., line 3 |
| p15_quoted_key (I1 addition) | `"tools": Read, Bash` | text after closing quote on frontmatter line 2 (item 080) |

New TREE cases: n8_quoted_description and n9_tab_list exactly as in 03 step 3. Each expects a single problem `.claude/agents/r1-researcher.md: <080 text>` and no_bash = NO_SHELL − {"r1-researcher"}.

Probes and mutations (I2 in 05, I3 in 06, on a scratch copy only, never in the repo). All of 03 step 4 applies (a1-n1 double- and single-quoted → `unclosed quoted value on frontmatter line 3 (item 080)` in the real-tree test; a1-n2 → `tab in indentation on frontmatter line 5 (item 080)`; the base run fails p1-p3, p5-p8, p14, p15, n8, n9). The named targets are 03's, plus p15 where marked:
- M14 `_is_item` without `s == "-"` → p4.
- M15 the `_frontmatter_error` call removed → p1, p2, p3, p5, p6, p7, p8, p14, p15, n8, n9.
- M16 rule (a) removed → p3, n9.
- M17 end of line without a close treated as closed → p1, p2, p5, p6, p7, p14, n8.
- M18 replace the `_quote_end` call and rule (c) with exactly `v = line[m.start(1):]` and `if not (len(v) > 1 and v.rstrip().endswith(v[0])): return unclosed-text` → p5, p6, p8, p10, p15.
- M19 `''` handling removed → p6, p10.
- M20 `\` skip removed → p5.
- M21 rule (c) removed → p8, p15.
- M22 rule (a) applied to the whole line → p11.
- M23 `QUOTE_START_RE.match` replaced by a search for the first `"` or `'` anywhere in the line → p12.
- M24 rule (b) only on column-0 `key: ` lines → p14.
A mutation that leaves every test green is a finding.

Checks: `python3 -m pytest -q tests/test_agent_tools.py` → 59 passed (33 + 15 = 48 parser, 7 + 2 = 9 tree, + no-files + real-tree). `python3 -m pytest -q` on the branch → I2's base total + 17, same skips. `python3.11 -m py_compile tests/test_agent_tools.py` → no output.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 (a) tab in leading whitespace → error, file line n = index + 2 | Files 1, `_frontmatter_error` (a); p3, n9, a1-n2 probe; M16, M22 |
| Step 1 (b) value-start quote via QUOTE_START_RE, escape-aware scan, open at end of line → error | Files 1, QUOTE_START_RE, `_quote_end`, (b); p1, p2, p5, p6, p7, p14, n8, a1-n1 probe; M17, M18, M19, M20, M23, M24 |
| Step 1 (c) after the close only `( +#.*)? *` | Files 1, AFTER_CLOSE_RE, (c); p8, p10, p15; M21 |
| Step 1 call placement: after L109, before `_field` | Files 1, `agent_tools`; M15 |
| Step 1 docstring "item 080" | Files 1, docstring (plus the research 2 sentence) |
| Step 2 no other code change (L54 left, D4) | Files 1 ("Nothing else changes") |
| Step 3 fixtures p1-p14, n8, n9 | Tests and checks tables (all 16 kept; p15 added) |
| Step 4 probes and mutations M14-M24 | Tests and checks, mutation list (M18 text pinned; p15 targets added) |
| Step 5 whole suite + 3.11 compile | Tests and checks, Checks line |
| D1 precedence: first line wins; tab before quote within a line | `_frontmatter_error` order; p15 pins the precedence over `_field` |
| D2 scanner, not `endswith` | `_quote_end`; M18 |
| D3 after close: spaces or spaces + `#`; trailing tab rejected | AFTER_CLOSE_RE (`" +"`, not `[ \t]+`); p8, p10 |
| D4 tab rule on leading whitespace only; `tools:\t` stays valid | (a) uses `lead`; p11; M22 |
| D5 open `[`/`{` on other keys | DROPPED: outside the request and no probe run (03 D5). The follow-up for the orchestrator, A1 probing with PyYAML, is extended by research 3 (`tools:\t`) |
| D6 `<n>` = file line, 1-based | `n = i + 2`; the line numbers in p1-p15, n8, n9, probes |
| D7 no PyYAML | No import, no skip path; research 4 rejects `claude plugin validate` for the same reason |
| D8 no runtime claim | Docstring wording (Files 1) |
| Missing inputs table (03) | Guardrail tests, Missing inputs lines |
| Correction sections in 03 | None exist in 03 (no `§ Correction` heading). The Self-check mismatches (M18 targets, `"abc \`) are already folded into step 4 |

## Guardrail tests
- Feasibility: per-line frontmatter rule (a)-(c) → `test_no_shell_agents_leave_commands_to_orchestrator` pins 21 of 21 real lines passing (7 files x L2-L4, 2026-11-20, 03 S1; non-zero). The 33 + 7 existing parametrized cases pin 40 of 40 unchanged (03 S2). p9, p10, p11, p12 and p13 pin that the valid shapes still pass (5 positives, non-zero).
- Missing inputs: frontmatter block absent or unclosed → `a_no_frontmatter` (unchanged, still `no frontmatter`).
- Missing inputs: a frontmatter line not readable on its own → p1, p2, p3, p5, p6, p7, p8, p14, p15, n8, n9 (named 080 error, never a tool set).
- Missing inputs: `tools:` key absent → `b_no_tools_line` (unchanged, 072 text).
- Missing inputs: a block list item with no name (bare `-`) → p4 (`unparsed tools: entry '' (item 075)`, pinned against M14).
- Missing inputs: Claude Code's own reading → no test possible. No claim is made (D8), and the docstring says so.
- Missing inputs: PyYAML → not used, so there is no skip path to test (D7).
- Missing inputs: ccbot/screen.TESTS, ccbot/missing.MISSING_POLICY → N/A (no ticker or data input in this item).

## Expected result
- tests/test_agent_tools.py: 59 passed (was 42). That is 17 new tests: 15 parser (p1-p15) and 2 tree (n8, n9). On the base code, p1, p2, p3, p5, p6, p7, p8, p14, p15, n8 and n9 fail. p4, p9-p13 pass on the base too: p4 already gives the 075 text, and the positives are unchanged.
- Whole suite: I2's base total + 17 passed, skips unchanged. `py_compile` on 3.11 is clean.
- A1's probes now fail loudly: a1-n1 gives `unclosed quoted value on frontmatter line 3 (item 080)`, and a1-n2 gives `tab in indentation on frontmatter line 5 (item 080)`. Each of M14-M24 fails at least its named cases ("Done looks like" in request.md).
- The real agent files and every existing case give the same result as before. No file other than tests/test_agent_tools.py changes.
- I1 log fields (the orchestrator writes them with `--log`): `FIT WITH CHANGES | 1 files planned`.
