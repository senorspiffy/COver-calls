# Work item 009
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Make the PBO n/a line name the condition that actually failed: T < 8 months, N < 2 configs, or a non-finite return in R.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
`ccbot/report.py` prints one fixed text, "n/a (needs >= 8 non-held-out months and >= 2 configs; have T months)", for all three NaN causes in `walkforward.pbo_cscv` L95. If R has a NaN with T ≥ 8, the text points at the wrong cause (I3 note, 06 Re-verification 2).

## Done looks like
`pbo_cscv` returns (or `walk_forward` records) the reason code. The report prints it. There is one test per cause.
