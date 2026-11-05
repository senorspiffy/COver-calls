"""Missing-data policy (005, RI-002): what happens when each optional input is absent.

Absent never means none, 0, a default or a pass. Each value is (effect, reason or text):
block = no trade, with that reason code; n/a = shown as n/a with that text;
fallback = an existing labelled substitute; known_gap = not handled yet, stated here.
tests/test_missing_inputs.py drops each input in turn and checks the named result.
"""
MISSING_POLICY = {
    "csv.earnings": ("block", "EARNINGS_UNKNOWN"),          # stock only; an ETF has no earnings
    "csv.dividend": ("block", "DIVIDEND_UNKNOWN"),          # B&H n/a too: "dividend: not supplied"
    "csv.iv": ("fallback", "trailing realised vol (report: 'the `iv` column when present, else trailing realised vol')"),
    "snapshot.oi": ("block", "OI_UNKNOWN"),
    "snapshot.next_earnings": ("block", "EARNINGS_UNKNOWN"),  # stock only; see tickers.next_earnings for 040's estimate
    # Ticker facts file (040, 041): config/tickers.json, ccbot/tickers.py::TICKER_FIELDS.
    "tickers.next_earnings": ("fallback", "estimated as last_earnings + earnings_gap_days (040, person's house rule), "
                                          "labelled 'estimated'; EARNINGS_UNKNOWN when there is no last_earnings "
                                          "or the estimate has passed"),
    "tickers.asset_type": ("fallback", "the broker's asset type (Day default \"stock\"), so a stock's earnings "
                                       "must still be known, else EARNINGS_UNKNOWN (046)"),
    "tickers.last_earnings": ("block", "no estimate; with next_earnings null too → EARNINGS_UNKNOWN (046)"),
    "tickers.ex_div_date": ("n/a", "days to ex-dividend: n/a (not supplied); a past ex-date is unknown too (041), "
                                   "so dividend/div_next stay NaN"),
    "tickers.dividend": ("n/a", "dividend/div_next stay NaN (never 0.0) unless both ex-date and amount are known"),
    "snapshot.ex_div_date": ("n/a", "days to ex-dividend: n/a (not supplied)"),
    "snapshot.iv": ("fallback", "the held option is marked at its quoted mid (040); equity n/a only when "
                                "there is no quote and no vol; quotes keep their own delta"),
    "bh_benchmark": ("n/a", "100 shares cost more than cash − buffer"),
    # Broker path (014). Snapshots carry the ex-dividend date but no amount.
    "broker.div_next": ("n/a", "EARLY_ASSIGN_CHECK_NA event: ITM call with an ex-date ahead and no amount; "
                               "0.0 only when the ex-date is known and not the next trading day"),
    "broker.dividend": ("n/a", "DIVIDEND_UNKNOWN event on the ex-date: amount not supplied, nothing credited"),
    "broker.q": ("fallback", "q = 0 for model marks and the early-assignment time value on the broker path; "
                             "entry uses the broker's own quotes (delta, mid)"),
    "model.oi": ("fallback", "model-replay quotes have no OI; the screen runs with require_oi=False "
                             "(SimBroker series mode, tests only, not reachable from the CLI)"),
    "derived.capital": ("block", "CAPITAL_UNKNOWN"),   # equity NaN (e.g. option held, snapshot iv blank)
}
