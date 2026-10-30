# Work item 010
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
On short data, report the held-out CAGR for fixed variants (V0–V3, V5, one config each). Mark the config "fixed" instead of "not selected (no train years)".

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
`walkforward.walk_forward`: `chosen_h = select(yearly, pre) if pre else None` applies to every variant. For a 1-year CSV, 05 Revision 2 shows `| V0 | not selected (no train years) | n/a | -1.94% | n/a |`. Nothing needed selecting, so the user loses the only out-of-sample number for 5 of 6 variants. Only V4 (3 θ configs) truly needs train years.

## Done looks like
For variants with one config, the held-out row shows the config and its CAGR/excess. V4 still shows "not selected" when there are no train years. The test in `tests/test_cli.py` is updated.
