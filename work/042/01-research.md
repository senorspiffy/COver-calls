# 01 Research brief - 042
## Question
Can `check_pipeline.py` accept FAST only with the person's who/date, and stop counting an `A1 result: FAIL` item as complete?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `read_request` matches `Scope: (FULL|RESEARCH ONLY|FAST)` with no who-field [scripts/check_pipeline.py read_request]
- a probe item with `Scope: FAST (I2, 2026-11-04)` shows complete [A1 probe 2026-11-04]
- run-item: `Scope: FAST (person, <date>)`; nobody else may shorten the pipeline [.claude/commands/run-item.md]
- `classify` checks `^A1 result:` exists, not its verdict [scripts/check_pipeline.py classify]
- 040's request line is bare `Scope: FAST`; the person's decision is dated 2026-11-03 in the same file [work/040/request.md]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-002, RI-007, RI-009, RI-010).
## Numbers used (show the math)
FAST items today: 1 (040). A1 FAIL lines today: 1 (040, 2026-11-04).
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
