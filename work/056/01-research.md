# 01 Research brief - 056
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- R1. Webull's OpenAPI applies per-endpoint request-frequency limits and returns an error when they are exceeded; the docs list limits per API. [https://developer.webull.com/apis/docs/market-data-api/overview]
- R2. HTTP 429 means "Too Many Requests"; the client should wait before retrying. [https://www.rfc-editor.org/rfc/rfc6585#section-4]
- R3. Observed: a 429 from the sandbox after two back-to-back scans; a retry seconds later worked (VPS run 2026-11-12, not logged in the repo): UNVERIFIED beyond that run.
## Numbers used (show the math)
Backoff 2+4+8+16+32 = 62 s at most before giving up; above Webull's 60 s window, so a full window passes before the last try.
