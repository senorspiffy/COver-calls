# 02 Improvements - 059
## What past logs say
056 (2026-11-12) added the retry with a text match; its negative test used "UNAUTHORIZED" only. No recurring issue on error matching before this (RI-012 opened today).
## 3 ways FOR
1. Reading `http_status` uses the value the SDK already parsed (01 F1), so ids and messages can no longer cause a false retry.
2. A false retry of `place_option` can no longer resend an order after a non-429 error (request evidence, line 254).
3. A negative test with "429" embedded in an id pins the fix: restoring the substring match fails it.
## 3 ways AGAINST
1. Other SDK paths (or a stub) may raise a plain exception with only text; keep a narrow text fallback (`HTTP Status: 429` token or "too many requests") so real 429s still retry.
2. A 429 reply with a non-standard status attribute name would not be seen; mitigated by the text fallback on the SDK's fixed `HTTP Status: <n>,` prefix (01 F2).
3. Small extra code for a rare case; cost is one helper and two tests.
## Findings by language
Languages: N/A (no new external claims): the fix reads a value the SDK already exposes; facts F1–F4 are from the SDK source and RFC already cited by R1.
## Holes to watch out for (summary)
Do not match "429" inside RequestID or Msg; keep `_assert_sandbox()` on every try; keep the 5-try cap.
