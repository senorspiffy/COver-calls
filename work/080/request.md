# Work item 080
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-20

## What we want
The agent-tools drift test (075, tests/test_agent_tools.py, on PR #33) reads an agent file's frontmatter the way a YAML reader does, so a `tools:` line that YAML would not see as a key can never pass as the agent's tool list.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-19-075.md P1: r1's `description:` written as a quoted value spanning several lines, with the `tools:` line inside it → test 42 passed; PyYAML 6.0.3 sees no `tools` key (the agent would inherit every tool, Bash included; Claude Code's own reading not tested).
- Same file: a tab-indented block list passes the test though PyYAML rejects it.
- logs/audit/2026-11-19-075.md P2 / work/075/06 M14: `_is_item` ignoring a bare `-` survives all 42 tests.

## Root cause and prevention guardrail (BUG only)
Root cause: the hand parser reads lines one by one and doesn't track YAML state (open quoted scalar, tab indent), so text that is not a key is read as one (RI-002 pattern: an unreadable value turned into a verdict).
Guardrail: an unclosed quoted value or a tab in frontmatter indentation is an error; fixtures for both plus a bare `-` list item; mutation for each.

## Recurring issue link (RI-#, if any)
RI-002 pattern. Found by A1 before merge; not counted (precedent 069/070).

## Done looks like
Multi-line-quoted, tab-indented and bare `-` fixtures each fail the test; each mutation fails a named test.
