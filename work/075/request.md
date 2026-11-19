# Work item 075
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-19

## What we want
The agent-tools drift test (072, tests/test_agent_tools.py, on PR #32) reads every `tools:` form the Claude Code docs allow, and errors on any entry it can't parse, so a no-shell agent can never get Bash unnoticed.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-18-072.md (A1, probe x4): r1-researcher.md with `tools: [Read, Write, Glob, Grep, WebSearch, WebFetch, Bash]` passes all 7 tests. The parser keeps the token `Bash]` and doesn't count it as Bash.
- Today all 7 agent files use the comma form, so nothing shipped is affected.

## Root cause and prevention guardrail (BUG only)
Root cause: the parser tolerates tokens it doesn't recognise instead of rejecting them (an unknown value is treated as "not Bash", the RI-002 pattern).
Guardrail: parse the inline `[...]` list and quotes; any `tools:`/`disallowedTools:` entry not matching `^[A-Za-z]+(\(.*\))?$` is an error. Fixture cases for inline list with Bash, quoted names, and junk token. Optional: stricter wording check (a line naming the orchestrator as the runner, not just containing the word).

## Recurring issue link (RI-#, if any)
RI-002 pattern. Caught by A1 before merge, so not counted as an occurrence (same precedent as 069/070 on 2026-11-18).

## Done looks like
Inline-list fixture with Bash on a no-shell agent fails the test; junk token fails; m-probes recorded in 05/06.
