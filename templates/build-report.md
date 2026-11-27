# 05 Build report - <ID>
Scratch dir: <absolute path printed by mkdtemp; one line per dir used, or none (<reason>)>
## Changes made (file: what changed)
## Connectivity check
- [ ] every new function/rule is used
- [ ] every input has a source, every output has a consumer
- [ ] every branch ends in a defined result
- [ ] no leftover TODOs or unused files
## Test output (pasted, not summarized)
Each later round's runs go under their own level-2 heading `## Test output (round N, pasted)`, never under a `###` heading or a `Round N ...` heading (item 091).
Suite: <last line of python3 -m pytest -q, as printed; copy it unchanged into the I2 log tests field>
## Real-data effect (diff_reports output, pasted)
<!-- Required when the item changes ccbot/realtest.py or a module/file it reads (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py: ccbot/realtest.py, costs.py, expiries.py, config.py, pricing.py, config/default.json, tickers.json, holidays.json, data/real/; from item 070 check_pipeline.py requires diff_reports' TOTAL line in this section). Paste: before/after SHA, --data path(s) and their hash, python/pandas version, the command, and the whole output down to TOTAL. Otherwise: `not required (<git diff --stat file list>)`. -->
## Deviations from plan
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).
