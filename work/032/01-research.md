# 01 Research brief - 032
## Question
Can the 'compiles on the oldest supported Python' check (027) run as a test instead of a manual I3 step?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- pyproject: requires-python >= 3.10 [pyproject.toml]
- i3 step 2 runs `python3.11 -m py_compile` by hand [.claude/agents/i3-verifier.md]
- This machine has /usr/bin/python3.11, no python3.10 [ls /usr/bin/python3*]
- The 027 token test covers only same-quote nested f-strings [tests/test_safety.py]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first.
## Numbers used (show the math)
Tracked .py files compiled with python3.11 on 2026-11-01: all, 0 errors.
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
