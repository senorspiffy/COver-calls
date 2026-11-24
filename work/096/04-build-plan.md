# 04 Build plan - 096
Fit verdict: FIT WITH CHANGES

I1 read the branch copy of .claude/agents/i1-reviewer.md, logs/recurring-issues.md, work/096/request.md and 01-03, templates/build-plan.md, all of tests/test_agent_tools.py (487 lines, 92 tests) and the frontmatter of the 7 files under .claude/agents. I1 has no shell (item 072), so nothing was run. Every trace below was done by hand. I2 confirms each one by running it.

Fit check:
- Account and strategy: test-only change. It touches no ccbot/ code, no strategy rule and nothing the person follows (no 001 rule text to update). The ~$3k account is not affected.
- Existing code: the only file changed is tests/test_agent_tools.py. 092 (check_handoff) and 093 (waivers) are built first on this branch. Neither plans an edit to this file or to any agent frontmatter (Grep of work/092/04 and work/093/04 found no hit for test_agent_tools, `tools:` or a `---` line). 094, 095 and 097 are built after 096 and edit agent body text (e.g. work/097/04 L22-L25, work/094/04 L48). They do not edit frontmatter lines. The real-tree test runs again on each of their builds, so if a later item adds a column-0 non-key frontmatter line, it fails there.
- Real tree today: 7 files, 14 `---` lines, 21 frontmatter lines. Each is `name: `, `description: ` or `tools: ` at column 0, and each first character is a letter (I1 Grep 2026-11-24, same counts as 03 row 9). a1-auditor's `description: Audit & Efficiency team. ...` has the `&` inside the value, so KEY_RE stops at the first colon.
- Changes to 03 (why the verdict is WITH CHANGES): (1) Two fixtures are added, nk11 and nk12, with mutations M51 and M52 (see Extra research 3-4). (2) The comment test for the `prev_open` update is pinned as `line.strip().startswith("#")`, because 03 step 2's "does not start with `#`" does not say whether the line is stripped first. (3) Fixture ids get fixed names. The counts become 105 tests in total, and on the base parser 9 fail and 96 pass.

D4 (copied from 03): 087's q30 (`...x` / `---x`) was not valid YAML (PyYAML 6.0.3 ScannerError, work/087/06-verification.md L14); 087/04 L229 called it valid.

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN). Related GUARDED entries also checked: RI-002, RI-004, RI-005, RI-006, RI-007, RI-008, RI-012.
- RI-001: the allow-list is a filter rule. Its dated count is in 03 (21 of 21 real lines pass, 2026-11-24, re-grepped by I1). The real-tree test and every fixture below pin it. Nothing is asserted as "always".
- RI-002 (this item's pattern): a line the test cannot read becomes NO_KEY and never a tool set. The absent previous line starts closed (`prev_open = False`). 03 had no fixture for that start state, so I1 adds nk11 and M51.
- RI-004/005: every count in "Expected result" was re-derived from the rule's own regex and state (Self-check below).
- RI-006: I2 takes every count from pytest output as printed. No hand totals are written into 05.
- RI-007: Scope FULL. I1-I3 run, and no code is written before I2.
- RI-008: no walrus, no `re.prefixmatch`, no 3.11+ syntax. `bool(k and ...)` and `str.startswith(tuple)` both work on 3.10.
- RI-010: this file ends with the Log fields line only. No log line is typed.
- RI-012: KEY_RE is anchored with `.match`. Negative in-text cases: q30 (marker as a key prefix), nk10 (inner colon), nk5 (`%` first).
- RI-014: does not apply (no git and no clone-depth path is involved).

## Extra research (with sources)
1. The spec's plain-scalar first character, which backs D2's KEY_RE first-character class: "ns-plain-first(c) ::= (ns-char – c-indicator) | ((? | : | -) Followed by ns-plain-safe(c))", YAML 1.2 production [126], quoted in the rlsp-yaml-parser source (https://docs.rs/crate/rlsp-yaml-parser/latest/source/src/lexer/plain.rs). That confirms the `-(?=\S)` alternative. It also shows that `?x: y` and `:x: y` are valid keys under the spec. KEY_RE rejects them, but no new false error comes from 096: VALUE_START_RE already gives START for these lines (087's documented false error "plain values starting with `?` or `:`"), so they never reach the new check. M46 (q16, q17) pins that order. The docstring does not list them again.
2. Reserved indicators: PyYAML's own test data spec-05-10.error reads "ERROR: Reserved indicators can't start a plain scalar." (https://flutter.googlesource.com/third_party/pyyaml/+/refs/heads/main/tests/data/spec-05-10.error). This agrees with excluding `@` and the grave accent from KEY_RE's first character (03 row 47).
3. Edge case 03 missed (Missing-inputs row "Previous non-blank, non-comment line"): no fixture has a column-0 item as the first meaningful line. With `prev_open = True` as the start value, nk3, nk4 and nk8 still fail, because `name: x` / `  a: b` set P = False first. So the absent-case policy is not pinned. Added: nk11 `_fm("- a", TOOLS)` → NO_KEY(2), and mutation M51 (`prev_open = True` before the loop) → nk11 only. Trace: under M51 the item at i = 0 is allowed, and `_field` returns {Read, Write}. Every other fixture's first meaningful line either sets P itself (a key or a scalar line) or errors earlier (q16 `?`, q17 `:`, p15 `"`).
4. Edge case 03 left open (step 2 wording): an indented comment between an empty-valued key and a column-0 item. Spec-valid shape: comments are not content (03 row 21's spec example plus a comment line). If the comment test is `line.startswith("#")`, then `  # c` counts as meaningful, sets P = False, and the item is rejected. Pinned as positive nk12 `_fm("hooks:", "  # c", "- a", TOOLS)` → {Read, Write}, with mutation M52 (comment test on the unstripped line) → nk12 only. q23 has indented comments, but no column-0 item follows them, so it does not pin this.
5. PyYAML verdicts on nk4, nk5, nk8, nk11 and nk12 are not measured. As 03 Removed claim 3 says, I2/I3 may probe them in scratch as information only, and 05/06 must not call them YAML-invalid without that probe output.

## Files to create/change
1 file: tests/test_agent_tools.py (anchors are names, not line numbers).

a. Constants. Right after `DOC_MARKER_RE`:
```
KEY_RE = re.compile(r"""(?:[^\s"'#&!*\[\]{},|>%@`?:-]|-(?=\S))[^:]*:(?=[ \t]|$)""")
```
In the message-constant block, next to `DOC` / `TAB_BEFORE`:
```
NO_KEY = "no key on frontmatter line {} (item 096)"
```

b. `_frontmatter_error`: set the docstring to "... (items 080, 087, 096)." Add `prev_open = False` before the loop. At the end of the loop body, after the existing `if m:` block (so it is the last check in the line, D3), add:
```
        if line[:1] not in ("", " ", "\t", "#") and not line.startswith(FLOW_KEYS):
            if _is_item(line):
                if not prev_open:
                    return NO_KEY.format(n)
            elif not KEY_RE.match(line):
                return NO_KEY.format(n)
        t = line.strip()
        if t and not t.startswith("#"):
            k = KEY_RE.match(line)
            prev_open = line[0] != " " and (_is_item(line) or bool(k and not line[k.end():].strip()))
```
Do not reuse `s` or `c`, which the `if m:` block uses. No walrus. The `prev_open` update also runs on `tools:` / `disallowedTools:` lines, so nk6 works.

c. Module docstring: add an "Item 096:" paragraph after the Item 087 one, with the 03 step 3 content. A column-0 frontmatter line must be blank, a `#` comment, a `key:` (followed by a space, a tab or the end of the line; the key does not start with a YAML indicator, except `-` followed by a non-space), or a `- ` item directly after a column-0 empty-valued key or another column-0 item. Blank and comment lines (at any indent) are skipped. `tools:` and `disallowedTools:` lines are left to `_field`. Anything else is an error. The paragraph keeps "This says nothing about what Claude Code does with such a file." Known fail-closed false errors: a key with an inner colon not followed by a space (`a:b: c`). Also rejected (YAML's reading not checked): a column-0 item after an empty-valued key that carries a comment (`hooks: # c`); a column-0 item after the indented content of an earlier column-0 item; text split by `str.splitlines()` at \x0b, \x0c, \x1c, \x1d, \x1e, \x85, U+2028 or U+2029.

d. CASES: replace q30 in place with `"q30_marker_prefix_text": (_fm("name: x", "...x: y", "---x: z", TOOLS), {"Read", "Write"}, None)`. Add the following, with error cases written as `(text, None, NO_KEY.format(n))`:
| id | text | expected |
|---|---|---|
| nk1_plain_word | `_fm("name: x", "foo", TOOLS)` | NO_KEY(3) |
| nk2_plain_word_last | `_fm("name: x", TOOLS, "foo")` | NO_KEY(4) |
| nk3_item_after_scalar | `_fm("name: x", "- a", "tools: Read")` | NO_KEY(3) |
| nk4_map_item_after_scalar | `_fm("name: x", "- a: b", TOOLS)` | NO_KEY(3) |
| nk5_indicator_key | `_fm("name: x", "%x: y", TOOLS)` | NO_KEY(3) |
| nk6_tools_col0_list | `_fm("name: x", "tools:", "- Read", "- Write")` | {Read, Write} |
| nk7_item_after_empty_key | `_fm("description:", "- a", TOOLS)` | {Read, Write} |
| nk8_item_after_nested_map | `_fm("hooks:", "  a: b", "- c", TOOLS)` | NO_KEY(4) |
| nk9_tools_blank_then_item | `_fm("tools:", "", "- Read")` | "blank or comment line inside tools: list (item 075)" |
| nk10_inner_colon_key | `_fm("a:b: c", TOOLS)` | NO_KEY(2) |
| nk11_item_first_line (I1) | `_fm("- a", TOOLS)` | NO_KEY(2) |
| nk12_indented_comment_then_item (I1) | `_fm("hooks:", "  # c", "- a", TOOLS)` | {Read, Write} |

e. TREE: `"n12_no_key_line": ({"r1-researcher": f"---\nfoo\ntools: {SIX}\n---\n"}, None, [f"{R1}: {NO_KEY.format(2)}"], NO_SHELL - {"r1-researcher"})`.

## Tests and checks
1. `python3 -m pytest tests/test_agent_tools.py` gives 105 passed (79 + 12 = 91 parser cases, 11 + 1 = 12 tree cases, plus test_tree_problems_no_files and test_no_shell_agents_leave_commands_to_orchestrator).
2. Base-failure check: the head fixtures run against the base parser (the new check and `prev_open` removed, which is M42). Exactly these fail: nk1, nk2, nk3, nk4, nk5, nk8, nk10, nk11 and n12. That is 9 failed and 96 passed. nk12, nk6, nk7, nk9 and q30 pass on the base parser.
3. Mutations. I2 runs them one at a time on a scratch copy, and I3 re-runs them. Each one's failing ids must equal this list, or 05 states the difference as a Deviation and pastes the run output.
   - M41 (existing; DOC terminator dropped) → q30
   - M42 (new check removed) → nk1, nk2, nk3, nk4, nk5, nk8, nk10, nk11, n12
   - M43 (new check skips the last front line) → nk2
   - M44 (item always allowed) → nk3, nk4, nk8, nk11
   - M45 (KEY_RE lookahead `(?=[ \t])`) → p13, p14, q5, q6, q13, q15, q18, q23, nk6, nk7, nk8, nk9, nk12
   - M46 (new check moved before the DOC check) → p15, q16, q17, q27, q28
   - M47 (L45 first-character class) → nk5
   - M48 (P updated only on column-0 lines) → nk8
   - M49 (a blank or comment line sets P = False) → nk9, nk12
   - M50 (FLOW_KEYS exemption dropped) → s_no_space
   - M51 (`prev_open = True` at start) → nk11
   - M52 (comment test on the unstripped line) → nk12

   Changes from 03, traced by I1: M42 and M44 also kill nk11, because P starts False and the item is the first line. M45 also kills nk12: `hooks:` is not FLOW_KEYS and fails KEY_RE, so NO_KEY(2). M49 also kills nk12: `  # c` sets P = False, so NO_KEY(4). M43 does not kill nk11: under M43 the last line is TOOLS, which is exempt anyway, and `- a` is at i = 0, so nk11 still gives NO_KEY.
4. The real-tree test `test_no_shell_agents_leave_commands_to_orchestrator` passes: 21 of 21 lines.
5. `python3.11 -m py_compile tests/test_agent_tools.py`, where python3.11 is available (RI-008).
6. 05 carries the D4 sentence, the suite line as printed, and the real-tree result.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 KEY_RE and NO_KEY constants | Files a; Tests 1, M45, M47 |
| Step 2 new check last in line, FLOW_KEYS exempt, item/`prev_open` branch, any-column state, blank/comment non-reset | Files b (comment test pinned as stripped); Tests 1-3 (M42-M52) |
| Step 2 Feasibility: 21 of 21 real lines, 90 of 90 existing fixtures unchanged | Tests 4 (real-tree test) and Tests 1 (all existing ids pass; only q30 is rewritten) |
| Step 3 docstring paragraph and known false errors | Files c |
| Step 4 q30 rewrite, nk1-nk10, n12 | Files d, e; nk11 and nk12 added by I1 |
| Step 5 mutations M41-M50 | Tests 3 (lists updated for nk11/nk12 and M51/M52 added) |
| Step 6 D4 sentence in 04 and 05; 05 suite line and real-tree run | D4 at the top of this file; Tests 6 |
| D1 option (b) | Files b, nk6/nk7/nk8/nk9/nk12 |
| D2 KEY_RE | Files a, nk5/nk10/q30 |
| D3 order: last check in line | Files b, M46, M50 |
| D5 error text | Files a (NO_KEY) |
| Missing inputs: frontmatter absent / `tools:` absent | unchanged; existing a_no_frontmatter, b_no_tools_line |
| Missing inputs: no previous meaningful line | nk11 + M51 (I1 addition) |
| Missing inputs: line has no key shape | nk1, nk2, nk5, nk10, n12 |
| Missing inputs: PyYAML verdict, Claude Code reader | DROPPED: not measured, so not claimed (03 Removed claim 3, row 26). The docstring keeps the "says nothing" sentence |
| Follow-ups F-1 to F-5 | DROPPED: outside 096 scope; new items for A1 (053) |
| Rule text the person follows | none changed (test-only) |

## Guardrail tests
- Feasibility: column-0 allow-list (21 of 21 real lines pass, I1 Grep 2026-11-24) → test_no_shell_agents_leave_commands_to_orchestrator; selection pinned by nk1-nk12, q30 and n12 with mutations M42-M52
- Missing inputs: previous meaningful line absent → nk11_item_first_line (NO_KEY(2)), M51
- Missing inputs: key shape absent → nk1_plain_word, nk10_inner_colon_key, n12_no_key_line
- Missing inputs: frontmatter / tools line absent → a_no_frontmatter, b_no_tools_line (unchanged)

## Expected result
tests/test_agent_tools.py: 105 passed. On the base parser, 9 failed and 96 passed (nk1-nk5, nk8, nk10, nk11, n12). Each of M41-M52 fails exactly its listed ids. The real agent tree still passes. A column-0 `foo`, `- a` after a scalar, `- a: b`, `%x: y` or `a:b: c` now gives `no key on frontmatter line <n> (item 096)` instead of a tool set.

Self-check (I1 additions only; 03 Self-check 1-19 is unchanged otherwise). Total: 79 + 12 = 91, 11 + 1 = 12, 91 + 12 + 2 = 105. Base: 8 (03) + nk11 = 9 fail, 105 − 9 = 96 pass. nk11: `- a` at i = 0, n = 2. It is an item, P starts False → NO_KEY(2). nk12: `hooks:` gives P = True. `  # c` stripped starts with `#`, so P is kept. `- a` at i = 2 is an item with P → allowed. `_field` returns {Read, Write}.

Sources: https://docs.rs/crate/rlsp-yaml-parser/latest/source/src/lexer/plain.rs ; https://flutter.googlesource.com/third_party/pyyaml/+/refs/heads/main/tests/data/spec-05-10.error

Log fields: FIT WITH CHANGES | 1 files planned
