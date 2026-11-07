# 01 Research brief - 050
## Question
How should `check_pipeline.py` say which log format it expects, both in INCOMPLETE and in `--log` refusals?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- No external facts are needed: the change is in this repo's own script. Sources are repo files and commands.
- INCOMPLETE says only `log line for I1 I2 does not match its format (item 045)` [repo: scripts/check_pipeline.py `def incomplete`; main 2026-11-07 output].
- `--log` refusals print the raw regex from `LOG_FORMAT` [repo: `def write_log`; A1 probe 2026-11-07: `does not match \d+ files? changed \| tests \d+/\d+\b.*`].
- The agent files already spell each format in words, e.g. i1-reviewer.md `"<verdict> | <n> files planned"`, i2-builder.md `"<n> files changed | tests <pass>/<total>"` [repo: .claude/agents/*.md, last paragraph].
- `test_malformed_log_line_is_incomplete` asserts the exact INCOMPLETE text `150 (log line for I2 does not match its format (item 045))` [repo: tests/test_pipeline_check.py].

## Numbers used (show the math)
- 6 agents → 6 plain-word hints, one per `LOG_FORMAT` key.

## Fit for a ~$3k account
Process only; no trading rule or number changes.

## Open questions
- Keep the item-045 text so old reports still match a grep? R2 to weigh.
