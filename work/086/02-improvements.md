# 02 Improvements - 086
## What past logs say
- RI-010 (logs/recurring-issues.md L118-130) is ESCALATED with 5 occurrences. Every past guardrail checked a line's presence, format or time after its commit, but never the moment of writing compared with the step's file. 043 checked presence, 045 checked format plus "not after commit", and 049 added a named exception for 048. 083 passed all of them (logs/audit/2026-11-20-083.md L14; logs/audit/2026-11-20.md L24, L49). GUARDED condition: "086 is merged and its 083 fixture is flagged."
- Precedent for a named exception: 049's `LOG_TIME_EXCEPT = {"048": ...}` with "Never add a new item here" (scripts/check_pipeline.py L236-239). It is printed with its reason on the LOG TIME line (L1129-1132), so the exception stays visible on main. LEGACY (L299-301) is the same pattern. 049/02 FOR 2 and AGAINST 1 back this: honest when the real times cannot be recovered, and safe when a test pins the list.
- 049/02 "Holes" warned that re-committing a line moves its blame. That is why 048 could not be fixed by re-typing. The same holds for 083: its real times are lost (01 F20).
- No past audit or efficiency log proposes a write-time order check. 045's `write_log` (L558-579) checks only agent, ID, fields and request.md. This item would add the first check that ties a line to the step files.
- Process facts that bear on rule D (from .claude/commands/run-item.md):
  - L14: "If a step returns BLOCKED, NOT A FIT, or FAIL, send the item back to the step named in that file."
  - L16: the orchestrator logs each R1-I1 step "one step at a time and never in a batch across steps or parallel items", in the order file exists -> check_handoff -> `--log` -> commit. "A `--log` refusal (exit 2) goes back to the step."
  - L8: R3 writes 07 for RESEARCH ONLY items. L10: FAST may skip R2 and I1.
- Today's concurrent run: logs/research/2026-11-20.md L10-13 has R2 lines for 085, 080 and 084 plus R1 082, all at 23:27. One minute holds four lines from four items. Any rule must be per item (see FOR 1 and the Holes section).

## 3 ways FOR
1. **Pair D (write time) with C (history), as R1 proposes. D is the main guard, C the proof check on committed history.**
   - Reasoning chain: in a batch at the end, all six files exist before the first `--log`. D refuses R1 because 02-06 exist. That catches 083, and also untimed batches like 048, 055 and 058, which C cannot compute (01 F15, F18). No git, no timing and no history replay are needed (F19).
   - C catches what D lets through in a send-back round (AGAINST 1), and it works on lines already committed. On the 35 FULL items from 045 on, C has 1 hit (083) and 0 false positives, proved by 48.51 + 47.57 = 96.08 ≥ 60 (F8, F15).
   - D also makes C's premise enforceable. C assumes the round's start line (I1 or the I3 FAIL) was written before I2's test run started (F6). With D, `--log I1` is refused once 05 exists, so a late I1 line is refused loudly instead of silently shrinking the gap.
   - Concurrency: both rules look only at the item's own folder and its own lines. Today's four lines from four items at 23:27 (research log L10-13) cannot trip either rule. A cross-item "lines in one minute" rule (rule A over the whole log) would trip.
2. **083 decision: run C from LOG_CHECK_FROM (45), with a new, pinned `LOG_BATCH_EXCEPT = {"083": "<reason>"}`, not a cutoff at 084.**
   - Reasoning chain: from 45 or from 84, C flags the same set, {083} (F15). So the cutoff buys nothing and hides 083, plus any future re-check of 045-082, behind a constant.
   - A named exception follows the 049 precedent. It is printed with its reason (e.g. `LOG BATCH: none (083 excepted: lines written in one batch at 10:15 after the build; real times not recoverable, item 086)`), keeps main at exit 0, and can be pinned by a test (`set(LOG_BATCH_EXCEPT) == {"083"}`, "Never add a new item here").
   - Keep it a separate dict. Adding 083 to LOG_TIME_EXCEPT would break that list's "never add" rule, and it would wrongly switch off LOG TIME for 083, whose lines are not late.
   - Fixtures that meet RI-010's GUARDED condition with real data:
     - (a) In a tmp repo, 083's six lines and its 05/06 summary lines copied under ID 999 (not 083, which the exception would hide). The I2 field is in pytest form, `2 files changed | tests 344 passed, 1 skipped in 48.51s`, so the fixture tests only LOG BATCH and not 084's INCOMPLETE (F22). Expect `LOG BATCH: 999`.
     - (b) On the real repo with `LOG_BATCH_EXCEPT` monkeypatched to `{}`, expect `LOG BATCH: 083`. This is "its 083 fixture is flagged" on real data.
     - (c) The real repo as is gives none, with 083 named.
     - Negatives: 079's real lines (send-back round and date rollover, F23), the 59.99 s / 60.00 s boundary pair, and an interleaved fixture with three items' lines in one minute (today's 23:27 pattern) giving none.
3. **Read the durations the cheap and unambiguous way.**
   - Reasoning chain: from 076 on, the I2 log field must be pytest's own summary line (TESTS_FORMAT_FROM = 76, LOG_FORMAT["I2"] L281). So t05 can come from the item's last I2 line rather than from free text in 05. That avoids 076's case, where 06 quotes 05's run (F21).
   - t06 is the last summary line in 06's `## Tests re-run` section, counted only when it differs from t05 (R1 open question 4: last line, not every run).
   - Reuse `_STATS`/`_TAIL` (L228-234) so that the ≥ 60 s form `61.68s (0:01:01)` parses. pytest prints `f"{seconds:.2f}s ({dt})"` from 60 s on (F5, https://pytest.org/latest/_modules/_pytest/terminal.html).
   - For items before 076, fall back to the 05 `## Test output` section. If neither file has a time, print nothing for C. C must never flag an item it cannot compute.

## 3 ways AGAINST
1. **R1's exception list for D is incomplete, so D as drafted would refuse legitimate re-runs.**
   - Reasoning chain: run-item L14 sends an item back on R3 BLOCKED, I1 NOT A FIT, or I3/A1 FAIL. R1's exception (F18) covers only an I3 FAIL line or 07 `A1 result: FAIL`.
   - After I1 NOT A FIT, R1 re-runs while 02, 03 and 04 exist. After R3 BLOCKED, R1 or R2 re-runs while 03 exists. D would refuse both.
   - Fix: the exception applies when the item's latest step line is a send-back verdict (R3 `| BLOCKED`, I1 `NOT A FIT |`, I3 `FAIL |`) or 07's last `A1 result:` is FAIL (format: work/069/07-audit-task.md L22). Tests are needed for each of the four.
   - Cost that remains: inside a send-back round a batch passes D. Only C (I rounds, timed) backs it up. R rounds after BLOCKED or NOT A FIT have no timing check at all. Write this down as a known gap rather than claim full cover.
   - Keep 07 out of D's "later files" set. A RESEARCH ONLY item's R3 writes 03 and 07 before its `--log R3` (run-item L8), and a FAST item's missing 02 or 04 (L10) must not matter.
2. **C is weak on its own, and its "proof" rests on a process assumption.**
   - Reasoning chain: minute stamps (F4) mean C can only flag when t05 + t06 ≥ (Δ+1)×60 s. A batch of an item with a fast suite (most items before 061 ran ≤ 23 s, Numbers table) or with untimed 05/06 (048, 055, 056, 058) evades it. Only the last round can be checked, because 05/06 are overwritten (F15).
   - The arithmetic proves a batch only if the start line was written before I2's run started. That holds under run-item L16 (log, then next step), not by the stamps alone.
   - With D alone the hard bound is weaker: I1's line comes before 05 exists, and I3's line comes after 06 exists, so the gap > t06 only. 083's t06 = 47.57 s would not pass that stricter test.
   - Fix: the output and the docstring should say "impossible under the run-item order (L16)", not "impossible". R1's open question 5 should not make 05/06 times mandatory just for C, since D covers untimed batches.
3. **Cost: a rule-file change that needs the person's OK, a third named-exception list, and RI-010's condition met partly in tests.**
   - Reasoning chain: scripts/check_pipeline.py is in RULE_PATHS (L260), so the change waits for the person's review, as 049 did.
   - LEGACY, LOG_TIME_EXCEPT and now LOG_BATCH_EXCEPT make three closed lists. Each is safe only while its pin test exists.
   - D's refusal turns an orchestrator slip into a re-run. Example: `--log R2` is skipped, R3 runs, and now R2 is refused for as long as 03 exists. The step goes back (L16), up to 3 loops, then to the person.
   - Fix: the refusal message must name the later file(s) and say the fix: redo the later step after this line is written. Never delete or edit by hand without the step.
   - The test suite (~90 s, 079/05) grows by a few tmp-repo fixtures. Small but real: the orchestrator's log-then-launch order makes I2 -> I3 slower to start.

## Findings by language
Languages: N/A (no new external claims). The fix is a check inside this repo: step-file existence at `--log` time, plus arithmetic on the repo's own log stamps and pytest lines. No fee, rule or market fact changes, and the one outside fact it uses (pytest's summary time is wall-clock session time, ≥ 60 s format) is already sourced by R1 (F5).

## Holes to watch out for (summary)
- D's exception must cover all four send-back verdicts from run-item L14 (R3 BLOCKED, I1 NOT A FIT, I3 FAIL, A1 FAIL), with a test for each. 07 must never count as a later step file.
- D and C must be per item. Today's run put four items' lines in one minute (research log L10-13). A test should interleave items so that none is flagged.
- The 083 positive fixture must use a non-excepted ID (999) with a pytest-form I2 field. The real-data check is the repo run with `LOG_BATCH_EXCEPT = {}`, which gives `LOG BATCH: 083`.
- `LOG_BATCH_EXCEPT` is a separate dict pinned to {083} and printed with its reason. Do not add 083 to LOG_TIME_EXCEPT.
- C must stay silent on an item it cannot compute (no time in 05/06 or the I2 line). It must never treat a missing time as 0 s or as a flag.
- t06 counts only if it differs from t05 and is the last summary line in `## Tests re-run` (076's quoted run). Parse the `(0:01:01)` suffix.
- Wording: "impossible under run-item L16 order". C's proof assumes the start line was logged before I2 ran. D only guarantees it was logged before 05 existed.
- I2/I3 must re-derive R1's counts with code: 35 FULL items from 045 on, C = 1 (083), D's history UNVERIFIED (01 F18). They should state the count in 05/06 as "Done looks like" asks.
- D does not need an 083 exception (write time only, no history). Say so in 05 so nobody adds one.

Log fields: 3 for / 3 against | languages: N/A
