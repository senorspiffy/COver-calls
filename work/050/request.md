# Work item 050
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-07

## What we want
When a log line is INCOMPLETE because of its format, `check_pipeline.py` should print the format it expects, so whoever fixes it doesn't have to open the script.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- Today on main: `INCOMPLETE: 048 (log line for I1 I2 does not match its format (item 045))`. To know what I1 and I2 want, A1 had to read `LOG_FORMAT` in scripts/check_pipeline.py (L86–93).
- `--log` already prints the expected pattern when it refuses (`--log refused: I2 | 048 | see 05 does not match \d+ files? changed \| tests \d+/\d+\b.*`, A1 probe 2026-11-07), but as a regex. A readable form (`I2: <n> files changed | tests <passed>/<total>`) helps both.

## Recurring issue link (RI-#, if any)
RI-010 (related: same log lines).

## Done looks like
The INCOMPLETE message names each bad agent with a readable expected format, e.g. `I1 wants "FIT | <n> files planned"`; `--log` refusals print the same text. A test pins one message.
