# 06 Verification - <ID>
Verdict: PASS | FAIL (round <n>; earlier rounds: <verdicts>)
<!-- On every re-verification, update this line first: it must show the latest round. -->
## I1 audit (plan vs research)
## I2 audit (build vs plan)
## Tests re-run (output)
## Real-data effect (diff_reports output, pasted)
<!-- Required when the item changes ccbot/realtest.py or a module/file it reads (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py: ccbot/realtest.py, costs.py, expiries.py, config.py, pricing.py, config/default.json, tickers.json, holidays.json, data/real/; from item 070 check_pipeline.py requires diff_reports' TOTAL line in this section). Paste: before/after SHA, --data path(s) and their hash, python/pandas version, the command, and the whole output down to TOTAL. Otherwise: `not required (<git diff --stat file list>)`. I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's. -->
## Recurring issues checked (step 0)
Recurring issues checked: RI-0xx, RI-0yy (what you checked for each)
## Pipeline line (step 2)
check_pipeline line: `<ID>: <status> (...)`
## Sent back / sent to Audit
