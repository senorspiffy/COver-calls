# Work item 028
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
Running `scripts/check_handoff.py` on every item, as A1 must, prints 14 FAIL lines for 002–008, whose hand-offs were written before the Totals and Self-check fields existed (019, 017). Mark them as legacy so the daily run shows only new problems, and add an `--all` mode so A1 runs one command instead of a loop.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
A1, 2026-10-31: for 002–008, each prints "FAIL: no Totals line" and "FAIL: missing '## Self-check' section" (exit 1). 001 and 017–022 print PASS. All 002–008 hand-offs are dated 2026-10-30, before the template change in commit 77273f0.

## Done looks like
`python3 scripts/check_handoff.py --all` prints one line per item (PASS / LEGACY / FAIL / no hand-off) and exits 1 only on FAIL; a legacy item is named in a list in the script with the reason; a test covers both modes.
