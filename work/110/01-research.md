# 01 Research brief - 110
## Question
Item 103 left two LOG BATCH residuals open. Should each one get a rule (with fixtures and a mutation), or should it be recorded as a documented no-go? [work/110/request.md L7, L11, L15; work/103/03-handoff.md L68]
- (a) A pytest summary line sits directly under a `## Round N (...)` wrapper (`#` or `##`, any wording that is neither 091's run heading nor 098's build heading), with no run-shaped sub-heading. Neither the 091 rule nor the 098 rule sees it, and LOG BATCH never reads it.
- (b) SUMMARY_LINE never matches a run whose pytest line contains `N deselected` (a `-k` or single-file run). Such a run is never counted in LOG BATCH's Σ.

The request says "measure first". R1 has no shell, so the measurement is the read-only script below. Its result is PENDING.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Repo facts cite file:line, read on branch daily-fixes/2026-11-25 on 2026-11-25. The only outside fact is pytest's summary-line format.

1. Item 103 measured 30 of 152 summary lines in work/076-098 05/06 as sitting outside every read section, 0 of them at 092-098. 14 of the 30 are correctly quoted. The broad rule (any outside SUMMARY_LINE) and the narrow `#{1,2} round \d+\b` wrapper rule were both NO-GO: the narrow rule gives 9 hits, 6 of them quoted. [work/103/03-handoff.md L5-9, L66-67; logs/audit/2026-11-25-103.md L17-25]
2. 103 states residual (a) like this: in 076-098 the only real run under a non-run wrapper with no run sub-heading is 076/05 L59, and the 098 rule covers that line. Its suggested fix if the shape comes back at 099 or later is "the template sentence (templates/build-report.md L10) plus a heading rule, not a summary-line rule". [work/103/03-handoff.md L68; work/103/02-improvements.md L54, L82]
3. The narrow rule failed on mutant lines: 076/05 rows 1-4 under `## Round 2 build` and 084/05 rows 19-20 under `## Round 2 mutations`. A wrapper rule that skips `build` (already the 098 rule) and keeps `mutation` would still be a heading-wording rule. 02 AGAINST 3 says that kind of rule costs more than it covers. [work/103/03-handoff.md L50; work/103/02-improvements.md L20-23, L38-39, L64]
4. `_section_flags` opens a read section only at an "out" row matching RUN_HEADING (`## Test output\b` for 05, `## Tests re-run\b` for 06). It closes the section at any "out" `#`/`##` row. So a `# Round N` or `## Round N` wrapper closes a read section, and rows under it are unread until the next opener. [scripts/check_pipeline.py L497, L1454-1468]
5. The 091 and 098 rules flag headings only (`stray_run_headings`, STRAY_RUN_HEADING L498, ROUND_BUILD_HEADING L500), from ROUND_HEADING_FROM = 92 and ROUND_BUILD_FROM = 99. Each is gated by `_rule_seen`. [scripts/check_pipeline.py L452, L459, L1135-1159, L1471-1483]
6. A new case at 099 or later: 104/06 L108 has the wrapper `# Round 2 (2026-11-25, I3)`, and its round-2 suite sits under `## Tests re-run (round 2)` (L123, L136). That opener matches RUN_HEADING, so LOG BATCH reads it. The same file's mutant lines (L145-162) start with `BASE:`/`M56:` etc., so SUMMARY_LINE (`.match` at the line start) does not match them. This is the only `#{1,2} Round N` heading in work/099-104 05/06. [Grep `^#{1,2} [Rr]ound \d+` over work/{099..104}/0[56]-*.md; Grep of work/104/06-verification.md headings and `in \d+\.\d+s` lines]
7. 05/06 files exist for 099-104 only. 105-109 have none yet. So for (a), the only data newer than 103's measurement is 099-104, and the script below covers it. [Glob work/1[01][0-9]/0[5-7]-*.md and work/09[89]/0[5-7]-*.md]
8. Design note for (b): the code leaves `deselected` out of `_STATS_PARTS` on purpose, with the comment "a full-suite run has none". `--log` refuses `deselected` in the I2 field. [scripts/check_pipeline.py L464-470, L117-118]
9. LOG BATCH's Σ uses the largest time per file, not a sum: t05 = max over 05's read sections plus the I2 fields, and t06 = max of 06's read values after copies are dropped. A missed run can therefore change Σ only if it is longer than every counted run in its file. [scripts/check_pipeline.py L1571-1588]
10. Leaving a run out can only lower Σ, so (b) can cause a missed flag but never a false one. The docstring already says the same for gap (w): "only lowers Σ". [scripts/check_pipeline.py L194-196, L1587-1588]
11. pytest's summary part order is KNOWN_TYPES = failed, passed, skipped, deselected, xfailed, xpassed, warnings, error, subtests passed/failed/skipped. So `deselected` comes right after `skipped`. [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py]
12. pytest's `pluralize` changes only "error", "warnings" and "test". `deselected` is printed as `N deselected` for every N, including 1. [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py]
13. pytest records deselected items through the `pytest_deselected` hook (`self._add_stats("deselected", items)`), and the normal summary line prints every non-empty known type. [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py]
14. Rough size of (b): Grep `deselected in \d` over work/*/0[56]-*.md finds 308 occurrences across 49 files (053-104). This is an upper bound only. It does not separate inside from outside, and it counts prose and quoted lines. [Grep tool count, this brief]
15. An example of a (b) line: A1's mutant run `1 failed, 506 deselected in 0.65s` (103 audit). Its time is under 1 s, while full suites in the same item take 120.27 s. If that pattern holds, a deselected run is never the per-file max. This has not been measured across all items, so it is UNVERIFIED until the script runs. [logs/audit/2026-11-25-103.md L38-45]

## Numbers used (show the math)
- 103's totals, as stated there: 60 + 62 + 23 + 7 = 152 summary lines, 23 + 7 = 30 outside. Narrow rule: 9 hits = 6 Q + 3 R. [work/103/03-handoff.md L83-86]
- Effect of (b) on Σ (finding 9): Σ' = max(t05 ∪ D05) + max(t06' ∪ D06'), where D is the set of deselected times. If max(D) < max(t) in both files, then Σ' = Σ and no flag changes. The script measures this directly instead of assuming it.
- No other number is derived by hand. Everything else is PENDING on the script.

## Script for the orchestrator
Read-only. It writes no files, runs no git (`batch_log_items` and `_run_seconds` use no git, L182, L1433-1451), and imports only `scripts/check_pipeline.py`, which imports only the standard library (L415-421) and runs `main()` only under `__main__` (L2398). It changes `cp.SUMMARY_LINE` only in memory, for the (b) comparison, and restores it afterwards. Run it from the repo root on the branch head, paste the full stdout and exit code below, and say which commit it ran on.

```
cd /home/claude/cover-calls && python3 -I - <<'EOF'
import sys, re, collections
sys.path.insert(0, "scripts")
import check_pipeline as cp
from pathlib import Path

# (b) the SUMMARY_LINE variant with pytest's "N deselected" part after "skipped" (KNOWN_TYPES order)
parts = list(cp._STATS_PARTS)
assert parts[2] == rf"{cp._N} skipped", parts[2]
parts.insert(3, rf"{cp._N} deselected")
STATS_D = r"(?=[1-9])" + "".join(f"(?:{p}{cp._END})?" for p in parts)
SUMMARY_D = re.compile(rf"(?:=+ )?(?={cp._N} )(?:{STATS_D}) in (\d+\.\d+)(?:s| seconds)\b")
for s, base_ok, d_ok in [("1 failed, 506 deselected in 0.65s", False, True),
                         ("1 passed, 506 deselected in 0.59s", False, True),
                         ("994 passed, 1 skipped in 120.27s (0:02:00)", True, True),
                         ("2 passed, 1 skipped, 3 deselected, 1 warning in 0.10s", False, True),
                         ("FAILED t[1 failed in 58.86s]", False, False),
                         ("BASE: 13 failed, 119 passed in 0.25s", False, False)]:
    assert bool(cp.SUMMARY_LINE.match(s)) is base_ok and bool(SUMMARY_D.match(s)) is d_ok, s
print("SELF-TEST ok")

# (a) wrapper: an out `#`/`##` heading `round N` that is neither opener, STRAY (091) nor ROUND_BUILD (098)
WRAP = re.compile(r"#{1,2} round \d+\b", re.I)
def is_wrap(h, step):
    return bool(WRAP.match(h)) and not cp.STRAY_RUN_HEADING.match(h) \
        and not cp.ROUND_BUILD_HEADING.match(h) and not re.match(cp.RUN_HEADING[step], h)

def band(n):
    return "<092" if n < 92 else ("092-098" if n < 99 else ">=099")

ids = sorted(int(d.name) for d in Path("work").glob("[0-9][0-9][0-9]") if d.is_dir())
A = collections.Counter(); AD = collections.Counter(); B = collections.Counter(); W = collections.Counter()
files = 0
for n in ids:
    if n < cp.TESTS_FORMAT_FROM:
        continue
    for step in ("05", "06"):
        p = Path("work") / f"{n:03d}" / cp.STEPS[step]
        if not p.exists():
            continue
        text, why = cp._read(p)
        if why:
            print(f"{n:03d}/{step}: {why}"); continue
        files += 1
        rows, open_end = cp._md_lines(text)
        if open_end:
            print(f"{n:03d}/{step}: open_fence_at_end=True (in/out split suspect)")
        flags = cp._section_flags(rows, cp.RUN_HEADING[step])
        sec = near = "(none)"
        for (line, state), inside in zip(rows, flags):
            if state == "out" and re.match(r"#{1,2} ", line):
                sec = near = line.strip()
                if is_wrap(sec, step):
                    W[band(n)] += 1
                    print(f"  WRAP {n:03d}/{step} | {sec[:80]}")
            elif state == "out" and re.match(r"#{1,6} ", line):
                near = line.strip()
            if state not in ("out", "in"):
                continue
            s = line.strip()
            m0, m1 = cp.SUMMARY_LINE.match(s), SUMMARY_D.match(s)
            if m0 and not m1:
                print(f"  REGEX NOT SUPERSET {n:03d}/{step} | {s[:90]}")
            under_bare_wrap = (not inside) and near == sec and is_wrap(sec, step)
            if under_bare_wrap and m0:
                A[band(n)] += 1
                print(f"  A {n:03d}/{step} | {state} | section={sec[:60]} | {s[:90]}")
            elif under_bare_wrap and m1:
                AD[band(n)] += 1
                print(f"  A-DESEL {n:03d}/{step} | {state} | section={sec[:60]} | {s[:90]}")
            if m1 and not m0:
                B["in" if inside else "out", step] += 1
                if inside:
                    print(f"  B-IN {n:03d}/{step} | {state} | section={sec[:60]} | t={m1[1]} | {s[:90]}")
print("FILES READ (>= TESTS_FORMAT_FROM):", files)
print("(a) WRAP HEADINGS BY BAND:", dict(W))
print("(a) SUMMARY_LINE UNDER A BARE WRAPPER BY BAND:", dict(A))
print("(a) DESELECTED-ONLY LINES UNDER A BARE WRAPPER BY BAND:", dict(AD))
print("(b) DESELECTED-ONLY SUMMARY LINES (in/out read section, step):", dict(B))

# (b) per-file max change and LOG BATCH outcome, all IDs >= LOG_CHECK_FROM
def maxes():
    out = {}
    for n in ids:
        if n < cp.LOG_CHECK_FROM:
            continue
        for step in ("05", "06"):
            t, why = cp._run_seconds(Path("work") / f"{n:03d}" / cp.STEPS[step], cp.RUN_HEADING[step])
            out[n, step] = (max(t) if t else None, len(t), why)
    return out
base_m, base = maxes(), cp.batch_log_items()
orig = cp.SUMMARY_LINE
cp.SUMMARY_LINE = SUMMARY_D
try:
    alt_m, alt = maxes(), cp.batch_log_items()
finally:
    cp.SUMMARY_LINE = orig
changed_count = changed_max = 0
for k in sorted(base_m):
    if base_m[k][1] != alt_m[k][1]:
        changed_count += 1
    if base_m[k][0] != alt_m[k][0]:
        changed_max += 1
        print(f"  MAX CHANGED {k[0]:03d}/{k[1]}: {base_m[k][0]} -> {alt_m[k][0]} (values {base_m[k][1]} -> {alt_m[k][1]})")
print("(b) FILES WITH MORE READ VALUES:", changed_count, "| FILES WHOSE MAX CHANGED:", changed_max)
for key in ("flagged", "flagged_ids", "excepted", "not_computable", "checked", "in_progress"):
    same = base[key] == alt[key]
    print(f"(b) batch_log_items[{key}] same={same}" + ("" if same else f" | base={base[key]} | with deselected={alt[key]}"))
print("BASE flagged_ids:", base["flagged_ids"], "| checked:", base["checked"])
EOF
```

Result (run by the orchestrator 2026-11-25 23:28 UTC on daily-fixes/2026-11-25 at 4404a28, `python3 -I -` from the repo root; full stdout, last line is the exit code):

```
SELF-TEST ok
  WRAP 076/05 | # Round 1 report (kept as written, 266a6a2)
  WRAP 076/06 | # Round 2
  B-IN 076/06 | in | section=## Tests re-run (output) | t=0.99 | 19 passed, 169 deselected in 0.99s
  WRAP 076/06 | # Round 1 (kept as written, 266a6a2)
  B-IN 076/06 | in | section=## Tests re-run (output) | t=2.75 | 34 passed, 154 deselected in 2.75s
  B-IN 076/06 | in | section=## Tests re-run (output) | t=2.86 | 2 failed, 32 passed, 154 deselected in 2.86s
  WRAP 077/05 | # Round 2 (I3 FAIL round 1 -> I2, tests only)
  WRAP 077/05 | # Round 1
  B-IN 077/06 | in | section=## Tests re-run (output) | t=5.56 | 1 failed, 1 passed, 211 deselected in 5.56s
  B-IN 077/06 | in | section=## Tests re-run (output) | t=4.01 | 1 failed, 1 passed, 211 deselected in 4.01s
  B-IN 077/06 | in | section=## Tests re-run (output) | t=0.32 | 1 failed, 1 passed, 211 deselected in 0.32s
  WRAP 077/06 | # Round 1 (FAIL, kept for the record)
  WRAP 079/05 | ## Round 2 (I3 FAIL round 1, P1)
  WRAP 079/05 | ## Round 1
  WRAP 079/06 | ## Round 1 (FAIL, kept for the record)
  B-IN 080/06 | in | section=## Tests re-run (output) | t=0.16 | 1 passed, 8 deselected in 0.16s
  WRAP 081/05 | ## Round 2 (2026-11-21, I2)
  WRAP 081/06 | # Round 2 (2026-11-21, I3)
  WRAP 082/05 | ## Round 2 (sent back by I3, 06 finding 1)
  WRAP 082/06 | ## Round 1 (FAIL, kept for the record)
  B-IN 084/05 | in | section=## Test output (pasted, not summarized) | t=6.06 | 7 failed, 2 passed, 238 deselected in 6.06s
  B-IN 084/05 | in | section=## Test output (pasted, not summarized) | t=3.87 | 3 failed, 6 passed, 238 deselected in 3.87s
  B-IN 084/05 | in | section=## Test output (pasted, not summarized) | t=4.35 | 1 failed, 8 passed, 238 deselected in 4.35s
  B-IN 084/05 | in | section=## Test output (pasted, not summarized) | t=4.27 | 6 failed, 3 passed, 238 deselected in 4.27s
  B-IN 084/05 | in | section=## Test output (pasted, not summarized) | t=3.71 | 1 failed, 8 passed, 238 deselected in 3.71s
  WRAP 084/05 | # Round 2 (I3 FAIL F1, work/084/06-verification.md; 2026-11-21, base HEAD 416835
  WRAP 084/05 | ## Round 2 changes (file: what changed)
  WRAP 084/05 | ## Round 2 deviation from plan
  WRAP 084/05 | ## Round 2 connectivity check
  WRAP 084/05 | ## Round 2 mutations (scratch copy, never the repo)
  A-DESEL 084/05 | in | section=## Round 2 mutations (scratch copy, never the repo) | 4 failed, 7 passed, 266 deselected in 2.00s
  A-DESEL 084/05 | in | section=## Round 2 mutations (scratch copy, never the repo) | 4 failed, 7 passed, 266 deselected in 2.07s
  A 084/05 | in | section=## Round 2 mutations (scratch copy, never the repo) | 8 failed, 269 passed in 33.54s
  A 084/05 | in | section=## Round 2 mutations (scratch copy, never the repo) | 8 failed, 269 passed in 33.72s
  WRAP 084/05 | ## Round 2 recurring issues checked
  B-IN 084/06 | in | section=## Tests re-run (output) | t=3.73 | 11 failed, 2 passed, 264 deselected in 3.73s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.59 | 4 failed, 9 passed, 264 deselected in 4.59s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.57 | 2 failed, 11 passed, 264 deselected in 4.57s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.93 | 6 failed, 7 passed, 264 deselected in 4.93s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.59 | 2 failed, 11 passed, 264 deselected in 4.59s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.52 | 5 failed, 8 passed, 264 deselected in 4.52s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=4.80 | 5 failed, 8 passed, 264 deselected in 4.80s
  B-IN 084/06 | in | section=## Tests re-run (output) | t=0.68 | 3 failed, 1 passed, 273 deselected in 0.68s
  WRAP 084/06 | ## Round 1 (FAIL, kept for the record)
  WRAP 086/05 | ## Round 2 (2026-11-21, I2)
  WRAP 086/06 | # Round 1 (FAIL, kept as written)
  B-IN 086/06 | in | section=## Tests re-run (output) | t=2.51 | 1 failed, 3 passed, 243 deselected in 2.51s
  WRAP 087/05 | ## Round 2 (2026-11-22, I2)
  B-IN 087/06 | in | section=## Tests re-run (output) | t=0.13 | 1 passed, 8 deselected in 0.13s
  WRAP 087/06 | # Round 1 (FAIL, kept as written)
  WRAP 091/05 | ## Round 2 (I3 FAIL round 1: 06 F1, F2, F3)
  WRAP 091/06 | # Round 2 (I3, 2026-11-22)
  B-IN 093/05 | in | section=## Test output (pasted, not summarized) | t=3.67 | 30 passed, 375 deselected in 3.67s
  B-IN 093/06 | in | section=## Tests re-run (output) | t=2.57 | 30 passed, 375 deselected in 2.57s
  B-IN 094/05 | in | section=## Test output (pasted, not summarized) | t=13.07 | 46 passed, 377 deselected in 13.07s
  WRAP 094/05 | ## Round 2 changes (file: what changed)
  B-IN 094/05 | in | section=## Test output (round 2, pasted) | t=1.19 | 6 passed, 419 deselected in 1.19s
  B-IN 094/05 | in | section=## Test output (round 2, pasted) | t=4.60 | 3 failed, 3 passed, 419 deselected in 4.60s
  B-IN 094/05 | in | section=## Test output (round 2, pasted) | t=4.01 | 3 failed, 3 passed, 419 deselected in 4.01s
  B-IN 094/05 | in | section=## Test output (round 2, pasted) | t=0.24 | 1 failed, 4 passed, 420 deselected in 0.24s
  B-IN 094/05 | in | section=## Test output (round 2, pasted) | t=0.70 | 1 failed, 424 deselected in 0.70s
  B-IN 095/05 | in | section=## Test output (pasted, not summarized) | t=23.78 | 37 passed, 396 deselected in 23.78s
  B-IN 099/05 | in | section=## Test output (pasted, not summarized) | t=1.60 | 15 passed, 491 deselected in 1.60s
  B-IN 099/06 | in | section=## Tests re-run (output) | t=6.98 | 15 passed, 491 deselected in 6.98s
  B-IN 100/05 | in | section=## Test output (pasted, not summarized) | t=9.31 | 2 failed, 13 passed, 488 deselected in 9.31s
  B-IN 100/05 | in | section=## Test output (pasted, not summarized) | t=0.19 | 20 passed, 483 deselected in 0.19s
  B-IN 100/05 | in | section=## Test output (pasted, not summarized) | t=3.12 | 1 failed, 3 passed, 499 deselected in 3.12s
  B-IN 100/05 | in | section=## Test output (pasted, not summarized) | t=3.73 | 4 passed, 499 deselected in 3.73s
  B-IN 100/05 | in | section=## Test output (round 2, pasted) | t=2.31 | 1 failed, 3 passed, 499 deselected in 2.31s
  B-IN 100/06 | in | section=## Tests re-run (output) | t=2.44 | 1 failed, 3 passed, 499 deselected in 2.44s
  B-IN 100/06 | in | section=## Tests re-run (output) | t=0.73 | 4 passed, 499 deselected in 0.73s
  B-IN 100/06 | in | section=## Tests re-run (round 2) | t=0.98 | 3 failed, 8 passed, 492 deselected in 0.98s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.66 | 14 passed, 485 deselected in 0.66s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.65 | 1 failed, 13 passed, 485 deselected in 0.65s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.73 | 1 failed, 13 passed, 485 deselected in 0.73s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.74 | 1 failed, 13 passed, 485 deselected in 0.74s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.81 | 2 failed, 12 passed, 485 deselected in 0.81s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.83 | 2 failed, 12 passed, 485 deselected in 0.83s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.69 | 1 failed, 13 passed, 485 deselected in 0.69s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.79 | 1 failed, 13 passed, 485 deselected in 0.79s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.75 | 1 failed, 13 passed, 485 deselected in 0.75s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.76 | 1 failed, 13 passed, 485 deselected in 0.76s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.68 | 1 failed, 13 passed, 485 deselected in 0.68s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.98 | 4 failed, 495 deselected in 0.98s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=1.17 | 4 failed, 495 deselected in 1.17s
  B-IN 101/05 | in | section=## Test output (pasted, not summarized) | t=0.80 | 2 failed, 497 deselected in 0.80s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=2.55 | 14 passed, 485 deselected in 2.55s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.85 | 1 failed, 13 passed, 485 deselected in 0.85s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.76 | 1 failed, 13 passed, 485 deselected in 0.76s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.73 | 1 failed, 13 passed, 485 deselected in 0.73s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.80 | 2 failed, 12 passed, 485 deselected in 0.80s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.69 | 2 failed, 12 passed, 485 deselected in 0.69s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.72 | 1 failed, 13 passed, 485 deselected in 0.72s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.73 | 1 failed, 13 passed, 485 deselected in 0.73s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.78 | 1 failed, 13 passed, 485 deselected in 0.78s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.71 | 1 failed, 13 passed, 485 deselected in 0.71s
  B-IN 101/06 | in | section=## Tests re-run (output) | t=0.73 | 1 failed, 13 passed, 485 deselected in 0.73s
  B-IN 102/05 | in | section=## Test output (pasted, not summarized) | t=0.50 | 12 passed, 34 deselected in 0.50s
  B-IN 102/05 | in | section=## Test output (pasted, not summarized) | t=1.44 | 11 passed, 507 deselected in 1.44s
  B-IN 102/06 | in | section=## Tests re-run (output) | t=4.40 | 23 passed, 541 deselected in 4.40s
  B-IN 102/06 | in | section=## Tests re-run (output) | t=0.19 | 1 passed, 8 deselected in 0.19s
  B-IN 103/05 | in | section=## Test output (pasted, not summarized) | t=0.64 | 2 passed, 505 deselected in 0.64s
  B-IN 103/06 | in | section=## Tests re-run (output) | t=0.07 | 2 passed, 505 deselected in 0.07s
  WRAP 104/06 | # Round 2 (2026-11-25, I3)
FILES READ (>= TESTS_FORMAT_FROM): 58
(a) WRAP HEADINGS BY BAND: {'<092': 26, '092-098': 1, '>=099': 1}
(a) SUMMARY_LINE UNDER A BARE WRAPPER BY BAND: {'<092': 2}
(a) DESELECTED-ONLY LINES UNDER A BARE WRAPPER BY BAND: {'<092': 2}
(b) DESELECTED-ONLY SUMMARY LINES (in/out read section, step): {('out', '05'): 6, ('in', '06'): 36, ('in', '05'): 36, ('out', '06'): 5}
(b) FILES WITH MORE READ VALUES: 34 | FILES WHOSE MAX CHANGED: 0
(b) batch_log_items[flagged] same=True
(b) batch_log_items[flagged_ids] same=True
(b) batch_log_items[excepted] same=True
(b) batch_log_items[not_computable] same=True
(b) batch_log_items[checked] same=True
(b) batch_log_items[in_progress] same=True
BASE flagged_ids: [] | checked: 59
exit 0
```

What to read from the output:
- (a) The number of `A` lines at `>=099` (the newest shapes) and at `092-098`. Also each A line's text, so R2/R3 can mark it R (a real run of the item) or Q (correctly quoted: mutant, base-failure, evidence). This R/Q call is made by hand, as in 103 01 (e), and the script does not make it.
- (a) `WRAP` headings at `>=099`: how often the wrapper shape occurs at all. From finding 6, 104/06 L108 is expected to be one, with 0 A lines under it, because its suite sits under `## Tests re-run (round 2)`. This is UNVERIFIED until the script runs.
- (b) `B-IN` lines: deselected runs inside read sections that LOG BATCH skips today. `MAX CHANGED` and the `batch_log_items[...] same=` lines show whether counting them would change any per-file max or any LOG BATCH result.
- `REGEX NOT SUPERSET` must not appear. If it does, the variant regex is wrong and the (b) comparison is void.

## Fit for a ~$3k account
No account effect. This is a pipeline-check question only. It touches no trading code, cap, quote, order path, tax or commission figure.

## Open questions
1. Decision rule for (a), for R2/R3 (request L11, following 103). Build a rule only if the measured A lines at or above the cutoff include no correctly quoted line, and only if it adds a catch that 091/098 miss. If the A count at 092 and above is 0, the benefit is unmeasured and 103's finding stands: R3 records a no-go and can offer the template sentence (103 03 L68) as text only. UNVERIFIED until the script runs.
2. Decision rule for (b). If every `batch_log_items[...]` line says `same=True` and `FILES WHOSE MAX CHANGED` is 0, counting deselected runs would change no outcome in any item. A rule would then add a fixture and mutation for zero effect, so it is a no-go candidate. The case for building it: a deselected run can never cause a false flag (finding 10), because it is a real run that took real time, so adding it is safe in principle. The design comment at L465 says a full suite has no deselected part, and LOG BATCH reads all runs, not only the full suite. That rests on L465's stated reason; any further reasoning is UNVERIFIED. R3 decides.
3. If (b) is built: the variant must keep pytest's order (`deselected` after `skipped`, finding 11) and must not loosen the I2 `--log` field (L117-118). SUMMARY_LINE is shared by the I2 per-round bound (L1535, L1579), and I2 fields cannot contain `deselected`, so that path is unchanged. A cutoff and a `_rule_seen` gate are needed only if the change could flag an earlier item. The script's `flagged` comparison answers that.
4. Without the orchestrator's output, both parts are BLOCKED on numbers (RI-001).
5. R1 log line: the orchestrator runs `python3 scripts/check_handoff.py 110` for the sources count, then `python3 scripts/check_pipeline.py --log R1 110 "brief written | <count>"`.
