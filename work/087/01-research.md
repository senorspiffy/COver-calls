# 01 Research brief - 087

Type BUG, Scope FULL, opened by A1, 2026-11-21. Branch daily-fixes/2026-11-21 (read only). R1 has no shell (tools: Read, Write, Glob, Grep, WebSearch, WebFetch), so every repo fact below comes from reading files and is cited as path:line. R1 ran no test, PyYAML call or regex. Every probe result is quoted from logs/audit/2026-11-20-080.md. Any trace R1 did by hand is labelled "R1 trace (not run)".

## Question
tests/test_agent_tools.py (075/080) treats a frontmatter value as multi-line only when a quote comes directly after `key: ` or `- ` (QUOTE_START_RE, L32). A1 found three ways a later column-0 `tools:` line still gets through while PyYAML sees no `tools` key:
- F1: YAML node properties (`&anchor`, `!tag`) between the indicator and an open quote.
- F3: a flow collection (`[`, `{`) left open on any key other than `tools:`/`disallowedTools:`.
- F2: the `(?:-[ ]+)*` part of QUOTE_START_RE is not pinned by any fixture.

The request also asks for a decision on p11 (`tools:\tRead`). What does the YAML grammar allow before a scalar or flow collection, and what rule, fixtures and mutations make each shape fail with a named error and no false error on today's tree?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. `QUOTE_START_RE = [ ]*(?:-[ ]+)*(?:[^\s"'#][^:]*:[ \t]+)?(["'])` is applied with `.match` to every frontmatter line. The quote group must come right after the optional `- ` run and the optional `key:` + whitespace (tests/test_agent_tools.py L32, L138).
F2. `_frontmatter_error` checks only three things: a tab in the leading whitespace (L135-L137), an open quote at the value start (L138-L142) and text after the close (L143-L144). Nothing checks `&`, `!`, `*`, `[` or `{` at a value start.
F3. An open `[` is checked only on the `tools:`/`disallowedTools:` value, inside `_field` (L74-L76, text `unclosed [ in {key}: (item 075)`). `{` is never checked.
F4. In `_field`, a column-0 line that is not a `- ` item ends the block (L64-L65). So the closing `end"` or `]` line of A1's shapes ends the scan, and the hidden `tools:` line is read as the tool list.
F5. R1 trace (not run) of the F1 shape `description: &d "Research team,` against L32: the key group matches `description:` + ` `, and the next character is `&`, not a quote. `[^:]*` cannot cross the only `:`. With the key group skipped, position 0 is `d`. So there is no match, no error, and `_field` returns the six tools. This agrees with A1's `59 passed` (logs/audit/2026-11-20-080.md L58).
F6. R1 trace (not run) of `- &a "x`: `-[ ]+` matches, the key group fails (no `:`), and the next character is `&`. No match. Same result as A1's shapes.py (logs/audit/2026-11-20-080.md L59).
F7. Today's 7 agent files have 0 tab characters (Grep `\t` in .claude/agents: 0). They also have 0 lines whose value start is `&`, `!`, `*`, `[`, `{`, `|` or `>` (Grep `^[ \t]*(- +)*([^\s"'#][^:]*:[ \t]+)?[&!*\[{|>]` over the whole files: 0 hits). Each file has exactly 2 `^---$` lines and 3 frontmatter keys, `name`/`description`/`tools` on L2-L4 (Grep). So a rule anchored at the value start finds no false error on today's tree.
F8. One real description has `&` in the middle of the value: a1-auditor.md L3, `description: Audit & Efficiency team. ...`. Any `&`/`!` rule must therefore be anchored at the value start. A rule that searches anywhere in the line would turn a1-auditor into a false error (R1 trace, not run). This is the RI-012 shape ("short-pattern search").
F9. The test file currently has 48 parser cases, 9 tree cases, 1 no-files test and 1 real-tree test = 59. This matches A1's `59 passed` (tests/test_agent_tools.py L213-L296, L323-L342; logs/audit/2026-11-20-080.md L19). The 080 mutations are numbered M14-M24 (work/080/03-handoff.md step 4), so new ones can start at M25.
F10. No other open item's request names tests/test_agent_tools.py, .claude/agents or QUOTE_START_RE (Grep over work/08*/ and 09*/request.md: 0 files; 091 is check_pipeline/run-item work).

### YAML grammar: what may come before a scalar or flow collection
F11. "Each node may have two optional properties, anchor and tag, in addition to its content." "Node properties may be specified in any order before the node's content." "Either or both may be omitted." [https://spec.yaml.io/main/review/markdown.html] (YAML 1.2.2 text, revision 2021-10-01. The canonical page https://yaml.org/spec/1.2.2/ came back cut off at 6.6 for R1, the same limit 080 hit, so the 6.9 text was read from this rendering.)
F12. Production `c-ns-properties(n,c) ::= ( c-ns-tag-property ( s-separate(n,c) c-ns-anchor-property )? ) | ( c-ns-anchor-property ( s-separate(n,c) c-ns-tag-property )? )`. So there is at most one tag and at most one anchor, in either order, separated by whitespace. [https://spec.yaml.io/main/review/markdown.html]
F13. The same section's example puts a tag and an anchor before a double-quoted scalar: `!!str &a1 "foo":` / `  !!str bar` / `&a2 baz : *a1`. [https://spec.yaml.io/main/review/markdown.html]
F14. Indicators (5.3): "`&` (x26, ampersand) denotes a node's anchor property." "`*` (x2A, asterisk) denotes an alias node." "The `!` (x21, exclamation) is used for specifying node tags." `[`/`]` start/end a flow sequence and `{`/`}` start/end a flow mapping. [https://yaml.org/spec/1.2.2/]
F15. "Repeated nodes (objects) are first identified by an anchor (marked with the ampersand - "&"), and are then aliased (referenced with an asterisk - "*") thereafter." Example 2.10: `- &SS Sammy Sosa` / `- *SS # Subsequent occurrence`. [https://yaml.org/spec/1.2.2/]
F16. Example 2.23 has a tag before a plain and before a block scalar: `not-date: !!str 2002-04-28`, `picture: !!binary |`. [https://yaml.org/spec/1.2.2/]
F17. Separation whitespace may be tabs: "Note that such white space may safely include tab characters." The production is `s-separate-in-line ::= s-white+ | <start-of-line>`. [https://yaml.org/spec/1.2.2/] So a property may be followed by a tab, and the separator group must be `[ \t]+`, not `[ ]+`.
F18. Whether an alias node may carry properties or content: UNVERIFIED. The 7.1 text was cut off in both renderings R1 fetched. Only "Subsequent occurrences of a previously serialized node are presented as alias nodes" was returned [https://spec.yaml.io/main/review/markdown.html].
F19. Grammar of anchor names and tag text (which characters `\S*` must cover, e.g. `!<tag:yaml.org,2002:str>` verbatim tags): UNVERIFIED. The 6.9.1/6.9.2 productions were not returned in the fetched text.

### Flow collections span lines
F20. "YAML also has flow styles, using explicit indicators rather than indentation to denote scope." [https://yaml.org/spec/1.2.2/] "Flow styles typically depend on explicit indicators rather than indentation to convey structure." (6.5) [https://yaml.org/spec/1.2.2/]
F21. Example 2.6 is a flow mapping across lines (`Sammy Sosa: {` / `    hr: 63,` / `    avg: 0.288,` / ` }`). Example 2.11 has flow sequences across lines after the explicit `?`/`:` indicators: `? [ New York Yankees,` / `    Atlanta Braves ]` / `: [ 2001-07-02, 2001-08-12,` / `    2001-08-14 ]`. [https://yaml.org/spec/1.2.2/]
F22. PyYAML documents that it does not enforce the spec's flow indentation: "Indentation of flow collections. The spec requires them to be indented more than their block parent node. Unfortunately this rule renders many intuitively correct constructs invalid", with the example `block: {` / `} # this is indentation violation according to the spec.` [https://pyyaml.org/wiki/PyYAMLDocumentation] This is consistent with A1's F3 probe, where `description: [a,` / `tools: Read, Write` / `]` at column 0 loads in PyYAML 6.0.3 with no `tools` key (logs/audit/2026-11-20-080.md L68). A strict 1.2.2 reader might reject that file instead. Either way, it is not "two tools".
F23. A `]` or `}` inside a quoted entry, or after a ` #` comment, does not close a flow collection. Comments must be separated from other tokens by white space (6.6, verified in 080: work/080/03-handoff.md #15) [https://yaml.org/spec/1.2.2/]. Consequence (R1 trace, not run): a rule of the form "a `[` at the value start must end with `]` on its line" or "bracket depth returns to 0" misses `description: ["]",` and `description: [a, # ]`. Both look closed, but both are still open. A closed-on-line check needs the existing `_quote_end` scanner (L110-L128) for quoted entries and must stop at ` #`. Whether PyYAML reads these two shapes as open: UNVERIFIED (not run).

### Other indicator prefixes the regex does not know
F24. "A question mark and space (`? `) indicate a complex mapping key." "`?` (x3F, question mark) denotes a mapping key." "`:` (x3A, colon) denotes a mapping value." [https://yaml.org/spec/1.2.2/] Example 2.11 puts a value on a line that starts with `: ` (F21).
F25. R1 trace (not run): `QUOTE_START_RE` does not match a line that starts with `: "`. `(?:-[ ]+)*` only knows `-`. The key group needs a `:` after at least one character. The quote group then sees `:` at position 0. So `? description` / `: "Research team,` / `tools: Read, Write` / `end"` would give {Read, Write}, the same hole as F1. Whether PyYAML loads this shape with no `tools` key: UNVERIFIED (not run). It is not in A1's list. It is the same root cause (prefixes before a value start were taken from probes, not from the grammar), so R1 raises it for R2/R3 rather than leaving it out.
F26. R1 trace (not run): `-` followed by a tab (`  -\t"x,`) is not matched by `(?:-[ ]+)*`, and the tab rule (L135) looks only at the leading whitespace, which stops at `-`. Whether YAML or PyYAML accepts a tab after a block-sequence `-`: UNVERIFIED. If either does, the shape hides `tools:` like F2. Failing closed on it costs nothing on today's tree (F7: 0 tabs).

### Tabs after `tools:` (p11)
F27. The spec allows a tab as separation inside a line (F17). So `tools:\tRead, Write` is valid YAML 1.2.2 [https://yaml.org/spec/1.2.2/].
F28. PyYAML 6.0.3 raises `ScannerError` on `tools:\tRead, Write` (A1 measured, logs/audit/2026-11-20-080.md L69). PyYAML's own docs list tabs as a known deviation: "rules for tabs in YAML are confusing. We are close, but not there yet." "Anyway, the best rule for tabs in YAML is to not use them at all." [https://pyyaml.org/wiki/PyYAMLDocumentation]
F29. The Claude Code docs do not name the YAML parser used for subagent frontmatter. They also don't mention tabs, anchors or tags (WebFetch of both halves of the page) [https://code.claude.com/docs/en/sub-agents]. Which reading the runtime uses for p11 is UNVERIFIED.
F30. Docs: "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." Separately: "A plugin subagent whose frontmatter has no `name` or doesn't parse still loads, under its filename." [https://code.claude.com/docs/en/sub-agents] .claude/agents files are project subagents, not plugin ones. So the first sentence applies, and p11 under a PyYAML-like reader means "r1 does not load", not "r1 has Read, Write". Inference from the docs, not run.
F31. The docs name a runtime check: "To find files in an `agents` directory whose frontmatter doesn't parse, run `claude plugin validate` against the directory, for example `.claude/agents`" [https://code.claude.com/docs/en/sub-agents]. This is the only documented way to learn the runtime's own verdict on p11. It needs a shell, so it is for the orchestrator or A1, on a scratch copy only. R1 has not run it, and its result on a tab-separated `tools:` line is UNVERIFIED.
F32. `tools`: "a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents] (Same as 080 F19. This is why an absorbed `tools:` line matters.)

### Python `re` constraints (RI-008: project minimum 3.10)
F33. `match`: "If zero or more characters at the beginning of string match the regular expression pattern, return a corresponding Match." `fullmatch`: "If the whole string matches the regular expression pattern, return a corresponding Match." [https://docs.python.org/3/library/re.html]
F34. `(?:...)`: "A non-capturing version of regular parentheses." `\S`: "Matches any character which is not a whitespace character." `*`: "match 0 or more repetitions of the preceding RE, as many repetitions as are possible." [https://docs.python.org/3/library/re.html] So `(?:[&!]\S*[ \t]+)*` adds no capture group, and `m.start(1)` (L140) still points at the quote.
F35. The fetched docs are for Python 3.15.2. In them, `re.match`/`Pattern.match` are "Soft deprecated since version 3.15" in favour of `prefixmatch()` ("Added in version 3.15"). The docs also say code supporting older versions "should continue to use `match()`". Possessive quantifiers and atomic groups `(?>...)` are "Added in version 3.11". [https://docs.python.org/3/library/re.html] With the 3.10 floor (RI-008), the fix must keep `.match` and must not use `*+`, `++` or `(?>...)`.

## Numbers used (show the math)
- Today's test count: 48 parser (33 from 075 + p1-p15) + 9 tree (n0-n5, n7, n8, n9) + 1 + 1 = 59 (F9).
- Real frontmatter lines a value-start rule would see: 7 files x 3 lines = 21. Lines with a value start in `&!*[{|>`: 0 (F7). Lines with `&` elsewhere in the value: 1 (a1-auditor L3, F8). Tabs: 0.
- Proposed parser fixtures (counts of proposals, not test results). Expected texts use 080's `UNCLOSED`, plus a new open-flow text whose wording is for R3. Line n = front index + 2.
  1. `description: &d "Research team,` / `tools: Read, Write` / `end"` → UNCLOSED line 2 (F1 anchor)
  2. same with `!!str "` → UNCLOSED 2 (F1 tag)
  3. same with `!!str '` → UNCLOSED 2
  4. same with `&a !!str "` → UNCLOSED 2 (anchor + tag, F12)
  5. `hooks:` / `  - &a "x,` / `tools: Read, Write` / `y"` → UNCLOSED 3 (`- &a "`)
  6. `hooks:` / `  - "x,` / `tools: Read, Write` / `y"` → UNCLOSED 3 (F2; A1 gave this text, logs/audit/2026-11-20-080.md L64)
  7. `description: [a,` / `tools: Read, Write` / `]` → open-flow line 2 (F3)
  8. `description: {a: b,` / `tools: Read, Write` / `}` → open-flow line 2
  9. `description: !!seq [a,` / `tools: Read, Write` / `]` → open-flow line 2 (property before flow)
  10. `description: ["]",` / `tools: Read, Write` / `]` → open-flow line 2 (F23, quoted `]`)
  11. `description: [a, # ]` / `tools: Read, Write` / `]` → open-flow line 2 (F23, comment `]`)
  12. positive `description: &d "a"` / `tools: Read, Write` → {Read, Write}. Only if R3 picks the "allow properties" option. Under "fail closed on `&`/`!`/`*`" it becomes an error fixture.
  13. positive `description: Audit & Efficiency team` / `tools: Read, Write` → {Read, Write} (F8 anchoring; RI-012 negative test)
  14. positive: the docs' closed nested flow `args: ["-y", "@playwright/mcp@latest"]` under `mcpServers:` → no error (080 S7 shape)
  15. optional (F25): `? description` / `: "Research team,` / `tools: Read, Write` / `end"` → UNCLOSED 3
  16. p11 changed or kept per the decision below.

  Total: 14 to 15 new parser cases. Tree cases: r1 with the anchor shape (UNCLOSED 3) and r1 with the open-flow shape (open-flow 3) = 2. If all are adopted, 59 + 15 + 2 = 76 tests (a projection, not a run).
- Proposed mutations (predictions, not runs):
  - M25 drop the property group → fixtures 1-5 (and 9 if the flow rule shares it).
  - M26 drop the flow targets / flow rule → 7-11.
  - M27 = A1-m3 drop `(?:-[ ]+)*` → 5, 6. R1 trace for 6: without the group, the key group takes `-`, but `[^:]*` finds no `:`, and position 2 is `-`, not a quote, so the error is lost.
  - M28 flow check by bracket depth with no quote awareness → 10.
  - M29 flow check ignoring ` #` → 11.
  - M30 property rule searched anywhere in the line → 13 and the real-tree test (a1-auditor).
  - If F25 is adopted, M31 drop `?`/`:` from the indicator group → 15.

## Fit for a ~$3k account
This is a test/process item. It changes no strategy rule, trade, premium, dividend, tax or liquidity input, so the $3k limits do not apply. It makes the agent-tools drift test fail loudly when a frontmatter shape can hide the `tools:` line from YAML readers. It does not enforce what Claude Code actually grants (080 #29). Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. Allow node properties, or fail closed on them (request, both options)? Allowing `(?:[&!]\S*[ \t]+)*` before the quote (F11-F13, F17) keeps valid YAML readable, but the anchor/tag sub-grammar is UNVERIFIED (F19). Failing closed on any value start `&`, `!` or `*` has no false error today (F7: 0 lines). It needs no grammar, and it also covers aliases, whose rules R1 could not verify (F18). Either way, the rule must be anchored at the value start (F8). R1 leans fail closed, since the file format needs none of these and no agent uses them, but that is R2/R3's call.
2. Open-flow rule: on which keys, and with what precedence over `_field`'s `unclosed [ in tools:` (L74-L76)? If the new check runs first on every line, j3 (`tools: [Read, Bash`, L230) changes text. 080 D5 avoided that by leaving flow out. Options: exempt `tools:`/`disallowedTools:` from the new check, or keep j3's text by having `_frontmatter_error` skip those two keys, or accept the new text and update j3. The check must be quote- and comment-aware (F23), or else fail closed on any value-start `[`/`{` outside `tools:`/`disallowedTools:` (0 lines today, F7; it would turn the docs' `mcpServers` example into a false error).
3. Should the prefix group cover `?` and `:` as well as `-` (F24, F25), and a tab after `-` (F26)? Neither is in A1's list, and neither has been probed with PyYAML. Suggest A1 or I2 probe `? description` / `: "...` and `-\t"x,` in a scratch dir before R3 decides.
4. p11 (`tools:\tRead, Write`): the spec says valid (F27), PyYAML says invalid (F28), and the runtime reader is unknown (F29). Under the documented behaviour, an unparsed project agent is skipped (F30). Choices: (a) fail closed (a tab anywhere in a `tools:`/`disallowedTools:` line → error; 0 real lines affected, F7). This changes p11 to an error fixture, and M22 needs a new target. (b) Keep p11 positive only if the orchestrator runs `claude plugin validate` on a scratch `.claude/agents` holding the p11 shape and it reports no parse error (F31), with that output pasted into 05. (a) needs no runtime claim and matches 080 D8.
5. The existing 080 docstring (L15-L21) lists three unreadable cases. It needs the new ones (properties, open flow) and must keep "says nothing about what Claude Code does".
6. RI-002 wording: A1 counts this as a near miss caught before merge, not an occurrence (request; logs/recurring-issues.md L25). 087 runs on daily-fixes/2026-11-21 on top of PR #35, so no GUARDED condition changes.
