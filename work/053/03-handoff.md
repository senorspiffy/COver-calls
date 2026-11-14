# 03 Research hand-off - 053
Status: READY (`python3 scripts/check_handoff.py 053` → PASS, run by the orchestrator 2026-11-11 because R3 had no shell; output in Self-check.)
Recurring issues checked (R3): RI-007 (this item; guardrail in map steps 1–5), RI-002 (new look-ahead found in `tickers.enrich`, step 7; Missing inputs table filled, no unknown PBR value filled), RI-001 (Feasibility column has counts for the commit filter and the earnings window), RI-004 / RI-005 (worked examples checked against their rules' triggers, Self-check), RI-006 (totals for the script, not hand-copied into the log), RI-009 / RI-011 (walk defined on HEAD's first-parent chain only, no merge-base guessing), RI-010 (log line left for `--log`, not typed by hand), RI-003 (2026-12-18 and 2026-12-23 checked against config/holidays.json: both trading days), RI-008 (step 2 note: no 3.12-only syntax).

Git facts verified by the orchestrator for R3 (no shell here): `git rev-parse --is-shallow-repository` → false; de5406c (PR #18) is a merge commit with parents 96b7f94 and 3ba835e; a541477 (052, PR #17) is not on origin/main but is in this branch's history (HEAD 87772a8, built on daily-fixes/2026-11-10, main merged in); `git show --stat 3ba835e` → config/tickers.json, tests/test_practice.py, work/048/05-build-report.md.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1: every `classify()` status comes from step files and 07's `A1 result:` lines; nothing in `main()` reads commit contents outside work/ and logs/ | scripts/check_pipeline.py `classify`, `main`, `open_branches` | WRONG (in part) | `open_branches()` also diffs `RULE_PATHS` (.claude/, templates/, scripts/check_*.py) on unmerged branches for RULES BRANCH. The correct claim: nothing reads code/config changes in HEAD's own history. |
| R1: the only git-history checks are `late_log_lines()` L232–256 and `open_branches()` L273–341 | scripts/check_pipeline.py | VERIFIED | |
| R1: 048 has every FULL step file and 07 L7 `A1 result: PASS (2026-11-07, ...)`, so it shows complete (classify L163–171) | work/048/07-audit-task.md L7; check_pipeline.py L163–171 | VERIFIED | |
| R1: work/048/05 ends with `## Follow-up 2026-11-11` (L12–13) | work/048/05-build-report.md | VERIFIED | |
| R1: 3ba835e changed config/tickers.json, tests/test_practice.py, work/048/05; check_pipeline on de5406c exit 0 | orchestrator `git show --stat 3ba835e`; logs/audit/2026-11-11.md L2, L11, L21 | VERIFIED | |
| R1: first fetch was `--depth 50`, "so this clone is **shallow**" | .git/logs/refs/remotes/origin/main L1; orchestrator `git rev-parse --is-shallow-repository` → false | WRONG | The reflog line does read `fetch --no-progress --depth 50`, but the clone is not shallow now. Shallow handling stays in the design for other clones (CI, fresh `--depth` clones). It is not a risk for this clone. |
| R1: this branch got main by a merge commit (87772a8, ort) | .git/logs/HEAD L9 | VERIFIED | |
| `git rev-list A..B`: reachable from B, not from A | https://git-scm.com/docs/git-rev-list | VERIFIED | |
| `--no-merges` skips commits with more than one parent | https://git-scm.com/docs/git-rev-list | VERIFIED | Doc: "exactly the same as `--max-parents=1`". |
| `--since` may stop at the first older commit; `--since-as-filter` visits all commits | https://git-scm.com/docs/git-rev-list | VERIFIED | The stopping is stated in the `--since-as-filter` text ("rather than stopping at the first commit which is older"). |
| `diff-tree -r --name-only --no-commit-id`; merges have special handling (`-m`, `-c`, `--cc`) | https://git-scm.com/docs/git-diff-tree | VERIFIED | |
| Petrobras IR notice 13 Oct 2026: 3Q26 results 10 Nov after close, webcast 11 Nov 11:30 Brasília (mirror) | https://investidor10.com.br/acoes/link_comunicado/PETR3/50791/ | VERIFIED | |
| Preview of 9 Nov 2026: "divulga seus resultados em 10 de novembro, após o fechamento do mercado" | https://euqueroinvestir.com/acoes/o-que-esperar-do-balanco-da-petrobras-no-3t26 | VERIFIED | Translation checked: "releases its results on 10 November, after market close". |
| bpmoney (29 Oct 2026) said 11 Nov after close; contradicted | https://bpmoney.com.br/negocios/empresas/petrobras-petr4-dividendos-ate-42-bilhoes-3t26/ | VERIFIED | Page: "Em 11 de novembro, depois que o mercado encerrar". |
| Petrobras Agência, posted 2026.11.10: 3Q26 net income BRL 39.8 bn (US$ 7.7 bn); first paragraph says "2024" (typo) | https://agencia.petrobras.com.br/en/w/negocio/petrobras-registra-lucro-l%C3%ADquido-de-r-39-8-bilh%C3%B5es-no-terceiro-trimestre-de-2026 | VERIFIED | |
| InfoMoney 10 Nov 2026 20:31: R$ 39.75 bn vs LSEG consensus R$ 47.02 bn | https://www.infomoney.com.br/mercados/petrobras-petr4-balanco-3t26/ | VERIFIED | |
| No 3Q26 / remuneration 6-K on EDGAR | R3 search of sec.gov: newest Petrobras 6-Ks returned are pbr20260806_6k and pbrfs2q26usd_6k (Aug 2026) | VERIFIED | Still absent on 2026-11-11. The company newsroom (primary) is the source used. CVM not searched. |
| Dividend BRL 15.3 bn on the 30 Sep 2026 balance sheet, advance on fiscal-2026 remuneration, posted 2026.11.10 | https://agencia.petrobras.com.br/en/w/institucional/petrobras-aprova-pagamento-de-r-15-3-bilh%C3%B5es-aos-seus-acionistas | VERIFIED | |
| R$ 1.18732774 per common/preferred share, two installments of R$ 0.59366387 (2 × 0.59366387 = 1.18732774) | same Petrobras dividend URL | VERIFIED | The installments are Selic-adjusted from 31 Dec 2026, so the paid amounts will differ slightly. |
| Form (dividend and/or interest on equity) set by 10 Dec 2026 | same Petrobras dividend URL | VERIFIED | |
| Subject to withholding income tax (no rate given) | same Petrobras dividend URL | VERIFIED | |
| B3: record 21 Dec, ex 22 Dec 2026; paid 22 Feb and 22 Mar 2027 | same Petrobras dividend URL | VERIFIED | |
| NYSE ADR: record date 23 Dec 2026; installments 1 Mar and 29 Mar 2027 | same Petrobras dividend URL | VERIFIED | |
| No ADR ex-date, ADS ratio or USD per ADR published | same Petrobras dividend URL | VERIFIED | |
| Secondary: R$ 1.19, two installments, B3 record 21 Dec, ex 22 Dec | https://investirecocaresocomecar.com.br/petr4-dividendo-3t26-r-1-19/ | VERIFIED | |
| FINRA 11140(b) under T+1: ex-date "shall be the record date if the record date falls on a business day" | https://www.finra.org/rules-guidance/notices/24-04 | VERIFIED | Applies to distributions under 25% of the security's value. 2026-12-23 is a Wednesday, not in config/holidays.json. Ex = 23 Dec stays a derivation, not used (see 02 AGAINST 3). |
| 6-K of 6 Aug 2026: ADR record 25 Aug; ADR payments 1 Dec and 29 Dec 2026 | https://www.sec.gov/Archives/edgar/data/0001119639/000129281426004123/pbr20260806_6k.htm | VERIFIED | |
| oilandgas360 lead undated; $6 bn Q3 net income and R$ 12.16 bn interim dividend match the 2025 declaration (headline "dividendos de R$ 12,16 bilhões referentes ao exercício de 2025") | https://www.oilandgas360.com/petrobras-hikes-dividend-as-production-surge-offsets-lower-oil-prices/; https://euqueroinvestir.com/acoes/petrobras-anuncia-dividendos-de-r-1216-bilhoes-referentes-ao-exercicio-de-2025 | WRONG (quote) | The euqueroinvestir headline is "Petrobras anuncia dividendos de R$ 12,16 bilhões", dated 06 Nov 2025. "referentes ao exercício de 2025" is only in the URL. The conclusion stands: the lead is the 2025 declaration, not 3Q26. |
| PBR estimate: 2026-11-10 + 70 d = 2027-01-19; 2026-12-18 is the third Friday | arithmetic (Self-check) | VERIFIED | |
| R1: PBR's blocked set "stays `set()` with a correct `last_earnings`" (as 3ba835e's test edit asserts) | tests/test_practice.py L35–42 (day = 2026-11-09); ccbot/tickers.py L50–53 | WRONG | The test's day is 2026-11-09, before the 10 Nov report. `enrich` uses `last_earnings` without checking that it is on or before `day.date`, so on 11-09 PBR gets a 2027-01-19 estimate it could not know (look-ahead, RI-002). Correct result: 13 of 13 clear Dec 18 on days from 2026-11-11 on. On 2026-11-09, 12 of 13 clear and PBR does not. Fixed in map steps 7–8. |
| ADR record 2026-12-23 is 5 calendar days after the Dec 18 expiry | arithmetic (Self-check) | VERIFIED | |
| USD per ADR not computable (no ADS ratio, FX, or dividend/interest-on-equity split) | Petrobras dividend URL | VERIFIED | |
| `last_earnings` 2026-11-10 is confirmed by a primary source | Petrobras Agência results URL (posted 2026.11.10) | VERIFIED | |
| R1: read 07 at C's parent, "otherwise a commit that writes the A1 PASS line together with a code change hides the change" | logic against R1's own rule; logs/audit/2026-11-11.md L5, L18 (051/052 have A1 PASS on their branches) | WRONG (reason) | The reason is inverted. Reading at C would *flag* such a commit, and reading at the parent is what lets it pass. Reading at the parent is still right: a PR merge brings in 07 files that already hold A1 PASS (051 on PR #16, 052 on PR #17), and reading at C would flag every such merge. The gap is closed in map step 2: only step files 01–06 can cover code, and 07 is read only for its A1 line. |
| R2: RI-007 ESCALATED at 5; 026/031/035/038/042 all check step files | logs/recurring-issues.md L84–97 | VERIFIED | |
| R2: house pattern `LOG TIME: not checked (no git)`, closed lists `LOG_TIME_EXCEPT`, `PRE_A1_LINE` ("Never add") | scripts/check_pipeline.py L86–88, L97–100, L434 | VERIFIED | |
| R2: `tickers.ex_div_date` and `tickers.dividend` are `n/a`; neither has a fallback row | ccbot/missing.py L21–23 | VERIFIED | |
| R2: 041, a past `ex_div_date` is unknown | ccbot/tickers.py L56–58 | VERIFIED | |
| R2: reflog de5406c → a607ed4 (A1 daily, 053); branch at a541477 merged origin/main as 87772a8 | .git/logs/HEAD L7–9 | VERIFIED | Orchestrator: a541477 is not on origin/main. It is in this branch, so 052's code is already under this branch. |
| `--first-parent`: "follow only the first parent commit upon seeing a merge commit" | https://git-scm.com/docs/git-rev-list | VERIFIED | |
| R2: 3ba835e fails on main "as de5406c (diff vs a30101c = config/tickers.json, tests/test_practice.py, work/048/05)" | orchestrator: de5406c parents 96b7f94, 3ba835e | WRONG | The first parent is 96b7f94 (A1's 11-10 audit commit), not a30101c. The unit to judge is `git diff --name-only de5406c^1 de5406c`. Its file list should equal 3ba835e's stat. I3 confirms it with that command (step 4 check). |
| R2: `A..B` excludes everything reachable from A, so a branch cut before the cutoff and merged after it is still checked | https://git-scm.com/docs/git-rev-list | VERIFIED | On the first-parent walk only its merge commit is judged. |
| `rev-parse --verify "$VAR^{commit}"` and `--is-shallow-repository` quotes | https://git-scm.com/docs/git-rev-parse | VERIFIED | |
| R2: "This clone was fetched with `--depth 50`, so the cutoff ... falls out after about 50 newer commits. A1 should unshallow once." | orchestrator `--is-shallow-repository` → false | WRONG | Not shallow. Nothing falls out, and no unshallow is needed here. The `not checked` path stays for shallow clones elsewhere. |
| R2: PR #18 "probably" landed as a merge commit (UNVERIFIED) | orchestrator: de5406c has 2 parents | VERIFIED | It is confirmed a merge commit, so main's PRs land as merge commits today. |
| R2: an entered 2026-12-23 ex-date with unknown amount gives `EARLY_ASSIGN_CHECK_NA` for a held ITM call whose expiry is on or after it | ccbot/rules.py L214–219 | VERIFIED | |
| R2: 6-K Aug 2026: B3 record 21 Aug, B3 ex 24 Aug, ADR record 25 Aug, no ADR ex-date | https://www.sec.gov/Archives/edgar/data/0001119639/000129281426004123/pbr20260806_6k.htm | VERIFIED | |
| R2: stockanalysis lists ADR ex-div 25 Aug 2026 (so ADR ex = ADR record last cycle) | https://stockanalysis.com/stocks/pbr/dividend/ | VERIFIED | Row: ex 25 Aug 2026, $0.44103, record 25 Aug, pay 1 Dec 2026. This also confirms tickers.json's $0.44103. Page last checked 25 Oct 2026, so no Dec 2026 row. |
| Suno 2023: "ex-direitos" on B3 and NYSE from 22 Aug; ADR record 23 Aug | https://www.suno.com.br/noticias/?p=438168 | VERIFIED | Dated 03/08/2023. Translation checked. |
| Moomoo (Chinese): dividends may trigger early exercise; sellers should watch the risk | https://www.moomoo.com/us/hans/learn/short-call-options | VERIFIED | Both sentences present. Translation checked. |
| Rankia (Spanish) forum post: close everything before an imminent dividend | https://www.rankia.com/foros/bolsa/temas/1090294-call-cubierta | VERIFIED | Reply #2, 05/02/12. Opinion. |
| Matsui (Japanese): record date and ex-rights date are the same day | https://support.matsui.co.jp/faq/show/35901 | VERIFIED | Covers US stocks and ETFs. ADRs are not named. |
| Lynx (German): a short-call writer should watch dividend dates; early exercise only makes sense when the dividend exceeds the remaining time value | https://www.lynxbroker.de/artikel/vorzeitige-ausuebung-von-optionen-so-reagieren-sie-richtig | VERIFIED | The sentence is present (the fetch tool quoted its first half). Translation checked. |
| tmsstory (Korean): under T+1 the gap between record date and last buy date shrinks by a day | https://tmsstory.co.kr/배당-기준일-배당금-날짜/ | VERIFIED | Translation checked. |
| R2: a new fallback row is a rule change; 040's earnings fallback needed the person's OK | ccbot/missing.py L15 ("040, person's house rule"); logs/recurring-issues.md L45 | VERIFIED | |
**Totals:** 55 rows checked → **48 VERIFIED as-is**, **7 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None. The advice to unshallow this clone is replaced by the correct fact, so that row counts as fixed.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: `CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/", ".claude/")`. `UNTRACKED_FROM = "<40-char sha>"` = HEAD of daily-fixes/2026-11-11 just before I2's first code commit for 053 (it contains de5406c, so 3ba835e is before it). Comment: "item 053; never move it forward". I1 decides whether to add `templates/` (RULE_PATHS treats it as rules; the request does not list it). | – | constants | `git merge-base --is-ancestor <UNTRACKED_FROM> de5406c` exits 1 and `git merge-base --is-ancestor de5406c <UNTRACKED_FROM>` exits 0 (I3) | – |
| 2 | `untracked_changes()`: None without git. Cutoff check: `rev-parse --verify -q <cutoff>^{commit}` and `merge-base --is-ancestor <cutoff> HEAD`. If either fails and `--is-shallow-repository` is true → `not checked (cutoff <short> not in this shallow clone; run git fetch --unshallow)`. If either fails in a full repo → error (squash/rebase or wrong SHA). Walk `rev-list --first-parent <cutoff>..HEAD`. For each C: files = `diff --name-only C^1 C`. If any file starts with a CODE_PATH, C is covered only when it also changes `work/<ID>/<01–06 step file>` for an ID whose `C^1:work/<ID>/07-audit-task.md` is missing or has no `^A1 result:` line. 07 never covers code. Uncovered → `<short sha> <code files>`. Python ≥ 3.10 syntax (RI-008). | git history, work/ at C^1 | list, None, or a not-checked or error string | fixtures in step 4 | Commit filter on known history: 1 of 1 bad commit (3ba835e) matches: 2 of its 3 files are CODE_PATHS, and its only step file is work/048/05, whose 07 has A1 PASS (since 2026-11-07, so at any parent after then; I3 confirms with `git show 3ba835e^:work/048/07-audit-task.md`). After the cutoff on this branch: 0 commits when the constant is set; I2's code+05 commits, each covered by 053's 05. |
| 3 | `main()`: print `UNTRACKED CHANGE: none`, the list, or `not checked (...)`. List or error → exit 1; not checked → exit unchanged. Docstring entry with known gaps: (a) any open item's 01–06 file covers unrelated code in the same unit; (b) on a branch each direct commit is a unit, so commit code with your 05; (c) the PR must land as a merge commit; (d) a merge's conflict edits are judged with the whole merge against its first parent. | step 2 | report line, exit code | `test_untracked_line_printed`: line present, exit 1 on a fixture with an entry | – |
| 4 | tests/test_pipeline_check.py fixtures (temp git repos): (a) a commit editing a completed item's 05 + config → `UNTRACKED CHANGE`, exit 1; (b) a new item's 01 + code → none; (c) a merge whose second parent brings (a) → flagged on the first-parent walk; (d) cutoff missing in a `git clone --depth 1` fixture → `not checked`, exit 0; (e) cutoff missing in a full repo → exit 1; (f) commits before the cutoff ignored; (g) a commit changing only a completed item's 07 + code → flagged; (h) a merge bringing an item whose 07 already has A1 PASS on its branch, absent at C^1, plus code → none (PR #16/#17 shape). | fixtures | tests | all pass on the new code; (a), (c) and (g) fail if the check is removed (mutation). I3 also runs `git diff --name-only de5406c^1 de5406c` and confirms the 3 files. | 8 fixtures, each with one expected result |
| 5 | .claude/commands/run-item.md and .claude/agents/a1-auditor.md: "A follow-up to a completed item is a new item (053)"; "I2 commits code together with its 05 change"; "merge PRs with Create a merge commit, never squash or rebase"; "A1's daily commits never change CODE_PATHS". | – | 2 rule lines each | `grep -n "053" .claude/commands/run-item.md .claude/agents/a1-auditor.md` | – |
| 6 | config/tickers.json PBR: values unchanged (`last_earnings` 2026-11-10, `next_earnings` null, `ex_div_date` null, `dividend` null). Sources replaced with: the Petrobras Agência results URL (posted 2026.11.10); the Petrobras dividend URL with "ADR record date 2026-12-23, ex-date not published; amount per ADR not published (R$ 1.18732774/share in 2 installments, form set by 2026-12-10)"; the stockanalysis dividend URL with "last ex-div Aug 25 2026 $0.44103". No new keys. | Petrobras URLs above | tickers.json | `test_every_universe_ticker_has_sourced_facts`, `test_ticker_fields_cover_file_and_code` pass | – |
| 7 | ccbot/tickers.py `enrich`: a `last_earnings` after `day.date` is not a past report on that day, so no estimate is made from it (with `next_earnings` null → EARNINGS_UNKNOWN). ccbot/missing.py `tickers.last_earnings` text: add "a last_earnings after the scan date is unknown on that date (053)". | tickers.json, day.date | Day.next_earnings / earnings_known | new `test_enrich_future_last_earnings_is_unknown` (PBR-shaped fact, day 2026-11-09 → earnings_known False; day 2026-11-11 → next 2027-01-19, estimated). Mutation: remove the guard → fails. | Earnings window on config/practice.json: 12 of 13 clear Dec 18 on 2026-11-09 (PBR is the only last_earnings > 11-09), 13 of 13 on 2026-11-11 (earliest estimate KEY 2026-12-29 > 12-18). Computed from config/tickers.json in the Self-check. |
| 8 | tests/test_practice.py: day 2026-11-09 → `set(universe) - clear == {"PBR"}` (honest: it reports 11-10); add day 2026-11-11 → `set()`. Docstring names 053. | step 7 | test | both asserts pass after step 7; the 11-09 assert fails on today's enrich | same counts as step 7 |
| 9 | work/053/05 flags for the person, and the A1 report repeats them: don't open a Jan 2027 PBR call without the ADR ex-date (ADR record date 2026-12-23 is before a Jan expiry; no effect on Dec 18 calls). Offer IDEA "ADR ex = ADR record date (FINRA 11140), labelled" as a separate item. The step-7 look-ahead is listed for A1 as a possible RI-002 occurrence (A1 decides). | – | 05 text | read 05 | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git (check_pipeline.py run outside a git work tree) | `untracked_changes()` → None | `UNTRACKED CHANGE: not checked (no git)`, exit unchanged |
| cutoff commit, shallow clone | missing, or not an ancestor of HEAD | `UNTRACKED CHANGE: not checked (cutoff <short> not in this shallow clone; run git fetch --unshallow)`, exit unchanged |
| cutoff commit, full clone | missing, or not an ancestor of HEAD | `UNTRACKED CHANGE: cutoff <short> not in HEAD's history (squash/rebase or wrong SHA)`, exit 1. Never a silent pass. |
| `C^1:work/<ID>/07-audit-task.md` | absent at the parent | The item is not yet audited, so it is open. This is the rule's meaning, not a default. Only its 01–06 files can cover code. |
| `C^1` for the root commit | none | Not reachable: the walk starts after the cutoff, so every C has a first parent |
| tickers.last_earnings (PBR on a day before 2026-11-10) | after day.date | No estimate. With next_earnings null → `EARNINGS_UNKNOWN` (step 7) |
| tickers.next_earnings (PBR) | null (4Q26 date not published) | Fallback per house rule 040: 2027-01-19, labelled "estimated" |
| tickers.ex_div_date (PBR) | null (ADR ex-date not published) | "days to ex-dividend: n/a (not supplied)". The ADR record date goes in the sources text only. |
| tickers.dividend (PBR) | null (USD per ADR, ADS ratio, FX and form not published) | dividend/div_next NaN, never 0.0 |
| PBR screen result (price, quotes, OI, spread) | not computed in this item | No screen PASS is claimed for PBR. The only screen test this item touches is EARNINGS/EARNINGS_UNKNOWN (`screen.TESTS`). |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | as-is + fixed + removed = rows | 48 + 7 + 0 = 55 | ✓ |
| PBR estimate | 2026-11-10 + 70 d | Nov 11–30 = 20; + Dec 31 = 51; + Jan 1–19 = 19 → 70 → 2027-01-19 | ✓ |
| Dec 18 is the monthly expiry | third Friday of Dec 2026 | 2026-01-01 Thu; Dec 18 = day 352, (352 − 1) mod 7 = 1 → Fri; Fridays Dec 4, 11, 18 | ✓ |
| Earnings window threshold | estimate > 2026-12-18 ⇔ last_earnings > 2026-12-18 − 70 = 2026-10-09 | Dec 18 − 18 = Nov 30; − 30 = Oct 31; − 22 = Oct 9 (18+30+22 = 70). Earliest last_earnings is KEY 2026-10-20 > 10-09 | ✓ all 13 |
| Earliest estimate | KEY 2026-10-20 + 70 | Oct 21–31 = 11; + Nov 30 = 41; + Dec 1–29 = 29 → 70 → 2026-12-29 > 12-18 and > 11-11 | ✓ |
| 2026-11-09 count (step 7 guard) | last_earnings ≤ 2026-11-09 | PBR 11-10 > 11-09; the next latest are PFE and ITUB 11-03 ≤ 11-09 → 12 of 13 | 12/13 ✓ |
| 2026-11-11 count | last_earnings ≤ 11-11 and estimate > 12-18 | all 13 ≤ 11-10; min estimate 12-29 | 13/13 ✓ |
| ADR record vs expiry | 2026-12-23 − 2026-12-18 | 5 days; Dec 23 = Wed (Fri + 5), not in config/holidays.json | ✓ |
| Installments | 2 × 0.59366387 | 1.18732774 | ✓ |
| Worked example, 3ba835e shape (step 2 trigger: any CODE_PATH file and no covering 01–06 file of an item open at C^1) | files config/tickers.json, tests/test_practice.py, work/048/05 | 2 CODE_PATH files; covering candidates = work/048/05, but 048/07 at C^1 has A1 PASS → 0 covering | flagged ✓ |
| Worked example, PR #16 merge on main (fixture h) | 051 01–06 + scripts/check_pipeline.py vs first parent = main | 051/07 is absent on main at C^1 → open; 051's 01–06 change → covered | none ✓ |
| Worked example, A1 PASS + code (fixture g) | 07 + code only | 07 does not cover → 0 covering | flagged ✓ |

`python3 scripts/check_handoff.py 053` output (pasted, must say PASS):
```
Run by the orchestrator (R3 had no shell), 2026-11-11:
```
sources count (unique URLs in 01-research.md): 13
fact-check rows: 55
totals line: 55 rows -> 48 as-is, 7 fixed, 0 removed
PASS
```
```
