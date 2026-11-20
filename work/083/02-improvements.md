# 02 Improvements - 083
## What past logs say
RI-001 (window never computed), RI-002 (no invented values).
## 3 ways FOR
1. Root-cause fix: the held strike is requested, so a real quote marks it.
2. No made-up mark ($0.01 or stale): stays within RI-002.
3. One line in one place; all callers (capital, exit check, screen prefetch) benefit.
## 3 ways AGAINST
1. If Webull lists no contract or quote for that strike, the freeze remains.
2. A wider window means a few more symbols per held ticker (rate limit; 056 retry covers it).
3. A held put (wheel V5) far below the window is covered the same way, but untested live.
## Findings by language
Languages: N/A (internal bug).
## Holes to watch out for (summary)
A last-mark fallback was suggested; not built, since it would hide a missing quote (RI-002). Revisit if the freeze recurs with the window fixed.
