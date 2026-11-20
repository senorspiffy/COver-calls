# Work item 083
Type: BUG
Scope: FULL
Opened by: person (project thread; bug found by the morning-recap thread, journal/recaps/2026-11-19.md on claude/project-thread-f64g3k)
Date: 2026-11-20
## What we want
A held short option always gets a quote request, so equity can be marked and the account isn't frozen.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
2026-11-19 main scan: VALE closed $9.83 with a held VALE 13C 12/18. BrokerMarket.chain read strikes 0.7-1.3 x close = 6.88-12.78, so the 13 strike was never requested. `_capital` fell back to BS on NaN vol → equity NaN → F, VALE, AAL rejected CAPITAL_UNKNOWN; banner "UNIVERSE EMPTY: rule CAPITAL_UNKNOWN".
## Root cause and prevention guardrail (BUG only)
Root cause: the strike window is set from today's close only, assuming a held strike is within ±30%. Guardrail: the window always includes the held option's strike for its expiry; tests pin the 2026-11-19 case.
## Recurring issue link (RI-#, if any)
RI-001 (window assumed to have candidates, never computed). RI-002 checked: no fallback value is invented; if the broker still has no quote, equity stays NaN.
## Done looks like
VALE 13C is requested on a $9.83 close; tests pass; next main scan marks equity.
