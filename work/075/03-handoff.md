# 03 Research hand-off - 075
Status: READY (R3's own checks pass. check_handoff is run by the orchestrator and pasted at the end of Self-check. READY stands only if that output says PASS; on FAIL the item comes back to R3.)

Recurring issues checked (item 013), against this file:
- RI-001 (ESCALATED): every selector in the map has a count R3 computed from file reads of today's tree (branch daily-fixes/2026-11-19):
  - Parser: runs on 7 of 7 agent files. All 7 parse with no error: 40 of 40 entries on the 7 L4 lines are letters only.
  - Allow-list check: runs on 4 NO_SHELL files, and 4 of 4 hold exactly the 6 allowed tools.
  - Body-line check: covers 5 lines, and 5 of 5 name the orchestrator.
  - No "always" or "every" appears without a count.
- RI-002 (GUARDED; 075 is its near miss): this item is the fix. Every token the parser cannot read becomes a named error, never "not Bash" (step 1). Missing inputs lists each absent input with its result. Nothing is defaulted.
- RI-014 (OPEN): not touched. 079 changes scripts/check_pipeline.py; 075 changes only tests/test_agent_tools.py.
- RI-006: the totals below were counted by R3 from this table. The orchestrator's check_handoff run is the authority.
- RI-004 / RI-005: every fixture's expected result in the map is traced, one step at a time, through the rule it shows (Self-check). Two mismatches were found and fixed in the map before READY (see the end of Self-check).
- RI-012: the new parser classifies entries by a full-match regex on a parsed token, not by a substring search. The wording lint (a substring rule) is unchanged and out of scope (D5).
- RI-007: Scope FULL, and the code change is in tests/ only, so I1-I3 run. There is no `.claude/` or `templates/` edit, so this is not a RULES branch.
- RI-008: stdlib `re` only, and no syntax newer than 3.10 (no `match`). I3 runs the 3.11 compile.
- RI-009 / RI-011: per the brief, no file overlap with 076-079 (they change scripts/check_pipeline.py and scripts/probe_guardrails.py).
- Not applicable: RI-003 (no calendar), RI-010 (no agent-text duty added), RI-013 (no realtest change).

Sources:
- Repo on branch daily-fixes/2026-11-19. R3 opened every cited file:line. R3 has no shell: it ran no git command, no test and no script.
- Fetched 2026-11-19:
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/tools-reference
  - https://yaml.org/spec/1.2.2/
  - https://docs.rs/crate/roba/0.7.1/source/src/agent_check.rs
  - https://code.claude.com/docs/es/sub-agents.md
  - https://code.claude.com/docs/zh-CN/sub-agents.md
  - https://code.claude.com/docs/ja/tools-reference.md
  - https://code.claude.com/docs/ru/sub-agents
  - https://www.glukhov.org/fr/ai-devtools/claude-code/claude-code-subagents/
  - https://agentsroom.dev/tr/blog/read-only-review-agent
- The claudeissues.com titles were confirmed by WebSearch only. R3 did not read those pages.
- New for D1 (1), R3's own finding: https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/42124227/why-does-the-yaml-spec-mandate-a-space-after-the-colon. It quotes the YAML spec: "Normally, YAML insists the “:” mapping value indicator be separated from the value by white space." This is a secondary source: the yaml.org pages R3 fetched were cut off before that section. The rule fails closed whichever way the runtime reads such a line, so the map does not depend on the quote.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| #1 01 F1: `_field` returns the comma-split value of the first `key:` line, or the following `- X` lines when the value is empty, and keeps every non-empty token unchanged | tests/test_agent_tools.py L16-L36 | VERIFIED | - |
| #2 01 F2: `agent_tools` takes the name before `(` and subtracts `disallowedTools`; no entry is checked against a pattern | tests/test_agent_tools.py L54-L56 | VERIFIED | - |
| #3 01 F3: the tree test skips a file when `"Bash" in tools` and compares only the literal `Bash` | tests/test_agent_tools.py L98-L99 | VERIFIED | - |
| #4 01 F4: A1 probes x4 and x5 (7 passed), x1 on i2 (1 failed) | logs/audit/2026-11-18-072.md L55, L58, L59, L66-L70 | VERIFIED | - |
| #5 01 F5: 7 agent files, each with a one-line comma `tools:` at L4; no `disallowedTools:`; no Agent, Monitor, PowerShell or `mcp__` | Grep `^(tools\|disallowedTools\|Tools):` in .claude/agents (7 hits) | VERIFIED | - |
| #6 01 F6: dependencies are numpy and pandas, pytest is dev; no yaml import | pyproject.toml L10, L13; Grep `import yaml\|from yaml` (only hit: work/075/01-research.md) | VERIFIED | pyproject also has an optional `webull` extra (L14). It does not change the conclusion: the parser stays stdlib. |
| #7 01 F7: `tools` quote ("comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool ... if omitted.") | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #8 01 F8: `disallowedTools` "Same format as `tools`" | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #9 01 F9: "Subagent files use YAML frontmatter for configuration" | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #10 01 F10 (spec part): "The flow sequence is written as a comma separated list within square brackets." | https://yaml.org/spec/1.2.2/ | VERIFIED | - |
| #11 01 F10 (runtime part): Claude Code reads x4 as a list holding `Bash` and grants it, and strips the quotes in x5 | none (no run) | UNSUPPORTED | Removed. The map does not depend on it: steps 1-2 make x4 and x5 fail the test whatever the runtime does. |
| #12 01 F11: double- and single-quoted flow scalars; "escape sequences are only interpreted in double-quoted scalars"; "All flow scalars can span multiple lines" | https://yaml.org/spec/1.2.2/ | VERIFIED | - |
| #13 01 F12: "Comments must be separated from other tokens by white space characters." | https://yaml.org/spec/1.2.2/ | VERIFIED | - |
| #14 01 F13: the fetched spec text does not state that flow sequences may span lines; the runtime's behaviour is unknown | https://yaml.org/spec/1.2.2/ (R3 re-fetch: no such sentence, only examples) | VERIFIED | Kept as an unknown. The map fails closed: an unclosed `[` is an error. |
| #15 01 F14: `tools: Agent(worker, researcher), Read, Bash` is a documented form; a plain comma split breaks it | https://code.claude.com/docs/en/sub-agents | VERIFIED | The same page says the type list is ignored in a subagent definition (see #44). |
| #16 01 F15: MCP entries `mcp__github__*`, `mcp__github`, `mcp__*`, `mcp__reports__v2__*`, `mcp__reports__run_query` | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #17 01 F16: `Task(...)` still works as an alias of `Agent` since 2.1.63 | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #18 01 F17: "The tool names are the exact strings you use in permission rules, subagent tool lists, and hook matchers." Case handling unknown | https://code.claude.com/docs/en/tools-reference | VERIFIED | The map compares names exactly, so it does not need the case answer: `bash` on r1 fails the allow-list. |
| #19 01 F18: "If every entry in a subagent's `tools` list fails to match a usable tool, the Agent tool usually returns an error naming the entries"; a single unresolved entry is not covered | https://code.claude.com/docs/en/tools-reference L114 | VERIFIED | The sub-agents `tools` row says the same ("If no entry in the list resolves to a tool, the subagent usually fails to launch"). The single-entry case stays unknown, and the map does not depend on it. |
| #20 01 F19: `_field` takes the first `key:` match; which one the runtime uses is unknown | tests/test_agent_tools.py L21-L22 | VERIFIED | - |
| #21 01 F20: Bash "Executes shell commands in your environment"; PowerShell "Executes PowerShell commands natively"; Monitor "Runs a command in the background and feeds each output line back to Claude" | https://code.claude.com/docs/en/tools-reference L24, L39, L41 | VERIFIED | - |
| #22 01 F21: Monitor "uses the same permission rules as Bash"; `Bash(npm run *)` applies to "Bash, Monitor" | https://code.claude.com/docs/en/tools-reference L82, L382 | VERIFIED | - |
| #23 01 F22: "Match `Bash\|PowerShell` in hooks ... matching `Bash` alone is not enough"; PowerShell is opt-in on Linux | https://code.claude.com/docs/en/tools-reference L432, L436 | VERIFIED | - |
| #24 01 F23: `Agent` lets a subagent spawn subagents of its own; general-purpose has every tool available to subagents; background subagents keep Bash, PowerShell and Monitor | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| #25 01 F24: the literal `"Bash" in tools` misses PowerShell, Monitor and Agent/Task on a no-shell agent | tests/test_agent_tools.py L98 | VERIFIED | Closed by the allow-list (D2). |
| #26 01 F25: the five no-shell `python3 scripts/` lines (r1 L19, r2 L22, r3 L20, r3 L24, i1 L18) and their wording | Grep `python3 scripts/` in .claude/agents | VERIFIED | - |
| #27 01 F26: A1's literal pair matches 3 of 5 lines (r3 L20 "The" and r3 L24 "then runs" miss) | logs/audit/2026-11-18-072.md L65; Grep above | VERIFIED | - |
| #28 01 F27: A1's x2 text passes today's substring rule | logs/audit/2026-11-18-072.md L56, L62 | VERIFIED | - |
| #29 01 Numbers: 7 files = 4 no-shell + 3 shell; 7 of 7 in comma form | Grep `^tools:` in .claude/agents | VERIFIED | - |
| #30 01 Numbers: x4 gives 7 tokens; 2 (`[Read`, `Bash]`) are not names; 0 equal `Bash` | R3 trace of the L25 split on the x4 line | VERIFIED | - |
| #31 01 Numbers: the request pattern fails `[Read`, `Bash]`, `Agent(worker`, `researcher)` and 5 of 5 MCP forms | R3 trace of `^[A-Za-z]+(\(.*\))?$` | VERIFIED | `researcher)` fails because the pattern needs `(` right after the letters; the MCP forms fail on `_` and `*`. |
| #32 01 Numbers: the wording regex matches 5 of 5 lines and not x2; A1's pair matches 3 of 5 | R3 trace on the 5 lines in #26 | VERIFIED | - |
| #33 01 Numbers: 5 shell-capable names; 0 of 4 no-shell files list one | #5, #21-#24 | VERIFIED | - |
| #34 01 OQ7: no file overlap with 076-079 | brief.md L3 | VERIFIED | - |
| #35 02 Past logs: A1's x4/x5 probes, P1, the root-cause quote "the parser silently drops any token it does not recognise, so 'could not parse' becomes 'not Bash'"; x2 "optional", "not on its own worth an item" | logs/audit/2026-11-18-072.md L58-L59, L63, L65, L70, L79-L87 | VERIFIED | - |
| #36 02 Past logs: RI-002 near-miss wording; RI-012 L138-L141; A1's 072 audit L64 says RI-012 does not apply to a text lint | logs/recurring-issues.md L25, L138-L141; logs/audit/2026-11-18-072.md L64 | VERIFIED | - |
| #37 02 Past logs: 072 planned "comma string or YAML list" but built only the block `- X` form | work/072/04-build-plan.md L6, L14; logs/audit/2026-11-18-072.md L21 | VERIFIED | - |
| #38 02 Tree: all 4 no-shell files list exactly `Read, Write, Glob, Grep, WebSearch, WebFetch`; no `disallowedTools:` | Grep (#5) | VERIFIED | - |
| #39 02 Language rotation: 073 used German, Korean, Portuguese; 070, 071, 072 and 074 were N/A | logs/research/2026-11-18.md L7-L10; logs/research/2026-11-17.md L5 | VERIFIED | - |
| #40 02 FOR 1: roba 0.7.1 `agent_check.rs` has the comment "// Inline list: `tools: Read, Edit, Write`", `.split(',')` + `.trim()`, no bracket or quote handling, and does not reject unknown entries | https://docs.rs/crate/roba/0.7.1/source/src/agent_check.rs | VERIFIED | R3's fetch adds that an unknown entry ends up in a missing-tools warning. It is still not rejected. |
| #41 02 FOR 1 (Spanish): "como una cadena separada por comas como `Read, Grep, Bash` o una lista YAML"; translation | https://code.claude.com/docs/es/sub-agents.md | VERIFIED | Translation checked against the original: correct. |
| #42 02 FOR 1: both forms appear in the English, Chinese and Spanish docs | en, zh-CN and es sub-agents pages | VERIFIED | zh row: "可以是逗号分隔的字符串（如 `Read, Grep, Bash`）或 YAML 列表". |
| #43 02 FOR 2 (Japanese): "Monitor がコマンドを実行する場合、Bash と同じ権限ルールを使用する..."; translation | https://code.claude.com/docs/ja/tools-reference.md L227 | VERIFIED | In the original, "Bash と同じ権限ルール" is a link. Translation correct. |
| #44 02 FOR 2 (Chinese): in a subagent definition the `Agent(...)` type list is ignored, "括号内的任何类型列表都会被忽略"; translation | https://code.claude.com/docs/zh-CN/sub-agents.md; English equivalent on /en/sub-agents | VERIFIED | Translation correct. EN: "but any type list inside the parentheses is ignored." |
| #45 02 FOR 2: a subset check of the NO_SHELL stems against the 6-tool allow-list catches Bash, `bash`, `Bash]`, `"Bash"`, Monitor, PowerShell, Agent/Task, Skill, `mcp__*` and future tools; "Shell agents (i2, i3, a1) need only the parse check" | R3 trace; tests/test_agent_tools.py L98-L107; logs/audit/2026-11-18-072.md m5 (L53) | Fixed | The list is right: each named entry is outside the 6-name set, so the subset check fails. The second sentence is wrong as a plan: 072's m5 (`disallowedTools: Bash` on i2, which must fail) relies on the existing `"Bash" in tools` / `no_bash == NO_SHELL` checks. Map step 2 keeps those checks and adds the allow-list on top, rather than replacing them. |
| #46 02 FOR 2 (French): "Le champ `tools` est votre frontière d'isolation."; translation | https://www.glukhov.org/fr/ai-devtools/claude-code/claude-code-subagents/ | VERIFIED | The original uses typographic apostrophes. Translation correct. |
| #47 02 FOR 2 (Turkish): "... modelin tartışamayacağı kuraldır: orada olmayan bir araç."; translation | https://agentsroom.dev/tr/blog/read-only-review-agent | VERIFIED | Full sentence: "Makul bir istisnayla karşılaşıp ayakta kalan tek kural, modelin tartışamayacağı kuraldır: orada olmayan bir araç." Translation correct. |
| #48 02 FOR 3 (Chinese): "Claude Code 会忽略无法识别的字段，且不报告错误"; translation | https://code.claude.com/docs/zh-CN/sub-agents.md; EN "Claude Code ignores a field it doesn't recognize without reporting an error" | VERIFIED | Translation correct. |
| #49 02 FOR 3: Claude Code ignores a mis-cased `Tools: Read`, so the agent inherits every tool | en sub-agents: field names "must match the table exactly"; `tools` "Inherits every tool ... if omitted" | VERIFIED | Inference from two documented sentences, not from a run. The map fails closed either way. |
| #50 02 FOR 3: the current `_field` uses an exact `startswith("tools:")`, so `Tools: Read` gives "no tools: line" | tests/test_agent_tools.py L22, L50-L51 | VERIFIED | - |
| #51 02 FOR 3: Claude Code and the test both ignore a misspelled `disallowedtools:` | en sub-agents (#48); tests/test_agent_tools.py L55 | VERIFIED | - |
| #52 02 AGAINST 1: YAML has more forms than R1's (a)-(f): multi-line flow lists, block scalars, anchors, tags, a whole value in quotes, comments | https://yaml.org/spec/1.2.2/ | Fixed | R3 re-checked flow sequences, multi-line flow scalars, quoted scalars and comments (#10, #12, #13). R3 did not re-check anchors, tags or block scalars, so that part rests on R2 alone. The map does not need it: each such form puts a token (`&a ...`, `!!str ...`, `>`, `\|`) into an entry that fails the pattern, which is an error (Self-check S10). |
| #53 02 AGAINST 1: issue titles #60237 and #14580 "suggest the runtime's own array handling has changed between versions" | WebSearch (claudeissues.com titles); page bodies not read | Fixed | The two titles exist (WebSearch, 2026-11-19), but the bodies are unread. "Changed between versions" is UNSUPPORTED and dropped. What is kept: two issues were filed with these titles. Nothing in the map rests on them. |
| #54 02 AGAINST 2 (Russian): "YAML, который не парсится: Claude Code не читает никакие поля из файла, пропускает его и записывает ошибку парсинга в журнал отладки."; translation | https://code.claude.com/docs/ru/sub-agents L343; EN "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." | VERIFIED | Translation correct. |
| #55 02 AGAINST 2 (French): "L'isolation est une liste d'outils autorisés, pas un sandbox."; translation | https://www.glukhov.org/fr/ai-devtools/claude-code/claude-code-subagents/ | VERIFIED | Translation correct. |
| #56 02 AGAINST 2 (Turkish): "bir `bash -c` araç yasak listesinin etrafından dolaşır."; translation | https://agentsroom.dev/tr/blog/read-only-review-agent | VERIFIED | It is a fragment of "Bildiren kişi bunu raporunda söyledi ve haklıydı: bir `bash -c` ...". Translation correct. |
| #57 02 AGAINST 3 and Hole 4: the greedy `(\(.*\))?` "lets `Bash) (x` through" | R3 trace of `^[A-Za-z]+(\(.*\))?$` | Fixed | WRONG example. `Bash) (x` fails that pattern, because after `Bash` the next character is `)`, not `(`. The real greedy hole is two groups in one token: `Bash(a)(b)` and `Bash(a) (b)` pass `\(.*\)` but fail `\([^()]*\)`. The conclusion (use `\([^()]*\)`) stands, and fixture t2 uses the corrected example. |
| #58 02 AGAINST 3: the zh-CN page "cites versions from v2.1.172 to v2.1.296" | https://code.claude.com/docs/zh-CN/sub-agents.md | Fixed | The page also cites 2.1.63 (the Task rename), so the range is 2.1.63 to v2.1.296. The point (many version notes) stands. |
| #59 02 AGAINST 3: a hard-coded shell-name set misses the next command-capable tool | reasoning; tools-reference lists tools gated by recent versions (e.g. EndConversation "Requires Claude Code v2.1.213") | VERIFIED | Supports D2. |
| #60 02 Hole 2: `tools: 'Read, Bash'` splits into `'Read` and `Bash'`, which fail the pattern → error | R3 trace (Self-check S9) | VERIFIED | - |
| #61 02 Hole 7: the ru `tools` row leaves out "comma string or YAML list" | https://code.claude.com/docs/ru/sub-agents L306 | VERIFIED | - |
| #62 01 OQ2: tighten to `\([^()]*\)` "so `Bash) (x` cannot pass" | R3 trace | Fixed | Same wrong example as #57: `Bash) (x` already fails the original pattern. The tightening is still right, because of `Bash(a)(b)`. |

**Totals:** 62 rows checked → **55 VERIFIED as-is**, **6 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- #11 (01 F10, runtime part): "Claude Code reads A1's x4 line as a list holding `Bash` and grants it; YAML strips the quotes in x5." No run supports it. The map does not need it: x4 and x5 fail the test whatever Claude Code does with them.

## Decisions on R1/R2 open points (with reasons)
- **D1 Parser (R1 OQ1 (a)-(f)): adopted, with three additions.** Stdlib only (#6).
  - (1) A line that starts `tools:` or `disallowedTools:` must continue with a space, a tab or the end of the line. Anything else is an error, because YAML reads `tools:Read` as one plain scalar, not a key (secondary source above). Today's `startswith` reads that line as `{Read}`. So a no-shell agent with no real `tools` key, which therefore inherits every tool, would pass the test. This is the RI-002 shape again, found by R3.
  - (2) An empty entry (`Read,,Write`, `tools: ""`, a bare `-` list item) is an error, not skipped, because an empty string does not match the pattern.
  - (3) A `)` with no matching `(`, or a `(` still open at the end of the value, is also an error.
- **D2 Allow-list (R2 FOR 2): adopted, on top of 072's checks (#45).** `NO_SHELL_ALLOWED = {"Read", "Write", "Glob", "Grep", "WebSearch", "WebFetch"}`. Every NO_SHELL stem's parsed set must be a subset of it, by exact name. This makes R1 OQ3 (the shell-name set) and the case question (#18) unnecessary. 072's `"Bash" in tools` and `no_bash == NO_SHELL` checks stay, so 072's m3 and m5 still fail.
- **D3 Entry pattern (R1 OQ2): option (i).** `ENTRY_RE = ^[A-Za-z]+(\([^()]*\))?$`, matched in full, with no MCP form. 0 of 7 files list an MCP entry today. If one is added later, the test fails loudly until the pattern is widened, and that widening is a visible edit in review. Fail closed.
- **D4 Fixtures:** R1 OQ4 cases g-n, plus R2's (`Tools:`, whole value in quotes, `disallowedtools:`), plus R3's (`tools:Read`, `Bash(a)(b)`, empty entry, block scalar `>`, tree-level x4/x5/Monitor/`bash`). All are listed in step 3.
- **D5 Wording regex (R1 OQ5): left out.** The request marks it optional, A1 rated it "not on its own worth an item" (#35), and R2 AGAINST 2 agrees. The substring rule at L104 is unchanged. If the person wants it, it should be a separate item.
- **D6 Duplicate keys (R1 OQ1 (f)): error** for a second `tools:` or a second `disallowedTools:` line, because which line the runtime uses is unknown (#20).
- **D7 Flow lists over several lines (#14) and block scalars: error.** Claude Code's handling is unknown, and this repo uses neither form.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | **tests/test_agent_tools.py parser.** Replace `_field` with `_field(lines, key) -> (found, entries, error)`. (a) Key line: `line == key + ":"` or `line.startswith(key + ": ")` / `key + ":\t"`. A line that starts `key + ":"` followed by any other character → `"<key>: needs a space after the colon (item 075)"`. (b) A second key line → `"duplicate <key>: line (item 075)"`. (c) If the value starts with `[`, it must end with `]` on the same line, else `"unclosed [ in <key>: (item 075)"`. Strip the brackets. (d) Split on commas at paren depth 0. A `)` at depth 0, or depth > 0 at the end → `"unbalanced ( ) in <key>: (item 075)"`. (e) For each entry (comma, flow or block `- X`; a bare `-` is an empty entry): strip whitespace, then strip one matching pair of `"` or `'` around the whole entry. (f) Every entry must full-match `ENTRY_RE = r"^[A-Za-z]+(\([^()]*\))?$"`, else `"unparsed <key>: entry '<x>' (item 075)"`. (g) An empty value with no block items, or `[]`, keeps 072's `found, []`, so `tools` gives `"empty tools: (item 072)"`. An empty `disallowedTools` removes nothing. `agent_tools` returns the first error from `tools`, then from `disallowedTools`. Names are the text before `(`. Update the module docstring: every entry the parser cannot read is an error (item 075). | the frontmatter lines of each file | `(tools set, error or None)` | The parser fixtures (step 3) pass. 072's 6 cases a-f are unchanged and still pass. | 7 of 7 agent files parse with no error, today's tree 2026-11-19 (Grep `^tools:` in .claude/agents: 7 lines, 40 entries, 40 of 40 letters only; 0 `disallowedTools:` lines) |
| 2 | **Allow-list on the no-shell stems.** Add `NO_SHELL_ALLOWED`. Move the tree test's loop into `tree_problems(texts: dict[stem, text]) -> (problems, no_bash)` so fixtures can call it. For a NO_SHELL stem whose parsed set is not a subset of NO_SHELL_ALLOWED, add `"<stem>: tools beyond the no-shell allow-list: <sorted extras> (RULES decision, item 075)"`. Run this check before the `"Bash" in tools` skip. Keep 072's parse-error line, Bash skip, body-line check, `no_bash == NO_SHELL` assert and run-item.md strings unchanged. The real-tree test calls `tree_problems` on `.claude/agents/*.md`. | parsed sets from step 1 | problem list | Tree fixtures n0-n4 (step 3). The real-tree test passes. | 4 of 4 NO_SHELL files ⊆ the allow-list (each lists exactly the 6 names); 3 of 3 shell files list Bash; 5 of 5 no-shell `python3 scripts/` lines name the orchestrator. Today's tree, Grep |
| 3 | **Fixtures.** Parser CASES (expected tools or error): g `tools: [Read, Write, Bash]` → {Read, Write, Bash}; h `tools: [Read, Write]` → {Read, Write}; i1 `tools: Read, "Bash"` → {Read, Bash}; i2 block `- 'Bash'` → {Bash}; j1 `tools: Read, Bash]` → unparsed `Bash]`; j2 `tools: Read, Write # Bash` → unparsed `Write # Bash`; j3 `tools: [Read, Bash` → unclosed [; k `tools: Agent(worker, researcher), Read` → {Agent, Read}; l two `tools:` lines → duplicate; m `tools: Read, Bash` + `disallowedTools: [Bash]` → {Read}; q `Tools: Read` → 072's no-tools-line error; r `tools: 'Read, Bash'` → unparsed `'Read`; s `tools:Read` → needs a space; t1 `tools: Bash) (x` → unbalanced; t2 `tools: Bash(a)(b)` → unparsed `Bash(a)(b)`; u `tools: Read,,Write` → unparsed `''`; v `tools: []` → empty tools; w `tools: Read, Bash` + `disallowedtools: Bash` → {Read, Bash}; x `tools: >` → unparsed `>`. Tree cases via `tree_problems` (the 4 NO_SHELL stems with the 6 tools, the 3 shell stems with `Read, Bash`, empty bodies): n0 baseline → no problems and no_bash == NO_SHELL; n1 r1 = x4's line → exactly one problem, the allow-list problem naming `Bash` (x4 is a valid one-line flow list, so it parses cleanly); n2 r1 = x5's line → the allow-list problem naming `Bash`; n3 r1 `tools: Read, Monitor` → the allow-list problem naming `Monitor`; n4 r1 `tools: Read, bash` → the allow-list problem naming `bash`. Tree cases assert the exact problem text. | step 1-2 functions | pytest cases | Each case asserts the exact error, problem text or set. `pytest tests/test_agent_tools.py` passes. | – |
| 4 | **Probes and mutations (I2 in 05, I3 in 06), on a scratch copy only.** Probes: A1's x4 and x5 lines on r1 → the tree test fails (request "Done looks like"). A1's x1 (i2 flow list with Bash) now passes: a correct parse, and a change from 072's 06. 072's m1-m5 still fail and m6 still passes. Mutations; each must fail at least the named cases: M1 plain comma split restored → g, h, n1 (n1 becomes the parse error `'[Read'`); M2 quote strip removed → i1, i2, n2; M3 ENTRY_RE check removed → j1, j2, t2, x; M4 depth-0 split replaced by a plain split → k; M5 allow-list check removed → n1, n2, n3, n4; M6 duplicate check removed → l; M7 key-separator check removed → s; M8 `[^()]*` back to `.*` → t2. | branch head | pass/fail counts per probe | 05/06 tables record each result. A mutation that leaves every test green is a finding. | – |
| 5 | **Whole suite.** `python3 -m pytest -q` on the branch, plus `python3.11 -m py_compile tests/test_agent_tools.py` (RI-008). | branch head | totals | Passed and skipped counts copied from pytest's last line (RI-006) | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Frontmatter `---` block (step 1) | none, or not closed | `no frontmatter` (072, unchanged). Never "no Bash". |
| `tools:` key (step 1) | no line, or mis-cased (`Tools:`) | `no tools: line (inherits every tool incl. Bash, item 072)`. An error, because Claude Code would grant every tool. |
| `tools:` value (step 1) | empty with no `- X` items, or `[]` | `empty tools: (item 072)`. |
| A single entry (step 1) | empty, unreadable, or outside ENTRY_RE | `unparsed <key>: entry '<x>' (item 075)`. Never dropped, never "not Bash". |
| `disallowedTools:` key (step 1) | absent or misspelled | Removes nothing. This is the documented meaning ("`tools` only: the subagent gets only the listed tools"), not a default. Fixture w pins it. |
| A NO_SHELL stem's file (step 2) | file missing | The stem is not in `no_bash`, so the `no_bash == NO_SHELL` assert fails and names the set. |
| `.claude/agents/*.md` (step 2) | no files | `no agent files under .claude/agents` (072, unchanged). |

## Self-check
Every fixture is traced through the step 1 rules (a)-(g) and the step 2 subset rule. ENTRY_RE = `^[A-Za-z]+(\([^()]*\))?$`, matched in full.

| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| S1 today's tree parses (step 1 feasibility) | every entry on the 7 L4 lines full-matches ENTRY_RE | a1 5 + i1 6 + i2 6 + i3 5 + r1 6 + r2 6 + r3 6 = 40 entries. Each is one of Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Bash: letters only, no parens → 40 of 40 match | PASS |
| S2 allow-list on today's tree | for r1, r2, r3, i1: set ⊆ {Read, Write, Glob, Grep, WebSearch, WebFetch} | each set is exactly those 6 → extras = ∅, 4 of 4 | PASS |
| S3 072 cases a-f unchanged | a: line 0 ≠ `---` → no frontmatter. b: no `tools` key line → no tools line. c: line is `tools:` == key + ":", value empty, the next line `---` is not `- ` → [] → empty. d: block `- Read`, `- Write` → {Read, Write}. e: `Read`, `Bash`; denied `Bash(git push *)` matches (inner `git push *` has no parens), name Bash → {Read}. f: `Bash(git *)` matches → {Read, Bash} | as stated | PASS (6 of 6) |
| S4 g / h | value `[Read, Write, Bash]` starts with `[` and ends with `]` → inner text split at depth 0 → 3 entries, all match | {Read, Write, Bash}; h → {Read, Write} | PASS |
| S5 i1 / i2 | `"Bash"`: the whole entry is wrapped in one matching `"` pair → stripped → `Bash` matches; block `'Bash'` → `Bash` | {Read, Bash}; {Bash} | PASS |
| S6 j1 / j2 / j3 | j1 `Bash]`: `]` is not a letter → no match → error. j2 `Write # Bash` holds spaces and `#` → error. j3 starts with `[`, but the last character `h` ≠ `]` → unclosed | 3 errors | PASS |
| S7 k | depth: `(` → 1; the comma at depth 1 does not split; `)` → 0; the comma at depth 0 splits → `Agent(worker, researcher)`, `Read`. The inner `worker, researcher` has no parens → match. Name before `(` = Agent | {Agent, Read} | PASS |
| S8 l / m | l: a second `tools:` line → duplicate. m: denied `[Bash]` → {Bash}; {Read, Bash} − {Bash} | error; {Read} | PASS |
| S9 q / r | q: `Tools: Read` does not start with `tools:` (case) → not found → no-tools error. r: `'Read, Bash'` splits into `'Read` and ` Bash'`; after the whitespace strip, `'Read` has no closing `'`, so nothing is stripped → no match | error; error on `'Read` (the first failing entry) | PASS |
| S10 s / t1 / t2 / x | s: `tools:Read`: the character after `tools:` is `R` → needs-space error. t1: `Bash) (x`: `)` at depth 0 → unbalanced. t2: `Bash(a)(b)`: depth 1, 0, 1, 0, never below 0 → one entry; `\([^()]*\)` matches `(a)` and `(b)` is left over → no full match → unparsed (the old `\(.*\)` would match `(a)(b)`). x: `>` → no match | 4 errors | PASS |
| S11 u / v / w | u: `Read,,Write` → entries `Read`, ``, `Write`; the empty string does not match (`[A-Za-z]+` needs at least 1 character) → error. v: `[]` → empty inner text → no entries → empty-tools error. w: `disallowedtools` ≠ `disallowedTools` → not found → nothing removed | error; error; {Read, Bash} | PASS |
| S12 n0-n4 tree | n0: 4 stems ⊆ allowed and 3 stems have Bash → problems [] and no_bash = NO_SHELL. n1: x4's `[Read, Write, Glob, Grep, WebSearch, WebFetch, Bash]` is a valid one-line flow list → set = the 6 + Bash → extras {Bash} → allow-list problem. (r1 is then skipped as a Bash file, so no_bash lacks r1 and the set assert also fails in the real-tree test.) n2: x5 `..., WebFetch, "Bash"` → `Bash` after the quote strip → extras {Bash}. n3: extras {Monitor}. n4: `bash` matches ENTRY_RE and ≠ every allowed name → extras {bash} | n1-n4 each give exactly the allow-list problem named in step 3 | PASS |
| S13 request "Done looks like" | an inline list with Bash on a no-shell agent fails; a junk token fails | n1 fails (S12); j1 and j2 fail (S6) | PASS |
| S14 each mutation changes an asserted result | M1 plain split → g gives `[Read`, which fails the pattern → error ≠ expected set; n1 gives a parse-error problem ≠ the allow-list text. M2 → i1 keeps `"Bash"` → no match → error ≠ {Read, Bash}. M3 → j1 returns {Read, Bash]} with no error ≠ expected error. M4 → k gives `Agent(worker` → unbalanced/unparsed ≠ {Agent, Read}. M5 → n3 gives no problem. M6 → l gives no error. M7 → s gives {Read} with no error. M8 → t2 gives {Bash} with no error | each changes at least one asserted result | PASS |

Mismatches found by this Self-check and already fixed in the map above:
- Step 1 Feasibility first said 37 entries. The recount (S1) gives 40.
- Step 3 n1 first expected a parse-error problem. x4's line is a valid one-line flow list, so the new parser reads it cleanly and the expected result is the allow-list problem naming `Bash` (S12). Because n1 asserts the exact text, M1 still changes its result (S14).

check_handoff output (run by the orchestrator 2026-11-19 23:41 UTC, exit 0; must say PASS):
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 62
totals line: 62 rows -> 55 as-is, 6 fixed, 1 removed
PASS
```