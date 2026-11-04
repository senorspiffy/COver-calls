# Work item 042
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-04

## What we want
`scripts/check_pipeline.py` accepts two lines by their presence, not their content:
1. Any `Scope: FAST` line lets an item skip R2 and I1, whoever wrote it. run-item.md says the line is `Scope: FAST (person, <date>)` and "Nobody else may shorten the pipeline".
2. Any `A1 result:` line makes an item complete, including `A1 result: FAIL`.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/040/request.md` L3: `Scope: FAST` (no who or date). The person's choice is only in an HTML comment below it. `check_pipeline.py` → `040: awaiting A1 (FAST)`.
- A1 probe 2026-11-04 (scratch worktree of daily-fixes/2026-11-03 merged with main): a temp item with `Scope: FAST (I2, 2026-11-04)`, `Opened by: I2` and files 01 03 05 06 07 → `999: complete (FAST)`. Same with bare `Scope: FAST`.
- `read_request`: `re.search(r"^Scope:\s*(FULL|RESEARCH ONLY|FAST)\b", ...)` reads no who-field. `classify`: `re.search(r"^A1 result:", ...)` reads no verdict.
- Today A1 records `A1 result: FAIL` for 040 (this audit); without a fix the check prints `040: complete (FAST)`.

## Root cause and prevention guardrail (BUG only)
Root cause: 031 added a who-check for `Waived:` lines only. FAST is the other way to shorten the pipeline and got no such check; 035 checked that the A1 line exists, not what it says.
Guardrail: `Scope: FAST` counts only as `FAST (person, YYYY-MM-DD)`; any other FAST line → SKIPPED "FAST needs (person, <date>)". The last `A1 result:` line decides: FAIL → status `A1 FAIL` and an `A1 FAIL:` summary line (exit 1) until a later PASS line. Tests for both; 040's request line gets its who/date from the person's recorded decision (2026-11-03).

## Recurring issue link (RI-#, if any)
RI-007 (guardrail gap, like 031; no work was used without the person's approval).

## Done looks like
The probe item shows SKIPPED; an item whose last A1 line is FAIL shows `A1 FAIL`; 040 shows `Scope: FAST (person, 2026-11-03)`.
