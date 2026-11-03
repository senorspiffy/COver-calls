# Work item 030
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
Stop tracking the 36 compiled `__pycache__/*.pyc` files. `.gitignore` already lists `__pycache__/`, but the files were committed in 5e46bef, so every test run changes them and they show up in `git diff` and `git status`.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
A1, 2026-10-31: `git ls-files | grep -c pycache` → 36; first added in 5e46bef. After one `pytest` run, `git diff --stat` lists 30 changed `.pyc` files next to the 2 real changes.

## Done looks like
`git rm --cached` on them; `git ls-files | grep -c pycache` → 0; a test fails if any tracked path contains `__pycache__`.
