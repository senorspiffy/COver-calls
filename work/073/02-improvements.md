# 02 Improvements - 073
The person chose "Always own run" (request.md L11, 2026-11-18). The AGAINST points below are for the record. They do not reopen that choice; each one ends with the mitigation that fits inside it.

## What past logs say
- 068 is the only earlier case. One head run (068-after) was made by the orchestrator and used by both I2 and I3. A1 called it a disclosed deviation, not an error, because I3 ran under the older text, and asked the person to choose. [logs/audit/2026-11-17-068.md L14-21, L82; work/068/06-verification.md L24, L87]
- I3 skipped its run "on the orchestrator's instruction" (06 L24, L87). So the orchestrator's text (run-item.md L18) matters as much as i3-verifier.md L13. [work/068/06-verification.md L24]
- A1 found that 068's scratch `--out` rule is "agent text only" (no check_pipeline hit for `reports|--out`). That is the same kind of gap a text-only "own run" rule has. [logs/audit/2026-11-17-068.md L83-85]
- RI-010 (GUARDED) root cause: "some step duties ... exist only in the agent text; the template has no field for them and no script checks them, so files written outside run-item skip them first." 073 adds another duty of that kind. [logs/recurring-issues.md L120]
- RI-013 (GUARDED, 067): whole-output diff via `scripts/diff_reports.py`, plus the 070 field-fill check of the TOTAL line. Gap (o): a TOTAL line "does not prove 06's TOTAL equals 05's (I3 still compares, templates/verification.md)". [logs/recurring-issues.md L144-147; scripts/check_pipeline.py L123-125]
- Past R2s for 067, 068 and 070 logged `languages: N/A` (process items). 073 is an IDEA item, so it gets the full search. [logs/research/2026-11-16.md L5-6; logs/research/2026-11-17.md L5]

## 3 ways FOR
1. **Close every gap in the text with one rule in three places (all needed).**
   - i3-verifier.md L13: say "your own" full run at the head commit, in your own worktree and a scratch `--out` dir that is not 05's. Say "never the head run made for 05, whoever made it (I2 or the orchestrator), even if the same-inputs check passes".
     - "I2's run" alone would miss 068's case: there, the orchestrator made the head run (01 F4).
   - run-item.md L18: one sentence. The orchestrator reads its rules here, and in 068 the orchestrator told I3 not to re-run.
   - templates/verification.md L8: change "re-runs diff_reports.py on the same dirs" to "on 05's base dir and its own head-run dir". Otherwise the template keeps telling I3 to diff 05's head dir (01 F8).
   - This is a third file beyond request.md's "one line (and run-item.md if needed)". R2 thinks it is in scope: "Done looks like" asks for no contradicting text, and L8 contradicts.
   - Base-run reuse stays as it is (i2 step 3 check, run-item.md L18 second half).
   - [.claude/agents/i3-verifier.md L13; .claude/commands/run-item.md L18; templates/verification.md L8; work/073/01-research.md F4, F8]
2. **Independent regeneration of published numbers is standard practice in model validation, and it catches real differences that are not in the code.**
   - Independence of the checker:
     - SR 11-7: "validation is done by staff who are not responsible for model development or use".
     - Banco de España calls *réplica* "obtener resultados ya calculados por la entidad" (obtaining results the bank has already calculated). That is exactly I3 regenerating 05's numbers.
     - MaRisk commentary asks for "Funktionstrennung zwischen Entwicklung und Validierung" (separation of development and validation).
   - What a re-run catches that the code does not show:
     - A NinjaTrader user got ~$100k, ~$145k and ~$165k from "identical" PCs. The replies point to differing data and per-install settings.
     - Portuguese source: library versions and hardware add variability "mesmo quando se usa o mesmo dataset, base de código e ambiente" (even with the same dataset, code base and environment).
   - So I3's own run independently checks the head worktree's state, the data and the environment, not just the commit SHA. 068's head-run check compared only `ccbot/ config/` (06 L87).
   - [federalreserve.gov SR 11-7 p.3; repositorio.bde.es 03_Validacion_IRB p.84; 1plusi.de MaRisk Fachbeitrag; discourse.ninjatrader.com thread 6175; aimultiple.com/pt/reproducible-ai]
3. **Make the comparison concrete and cheap, with no new code. I3's run must give a byte-identical diff, and any difference is a finding.**
   - realtest is single-threaded and its Monte Carlo is seeded: `monte_carlo(..., seed=7)`, `rng = random.Random(seed)`. A grep finds no multiprocessing in realtest.py. [ccbot/realtest.py L710, L714]
   - So I3's `diff_reports.py --max-rows 0 <05 base> <I3 head>` output should be `cmp`-identical to 05's. 068/06 already did a `cmp` (06 L90), and A1 re-did it.
   - Have I3 write in 06: its own head dir, worktree path and SHA, run time and log file, Python/pandas versions, the data hash, and "`cmp` with 05's diff output: identical / differs (<lines>)".
   - The Mandarin source makes the same kind of check: the matching results were "经过逐笔校验完全一致" (checked trade by trade, fully identical).
   - Leave the optional check_pipeline dir-name check (01 Q4) to the efficiency list:
     - It proves only that two names differ (01 F16).
     - It would touch scripts/check_pipeline.py, which item 071 is editing in parallel.
   - [ccbot/realtest.py L710-714; work/068/06-verification.md L90; m.gelonghui.com/p/4745081; work/071/request.md L8]

## 3 ways AGAINST
1. **On a deterministic engine, a second run of the same code on the same data mostly repeats a result. It does not test it independently.**
   - The reproducibility literature separates "repeatability" ("the same investigators" get the same result) from reproducibility by "independent investigators". Of running the same program on the same setup it says "only that someone else pushes a button. This has little if any value." [arxiv.org/pdf/2011.10098]
   - A study of 5 backtest engines found "all engines agree exactly" at zero cost. Seven undocumented defects (one is a Backtrader default that divides the commission rate by 100) were found only by "multi-engine comparison". [arxiv.org/pdf/2603.20319, abstract]
   - So I3's own run cannot find a logic bug in realtest.py. It will reproduce the bug byte for byte. The independent checks of the logic are still I3's tests, mutations and line-by-line reading (i3 steps 2-3).
   - Mitigation: the rule should say what the run proves: the published numbers come from the head commit, data and environment. It should not suggest more.
2. **Cost: +1 full run per triggered item. Measured at 13m42.704s = 13.71 min.**
   - A triggered item needs 2 to 3 full runs: 2 x 13.71 = 27.42 min, 3 x 13.71 = 41.13 min. 068's practice was 1 run (01 Numbers).
   - The MaRisk commentary notes that such requirements tie up capacity: "die Umsetzung entsprechende Kapazitäten bindet".
   - SR 11-7 ties rigor to materiality: "more extensive and rigorous" where models materially affect decisions. Here the numbers are information for a ~$3k account, and no order depends on them (01 Fit).
   - A 14-minute run is also exposed to container restarts. 068's shared run came from exactly that (05 Deviations, 06 L24).
   - Mitigation: the rule must say that if I3's run is interrupted, I3 re-runs. It never falls back to 05's head run. Otherwise a restart brings the 068 pattern back.
   - [logs/audit/2026-11-17-068.md L75; work/073/01-research.md Numbers; 1plusi.de; federalreserve.gov SR 11-7 p.2]
3. **The rule stays text only, and RI-010's root cause says text-only duties get skipped first.**
   - Nothing checks that 06's head dir differs from 05's, or that I3 ran realtest at all. A copied dir, or 05's dir renamed, passes. Gap (o) already says a TOTAL line "proves a paste, not that it is current".
   - The person reads I3's numbers as independent, but only A1's reading of 06 enforces that. In 068, A1 was told not to re-run a full backtest either (068 audit L55).
   - Mitigation inside this item: the 06 fields in FOR 3 (own dir, log time, `cmp` result) give A1 something concrete to spot-check: a log time after 05's, and a dir that is not 05's.
   - The automated check stays a candidate for the efficiency list (01 Q4, F16).
   - [logs/recurring-issues.md L120; scripts/check_pipeline.py L123-125; logs/audit/2026-11-17-068.md L55, L83-85]

## Findings by language
Random languages this cycle: German, Korean, Portuguese (the last cycle, 069 on 2026-11-17, used French, Italian, Dutch; logs/research/2026-11-17.md L6).

No source found is about covered calls specifically. Independent re-running of a backtest is a validation and reproducibility topic, so the sources are model-risk rules and backtest-reproducibility writing.

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | FOR: validation independent of the developer. AGAINST: a same-code re-run is repeatability, not replication; engine defects need a second engine. HOLE: "identical" setups gave different PnL (data, per-install settings). | https://www.federalreserve.gov/supervisionreg/srletters/sr1107.pdf ; https://arxiv.org/pdf/2011.10098 ; https://arxiv.org/pdf/2603.20319 ; https://discourse.ninjatrader.com/t/nconsistent-backtest-results-on-3-identical-pcs-same-data-code-settings-huge-pnl-differences-100k-vs-145k-vs-165k-over-6-years/6175 | "Generally, validation is done by staff who are not responsible for model development or use" / "only that someone else pushes a button. This has little if any value." / "At zero transaction cost all engines agree exactly" / "PC1: ~$100,000 net profit PC2: ~$145,000 PC3: ~$165,000" | (English originals) |
| Mandarin Chinese | FOR: deterministic replays must match trade by trade, and the check is exact equality. | https://m.gelonghui.com/p/4745081 | "各倍速下 Swordfish 的撮合结果经过逐笔校验完全一致。" | "At every replay speed, Swordfish's matching results were checked trade by trade and were fully identical." |
| Spanish | FOR: replication (regenerating results the institution already computed) is a named validation procedure. | https://repositorio.bde.es/bitstream/123456789/23041/1/03_Validacion_IRB.pdf | "Los procedimientos de réplica consisten en obtener resultados ya calculados por la entidad" | "Replication procedures consist of obtaining results already calculated by the institution" |
| Japanese | HOLE: a seeded Monte Carlo stays reproducible only if the per-core split is fixed. realtest's MC is single-threaded (`random.Random(seed)`, L714), so this does not apply today. Recheck it if realtest is ever parallelised. | https://zenn.dev/mtec_blog/articles/dd72254537acda | "再現性を担保する上では、１コア当たりのシミュレーション回数を固定しておく必要がある。" | "To guarantee reproducibility, the number of simulations per core must be fixed." |
| German (random) | FOR: separation of development and validation. AGAINST: the requirement ties up capacity (cost). | https://1plusi.de/wp-content/uploads/2024/02/Fachbeitrag-MaRisk-Modul-Modelle-und-Validierung.pdf | "Anforderungen an eine „angemessene" Funktionstrennung zwischen Entwicklung und Validierung" / "die Umsetzung entsprechende Kapazitäten bindet" | "Requirements for an 'appropriate' separation of functions between development and validation" / "implementation ties up corresponding capacity" |
| Korean (random) | FOR: a backtest report proves nothing by itself, so write down the reproduction conditions and run it yourself. | https://algolab.co.kr/blog/backtest-statistical-significance-test-2026 | "재현 조건을 전부 적어 두었으니 직접 돌려 확인하시는 편이 좋습니다." | "We have written down all the reproduction conditions, so it is better to run it yourself and check." |
| Portuguese (random) | HOLE: library versions and hardware add variability even with the same data, code and environment. So record Python/pandas versions in 06 and compare them with 05's. | https://aimultiple.com/pt/reproducible-ai | "Diferenças nas versões dessas bibliotecas podem introduzir variabilidade adicional" | "Differences in the versions of these libraries can introduce additional variability" |

Searches that gave nothing usable: a Mandarin search for 回测 复现 独立验证 (results were English papers, and a bilibili page had no body text); the ECB internal-models page in Spanish (no sentence on independence); a Portuguese Banco Central / MRM search (okai.com.br fetch failed; the Management Solutions page has no relevant sentence); Korean wikidocs pages (fetch failed).

## Holes to watch out for (summary)
- **Trigger mismatch (for R3/I1 to decide).**
  - i3-verifier.md L13 and run-item.md L18 start with "If/When the item changes `ccbot/realtest.py`".
  - The Real-data field fires on all of TRIGGER: realtest.py, costs.py, expiries.py, config.py, pricing.py, config/default.json, tickers.json, holidays.json and data/real/.
  - An item that changes only config/default.json must paste a TOTAL line, but the head-run sentence does not literally apply to it.
  - Either word the new line as "when the item changes realtest's decision path (TRIGGER/TRIGGER_DIRS in scripts/check_pipeline.py)", or record that this was left out on purpose. [scripts/check_pipeline.py L183-186; templates/verification.md L8]
- **Separate `--out`.** I3's head dir must be new. If I3 reuses 05's path, its run overwrites 05's evidence and the `cmp` compares a dir with itself.
- **Interrupted run.** I3 re-runs. It never falls back to 05's head run (AGAINST 2).
- **Whoever made it.** The wording must cover a head run made by the orchestrator, not only by I2 (01 F4).
- **Base reuse unchanged.** Don't let the new sentence read as "I3 makes its own base too". The base keeps the i2 step 3 same-inputs check.
- **What the run proves.** It proves the numbers come from the head commit, data and environment. It does not prove the logic is right (AGAINST 1). Keep the tests, mutations and reading as the logic checks.
- **No full run at all.** Under 070, every trigger item needs the TOTAL paste, so a full run is always needed. R3 should confirm there is no exception (01 Edge case).
- **Determinism assumption.** It holds because the MC is single-threaded with seed 7 (realtest.py L710-714). If realtest is ever parallelised, recheck it (Japanese row).
- **Scope and overlap.**
  - Three RULE_PATHS files, so this is a RULES change and needs the person's OK in PR review.
  - Item 072 edits run-item.md L14, and 073 edits L18: expect a hand-merged conflict, not a conflict of meaning.
  - Don't touch scripts/check_pipeline.py here; 071 is in it.
  - Don't extend the rule to A1. Whether A1 re-runs is a separate question.
