# 01 Research brief - 045
## Question
How can a log line be tied to the moment its step ran, in its agent's format, so a batch typed at the end fails a check?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- 041–044's 12 lines all read `23:10` [logs/research/2026-11-04.md, logs/implementation/2026-11-04.md]
- They were added in a975744, committed 2026-11-04T22:24:41+00:00 [`git log -1 --format=%cI a975744`]
- I1/I2 lines use `see 04` / `see 05` instead of the agent's fields [same files; .claude/agents/i1-reviewer.md, i2-builder.md]
- R1–I1 had no lines when I2 ran [work/043/06-verification.md "Repo run before the 041–044 log lines were written"]
- `incomplete()` matches only `\|\s*<agent>\s*\|\s*<ID>\s*\|` [scripts/check_pipeline.py L126–143]
- `git blame --line-porcelain` gives `committer-time <unix seconds>` for every line of a committed file [https://git-scm.com/docs/git-blame#_the_porcelain_format]
- The six formats: R1 `brief written | <n>`, R2 `3 for / 3 against | languages: <list>`, R3 `<n> verified, <n> fixed, <n> removed | <READY/BLOCKED>` (logs use `as-is` for verified, e.g. 2026-11-04), I1 `<verdict> | <n> files planned`, I2 `<files changed> | tests <pass>/<total>`, I3 `<PASS/FAIL> | sent to audit: <yes/no>` [.claude/agents/*.md]

Internal item: read `logs/recurring-issues.md` first (RI-002, RI-007, RI-009, RI-010).
## Numbers used (show the math)
22:24:41 to 23:10 = 45 min 19 s; the lines are timed after their commit. First item checked: 045 (041–044 are the occurrence; their history is kept, not rewritten).
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
