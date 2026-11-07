# 02 Improvements - 050
## What past logs say
- 039, 044, 047 (EFFICIENCY): small output lines that save A1 a hand step were built and merged without trouble.
- RI-010: 041–044 and 048 used `see 04` / `see 05`; a plain hint in the error is the cheapest nudge toward the right form.

## 3 ways FOR
1. The fixer sees the expected form in the same line; no need to open the script (today A1 had to read L86–93).
2. One `LOG_HINT` dict used by both messages keeps them the same.
3. The hints copy the agent files' wording, so the script and the agents speak one language.

## 3 ways AGAINST
1. Two places (LOG_FORMAT, LOG_HINT) can drift. Reasoning: a test asserts every LOG_FORMAT key has a hint, and that each hint's example form (with numbers filled in) matches its regex.
2. Longer INCOMPLETE lines. Reasoning: only bad agents get a hint, usually one or two.
3. Changing the text breaks an existing test assertion. Reasoning: keep the old text as a prefix (answer to R1's question), so greps and the test still match.

## Findings by language
Languages: N/A (no new external claims). Wording of a repo script's messages only.

## Holes to watch out for (summary)
- Keep `does not match its format (item 045)` as the start of the message.
- `--log` refusal must still write nothing and exit 2.
