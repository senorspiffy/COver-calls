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
    "snapshot.next_earnings": ("block", "EARNINGS_UNKNOWN"),  # stock only
    "snapshot.ex_div_date": ("n/a", "days to ex-dividend: n/a (not supplied)"),
    "snapshot.iv": ("n/a", "equity n/a while an option is held (no vol to mark it); quotes keep their own delta"),
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
