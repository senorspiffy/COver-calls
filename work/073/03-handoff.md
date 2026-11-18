# 03 Research hand-off - 073
Status: READY (the orchestrator must paste `check_handoff.py 073` output below and it must say PASS; R3 has no shell. If it does not say PASS, the item comes back to R3.)

Type IDEA, Scope FULL. The person chose "Always own run" (request.md L11; logs/audit/2026-11-18.md L28, 2026-11-18 02:31 UTC). This hand-off does not reopen that choice. It changes text only: two `.claude/` files and one template, all RULE_PATHS (scripts/check_pipeline.py L193). So this is a RULES change and needs the person's OK in PR review. Nothing in ccbot/, config/, data/, reports/, scripts/, tests/ or 001 changes. Nothing connects to a brokerage.

## Fact check
Every repo path:line was opened. Every URL was fetched on 2026-11-18. Non-English quotes were checked against the original text.
| # | Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|---|
| 1 | 01 F1: in 068 the orchestrator made one head run (068-after) and both I2 and I3 used it | logs/audit/2026-11-17-068.md L14-15; work/068/06-verification.md L24, L87 | VERIFIED | - |
| 2 | 01 F2: I3 skipped its own run "on the orchestrator's instruction", relying on an empty `git -C wt-068-head diff --stat 8f384c9 -- ccbot/ config/` | work/068/06-verification.md L24, L87 | VERIFIED | - |
| 3 | 01 F3: A1 called it a disclosed deviation, not an error (old i3 text), and asked the person to choose | logs/audit/2026-11-17-068.md L16-20, L82 | VERIFIED | - |
| 4 | 01 F4: the head run was made by the orchestrator, not I2 | 01 cites work/068/05-build-report.md L96 and 06 L87 | WRONG (citation only) | 05 L96 names only the worktree `wt-068-head`. The orchestrator is named at 05 L140 (Deviations: "The orchestrator then made both full real-data runs") and at 06 L87. Claim kept with the 05 L140 source. |
| 5 | 01 F5: i3-verifier.md L13 says "make one full run at the head commit for the numbers in 06"; it never says the run must be I3's own; the same-inputs clause covers only the base | .claude/agents/i3-verifier.md L13 | VERIFIED | - |
| 6 | 01 F6: run-item.md L18 says "once per step that publishes numbers"; its reuse clause names only the base | .claude/commands/run-item.md L18 | VERIFIED | - |
| 7 | 01 F7: i2-builder.md L20 (step 3) is I2's own head run plus base reuse; no change needed | .claude/agents/i2-builder.md L20 | VERIFIED | - |
| 8 | 01 F8: templates/verification.md L8 ends "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's", which points I3 at 05's head dir | templates/verification.md L8 | VERIFIED | - |
| 9 | 01 F9: templates/build-report.md L10 says nothing about who makes the head run | templates/build-report.md L10 | VERIFIED | - |
| 10 | 01 F10: check_pipeline docstring gap (o): a TOTAL line "does not prove 06's TOTAL equals 05's (I3 still compares, templates/verification.md)" | scripts/check_pipeline.py L123-125 | VERIFIED | - |
| 11 | 01 F11: the logs/ mentions are historical (068 audit L14-20, L82; 2026-11-17 L14; 2026-11-16 L39; 065 audit L103; 2026-11-13 L33; efficiency 2026-11-16 L3) | Grep `full run\|head run\|reuse` over logs/ | VERIFIED | Same 7 locations found. None is edited. |
| 12 | 01 F12: no other .claude/, templates/ or scripts/ file matches the grep | Grep over .claude/, templates/, scripts/ | VERIFIED | 4 hits: i2-builder L20, i3-verifier L13, run-item L18, verification.md L8. |
| 13 | 01 F13: real-data runs are deterministic (fixed-seed MC), so I3's own head run should give a byte-equal diff output | work/068/06-verification.md L24; audit 068 L18; ccbot/realtest.py L710, L714 | VERIFIED | R3 grep over ccbot/ for `multiprocessing, concurrent.futures, threading, np.random, default_rng, random.seed, PYTHONHASHSEED`: 0 hits. The only RNG is `random.Random(seed)` at L714. Sets in realtest.py are sorted (L188) or used only for membership (L352, L571). |
| 14 | 01 F14: the 05/06 Real-data dirs are named only in free text `- After:`; only 068 uses it | Grep `^- After: ` over work/ | VERIFIED | 2 hits: 068/05 L96 and 068/06 L87. |
| 15 | 01 F15: check_pipeline already has TRIGGER, TRIGGER_DIRS, WHOLE_DIFF_FROM = 70 and a 05/06 section reader that reads inside fences | scripts/check_pipeline.py L111-118, L180-191 | VERIFIED | - |
| 16 | 01 F16: a dir-name check proves only that the names differ; a copied dir passes | scripts/check_pipeline.py L123-125 (gap o has the same shape) | VERIFIED | This follows from the logic. The check is left out (map step 6). |
| 17 | 01 Numbers: one full run 13m42.704s = 822.7 s = 13.71 min | work/068/05-build-report.md L97; audit 068 L75 | VERIFIED | 822.704 / 60 = 13.712. |
| 18 | 01 Numbers: "the orchestrator's note says ~13.7 min, from memory of item 067" | none in the repo (a message to R1) | UNSUPPORTED | Removed. The measured 068 figure (row 17) is used instead. |
| 19 | 01 Numbers: 068's practice was 1 full run (a shared head run plus a reused base) | audit 068 L20 | VERIFIED | - |
| 20 | 01 Numbers: under 073, 2 to 3 full runs: 27.42 and 41.13 min | arithmetic | WRONG (rounding and an edge case) | 3 x 822.704 s = 2468.1 s = 41.14 min (41.13 came from the rounded 13.71). 2 runs = 27.42 min. A 4th run is possible: if 05's base run is gone by I3 time, i3 L13 says "run the base too" (4 x 822.704 s = 54.85 min). |
| 21 | 01 Numbers: the extra cost against 068's practice is +1 run = +13.71 min per item | arithmetic | VERIFIED | - |
| 22 | 01 Numbers: 068/03 assumed 2 to 3 runs at 11.342 min = 22.7 to 34.0 min | work/068/03-handoff.md L95-96 | VERIFIED | 2 x 11.342 = 22.68; 3 x 11.342 = 34.03. |
| 23 | 01 Numbers: the 5-name `--tickers` run took 237.3 s = 28.8% of a full run | audit 068 L75; work/068/06-verification.md L149, L158 | VERIFIED | 237.339 / 822.704 = 0.2885. |
| 24 | 01 Fit: no trading rule, bot code or real-data output changes | this map | VERIFIED | Map steps 1-3 edit only .claude/ and templates/. |
| 25 | 01 OQ1: wording for i3 L13 | .claude/agents/i3-verifier.md L13 | WRONG (incomplete) | Kept, with three additions: it must also cover TRIGGER items that are not ccbot/realtest.py (decision D1), the run must be made after 05 exists, and a cut-off run is re-run (02 AGAINST 2). Final text in map step 1. |
| 26 | 01 OQ2: wording for run-item L18 | .claude/commands/run-item.md L18 | WRONG (incomplete) | Kept, with the same scope and re-run additions as row 25. Final text in map step 2. |
| 27 | 01 OQ3: templates/verification.md L8 must change, or contradicting text remains | templates/verification.md L8; request "What we want" | VERIFIED | In scope (decision D2). |
| 28 | 01 OQ4: the optional head-dir check is not free (template field, start constant, parser, fixtures) | scripts/check_pipeline.py L111-130, L183-191 | VERIFIED | Left out (decision D3). |
| 29 | 01 overlap: 072 edits run-item.md L14 and the r1/r2/r3/i1 agent files; 073 edits L18 | work/072/request.md L8, L16; .claude/commands/run-item.md L14, L18 | VERIFIED | Expect a merge conflict to resolve by hand, not a conflict of meaning. |
| 30 | 01 overlap: 071 edits scripts/check_pipeline.py | work/071/request.md L8 | VERIFIED | 073 does not touch that file. |
| 31 | 01 overlap: 074 is a new probe script plus a1-auditor.md, so no overlap | work/074/request.md L8, L19 | VERIFIED | - |
| 32 | 01: .claude/ and templates/ are RULE_PATHS, so this is a RULES change | scripts/check_pipeline.py L193 | VERIFIED | - |
| 33 | 01 Edge case: under 070, every trigger item needs the Real-data paste, "so a full run is always needed" | scripts/check_pipeline.py L111-118; run-item.md L18; i2-builder.md L20; i3-verifier.md L13 | WRONG | check_pipeline requires only a TOTAL line, and a `--tickers` diff also prints one. The full-run duty in all three rule texts starts "If/When the item changes `ccbot/realtest.py`". So for the other 7 TRIGGER paths and data/real/, no text requires a full run today. Fixed by D1: I3's own full head run covers every TRIGGER item. Exceptions left for I3: 0. |
| 34 | 02: 068 is the only earlier case | Grep `head run\|reuse` over logs/ and work/ | VERIFIED | - |
| 35 | 02: I3 skipped its run on the orchestrator's instruction, so run-item L18 matters as much as i3 L13 | work/068/06-verification.md L24, L87 | VERIFIED | - |
| 36 | 02: A1 found 068's scratch `--out` rule is "agent text only" | audit 068 L83-85 | VERIFIED | - |
| 37 | 02: the RI-010 root cause is text-only duties with no field and no check | logs/recurring-issues.md L120 | VERIFIED | - |
| 38 | 02: RI-013 guardrail and gap (o) | logs/recurring-issues.md L144-147; check_pipeline.py L123-125 | VERIFIED | - |
| 39 | 02: R2s for 067, 068 and 070 logged `languages: N/A` | logs/research/2026-11-16.md L5-6; 2026-11-17.md L5 | VERIFIED | - |
| 40 | 02 FOR 1: one rule in three places; "I2's run" alone misses 068's case | i3 L13; run-item L18; verification.md L8; 068/06 L87 | VERIFIED | - |
| 41 | 02 FOR 2: SR 11-7: "Generally, validation is done by staff who are not responsible for model development or use" | https://www.federalreserve.gov/supervisionreg/srletters/sr1107.pdf p.3 | VERIFIED | - |
| 42 | 02 FOR 2 and Spanish row: Banco de España, "Los procedimientos de réplica consisten en obtener resultados ya calculados por la entidad" | https://repositorio.bde.es/bitstream/123456789/23041/1/03_Validacion_IRB.pdf printed p.84 (G. Moral, Estabilidad Financiera no. 7) | VERIFIED | Translation correct. The sentence goes on "utilizando las bases de datos y los algoritmos analizados en la fase de revisión de la metodología" (using the databases and algorithms reviewed in the methodology phase). That is the same code and data, which matches I3's case. |
| 43 | 02 FOR 2 and German row: "MaRisk commentary" asks for "Funktionstrennung zwischen Entwicklung und Validierung" | https://1plusi.de/wp-content/uploads/2024/02/Fachbeitrag-MaRisk-Modul-Modelle-und-Validierung.pdf p.4 | WRONG (source label) | The source is a 2024 article by 1 PLUS i GmbH (Gruber, Heuter, Stepanek) on the 7th MaRisk amendment (AT 4.3.5), not an official MaRisk commentary. The quote and its translation ("an 'appropriate' separation of functions between development and validation") are exact. |
| 44 | 02 FOR 2: NinjaTrader PCs gave ~$100k, ~$145k and ~$165k; the replies point to differing data and per-install settings | https://discourse.ninjatrader.com/t/nconsistent-backtest-results-on-3-identical-pcs-same-data-code-settings-huge-pnl-differences-100k-vs-145k-vs-165k-over-6-years/6175 | VERIFIED | The replies are suggestions, not a confirmed cause. Nothing here depends on the cause. |
| 45 | 02 FOR 2: Portuguese, "library versions and hardware add variability 'mesmo quando se usa o mesmo dataset, base de código e ambiente'" | https://aimultiple.com/pt/reproducible-ai | WRONG | That quote is from section 1 and is about random weight initialisation, dropout and SGD. The library-version sentence is in section 3: "Diferenças nas versões dessas bibliotecas podem introduzir variabilidade adicional ... mesmo quando o código e os dados são idênticos" (even when the code and data are identical). Claim kept with the section 3 quote. |
| 46 | 02 FOR 2: "068's head-run check compared only `ccbot/ config/` (06 L87)" | work/068/06-verification.md L87-89 | WRONG (incomplete) | 06 L87 checked ccbot/ and config/, L88 checked the data hash, and L89 the Python/pandas versions. What I3's own run adds is a fresh run: the worktree state and process at run time, not just files declared equal. |
| 47 | 02 FOR 3: realtest is single-threaded and its MC is seeded (`seed=7`, `random.Random(seed)`) | ccbot/realtest.py L710, L714; grep | VERIFIED | See row 13. |
| 48 | 02 FOR 3: 068/06 already did a `cmp` (06 L90), and A1 re-did it | work/068/06-verification.md L90; audit 068 L71 | VERIFIED | - |
| 49 | 02 FOR 3: I3 writes its own head dir, worktree, log, run time, versions, data hash and a `cmp` result in 06 | templates/verification.md L8; scripts/diff_reports.py L233-293 | VERIFIED (feasible) | The template already asks for SHA, data hash, versions and command. diff_reports output lines name files, never the dirs (L233, L268, L274, L281, L293), so `cmp` across differently named dirs is meaningful. Added in map step 3. |
| 50 | 02 Mandarin row: "各倍速下 Swordfish 的撮合结果经过逐笔校验完全一致" | https://m.gelonghui.com/p/4745081 | VERIFIED | Translation correct. The full sentence is about replaying DolphinDB data at 5x, 10x and 20x speed. The page is a sponsored DolphinDB piece and is used only as an analogy for an exact-equality check. |
| 51 | 02 FOR 3: leave the dir-name check to the efficiency list, because it touches 071's file | work/071/request.md L8 | VERIFIED | Decision D3. |
| 52 | 02 AGAINST 1: repeatability vs reproducibility; "only that someone else pushes a button. This has little if any value." | https://arxiv.org/pdf/2011.10098 (Gundersen, The Fundamental Principles of Reproducibility) | VERIFIED | - |
| 53 | 02 AGAINST 1: 5 backtest engines; "At zero transaction cost all engines agree exactly" | https://arxiv.org/pdf/2603.20319 abstract | VERIFIED | - |
| 54 | 02 AGAINST 1: seven defects were found "only by multi-engine comparison" | https://arxiv.org/pdf/2603.20319 abstract, Section 6 | WRONG (overstated) | The abstract credits the seven defects to forensic analysis of three engines during quality control, each flagged because its output differed from the other engines (Section 6). Separately, it calls multi-engine comparison the most effective diagnostic. "Only" is dropped. |
| 55 | 02 AGAINST 1: a Backtrader default silently divides the commission rate by 100 | https://arxiv.org/pdf/2603.20319 abstract, Section 6.1 (`percabs` default False) | VERIFIED | - |
| 56 | 02 AGAINST 1: I3's own run cannot find a logic bug, because it reproduces the bug | logic; ccbot/realtest.py L714 | VERIFIED | The rule text says what the run proves (map step 1). |
| 57 | 02 AGAINST 2: 2 to 3 full runs, 27.42 and 41.13 min | arithmetic | WRONG (rounding and an edge case) | Same correction as row 20: 41.14 min, and up to 4 runs (54.85 min) if 05's base is gone. |
| 58 | 02 AGAINST 2: German, "die Umsetzung entsprechende Kapazitäten bindet" | 1plusi.de PDF p.6 (Zusammenfassung) | VERIFIED | Translation correct. The source label is fixed in row 43. |
| 59 | 02 AGAINST 2: SR 11-7, "more extensive and rigorous" where models have a material impact | https://www.federalreserve.gov/supervisionreg/srletters/sr1107.pdf p.2 | VERIFIED | - |
| 60 | 02 AGAINST 2: 068's shared run came from a container restart | work/068/05-build-report.md L140; 06 L24 | VERIFIED | - |
| 61 | 02 AGAINST 2 mitigation: if I3's run is cut off, I3 re-runs and never falls back to 05's | 02 L52 | VERIFIED | In map steps 1 and 2. |
| 62 | 02 AGAINST 3: nothing checks that 06's head dir differs from 05's, or that I3 ran realtest | scripts/check_pipeline.py L111-130 (checks only that a TOTAL line exists) | VERIFIED | - |
| 63 | 02 AGAINST 3: in 068, A1 was told not to re-run a full backtest | audit 068 L55 | VERIFIED | - |
| 64 | 02: the random languages are German, Korean and Portuguese; 069 used French, Italian and Dutch | logs/research/2026-11-17.md L6 | VERIFIED | - |
| 65 | 02 Japanese row: "再現性を担保する上では、１コア当たりのシミュレーション回数を固定しておく必要がある。" | https://zenn.dev/mtec_blog/articles/dd72254537acda | VERIFIED | Translation correct ("to guarantee reproducibility, the number of simulations per core must be fixed"). It does not apply today (row 13). |
| 66 | 02 Korean row: "재현 조건을 전부 적어 두었으니 직접 돌려 확인하시는 편이 좋습니다." | https://algolab.co.kr/blog/backtest-statistical-significance-test-2026 | VERIFIED | Translation correct. It is from the article's FAQ "Should I just trust the numbers in this article?" |
| 67 | 02 Portuguese row: "Diferenças nas versões dessas bibliotecas podem introduzir variabilidade adicional" | https://aimultiple.com/pt/reproducible-ai section 3 | VERIFIED | Translation correct. |
| 68 | 02 hole: i3 L13 and run-item L18 start with "If/When the item changes `ccbot/realtest.py`", while the Real-data field fires on all of TRIGGER and TRIGGER_DIRS | i3-verifier.md L13; run-item.md L18; check_pipeline.py L183-186; verification.md L8 | VERIFIED | Settled by D1. |
| 69 | 02 hole: I3's `--out` must be new, or it overwrites 05's evidence and `cmp` compares a dir with itself | logic | VERIFIED | In map steps 1 and 3. |
| 70 | 02 hole: don't touch scripts/check_pipeline.py here (071) | work/071/request.md L8 | VERIFIED | - |

**Totals:** 70 rows checked → **59 VERIFIED as-is**, **10 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- Row 18: "the orchestrator's note says ~13.7 min, from memory of item 067". No repo source. The measured 13m42.704s from 068/05 L97 replaces it in every number.

## Decisions on R1/R2 open points (with reasons)
- **D1 Rule scope (R2's open gap): the new "own head run" sentence covers every item whose 06 needs the Real-data TOTAL line, meaning TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py (L183-186: 8 paths plus data/real/), not only ccbot/realtest.py.**
  - Reasons:
    - The person chose "always".
    - templates/verification.md L8, the field I3 fills, already uses this scope.
    - With a realtest.py-only scope, an item that changes only config/default.json would still need a TOTAL line in 06, but no text would say whose head run it comes from. That is exactly 068's hole.
  - The scope is written inside the new sentence. The existing iteration and full-run clauses for I2 (run-item L18 first half, i2-builder L20) keep their ccbot/realtest.py trigger, because the person did not ask to change I2's duty.
  - Known gap G1: for a TRIGGER item that is not realtest.py, 05 may come from `--tickers` runs, so I3's full TOTAL may differ from 05's. I3 reports that as a finding with its reason (Missing inputs row 4), never as equal. Widening I2's full-run trigger is an efficiency-list candidate (map step 6).
- **D2 templates/verification.md L8 is in scope.** Its last sentence, "re-runs diff_reports.py on the same dirs", sends I3 to 05's head dir, which contradicts "What we want". Changing it is the smallest edit that leaves no contradicting text. It is one sentence in a template comment.
  - tests/test_real_data_field.py L149-155 requires the substring `from item 070 check_pipeline.py requires` in this comment, so that part stays unchanged.
- **D3 The optional "if cheap" head-dir check is not built here.** It needs a fixed template field, a start constant, a parser and fixtures in scripts/check_pipeline.py, which 071 is editing in parallel (row 30). It would prove only that two names differ (row 16). Instead, the template asks for concrete 06 fields (out dir, worktree, log file, wall time, `cmp` result) that A1 can spot-check. The automated check goes to the efficiency list (map step 6).
- **D4 Edge case: "no full run at all".** Under D1, every TRIGGER item gets I3's own full head run. Exceptions left: 0. A non-trigger item writes `not required (<file list>)` and makes no run, which is unchanged. 073 itself changes no TRIGGER path, so its own 05/06 write `not required (...)` and the item costs 0 full runs.
- **Out of scope (unchanged):** base-run reuse (i2 step 3 check; run-item L18 second half), A1's own re-run duty, i2-builder.md, templates/build-report.md, scripts/check_pipeline.py.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | **.claude/agents/i3-verifier.md step 2 (L13):** keep the sentence as it is and append exactly: " Your head run is always your own: one full run made by you after 05 exists, in your own worktree of the head commit, with a new scratch `--out` that is not 05's, for every item whose 06 needs the Real-data TOTAL line (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py, not only ccbot/realtest.py); never use the head run made for 05, whoever made it (I2 or the orchestrator), even if the same-inputs check passes; if your run is cut off, run it again; only the base run may be reused, under the check above. It shows that 06's numbers come from the head commit, data and environment, not that the logic is right (item 073)." | i3-verifier.md L13 | 1 appended sentence | `grep -c "item 073" .claude/agents/i3-verifier.md` = 1; `grep -c "item 068" .claude/agents/i3-verifier.md` = 1 (unchanged); the text "make one full run at the head commit" is still present (grep = 1). Replay on 068: 05 L96 names 068-after as 05's head run, so the new text forbids I3 using it, and I3 would have had to run. | Scope: 8 TRIGGER paths + 1 TRIGGER_DIRS prefix (check_pipeline.py L183-186). Items it applies to today: 0 of 071-074 (none of their requests names a TRIGGER path; the orchestrator confirms with the `REAL-DATA FIELD:` line). |
| 2 | **.claude/commands/run-item.md L18:** append exactly: " I3's head run is always its own full run, made for 06 with its own scratch `--out`, for every item whose 06 needs the Real-data TOTAL line (TRIGGER and TRIGGER_DIRS in scripts/check_pipeline.py): never give I3 the head run made for 05, even when the same-inputs check passes, and if I3's run is cut off, I3 runs it again; only a base run may be reused (item 073)." | run-item.md L18 | 1 appended sentence | `grep -c "item 073" .claude/commands/run-item.md` = 1; L18 still contains "counts as the base only if" (grep = 1). When the branch is merged with 072, L14 and L18 are both intact (hand-merged). | Same scope as step 1. |
| 3 | **templates/verification.md L8:** replace only the last sentence, "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's.", with: "I3 runs diff_reports.py on 05's base dir (or its own base run) and its own full head-run dir, never 05's head dir (item 073), and compares its TOTAL line with 05's. Also paste the head run's `--out` dir, worktree, log file and wall time, and `cmp` of this output with 05's diff output: identical, or differs (the differing lines)." | verification.md L8 | 1 changed sentence | `grep -c "same dirs" templates/verification.md` = 0; `grep -c "item 073" templates/verification.md` = 1; `grep -c "from item 070 check_pipeline.py requires" templates/verification.md` = 1; `python3 -m pytest -q tests/test_real_data_field.py -k t7d` passes (2 ids). | `cmp` is meaningful across dir names: 0 diff_reports output lines name a dir (scripts/diff_reports.py L233-293). 068 evidence: two separate runs (068-after, 068-tk) gave byte-identical trades files, 5 of 5 (068/06 L152). |
| 4 | **No change, confirmed:** .claude/agents/i2-builder.md, templates/build-report.md, scripts/check_pipeline.py, logs/ history | - | - | `git diff --stat <base>..HEAD -- . ':!work' ':!logs'` lists exactly 3 files: .claude/agents/i3-verifier.md, .claude/commands/run-item.md, templates/verification.md. I2 takes the count from the command, never by hand. | - |
| 5 | **Pipeline and suite checks (I2 records, I3 re-runs)** | branch HEAD | pasted output | `python3 -m pytest -q` total equals the base total (no test added or removed). `python3 scripts/check_pipeline.py`: 073 not SKIPPED or INCOMPLETE; `REAL-DATA FIELD:` does not name 073; 05/06 Real-data say `not required (<git diff --stat file list>)`. | - |
| 6 | **Follow-ups for A1's efficiency list (written in 05, not built):** (a) a check_pipeline check that 06 names a head-run `--out` dir different from 05's and a log time after 05's commit (D3; after 071 lands); (b) G1, widening the full-run trigger in run-item L18 first half, i2-builder L20 and i3 L13 first half from ccbot/realtest.py to TRIGGER/TRIGGER_DIRS. | 05 | 2 named candidates | 05 has a `Follow-ups for A1` list with (a) and (b); A1 copies them to logs/efficiency/ on main. | - |

## Missing inputs
Step 3a (ticker screen vs `screen.TESTS` / `MISSING_POLICY`): not applicable, because no ticker is screened. The rows below cover I3's inputs under the new text.
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| 05's base full-run dir (i3 L13) | gone, or its inputs differ from the base's | Unchanged rule: I3 runs the base too (item 068). 06 says which. |
| I3's own head run (step 1) | cut off (container restart, timeout) | I3 runs it again. It never falls back to 05's head dir. If it can't be finished, the verdict is FAIL "own head run not made (<why>)". It is never PASS on 05's run. |
| 05's TOTAL line | missing | check_pipeline already reports INCOMPLETE for 05 (item 070). I3 sends the item back to I2. |
| 05's head or base was a `--tickers` run (possible only for a TRIGGER item that is not realtest.py, gap G1) | no full 05 TOTAL to compare | 06: "TOTAL compare: n/a (05 used `--tickers <list>`)", plus I3's own full base and head TOTAL. It is never written as equal. |
| 05's saved diff output file (for `cmp`) | scratch file gone | 06: "cmp: n/a (05's diff output file gone: <path>)". The TOTAL line is still compared with 05's pasted TOTAL. |
| Head run's log file or wall time | not captured | 06: "wall time: unknown (<why>)". The value is never copied from 05. |
| Data hash or Python/pandas version at I3's run | not computed | 06: "unknown (<why>)". The value is never copied from 05. |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| One full run | 13m42.704s / 60 | 13 x 60 + 42.704 = 822.704 s; 822.704 / 60 = 13.712 min | 13.71 min |
| Runs per triggered item under 073 | I2 head + I3 head + 05 base (0 or 1) + I3 base if 05's is gone (0 or 1) | 2 x 822.704 = 1645.408 s = 27.42 min; 3 x = 2468.112 s = 41.14 min; 4 x = 3290.816 s = 54.85 min | 2-3 typical, 4 at most (rows 20, 57 fixed) |
| Extra against 068's practice | (2 - 1) runs | 1 x 13.712 = 13.71 min | +13.71 min |
| 068/03's old count | (2 or 3) x 11.342 | 22.684 → 22.7; 34.026 → 34.0 | matches 068/03 L96 |
| `--tickers` share | 237.339 / 822.704 | 3m57.339s = 237.339 s; 237.339 / 822.704 = 0.2885 | 28.8% |
| This item's own run cost | TRIGGER paths changed by 073 | 0 of 9 (the map touches only .claude/ and templates/) | 0 full runs; 05/06 `not required` |
| Step 1-3 grep counts | `grep -c "item 073"` per file | 1 new sentence per file, each with one `item 073` → 1, 1, 1; "same dirs" was 1 in verification.md L8, the replaced sentence removes it → 0 | 1/1/1 and 0 |
| Step 3 test anchor | test_t7d substring `from item 070 check_pipeline.py requires` | The replaced sentence is after this substring in L8, which stays unchanged → count 1 | test still passes |
| Worked example: 068 under the new rule | trigger "never use the head run made for 05, whoever made it" | 05 L96 names `068-after` as its head run; 06 L87 uses `068-after` → that is the head run made for 05 → the rule fires → I3 must make its own run in a new `--out` | the rule catches 068's case |
| Worked example: cut-off run | trigger "if your run is cut off, run it again" | 068's shared run followed a container restart (05 L140); under the new text I3 re-runs, so there is no path back to 05's run | the rule catches it |
| Step 1 scope count | len(TRIGGER) + len(TRIGGER_DIRS) | 8 + 1 = 9 (check_pipeline.py L183-186) | 9 |

Recurring issues checked: RI-001 (ESCALATED), RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-010, RI-013 (RI-003, RI-008, RI-011, RI-012: not applicable, since no calendar, Python code, branch diff or text classifier is touched).
- RI-001: no market filter. The one scope rule has a computed count (9 paths, 0 of 071-074 affected today). The "no full run" edge has a count (0 exceptions, D4). The 01 "always" claim is corrected (row 33).
- RI-002: every absent input in the Missing inputs table blocks or shows n/a with a reason. Nothing is copied from 05 or defaulted.
- RI-004/005: each worked example is run against the trigger it shows, and the cost numbers are re-derived above (2 rounding/edge fixes).
- RI-006: counts come from the table. The orchestrator pastes check_handoff output below, and the log line uses its counts.
- RI-007: Scope FULL, so I1-I3 run. No code, so item 062/064 do not apply. A RULES change needs the person's OK.
- RI-009: overlap with 072 (run-item.md) and 071 (check_pipeline.py, not touched) is named.
- RI-010: this is another text-only duty. The mitigation is concrete 06 fields that A1 can spot-check, plus a check_pipeline candidate (map step 6a).
- RI-013: I3's own diff is compared with 05's by TOTAL line and `cmp`.

check_handoff output (run by the orchestrator):
(run by the orchestrator 2026-11-18 23:34 UTC, exit 0)
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 70
totals line: 70 rows -> 59 as-is, 10 fixed, 1 removed
PASS
```
