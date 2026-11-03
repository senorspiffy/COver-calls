# 01 Research brief - 031
## Question
Can `check_pipeline.py` be made to enforce run-item's rule that R3 (03) and I3 (06) are never skipped, while keeping the person's after-the-fact waivers?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- run-item.md: 'R3's fact check and I3's verification never are [skipped]. Nobody else may shorten the pipeline.' [.claude/commands/run-item.md L10]
- `read_request` takes every `\d\d` on the Waived line; `classify` drops them from `need` with no check of step or author [scripts/check_pipeline.py]
- Probe: A1-written `Waived: 03 06` on a FULL item with no 03/06 → `complete`, exit 0 [A1, 2026-11-01, work/031/request.md]
- Only 023 (02, by A1) and 024 (01–04, by A1) carry Waived lines; PR #6 asked the person to approve both and senorspiffy merged it 2026-10-31 22:28 UTC [PR #6]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first.
## Numbers used (show the math)
Waived lines in work/: 2 (grep '^Waived:' work/*/request.md). Lines waiving 03 or 06: 1 (024). After the fix with who=person on 024: 0 SKIPPED.
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
