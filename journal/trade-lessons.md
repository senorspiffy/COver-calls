# Trade lessons (knowledge base)

Lessons from the paper bot's real trades, newest first. Each line: date, lesson, evidence. UNCONFIRMED = seen once; CONFIRMED = seen 3+ times.
Paper only, research, not financial advice. Lessons are notes only: no setting is tuned from paper results; any change waits for the Sunday review.

## 2026-11-13
- **The call cushion keeps shrinking as the stock falls.** VALE: shares -$150, calls +$24 (16% offset, down from 22% on 11-11). F: shares -$37, call +$11. Repeat of the 11-11 lesson: the risk is the stock. Seen 2 days.
- **Most of the premium is already earned on the falling names.** VALE 13C 0.16 to 0.04 (75% kept), F 0.23 to 0.12 (48%). A 50% buy-back (V1) would close VALE now and free it to sell again. Notes only; any rule change waits for the Sunday review. UNCONFIRMED.
- **A ticker's screen result flips day to day.** VALE passed on 11-12 and failed SPREAD on 11-13. One day's pass or fail is noise; pass history over 10+ scans matters more. UNCONFIRMED.

## 2026-11-11
- **Premium only cushions a small part of a share drop.** VALE (main): shares -$78, short calls +$17. The call offsets about 22% of the drop. Strategy risk sits in the stock, not the call. UNCONFIRMED.
- **Small, cheap calls decay fast on a falling stock.** VALE 13C went 0.16 to 0.075 (-53%) in a few days as the stock fell 3.3%. A 50% buy-back rule (variant V1) would already trigger here. Watch whether early buy-backs add value. UNCONFIRMED.
- **The bot sold a call outside its own delta band.** HBAN 17C sold at delta 0.23 with in_band False, for $0.15 ($45 on $4,764, about 0.9% for 37 days). Low premium on a low-delta call: check whether in_band False should block the sale. UNCONFIRMED.
- **Wide spreads are the main gate.** Practice: 6 of 13 tickers rejected for SPREAD (AAL, VZ, KMI, CMCSA, ITUB, KGC), 3 for no strike in tolerance. Supports moving the run before the 4:00 PM close (pending "move it to 3:45"). UNCONFIRMED.
- **Rising stocks lift the short call against you.** T (practice): shares +$92, calls -$26. Normal for covered calls; the cap only matters if T passes $23 by Dec 18. UNCONFIRMED.
