# 01 Research brief - 014
## Question
On the broker path, are unknown dividend values and NaN capital kept unknown instead of 0.0 or a pass?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `Day.q/dividend/div_next` defaulted to 0.0; neither broker set them [ccbot/rules.py, broker/sim.py, broker/webull_sandbox.py]
- `_reject` cap tests `x > NaN` are False, so NaN capital passed [ccbot/screen.py]
- Snapshots carry `ex_div_date` but no dividend amount [ccbot/data.py OPTIONAL_SNAPSHOT_FIELDS]
- `test_policy_lists_every_optional_input` enumerates only loader inputs [tests/test_missing_inputs.py]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-002 occ 5–6).
## Numbers used (show the math)
SYNTH_A ex-date 2026-12-18. On 2026-10-30 the next trading day is 11-02, so div_next = 0.0 (known). On 12-17 the next trading day is 12-18, so div_next = NaN (amount unknown).
## Fit for a ~$3k account
Safety change; it can only block or flag, never add a trade.
## Open questions
None.
