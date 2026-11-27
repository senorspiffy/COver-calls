# Work item 114
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-27
## What we want
Every sub-condition of 111's new frontmatter structure checks has a fixture that fails when it is broken, plus negatives on valid YAML.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-27-111.md F-1/F-2 (PR #40): mutants I3b (drop `not sb` in R-A), I3c (`dash[-1]` -> `dash[0]`) and B5 (`seq` kind set only at the item's own indent) survive; each turns an error into a tool set on files both PyYAML loaders reject. I3e, B1 (drop `not op`), B2 (`dash[-1] + 1`) survive for lack of negatives.
## Root cause and prevention guardrail (BUG only)
Root cause: mutants were planned one per rule, not one per sub-condition of a compound check (RI-002 pattern: unreadable file turned into a verdict).
Guardrail: fixtures `- |` / `  x` / ` b` -> INDENT(5), `- - a` / `  b` -> SEQ_LEVEL(4); negatives `a:` / `  b` / `  - x`, `hooks:` / `-` / `  b: c`, `hooks:` / `- a` / ` b` (PyYAML probe each, pure and libyaml); one mutant per sub-condition, each killed by a named fixture.
## Recurring issue link (RI-#, if any)
RI-002 (near miss, found before merge, not counted).
## Done looks like
I3b, I3c, B5, I3e, B1, B2 each fail a named fixture; real agent files still pass.
