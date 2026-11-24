# 01 Research brief - 096

Type BUG, Scope FULL, opened by A1, 2026-11-22. Branch daily-fixes/2026-11-24, read only. R1 has no shell (tools: Read, Write, Glob, Grep, WebSearch, WebFetch). Every repo fact below comes from reading files and is cited as path:line. R1 ran no test, no PyYAML call and no regex. Every PyYAML result is quoted from work/087/06-verification.md or logs/audit/2026-11-22-087.md. Anything R1 traced by hand is labelled "R1 trace (not run)".

## Question
tests/test_agent_tools.py `_frontmatter_error` (L170-L198) checks how a line's value starts. It never checks that a column-0 line is a mapping key. A1 and I3 found that a column-0 `foo` (in the middle or as the last line) and a column-0 `- a` after a scalar-valued key still return a tool set, while PyYAML 6.0.3 rejects the whole frontmatter. Fixture q30 (`...x` / `---x`) is also YAML-invalid, although 04 calls it valid. What allow-list of column-0 line shapes makes each of these fail with a named error, keeps every existing fixture's text and the real tree green, and lets q30 be swapped for a YAML-valid fixture that still kills M41?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. `_frontmatter_error` runs four checks on each frontmatter line, in this order: DOC_MARKER_RE (L174), a tab in the leading whitespace (L176-L178), and then, through VALUE_START_RE, a tab before the value (L182-L183), a value start in `&!*?:` (L184-L185), quote checks (L186-L191) and flow checks, which skip `tools:`/`disallowedTools:` lines (L192-L197). It returns the first error found and otherwise returns None (L198). No check asks whether a column-0 line is `key:`, `#...` or blank.
F2. `VALUE_START_RE = [ ]*(?:-[ \t]+)*(?:[^\s"'#&!*\[{?:][^:]*:[ \t]+)?(\S)` (L45). Its key group is optional, so a line with no colon still matches, and group 1 is simply the first non-space character.
F3. In `_field`, a column-0 line that is not a `- ` item ends the block (L79-L80). A column-0 `- X` line counts as an item (`_is_item`, L51-L52).
F4. R1 trace (not run), `_fm("name: x", "foo", TOOLS)`. On `foo`: no DOC, no lead, the key group fails (no colon), c = `f` is not special, so no error. `_field("tools")` reads line 4 with nothing after it, giving {Read, Write}. This agrees with I3's base probe `({'Read', 'Write'}, None)` (work/087/06-verification.md L17) and with A1 on head (logs/audit/2026-11-22-087.md L82-L84).
F5. R1 trace (not run), `_fm("name: x", TOOLS, "foo")`. `_frontmatter_error` finds nothing. In `_field`, `foo` is at column 0 and is not an item, so the loop breaks (L79-L80), giving {Read, Write}. A1 reports PyYAML raises ScannerError on this shape (logs/audit/2026-11-22-087.md L83).
F6. R1 trace (not run), `_fm("name: x", "- a", "tools: Read")`. VALUE_START_RE: `-[ \t]+` takes `- `, the key group fails, and c = `a`, so no error. `_field` reads `tools: Read`, giving {Read}. A1 reports PyYAML raises ParserError (logs/audit/2026-11-22-087.md L83-L84).
F7. q30 is `_fm("name: x", "...x", "---x", TOOLS)` → {Read, Write} (tests/test_agent_tools.py L404). PyYAML 6.0.3 `safe_load` gives `ScannerError while scanning a simple key` (work/087/06-verification.md L14), so 04's "valid" wording (work/087/04-build-plan.md L236-L243) is wrong for q30. It is the only fixture that M41 (DOC terminator dropped) kills (work/087/06-verification.md L56).
F8. I3's replacement `_fm("name: x", "...x: y", "---x: z", TOOLS)` loads in PyYAML as `{'name': 'x', '...x': 'y', '---x': 'z', 'tools': 'Read, Write'}`. The head checker returns {Read, Write}, and under M41 `...x: y` matches DOC at column 0 (work/087/06-verification.md L17; A1 confirmed, logs/audit/2026-11-22-087.md L79-L80).
F9. Real tree: 7 agent files, each with `---` on L1 and L5 (Grep `^---$`: 14 hits) and 21 frontmatter lines, all of the form `name: `, `description: ` or `tools: ` at column 0 (Grep `^(name|description|tools): `: 3 per file, 21 total). An allow-list of blank / `#...` / `key:` at column 0 therefore has 0 false errors on today's tree.
F10. Test count on the branch: 79 parser cases (075's 33 + p1-p15 + q1-q31), 11 tree cases (n0-n5, n7-n11), 1 no-files test and 1 real-tree test = 92 (tests/test_agent_tools.py L272-L406, L433-L458; matches I3's "92 in the file", work/087/06-verification.md L10). 087's mutations go up to M41, so new ones can start at M42.
F11. Apart from 096 itself, no open item's 09x step file names test_agent_tools.py or the frontmatter parser as something it changes (Grep `test_agent_tools|frontmatter` over work/09*/*.md: 096/request.md and a mention in 090/06 L5 saying 090 changes no file of it).

### Existing fixtures a column-0 rule would also see
F12. These fixtures have a column-0 line that is not `key: `, but an earlier line already gives their expected error, and the loop returns the first error (L172-L198): p1, p2, p5, p6, p14, q1-q10, q12-q15, n8, n10, n11 (closing `end"`, `x"`, `y"`, `]`, `}` lines; L321-L375, L446-L457). If the new check keeps the first-error order, none of these changes. R1 trace (not run).
F13. These fixtures have the column-0 non-key shape on the same line as their expected error, so the order of checks inside one line decides their text:
- q16 `? description` (START `?`, L376)
- q17 `: "Research team,` (START `:`, L378)
- p15 `"tools": Read, Bash` (AFTER, L354)
- q27 `...` and q28 `--- # c` (DOC, L401-L402; DOC already runs first)
- s_no_space `tools:Read` (075 text "needs a space after the colon", from `_field`, L296)
If the new check runs after the existing per-line checks and leaves `tools:`/`disallowedTools:` lines to `_field` (as the flow rule already does, L192), all six keep their text. R1 trace (not run).
F14. z_space_before_colon `tools : Read, Bash` → NO_TOOLS (L320). A key rule shaped like VALUE_START_RE's key group (`[^\s"'#&!*\[{?:][^:]*:`) accepts `tools :` as a key, so z keeps its text. A rule that forbids a space before the colon would turn z into the new error. R1 trace (not run).
F15. Empty-valued column-0 keys (`tools:`, `hooks:`, `mcpServers:`, `description:`) appear in c, d, i2, p3, p4, p13, p14, q5, q6, q13-q15, q18, q23, y2-y4, y7 (L275-L379). VALUE_START_RE's key group needs `[ \t]+` after the colon (L45), so the new key test must also accept colon-at-end-of-line (`:(?:[ \t]|$)`, A1's draft, logs/audit/2026-11-22-087.md L99), or these become false errors. R1 trace (not run).
F16. y6 has a column-0 `# c` line and a blank line (L315). That is allowed by the request's allow-list.
F17. No existing fixture has a column-0 `- X` line. All block items are indented (d, i2, p4, q5, q6, q15, q18, q23, y2-y5, y7). R1 trace (not run).

### YAML: what may appear at column 0 in a top-level block mapping
F18. "Each node must be indented further than its parent node." "All sibling nodes must use the exact same indentation level." [https://spec.yaml.io/main/review/markdown.html] (YAML 1.2.2, revision 2021-10-01, same rendering as 087.) So a column-0 line in a top-level mapping is a sibling key. It cannot be a continuation of the previous value.
F19. "Implicit keys are restricted to a single line." [https://spec.yaml.io/main/review/markdown.html]
F20. The "-", "?" and ":" characters used for block collection entries "are perceived by people to be part of the indentation." [https://spec.yaml.io/main/review/markdown.html]
F21. The spec's "Mapping Scalars to Sequences" example puts a block sequence at the same column as its key: `american:` / `- Boston Red Sox` / `- Detroit Tigers` / `- New York Yankees` / `national:` / `- New York Mets` ... [https://spec.yaml.io/main/review/markdown.html]. So `tools:` / `- Read` (column 0) is valid YAML. A blanket "column-0 `-` is an error" rule would be a fail-closed false error on this valid form. The current `_field` reads it as {Read} (F3, R1 trace, not run). Whether PyYAML 6.0.3 loads it as `{'tools': ['Read']}`: UNVERIFIED (not run).
F22. By contrast, `name: x` / `- a` (F6) places a sequence entry where the previous key already has a scalar value, and A1 measured a ParserError there (logs/audit/2026-11-22-087.md L83-L84). The spec text that makes this an error (8.2.x block-mapping productions): UNVERIFIED. R1 could not read it: yaml.org/spec/1.2.2 and 1.2.1 cut off before chapter 7 and spec.yaml.io cut off at Alias Nodes (all three WebFetch attempts, offsets included).
F23. Document markers: YAML uses three dashes ("---") to separate directives from document content, and three dots ("...") end a document without starting a new one [https://spec.yaml.io/main/review/markdown.html]. The spec text on why `...x` / `---x` with no colon fail (plain-scalar first-character rules, c-forbidden): UNVERIFIED (same cut-off as F22). The empirical result is PyYAML's ScannerError (F7).
F24. The indicator characters are: `-` `?` `:` `,` `[` `]` `{` `}` `#` `&` `*` `!` `|` `>` `'` `"` `%` `@` and the grave accent [https://spec.yaml.io/main/review/markdown.html]. A column-0 `%` (directive) or `@`/backtick (reserved) is not a key either, so an allow-list catches them with no extra rule. A deny-list would not (the root cause the request names).

### What the runtime does with such a file
F25. "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." [https://code.claude.com/docs/en/sub-agents] So a project agent with a column-0 `foo` in its frontmatter would not load with the tools the test reports, assuming Claude Code's reader rejects it as PyYAML does. Which YAML reader Claude Code uses is UNVERIFIED (not named in the docs, same as 087 F29).
F26. `tools`: "a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents]
F27. The documented runtime check is: "run `claude plugin validate` against the directory, for example `.claude/agents`" [https://code.claude.com/docs/en/sub-agents]. As in 087 D8 (work/087/03-handoff.md L147), the test makes no runtime claim, so this check is not needed for 096.

## Numbers used (show the math)
- Current file: 33 + 15 + 31 = 79 parser cases; 79 + 11 tree + 1 + 1 = 92 tests (F10).
- Real frontmatter lines: 7 files x 3 lines = 21. All 21 are `key: ` at column 0. 0 would hit the new rule (F9).
- Existing fixtures touched by a column-0 rule: 22 with the shape after an earlier error (F12: p1, p2, p5, p6, p14 = 5; q1-q10 = 10; q12-q15 = 4; n8, n10, n11 = 3; total 22). 6 with the shape on their error line (F13). 1 key-with-space (F14). 20 empty-valued keys (F15). 0 column-0 `- ` lines (F17).
- Proposed fixtures (proposals, not results; n = front index + 2; error text wording is R3's call, A1's draft is `no key on frontmatter line <n>`):
  1. `name: x` / `foo` / TOOLS → no-key error, line 3
  2. `name: x` / TOOLS / `foo` → no-key error, line 4 (last line)
  3. `name: x` / `- a` / `tools: Read` → no-key error, line 3 (column-0 item after a scalar value)
  4. q30 swapped to `name: x` / `...x: y` / `---x: z` / TOOLS → {Read, Write} (F8; still kills M41)
  5. optional: `%YAML 1.2` or `@x` at column 0 → no-key error (F24, allow-list vs deny-list)
  6. decision fixture for `tools:` / `- Read` at column 0 (F21): either {Read} (allowed shape) or no-key error (fail closed, listed as a known false error)
  7. tree case: r1 with a column-0 `foo` → `.claude/agents/r1-researcher.md: <no-key error line n>`
- Projection if 1-4, 6 and 7 are adopted: 92 + 5 parser cases (q30 is replaced, not added) + 1 tree case = 98, or 99 with 5 (a projection, not a run).
- Proposed mutations (predictions, not runs):
  - M42: drop the new check → fails 1, 2, 3, 5, 7.
  - M43: new check skips the last front line → fails 2.
  - M44: new check treats any `-`-leading column-0 line as allowed → fails 3.
  - M45: key test accepts only `:` + space (not end of line) → fails every empty-valued-key fixture (F15).
  - M46: new check runs before the existing per-line checks → q16, q17 and p15 change text (F13).
  - M41 (existing): must still fail the swapped q30.

## Fit for a ~$3k account
This is a test/process item. It changes no strategy rule, trade, premium, dividend, tax or liquidity input, so the $3k limits do not apply. It makes the agent-tools drift test fail loudly on frontmatter that YAML cannot read at all. It does not claim what Claude Code grants (F25, F27). Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. Column-0 `- X` (F21, F22). Option (a): fail closed on every column-0 `-` line. It is simple, there are 0 real lines and 0 existing fixtures, but `tools:` / `- Read` (valid per the spec example) becomes a known false error and goes in the docstring list. Option (b): allow a column-0 item only right after a column-0 empty-valued key or another column-0 item. That keeps the valid form readable and still catches F6, but adds state. 087 chose fail closed throughout (work/087/03-handoff.md D4). R1 leans (a) for consistency; this is R2/R3's call.
2. Key definition. Reuse VALUE_START_RE's key group with `(?:[ \t]|$)` after the colon (F14, F15)? It must accept `...x:` and `---x:` (F8) and `tools :` (z). Should a quoted key (`"tools": ...`, p15) count as a key? If the new check runs after the quote checks, p15 keeps AFTER either way (F13).
3. Precedence. The new check should run last within each line and leave `tools:`/`disallowedTools:` lines to `_field`, so that q16, q17, p15, q27, q28 and s_no_space keep their texts (F13). M46 pins this order. Confirm.
4. Should 04's q30 wording correction ("valid") go in 096's 04/05 as a note, or should the fixture swap alone be enough? (request: "fix 04's 'valid' wording", logs/audit/2026-11-22-087.md L101-L102)
5. Docstring: add an "Item 096" paragraph (column-0 lines must be blank, `#...` or `key:`), keep "This says nothing about what Claude Code does", and list any known fail-closed false error from OQ1.
6. PyYAML confirmation of the swapped q30 exists (F8). PyYAML results for fixture 6 (`tools:` / `- Read` at column 0) and 5 (`%YAML`) have not been run: UNVERIFIED. I2 or I3 could probe them in a scratch dir if R3 wants a measured value for the docstring.
7. RI-002: near miss found by A1 before merge, not counted (request). No GUARDED condition changes.
