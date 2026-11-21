# 05 Build report - <ID>
## Changes made (file: what changed)
## Connectivity check
- [ ] every new function/rule is used
- [ ] every input has a source, every output has a consumer
- [ ] every branch ends in a defined result
- [ ] no leftover TODOs or unused files
## Test output (pasted, not summarized)
Suite: <last line of python3 -m pytest -q, as printed; copy it unchanged into the I2 log tests field>
## Real-data effect (diff_reports output, pasted)
<!-- Required when the item changes ccbot/realtest.py or a module/file it reads (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py: ccbot/realtest.py, costs.py, expiries.py, config.py, pricing.py, config/default.json, tickers.json, holidays.json, data/real/; from item 070 check_pipeline.py requires diff_reports' TOTAL line in this section). Paste: before/after SHA, --data path(s) and their hash, python/pandas version, the command, and the whole output down to TOTAL. Otherwise: `not required (<git diff --stat file list>)`. -->
## Deviations from plan
