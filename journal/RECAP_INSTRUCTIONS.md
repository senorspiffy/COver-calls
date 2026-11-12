# Morning trade recap: how each run works

Runs Tue-Sat at 5:30 AM (user's local time) and covers the previous trading day (Mon-Fri runs of the paper bot).

## Data (on the VPS, `C:\Users\Administrator\cover-calls`, read-only)
| What | Main | Practice |
|---|---|---|
| Trades | `state\paper_trades.csv` | `state_practice\paper_trades.csv` |
| Ledger now | `state\sim_ledger.json` | `state_practice\sim_ledger.json` |
| Day scan (equity, rejects) | `state\scans\<date>.json` | `state_practice\scans\<date>.json` |
| Report | `reports\daily_<date>.md` | `reports_practice\daily_<date>.md` |
| Run log | `logs\daily_runs.log` (both) | |

Trades columns: date,variant,ticker,action,reason,contract,qty,limit,tif,fill,fees,mid,delta,in_band,in_window,status,dry_run,detail.
`action` is BUY_SHARES / SELL_CALL / NONE; parse `qty` as float. A screen reject shows reason UNIVERSE_EMPTY; the real cause is in `detail`.
Starting cash: main $5,000 (`config\paper.json`), practice $65,200 (`config\practice.json`).

## Steps
1. Read the files above for the previous trading day (read-only; never print keys; change nothing).
2. Write `journal/recaps/<date>.md`: run status, each trade (filled orders, buy-backs, rolls, expiries, assignments), realized and unrealized wins/losses per position, equity change, rejects by reason.
3. For each win or loss, write what it teaches (notes only; never change bot settings, changes wait for the Sunday review). Add only new or strengthened lessons to `journal/trade-lessons.md` (dated, with the evidence). Mark a lesson UNCONFIRMED until it repeats; don't invent causes.
4. Commit and push; post a short brief (under ~80 words) in the thread: trades, wins/losses, the lesson(s) added.
5. If the VPS can't be reached or no run happened (holiday, error), say so in one line and stop.
