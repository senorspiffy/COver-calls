# 02 Improvements - 067
## What past logs say
- RI-013 (OPEN, 1 occurrence): 065/05-07 reported only `counts_bot_rule_bid` and `bxm_vs_spy`; walkforward_picks, walkforward_by_ticker and MC median also moved [logs/recurring-issues.md L143-149; logs/audit/2026-11-15-065.md L85-91].
- RI-006 precedent: a script (`check_handoff.py`) replaced a hand count and held (GUARDED) [logs/recurring-issues.md L77-82]. RI-008: stdlib must parse on 3.10 (no QUOTE_STRINGS/NOTNULL) [01 finding 9]. RI-010: a template field alone is skipped unless something checks it [logs/recurring-issues.md L118-121].
## 3 ways FOR
1. Key-column row matching where a key exists, index otherwise. walkforward_picks by (train_from, test_from); walkforward_by_ticker and bot_rule_by_ticker by ticker; grid_in_sample by (ticker, config); trades_<tk>.csv by row index (no stable key) [01 finding 11]. Reason: with index alignment one added ticker shifts every later row, so the diff reports false changes in all of them (01 open question 3). A duplicate key must make the script exit non-zero; it must not pick one row.
2. Exact equality, no tolerance. Compare CSV cells as strings and JSON leaves with `==`, with NaN on both sides counted as equal and printed [01 findings 7, 10]. Reason: the change this item exists to catch is 0.0689 -> 0.0686 (0.0003). Any tolerance at or above that scale hides it. The question is "did anything move", not "did it move a lot".
3. Capped paste with full counts. Print every changed summary.json leaf (small: 9 top-level keys [01 finding 2]), then per CSV: rows matched / added / removed / changed and the first N changed rows (N=20 suggested, `--max-rows` flag), plus files present on one side only [01 finding 5]. End with a one-line total. Reason: a decision-path change can touch thousands of trades/grid rows (01 open question 2). An uncapped paste hides the important lines. The counts are never capped, so no change goes unreported; `--max-rows 0` prints all.
## 3 ways AGAINST
1. The trigger can be gamed or missed. "Decision path changes" is a judgement call. Recommendation: trigger = any diff to ccbot/realtest.py (01 open question 5); I3 checks `git diff --stat` against the field. Cost: cosmetic edits also need a run, about 11 min per side [01 Numbers]. Risk left: a change in a module realtest imports (e.g. ccbot/rules.py) changes the output but does not trigger the rule. UNVERIFIED which ccbot modules realtest.py imports; I1 should list them and add them to the trigger if they affect decisions.
2. A field with nothing that checks it is skipped (RI-010 pattern). If no check covers the pasted block, the next builder can leave it blank or paste a stale one. Mitigation: the pasted block must include the before/after dirs and the commit SHAs, and its totals line must be in the script's fixed format so I3/A1 can re-run it and compare. A check_pipeline check is out of scope here; at most note it as a follow-up.
3. Before/after outputs may not exist. 065's effect list needs 5883ba4 and e129253 outputs; the /tmp scratch dirs may be gone [01 open question 4]. Two ~11 min runs, and the data/real inputs must be identical on both runs, or the diff mixes code effects with data effects. Record the data file hashes, or state that the same data dir was used.
## Findings by language
Languages: N/A (no new external claims). This is a stdlib diff script and template wording inside this repo. The json/csv/pandas behaviour it relies on is already sourced in 01, and no market fact, fee or rule is added.
Random languages this cycle: none (N/A)
## Holes to watch out for (summary)
- The recursive diff must cover dicts AND lists. If list lengths differ, print the length change and the extra items. Index-align lists; walkforward_picks in JSON is a list.
- A key present on one side only (dict key, CSV column, file) must be printed as added/removed, never dropped.
- A CSV header change (column added or renamed) must be printed before the rows are compared.
- Parse JSON with a strict `parse_constant`, or count NaN explicitly. Never let NaN != NaN produce a false change [01 findings 7, 14].
- Fixture tests to add: a nested-key change (request), an added ticker with key matching (no false shifts), a row count over N (counts still exact), and a 0.0689 -> 0.0686 change (no tolerance).
- Acceptance: run on 065's before/after outputs, the script must reproduce 2/10 windows, 11/17 tickers (6 -> 5 positive) and MC median 0.0689 -> 0.0686 [01 finding 13].
- Research tooling only; no trading effect, not financial advice.
