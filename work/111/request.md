# Work item 111
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-26
## What we want
Agent-tools frontmatter test fails closed when a scalar list item is followed by a key at its content column (and on the documented D3/er1 shapes), since both YAML loaders reject these files.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-26-106.md F-1/F-2 (PR #39): `hooks:` / `- a` / `  b: c` / `tools: Read` and `hooks:` / `  - a` / `    b: c` / `tools: Read` return ({Read}, None) on a522c5d and ad16eb0; SafeLoader and CSafeLoader both raise ScannerError. Not in the docstring's "Not checked" list. D3/er1 (work/106/07 point 4) are documented but also return a tool set while both loaders raise. F-3: docstring version list should read "6.0.1, 6.0.3 and 6.0.4". No real agent file has these lines.
## Root cause and prevention guardrail (BUG only)
Root cause: the line parser accepts a mapping key after a scalar item at the item's content column; YAML forbids it (RI-002 pattern: unreadable file turned into a verdict).
Guardrail: refuse the shape with a named error (or VALUE); fixtures for both indent forms plus D3/er1; PyYAML probe per fixture (pure and libyaml where available); one mutation per new check fails a named fixture; real agent files still pass.
## Recurring issue link (RI-#, if any)
RI-002. Found by A1 before merge (existed on main before 106); near miss, not counted.
## Done looks like
Each shape gives a named error or a documented pass that matches YAML; mutants fail named fixtures; docstring version list fixed.
