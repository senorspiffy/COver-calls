# 01 Research brief - 035
## Question
Can `awaiting A1` cover every unaudited item, not just items with a request dated 2026-10-31 or later?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `A1_RESULT_FROM = dt.date(2026, 10, 31)` compared with the request Date [scripts/check_pipeline.py, PR #8]
- 009–016 are dated 2026-10-30, built 2026-10-31 in PR #7, and have no `A1 result:` line [work/0{09..16}/07-audit-task.md on PR #7]
- Items with 07 and no A1 line on main + PR #8: 002 003 017 018 019 020 021 022 [A1 grep, 2026-11-02]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-007, RI-009).
## Numbers used (show the math)
Pre-033 list: 8 items. Scratch merge of PR #7 before the fix: 0 awaiting A1; after: 8 (009–016).
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
