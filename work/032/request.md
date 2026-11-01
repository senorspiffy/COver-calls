# Work item 032
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-01

## What we want
Run the "compiles on the oldest supported Python" check as a test instead of a manual I3 step.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `pyproject.toml`: `requires-python = ">=3.10"`.
- `.claude/agents/i3-verifier.md` step 2: "If `python3.11` exists, run `python3.11 -m py_compile` on every changed `.py`" (item 027). It is a manual step; nothing reminds a fix made outside the pipeline (the RI-008 case) to do it.
- `tests/test_safety.py::test_fstrings_parse_on_python_310` catches one known 3.12-only pattern (same-quote nested f-strings), not others (e.g. `type X = ...`, PEP 695 generics, `except*` is fine but `ExceptionGroup` use is not).
- This machine has `/usr/bin/python3.11`; A1 ran `python3.11 -m py_compile` on every tracked `.py` on 2026-11-01: no errors.

## Done looks like
A test that, when `python3.10` or `python3.11` is on PATH, compiles every tracked `ccbot/`, `scripts/`, `tests/` `.py` with it and fails on any error; it skips with a reason when neither exists. I3's manual step points at the test.
