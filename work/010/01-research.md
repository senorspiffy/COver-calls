# 01 Research brief - 010
## Question
Should one-config variants show their held-out CAGR on short data?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `chosen_h = select(yearly, pre) if pre else None` applies to every variant [ccbot/walkforward.py]
- V0–V3 and V5 have one config each; V4 has three θ configs [ccbot/variants.py, `expand`]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (no linked entry).
## Numbers used (show the math)
Short 2025 CSV: V0 held-out CAGR −1.94% (was n/a).
## Fit for a ~$3k account
Report change; no trading change.
## Open questions
None.
