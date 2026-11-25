# 06 Verification - <ID>
Verdict: PASS | FAIL (round <n>; earlier rounds: <verdicts>)
Sent back to: <I1 | I2 | I1 I2 | none>
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Scratch dir: <absolute path printed by mkdtemp; one line per dir used, or none (<reason>)>
## I1 audit (plan vs research)
## I2 audit (build vs plan)
## Tests re-run (output)
Each later round's runs go under their own level-2 heading `## Tests re-run (round N)`, never under a `###` heading or a `Round N ...` heading (item 091).
## Real-data effect (diff_reports output, pasted)
<!-- Required when the item changes ccbot/realtest.py or a module/file it reads (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py: ccbot/realtest.py, costs.py, expiries.py, config.py, pricing.py, config/default.json, tickers.json, holidays.json, data/real/; from item 070 check_pipeline.py requires diff_reports' TOTAL line in this section). Paste: before/after SHA, --data path(s) and their hash, python/pandas version, the command, and the whole output down to TOTAL. Otherwise: `not required (<git diff --stat file list>)`. I3 runs diff_reports.py, with the same `--max-rows` as 05, on 05's base dir (or its own base run) and its own full head-run dir, never 05's head dir (item 073), and compares its TOTAL line with 05's. Also paste the head run's `--out` dir, worktree, log file and wall time, and `cmp` of this output with 05's saved output file: identical, or differs (the differing lines); if that file is gone, compare with the lines pasted in 05 and say so. -->
## Recurring issues checked (step 0)
Recurring issues checked: RI-0xx, RI-0yy (what you checked for each)
## Pipeline line (step 2)
check_pipeline line: `<ID>: <status> (...)`
## Sent back / sent to Audit
