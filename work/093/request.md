# Work item 093
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
A person's `Waived: 01 02 03 04` on an item numbered 090 or later does not make LOG BATCH report a false INCOMPLETE.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-090.md F1 and work/090/06 follow-up A (PR #36): such an item shows `LOG BATCH not computable: no line before I2 (item 090)`; tests/test_pipeline_check.py `test_batch_no_line_before_i2_strict_from_090[990]` pins it. Precedent: item 024 had that waiver.
## Root cause and prevention guardrail (BUG only)
Root cause: 090's rule assumes a log line before I2 always exists; waivers were not in R3's map.
Guardrail: excuse that reason only when every step before I2 is waived by the person (`Waived: ... (person, <date>: ...)`); decide whether the per-round bound applies; flip the [990] fixture; add a non-person waiver fixture that stays INCOMPLETE.
## Recurring issue link (RI-#, if any)
RI-010 family. Near miss, not counted.
## Done looks like
Person-waived item passes; other waivers stay INCOMPLETE; mutation fails a named test.
