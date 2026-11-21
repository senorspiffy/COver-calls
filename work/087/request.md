# Work item 087
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-21
## What we want
The agent-tools test (tests/test_agent_tools.py, 075/080) never passes a frontmatter line whose value YAML reads as something that swallows a later `tools:` line.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-20-080.md F1: `description: &d "...` / `tools: ...` / `end"` → 59 passed; same with `!!str "`, `!!str '`, `&a !!str "`, `- &a "`. PyYAML sees no `tools` key.
- Same report F3: `description: [a,` / `tools: Read, Write` / `]` → test reads `{'Read','Write'}`; PyYAML sees no `tools` key. `tools:\tRead` (p11, kept positive) gives PyYAML ScannerError.
- F2: removing `(?:-[ ]+)*` from QUOTE_START_RE survives all 59 tests.
## Root cause and prevention guardrail (BUG only)
Root cause: QUOTE_START_RE expects the quote right after `key: `/`- `; YAML allows anchors/tags before it, and open flow collections (`[`, `{`) span lines too (RI-002 pattern: unreadable value turned into a verdict).
Guardrail: allow `(?:[&!]\S*[ \t]+)*` before the quote or fail closed on `&`/`!`/`*` values; open `[`/`{` on any key is an error; decide p11 from the runtime reader or fail closed; fixtures (parser + tree) and a mutation for each; add the `- "x,` block-list fixture for F2.
## Recurring issue link (RI-#, if any)
RI-002 pattern. Found by A1 before merge; near miss, not counted (precedent 069/070).
## Done looks like
Each shape above fails the test with a named error; each mutation fails a named fixture.
