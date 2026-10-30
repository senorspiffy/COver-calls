# Work item 012
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Compute the counts in log lines with a command instead of by hand, and define "sources count".

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `logs/implementation/2026-10-30.md` 18:58 and 05 L7 say "48 new" files. The listed breakdown (ccbot 19, tests 15, config 1, data/sample 6, scripts 1, reports 2, pyproject, .gitignore, .env.example) adds up to **47**, and `git status --short -uall` (excluding work/, logs/, caches) shows 47 `??` + 1 ` M` (README.md) = 48 lines.
- `logs/research/2026-10-30.md` 17:21 R1 001 "27" sources. `work/001/01-research.md` has 29 unique URLs. The count is not reproducible because "sources" is undefined.

## Done looks like
I2 instructions give the commands: new = `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` (47 today), changed = `… | grep -c '^ M'` (1). R1 instructions define sources = unique URLs (`grep -oE 'https?://…' | sort -u | wc -l`).
