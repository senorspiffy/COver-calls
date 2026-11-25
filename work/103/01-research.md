# 01 Research brief - 103
## Question
Should LOG BATCH get the broad rule (098 Residual (a)): from a new cutoff, a pytest summary line (SUMMARY_LINE) in a 05/06 file that sits outside every section LOG BATCH reads is INCOMPLETE? The request says to build it only if it flags no correctly quoted run at or above the cutoff. R1 has no shell, so this brief gives the exact read-only measurement for the orchestrator to run, and the counts R2/R3 need from it.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Sources here are repo files (file:line). No outside facts are needed: the question is only about this repo's own check.

1. What LOG BATCH reads. `_run_seconds` counts a SUMMARY_LINE only on rows where `_section_flags(rows, heading)` is True. The heading is `RUN_HEADING["05"] = r"## Test output\b"` or `RUN_HEADING["06"] = r"## Tests re-run\b"`. A section opens at the heading and closes at the next `#`/`##` heading outside fences. Rows inside fences ("in") count, fence marks ("mark") don't, and HTML comments are dropped first (`_md_lines`). [scripts/check_pipeline.py L492, L1422-1457, L652-666]
2. SUMMARY_LINE is `re.compile(rf"(?:=+ )?(?={_N} )(?:{_STATS}) in (\d+\.\d+)(?:s| seconds)\b")`, used with `.match` on the stripped line. [scripts/check_pipeline.py L496, L1437]
3. The existing heading rules check heading text only, never the summary lines under a heading. 091 (`ROUND_HEADING_FROM = 92`) flags a stray `Test output`/`Tests re-run` heading. 098 (`ROUND_BUILD_FROM = 99`) flags `#{1,6} round \d+ build`. A wrapper like `## Round 2 (2026-11-21, I2)` matches neither, so a summary line under it is silently not read. [scripts/check_pipeline.py L445-454, L493-495, L1122-1153; work/103/request.md L7]
4. The current cutoffs are 92 and 99, and each has a `_rule_seen` (item 084) RULE NOT SEEN gate. A new rule needs its own `*_FROM` and the same gate. [scripts/check_pipeline.py L1131, L1146]
5. Known shape of the problem: 076/05 has `## Round 2 build` at L6 and `## Test output (pasted, not summarized)` at L147. Rows L6-84 belong to the unread Round 2 build section. [work/076/05-build-report.md, Grep `^#{1,6} `: L1, L6, L85, L86, L121, L147, L205, L208]
6. Earlier count: 345 summary-like lines in 78 05/06 files, with no inside/outside split. [work/098/01-research.md L59; work/098/03-handoff.md L43]
7. R1 approximate Grep over the target range work/076-098/0[56]-*.md (46 files, all present): 194 summary-like lines. 076/05 = 14, 076/06 = 18, 084/05 = 15, 084/06 = 18. Pattern: `^\s*(=+ )?[1-9]\d* (failed|passed|skipped|xfailed|xpassed|warnings?|errors?)\b.* in \d+\.\d+(s| seconds)\b`. Comments and fence marks are not removed, and lines are not split by section, so this is an upper-bound guide only. The real numbers come from the command below. [Grep tool count, this brief]
8. No item at 099 or later has a 05/06 yet (Glob `work/0[789]*/0[56]-*.md` stops at 098). So the measurement can only be retrospective. Whether a new cutoff would flag a correct run can be judged only from the shapes found in 076-098 (RI-001). [Glob, this brief]
9. Precedent: when 098 lacked a shell, it dropped this rule rather than guess (RI-001). [work/098/04-build-plan.md L75, L85]

## Numbers used (show the math)
- Files measured: 23 items (076-098) × 2 steps = 46 files. Glob lists all 46.
- Grep upper bound: 194 lines (tool total, "Found 194 total occurrences across 46 files").
- No in/out split by hand. That split is the measurement.

### Measurement for the orchestrator (read-only; writes nothing, no git)
Run from the repo root and paste the full output into 02/03:

```
cd /home/claude/cover-calls && python3 -I - <<'EOF'
import sys, re, collections
sys.path.insert(0, "scripts")
import check_pipeline as cp
from pathlib import Path
tot = collections.Counter(); heads = collections.Counter(); items_out = collections.Counter()
for n in range(76, 99):
    for step in ("05", "06"):
        p = Path("work") / f"{n:03d}" / cp.STEPS[step]
        if not p.exists():
            print(f"{n:03d}/{step}: absent"); continue
        text, why = cp._read(p)
        if why:
            print(f"{n:03d}/{step}: {why}"); continue
        rows, open_end = cp._md_lines(text)
        flags = cp._section_flags(rows, cp.RUN_HEADING[step])
        h12 = hany = "(none)"; ins = outs = 0
        for (line, state), inside in zip(rows, flags):
            if state == "out" and re.match(r"#{1,2} ", line): h12 = line.strip()
            if state == "out" and re.match(r"#{1,6} ", line): hany = line.strip()
            if state in ("out", "in") and cp.SUMMARY_LINE.match(line.strip()):
                if inside: ins += 1
                else:
                    outs += 1; heads[h12] += 1
                    print(f"  OUT {n:03d}/{step} | {state} | section={h12[:60]} | nearest={hany[:60]} | {line.strip()[:90]}")
        tot["in", step] += ins; tot["out", step] += outs; items_out[f"{n:03d}"] += outs
        print(f"{n:03d}/{step}: inside={ins} outside={outs} open_fence_at_end={open_end}")
print("TOTAL", dict(tot))
print("ITEMS WITH >=1 OUTSIDE:", sorted(k for k, v in items_out.items() if v))
print("OUTSIDE BY SECTION HEADING:")
for h, c in heads.most_common(): print(f"  {c:4d}  {h[:80]}")
EOF
```

It uses only `cp.STEPS`, `cp._read`, `cp._md_lines`, `cp._section_flags`, `cp.RUN_HEADING` and `cp.SUMMARY_LINE`, the same objects `_run_seconds` uses (L1428-1440). The module imports only the standard library (L410-416), and `main()` runs only under `__name__ == "__main__"` (L2387), so importing it changes nothing.

Counts to report:
(a) TOTAL inside/outside for 05 and for 06.
(b) Per file inside=/outside=.
(c) Items with at least 1 outside line.
(d) Outside lines grouped by their `#`/`##` section heading.
(e) For each OUT line: whether it is a real run of that item that LOG BATCH should have timed (an unread round wrapper such as `## Round 2 build`, `# Round 1 report`) or a correctly quoted line (a Deviations note, a mutant result, an Evidence quote, 06's re-run of another round already timed). R2/R3 make this call by hand from the printed section/nearest heading, and it is not part of the script. Note that row text is printed and file line numbers are not, because `_md_lines` drops comments before splitting (L659).

## Fit for a ~$3k account
No account effect. This is a pipeline-check rule only. It changes no trading code, cap, quote or order path.

## Open questions
1. Decision rule for R2/R3 (request L11): build only if (e) finds no correctly quoted line that the rule would flag at or above the cutoff. If (e) finds any quoted outside line in Deviations/Mutations/Evidence sections, the broad rule would flag correct files, so it is a no-go. A narrower option is to allow-list heading shapes (e.g. any `#{1,6} round \d+\b` heading), which 02 of 098 counted at 39 headings in 25 files [work/098/02-improvements.md L51]. That option needs its own measurement from the same output's nearest= column. UNVERIFIED until run.
2. If a rule is built, which cutoff? It must sit above every item open when it merges (099-104 are in flight today), with a `_rule_seen` gate like 092/099. R3 decides.
3. 02/03 can't proceed on numbers until the orchestrator pastes the output. Without it the outcome is BLOCKED (RI-001).
4. R1 log line: I had no shell, so the orchestrator must run `python3 scripts/check_handoff.py 103` for the sources count and then `python3 scripts/check_pipeline.py --log R1 103 "brief written | <count>"`.
