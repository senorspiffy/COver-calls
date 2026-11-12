# 02 Improvements - 056
## What past logs say
Read first: RI-002 (no silent values), RI-010.
## 3 ways FOR
1. A scan no longer dies halfway when several accounts run back to back.
2. Bounded: gives up after 5 retries (62 s), so a real outage still fails loudly.
3. Only 429s retry; auth or other errors still raise at once.
## 3 ways AGAINST
1. A daily run can take up to a minute longer per throttled call.
2. Matching "429" in error text depends on the SDK's message format.
3. Retrying hides how close we run to the limit; the log warning keeps it visible.
## Findings by language
Languages: N/A (vendor API docs and an RFC).
## Holes to watch out for (summary)
SDK message format could change; tests pin both forms (status code and error text).
