# 01 Research brief - 059
## Question
How does the Webull SDK report a rate-limit error, so `_call` can retry only HTTP 429 and nothing else?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. The SDK raises `webull.core.exception.exceptions.ServerException(code, msg, http_status, request_id)` for any reply outside 200–299; `http_status` is kept as an attribute and `get_http_status()` returns it (SDK 3.0.4, `webull/core/client.py` `_get_server_exception`, `webull/core/exception/exceptions.py`). [https://pypi.org/project/webull-openapi-python-sdk/3.0.4/]
- F2. `str(ServerException)` is `"HTTP Status: %s, Code: %s, Msg: %s, RequestID: %s"`: the server's message and a request id are in the same text as the status, so a plain "429" substring can come from the message or the id. [https://pypi.org/project/webull-openapi-python-sdk/3.0.4/]
- F3. HTTP 429 means "Too Many Requests"; the client should wait before retrying. [https://www.rfc-editor.org/rfc/rfc6585#section-4]
- F4. The SDK's own default retry list is 500, 502, 503, 504 (`retry_condition.py` `DEFAULT_RETRYABLE_HTTP_STATUS_LIST`); 429 is not in it, so the bot's retry is still needed. [https://pypi.org/project/webull-openapi-python-sdk/3.0.4/]
- F5. A1 probe on main 05a33fd: `_rate_limited('ServerException: http_status=500 error_code=INTERNAL msg=order 7a4291c failed')` → True (work/059/request.md).

## Numbers used (show the math)
A random 32-hex `client_order_id` holds "429" somewhere with probability 1 − (1 − 1/4096)^30 ≈ 30/4096 ≈ 0.73%. Wasted wait per false match: 2+4+8+16+32 = 62 s.

## Fit for a ~$3k account
No strategy change; paper scans only (webull-paper / sandbox).

## Open questions
None.
