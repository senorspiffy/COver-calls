# 05 Build report - 041
## Changes made (file: what changed)
ccbot/tickers.py (stale ex-date guard, `TICKER_FIELDS`); ccbot/missing.py (3 `tickers.*` rows; `snapshot.next_earnings` comment names 040's estimate); tests/test_missing_inputs.py (enumeration over `TICKER_FIELDS`, 3 drop tests); tests/test_paper.py (`test_enrich_past_ex_div_is_unknown`)
(One branch, `daily-fixes/2026-11-04`, carries items 041–044. It is built on `daily-fixes/2026-11-03` (PR #10, unmerged) because 042/043 change `scripts/check_pipeline.py`, which PR #10 changes too (item 034 rule), and on main at the 2026-11-04 audit.)
## Connectivity check
- [x] every new function/rule is used (`TICKER_FIELDS` is read by `test_policy_lists_every_optional_input`; the new rows are each run by `test_drop_each_input`)
- [x] every input has a source, every output has a consumer (A1's daily step reads the check output)
- [x] every branch ends in a defined result
- [x] no leftover TODOs or unused files
Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0" ccbot/tickers.py` → 2 hits, both `... else 0.0` in `enrich` L53–54: reached only when the ex-date is today-or-future and the amount known, so 0.0 means "this day is not the ex-date / next day is not" (broker.div_next policy). The past-date case now returns before them.
RI-002: guardrail built (041); GUARDED when merged and a new unlisted tickers.json key fails the enumeration test.
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
182 passed, 1 skipped (+1 failed: test_repo_pipeline_has_no_skipped_items, the real work/ folder, until the 041–044 log lines and 06/07 exist; re-run in 06)
$ python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py ccbot/tickers.py ccbot/missing.py
(no output, exit 0)
```
## Deviations from plan
None.
