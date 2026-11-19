# Trade lessons (knowledge base)

Lessons from the paper bot's real trades, newest first. Each line: date, lesson, evidence. UNCONFIRMED = seen once; CONFIRMED = seen 3+ times.
Paper only, research, not financial advice. Lessons are notes only: no setting is tuned from paper results; any change waits for the Sunday review.

## 2026-11-18
- **The run took 19 minutes instead of ~20 seconds.** Exit 0 and the results look normal, so the cause is unknown (slow broker API? VPS load?). If a run ever runs past the close, the quotes are stale. Watch run times. UNCONFIRMED.
- **The drawdown keeps growing; premium can't keep up.** Shares -$486, calls +$49.50 (10%). VALE is -16% from its basis. Repeats the CONFIRMED lesson.

## 2026-11-17
- **A near-worthless call still blocks the shares for a month.** VALE 13C is at $0.005 (97% of premium earned) with 31 days left. Closing it for about $1 per contract would let the bot sell a fresh call at a strike at or above the $11.97 basis. For the Sunday review: compare with variant V1 (50% buy-back). UNCONFIRMED.
- **The loss is still growing while the premium is almost all earned.** Shares -$404, calls +$48 (12%). Repeats the CONFIRMED 11-16 lesson; no new cause.

## 2026-11-16
- **The call cushion is now small next to the drop.** Shares -$373, calls +$40.50 (11% offset). VALE alone: -$302 vs +$25 (8%). Seen 3 days: CONFIRMED. On a falling stock, the premium does not protect the account.
- **Two names = concentrated risk.** Both holdings fell together (F -5.8%, VALE -12.6% from basis), so equity is -6.7% in a week. Notes only for the Sunday review: compare with a wider or ETF-based setup before adding capital. UNCONFIRMED.
- **Full slots lock out new setups.** AAL passed the screen but could not be bought because both position slots hold losing stocks. UNCONFIRMED.
- **Once the stock falls, the short call has almost nothing left to give.** VALE 13C is now 24% out of the money at $0.035. The remaining premium ($7) is too small to matter, and the cost-basis floor (kept by the user 2026-11-14) blocks rolling the strike down below basis. UNCONFIRMED.

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
