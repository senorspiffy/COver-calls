# Work item 096
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
The agent-tools frontmatter test fails closed on any column-0 line that YAML would reject (no `key:`), and its fixtures are valid YAML where they claim to be.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-087.md N1 and work/087/06 round 2 note N1 (PR #36): column-0 `foo` (also as last line) and column-0 `- a` return a tool set; PyYAML 6.0.3 rejects the whole frontmatter, so `tools:` is lost. q30 (`...x` / `---x`) is a ScannerError in PyYAML though 04 calls it valid. No real agent file has such a line.
## Root cause and prevention guardrail (BUG only)
Root cause: the hand parser deny-lists bad shapes instead of allowing known line shapes (RI-002 pattern: unreadable value turned into a verdict).
Guardrail: column-0 line that is not blank, `#...` or `key:` → named error; fixtures + mutation; swap q30 for `...x: y` / `---x: z` (still kills M41).
## Recurring issue link (RI-#, if any)
RI-002. Found by A1 before merge; near miss, not counted.
## Done looks like
Each shape fails with a named error; mutation fails named fixtures; real agent files still pass.
