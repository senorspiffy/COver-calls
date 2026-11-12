# 07 Audit task - 056
A1, please check:
- check_handoff 056 → PASS; check_pipeline → 056 awaiting A1.
- Only 429 retries; 401 and other errors raise at once; `_assert_sandbox` runs each try.
A1 result: FAIL (2026-11-12, logs/audit/2026-11-12.md: _rate_limited matches '429' anywhere in error text, so a 500 whose message holds '429' (e.g. an order id) is retried 5 times; BUG 059)
A1 result: PASS (2026-11-12, logs/audit/2026-11-12.md: the FAIL above is fixed by 059 on daily-fixes/2026-11-12; _rate_limited now reads http_status)
