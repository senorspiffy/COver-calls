# 01 Research brief - 053
## Question
(1) How can `scripts/check_pipeline.py` detect a commit that changes `ccbot/`, `config/`, `scripts/`, `tests/` or `.claude/` without belonging to a work item still in the pipeline (the shape of 3ba835e)?
(2) PBR: did Petrobras release Q3 2026 results on/around 2026-11-10, and is there a newly declared dividend (ex-date, amount) for the NYSE ADRs? Are `last_earnings`, `ex_div_date`, `dividend` in config/tickers.json right under `ccbot/missing.MISSING_POLICY`?

Limits of this run: R1 had no shell in this session, so `git log`, `git show 3ba835e`, `check_pipeline.py` and `check_handoff.py` were not run by R1. Repo evidence below is from files read directly (`.git/logs/*`, work/, logs/, scripts/) and from A1's recorded runs. R2/R3 should re-run the git commands named here.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### Part 1: process bug (repo evidence; no market facts)
- Every status `classify()` gives comes from the step files present in `work/<ID>/` and the `A1 result:` lines in 07. Nothing in `main()` reads commit contents outside `work/` and `logs/` [repo: scripts/check_pipeline.py `def classify`, `def main`].
- The only git-history checks are `late_log_lines()` (git blame on logs/) and `open_branches()` (unmerged remote branches). Neither looks at commits already in HEAD that touch code/config [repo: scripts/check_pipeline.py L232–256, L273–341].
- 048 has every FULL step file and its 07 ends `A1 result: PASS (2026-11-07, ...)`, so it shows `complete` whatever is appended to its 05 later [repo: work/048/07-audit-task.md L7; scripts/check_pipeline.py L163–171].
- work/048/05-build-report.md now ends with `## Follow-up 2026-11-11` (PBR last_earnings set to 2026-11-10, next_earnings cleared) [repo: work/048/05-build-report.md L12–13].
- 3ba835e (21:50 UTC 2026-11-11, merged as PR #18, de5406c) changed config/tickers.json, tests/test_practice.py and work/048/05. `check_pipeline.py` on de5406c exited 0 [repo: work/053/request.md Evidence; logs/audit/2026-11-11.md L2, L11]. R1 did not re-run `git show 3ba835e --stat` (no shell): UNVERIFIED by R1, recorded by A1.
- Reflog: origin/main moved a30101c → de5406c by `fetch -q origin: fast-forward`. The repo's first fetch was `fetch --no-progress --depth 50 origin main`, so this clone is **shallow** and any history walk can hit the graft boundary [repo: .git/logs/refs/remotes/origin/main L1–2].
- The current branch daily-fixes/2026-11-11 got main by a merge commit (`merge origin/main: Merge made by the 'ort' strategy`, 87772a8) [repo: .git/logs/HEAD L9]. So a branch walk will meet merge commits that carry other people's changes.
- `git rev-list A..B` lists commits reachable from B and not from A [https://git-scm.com/docs/git-rev-list].
- `--no-merges` skips commits with more than one parent [https://git-scm.com/docs/git-rev-list].
- `--since` may stop at the first older commit. `--since-as-filter` "visits all commits in the range" [https://git-scm.com/docs/git-rev-list].
- `git diff-tree -r --name-only --no-commit-id <sha>` lists the files a commit changed. Merge commits get special handling (`-m`, `-c`, `--cc`) [https://git-scm.com/docs/git-diff-tree].

Design facts for R2/I1, derived from the above (not external claims):
- Test per commit C after the cutoff, with `--no-merges`: files = `diff-tree -r --name-only --no-commit-id C`. If any file starts with `ccbot/ config/ scripts/ tests/ .claude/`, C must also add or change `work/<ID>/<step file>` (a name in STEPS) for some ID whose 07 **at C's parent** (`git show C^:work/<ID>/07-audit-task.md`) is missing or has no `A1 result:` line. Otherwise print `UNTRACKED CHANGE: <sha> <files>` and exit 1.
- Read 07 at the parent, not at C. Otherwise a commit that writes the A1 PASS line together with a code change hides the change. 3ba835e fails either way: 048/07 had PASS since 2026-11-07.
- `request.md` alone is not a step file. A commit adding only request.md plus code fails, which matches "no code before its research".
- Cutoff: this item's merge SHA can't be written into the commit that builds it. Options: (a) a committer-date constant filtered in Python from `%ct` (or `--since-as-filter`, not `--since`); (b) the SHA added in a later commit. R2 to weigh.
- Shallow clone: if the cutoff commit is not in local history (`git cat-file -e <cutoff>` fails), the check must print a "not checked" line and not pass silently (same spirit as RI-002 and the `LOG TIME: not checked (no git)` line).
- Merge commits are skipped by `--no-merges`. A merge that resolves conflicts by editing code would not be seen. This is a known gap to list in the docstring, like the blame gap at L56–57.

### Part 2: PBR facts
- Petrobras IR notice (Rio de Janeiro, 13 Oct 2026, mirrored on investidor10): 3Q26 financial results on **10 Nov 2026 after market close**, webcast 11 Nov 2026 11:30 Brasília [https://investidor10.com.br/acoes/link_comunicado/PETR3/50791/]. This is a mirror of the IR text, not the IR site itself.
- A secondary preview (9 Nov 2026) gives the same date: "divulga seus resultados em 10 de novembro, após o fechamento do mercado" [https://euqueroinvestir.com/acoes/o-que-esperar-do-balanco-da-petrobras-no-3t26].
- A 29 Oct 2026 article said 11 Nov after close [https://bpmoney.com.br/negocios/empresas/petrobras-petr4-dividendos-ate-42-bilhoes-3t26/]. The IR notice and the release itself contradict it; it is an analyst-estimate piece.
- **Released:** Petrobras Agência (primary, company newsroom), "Posted on 2026.11.10": 3Q26 net income BRL 39.8 billion (US$ 7.7 billion) [https://agencia.petrobras.com.br/en/w/negocio/petrobras-registra-lucro-l%C3%ADquido-de-r-39-8-bilh%C3%B5es-no-terceiro-trimestre-de-2026]. Its first paragraph says "third quarter of 2024", a typo on the page; the title and the rest say 2026.
- InfoMoney (10 Nov 2026, 20:31 Brasília): net income R$ 39.75 billion, below the LSEG consensus of R$ 47.02 billion [https://www.infomoney.com.br/mercados/petrobras-petr4-balanco-3t26/].
- R1 found no Petrobras 6-K on sec.gov for the 3Q26 release or remuneration. The SEC search returned only earlier 2026 6-Ks. UNVERIFIED on EDGAR. R1 did not search CVM directly.
- **Dividend declared (primary), Petrobras Agência "Posted on 2026.11.10":** BRL 15.3 billion, based on the 30 Sep 2026 balance sheet, an advance on fiscal-2026 remuneration [https://agencia.petrobras.com.br/en/w/institucional/petrobras-aprova-pagamento-de-r-15-3-bilh%C3%B5es-aos-seus-acionistas].
  - R$ 1.18732774 per common and preferred share, in two installments of R$ 0.59366387 [same URL].
  - Form (dividends and/or interest on equity) "will be determined by December 10, 2026" [same URL].
  - Subject to withholding income tax [same URL].
  - B3: record date 21 Dec 2026, ex 22 Dec 2026, paid 22 Feb 2027 and 22 Mar 2027 [same URL].
  - **NYSE ADRs:** "the record date will be December 23, 2026", installments "as of March 1 and March 29, 2027" [same URL].
  - No ADR ex-date, no ADS ratio and no USD-per-ADR amount are published [same URL].
- Secondary sources agree on R$ 1.19 per share, two installments, B3 record 21 Dec and ex 22 Dec [https://investirecocaresocomecar.com.br/petr4-dividendo-3t26-r-1-19/]. InfoMoney gives the same R$ 1,18732774 per share [https://www.infomoney.com.br/mercados/petrobras-petr4-balanco-3t26/].
- ADR ex-date is not published: UNVERIFIED. Under FINRA Rule 11140(b) as amended for T+1, the ex-date "shall be the record date if the record date falls on a business day" [https://www.finra.org/rules-guidance/notices/24-04]. That points to Wed 23 Dec 2026, but this is a derivation. NYSE/depositary practice for PBR was not checked.
- The previous ADR distribution (6-K, 6 Aug 2026) had ADR record date 25 Aug 2026 and ADR payments 1 Dec and 29 Dec 2026 [https://www.sec.gov/Archives/edgar/data/0001119639/000129281426004123/pbr20260806_6k.htm]. This matches tickers.json's "last ex-div Aug 25 2026". The $0.44103 USD amount in tickers.json comes from stockanalysis and was not re-checked here.
- The lead in request.md (oilandgas360, "Petrobras hikes dividend…") is undated on the page. It cites Q3 net income of $6 billion and R$ 12.16 billion interim dividends [https://www.oilandgas360.com/petrobras-hikes-dividend-as-production-surge-offsets-lower-oil-prices/]. Those figures match the **2025** declaration (headline "dividendos de R$ 12,16 bilhões referentes ao exercício de 2025") [https://euqueroinvestir.com/acoes/petrobras-anuncia-dividendos-de-r-1216-bilhoes-referentes-ao-exercicio-de-2025], not 3Q26 (R$ 15.3 billion above). So it is not evidence for 3Q26. R1 matched it by the figures; the article's date is UNVERIFIED.

## Numbers used (show the math)
- PBR fallback estimate (house rule 040, `earnings_gap_days` 70): 2026-11-10 + 70 d. Nov 11–30 = 20 d, Dec = 31 d (51), Jan 1–19 = 19 d (70) → **2027-01-19**. That is after the 2026-12-18 monthly expiry (third Friday: Fridays Dec 4, 11, 18), so PBR's blocked set stays `set()` with a correct `last_earnings`. Matches 048/05 and A1's arithmetic check (logs/audit/2026-11-11.md L41).
- Installments: 2 × 0.59366387 = 1.18732774 ✓ (per-share total).
- ADR record date 2026-12-23 − Dec 18 expiry = 5 calendar days after expiry. A Dec 18 call expires before the ADR record/ex-date, whatever the exact ex-date. A Jan 2027 call would be open across it.
- USD per ADR: not computable. The BRL amount is known, but the ADS ratio is not in the source, the FX rate is not fixed, withholding depends on the dividend vs interest-on-equity split (set by 10 Dec), and Petrobras gives no USD figure.

## Fit for a ~$3k account
- No trading rule changes. For PBR the facts give:
  - `last_earnings` 2026-11-10 is now **confirmed by a primary source** (Petrobras Agência, posted 2026-11-10). The value 3ba835e entered is right, but its cited source (stockanalysis, "snapshot Oct 27: the report itself not confirmed") did not confirm it. The fix is to cite the Petrobras URL, not to change the date.
  - `next_earnings`: 4Q26 date not published → stays null, and the house-rule estimate (2027-01-19, labelled) applies.
  - `ex_div_date`: Petrobras publishes an ADR **record** date (2026-12-23), not an ex-date. Entering 2026-12-23 as ex-date would be a derivation (FINRA 11140 T+1 rule). R2/R3 decide whether that is a labelled entry or stays null (`n/a` policy).
  - `dividend`: the USD amount per ADR is unpublished → **stays null** (`tickers.dividend` n/a: NaN, never 0.0).
- Early-assignment risk: both the record date and the derived ex-date fall after the Dec 18 expiry, so they don't matter for a Dec 18 call. They do matter for any later expiry. The PBR share price was not checked here (UNVERIFIED), so the 100-share cost vs ~$3k is not assessed in this brief.
- Tax note: Brazilian withholding on interest on equity reduces the cash an ADR holder gets. The rate and form are not set until 10 Dec (UNVERIFIED rate).

## Open questions
- R2: date cutoff vs SHA cutoff; read 07 at the parent vs at the commit; merge-commit gap; shallow-clone behaviour (not checked vs fail).
- R2/R3: should `ex_div_date` hold the ADR record date 2026-12-23 with a "record date; ex-date not published" label, or stay null until an ex-date is published (NYSE/depositary notice)?
- R3: confirm the 3Q26 release and remuneration on sec.gov EDGAR (6-K) or CVM. R1 found only the company newsroom.
- R3: re-run `git show --stat 3ba835e` and `git log --no-merges --format='%h %ct' <cutoff>..HEAD` to confirm the repo evidence R1 read second-hand.
