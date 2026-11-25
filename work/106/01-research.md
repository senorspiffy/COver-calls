# 01 Research brief - 106

Type BUG, Scope FULL, opened by A1, 2026-11-25. Branch daily-fixes/2026-11-25, read only. R1 has no shell: it ran no test, regex, PyYAML call or git command. Repo facts are cited as path:line and come from reading files. Anything R1 worked out by hand is labelled "R1 trace (not run)". A PyYAML verdict is "measured" only when an earlier 05/06 pasted probe output for that exact shape. Every other verdict is a prediction for I2/I3 to probe, as information only (PyYAML is not a declared dependency, work/104/01-research.md L3).

Recurring issues read first (logs/recurring-issues.md): RI-002 is this item's root cause (an unreadable line must become a named error, never a tool set; near miss, not counted, L25). RI-001: each new rule gets a computed count on the real tree and the fixtures (Numbers). RI-012: the tab rule classifies by text, so it needs in-text negatives (a tab inside quotes, a tab inside a comment). RI-008: no 3.11+ syntax is proposed. RI-010: the orchestrator writes the log line. RI-003, 009, 011, 013, 014 do not apply (no calendar, git, branch, realtest or clone path).

## Question
104 (PR #38) left three shapes open (logs/audit/2026-11-25-104.md L59-L62; tests/test_agent_tools.py L63-L66 docstring):
- S-1: a tab before `#` in a plain value (`description: a\t# see: b`) passes, and the pure-Python and libyaml PyYAML loaders disagree on it.
- S-2 (104 D3): sibling indent levels are not checked.
- S-3: a continuation line under a closed `tools:` line gives VALUE (item 104), not `_field`'s message (item 075).

For each one: what rule gives a named error or a documented pass, keeps the 7 real agent files passing, and has a fixture that a named mutation kills?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. `COMMENT_CUT_RE = r"[ \t]#"` (tests/test_agent_tools.py L82). `_plain_colon` cuts the value at its first match (L214-L219), so `a\t# see: b` is cut to `a`, which has no colon. `_node` returns no error (L245-L247). R1 trace (not run). A1 measured the result: `description: a\t# see: b` → None (passes) (logs/audit/2026-11-25-104.md L60).
F2. Measured by I3 (work/104/06-verification.md L77): on `description: a\t# see: b`, PyYAML 6.0.4 SafeLoader raises "found character '\t' that cannot start any token", and CSafeLoader loads `{'description': 'a', ...}`.
F3. Tabs before `#` that are already refused: a tab in the leading whitespace (L259-L261, TAB, p3), a tab before the value (L265-L266, TAB_BEFORE, p11, q18), a tab or space before `#` inside a key (KEY_RE `[ \t](?!#)`, L79; nk16 → NO_KEY), and text after a closed quote other than spaces or ` #` (AFTER_CLOSE_RE `( +#.*)? *`, L86, AFTER). `#` after a space or tab inside a flow value makes `_flow_end` return None (L195-L196), which gives FLOW_OPEN. `tools:`/`disallowedTools:` values go to `_field`, where `Read\t# c` fails ENTRY_RE (L153-L158). R1 trace (not run).
F4. Paths that still accept a tab outside quotes: the plain value of a structure line (`_node` L239-L247), a continuation (L294-L296; both through `_plain_colon`, which also strips a trailing tab, L219), and the block header (`BLOCK_RE` allows `[ \t]+#` and a trailing `[ \t]*`, L80). R1 trace (not run).
F5. Indentation state is only `prev = (node column, open)` for the last structure line (L253, L294-L303). Nothing remembers older levels, so a dedent to a column that no ancestor used is not seen. R1 trace (not run).
F6. Measured (work/104/05-build-report.md L107, e2): `hooks:` / `    a: b` / `  c: d` passes the test with {Read, Write}. SafeLoader raises "expected <block end>, but found '<block mapping start>'" (line 3), and CSafeLoader raises "did not find expected key" (line 3). 05 L117 calls this a disagreement that is documented as not checked (104 D3).
F7. S-3 trace (R1, not run): for `tools: Read, Write` / `  Bash: x`, line 2 goes to `_node(line, n, False)` because it starts with FLOW_KEYS (L298). The value is not open, so `_node` returns closed with col 0 (L239-L240). Line 3 has ind 2 > 0 under a closed parent, so it is a continuation, and `_plain_colon("Bash: x")` gives VALUE(3) (L294-L296). Without that branch, `_field` would return `unparsed tools: line 'Bash: x' (item 075)`: the line starts with a space, so the loop does not break, and `value` is non-empty (L117-L120).
F8. `_field` rejects every non-blank, non-comment indented line after a non-empty `tools:` value (L119-L120), and every indented non-item line inside a `tools:` block list (L121-L122). So skipping the 104 continuation check inside a FLOW_KEYS block cannot turn such a line into a tool set. `_field` still reads it as an error. R1 trace (not run). Existing pins: y1 (`  , Bash`, L417), y4 (`    Bash`, L423), y5 (`  - Bash`, L425).
F9. The same continuation path applies under a `tools:` block item. `tools:` / `  - Read` / `      Bash: x`: `- Read` has col 4 and is closed, and 6 > 4, so the line is a continuation and gives VALUE(4), not `_field`'s `unparsed tools: line 'Bash: x'`. R1 trace (not run).
F10. A tools-path hole found while tracing S-2: `tools:` / `    - Read` / `  - Write`. Today `_frontmatter_error` passes it (`  - Write` is not indented past the closed `- Read` col 6, so `_node` runs with check off). Then `_field` appends both items and returns {Read, Write} (L112-L125). By F14 the two items are siblings at different levels. PyYAML's verdict on this exact shape: UNVERIFIED (I2 probe). R1 predicts a raise, the same way as e2. If PyYAML raises, this is a tool set returned for a file YAML cannot read (the RI-002 pattern), not only a message issue.
F11. A related shape that is still not checked, and that this item does not need to close: `tools:` / `  - Read` / `      - Bash` is a continuation (6 > 4). It has no colon, so it passes, and `_field` reads {Read, Bash}. YAML folds it into the plain scalar `Read - Bash`, by analogy with the measured e1 `name: x` / `  - a` → `{'name': 'x - a'}` (work/104/05-build-report.md L106). The docstring already lists "a continuation that starts with `- `" as not checked (L66). See OQ5.
F12. Real tree (R1 Grep, 2026-11-25, .claude/agents/*.md): 0 tab characters in any of the 7 files. `---` is on L1 and L5 of each file, and L2-L4 are the `name:`/`description:`/`tools:` lines (7 x 3 = 21 frontmatter lines). 0 frontmatter lines are indented (every `^[ \t]` hit is at L11 or later, in the body). 0 `name|description|tools` lines contain `#` or a second `: `.
F13. Fixtures that contain a tab: p3 (L437), p11 (L451), q18 (L491), nk16 (L534) and the tree fixture at L611. Each one errors in an existing check that runs before any new check proposed below (TAB, TAB_BEFORE, NO_KEY, TAB). R1 trace (not run).

### YAML: tabs and comments (S-1)
F14. YAML 1.2.2: "s-white ::= s-space | s-tab" (§5.5); "s-separate-in-line ::= s-white+ | <start-of-line>" (§6.2); "Comments must be separated from other tokens by white space characters." (§6.6); and about separation, "such white space may safely include tab characters" (§6.2) [https://yaml.org/spec/1.2.2/]. By the spec, `a\t# c` is the value `a` plus a comment. The current cut (F1) matches the spec, and libyaml agrees (F2).
F15. YAML 1.2.2 §6.1: "tab characters must not be used in indentation" [https://yaml.org/spec/1.2.2/].
F16. PyYAML's `scan_to_next_token` skips only spaces (`while self.peek() == ' ':`), with the comment "TODO: We need to make tab handling rules more sane", and raises "found character %r that cannot start any token". `scan_plain_spaces` consumes only spaces between chunks (`while self.peek(length) in ' ':`), and `scan_plain` ends a chunk at `'\0 \t\r\n\x85  '` [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py]. R1's reading (not run): in the pure loader, any tab after the first character of a plain value in block context (`a\t# c`, `a\tb`, a trailing `a\t`) is left over after the scalar and raises. This is measured only for `a\t# see: b` (F2). The rest is a prediction (I2 probe).
F17. PyYAML's `scan_block_scalar_ignored_line` (the text after `|`/`>` and its indicators) skips only spaces (`while self.peek() == ' ':`) and raises "expected a comment or a line break, but found %r" [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py]. R1's reading (not run): `description: |\t# c` raises in the pure loader, while BLOCK_RE accepts it (F4). Prediction, I2 probe.
F18. libyaml's `yaml_parser_scan_to_next_token` skips a tab when `(parser->flow_level || !parser->simple_key_allowed)`. Its comment reads "Tabs are allowed: in the flow context; in the block context, but not at the beginning of the line or after '-', '?', or ':' (complex value)." [https://raw.githubusercontent.com/yaml/libyaml/master/src/scanner.c]. This explains F2: after a plain value, libyaml skips the tab and reads `#` as a comment.
F19. Claude Code's docs do not name the YAML parser that reads subagent frontmatter. "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." `tools` is "a comma-separated string such as `Read, Grep, Bash` or a YAML list" [https://code.claude.com/docs/en/sub-agents] (re-read 2026-11-25; the first 100,000 of 113,622 characters were read). So R1 cannot tell which loader's verdict on S-1 matches the runtime. A disagreement between two common loaders is an "unreadable value" in RI-002's sense.

### YAML: sibling indentation (S-2)
F20. YAML 1.2.2 §6.1: "Each node must be indented further than its parent node." "All sibling nodes must use the exact same indentation level." Also, the "-", "?" and ":" indicators "are perceived by people to be part of the indentation", and this "is handled on a case-by-case basis by the relevant productions" [https://yaml.org/spec/1.2.2/].
F21. The rule for a block sequence nested at the same indent as its parent key (`a:` / `- x`): the §8.2 text was not in the fetched page (it stopped at §6.6). UNVERIFIED from the spec. At column 0 it is measured: v18/v19 load in PyYAML (work/104/05-build-report.md L101-L102), and the spec example "Single Document with Two Comments" has this shape (work/104/01-research.md F23). Indented (`  a:` / `  - x`): UNVERIFIED (I2 probe).
F22. Compact nested mapping `- item : Super Hoop` / `  quantity: 1`: a key inside an item has siblings at the key's column (work/104/01-research.md F18, spec.yaml.io; not re-read by R1 today). p13 (L454-L463) and q23 (L497-L508) rely on it.

## Numbers used (show the math)
- Current file: 136 tests in tests/test_agent_tools.py (A1: BASE "15 failed, 121 passed" = 136, logs/audit/2026-11-25-104.md L34). Full suite 990 passed, 1 skipped (L26). The last mutation is M68 (work/104/06-verification.md L158), so new ones start at M69.
- Real tree: 21 frontmatter lines, 0 tabs, 0 indented (F12). Every rule below selects 0 of 21 real lines. RI-001 feasibility: the rules cost nothing on the real tree and fail on the fixtures listed.

### Proposal S-1 (tab), rule B recommended, rule A fallback
- Rule B (broad, R1 recommendation): in a plain value (structure line after `_node` has passed the quote/flow branch), a continuation line, or a block header, the text before the first space+`#` may not contain a tab. Error: named text, R3's call (e.g. "tab in unquoted value on frontmatter line {} (item 106)"). Basis: the pure loader raises on each of these shapes (F16, F17; measured only for S-1 itself), libyaml and the spec accept them (F14, F18), and the runtime parser is unknown (F19), so the shape is unreadable and must fail closed (RI-002).
- Rule A (narrow, the request's wording): the same check, but only for `\t#`. `a\tb` and a trailing `a\t` keep passing. These are a documented disagreement, listed as "not checked".
- In both rules, BLOCK_RE's comment separator and trailing class go from `[ \t]` to space only, or the tab check runs on the header first.
- Placement: after the existing 080/087/096 per-line checks and the column-0 check, inside `_node` before `_plain_colon`, and in the continuation branch. Then the 5 tab fixtures (F13) keep their current errors. R1 trace (not run).
- Proposed fixtures (n = index + 2; expectations are proposals, not runs):
  - w1 `_fm("description: a\t# see: b", TOOLS)` → TAB-error(2) (the request's shape; SafeLoader raises, CSafeLoader loads, both measured, F2)
  - w2 `_fm("description: a\t# c", TOOLS)` → TAB-error(2)
  - w3 `_fm("description: a\tb", TOOLS)` → TAB-error(2) under B; {Read, Write} under A
  - w4 `_fm("description: x", "  more\t# c", TOOLS)` → TAB-error(3) (continuation)
  - w5 `_fm("hooks:", "  - a\t# c", TOOLS)` → TAB-error(3) (item value)
  - w6 `_fm("description: |\t# c", "  a", TOOLS)` → BLOCK(2) (or the tab error if the check runs first)
  - w7, an RI-012 negative: `_fm('description: "a\t# b"', TOOLS)` → {Read, Write} (a tab inside quotes)
  - w8, an RI-012 negative: `_fm("description: a # x\ty", TOOLS)` → {Read, Write} (a tab inside a ` #` comment)
- Mutations: M69 the tab check removed → w1-w5 fail (w3 only under B). M70 the check run on the whole value, before the space+`#` cut → w8 fails. M71 the check also applied to quoted values → w7 fails. M72 BLOCK_RE back to `[ \t]` → w6 fails.
- PyYAML predictions for I2 (pure / libyaml): w1 raise / load (measured); w2-w5 raise / load (F16, F18, not measured); w6 raise / load (F17, F18, not measured); w7, w8 load / load (not measured).

### Proposal S-2 (sibling indent)
- State: a stack `S` of indent levels. For each structure line (not a continuation, block content, blank or comment line; FLOW_KEYS lines included), its levels are its lead indent, the column of each further `- ` prefix, and its node column.
- Rule: `ind` = lead spaces. Pop while `S[-1] > ind`. If anything was popped and then (`S` is empty or `S[-1] != ind`), return INDENT (named text, R3's call, e.g. "indent matches no parent level on frontmatter line {} (item 106)"). Otherwise trim `S` to `ind` and push the line's levels. Run this after `_node` returns no error, so existing messages keep their order.
- Traces (R1, not run):
  - e2 (s1): `hooks:` [0] → `    a: b` child [0,4] → `  c: d` pops 4, S[-1]=0 ≠ 2 → INDENT(4). PyYAML raises (measured, F6).
  - p13: [0] → `  PreToolUse:` [0,2] → `    - matcher:` [0,2,4,6] → `      hooks:` ind 6 = top → `        - type:` [..,8,10] → `          command:` ind 10 = top → pass (unchanged).
  - q23: `mcpServers:` [0] → `  - playwright:` [0,2,4] → `      type:` [0,2,4,6] → `command`, `args` = 6 → `  - github` pops 6 and 4, top 2 = 2 → pass (unchanged).
  - d, y1-y7, p4, i2, v3, v9, v10, v16, v17, v20, nk8, nk12: no dedent to a new level. y1/y5 are continuations, nk8 gets its NO_KEY first. All unchanged.
- Fixtures:
  - s1 `_fm("hooks:", "    a: b", "  c: d", TOOLS)` → INDENT(4)
  - s2 `_fm("tools:", "    - Read", "  - Write")` → INDENT(4) (today {Read, Write}, F10)
  - s3 `_fm("hooks:", "  - a: b", "    c: d", "  - e: f", TOOLS)` → {Read, Write}
  - s4 `_fm("hooks:", "  - a: b", " c: d", TOOLS)` → INDENT(4)
  - s5 `_fm("  name: x", TOOLS)` → INDENT(3) (an indented first line, then column 0; today it passes)
  - s6 `_fm("hooks:", "  a:", "  - x", "  b: c", TOOLS)` → {Read, Write} (indented same-level sequence; PyYAML UNVERIFIED, F21)
- Mutations: M73 the INDENT check removed → s1, s2, s4, s5 fail. M74 only the node column is pushed (no item levels) → s3 and q23 fail. M75 the pop uses `>=` → d, p13, q23, s3 and s6 fail (every sibling becomes INDENT).
- PyYAML predictions: s1 raise (measured). s2, s4, s5 raise; s3, s6 load. All UNVERIFIED (I2 probe).

### Proposal S-3 (continuation under a closed `tools:`)
- Rule: keep a flag `in_flow`. It is set by a column-0 FLOW_KEYS line and cleared by the next column-0 line that is not FLOW_KEYS (blank and comment lines leave it alone). While `in_flow` is set, the continuation branch skips the 104 check, so `_field`'s item 075 message is returned (F7, F8). R1 recommends this over a new error text, because the request's evidence asks for "`_field`'s message" and `_field` already rejects every such line (F8).
- Fixtures:
  - c1 `_fm("tools: Read, Write", "  Bash: x")` → `unparsed tools: line 'Bash: x' (item 075)` (today VALUE(3))
  - c2 `_fm("tools:", "  - Read", "      Bash: x")` → `unparsed tools: line 'Bash: x' (item 075)` (today VALUE(4), F9)
  - c3 `_fm("tools: Read, Bash", "disallowedTools: Bash", "  Read: x")` → `unparsed disallowedTools: line 'Read: x' (item 075)` (R1 trace: `_field("tools")` breaks at the column-0 `disallowedTools:`, L117-L118)
  - c4, a negative: `_fm("tools: Read, Write", "name: x", "  foo: bar")` → VALUE(4) (the flag is cleared)
- Mutations: M76 the skip removed → c1-c3 fail (they get VALUE). M77 the flag never cleared → c4 fails (it returns {Read, Write}).
- Projection: 136 + 8 (w) + 6 (s) + 4 (c) = 154 tests in the file, with no existing expectation changed (F13 and the traces). This is a projection, not a run. BASE (the 104 parser with the new fixtures) is predicted to fail w1-w6 (w3 under B), s1, s2, s4, s5 and c1-c3 = 13 under B, 12 under A. That is R1 trace only; I2 runs it.
- Docstring: add an "Item 106:" paragraph. Under "Item 104", take "sibling indentation levels" out of "Not checked". Add the tab rule, plus rule A's documented passes if R3 chooses A. Keep "This says nothing about what Claude Code does with such a file."

## Fit for a ~$3k account
This is a test-only item. It changes no strategy rule, order, premium, dividend, tax or liquidity input, so the $3k limits do not apply. It makes the agent-tools drift test fail with a named error on three more frontmatter shapes that a common YAML loader rejects or reads differently. It makes no claim about what Claude Code grants (F19). Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. S-1: rule B (any tab in plain text before ` #`) or rule A (only `\t#`)? B also closes `a\tb` and a trailing tab, which the pure loader is predicted to reject (F16). Its cost on the real tree is 0 (F12). A follows the request's wording.
2. S-1: should a tab inside a key (`a\tb: c`, which KEY_RE accepts, L79) get the same rule? The pure loader is predicted to raise (F16, not measured). 0 real lines. If not, list it as "not checked".
3. S-2: should an indented sequence at the same level as an indented key with a scalar value (`  a: v` / `  - x`) be refused, the indented analogue of nk3? It passes today. The PyYAML verdict is UNVERIFIED. It is outside the request, so it could be listed as "not checked" instead.
4. S-2: s5 (an indented first line) is refused by the rule. Confirm with I2's probe that PyYAML raises. If it loads, s5 becomes a documented fail-closed false error.
5. F11 (`tools:` block item followed by a more-indented `- Bash` continuation, which `_field` reads as a tool) is not in this request. Should it become a separate item (it looks like RI-002) or be handled here in `_field`?
6. RI-002 near miss, not counted (request). No GUARDED condition changes. F10 (s2) should be named in 05 if I2's probe shows that PyYAML raises on it, because it is a tool set from YAML that will not load, not only a message difference.
