# 01 Research brief - 027
## Question
Does every script run on Python 3.10/3.11, as pyproject declares?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- pyproject: requires-python = '>=3.10' [pyproject.toml]
- Same-quote nesting inside f-strings is new in 3.12 [https://peps.python.org/pep-0701/]
- `python3.11 scripts/check_handoff.py 001` → SyntaxError at L49 (A1, 2026-10-31)
- All other .py compile under 3.11 (A1, py_compile)

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-008 occ 1).
## Numbers used (show the math)
1 bad line of all .py files in ccbot/, scripts/, tests/.
## Fit for a ~$3k account
One-line fix and one test.
## Open questions
None.
