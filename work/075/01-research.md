# 01 Research brief - 075

Type BUG, Scope FULL, opened by A1, 2026-11-19. Branch daily-fixes/2026-11-19 (read only). R1 has no shell (tools: Read, Write, Glob, Grep, WebSearch, WebFetch), so every repo fact below comes from reading files, cited as path:line. Nothing below is a measured test run; A1's probe results are quoted from logs/audit/2026-11-18-072.md.

## Question
tests/test_agent_tools.py (072) parses each agent file's `tools:` / `disallowedTools:` frontmatter with a comma split and keeps any token it gets. An inline list `tools: [Read, ..., Bash]` yields the token `Bash]`, which is not `Bash`, so a no-shell agent given Bash passes all 7 tests (A1 probe x4). Which `tools:` forms does Claude Code accept, how should the test read each of them, and what must make it fail (error, never "not Bash")?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The bug, as it stands in the repo
F1. `_field` returns the comma-split value of the first line starting with `key:`, or the following `- X` lines when the value is empty; it keeps every non-empty token unchanged (tests/test_agent_tools.py L16-L36).
F2. `agent_tools` takes the name before `(` of each entry and subtracts `disallowedTools` the same way; no entry is checked against any pattern (tests/test_agent_tools.py L54-L56).
F3. The tree test skips a file when `"Bash" in tools` and otherwise checks body lines; it compares only the literal string `Bash` (tests/test_agent_tools.py L98-L99).
F4. A1 probes on e54a77e: x4 r1 `tools: [Read, Write, Glob, Grep, WebSearch, WebFetch, Bash]` → 7 passed (Bash granted, not detected); x5 r1 `..., WebFetch, "Bash"` → 7 passed; x1 the same flow list on i2 → 1 failed only because i2's body lines then count as no-shell lines (logs/audit/2026-11-18-072.md L55-L59, L66-L70).
F5. All 7 agent files today use a one-line comma `tools:` value, and none lists Agent, Monitor, PowerShell or an `mcp__` name (Grep `^(tools|disallowedTools):` in .claude/agents: 7 hits, each L4; no `disallowedTools:` line).
F6. The project declares only numpy and pandas as dependencies (pytest as dev); nothing in the repo imports yaml (pyproject.toml L10, L13; Grep `import yaml|from yaml`: 0 files). A YAML library is therefore not available to the test without a new dependency; the parser stays stdlib.

### What Claude Code accepts in `tools:` (official docs)
F7. `tools` lists "Tools the subagent can use, as a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents]
F8. `disallowedTools`: "Tools to deny, removed from inherited or specified list. Same format as `tools`." [https://code.claude.com/docs/en/sub-agents]
F9. "Subagent files use YAML frontmatter for configuration" between `---` markers. [https://code.claude.com/docs/en/sub-agents]
F10. Inference from F7 + F9 (not tested in Claude Code): the frontmatter is YAML, and `[Read, Bash]` is YAML list syntax, so Claude Code reads A1's x4 line as a list holding `Bash` and grants it; YAML also strips the quotes in `"Bash"` (x5). The YAML spec: "The flow sequence is written as a comma separated list within square brackets." [https://yaml.org/spec/1.2.2/] That Claude Code grants Bash from x4/x5 is UNVERIFIED by a run.
F11. A YAML flow scalar may be double- or single-quoted; "escape sequences are only interpreted in double-quoted scalars", and "All flow scalars can span multiple lines". [https://yaml.org/spec/1.2.2/]
F12. YAML comments: "Comments must be separated from other tokens by white space characters." So `tools: Read, Write # Bash` is `Read, Write` to a YAML reader. [https://yaml.org/spec/1.2.2/]
F13. Whether a flow list for `tools` may be split over several frontmatter lines in Claude Code is UNVERIFIED (the spec text fetched did not state it for sequences; F11 says flow scalars may span lines).
F14. A comma inside a specifier is a documented form: `tools: Agent(worker, researcher), Read, Bash`. [https://code.claude.com/docs/en/sub-agents] A plain comma split (F1) breaks this entry into `Agent(worker` and `researcher)`.
F15. MCP entries are documented in `tools`/`disallowedTools`: `mcp__github__*`, `mcp__github`, `mcp__*`, `mcp__reports__v2__*`, `mcp__reports__run_query`. [https://code.claude.com/docs/en/sub-agents] None of these matches the request's proposed pattern `^[A-Za-z]+(\(.*\))?$` (underscores, `*`).
F16. `Task(...)` is a still-working alias of `Agent(...)` since v2.1.63. [https://code.claude.com/docs/en/sub-agents]
F17. "The tool names are the exact strings you use in permission rules, subagent tool lists, and hook matchers." [https://code.claude.com/docs/en/tools-reference] Whether Claude Code resolves a differently cased name (`bash`) is UNVERIFIED.
F18. "If every entry in a subagent's `tools` list fails to match a usable tool, the Agent tool usually returns an error naming the entries". [https://code.claude.com/docs/en/tools-reference] What Claude Code does with a single unresolved entry among valid ones is not stated in the text fetched: UNVERIFIED (the linked errors-page section "Agent would be spawned with zero tools" could not be read; WebFetch returned other parts of the page).
F19. Duplicate `tools:` keys: `_field` takes the first match (tests/test_agent_tools.py L21-L22). Which one Claude Code uses is UNVERIFIED.

### Bash is not the only way to run a command (official docs)
F20. Tools table: `Bash` "Executes shell commands in your environment"; `PowerShell` "Executes PowerShell commands natively"; `Monitor` "Runs a command in the background and feeds each output line back to Claude". [https://code.claude.com/docs/en/tools-reference]
F21. "When Monitor runs a command, it uses the same permission rules as Bash"; the rule format `Bash(npm run *)` "Applies to: Bash, Monitor". [https://code.claude.com/docs/en/tools-reference]
F22. "Match `Bash|PowerShell` in hooks that inspect shell commands; ... matching `Bash` alone is not enough." PowerShell is opt-in on Linux. [https://code.claude.com/docs/en/tools-reference]
F23. `Agent` in a subagent's `tools` "lets that subagent spawn subagents of its own while the depth limit allows it"; the built-in general-purpose subagent has "every tool available to subagents"; Bash, PowerShell and Monitor stay in a background subagent's tool set. [https://code.claude.com/docs/en/sub-agents] So `Agent` (or `Task`) on a no-shell agent is an indirect shell (R1's reasoning from these three quotes).
F24. Consequence for the test: F3's literal `"Bash" in tools` misses `PowerShell`, `Monitor`, `Agent`/`Task` on a no-shell agent, the same "unrecognised → not Bash" shape as the request (RI-002). Not in the request's evidence; in scope only if I1 agrees.

### Wording check (request's optional part)
F25. The five no-shell lines holding `python3 scripts/` today say: r1 L19 "the orchestrator runs"; r2 L22 "the orchestrator copies"; r3 L20 "The orchestrator runs"; r3 L24 "The orchestrator then runs"; i1 L18 "the orchestrator copies" (Grep `python3 scripts/` in .claude/agents).
F26. A1's suggested literal strings ("the orchestrator runs" / "the orchestrator copies", case-sensitive) match 3 of these 5 lines; r3 L20 ("The") and r3 L24 ("then runs") would fail (logs/audit/2026-11-18-072.md L65; F25).
F27. A1's x2 text "Run `python3 scripts/check_handoff.py <ID>` yourself; do not wait for the orchestrator." passes today's substring rule (logs/audit/2026-11-18-072.md L56, L62).

## Numbers used (show the math)
- Agent files 7; comma-form `tools:` 7 of 7; no-shell 4 (r1, r2, r3, i1) + shell 3 (i2, i3, a1) = 7 (F5).
- x4 tokens under the current split: `[Read`, `Write`, `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Bash]` = 7 tokens; 2 of 7 (`[Read`, `Bash]`) are not tool names; 0 equal `Bash`, so Bash is not seen.
- Proposed pattern `^[A-Za-z]+(\(.*\))?$` on x4 tokens: `[Read` fails, `Bash]` fails → error (good). On F14 `Agent(worker`, `researcher)`: both fail → error on a documented form (false error unless the split is paren-aware). On F15 MCP names: 5 of 5 fail.
- Wording regex `\b[Tt]he orchestrator (then )?(runs|copies)\b` on F25 lines: r1 yes, r2 yes, r3 L20 yes, r3 L24 yes, i1 yes = 5 of 5; on x2 text ("wait for the orchestrator.") no match → fails. A1's literal pair: 3 of 5 (F26).
- Shell-capable names per F20-F23: Bash, PowerShell, Monitor, Agent, Task = 5; today's 4 no-shell files list 0 of them (F5).

## Fit for a ~$3k account
Process/test item. It changes no strategy rule, trade, price, premium, dividend, tax or liquidity input, so the $3k limits don't apply. It keeps the research agents (which read untrusted web text) without a shell, which protects the machine that runs the bot. Nothing connects to a broker.

## Open questions
1. Parser shape for R2/R3/I1 (stdlib, F6). Proposal: one splitter for all three forms. (a) value starts with `[`: it must end with `]` on the same line, else error (multi-line flow list is UNVERIFIED in Claude Code, F13, so fail closed); strip the brackets. (b) split on commas at paren depth 0 only (F14). (c) strip surrounding whitespace, then one pair of matching `"` or `'` (F10, F11), for flow, comma and block `- X` entries alike. (d) every entry must match the allowed pattern, else error `unparsed tools: entry '<x>' (item 075)`; same for `disallowedTools`. (e) `[]`, or a list that is empty after parsing → the existing "empty tools:" error. (f) more than one `tools:` (or `disallowedTools:`) line → error (F19).
2. Allowed-entry pattern. The request's `^[A-Za-z]+(\(.*\))?$` rejects every documented MCP form (F15). Options: (i) keep it and accept that adding an MCP tool to any agent later fails the test until the pattern is widened (fail closed, visible); (ii) add `mcp__[A-Za-z0-9_-]+(__\*)?|mcp__\*` (allowed MCP server-name characters UNVERIFIED). Also tighten `(.*)` to `\([^()]*\)` so `Bash) (x` cannot pass. R2/R3/I1 decide.
3. Shell set (F20-F24). Should the test count `PowerShell`, `Monitor`, `Agent` and `Task` as shell-capable, so any of them on r1/r2/r3/i1 fails the set assert like Bash does? Compare names case-insensitively for this set (F17 case handling UNVERIFIED), so `bash` cannot slip through. Today 0 of 4 no-shell files list one (F5), so the suite stays green.
4. Fixture cases (request: inline list with Bash, quoted names, junk token). Proposed: g `[Read, Write, Bash]` → Bash present; h `[Read, Write]` → no Bash, no error; i `Read, "Bash"` and block `- 'Bash'` → Bash present; j junk: `Bash]`, `Read, Write # Bash`, unclosed `[Read, Bash` → error each; k `Agent(worker, researcher), Read` → {Agent, Read}, no error; l two `tools:` lines → error; m `disallowedTools: [Bash]` with `tools: Read, Bash` → Bash removed; plus a tree-level probe: x4's line on a scratch r1 → test fails. If 3 is adopted: n `tools: Read, Monitor` on a no-shell fixture → counted as shell.
5. Optional wording tightening (request, F25-F27): use the regex above (5 of 5 current lines pass, x2 fails), not A1's literal pair (3 of 5). Still a text lint: "Run it yourself; the orchestrator runs nothing" would pass. Worth it, or leave for later?
6. Mutations for 05/06 (request "m-probes"): restore the plain comma split → g and j fail; drop the quote strip → i fails; drop the pattern check → j fails; drop the depth-0 split → k fails; (if 3) shell set back to `{"Bash"}` → n fails.
7. Order: 075 is first in today's chain (brief). 076, 077, 079 change scripts/check_pipeline.py and 078 scripts/probe_guardrails.py; none of them touches tests/test_agent_tools.py per the brief, so no file overlap is known. Not checked against their plans (they don't exist yet).
