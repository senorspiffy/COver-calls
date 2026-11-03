# Work item 040 (built in the 023 thread as "025"; renumbered: main already has a 025)
Type: IDEA
Scope: FAST
Opened by: person (023 thread, 2026-10-31: paper trade Ford/Vale from the VPS)
<!-- FAST: on 2026-11-03 the person chose "estimate the date and merge" over "run it through the full team review" (decision card in the 023 thread). R2 and I1 skipped; R3 fact check (03) and I3 verification (06) done. -->
Date: 2026-10-31
## What we want
Paper trade real tickers (F, VALE, AAL) on the VPS: Webull sandbox market data, fills simulated in the local paper ledger, earnings/dividend facts the feed lacks.
## Done looks like
`python -m ccbot scan --config config/paper.json --broker webull-paper --date <today>` runs with sandbox keys, opens up to two positions within the caps, never calls Webull's order endpoints, and the report labels estimated earnings dates.

## Person's decision (2026-11-03)
Asked in the 023 thread: "Should the bot trade Ford/Vale before their next earnings dates are published?" Chose: "Yes, estimate the date (+70 days)". This knowingly changes 001 step 3 (Correction 005) and answers the conflict raised by BUG 025 and the 2026-11-03 daily audit: an unpublished date may be estimated as last report + earnings_gap_days, only from config/tickers.json, labelled "estimated" in the report, and blocks again once the estimate passes.
