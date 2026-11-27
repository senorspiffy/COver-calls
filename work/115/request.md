# Work item 115
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-27
## What we want
The five documented frontmatter shapes that still return a tool set while both PyYAML loaders raise get a named error.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-27-111.md F-3 (PR #40) table: flow item `- [a]` / `  b`, nc1 `- "a"` / `  b`, d6a `a:` / `  b` / `  c: d`, and the other 04 C2 "Known passes" shapes: test gives {Read, Write}, SafeLoader and CSafeLoader raise. Existed before 111. No real agent file has these lines.
## Root cause and prevention guardrail (BUG only)
Root cause: the line parser has no rule for a scalar that cannot continue (quoted, flow, comment-ended) or a key after a continued plain scalar (RI-002 pattern).
Guardrail: refuse each shape with a named error; fixture + PyYAML probe per shape; one mutant per new check; docstring "Known passes" list emptied or each left entry justified.
## Recurring issue link (RI-#, if any)
RI-002 (existed before 111; found by A1, not counted).
## Done looks like
Each of the five shapes gives a named error matching both loaders; mutants killed; real files pass.
