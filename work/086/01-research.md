# 01 Research brief - 086
## Question
083's six step lines (R1-I3) are all timed 10:15, and its build commit is cfc0634 at 10:15:48 UTC. `LOG TIME` (045) only flags a line timed after its commit, so `check_pipeline.py` passed it. Which rule would catch step lines written in one batch at the end, measured on every past FULL item from 045 on? The request gives two candidates: (a) `--log` refuses unless the previous step's line exists; (b) `LOG BATCH: <ID>` when I2 and I3 share one minute while 05/06 report a pytest run over 30 s. For each rule this brief gives exact counts and false positives. Repo-internal item: nothing touches ccbot/, config/, data/ or a brokerage (see "Fit").

R1 has no shell. Every count below comes from Grep/Read on the working tree (branch daily-fixes/2026-11-20) on 2026-11-20. None was produced by running check_pipeline. I2/I3 should re-derive the counts with code.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Recurring issues read first: RI-010 (logs/recurring-issues.md L118-130) is this item's link. It is ESCALATED with 5 occurrences: "**Move to GUARDED when:** 086 is merged and its 083 fixture is flagged." Its earlier batch occurrences are 043's 041-044 lines (all 23:10, 46 min after the commit) and 048's six lines (all 20:40, after the commit). Both were caught only because they were timed after the commit. Audit read: logs/audit/2026-11-20-083.md L14.

### What the checker does today
- F1. `write_log` (scripts/check_pipeline.py L558-579) checks the agent, the 3-digit ID, the field format (`log_fields_ok`) and that work/<ID>/request.md exists, then stamps `now` as `%H:%M`. It never looks at the item's other step files or its other log lines. [repo: scripts/check_pipeline.py L558-579]
- F2. `late_log_lines` (L592-616) flags a committed line only when its stated time is later than the blamed commit's time with seconds dropped (`stated > commit`). 083's lines say 10:15 and the commit is 10:15:48, which truncates to 10:15. The line is not later, so it is not flagged. A batch written before the commit therefore always passes. [repo: scripts/check_pipeline.py L610-612; logs/audit/2026-11-20-083.md L14]
- F3. Git's porcelain blame output gives per-commit header fields "author name (`author`), email (`author-mail`), time (`author-time`), and time zone (`author-tz`); similarly for committer". `late_log_lines` reads the `committer-time` row as Unix seconds (`fromtimestamp`). The page I fetched did not state the unit. [https://code.googlesource.com/git/+/HEAD/Documentation/git-blame.adoc?autodive=0; unit UNVERIFIED from docs, repo L605-611]
- F4. The log line format has minute resolution only: `LOG_LINE = ^(\d{2}):(\d{2}) \| (R1|...|I3) \| (\d{3}) \| (.*)$` (L297). Two lines with the same date and HH:MM can therefore be anywhere from 0 to 59.99 s apart. Lines Δ minutes apart are less than (Δ+1)×60 s apart. [repo: scripts/check_pipeline.py L297, L575; derived]

### What 05/06 timings mean
- F5. The pytest summary's "in X s" is wall-clock session time: `session_duration = timing.time() - self._sessionstarttime`, printed as `f"{seconds:.2f}s"` under 60 s and as `f"{seconds:.2f}s ({dt})"` from 60 s on. [https://pytest.org/latest/_modules/_pytest/terminal.html]
- F6. Step order in the agent files: I2 runs the full suite before it writes 05 and logs. I3 re-runs the tests itself after 05 exists (i3 step 2, "Re-run the tests yourself"; "one full run made by you after 05 exists"), then writes 06, then runs `--log`. So I2's suite run starts after the round's start line (I1's line, or the previous I3 line in a send-back round), and I3's run falls between I2's line and I3's line. [repo: .claude/agents/i3-verifier.md L13, L16; .claude/agents/i2-builder.md L25]
- F7. From F4-F6, the time from the round's start line to its I3 line is at least t05 + t06, where t05 is the run in 05's `## Test output` section and t06 is the run in 06's `## Tests re-run` section (templates/build-report.md L8, templates/verification.md L7). If the start line and I3 share one minute, that gap is under 60 s. So t05 + t06 ≥ 60 s with both lines in the same minute is arithmetically impossible, which proves a batch. In general a round is impossible when t05 + t06 ≥ (Δ+1)×60 s. [derived from F4-F6]
- F8. 083: 05 shows `344 passed, 1 skipped in 48.51s` (05 L12) and 06 shows `344 passed, 1 skipped in 47.57s` (06 L9). 48.51 + 47.57 = 96.08 s ≥ 60 s, but I1 and I3 are both 10:15. So the impossibility in F7 holds for 083. [repo: work/083/05-build-report.md L12, work/083/06-verification.md L9, logs/implementation/2026-11-20.md L18-20]
- F9. The request's rule (b) is not a proof on its own. 06 holds one timed run for 083 (47.57 s). A real I3 that logs I2 at hh:mm:00 and I3 at hh:mm:59 could fit a 47 s run in one minute stamp. Rule (b) flags 083 only through its 30 s threshold. Rule (c), I1 to I3 with the sum ≥ 60 s, flags it by arithmetic. [derived from F4, F8]

### Measured on every FULL item from 045 on (Numbers used has the per-item table)
- F10. Items checked: 35, meaning every Scope FULL item from 045 on that has log lines: 045-056, 058-079, 083. 057 is RESEARCH ONLY (work/057/request.md L3). 080-086 have no log lines yet; logs/research/2026-11-20.md and logs/implementation/2026-11-20.md hold only 083 and 076-079 lines. [repo grep: work/0[4-8]*/request.md `^Scope:`; logs/research/*.md, logs/implementation/*.md]
- F11. Known batches among them (RI-010 occurrences): 048 (excepted from LOG TIME, LOG_TIME_EXCEPT L239) and 083. [repo: logs/recurring-issues.md L129-130; scripts/check_pipeline.py L239]
- F12. Rule A ("3+ step lines of one item in one minute", same date and HH:MM) flags 12 of 35: 047, 048, 050, 051, 052, 054, 055, 056, 058, 060, 061, 083. Two are known batches (048, 083). The other 10 cannot be proved either way from the stamps. Each is an R or I run of a small item with ≤ 23 s suite runs or no timing, except 061, whose three same-minute lines are its R lines. They are likely batches (054-058 on 2026-11-12 each have 4-6 lines in 1-2 minutes, 9-31 min apart), but that is not provable, so they count as possible false positives. With a cutoff at 062 (19 items: 062-079, 083), Rule A flags only 083. [repo: logs/research/2026-11-05..20.md, logs/implementation/2026-11-05..20.md; derived]
- F13. From 062 on, no item has any two of its own step lines in the same minute except 083. The smallest gap between consecutive lines of one item is 1 minute, which happens 4 times (062 I3 23:46 -> I2 23:47; 063 R1 23:22 -> R2 23:23; 067 R1 23:20 -> R2 23:21; 068 R1 23:20 -> R2 23:21). A 1-minute stamp gap can be about 1 s of real time (F4). So a stricter "2 in one minute" rule has a real false-positive risk on future fast steps, even though it has 0 hits from 062 to 079. [repo logs; derived]
- F14. Rule B (the request's: I2 and I3 lines in the same minute while 05/06 show any pytest run > 30 s) gives these I2/I3 same-minute pairs: 9 of 35 items (048, 050, 052, 054, 055, 056, 058, 059, 083). Their largest 05/06 runs are 048 none, 050 22.92 s, 052 21.45 s, 054 22.90 s, 055 none, 056 none, 058 none, 059 0.55 s, 083 48.51 s. Rule B flags 1 (083) with 0 false positives, and misses known batch 048 (no timing in 05/06). [repo grep `\d+ passed.* in \d+\.\d+ ?s` over work/0[4-8]*/0[56]-*.md; work/048/05 L8, 06 L6 print `187 passed, 1 skipped.` without a time]
- F15. Rule C (F7). The round start is the latest I1 or I3 line of the item before the round's I2 line, and the round ends at the next I3 line. A round is flagged when t05 + t06 ≥ (Δ+1)×60 s; for Δ = 0 that means ≥ 60 s. Only the item's last round can be checked, because 05/06 are rewritten each round. Rule C flags 1 (083) with 0 false positives. The arithmetic proves it a batch. 4 items cannot be computed: 048, 055, 056, 058 print `N passed, 1 skipped.` with no time. Of those, 048, 055 and 058 have all six lines in one minute. For every other item the summed runs are far under the limit (table). [repo; derived]
- F16. Margin for rules B and C: items with a full run > 30 s are 061 and 063-079 (18 items, 26 I2->I3 rounds). Their smallest I2->I3 gap is 3 minutes (069 round 2: I2 23:55 -> I3 23:58, 06 run 58.61 s). Their smallest round span (round start -> I3) is 8 minutes over all rounds (069 round 2: I3 FAIL 23:50 -> I3 23:58). Over last rounds only, it is 9 minutes (066: I1 23:33 -> I3 23:42, 47.65 + 46.44 = 94.09 s vs a 600 s limit). So no real item comes near either threshold. [repo logs; derived]
- F17. Rule (a) from the request ("--log refuses unless the previous step's line exists"): 083's lines are in order R1, R2, R3, I1, I2, I3 (research L3-5, implementation L18-20), so this rule passes 083. It does not catch an in-order batch. [repo: logs/research/2026-11-20.md L3-5, logs/implementation/2026-11-20.md L18-20]
- F18. Write-time alternative, rule D: `--log <agent> <ID>` refuses when a later step file (01..06 after this agent's own) already exists in work/<ID>/, unless the item is in a send-back round (its last I3 line is FAIL, or 07's last `A1 result:` is FAIL). In a batch at the end, all six files exist when R1's line is written, so R1 is refused. That catches 083 and 048 whether or not 05/06 have times. Every past re-log of an earlier step came after an I3 FAIL or an A1 FAIL: 061, 062, 076, 077 and 079 after an I3 FAIL line; 069 round 3 (I1 00:12) and 070 round 3 (I2 00:24) after `A1 result: FAIL` in 07 (work/069/07 L22, work/070/07 L20). So the exception covers them. Whether later files existed at each past `--log` moment cannot be replayed from the repo, so rule D's history count is UNVERIFIED. 061's second R3 line (2026-11-14 00:06, I1 at 04:36) would have needed 04 absent at 00:06, which is UNVERIFIED. [repo: logs/implementation/2026-11-13..20.md; work/069/07-audit-task.md L22; work/070/07-audit-task.md L20; UNVERIFIED by a run]
- F19. Rule D needs no git and no timing. Rule C needs no git (log text plus 05/06 text), so it also works where LOG TIME prints "not checked (no git)" (L1132). [repo: scripts/check_pipeline.py L1128-1132; derived]
- F20. A repo-side LOG BATCH flags 083 itself on main, as LOG TIME did 048. Precedent 049: a named exception (`LOG_TIME_EXCEPT = {"048": ...}`, "Never add a new item here"). Otherwise `test_repo_pipeline_has_no_skipped_items` (assert exit 0, logs/audit/2026-11-18-069.md L6) goes red when 086 merges. 083's real times are not recoverable. [repo: scripts/check_pipeline.py L236-239; logs/audit/2026-11-18-069.md L6]
- F21. Rule C reads one duration per file. Some 06 files quote I2's run as well as I3's own: 076/06 L17 quotes `525 passed, 1 skipped in 81.91s`, which is 05's run (05 L59). Taking the last summary line in the `## Tests re-run` section, and counting t06 only when it differs from t05, avoids double-counting a copied run. In 083, t05 (48.51) ≠ t06 (47.57). [repo: work/076/05-build-report.md L59, work/076/06-verification.md L17, L36; derived]

### Fixtures
- F22. 083 positive fixture (lines as committed): research `10:15 | R1 | 083 | brief written | 0`, `10:15 | R2 | 083 | 3 for / 3 against | languages: N/A`, `10:15 | R3 | 083 | 4 verified, 0 fixed, 0 removed | READY`. Implementation `10:15 | I1 | 083 | FIT | 2 files planned`, `10:15 | I2 | 083 | 2 files changed | tests 344/344`, `10:15 | I3 | 083 | PASS | sent to audit: yes`. 05 has `344 passed, 1 skipped in 48.51s` and 06 has `344 passed, 1 skipped in 47.57s`. The I2 field `tests 344/344` is the pre-076 form, which is INCOMPLETE under TESTS_FORMAT_FROM = 76 (084's issue). A fixture with an ID ≥ 076 should use pytest's line (`2 files changed | tests 344 passed, 1 skipped in 48.51s`) so it tests only LOG BATCH. [repo: logs/research/2026-11-20.md L3-5; logs/implementation/2026-11-20.md L18-20; scripts/check_pipeline.py L225, L281]
- F23. Correctly spaced negative fixture: 079's lines (R1 23:25, R2 23:28, R3 23:35, I1 23:39 on 2026-11-19; I2 02:02, I3 02:10 FAIL, I2 02:15, I3 02:22 on 2026-11-20). Last round: I3 FAIL 02:10 -> I3 02:22 = 12 min, t05 87.19 s, t06 89.70 s, sum 176.89 s < 13 × 60 = 780 s. This also covers a date rollover and a send-back round. A near-threshold negative: same-minute round start and I3 with t05 + t06 = 59.99 s gives no flag. Positive: 60.00 s gives a flag. [repo: logs/research/2026-11-19.md L3-16; logs/implementation/2026-11-19.md L6, 2026-11-20.md L14-17; work/079/05-build-report.md L51, work/079/06-verification.md L144]

### Mutations ("Done looks like")
- M1 (rule C): change `≥` to `>`, or drop the `+1` in (Δ+1). The 60.00 s boundary fixture fails.
- M2 (rule C): read only t05 (ignore 06). 083's fixture (48.51 < 60) loses `LOG BATCH: 083`.
- M3 (rule D): remove the later-file check. A fixture that runs `--log R1 999` with 02-06 present then writes a line, and the test fails. Remove the send-back exception: a round-2 `--log I2` after an I3 FAIL line is refused, and that test fails.

## Numbers used (show the math)
Per item: first-round lines (date omitted unless it changes), the largest number of the item's lines in one minute, the I2->I3 minutes per round, and the 05/06 suite times (largest run in 05 | 06; "-" = no time printed).

| Item | Lines | Max/min | I2->I3 | 05 / 06 run (s) | A | B | C |
|---|---|---|---|---|---|---|---|
| 045 | R1 22:19 R2 22:19 R3 22:20 I1 22:20 I2 22:23 I3 22:24 | 2 | 1 | 16.96 / - | - | - | - |
| 046 | same as 045 | 2 | 1 | 16.96 / - | - | - | - |
| 047 | 22:17 22:18 22:18 22:18 22:19 22:20 | 3 | 1 | 18.64 / - | X | - | - |
| 048 | all 20:40 | 6 | 0 | - / - | X | - (no time) | n/c |
| 049 | 22:18 22:18 22:19 22:19 22:20 22:21 | 2 | 1 | 22.63 / - | - | - | - |
| 050 | 22:21 x4, 22:22 x2 | 4 | 0 | 22.92 / - | X | - (22.92) | - (Δ1) |
| 051 | 22:17 x4, 22:18, 22:19 | 4 | 1 | 16.57 / - | X | - | - |
| 052 | 22:23 x4, 22:26 x2 | 4 | 0 | 21.45 / - | X | - (21.45) | - |
| 053 | 22:22 22:28 22:37 22:44 22:50 22:56 | 1 | 6 | 23.54 / 25.35 | - | - | - |
| 054 | 13:54 x4, 13:55 x2 | 4 | 0 | 22.90 / - | X | - (22.90) | - (Δ1, 22.90 < 120) |
| 055 | all 14:09 | 6 | 0 | - / - | X | - (no time) | n/c |
| 056 | 14:18 x4, 14:19 x2 | 4 | 0 | - / - | X | - (no time) | n/c |
| 058 | all 14:49 | 6 | 0 | - / - | X | - (no time) | n/c |
| 059 | 23:21 23:21 23:22 23:22 23:23 23:23 | 2 | 0 | 0.55 / - | - | - (0.55) | - |
| 060 | 23:24 x4, 23:25, 23:26 | 4 | 1 | 0.55 / - | X | - | - |
| 061 | R1-R3 22:35 (11-13); R3 00:06, I1 04:36, I2 05:10, I3 05:22 F, I2 05:27, I3 05:32 | 3 | 12, 5 | 61.68 / 58.14 | X | - | - |
| 062 | 23:27 23:29 23:34 23:37 23:42 23:46F 23:47 23:49 | 1 | 4, 2 | 26.61 / 25.25 | - | - | - |
| 063 | 23:22 23:23 23:33 23:37 / 00:10 00:29 | 1 | 19 | 55.09 / 51.95 | - | - | - |
| 064 | 23:24 23:26 23:33 / 00:11 00:16 00:21 | 1 | 5 | 51.67 / 52.58 | - | - | - |
| 065 | 23:22 23:24 23:33 23:37 23:59 / 00:13 | 1 | 14 | 42.67 / 44.88 | - | - | - |
| 066 | 23:21 23:23 23:29 23:33 23:38 23:42 | 1 | 4 | 47.65 / 46.44 | - | - | - |
| 067 | 23:20 23:21 23:29 23:31 23:45 23:52 | 1 | 7 | 69.71 / 53.01 | - | - | - |
| 068 | 23:20 23:21 23:28 23:31 / 00:12 00:20 | 1 | 8 | 55.51 / 52.67 | - | - | - |
| 069 | 23:21 23:24 23:32 23:37 23:44 23:50F 23:55 23:58; I1 00:12 I2 00:20 I3 00:25 | 1 | 6, 3, 5 | 63.33 / 63.76 | - | - | - |
| 070 | 23:22 23:24 23:36 23:40 23:52 / 00:00F 00:08 00:15 00:24 00:28 | 1 | 8, 7, 4 | 63.04 / 63.55 | - | - | - |
| 071 | 23:23 23:26 23:38 23:45 23:54 / 00:08 | 1 | 14 | 62.74 / 64.00 | - | - | - |
| 072 | 23:22 23:26 23:31 23:34 23:42 23:48 | 1 | 6 | 60.01 / 62.97 | - | - | - |
| 073 | 23:22 23:27 23:34 23:37 23:46 23:51 | 1 | 5 | 60.40 / 62.24 | - | - | - |
| 074 | 23:24 23:27 23:38 23:43 / 00:08 00:28 | 1 | 20 | 68.26 / 61.83 | - | - | - |
| 075 | 23:27 23:31 23:41 23:46 23:51 23:57 | 1 | 6 | 69.79 / 64.91 | - | - | - |
| 076 | 23:25 23:30 23:37 23:41 / 00:10 00:17F; I1 00:20 I2 00:25 I3 00:31 | 1 | 7, 6 | 85.49 / 85.49 | - | - | - |
| 077 | 23:29 23:32 23:44 23:51 / 00:44 00:58F 01:02 01:12 | 1 | 14, 10 | 91.97 / 104.86 | - | - | - |
| 078 | 23:27 23:32 23:37 23:45 / 01:29 01:45 | 1 | 16 | 100.14 / 113.36 | - | - | - |
| 079 | 23:25 23:28 23:35 23:39 / 02:02 02:10F 02:15 02:22 | 1 | 8, 7 | 90.93 / 90.21 | - | - | - |
| 083 | all 10:15 | 6 | 0 | 48.51 / 47.57 | X | X | X |

A = 3+ lines of the item in one minute; B = I2 and I3 in the same minute and a 05/06 run > 30 s; C = t05 + t06 ≥ (Δ+1)×60 s over the last round (round start = latest I1 or I3 line before the round's I2; end = its I3); n/c = not computable (no time printed); F = an I3 FAIL line. "Max/min" = the most lines of the item in one minute; for 061 it is the three R lines at 22:35. Times are from logs/research/*.md and logs/implementation/*.md. Runs are from the work/<ID>/05 and 06 grep: the largest "N passed ... in X s" per file, which is an upper bound for C. 076/06's largest (85.49) is a quoted I2 run (F21), and its own runs are 83.27 and 85.42.

Counts over 35 items:
- Rule A: 12 flagged (047, 048, 050, 051, 052, 054, 055, 056, 058, 060, 061, 083). 2 are known batches and 10 are possible false positives (not provable). From 062 on (19 items): 1 flagged (083), 0 false positives.
- Rule B: 9 items have I2 and I3 in the same minute. 1 flagged (083), 0 false positives, and it misses 048. Not a proof (F9).
- Rule C: 1 flagged (083), 0 false positives, proved: 48.51 + 47.57 = 96.08 ≥ 60. 4 not computable (048, 055, 056, 058). Every other item has Δ ≥ 1 minute for its last round. The tightest before 061 is 054 (I1 13:54 -> I3 13:55, Δ1, 22.90 s vs 120 s). From 061 on the tightest last round is 066 (Δ9, 94.09 s vs 600 s), and the tightest of any round is 069 round 2 (Δ8, under a 540 s limit).
- Rule (a) (previous line exists): 0 flagged. 083 is in order (F17).
- Rule D (later step file exists at `--log`): catches 083 and 048 by construction. Its history count cannot be replayed (UNVERIFIED).
- Margin (F16): from 061 on, the smallest I2->I3 gap is 3 min and the smallest round span is 8 min.

## Fit for a ~$3k account
Not applicable to trading. Only scripts/check_pipeline.py, tests/ and, if chosen, rule text change. Nothing in ccbot/, config/ or data/ changes, and nothing connects to a brokerage. scripts/check_pipeline.py is a RULE_PATH (L260), so the change needs the person's OK at PR review.

## Open questions
1. My recommendation for R2/R3: pair rule D (write-time, `--log` refuses when a later step file exists, with the I3 FAIL / A1 FAIL send-back exception) with rule C (`LOG BATCH: <ID>` in check_pipeline, exit 1 like LOG TIME). Rule C has 0 false positives on 35 items and proves its one hit. Rule D catches untimed batches like 048/055/058 going forward. Rule B as the request words it has the same count as C but is not a proof (F9). Rule A from 062 on also gives exactly 083, but it relies on agents never being fast (F13).
2. Cutoff and exception: should rule C start at LOG_CHECK_FROM (45)? It gives the same result, since only 083 is flagged. If so, 083 needs a named exception like 048 (F20) so main exits 0, but then the "083 fixture is flagged" condition (RI-010) is met only in tests/. Or should it start at 084 with 083 as a fixture only?
3. Rule D's exception: are an I3 FAIL line and an A1 FAIL in 07 the only legitimate reasons for a later step file to exist (F18)? 061's second R3 line is the one past case R1 cannot check.
4. Rule C parsing: last summary line in the `## Test output` / `## Tests re-run` section only, and t06 counted only when ≠ t05 (F21)? Or every run in the sections, which is stronger but double-counts copies?
5. Should 05/06 be required to print the pytest time (048, 055, 056, 058 printed none, so rule C cannot run on them)? Since 076, the I2 log field already carries pytest's line with its time (L281). For items ≥ 076, rule C could read t05 from the I2 log line instead of 05.
