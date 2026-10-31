# Work item 025
Type: IDEA
Scope: FULL
Opened by: person (023 thread, 2026-10-31: paper trade Ford/Vale from the VPS)
Date: 2026-10-31
## What we want
Paper trade real tickers (F, VALE, AAL) on the VPS: Webull sandbox market data, fills simulated in the local paper ledger, earnings/dividend facts the feed lacks.
## Done looks like
`python -m ccbot scan --config config/paper.json --broker webull-paper --date <today>` runs with sandbox keys, opens up to two positions within the caps, never calls Webull's order endpoints, and the report labels estimated earnings dates.
