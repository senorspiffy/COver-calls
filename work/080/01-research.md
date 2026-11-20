# 01 Research brief - 080

Type BUG, Scope FULL, opened by A1, 2026-11-20. Branch daily-fixes/2026-11-20 (read only). R1 has no shell (tools: Read, Write, Glob, Grep, WebSearch, WebFetch), so every repo fact below comes from reading files, cited as path:line. Nothing below is a measured test run by R1; probe results are quoted from logs/audit/2026-11-19-075.md and work/075/06-verification.md.

## Question
tests/test_agent_tools.py (075, PR #33) finds a key by testing each frontmatter line on its own (`line.startswith(key + ":")`). It does not track YAML state, so (1) a `tools:` line inside a multi-line quoted `description:` value is read as the tool list, (2) tab indentation, which YAML rejects, is accepted, and (3) no fixture pins the bare `-` item, so mutation M14 stays green. How does YAML (and Claude Code) read these shapes, and what exact rules and fixtures make each one fail a named test?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. `_field` collects every frontmatter line that starts with `key + ":"` (tests/test_agent_tools.py L36). Nothing before it checks whether an earlier line opened a quoted value, so a column-0 `tools:` line inside an open quoted `description:` value counts as the key.
F2. `agent_tools` takes `front = lines[1:end]`, where `end` is the first later line equal to `---`. It then calls `_field` for `tools` and `disallowedTools` only (L105-L118). No other frontmatter line (for example `description:`) is checked.
F3. A block-list line counts as a continuation when `line[0] in " \t"` (L54), so a leading tab is accepted as indentation. L39 also accepts `tools:\t` (a tab after the colon).
F4. `_is_item(s)` is `s == "-" or s.startswith("- ")` (L26-L27). With a bare `-`, `s[1:].strip()` is `''`, ENTRY_RE rejects it, and the error is `unparsed tools: entry '' (item 075)` (L62, L94-L95). No case in CASES (L159-L208) has a bare `-` line.
F5. Today's 7 agent files each have a 3-line frontmatter (`name`, `description`, `tools`, L2-L4) with unquoted one-line values. No frontmatter line has a tab in its indentation or a value starting with `"`, `'`, `[` or `{` (Grep `^\t|^ +\t|^[A-Za-z]+: *["'\[{]` in .claude/agents: 0 hits; Grep `^---$`: 2 per file). New checks would therefore leave the real-tree test green.
F6. 075's research found that nothing in the repo imports yaml, and the declared dependencies are numpy and pandas (work/075/01-research.md F6). A1 says not to add a PyYAML cross-check, because it would be skipped wherever PyYAML is missing (logs/audit/2026-11-19-075.md L62).

### The probes (quoted)
F7. a1-n1: r1's `description: "Research team, ...` opens a double-quoted value on L3. The value closes on a line after `tools: Read, Write, Glob, Grep, WebSearch, WebFetch`. PyYAML 6.0.3 keys: `['name', 'description']`, so there is no `tools` key. The test gives 42 passed. The single-quoted form behaves the same way (logs/audit/2026-11-19-075.md L43).
F8. a1-n2: r1 with a tab-indented block list of the six names. PyYAML raises `ScannerError` and the test gives 42 passed. With Bash in the tab list the test does fail, but only because Bash is not on the allow-list (logs/audit/2026-11-19-075.md L44).
F9. M14 (`_is_item` without `s == "-"`): 42 passed. The bare `-` then gives `unparsed tools: line '-'` instead of `unparsed tools: entry ''`. The result is still an error, but no fixture pins the text (work/075/06-verification.md L75, L77; logs/audit/2026-11-19-075.md L45).
F10. Other shapes A1 tried already fail closed: anchor, alias, tag, quoted key, indented mapping, `? tools`, a flow mapping across lines on `tools:`, and a BOM. CRLF parses the same as LF (logs/audit/2026-11-19-075.md L31-L40).

### YAML rules (spec)
F11. "To maintain portability, tab characters must not be used in indentation, since different systems treat tabs differently." [https://yaml.org/spec/1.2.2/] Tabs are still allowed as separation whitespace inside a line (same source, as summarised by WebFetch), so `tools:\t Read` (F3, L39) is valid and the new rule should cover leading whitespace only.
F12. "All flow scalars can span multiple lines; line breaks are always folded." [https://yaml.org/spec/1.2.2/] So a `"` or `'` value left open on its first line is valid YAML, and it absorbs the following lines, including a column-0 `tools:` line (F7, measured with PyYAML).
F13. In double-quoted scalars a `"` can be escaped as `\"` ("Escaped ASCII double quote (x22)"), and escapes are only interpreted in double-quoted scalars. [https://yaml.org/spec/1.2.2/] In single-quoted scalars a literal `'` is written `''` (spec Example 2.17: `' # Not a ''comment''.'`). [https://yaml.org/spec/1.2.2/]
F14. Consequence of F13 (R1's reasoning, not run): A1's suggested rule, "value starts with a quote and does not end with the same quote on that line" (logs/audit/2026-11-19-075.md L59), misses two open values. `description: "abc\"` ends with `"`, but that `"` is escaped, so the value is still open. `description: 'it''` ends with `'`, but `''` is one literal quote, so it is still open. A small scanner can tell them apart. Double quotes: skip the character after each `\`; the first unescaped `"` closes. Single quotes: `''` is a literal; a lone `'` closes. The same scanner flags `"abc\\"` and `'it'''` as closed. Whether PyYAML reads these four exactly this way is UNVERIFIED (R1 cannot run it).
F15. A closed quoted value followed by a comment (`description: "x" # c`) is valid YAML, because comments must be separated by white space [https://yaml.org/spec/1.2.2/]. A strict "must end with the quote" rule would report it as an error. That fails closed, and no agent file has this shape today (F5).
F16. Flow collections can also span lines: section 2.1 says flow styles use "explicit indicators rather than indentation to denote scope", and Example 2.6 is a flow mapping across several lines. [https://yaml.org/spec/1.2.2/] By the same reasoning as F12, `description: [a,` or `description: {a: b,` left open could absorb a later column-0 `tools:` line. This is not in the request, and it is UNVERIFIED by a PyYAML run. A1's probe only tried a multi-line flow mapping on `tools:` itself, where the test already errors (F10). The 075 code checks an unclosed `[` only on `tools:`/`disallowedTools:` (L64-L66).
F17. Whether YAML forbids a `---` line inside an open quoted scalar is UNVERIFIED: the spec text WebFetch returned cut off before the `c-forbidden` production. It does not matter for the fix: with the F14 scanner, the open quote is reported whether or not `---` ends the frontmatter (F2).

### How Claude Code reads it (official docs)
F18. "Subagent files use YAML frontmatter for configuration, followed by the system prompt in Markdown." [https://code.claude.com/docs/en/sub-agents]
F19. `tools`: "Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents]
F20. For an invalid file, the docs say "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log", and this happens "without reporting it in the session". [https://code.claude.com/docs/en/sub-agents]
F21. Inference from F18 + F19 + F7 (not run in Claude Code): a1-n1 is valid YAML with no `tools` key, so r1 would load with every tool, Bash included. Inference from F20 + F8: a1-n2 does not parse, so r1 would not load at all, silently. That is a different failure from a1-n1, but in both cases the test's "six tools" verdict is wrong. Claude Code's actual behaviour on both files is UNVERIFIED.
F22. The docs do not say whether `description` may be quoted or multi-line. Every example on the page uses a single unquoted line (WebFetch summary of [https://code.claude.com/docs/en/sub-agents]).

## Numbers used (show the math)
- Today's suite: 42 tests in tests/test_agent_tools.py = 33 parser cases + 7 tree cases + 1 no-files + 1 real-tree (logs/audit/2026-11-19-075.md L11). On the head with a1-n1 / a1-n2 / M14: 42 passed each (F7-F9).
- Real agent files hit by the new rules: 0 of 7 (F5), so the real-tree test stays green.
- Minimum new parser fixtures for "Done looks like": double-quote multi-line (1) + single-quote multi-line (1) + tab-indented block list (1) + bare `-` (1) = 4. Optional: escaped-end cases `"abc\"` and `'it''` (2, F14), and a multi-line flow value on `description:` (1, F16). That gives 4 to 7 new parser cases. Tree-level a1-n1 and a1-n2 on r1 add 2 more. These are counts of proposed cases, not test results.
- Proposed mutations, each meant to fail at least one named fixture. These are predictions, not runs:
  - Remove the open-quote check → both multi-line quoted fixtures fail.
  - Remove the tab check → the tab fixture fails.
  - M14 → the bare `-` fixture fails (expected text `unparsed tools: entry '' (item 075)`, F4).
  - Replace the scanner with a plain `endswith` (if the F14 cases are adopted) → the escaped-end fixtures fail.

## Fit for a ~$3k account
This is a process/test item. It changes no strategy rule, trade, price, premium, dividend, tax or liquidity input, so the $3k limits don't apply. It keeps the no-shell research agents, which read untrusted web text, from silently getting Bash (F21) and protects the machine that runs the bot. Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. Scope of the checks (for R2/R3/I1). Run the open-quote and tab checks on every frontmatter line in `agent_tools`, before `_field`, not only on `tools:`/`disallowedTools:`. The attack line is `description:` (F2, F7). Suggested error texts: `unclosed quoted value on frontmatter line <n> (item 080)` and `tab in indentation on frontmatter line <n> (item 080)`.
2. Which lines does the quote rule apply to? `key: "...` / `key: '...` values and block items `- "...`. Should the check also treat a value starting with `[` or `{` that does not close on its line as an error on any key (F16)? That is outside the request's wording, the same hole class, and UNVERIFIED by a run. If adopted, it fails closed.
3. Quote rule: a simple `endswith` (A1's text) or the F14 scanner? The scanner closes two holes the request does not name. Both fail closed on F15's `"x" # c`. Is that acceptable, given that no agent file has it (F5)?
4. Tab rule: leading whitespace only (F11). Keep the separator tab after `tools:` (L39) valid. After the rule, the `\t` in L54's `" \t"` can never be reached inside frontmatter. Leave it or remove it?
5. RI-002 wording: A1 counts this as a near miss caught before merge, not an occurrence (precedent 069/070/072; logs/recurring-issues.md L25). 080 is built on daily-fixes/2026-11-20, which is on top of PR #33, so it should not change any GUARDED condition there.
6. Overlap: the request files for 081, 082, 084, 085 and 086 do not name tests/test_agent_tools.py or .claude/agents/ (Grep over work/081-086: 0 hits), so no file clash is known.
