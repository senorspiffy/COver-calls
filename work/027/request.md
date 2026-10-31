# Work item 027
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
`scripts/check_handoff.py` does not run on Python 3.10 or 3.11, but `pyproject.toml` says `requires-python = ">=3.10"`. Fix it and stop 3.12-only syntax from coming back.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `scripts/check_handoff.py` L49 (from commit d994307): `print(f"sources count ...: {len(unique_urls(research.read_text(encoding="utf-8")))}")`. Double quotes inside a double-quoted f-string are allowed only from Python 3.12 (PEP 701).
- A1, 2026-10-31: `python3.11 scripts/check_handoff.py 001` → `SyntaxError: f-string: unmatched '('`. `python3.11 -m py_compile` on every other `.py` in ccbot/, scripts/, tests/ passes.
- This script is the RI-005/RI-006 guardrail that R1, R3, I3 and A1 must run, so on 3.10/3.11 the guardrail itself crashes.

## Root cause and prevention guardrail (BUG only)
Root cause: the suite only runs on whatever Python the machine has (3.13 here), and nothing checks the minimum version the project declares. The UTF-8 edit was mechanical and was not verified (see 026).
Guardrail: a test that tokenizes every `.py` in ccbot/, scripts/ and tests/ and fails if any f-string's replacement field contains a string using the same quote as the f-string itself. Under 3.10/3.11 the file would fail to compile anyway, so the test is effective on every version. I3 also runs `python3.11 -m py_compile` when it is available.

## Recurring issue link (RI-#, if any)
RI-008 (new, occurrence 1)

## Done looks like
`python3.11 scripts/check_handoff.py 001` prints PASS; the new test fails on the old line and passes on the fix.
