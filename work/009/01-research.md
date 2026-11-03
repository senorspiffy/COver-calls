# 01 Research brief - 009
## Question
Can the PBO n/a line name the condition that actually failed?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `pbo_cscv` returns NaN for T < 8, N < 2, or a non-finite R, with one shared report text [ccbot/walkforward.py, ccbot/report.py]
- 002/06 Re-verification 2 notes the text can point at the wrong cause [work/002/06-verification.md]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (no linked entry).
## Numbers used (show the math)
Short CSV: T = 0 months, N = 8 configs → only the months condition fails.
## Fit for a ~$3k account
Report wording; no trading change.
## Open questions
None.
