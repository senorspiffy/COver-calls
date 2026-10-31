# 03 Research hand-off - 014
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Day defaults 0.0 | rules.py | VERIFIED |  |
| NaN capital passes caps | A1 probe | VERIFIED |  |
| SYNTH_A call sold on ex-date contract with div_next 0.0 | A1 probe | VERIFIED |  |
| Fix: sim gives a non-zero div_next | snapshot has no amount | WRONG | NaN + EARLY_ASSIGN_sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS_NA (per 'or is marked unknown') |
**Totals:** 4 rows checked → **3 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Day q/dividend/div_next default NaN | rules.py | NaN unless set | test_day_float_defaults_are_nan | – |
| 2 | Sim: dividend/div_next from ex-date (unknown amount → NaN); q = 0.0 labelled; Webull q = 0.0 labelled | snapshots | Day | drop tests broker.* | – |
| 3 | settle_day: DIVIDEND_UNKNOWN and EARLY_ASSIGN_sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS_NA events | Day | events | drop tests | – |
| 4 | _reject: CAPITAL_UNKNOWN; caps fail closed | capital | reject code | drop test derived.capital | – |
| 5 | Policy rows + enumeration tests; i2 grep notes | missing.py, tests, i2 | rows, tests | test_every_day_default_is_listed | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| broker.dividend | ex-date today, no amount | DIVIDEND_UNKNOWN event, nothing credited |
| broker.div_next | ex-date next trading day, no amount; or no ex-date | NaN; EARLY_ASSIGN_sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS_NA when an ITM call spans a known ex-date |
| broker.q | never supplied | fallback 0 (labelled) |
| model.oi | model replay | screen require_oi=False (tests only) |
| derived.capital | NaN equity | CAPITAL_UNKNOWN |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Eve of ex-date | next trading day after 2026-12-17 | 2026-12-18 = ex → NaN | ✓ |
| Not eve | next after 2026-10-30 | 2026-11-02 ≠ 12-18 → 0.0 | ✓ |
| Totals | 3+1+0=4 | 4 | ✓ |
`python3 scripts/check_handoff.py 014` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS
```
