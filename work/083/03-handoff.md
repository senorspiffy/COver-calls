# 03 Research hand-off - 083
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 window 0.7-1.3 | ccbot/bot.py | VERIFIED |  |
| F2 13 outside window | recap + arithmetic | VERIFIED |  |
| F3 NaN fallback | ccbot/bot.py, webull_sandbox.py | VERIFIED |  |
| F4 CAPITAL_UNKNOWN | ccbot/screen.py | VERIFIED |  |
**Totals:** 4 rows checked → **4 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `BrokerMarket(…, held)`; chain window = min/max of [0.7,1.3] x close and the held strike, for the held expiry | start positions | held strike requested | test_window_widens_to_the_held_strike | 1 of 1 case (VALE 11-19) |
| 2 | Pass `start.get(t).option` at both BrokerMarket constructions | Portfolio | – | test_window_unchanged_without_a_held_option_or_on_another_expiry | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Quote for held strike | broker returns none | equity NaN → CAPITAL_UNKNOWN (unchanged, RI-002) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Old window top | 1.3 x 9.83 | 12.779 < 13 | ✓ |
| Totals | 4+0+0=4 | 4 | ✓ |
