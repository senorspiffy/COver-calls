# 02 Improvements - 092
## What past logs say
- This is the follow-up named three times before:
  - work/089/02 AGAINST 3 and hole 9 (L76-78, L107): "scripts/check_handoff.py L55 and L62 read 01/03 strictly ... Widen the census or open a follow-up item today."
  - logs/audit/2026-11-22-089.md 07 point 9 (L93-96) confirmed both lines still strict, and N1 (L103-105) proposed this item with the guardrail the request copies.
  - scripts/check_pipeline.py docstring L360: "Known gap: scripts/check_handoff.py still reads its files strictly." It has to change in the same build (01 F23).
- 089's accepted design (audit L20-23, L38) is the template:
  - `_read` uses read_bytes, a strict decode, and catches `(OSError, UnicodeDecodeError)` with `missing_ok`;
  - `test_read_census` pins `{("_read","read_bytes"):1, ("write_log","open"):1}`;
  - each mutation fails a named test (M3, M5, M7, M10, M13, M14).
- 089 lesson on exit codes (audit L53-54): the unfixed crash already exits 1. So "exit 1" alone proves nothing (01 F12). Each fixture needs no-Traceback, the named line, and a clean twin.
- RI-014 (logs/recurring-issues.md L152-158) is the family and RI-002 is the shape to avoid (01 F14). The request says near miss, not counted.
- Process state: logs/audit/2026-11-24.md L28 lists 092 as STUCK (opened 2026-11-22). R1 for 092 is logged (logs/research/2026-11-24.md L5, `brief written | 7`). The orchestrator runs check_handoff right after R1 for every item (.claude/agents/r1-researcher.md L19), so a regression here affects every item's first step.
- A test detail that matters for the fix (tests/test_pipeline_check.py L2602-2614): `test_check_handoff_open_branches_states` patches `open_branches` on the `check_pipeline` module object (`monkeypatch.setattr(cp, "open_branches", ...)`). This works only because check_handoff runs `from check_pipeline import open_branches` inside `_branch_with_handoff` (L95), at call time. See AGAINST 1.
- Languages precedent: every BUG/EFFICIENCY item inside these checkers logged `languages: N/A`, 089 included (logs/research/2026-11-21.md L10; work/089/02 L86-87).

## 3 ways FOR
1. **Re-use the 089 reader through the module (`import check_pipeline as cp` and `cp._read(path, missing_ok=True)`). Do not use `from check_pipeline import _read, open_branches`.**
   - The request wants "one reader returning (text, why)". `cp._read` already has the agreed contract: strict UTF-8, newline rule, `(OSError, UnicodeDecodeError)`, and a detail with no content (01 F19; check_pipeline.py L526-542). A second reader would be the "each script decodes on its own" root cause again.
   - `missing_ok=True` also replaces the `exists()` + read pairs at L54-55 and L58-62:
     - `(None, None)` means "no file". That keeps today's `no ...; nothing else to check` path.
     - `(None, why)` means unreadable. That covers a directory named 03-handoff.md (01 F2), which passes `exists()` today.
   - Calling through the module attribute keeps the monkeypatch in L2609/L2612 working, because the name is looked up at call time. A module-level `from ... import open_branches` would bind the real function once, and the h2 test would then call real git (reasoning chain from L2605-2612 and L95). Put the `sys.path.insert` and the import at module top, or at the start of `main`, so both reads and `_branch_with_handoff` use the same `cp`.
   - Take `why` from the return value and never from `cp._UNREAD`, which only check_pipeline's main clears (01 F21). Detail text: use `cp._UNREAD[shown]` only for the bracket detail just written, or have `_read` return it. Either way, pin the exact line in a test.
2. **Make every path fail closed, in the forms check_all and the R1 log can already handle.**
   - 03 unreadable: `problems.append(f"{why} ({detail})")`, then the normal `FAIL: ...` print, `n problem(s)` and `return 1`. Because it goes through `problems`, `--all` picks it up through the existing `l.startswith("FAIL: ")` filter (L126), with no change to check_all (kills 01 M-d by construction).
   - 01 unreadable: print `sources count (unique URLs in 01-research.md): not computed (<why>)` and also add it to `problems`. The "no 03 yet" branch must then return `1 if problems else 0`, not `0` (01 F13, kills M-c). Print the FAIL line before that return too.
   - The non-number fails closed downstream. The R1 log format is `brief written \| \d+` checked with `re.fullmatch` (scripts/check_pipeline.py L480, L732). An orchestrator that copies "not computed ..." into `--log R1` is refused, so no false `0` can reach the log (RI-002). Pin this with one unit assert: `cp.LOG_FORMAT["R1"]` must not fullmatch `brief written | not computed (...)`.
   - LEGACY (01 open question 1): put the unreadable check in check_all before the LEGACY branch. If any problem line contains ` unreadable (`, the item is FAIL even in 002-008. LEGACY's own reason text (L21) is "before the Totals/Self-check template", which does not cover a file that can't be read. Reasoning chain: L129-130 would otherwise turn an unread 03 into exit 0 (01 F16).
3. **Guardrail tests that copy 089's teeth, adapted to this script.**
   - Census twin of `test_read_census` over scripts/check_handoff.py. Use the same `ast.Attribute` walker for `read_text`/`read_bytes`/`open` plus a builtin `open` Name, and expect `{}` (total 0). Calls of the form `cp._read(...)` must not count as raw reads: their attr is `_read`, so they are not in the set. Computed by AST, never typed by hand (RI-006; 01 F25). Restoring L55 or L62 (M-a, M-b) then fails it.
   - Use a 3-tuple subprocess helper. `_run` returns only `(code, stdout)` (L63-66), and 089 added `_run3` for this reason (audit L11). Re-use `_run3` with `cwd=tmp_path`. `main` uses the cwd-relative `Path("work")` (01 F18), so in-process `check_all(tmp_path/"work")` does not isolate `main`'s reads.
   - Fixtures (a)-(d) from 01 F26, each with a clean twin that exits 0/PASS and differs only in the bad byte (`b"\xff"`, never valid UTF-8, 01 F4). Plus (e): bad 03 in a LEGACY ID (`003`) gives `003: FAIL: ... unreadable` and exit 1.
   - Each fixture asserts: `Traceback` not in stderr, the exact named line on stdout, and exit 1.
   - Mutations each must fail a named test (I2 to run them, UNVERIFIED until run):
     - M-a/M-b, a strict read restored → census + (a)/(b);
     - M-c, no-03 `return 0` → (a);
     - M-d, the unreadable line printed without `FAIL: ` → (c);
     - M-e, catch only `OSError` inside the reader → census unchanged, so only (a) kills it. Note it is a check_pipeline mutation, which 089's tests already cover;
     - M-f, LEGACY branch before the unreadable check → (e).

## 3 ways AGAINST
1. **It couples check_handoff to check_pipeline on every single-item run.**
   - Today a single-item run (`check_handoff.py <ID>`, after R1, R3 and I3) imports nothing from check_pipeline. Only `--all` does, lazily (L94-95).
   - After 092, any import-time failure in check_pipeline.py takes down check_handoff for every item. On a shared checkout where other items' builders edit check_pipeline.py at the same time (this branch carries PRs #31-#36 and seven STUCK items, logs/audit/2026-11-24.md L28), a half-written check_pipeline.py would mean no sources count for any R1. A local 10-line reader would avoid that coupling, but it breaks the request's "one reader" and brings back the root cause.
   - Mitigations:
     - import inside `main` (so `--help`/usage still works);
     - say in 04 that check_handoff depends on check_pipeline importing cleanly;
     - keep the `cp.` attribute calls (FOR 1), or the h2 test silently starts calling real git.
   - Cost of being wrong: the h2 test (L2602-2614) either fails, or passes while it shells out to git in tmp_path. Both are reasoning-chain risks, UNVERIFIED by a run.
2. **It changes what the orchestrator sees right after R1, and the runbook may not say what to do.**
   - Today the after-R1 call always exits 0 when there is no 03 (L59-61). After 092 an unreadable 01 gives exit 1 and a non-number. `--log R1` then refuses the line (L480, L732), so the item cannot get its R1 log line and shows as INCOMPLETE/STUCK.
   - That is the correct fail-closed result. But .claude/commands/run-item.md L17 and r1-researcher.md L19 describe only the number case. If nobody writes what to do (re-run R1 or fix the file), the item sits like 092-098 did (audit 2026-11-24 L28).
   - A runbook line is a `.claude/` rule-path change (RULE_PATHS L463) and needs the person's OK. Leaving it out is acceptable only if 04/05 record it as a known gap. How the orchestrator parses the sources line is UNVERIFIED (01 open question 5).
   - The LEGACY change (FOR 2) also changes `--all` verdict semantics for 002-008. It is safe today only if those 03 files are readable. A1's daily `--all` ran "no new failures" on main ae2f8c7 (audit 2026-11-24 L31), which suggests they are, but that run was before any change and does not test unreadability.
3. **The scope is narrow by design, so "never crashes" stays partly unproven, and the test cost grows.**
   - 01 F17: `--all` never reads 01. A bad 01 in an item without 03 is silent there, so the daily `--all` does not see it. Only the single-item run catches it.
   - 01 F22: `open_branches()` reads request.md through `_read` and drops `why` in check_handoff's use. No crash, but there is a silent not-checked.
   - `work.iterdir()` and the `is_dir()` calls (L114) can still raise OSError on a permission-denied work/. That is outside the request and not a file decode, but the docstring must not claim "never crashes" in general. State the claim exactly: no traceback on an unreadable 01 or 03.
   - Cost:
     - 5-6 new subprocess fixtures plus clean twins (about 10 runs of a short script) in a suite that 089's audit timed at about 82 s (audit L41);
     - one rule-path docstring edit in check_pipeline.py (L360) plus check_handoff's own docstring (L2-12, which should name the unreadable line and the LEGACY exception).
   - Both scripts are RULE_PATHS (L463), so the person approves at PR review (01 F24).

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 092 is a BUG fix inside this repo's own checker: how check_handoff.py reads work/ files, its output lines, exit code and tests. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts (Python pathlib/codecs/exceptions behaviour, RFC 3629) were sourced by R1 (01 F1-F9) from official English docs, the same as the 089 precedent (work/089/02 L87).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no new external claims; R1's F1-F9 cover the Python facts used) | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |

## Holes to watch out for (summary)
1. **Import binding.** Use `import check_pipeline as cp` and `cp._read`/`cp.open_branches`, never `from check_pipeline import ...` at module level, or the h2 monkeypatch (tests L2609, L2612) stops reaching check_handoff.
2. **No-03 return.** An unreadable 01 must make the `nothing else to check` path exit 1 (01 F13). This is the most likely half-fix, and only fixture (a) catches it.
3. **No number from nothing.** Never call `unique_urls` on "" or None. Print `not computed (<why>)` (01 F14). `--log R1` already refuses non-digits (L480, L732); pin it.
4. **`FAIL: ` prefix.** Unreadable problems go through `problems`, so check_all L126 sees them (01 F15).
5. **LEGACY masking.** Check for unreadable before the LEGACY branch (01 F16). Add fixture (e).
6. **Exit 1 is not proof.** The crash also exits 1. Assert no `Traceback` in stderr with `_run3`, the exact line, and a clean twin (089 audit L53-54).
7. **cwd.** `main` uses `Path("work")` relative to cwd (01 F18). Run fixtures by subprocess with `cwd=tmp_path`.
8. **`_UNREAD` side effect.** It grows across `--all` items and is never printed by check_handoff. Take `why` from the return value (01 F21).
9. **Docstrings.** Delete "Known gap" at check_pipeline.py L360, or reword it to the remaining gaps (F17, F22). Update check_handoff's docstring L2-12 with the unreadable line and the LEGACY rule.
10. **Runbook gap.** State in 04/05 what the orchestrator does when the R1 sources count is "not computed". A `.claude/` edit needs the person's OK (RULE_PATHS).
11. **Census scope.** Expect total 0 raw reads in check_handoff.py. `cp._read` has attr `_read` and is not counted. Re-count by AST after the edit, never by hand (RI-006).

Log fields: 3 for / 3 against | languages: N/A
