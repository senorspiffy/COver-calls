# 03 Research hand-off - <ID>
Status: READY | BLOCKED (<reason>)
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
**Totals:** <n> rows checked → **<n> VERIFIED as-is**, **<n> fixed**, **<n> removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
<!-- Required for every filter or window rule (universe/price/asset cap, liquidity, DTE, delta, weekday): "<n pass> of <n checked>, <date range>, <command or test>". 0 or blank → Status BLOCKED. Other steps: "–". -->
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
<!-- Every optional input a step reads. Absent never means none, 0, a default or a pass. -->
## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
`python3 scripts/check_handoff.py <ID>` output (pasted, must say PASS):
