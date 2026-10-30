# 03 Research hand-off - 003
Status: READY

Checked 2026-10-30 by R3. Code line numbers are on branch `claude/bugfixes-003-008` at `74cf949`. Point-in-time quotes (Cboe snapshots from 2026-10-08 to 10-30) were not pulled again. They are checked against 002/03 L70–76 and L113–120, which verified them against the JSON files.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1 F1: no diversified ETF ≤ $28 with liquid options, among 11 checked | 002/03 L114 (from Cboe snapshots) | VERIFIED (carried from 002/03, not re-pulled) | – |
| R1 F2: KWEB/BITO/UNG/MSOS pass only at Δ0.11–0.23; MSOS fails (OI 262, $0.06) | 002/03 L74, L114 | VERIFIED (carried) | – |
| R1 F3: SOFI $16.77, 17.5C Δ0.28 $0.01 OI 12,667; F $11.94, 12.5C Δ0.33 $0.04 OI 4,056; T $21.09, 21.5C Δ0.37 $0.05; PFE $29.56 | 002/03 L70–73 | VERIFIED (carried; 11-06 weekly) | – |
| R1 F4: monthly spreads/OI for these tickers not read | 002/02 holes 2 | VERIFIED as UNVERIFIED (kept as an open item, not used as a fact) | – |
| R1 F5: "$5,000 is at the edge of where the system starts to function", "names in the $15–$40 range" | wheelstrategy.substack.com (fetched; dated 2025-10-25) | VERIFIED | – |
| R1 F6: Webull Level 1 = covered calls, buy-writes, CSPs | webull.com/help/faq/10980 (fetched) | VERIFIED | – |
| R1 F7: quotes are logged to `state/paper_snapshots.csv` (`bot.py` L23, L172); `feasible_universe` reads only `asof`; nothing counts past scans | code | VERIFIED. Also: each scan JSON already stores `passing` and `rejects` (`bot.py` L176), so a pass count needs no re-screen | – |
| grep "5 of" / "last 10" in `ccbot/`, `tests/`: no hits | `grep -rn` | VERIFIED | – |
| $28 cap = (3,000 − 200)/100; 50% cap = $1,500 → ≤ $15/share | math | VERIFIED | – |
| SOFI $1,677/$3,000 = 55.9% (fails the cap); a $15 strike is 10.6% below $16.77 | math | VERIFIED (10.55%) | – |
| F $1,194/$3,000 = 39.8% (passes the cap); 12.5C passes under [0.20, 0.35] | math + `pricing.pick_strike` (nearest 0.275: 12.5C gap 0.055 beats 13C gap 0.095) | VERIFIED (weekly quote only) | – |
| R2 FOR 2: waiting 10 scans ≈ half a cycle ≈ $23 of a $46.90 premium; it protects at most one $0.05 spread = $5 a side | math | VERIFIED (arithmetic; reasoning, not sourced) | – |
| R2 table, English: M-X "This is because Theta decays…" | m-x.ca PDF (fetched) | VERIFIED. The same PDF says "Expiration Selection - 30-45 days" for covered calls | – |
| R2 table, English: hackernoon "have no price data in either of my data sources" … "probably an upper bound" | hackernoon (fetched) | VERIFIED | – |
| R2 table, Chinese: 「到期月份的第四个星期三（遇法定节假日顺延）」 | sse.com.cn (fetched) | VERIFIED (quote and translation) | – |
| R2 table, Spanish: «Incluir instrumentos delistados…» | backtrex.com (fetched) | VERIFIED | – |
| R2 table, Japanese: three Nikkei guidebook quotes | Nikkei PDF (fetched) | VERIFIED (the first sentence continues 「ただし、いわゆるミニオプションは対象としない。」) | – |
| R2 table, Arabic: «خيار البيع المغطى هي استراتيجية خيارات شائعة…» translated as "The covered **[call]** …" | sahmcapital.com (fetched) | Quote VERIFIED. Translation **WRONG** | خيار البيع المغطى literally means "covered **put**". The page swaps the labels both ways: its covered-call description sits under "covered put", and its protective-put section (خيار البيع الوقائي, "like buying insurance") sits under خيار الشراء المغطى ("covered call"). Correct translation: "The 'covered put' [the page's label; the text describes a covered call] is a popular strategy offering limited return with limited risk." R2's HOLE ("labels are unreliable") stands, and is stronger than R2 said |
| R2 table, Arabic: «…ولكنهم لا يتوقعون زيادة ملحوظة في الأسعار على المدى القريب» | same | VERIFIED (end of a longer sentence) | – |
| R2 table, Hindi: «इस रणनीति में अधिकतम जोखिम शेयर मूल्य और प्राप्त प्रीमियम के अंतर के बराबर है।» | icicidirect.com (fetched) | VERIFIED (quote and translation) | – |
| R2 table, Hindi: «समाप्ति के दिनों में व्यापार करना उच्च जोखिम प्रस्तुत करता है» | angelone.in (fetched) | VERIFIED (part of a longer sentence) | – |
| R2 table, Turkish: «Yurt içi piyasaların resmi tatil nedeniyle yarım gün olması durumunda vade sonu bir önceki iş günüdür.» / «Bir adet standart sözleşme, dayanak varlığa ait 100 adet payı temsil eder.» | borsaistanbul.com PDF (fetched; "İstanbul, Kasım 2014") | VERIFIED. The half-day rule appears for stock options, stock futures and BIST 30 index options | – |
| R2 AGAINST 2: the corrected rule may be empty at $3k today, because no monthly quote has been read | 003/01 F4 | VERIFIED (reasoning) | Feasibility goes into the 001 text below |

## Removed claims
- None removed. One translation was corrected (Arabic, above).
- Not adopted (a decision, not a fact): R1's "block until 5 of the last 10 logged scans pass, `HISTORY_SHORT` blocks" gate. See the decision below.

## Decision (R1 vs R2)
**There is no hard 10-scan gate. The count is logged and shown as information only** (R2 FOR 2 / AGAINST 1).
- Why: the order-time screen (spread ≤ $0.05, OI ≥ 500, strike in tolerance) already blocks an illiquid trade on the day it would happen. The history count only guards against a one-day fluke.
- A gate would block every ticker for about 2 trading weeks on a new paper account (`HISTORY_SHORT`), and that block is not a safety input.
- RI-002 is still respected: when fewer than 10 scans are logged, the line says `n of k (history short)`. It never shows a guessed count.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | **Code:** new `screen.pass_history(scans, ticker, k=10)` → `(n_passed, n_scans)`. It counts the last ≤ k scan dicts whose `passing` list contains `ticker`. `bot.py` puts it in the scan dict as `"pass_history": {t: [n, k_seen]}` for each universe ticker, from the prior files in `state/scans/`. Read them the same way `write_reports` does at L194, where today they are read only on weekly days. It never blocks an order. | `state/scans/*.json` (`passing`, already written at L176) | scan dict field | `tests/test_screen_bot.py::test_pass_history_counts_last_10`: 10 scans with 4 passes → (4, 10), and the order is still placed when today passes; with 3 scans → (n, 3) |
| 2 | **Code:** `report.daily_report` § Screen prints `- <ticker>: passed n of last k logged scans` and adds ` (history short: k < 10)` when k < 10. Information only. | step 1 field | daily report line | `tests/test_report.py::test_daily_report_shows_pass_history`: the "(history short" text appears with 3 scans and is absent with 10 |
| 3 | **Docs: replace 001/03 step 1** (`work/001/03-handoff.md` L120) with: "**Account size.** At $3,000, trade **one** underlying that passes today's step-3 screen at the step-5 strike of the step-4 expiry, and fits both caps: 100 sh ≤ cash − $200 (≤ $28/share at $3k) and, for a single stock, ≤ 50% of capital (≤ $15/share at $3k). Prefer a diversified ETF if one passes. **Feasibility, 2026-10-30:** 0 tickers confirmed on monthly quotes. No diversified ETF ≤ $28 passes (002/03 L114). F ($11.94, 39.8% of capital) passes only on an 11-06 weekly quote (003/03). So the real-ticker universe at $3k is unproven until the paper bot logs monthly scans. If none passes, make no trade that day (the bot shows **UNIVERSE EMPTY**). The choices are then: (a) a CSP within the caps on a passing ticker, (b) add funds (two names from about $5.3k, 002/03), or (c) hold a covered-call ETF. The daily report shows how many of the last 10 logged scans each ticker passed. That count is information, not a gate. [house rule]". Check column: "Bot: `screen.feasible_universe` on every scan. Tests: `test_universe_empty_blocks_orders`, `test_shipped_config_has_a_passing_ticker` (SYNTH data only), `test_pass_history_counts_last_10`." | 001/03 | edited 001 | Diff shows L120 replaced. The text names the 3 tests, and each one exists (`pytest -q tests/test_screen_bot.py`) |
| 4 | **Docs: 001/03 step 9(a)** (L128): replace "max 50% in one single stock (so single stocks only at ≥ $5.6k)" with "max 50% of capital in one single stock (≤ $15/share at $3k; `max_single_name_frac: 0.5`)". This matches the bot. The old text contradicts both the code and the new step 1. | 001/03 | edited 001 | The step 9a text agrees with `config/default.json` |
| 5 | **Guardrail (BUG, RI-001 ESCALATED). Systemic, shared with 004 and 008.** Each part below needs the person's OK, because it edits agent and template files. Coordinate with 013, which edits the same agent files. (a) `templates/research-handoff.md`: add a column `Feasibility (n pass / n checked, date, command or test)` to the map table, required for every filter or window rule (price cap, asset type, liquidity, DTE, delta, weekday). (b) `.claude/agents/r3-fact-checker.md` step 1, one merged line (covers 008/RI-004 too): "For every filter/window rule, re-run its feasibility count with the cited command or test; mark the rule BLOCKED if the count is 0 or missing. For every worked example, check each step meets the rule it shows (thresholds, tick size, limits)." (c) `.claude/agents/i1-reviewer.md`: "Trace every rule in 03, including correction sections, to a plan line or write `DROPPED: <reason>`." (d) `.claude/agents/i3-verifier.md`: "When code changes a 001 rule (slack, tolerance, cap), the same item updates 001's text or opens a request; check it." (e) Prefer selectors that always have a candidate, or state the empty-day fallback (reason code + counted in the report). | RI-001 history | edited template and 3 agent files | Re-read each file. The next R3 handoff has a filled Feasibility column for every filter rule |
| 6 | **Not in this item:** real tickers (F, SOFI, KWEB, T) in a separate `config/paper.json` with its own feasibility test (R1/R2). This needs real monthly quotes first, so A1 should open it after the paper bot has logged monthly scans. | – | – | Listed in A1's backlog |
