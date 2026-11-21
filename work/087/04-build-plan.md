# 04 Build plan - 087
Fit verdict: FIT WITH CHANGES

Fit check. 087 is a test and process item. It changes only tests/test_agent_tools.py and adds no strategy input, so the ~$3k account and the covered-call rules (001) are not touched. No rule text the person follows (001 slack, tolerance or cap) changes, so no rule-text update or new request is due. Nothing else in the repo uses QUOTE_START_RE, `_frontmatter_error` or this test file (I1 Grep outside work/: only the test file itself and old audit logs). Today's other items change scripts/check_pipeline.py, so the files do not overlap (RI-009/RI-011). The map in 03 holds up when I re-trace it by hand (see the checks below). I1 makes two changes:
- C1 (an edge R3 missed): YAML document markers inside the frontmatter. This adds 1 rule, 2 fixtures and 1 mutation (with a sub-case).
- C2: the docstring names block-scalar content lines as a known fail-closed false error under the new start rules.

I1 also gives the new fixtures fixed full names, so that `q1...` cannot be confused with the existing `q_capital_key`.

Recurring issues checked (item 013), against this file: RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN), RI-002 (GUARDED, near miss here), plus RI-004/005, RI-006, RI-008, RI-009/011 and RI-012. The details are at the end.

## Extra research (with sources)
1. **Document markers hide a later `tools:` line (new, C1).**
   - The PyYAML docs say: "Documents are separated with `---`." "Documents may optionally end with `...`." `load` "returns a Python object constructed from for the first document in the stream", and "If a string or a file contains several documents, you may load them all with the `yaml.load_all` function." (https://pyyaml.org/wiki/PyYAMLDocumentation, fetched 2026-11-21.)
   - So consider a frontmatter line `...` or `--- # c` followed by `tools: Read, Write`. A first-document reader drops the `tools:` line, which means the agent inherits every tool, Bash included (item 072). A strict single-document reader errors instead.
   - The test today reads `{Read, Write}`:
     - `agent_tools` ends the front only on a line whose `.strip() == "---"`, so `--- # c` and `...` stay inside it.
     - QUOTE_START_RE does not match those lines.
     - `_field` finds the column-0 `tools:` line.
   - That is the same RI-002 shape as the request: a line the test cannot read becomes a tool set. Whether PyYAML's `load` errors or returns the first document is UNVERIFIED by I1 (I1 has no shell). The plan does not depend on it, because the rule fails closed either way.
   - Cost: 0 real lines. I1 Grep `^(\.\.\.|---[ \t]|%|@|`)` in .claude/agents finds 0 matches on 2026-11-21 (every front line starts with a letter, as S1 in 03 says).
2. **Reserved and other indicator starts: considered, not adopted.** The perl.org YAML quoting guide lists the characters that cannot start a plain scalar (https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html):
   - `!` tag, `&` anchor, `*` alias
   - `- `, `: ` and `? ` (each followed by a space)
   - `{ } [ ]`, `,`, `#`, `| >`
   - "The `@` character and backtick: Reserved characters"

   03 already covers every one of these that can carry content across lines (`&!*?:[{`, quotes) or that `_field` already reads (`|`, `>`, `#`). `@`, backtick and `,` make a YAML reader error. They do not swallow a later line, and the sub-agents docs say an unparsed project agent is skipped (03 #30), so no tool set is granted. They are left out to keep the scope to the request. A1 may open a FAST item if wanted.
3. **R3 trace re-checked by I1 (by hand, no shell).** I confirmed these by hand:
   - S2: all 59 existing tests (48 parser + 9 tree + 2), with p4 `  -` giving c `-` and s `tools:Read` giving c `t`.
   - S3 for q5, q13-q17, q20-q26.
   - S5 for M27, M32, M33 and M36.
   - `_flow_end` never pops an empty stack: the first char pushes, and the function returns as soon as the stack is empty. `line[i - 1]` is always valid at a `#`, because index `start` is the bracket.
   - `tools: {Read, Write}` (exempt from D2) still errors in `_field` as `unparsed tools: entry '{Read' (item 075)`, so the exemption does not let a flow mapping through.

## Files to create/change
1 file: **tests/test_agent_tools.py** (change). No other file.

1. **Module constants.**
   - Replace L32 QUOTE_START_RE with `VALUE_START_RE = re.compile(r"""[ ]*(?:-[ \t]+)*(?:[^\s"'#&!*\[{?:][^:]*:[ \t]+)?(\S)""")` (03 step 1).
   - Add `DOC_MARKER_RE = re.compile(r"(?:---|\.\.\.)(?:[ \t]|$)")` (C1).
   - Add `FLOW_KEYS = ("tools:", "disallowedTools:")`.
   - Keep AFTER_CLOSE_RE and ENTRY_RE unchanged.
2. **New helper `_flow_end(line, start) -> int | None`.** Write it exactly as in 03 step 1:
   - a closer stack `want`
   - quotes skipped with `_quote_end`; an unclosed quote returns None
   - `#` after a space or tab returns None
   - `[` pushes `]` and `{` pushes `}`
   - on a mismatched closer, return None; when the stack empties, return `i + 1`
   - at end of line, return None

   Note: the return annotation is not needed (RI-008: `int | None` in an annotation evaluates on 3.10+, but leave it out to match the file's style).
3. **`_frontmatter_error(front)`.** Keep `n = i + 2`. Rules run per line in this order (03 D5, plus C1 as rule 0):
   0. `DOC_MARKER_RE.match(line)` → `DOC.format(n)` (C1).
   1. A tab in the leading whitespace → the 080 TAB text (unchanged).
   2. `m = VALUE_START_RE.match(line)`; if m: `s, c = m.start(1), m.group(1)`.
      1. `"\t" in line[:s]` → `TAB_BEFORE.format(n)`.
      2. `c in "&!*?:"` → `START.format(c, n)`.
      3. `c in "\"'"` → the 080 quote logic, unchanged, with `s` as the quote position (UNCLOSED / AFTER texts).
      4. `c in "[{"` and `not line.startswith(FLOW_KEYS)`: `end = _flow_end(line, s)`. If `end is None` → `FLOW_OPEN.format(n)`. Else if `not AFTER_CLOSE_RE.fullmatch(line[end:])` → `FLOW_AFTER.format(n)`.

   Error texts, as module constants next to UNCLOSED/TAB/AFTER:
   - `START = "value starts with '{}' on frontmatter line {} (item 087)"`
   - `FLOW_OPEN = "unclosed flow collection on frontmatter line {} (item 087)"`
   - `FLOW_AFTER = "text after closing bracket on frontmatter line {} (item 087)"`
   - `TAB_BEFORE = "tab before the value on frontmatter line {} (item 087)"`
   - `DOC = "document marker on frontmatter line {} (item 087)"`

   Change the docstring line to "(items 080, 087)". No change to `_field`, `agent_tools`, `tree_problems`, ENTRY_RE or NO_SHELL_ALLOWED. L49's `:\t` branch becomes unreachable and stays (080 D4).
4. **Module docstring: add an "Item 087" paragraph (D6 + C2).** It should say:
   - A frontmatter line is also an error when any of these hold:
     - its value starts with `&`, `!`, `*`, `?` or `:` (anchor, tag, alias, explicit key)
     - a tab comes before the value
     - a `[` or `{` value is not closed on its own line, or is followed by text other than spaces or ` #...`
     - the line is a YAML document marker (`...`, or `---` followed by a space or tab)
   - `tools:` and `disallowedTools:` lines are left to `_field`.
   - Known fail-closed false errors:
     - valid properties, aliases and explicit keys
     - plain values starting with `?` or `:`
     - a tab after `-` or `key:`
     - a quote or apostrophe inside a plain scalar inside a flow collection (`[it's]`)
     - valid multi-line flow collections
     - block-scalar content lines that start with one of these characters (C2)
   - Keep the sentence "This says nothing about what Claude Code does with such a file."
5. **Fixtures.** Change p11 and add q1-q28 and n10-n11. The full list is in Tests and checks.

## Tests and checks
"tools" = the line `tools: Read, Write`. Fixture names are fixed so that I2/I3 ids match. In every row, n = front index + 2.

**Changed:** `p11_tab_after_colon` → `(None, TAB_BEFORE.format(2))`.

**New parser CASES** (03 step 3; q1-q26 are the texts in 03, q27-q28 are new from C1):

| id | front lines | expected |
|---|---|---|
| q1_anchor_dq | `description: &d "Research team,` / tools / `end"` | START('&', 2) |
| q2_tag_dq | `description: !!str "Research team,` / tools / `end"` | START('!', 2) |
| q3_tag_sq | `description: !!str 'Research team,` / tools / `end'` | START('!', 2) |
| q4_anchor_tag_dq | `description: &a !!str "Research team,` / tools / `end"` | START('&', 2) |
| q5_item_anchor | `hooks:` / `  - &a "x,` / tools / `y"` | START('&', 3) |
| q6_item_open_quote | `hooks:` / `  - "x,` / tools / `y"` | UNCLOSED(3) |
| q7_open_seq | `description: [a,` / tools / `]` | FLOW_OPEN(2) |
| q8_open_map | `description: {a: b,` / tools / `}` | FLOW_OPEN(2) |
| q9_quoted_closer | `description: ["]",` / tools / `]` | FLOW_OPEN(2) |
| q10_comment_closer | `description: [a, # ]` / tools / `]` | FLOW_OPEN(2) |
| q11_wrong_closer | `description: [a}` / tools | FLOW_OPEN(2) |
| q12_text_after_flow | `description: [a] "x,` / tools / `y"` | FLOW_AFTER(2) |
| q13_flow_next_line | `description:` / `  [a,` / tools / `]` | FLOW_OPEN(3) |
| q14_anchor_alone | `description: &d` / `  "x,` / tools / `y"` | START('&', 2) |
| q15_item_open_map | `hooks:` / `  - {a: b,` / tools / `}` | FLOW_OPEN(3) |
| q16_explicit_key | `? description` / `: "Research team,` / tools / `end"` | START('?', 2) |
| q17_colon_start | `: "Research team,` / tools / `end"` | START(':', 2) |
| q18_dash_tab | `hooks:` / `  -\t"x,` / tools / `y"` | TAB_BEFORE(3) |
| q19_alias | `description: *d` / tools | START('*', 2) |
| q20_tag_on_tools | `tools: !!str Read` | START('!', 2) |
| q21_mid_value_amp | `description: Audit & Efficiency team` / tools | {Read, Write} |
| q22_quoted_amp | `description: "&x"` / tools | {Read, Write} |
| q23_doc_mcp_example | the 11 browser-tester lines in 03 step 3 | {Read} |
| q24_closed_flow_comment | `description: [a, "b]"] # c` / tools | {Read, Write} |
| q25_open_flow_last_line | tools / `description: [a,` | FLOW_OPEN(3) |
| q26_disallowed_open | `tools: Read, Bash` / `disallowedTools: [Bash,` | `unclosed [ in disallowedTools: (item 075)` |
| q27_doc_end_marker | `name: x` / `...` / tools | DOC(3) |
| q28_doc_start_marker | `name: x` / `--- # c` / tools | DOC(3) |

**New TREE cases** (03 step 3):

| id | r1 text | expected |
|---|---|---|
| n10_anchor_description | `---\ndescription: &d "Research team,\ntools: {SIX}\nend"\n---\n` | [`{R1}: ` + START('&', 2)], no_bash = NO_SHELL − {r1-researcher} |
| n11_open_flow | `---\ndescription: [a,\ntools: {SIX}\n]\n---\n` | [`{R1}: ` + FLOW_OPEN(2)], same no_bash |

**Counts:**
- Parser cases: 48 + 28 = 76.
- Tree cases: 9 + 2 = 11.
- Tests in the file: 76 + 11 + 1 (no-files) + 1 (real tree) = 89. That is 30 new tests plus 1 changed.

**Checks (I2 in 05, I3 in 06):**
1. `python3 -m pytest -q tests/test_agent_tools.py` → `89 passed`.
2. On the base (before 087), these fail: q1-q5, q7-q20, q25, q27, q28, n10, n11 and the changed p11 (25 parser + 2 tree + p11 = 28). The other 61 pass, because q6, q21-q24 and q26 already pass on the base.
3. `python3.11 -m py_compile tests/test_agent_tools.py` passes (RI-008).
4. Whole suite `python3 -m pytest -q`: totals copied from pytest's last line (RI-006). Expected delta +30 tests over the suite at the branch base.

**Probes**, on a scratch copy only (03 step 4), each run against the real r1-researcher.md:
- Each of A1's 4 description shapes at file L3 → START on line 3.
- `hooks:` / `  - &a "x,` after L4 → START('&') on its line.
- `description: [a,` / tools / `]` → FLOW_OPEN on line 3.
- New (C1): `...` inserted after L3 → DOC on line 4.

**Mutations** (each must fail at least the named tests; a mutation that leaves every test green is a finding):
- M25-M37 exactly as in 03 step 4.
- **M38** (C1): the doc-marker rule removed → q27 and q28 fail.
- **M38b**: the `|$` alternative dropped → q27 fails.
- Re-run 080's M14-M24 and A1-m1, m2, m4. M22 still fails p11, now by text (03 #72).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 VALUE_START_RE | Files 1 |
| Step 1 FLOW_KEYS | Files 1; pinned by M32 (j3, q26) |
| Step 1 `_flow_end` | Files 2; q7-q13, q15, q24, q25; M28-M30 |
| Step 2 D5 order and texts | Files 3 (rules 1-2.4); every new fixture |
| Step 2 "`_field`, tree_problems, ENTRY_RE, NO_SHELL_ALLOWED unchanged; L49 kept" | Files 3 last sentence |
| Step 3 p11 change | Tests: Changed |
| Step 3 q1-q26 | Tests: q1-q26 (names fixed by I1) |
| Step 3 n10, n11 | Tests: TREE |
| Step 4 probes and M25-M37, 080 re-runs | Tests: Probes, Mutations |
| Step 5 whole suite + 3.11 compile | Tests: Checks 3-4 (+30, not +28, because of C1) |
| D1 fail closed on `&!*` | Files 3 rule 2.2; q1-q5, q14, q19, q20, n10; M25, M26 |
| D2 flow closed on its line, FLOW_KEYS exempt | Files 3 rule 2.4; M31, M32, M36, M37 |
| D3 `?`/`:` starts and the key-start class | Files 1, 3 rule 2.2; q15-q17; M33, M34 |
| D4 tabs after an indicator; p11 flips | Files 1 (`-[ \t]+`), 3 rule 2.1; p11, q18; M27, M35 |
| D5 precedence, first error in file order, n = i + 2 | Files 3 (C1 adds rule 0, which is disjoint from rule 1 because a marker is at column 0) |
| D6 docstring | Files 4 (+ C2 block-scalar false error, + C1 marker) |
| Missing inputs table (all rows) | Guardrail tests: Missing inputs |
| Correction #10 (only 080 and 087 match) | Fit check: no overlap; I1 re-grepped outside work/ |
| Corrections #13, #18, #19, #27, #33, #58, #60, #77, #78 | DROPPED: source wording corrections with no code effect. D1 needs no alias/tag grammar, D4 makes no 1.2.2 validity claim, `.match` is kept, and no PyYAML or allow-list is used |
| Corrections #38-#45 (fixture texts under D1/D3) | Tests: q1-q6, q16; R1's fixtures 9 and 12 dropped as duplicates (in 03) |
| Correction #46 (count 87) | Superseded by C1: 89 (Tests: Counts) |
| Correction #47 (M25-M37) | Tests: Mutations |
| Correction #72 (M22 still pins p11) | Tests: Mutations, 080 re-run |
| Correction #79 (g, h, m, v, n1 unchanged; j3 only via exemption) | Tests: Checks 2 (those stay green on base and head); M32 |
| Mismatches fixed in Self-check (key class, closer stack) | Files 1, 2; q15/M33, q11/M30 |
| I1 C1 document markers | Files 1, 3 rule 0; q27, q28; M38, M38b; probe |
| I1 C2 block-scalar false error | Files 4 |

## Guardrail tests
- Feasibility: every new frontmatter rule (doc marker, tab before value, `&!*?:` start, open/after flow). Count from 03 step 2 (2026-11-21): 21 of 21 real lines pass. Re-checked by I1 on 2026-11-21:
  - Grep `^(---|[A-Za-z]+:)` in .claude/agents gives 7 files x L2-L4, each `key: <letter>`.
  - Grep for a tab: 0.
  - Grep `^(\.\.\.|---[ \t]|%|@|`)`: 0.

  The rules fire on 0 real lines and pass 21 of 21, which is the non-zero dated count. Pinned by `test_no_shell_agents_leave_commands_to_orchestrator` (real tree, incl. a1-auditor's mid-value `&` → M26). Each rule's firing side is pinned by its fixture: DOC q27/q28, TAB_BEFORE p11/q18, START q1-q5/q14/q16/q17/q19/q20, FLOW_OPEN q7-q11/q13/q15/q25, FLOW_AFTER q12.
- Missing inputs:
  - Frontmatter block absent or unclosed → `a_no_frontmatter` (unchanged).
  - `tools:` line absent → `b_no_tools_line`, `q_capital_key`, `z_space_before_colon` (NO_TOOLS).
  - Optional `description` absent → `n0_baseline` (BASE has only `tools:`).
  - Optional `disallowedTools` absent → q21, q22, q24 ({Read, Write}).
  - Optional `hooks`/`mcpServers` absent → every case without them; present → p13, q23.
  - Readable value start absent → q1-q20, q25, q27, q28 (named error, never a tool set).
  - Claude Code's reader / PyYAML → not used; no skip path (080 D7/D8).

## Expected result
- tests/test_agent_tools.py has 89 tests, all passing on the branch head.
- The 28 listed (25 parser + n10 + n11 + p11) fail on the base.
- Each A1 shape from the request, plus the document-marker shape, gives a named `(item 087)` error and never a tool set.
- Each of M25-M38b fails at least its named fixtures.
- No other file changes.
- The full suite grows by 30 tests.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): the new rules are counted on today's tree (21 of 21 pass, 0 firing, dated 2026-11-21), and each is pinned by a fixture. No "always" without a count.
- RI-010 (ESCALATED): I1 writes no log line. The Log fields line below is for the orchestrator's `--log`.
- RI-014 (OPEN): not touched. Only tests/ changes.
- RI-002 (GUARDED): C1 closes one more silent-tool-set path, and every unreadable shape is a named error.
- RI-004/005: every new fixture's expected text was traced through its rule (q27/q28: index 1 → line 3).
- RI-006: totals come from pytest output.
- RI-008: stdlib `re`, 3.10-safe syntax, 3.11 compile check.
- RI-009/011: no file overlap with today's check_pipeline.py items.
- RI-012: the START rule is anchored at the value start (q21, q22, M26), and DOC_MARKER_RE is anchored at column 0 by `.match`.

Log fields: FIT WITH CHANGES | 1 files planned
