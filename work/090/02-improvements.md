# 02 Improvements - 090
## What past logs say
- RI-010 (logs/recurring-issues.md L118-130) is ESCALATED with 5 occurrences. The 2026-11-21 entry already names this item: "Near miss, not counted: untimed or sent-back rounds still escape LOG BATCH → 090". The GUARDED condition is still 086's: "086 is merged and its 083 fixture is flagged". 090 does not change that condition. It closes the residual gap A1 found (logs/audit/2026-11-21-086.md L58-62).
- Each RI-010 guardrail so far closed one shape and left the next one open:
  - 043 checked presence.
  - 045 checked format and "not after commit".
  - 049 added a named exception.
  - 086 added C (timing over the whole item) and D (later file at write time).
  - 090's gap is the same pattern: C is blind without a time, and D is off after one send-back (scripts/check_pipeline.py L815, `later and not _sent_back(item)`; `_sent_back` L773-796 has no round limit).
- 086/02 AGAINST 1 already wrote this down as a known cost: "inside a send-back round a batch passes D. Only C (I rounds, timed) backs it up. R rounds after BLOCKED or NOT A FIT have no timing check at all" (work/086/02-improvements.md L39). 090 is that note coming due.
- RI-014 (recurring-issues.md L152-158) is OPEN. Its root cause was 079's walk. 081 made failed git loud. A1's 081 probes found that three readers still answer from cut history (logs/audit/2026-11-21-081.md L98-102). The same audit's F3 (wrong reason on a non-UTF-8 .git/shallow) went to 089, not here (work/089/request.md L11, L14).
- Send-back history in the logs (Grep on logs/):
  - I3 FAIL lines: 13, from 002 to 082 (logs/implementation/2026-10-30.md L5 and L8 through 2026-11-21.md L18).
  - R3 `BLOCKED` lines and I1 `NOT A FIT` lines: 0 ever.
  - So the send-back rounds that actually happen are I rounds.
- Precedent for languages: the same checker topics, 079 (shallow), 084 (rule gate) and 086 (LOG BATCH), were all logged `languages: N/A` (work/079/02 L27, work/084/02 L24, work/086/02 L54).

## 3 ways FOR
1. **Treat (i) "I2 time required from a cutoff" and (iii) "per-round I2 bound" as one rule pair. (iii) cannot work without (i).**
   - Reasoning chain: R1's per-round bound (01 A10) needs the I2 field's own time. Without (i), an untimed field makes (iii) silently skip that round, which is the same "not computable" hole as today (01 A3).
   - With (i), every I2 round from the cutoff on carries a time, and (iii) checks each round against its own previous line. That covers the rounds after a send-back (gap y) that C's whole-item window misses (01 A5: 086's own Δ81 window).
   - Cost to a correct run is 0:
     - pytest `-q` always prints ` in <s>s` (01 A6, pytest terminal.py source).
     - 17 of 17 timed lines from 076 on already comply (01 A7).
     - SUITE_FROM = 87 already requires 05's `Suite:` line to equal the last I2 field (scripts/check_pipeline.py L313-315). So 05 also inherits the time.
   - Measured: 0 of 17 rounds flagged (01 Numbers). The tightest is 077 r2 at 91.97 s against 300 s.
   - Enforce it in two places, as 01 A9 says:
     - Numerically in `write_log`, so `--log I2` is refused with exit 2. This is the loud, early place, and the run-item L16 "refusal goes back to the step" loop handles it.
     - Gated by `_rule_seen` on 05 in the check, so already-committed history is never judged by a rule it did not see.
2. **Add R1's content check (01 A13) for send-back rounds. It also closes most of R1's I3 hole (01 A12) without a LOG_FORMAT change.**
   - Reasoning chain, by reading the step files at write time: after a send-back line, the file that holds the send-back verdict must still show it until the step that wrote it runs again.
   - Rule: if `--log <X>` runs for a step before that step, and the file shows a non-send-back verdict, then the later step already re-ran before X's line. That is a batch, so refuse.
   - Example: in round 2 after I3 FAIL, `--log I2` while 06 already says `Verdict: PASS` means I2 and I3 were batched at the end. That is the I3-untimed case R1 left open in A12. It is caught without timing and without putting an I3 run time in the I3 log field (01 Open question 3).
   - Verified here (R1 had this as UNVERIFIED):
     - Each template holds a line-2 verdict: `Status: READY | BLOCKED (<reason>)` (templates/research-handoff.md L2), `Fit verdict: FIT | FIT WITH CHANGES | NOT A FIT` (templates/build-plan.md L2) and `Verdict: PASS | FAIL (round <n>; ...)` (templates/verification.md L2).
     - Real files follow them: `^Status: (READY|BLOCKED)` is in 27 of 27 03 files (060-086), and `^Fit verdict:` is in 27 of 27 04 files.
     - 069/04 has two `Fit verdict:` lines (L2, and a round-2 section at L96). So read the first line (L2) only, as VERDICT_LINE already does for 06.
   - Like D, the check needs no git and no mtimes. It looks only at the item's own folder, so concurrent items (four lines in one minute, 086/02 L11) cannot trip it.
3. **Shallow side: reuse the one `env` value from main() (L1535) for all three readers, and keep the two answers that are still exact.**
   - Reasoning chain: `_anchor_env()` already returns `"shallow clone; run git fetch --unshallow"` for shallow boundaries or "unreadable" (01 B3). RULE NOT SEEN already prints `not checked ({env})` (L1618).
   - Passing the same `env` to `late_log_lines`, `main_ahead` and the unrelated test gives the request's exact text from one source. After 089 makes "unreadable" a sure answer (work/089/request.md L14), all four lines change together.
   - It is also a single mutation point: `env` forced to None should fail the depth-1 fixture on all three lines at once.
   - Precision that costs nothing:
     - MAIN AHEAD = 0 in a shallow view is exact (01 B8: the shallow view only removes parent edges, git-scm shallow docs). Only a positive count needs `not checked`.
     - Likewise, in OPEN BRANCHES, `merge-base --is-ancestor` exit 0 is exact. Only exit 1 (`behind` filter L1057) and unrelated `merge-base --all` exit 1 are uncertain (01 B9-B10).
   - If I1 keeps the request's uniform text, it should still say in 04 why the exact 0 is dropped, so a later item does not "fix" it back.

## 3 ways AGAINST
1. **Exit-code trap: the obvious way to return "not checked" changes the exit, in either direction.**
   - Reasoning chain from main() (L1643-1645):
     - `isinstance(ahead, str)` gives exit 1. A `main_ahead()` that returns the shallow hint as a str would make every shallow run exit 1 from MAIN AHEAD, even when the cut view counts 0.
     - `late` is truthy when it is non-empty. A `late_log_lines()` that returns `["not checked (...)"]` would also exit 1.
     - The other way: the unrelated-branch case is a BRANCH ERROR (exit 1) today (081 audit L61-63, exit 1). Making it "not checked" with exit unchanged turns that run into exit 0.
   - Precedent (UNTRACKED CHANGE 079, RULE NOT SEEN 084) is "not checked", exit unchanged (01 Open question 4). But a shallow daily worktree that exits 0 while three checks are off is the RI-002 shape: an unknown read as a pass by anyone who reads only the exit code.
   - Fix: give the shallow case its own sentinel (not the 081 str error path), and decide the exit on purpose. Pin the exit code in the depth-1 fixture, not just the three texts, so a refactor cannot flip it silently. The person should see the choice in the PR, because run-item L12 lists which lines may say "not checked".
2. **The per-round bound is weak by construction and depends on a suite that is currently slow. Its guarantee will fade without anyone noticing.**
   - Reasoning chain: with minute stamps, a round is flagged only when t − 0.005 ≥ (Δ+1)×60 (01 A10).
   - Today's runs are 74.44-92.66 s (01 Numbers). So only a same-minute (Δ0) batch is caught. A batch spread over 2 minutes (limit 120 s) passes, as R1 says (01 Numbers "price of minute stamps").
   - If the suite gets faster, the bound goes blind. A future speed-up item (EFFICIENCY items like 066/074 have touched test cost) would bring the run under 60 s, and then (iii) catches nothing. The same happened to C on pre-061 items, which ran ≤ 23 s (086/02 AGAINST 2).
   - The proof also holds only under run-item order (I1 logged before I2 starts the suite), not from the stamps alone (086/02 AGAINST 2).
   - Fix:
     - Word the output "impossible under the run-item order" (as 086 did, L1003).
     - Do not claim the bound closes gap (y). The content check (FOR 2) is the part that does not decay.
     - Make a test assert the bound's own margin, so a speed-up shows up as a visible cost and not a silent loss: for example, the boundary fixture at Δ0 with 60.00 s gives none, and with 60.01 s it flags (01 Numbers).
3. **Cost: more rule-file surface for a gap with 0 real occurrences, part of it guarding paths that have never been taken.**
   - Reasoning chain:
     - Both gaps are near misses that were not counted (request L15; RI-014 has 1 occurrence).
     - The fix adds a fourth item-number constant next to LOG_CHECK_FROM, TESTS_FORMAT_FROM and SUITE_FROM (L311-315), with two-way enforcement (numeric plus `_rule_seen`).
     - It adds a content check over three step files at `--log` time.
     - It adds a sentinel through three git readers.
     - scripts/check_pipeline.py and .claude/ are RULE_PATHS, so the person's OK is needed at PR review (01 "Fit").
   - The R-round half of the content check (03 BLOCKED, 04 NOT A FIT) guards a path with 0 log lines ever (Grep above). It is code that no real data has exercised. Its only evidence will be fixtures.
   - Regex risk: making the time mandatory means editing `_TAIL` (L324) or adding a per-ID variant.
     - The global `_TAIL` must stay optional, or 083's `tests 344/344` (LOG_BATCH_EXCEPT L333) and every pre-cutoff line become INCOMPLETE.
     - The free-text tail `(?: \(.*\))?` must not let a time inside parentheses count, so `tests 5 passed (in 3.00s)` must be refused.
   - Build order: 087, 088 and 089 change the same file on this branch (01 Open question 6). The new readers of 03/04/06 must go through 089's shared reader, or 089's census test will flag them.
   - Fix: keep the R-round half only if each check is one small function with its own named test. Otherwise drop it and write it down as a known gap. Gate the strict I2 form by ID, never globally. Build on top of 089.

## Findings by language
Languages: N/A (no new external claims). 090 is a BUG fix inside this repo's own pipeline checker: the I2 log-field format from a cutoff, a write-time content check on step files, and shallow-clone handling of three git readers. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are pytest and git tool behaviour, which R1 already cited to official English docs and source (pytest terminal.py; git-scm shallow, rev-parse, fetch, blame, rev-list, merge-base, clone). This follows 079, 084 and 086, the same checker and the same topics, all logged `languages: N/A`.

## Holes to watch out for (summary)
- The exit code in the depth-1 fixture must be asserted, not just the three texts.
  - Returning the hint as a str from `main_ahead` hits `isinstance(ahead, str)` (exit 1).
  - A non-empty list from `late_log_lines` makes `late` truthy (exit 1).
  - The unrelated BRANCH ERROR going to "not checked" drops exit 1. Choose on purpose and state it in 05.
- The depth-1 fixture needs `--no-single-branch` (01 B11), or origin/main and the branch refs are missing and MAIN AHEAD and OPEN BRANCHES are tested on nothing. It also needs a pinned committer time with a later commit on top, as in A1's `lt`/`lt1` (081 audit L99).
- The mandatory I2 time must be per-ID (cutoff), never a global `_TAIL` change. A time only inside the free-text `( ... )` tail must not count. Keep accepting the `(0:01:01)` suffix and the `in <n> seconds` form.
- The cutoff must be above every in-flight item that might log I2 under the old code (087-089 run today), or the check side must be gated by `_rule_seen` on 05 so that history is never judged by a rule it did not see (01 A9).
- The content check must read only the first verdict line:
  - 03 `Status:`, 04 `Fit verdict:` and 06 `Verdict:` (VERDICT_LINE L349).
  - 069/04 has a second `Fit verdict:` line at L96.
  - Match the word in its group, never a substring (RI-012).
  - An unreadable file must refuse, not pass (`_sent_back`'s "refusal side" note, L777).
- The content check covers only batches where the later step's verdict changed. A round-2 I3 that FAILs again leaves 06 at FAIL, so an I2+I3 batch in that round passes. Write this down as a known gap.
- Per-round bound:
  - Choose the prev line with 086's ordering rule (L946, L977): a research line with stamp ≤ counts as before, and an implementation line with the same stamp only if it is above. That matters for FAST items, whose round-1 prev line is R3 in the research log.
  - It is per item only. Today's log has 081, 084 and 086 lines interleaved in the same minutes (logs/implementation/2026-11-21.md L5-6, L12-15).
- "not computable" for new IDs: decide each reason separately (01 Open question 2).
  - "no pytest time" is closed by the mandatory time.
  - "no line before I2" should be impossible for a non-FAST item.
  - "unreadable" belongs to 089's reader.
- MAIN AHEAD 0 and `--is-ancestor` 0 are exact in a shallow view (01 B8-B9). If the uniform text is kept anyway, say why in 04.
- A single-branch shallow clone (01 B11) silently hides open branches and their IDs from `--next-id` (RI-009). It is out of scope here. Send it to A1 as a new item, not a silent pass.
- I2/I3 must re-derive by code R1's 17-round table and the 0-flag count, and this file's 27/27 template-line counts, before relying on them.

Log fields: 3 for / 3 against | languages: N/A
