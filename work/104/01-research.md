# 01 Research brief - 104

Type BUG, Scope FULL, opened by A1, 2026-11-24. Branch daily-fixes/2026-11-24-b (built on PR #37), read only. R1 has no shell (tools: Read, Write, Glob, Grep, WebSearch, WebFetch). R1 ran no test, regex, PyYAML call or git command. Repo facts are cited as path:line and come from reading files. Anything R1 worked out by hand is labelled "R1 trace (not run)". Every PyYAML verdict on a new shape is a prediction for I2/I3 to probe in scratch, as information only (PyYAML is not a declared dependency: pyproject.toml L10 `dependencies = ["numpy", "pandas"]`).

Recurring issues read first (logs/recurring-issues.md): RI-002 is this item's root cause (a line the test cannot read must become a named error, never a tool set; near miss, not counted). RI-001: every new rule below gets a computed pass count on the real tree and the fixtures (Numbers). RI-012: the new checks classify by text, so each one needs an in-text negative fixture (a positive that contains the pattern in an allowed place). RI-008: no 3.11+ syntax is proposed. RI-010: the orchestrator writes the log line. RI-003, 009, 011, 013, 014 do not apply (no calendar, git, branch or realtest path).

## Question
096 (PR #37) made column-0 frontmatter lines an allow-list in `_frontmatter_error` (tests/test_agent_tools.py L187-L226), but left five residuals (work/096/03-handoff.md L112-L117, docstring L44-L50):
- F-1: a second `: ` in a value (`name: x: y`) passes.
- F-2: an indented `  foo: bar` under a scalar-valued key passes.
- F-3: a column-0 key longer than 1024 characters passes.
- F-4: there is no allow-list for indented lines, which would close F-1 and F-2 for nested lines too.
- F-5: `hooks: # c` followed by a column-0 `- item` is a documented false error.

What allow-list for indented lines and plain value text, and what key-length cap, make F-1 to F-3 named errors and make F-5 pass, while keeping the real tree and all 109 existing tests green? Each new check also needs a fixture that a named mutation kills.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. `KEY_RE` (L63) accepts a column-0 key and stops at the first `:` followed by a space, a tab or the end of the line. It never looks at the value text after that colon, so `name: x: y` matches as the key `name`, and nothing later checks `x: y`. R1 trace (not run). This agrees with 096/03 row 57 (work/096/03-handoff.md L76).
F2. In `_frontmatter_error`, the column-0 check runs only when `line[:1] not in ("", " ", "\t", "#")` (L216). An indented line reaches only the earlier per-line checks: DOC (L192), the lead tab (L195), and through `VALUE_START_RE` the tab before the value, START, quote and flow checks (L197-L215). So `  foo: bar` under `name: x` passes. R1 trace (not run), same as 096/03 row 57.
F3. `prev_open` (L225) is True only if the column-0 line is an item, or a KEY_RE key with `line[k.end():].strip()` empty. For `hooks: # c` the rest is `# c`, which is not empty, so `prev_open` is False and the next column-0 `- a` gives NO_KEY (L217-L219). The docstring lists this as rejected (L47-L48).
F4. No check counts key length. KEY_RE's body `(?:[^: \t]|[ \t](?!#))*` (L63) has no upper bound.
F5. `_field` (L72-L139) reads `tools:`/`disallowedTools:` blocks itself. Indented lines under those keys are already parsed there (y1-y5, y7, d, i2, p4: L305, L313, L334-L348, L355). The column-0 check skips FLOW_KEYS lines (L210, L216).
F6. The test count on this branch is 109: 95 parser cases (079 + nk1-nk16, L302-L451), 12 tree cases (L480-L505), the no-files test (L522) and the real-tree test (L526). This matches A1's round 2 "109 passed" (work/096/07-audit-task.md L22) and 06 L123. 096's mutations go up to M55 (work/096/07-audit-task.md L22), so new ones start at M56.
F7. Real tree: 7 agent files, each with `---` on L1 and L5 (Grep `^---$`: 14 hits). Each has 3 frontmatter lines, all column-0 `name: `/`description: `/`tools: ` (Grep `^(name|description|tools): `: 3 per file, 21 total). That leaves 0 indented frontmatter lines. 0 lines have a second `: ` or ` #` after the key (Grep `^(name|description|tools): .*(: | #)`: 0), and 0 end with `:` (Grep `^(name|description|tools): .*:$`: 0). The longest key is `description` (11 characters). R1 Grep, 2026-11-24.
F8. These existing fixtures have indented lines outside a FLOW_KEYS block that reach the end of the line loop with no earlier error. Each must keep its result:
- p13 (L371-L380): `  PreToolUse:` / `    - matcher: "Bash"` / `      hooks:` / `        - type: command` / `          command: "./scripts/validate-readonly-query.sh"` → {Bash}
- q23 (L414-L425): `  # Inline ...` / `  - playwright:` / `      type: stdio` / `      command: npx` / `      args: ["-y", "@playwright/mcp@latest"]` / `  # Reference ...` / `  - github` → {Read}
- nk8 (L442): `  a: b` → NO_KEY(4), which comes from the later column-0 `- c`
- nk12 (L447): `  # c` → {Read, Write}

The other indented lines either error earlier (p3, p14, q5, q6, q13, q15, q18) or sit inside a FLOW_KEYS block. R1 trace (not run).

### YAML: value text (F-1)
F9. "A colon is allowed, but only if it's not followed by whitespace." (plain scalars) [https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html]
F10. Educative lists `key1: value1:` as an error example, "Due to an unnecessary colon after `value1`", under the message "mapping values are not allowed here" [https://www.educative.io/answers/unable-to-parse-yaml-mapping-values-are-not-allowed-here]. This is the end-of-line-colon form of F-1.
F11. APIMatic's rule text: "Make sure that for a key-value pair the `key` part and `value` part are separated by a colon `:` and a space" and "Try enclosing value in quotes." [https://docs.apimatic.io/rulesets/yaml-syntax-validation/mapping-value-not-allowed] So a quoted value with `: ` inside is fine (fixture p9, L364, already passes).
F12. In PyYAML's scanner, `scan_plain` ends a plain scalar at `:` when the next character is in `'\0 \t\r\n\x85  '`. In `fetch_value`, "There cannot be two simple keys one after another." is followed by `self.allow_simple_key = False`, and the block-context branch raises "mapping values are not allowed here" when `not self.allow_simple_key` [https://arai.searchfox.org/firefox-main/source/third_party/python/pyyaml/lib/yaml/scanner.py] (Firefox's vendored copy, PyYAML version not shown on the page: UNVERIFIED which release). R1's reading (not run): `name: x: y` raises "mapping values are not allowed here". PyYAML's verdict on `name: x: y`: UNVERIFIED (I2 probe).
F13. "A comment will end such a plain scalar" (a space followed by `#`) [https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html]. "Comments must be separated from other tokens by white space characters." [https://spec.yaml.io/main/review/markdown.html] So a value check must stop at ` #` or `\t#`. Otherwise `description: a # see: b` becomes a false error. PyYAML's verdict on that line: UNVERIFIED (I2 probe). R1 expects it to load as `{'description': 'a'}`.

### YAML: indented lines (F-2, F-4)
F14. "Each node must be indented further than its parent node." "All sibling nodes must use the exact same indentation level." [https://spec.yaml.io/main/review/markdown.html]
F15. A plain scalar "can also span multiple lines, and the newlines will be folded into spaces". "If lines are indented more than others, this is ignored" [https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html]. The spec example "Multi-line Flow Scalars" has `plain:` / `  This unquoted scalar` / `  spans many lines.` [https://spec.yaml.io/main/review/markdown.html]. So an indented line with no `key:` shape can be valid YAML (a plain continuation). A rule that only allows "key or item" for indented lines would make it a fail-closed false error.
F16. F-2's shape (`name: x` / `  foo: bar`): the continuation `foo: bar` holds `: `, which a plain scalar may not contain (F9). PyYAML's `scan_plain_spaces` sets `self.allow_simple_key = True` after a line break, and `stale_possible_simple_keys` drops a candidate key whose `key.line != self.line` [https://arai.searchfox.org/firefox-main/source/third_party/python/pyyaml/lib/yaml/scanner.py]. R1 cannot trace from this which error PyYAML raises. Verdict UNVERIFIED (I2 probe). 096/03 also left it unmeasured (L114).
F17. Block scalars: "All continuation lines in a block scalar have to be indented at least as much as the first line." [https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html]. The spec's literal example `--- |` / `  \//||\/||` / `  // ||  ||__` shows content that would fail a key/item shape test [https://spec.yaml.io/main/review/markdown.html]. So the lines after a `|` or `>` header are content, not structure, and must not get the key/value checks. Otherwise `description: |` / `  a: b` becomes a new false error. 087's docstring already lists "block-scalar content lines that start with one of these characters" as a fail-closed false error (L33-L34).
F18. The spec's "Compact Nested Mapping" example has `- item    : Super Hoop` / `  quantity: 1` [https://spec.yaml.io/main/review/markdown.html]. An item may carry a key on its own line, and its sibling keys are indented to the key's column. p13 and q23 rely on this (F8). Note `item    :`: spaces before the colon are allowed (as in 096/06's probe `a : c` → OK, work/096/06-verification.md L108).
F19. The spec's "Sequence of Mappings" example has a bare `-` line followed by `  name: Mark McGwire` [https://spec.yaml.io/main/review/markdown.html]. So a bare `-` opens a nested block, just as an empty-valued key does.

### Key length (F-3)
F20. PyYAML test data spec-10-08.error: "ERROR: - A simple key is restricted to only one line. - A simple key must not be longer than 1024 characters." [https://fuchsia.googlesource.com/third_party/pyyaml/+/refs/tags/5.2/tests/data/spec-10-08.error]
F21. PyYAML `stale_possible_simple_keys` drops a candidate key when `key.line != self.line or self.index-key.index > 1024`. It raises `ScannerError("while scanning a simple key", key.mark, ..."could not find expected ':'")` when the key is `required`, and `required = not self.flow_level and self.indent == self.column` [https://arai.searchfox.org/firefox-main/source/third_party/python/pyyaml/lib/yaml/scanner.py]. R1's reading (not run): the count is in characters (str index), from the key's first character to the token being fetched. A key of 1024 characters passes and 1025 fails, and the error text depends on whether the key is the first frontmatter line (not `required`). The exact boundary is UNVERIFIED (I2 probes 1024 and 1025, both as the first line and after `name: x`).
F22. The YAML 1.1 spec wording quoted in the SnakeYAML tracker: "the simple key must not span more than 1024 stream characters". The maintainer says SnakeYAML's own 128-character choice when dumping "is not a question of specification but a flavour of SnakeYAML" [https://bitbucket.org/snakeyaml/snakeyaml/issues/431/increase-simple-key-length-to-1024-stream]. The YAML 1.2.2 text of the 1024 limit: UNVERIFIED. spec.yaml.io's rendering stops at "Alias Nodes" (WebFetch at offset 60000) and has only "Implicit keys are restricted to a single line." [https://spec.yaml.io/main/review/markdown.html]

### Trailing comment after an empty-valued key (F-5)
F23. The spec's example "Single Document with Two Comments" is exactly F-5's shape: `---` / `hr: # 1998 hr ranking` / `- Mark McGwire` / `- Sammy Sosa` / `# 1998 rbi ranking` / `rbi:` / `- Sammy Sosa` / `- Ken Griffey` [https://spec.yaml.io/main/review/markdown.html]. So `hooks: # c` followed by a column-0 `- a` is valid YAML, and today's NO_KEY on it is a false error (F3).
F24. The same shape with `tools: # c` / `- Read` is handled by `_field`, not by the column-0 check. `value = "# c"` is non-empty (L88), so the next `- Read` gives `unparsed tools: line '- Read' (item 075)` (L98-L99). By F23 this is also a fail-closed false error, but it is `_field`'s and outside F-5's wording. R1 trace (not run). See OQ4.

### What the runtime does
F25. "**YAML that doesn't parse**: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." The `tools` field is "a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents]. The page does not name its YAML parser (re-read 2026-11-24, same as 096 F25), so the test still makes no runtime claim.

## Numbers used (show the math)
- Current tests: 79 + 16 (nk1-nk16) = 95 parser cases; 11 + 1 (n12) = 12 tree cases; 95 + 12 + 1 + 1 = 109 (F6).
- Real tree: 7 files x 3 lines = 21 frontmatter lines, all column 0. Proposed rules hit 0 of them: 0 indented, 0 with `: ` or ` #` in the value, 0 ending in `:`, longest key 11 ≤ 1024 (F7).
- Existing fixtures that reach a new indented-line check: p13 (5 indented lines), q23 (7), nk8 (1), nk12 (1), so 4 fixtures and 14 lines (F8). All must keep their result. R1 trace (not run).
- F-3 boundary (prediction, F21): `"k" * 1024 + ": v"` passes and `"k" * 1025 + ": v"` fails. 1024 + 2 (`: `) + 1 = 1027 characters per line.
- Proposed fixtures (proposals, not results; n = front index + 2; error texts are R3's call):
  1. F-1: `_fm("name: x: y", TOOLS)` → value error, line 2
  2. F-1 end-of-line: `_fm("name: x:", TOOLS)` → value error, line 2 (Educative shape, F10)
  3. F-1 nested: `_fm("hooks:", "  a: b: c", TOOLS)` → value error, line 3
  4. F-1 in-text negatives (RI-012): `_fm("description: a # see: b", TOOLS)` and `_fm("description: see https://x", TOOLS)` → {Read, Write}. The quoted `"a: b"` (p9) already exists.
  5. F-2: `_fm("name: x", "  foo: bar", TOOLS)` → indented-line error, line 3
  6. F-4 continuation decision fixture: `_fm("description:", "  plain text", TOOLS)` (spec "Multi-line Flow Scalars" shape, F15) → {Read, Write} if continuations are allowed, or a named error listed as a known false error (OQ1)
  7. F-4 block-scalar decision fixture: `_fm("description: |", "  a: b", TOOLS)` → {Read, Write} if block content is skipped (OQ2)
  8. F-4 bad indent: `_fm("hooks:", "    a: b", "  c: d", TOOLS)` → error if a sibling-indent rule is adopted (F14, OQ3; PyYAML verdict UNVERIFIED)
  9. F-3: `_fm("k" * 1025 + ": v", TOOLS)` → key-length error, line 2; `_fm("name: x", "k" * 1025 + ": v", TOOLS)` → line 3; positive `_fm("k" * 1024 + ": v", TOOLS)` → {Read, Write}
  10. F-5: `_fm("hooks: # c", "- a", TOOLS)` → {Read, Write}; spec Ex. 2.9 verbatim plus TOOLS → {Read, Write}
  11. tree case: r1 with `name: x: y` → `.claude/agents/r1-researcher.md: <value error line 2>`
- Projection if 1-5, 9 (3 cases), 10 (2) and 11 are adopted, and 6-8 are decided: 109 + 11 parser + 1 tree = 121, plus 0-3 for 6-8, so 121-124. This is a projection, not a run.
- Proposed mutations (predictions, not runs; I2 runs each on a scratch copy):
  - M56: the value `: ` check is removed → fixtures 1, 2, 3, 11 fail.
  - M57: the value check runs over the comment (no ` #` stop) → fixture 4 (`a # see: b`) fails.
  - M58: the indented-line check is removed → 5 (and 3 if the value check is reached only through it) fails.
  - M59: the key cap is removed → both 1025 fixtures fail; M60: cap `>= 1024` → the 1024 positive fails.
  - M61: `prev_open` goes back to "rest empty" (no trailing comment) → both F-5 fixtures fail.
  - M62: block-scalar skip removed (if adopted) → fixture 7 fails.
  - M63: the FLOW_KEYS exemption is dropped from the indented check → d, i2, y1-y5 or y7 change text (R3 traces which).
  - Existing M42-M55 must still fail their named fixtures. In particular, M53 (`[^:]*` key body) still fails nk13, nk14, nk16.
- Each new fixture's PyYAML verdict is recorded by I2/I3 in 05/06 as information only. A "YAML-invalid" claim is allowed only next to that probe output (096/03 Removed claim 3, L91).

## Fit for a ~$3k account
This is a test-only item. It changes no strategy rule, order, premium, dividend, tax or liquidity input, so the $3k limits do not apply. It makes the agent-tools drift test fail with a named error on more frontmatter that YAML would reject, and it stops one false error on a spec-valid shape (F23). It makes no claim about what Claude Code grants (F25). Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. Plain continuation lines (F15): should an indented line that is neither `key:` nor `- ` nor a comment be allowed when it holds no `:`+space/tab/EOL and no ` #`, or rejected as a documented fail-closed false error? 0 real lines either way (F7). Allowing it adds a rule and a fixture. Rejecting it adds a docstring entry.
2. Block scalars (F17): should lines after a `|`/`>` header (on any non-FLOW_KEYS key, more indented than that key) be skipped as content? This would also clear part of 087's known false error (L33-L34). If not, fixture 7 is a known false error.
3. Sibling indentation (F14): should the indented allow-list also check indentation levels (a stack of open parents, where a dedent must return to a known level)? This is closer to YAML but larger. Without it, fixture 8's shape passes. That PyYAML rejects it is UNVERIFIED (I2 probe), so it would be listed as a known gap.
4. `tools: # c` / `- Read` (F24) gives a `_field` false error. Fix it in this item (strip a ` #` comment from `value` in `_field`), or list it in the docstring next to F-5's fix? The request names only `hooks: # c`.
5. Key cap boundary (F21): pin the test at "more than 1024 characters from the key's first character to the colon" once I2's probe confirms 1024 passes and 1025 fails in PyYAML. If the probe differs, use the measured boundary or a lower cap (fail closed) and say so in 05.
6. Docstring: add an "Item 104:" paragraph. Remove `hooks: # c` from "Also rejected" (L47-L48), and add each new check and any known false error from OQ1-OQ4. Keep "This says nothing about what Claude Code does with such a file."
7. RI-002 near miss, not counted (request). No GUARDED condition changes.
