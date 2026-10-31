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
    "snapshot.iv": ("fallback", "the held option is marked at its quoted mid (025); equity n/a only when "
                                "there is no quote and no vol; quotes keep their own delta"),
    "bh_benchmark": ("n/a", "100 shares cost more than cash − buffer"),
    "broker.div_next": ("known_gap", "broker Day.div_next is 0.0, so the ex-dividend early-assignment "
                                     "check is off on the broker path; A1 to open an item"),
}
