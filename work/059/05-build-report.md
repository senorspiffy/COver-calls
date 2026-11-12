# 05 Build report - 059
## Changes made (file: what changed)
- ccbot/broker/webull_sandbox.py: `_rate_limited(exc)` reads `http_status` / `status_code` first (int == 429); text fallback only `HTTP Status: 429` (regex `http status:\s*429\b`) or "too many requests"/"too_many_requests"; `_call` passes the exception.
- tests/test_webull_sandbox.py: `_ServerError` (shape of SDK 3.0.4 ServerException), `test_429_inside_other_text_is_not_retried`, `test_rate_limit_status_attribute_is_retried`.
- .claude/agents/i3-verifier.md: step 3: every text-matching error classifier needs a negative test with the pattern inside other text (RI-012).
New files: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0. Changed: `... | grep -c '^ M'` → 3.
## Connectivity check
- [x] every new function/rule is used (`_rate_limited` called in `_call`; `_HTTP_429` used by it; i3 line read by I3)
- [x] every input has a source, every output has a consumer (exception from SDK → retry or raise)
- [x] every branch ends in a defined result (status 429 → retry; other status → raise; no status → text test → retry or raise; last try → raise)
- [x] no leftover TODOs or unused files
Grep (missing-data policy) on webull_sandbox.py: no hits. Absent `http_status` never means 429: falls to the text test, otherwise raises.
## Test output (pasted, not summarized)
`python3 -m pytest -q tests/test_webull_sandbox.py` → `18 passed in 0.55s`
`python3 -m pytest -q` → `FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items` / `1 failed, 235 passed, 1 skipped` (the failure is `A1 FAIL: 056`, open until A1 re-audits 056 with this fix, item 042).
Probe from request.md: `_rate_limited(RuntimeError('ServerException: http_status=500 error_code=INTERNAL msg=order 7a4291c failed'))` → False.
Mutation (scratch copy): `_rate_limited` → `return "429" in str(exc).lower()` → `FAILED test_429_inside_other_text_is_not_retried`, 1 failed, 17 passed.
RI-012: guardrail built (059); GUARDED when merged and the embedded-pattern test fails if the substring match is restored.
## Deviations from plan
None.
