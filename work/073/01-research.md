# 01 Research brief - 073
## Question
The person chose "Always own run" (request.md L11; logs/audit/2026-11-18.md L28, 2026-11-18 02:31 UTC). So when an item changes realtest's decision path, I3 always makes its own full realtest run at the head commit. It never reuses the head run made for 05, even when the same-inputs check passes. Base-run reuse stays as it is.

Questions for this brief:
- Where does the current text allow, or fail to rule out, head-run reuse?
- What is the smallest edit that leaves no contradicting text?
- What does the extra run cost?
- Is a check that 06 names a head-run output dir different from 05's cheap?

This is a process and rules item with no market or options content. All sources are repo files cited as path:line. The brief cites no external URLs (0 unique URLs), the same as 068/01.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
**How 068 ended up reusing a head run**
- F1. In 068, one head run (068-after) was made by the orchestrator after a container restart, and both I2 and I3 used it. I3 did not make its own run. [logs/audit/2026-11-17-068.md L14-15; work/068/06-verification.md L24, L87]
- F2. I3 skipped its own run "on the orchestrator's instruction". Its justification was that `git -C wt-068-head diff --stat 8f384c9 -- ccbot/ config/` was empty, so the run's inputs equalled the build commit. [work/068/06-verification.md L24, L87]
- F3. A1 judged this a disclosed deviation, not an error, because I3 ran under the older i3 text. A1 asked the person whether I3 should always make its own head run or may reuse one "under the same same-inputs check as the base". [logs/audit/2026-11-17-068.md L16-20, L82]
- F4. The head run in F1 was made by the orchestrator, not by I2. So the new rule has to cover any head run made for 05, whoever made it. "I2's run" alone would leave a gap. [work/068/05-build-report.md L96; work/068/06-verification.md L87]

**Text that touches head-run reuse (grep for `reuse|same.inputs|same inputs|full run|head run|base run|same dirs|re-runs diff_reports` over .claude/, templates/, scripts/, logs/; work/ excluded)**
- F5. `.claude/agents/i3-verifier.md` L13 (step 2) says: "make one full run at the head commit for the numbers in 06, compared with the base full run named in 05; if that run is gone or its inputs differ from the base's (same check as i2 step 3), run the base too (item 068)". It says "one full run" but never that the run must be I3's own, so F1's reading was possible. The same-inputs clause applies only to the base. [.claude/agents/i3-verifier.md L13]
- F6. `.claude/commands/run-item.md` L18 says: "run the full backtest (no `--tickers`, `--out <scratch>`) once per step that publishes numbers; a full run made at another commit counts as the base only if `git diff --stat <that commit> <base> -- ccbot/ config/` is empty and both used the same data". "Once per step that publishes numbers" implies a run each for I2 and I3. It does not say a head run cannot be shared, and the reuse clause names only the base. [.claude/commands/run-item.md L18]
- F7. `.claude/agents/i2-builder.md` L20 (step 3) says: "make one full run at the build commit, plus one at the base commit unless a full run with the same inputs exists ...". This is I2's own head run plus the base-reuse rule. It does not contradict 073 and needs no change. [.claude/agents/i2-builder.md L20]
- F8. `templates/verification.md` L8 (comment in `## Real-data effect`) ends: "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's." This contradicts 073: "the same dirs" means 05's base and 05's head dir, so I3 would diff I2's head output, not its own. It must change, or contradicting text remains. [templates/verification.md L8]
- F9. `templates/build-report.md` L10 says nothing about who makes the head run. No change needed. [templates/build-report.md L10]
- F10. The `scripts/check_pipeline.py` docstring gap (o) says a TOTAL line "does not prove 06's TOTAL equals 05's (I3 still compares, templates/verification.md)". This is consistent with 073 and needs no change. [scripts/check_pipeline.py L123-125]
- F11. Mentions in logs/ are historical and must not be edited: logs/audit/2026-11-17-068.md L14-20 and L82, logs/audit/2026-11-17.md L14, logs/audit/2026-11-16.md L39, logs/audit/2026-11-15-065.md L103, logs/audit/2026-11-13.md L33, logs/efficiency/2026-11-16.md L3. [grep output above]
- F12. No other `.claude/` file or template matched the grep. [grep over .claude/, templates/, scripts/]

**Why I3's own head run is expected to reproduce 05's numbers**
- F13. Real-data runs are deterministic. 068 relied on this: "the runs are deterministic (04 Extra research 3)", and the Monte Carlo uses a fixed seed. So I3's own head run should give a byte-equal diff_reports TOTAL line to 05's. A difference is itself a finding. [work/068/06-verification.md L24; logs/audit/2026-11-17-068.md L18]

**Is a check that 06 names a different head-run dir cheap?**
- F14. The 05/06 Real-data sections name their dirs only in free text (`- After: \`<path>\`, full run ...`). Only 068 uses this form; no fixed field exists. [work/068/05-build-report.md L96; work/068/06-verification.md L87; templates/build-report.md L10; templates/verification.md L8]
- F15. `check_pipeline.py` already knows which items trigger the Real-data field (TRIGGER, TRIGGER_DIRS, WHOLE_DIFF_FROM = 70). It already parses that section in 05 and 06, reading lines inside fences. A head-dir comparison could reuse this trigger and section reader. [scripts/check_pipeline.py L111-130, L179-191]
- F16. A dir-name check proves only that the names differ. It does not prove I3 ran realtest: a copied dir would pass. It would be one more "proves a paste, not that it is current" gap, like gap (o). [scripts/check_pipeline.py L123-125]

## Numbers used (show the math)
- One full run: 13m42.704s = 822.7 s. 822.7 / 60 = 13.71 min (about 13.7 min). The orchestrator's note says ~13.7 min, from memory of item 067. In the repo, the measured figure is from 068's head run. [work/068/06-verification.md L87; logs/audit/2026-11-17-068.md L75]
- What 068 did: 1 head run (shared) plus a reused base = 1 full run, about 13.7 min. [logs/audit/2026-11-17-068.md L20]
- Under 073, for each item that changes realtest's decision path:
  - I2 head (1), I3 head (1), and a base only if no same-inputs base exists (0 or 1) = 2 to 3 full runs.
  - 2 x 13.71 = 27.42 min. 3 x 13.71 = 41.13 min.
  - Extra compared with 068's practice: +1 run = +13.71 min per item.
- 068/03 assumed the same count, 2 to 3 full runs, priced at the older 11.342 min: 22.7 to 34.0 min. 073 matches that count; only the run time is longer now. [work/068/03-handoff.md L95-96; logs/audit/2026-11-17-068.md L20]
- `--tickers` iteration is unchanged: the 5-name run took 237.3 s, 28.8% of a full run. [logs/audit/2026-11-17-068.md L75]

## Fit for a ~$3k account
- The change touches no trading rule, bot code or real-data output. It changes only how independently I3 checks the backtest numbers the person reads. No effect on position size, assignment, dividends, taxes, commissions or liquidity.
- The benefit: every number I3 publishes in 06 comes from a run I3 made itself. This was the person's stated choice.

## Open questions
**Proposed wording, for R2/R3/I1 to settle**
1. i3-verifier.md L13 (the one clear line). Replace "make one full run at the head commit for the numbers in 06" with: "make your own full run at the head commit for the numbers in 06, in your own worktree and scratch `--out`; never reuse the head run made for 05 (by I2 or the orchestrator), even if the same-inputs check passes (item 073)". Keep the rest of the sentence: the base may still be reused under the i2 step 3 check.
2. run-item.md L18. Append: "I3's head run is always its own, never 05's; only the base run may be reused (item 073)." This is needed because L18 is where the orchestrator reads the rule. In 068, the orchestrator is the one who told I3 not to re-run (F2).
3. templates/verification.md L8 (needed to avoid a contradiction, F8). Change "I3 re-runs diff_reports.py on the same dirs" to "I3 runs diff_reports.py on 05's base dir and its own head-run dir (item 073)". Keep "and compares its TOTAL line with 05's".
   - This is a third file beyond the request's "one line (and run-item.md if needed)". R2/R3 should confirm it is in scope.
   - If it is left out, the template keeps telling I3 to diff 05's dirs.

**The optional "if cheap" check (F14-F16)**
4. It is not free. It needs:
   - a fixed field, for example `Head run: <out dir> (<who>, <SHA>)`, in both templates;
   - a start constant (items from 073 on);
   - code in check_pipeline.py and fixture tests.
   It would also only prove that the two dir names differ (F16). R2/R3 decide whether to build it here or leave it to the efficiency list. R1 leans toward the text-only change plus A1 spot-checking the 06 log time and dir, but that is a judgement, not a sourced finding.

**Overlap with parallel items**
- Item 072 edits run-item.md, but at L14 (the `--log` duty) and in the r1/r2/r3/i1 agent files, not in i3-verifier.md. 073 edits run-item.md L18. Different paragraphs of the same file, so expect a merge conflict to resolve by hand, not a conflict of meaning. Whichever item lands second rebases onto the first. [work/072/request.md L8, L16; .claude/commands/run-item.md L14, L18]
- Item 071 edits scripts/check_pipeline.py (the I3 FAIL verdict). If 073 builds open question 4, the two overlap in the same file. [work/071/request.md L8]
- Item 074 does not overlap (a new probe script and a1-auditor.md). [work/074/request.md L8, L19]
- All three files (.claude/ and templates/) are RULE_PATHS, so this is a RULES change and needs the person's OK in PR review. [scripts/check_pipeline.py L193]

**Edge case for R2/R3: no full run at all**
- If an item changes realtest but no full run is needed, the rule should still say what I3 does. Under F6 and 070, any trigger item needs the Real-data paste, so a full run is always needed. R3 should confirm there is no exception. [scripts/check_pipeline.py L111-118]
