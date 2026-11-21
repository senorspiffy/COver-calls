# 04 Build plan - 089
Fit verdict: FIT WITH CHANGES

Method: I1 has no shell (item 072). I read the rules file .claude/agents/i1-reviewer.md, templates/build-plan.md, work/089/request.md, 03-handoff.md (READY, 70 rows), logs/recurring-issues.md, work/088/04-build-plan.md, work/090 and work/091 request.md, scripts/check_pipeline.py, scripts/probe_guardrails.py, scripts/check_handoff.py and tests/test_pipeline_check.py (Read/Grep, 2026-11-21). Nothing was run.

**Build order.** 088's edits are already in this working tree:
- `_anchor_env` returns `(env, failed)`;
- `or env_failed` is in the exit expression;
- GIT_CENSUS has `("_anchor_env","_git"): 2` and no `("_rule_seen","_git")`;
- GIT_LINES ends with `"RULE NOT SEEN:"`.

So the line numbers below are post-088, but they are taken before 088's commit. **I2 re-reads every line by its text after 088 is committed**, then builds 089. 090 and 091 build on 089.

Fit:
- Process-only. No ccbot/, config/, data/ or broker path, so the ~$3k account and the 001 strategy rules are untouched. No rule the person follows (slack, tolerance, cap) changes.
- scripts/check_pipeline.py is in RULE_PATHS, so the person's OK is needed at PR review.
- No conflict with 088. Its `_anchor_env` keeps calling `_shallow_boundaries`, and 089 only makes that call return "unreadable" in more cases.

Changes to 03 (why "WITH CHANGES"):
1. **Test (c) UNTRACKED CHANGE text is wrong in 03 step 5.** The test passes `--untracked-from c`, so the line ends with `_note(c)`. The real expected line is `UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow) (cutoff <c7> from --untracked-from)`. test_malformed_shallow_line_real_git_not_checked (tests L1649-1650) pins the same form. The RULE NOT SEEN line has no note.
2. **ORPHAN LOG wording.** 03 step 3 (iii) would print `ORPHAN LOG: none; not checked: <whys>`. That starts with "none", the RI-002 shape. Every other line uses `not checked (...)`. So:
   - no orphans with whys → `ORPHAN LOG: not checked (<whys>; item 089)`;
   - orphans with whys → `ORPHAN LOG: <orphans>; not checked: <whys> (item 089)`;
   - no whys → today's text.
   Fixtures 6a and 6k pin both forms.
3. **Probe anchors must survive verbatim.** probe_guardrails.py anchors two lines that 089 edits next to. `tests/test_probe_guardrails.py` (C12, L250-258) asserts each anchor occurs exactly once:
   - `"                clashes.append(item)"` (open_branches);
   - `"            elif suites[0] != field:"` (incomplete).
   The plan keeps both lines byte-identical (see the code below).
4. **The ID CLASH compare stays strict, with no new branch.** `mine_text, _ = _read(mine)` gives None when mine is unreadable, and `theirs != None` is True. So an unreadable request.md that could clash is listed, not dropped, and ID CLASH never reads `none` for a compare that wasn't made. The anchor line stays. 03 (vii) said "no clash compare", which would hide it (RI-002). Pinned by T-ob and M13.
5. **Missing-input tests 03 left without a fixture** (i1 step 1a). 03's Missing inputs table lists these, but steps 6a-6j test none of them. They are added:
   - real_data_field (T-rd), research_code (T-rc), open_branches (T-ob);
   - inbox_section (T-is), _inbox_gate template (T-ig);
   - _sent_back (T-sb2), _shallow_boundaries unit cases (T-sh);
   - 07 (6l) and 05 at the Suite check (6m);
   - a below-CHECKLIST_FROM item in 6e.
6. **`real_data_field` with an unreadable request.md** keeps checking 05/06. The scope is unknown, so it is treated as built (strict), and the gap is `request.md not checked (<why>; item 089)`. 03 said only "adds gap".
7. **Path rendering.** The `why` text and the `_UNREAD` key both use one helper, `_shown(path)` = `path.as_posix().encode("utf-8", "backslashreplace").decode("utf-8")`. The `why` is printed in INCOMPLETE, LOG BATCH and INBOX, so it needs the safe form too, not only the UNREADABLE line. For a UTF-8 name the result is the same string, so N13 L3165 (`endswith(f"{bad.as_posix()} unreadable")`) holds.

## Extra research (with sources)
- **The newline normalisation is CPython's own rule for subprocess text mode.** `Lib/subprocess.py`, `_translate_newlines` (https://raw.githubusercontent.com/python/cpython/main/Lib/subprocess.py, fetched 2026-11-21):
  ```
  data = data.decode(encoding, errors)
  return data.replace("\r\n", "\n").replace("\r", "\n")
  ```
  POSIX `_communicate` calls it on stdout/stderr when `self.text_mode`. `_git` runs with `text=True`, so `theirs` in open_branches is already normalised this way.
  - **Edge case R3 missed:** without the normalisation in `_read`, a CRLF request.md present on both sides would compare `\r\n` (mine) with `\n` (theirs) and give a false ID CLASH. Step 1's two `.replace` calls keep today's read_text equality (03 row 68). Fixture 6h and test_read_contract pin it (M11).
- **backslashreplace on encode** (https://docs.python.org/3/library/codecs.html, fetched 2026-11-21): "On encoding, use hexadecimal form of Unicode code point with formats `\xhh` `\uxxxx` `\Uxxxxxxxx`." So a surrogate-escaped file name (U+DC80-U+DCFF, the 'surrogateescape' row on the same page) prints as `\udcff`, never a UnicodeEncodeError. This confirms 03 row 70 for `_shown`.
- **BOM, checked against the same docs:** `read_text(encoding="utf-8")` and `bytes.decode("utf-8")` both keep a leading U+FEFF (only "utf-8-sig" strips it). So `_read` changes nothing for a BOM file.
- **PermissionError is not testable here.** The tests run as root, and root ignores mode bits, so a chmod-000 fixture would read fine. IsADirectoryError (6b, T-sh) covers the "OSError class name" path instead. PermissionError is pinned only by the shared `except (OSError, UnicodeDecodeError)` and the census.
- **Repo code finding:** `_cp()` (tests L1186-1189) imports one shared module, so `_UNREAD` persists across tests.
  - Unit tests that read `_UNREAD` directly must start with `monkeypatch.setattr(cp, "_UNREAD", {})`.
  - `main` must use `_UNREAD.clear()`, never rebind the name (M4 relies on this).

Line table (re-read 2026-11-21, post-088 working tree; I2 re-finds each by text after 088's commit):

| Name | scripts/check_pipeline.py |
|---|---|
| `read_request` | L417-418 |
| `i3_verdict` | L473-493 (read L477) |
| `classify` | L528-569 (reads L530, L532, L552 via i3_verdict, L556, L563) |
| `_log_text` | L593-597 |
| `uncommitted_steps` | L605-625 (L615) |
| `_last_log_line` | L680-690 (L686) |
| `incomplete` | L700-783 (L711, L713, L742, L757, L776; probe anchor L748) |
| `_sent_back` | L786-809 (L795, L806) |
| `write_log` open | L838 |
| `orphan_log_lines` | L844-851 (L849) |
| `_item_lines` / `_run_seconds` | L902 / L927 |
| `open_branches` clash compare | L1135-1139 (probe anchor L1139) |
| `_shallow_boundaries` | L1196-1215 (L1209) |
| `research_code.request_text_of` | L1317-1319 |
| `real_data_field` | L1406 (read_request), L1415 |
| `_inbox_gate` / `inbox_section` | L1491 / L1508 |
| `main` | L1520; ORPHAN LOG L1648-1649; inbox L1650-1654; exit L1656-1658 |

| Name | tests/test_pipeline_check.py |
|---|---|
| `_run` | L62-65 |
| shallow unit tests | L1607-1663 |
| GIT_LINES / GIT_CENSUS / census total | L2365 / L2370 / L2432 (47) |
| test (a) / (c) | L2435 / L2476 |
| N11 / N13 | L3117 / L3154 |

Read-site count: Grep on 2026-11-21 (post-088) finds 21 `read_text(` lines (L418 … L1508) and one `.open(` (L838) = 22. This is the same as 03 row 17, because 088 added no read.

## Files to create/change
2 files planned (plus I2's own work/089/05).

**scripts/check_pipeline.py**
1. New module dict `_UNREAD = {}` (rendered path → detail). It holds reasons only, never file text.
2. New `_shown(path)`, as in change 7.
3. New `_read(path, missing_ok=False) -> (text, why)`, as in 03 step 1:
   - reads `path.read_bytes().decode("utf-8")`, then `.replace("\r\n", "\n").replace("\r", "\n")`;
   - `except (OSError, UnicodeDecodeError) as err`;
   - with missing_ok and FileNotFoundError → (None, None), nothing recorded;
   - any other failure → `_UNREAD[_shown(path)] = f"not UTF-8 at byte {err.start}"` if UnicodeDecodeError, else `type(err).__name__`, and the result is `(None, f"{_shown(path)} unreadable")`;
   - docstring: the contract and the subprocess `_translate_newlines` precedent.
4. `read_request(path)` is deleted (callers: classify, real_data_field; no test or other script uses it, Grep). Both callers do `_read` + `parse_request`.
5. New `_i3_verdict_text(text)`: today's body of `i3_verdict` from `rows, _ = _md_lines(...)` on. `i3_verdict(path)` stays as a wrapper: `text, why = _read(path)`, then `(None, None)` if why, else `_i3_verdict_text(text)`. Tests L2216, L2317, L2323 still call it.
6. `classify`:
   - one `_read(item_dir / "request.md")`; on why → `("UNREADABLE", why)`;
   - `parse_request(text)`, and the FAST check uses the same text (L530 and L532 become one read);
   - 06: `_read` → on why → `("UNREADABLE", why)`, else `_i3_verdict_text`;
   - 07 (both sites): `if audit.exists()` stays; `_read` → on why → `("UNREADABLE", why)`.
7. `_log_text(logs)` returns `(text, whys)`. Same globs. An unreadable file is left out of the text and its why is appended.
8. `uncommitted_steps`: when whys → `(f"not checked ({'; '.join(whys)}; item 089)", False)`.
9. `incomplete`:
   - **06:** read once: `ver_text, ver_why = _read(ver) if ver.exists() else (None, None)`. If ver_why, one entry `06 not checked (<why>; item 089)` replaces the RI-line check, the verdict-line checks and the I3 comparison. Otherwise use `ver_text` for the RI-line regex and `_i3_verdict_text(ver_text)`.
   - **Logs:** `text, log_whys = _log_text(logs)`. If log_whys and the item has any step file 01-06, one entry `log lines not checked (<whys joined by "; ">; item 089)` replaces:
     - the unlogged check;
     - the format check (the TESTS gate);
     - the whole Suite block;
     - the I3-line comparison.
     The 06 checks above, which need no log, still run. Feasibility: `????-??-??.md` ⊆ `*.md`, so every file `_last_log_line` and the I3 loop read is already covered by `_log_text`'s whys.
   - **Suite block**, written so the probe anchor stays byte-identical:
     ```
             body, why05 = _read(report)
             suites = _suite_lines(body) if why05 is None else []
             fired = None
             if why05:
                 missing.append(f"05 not checked ({why05}; item 089)")
             elif not suites:
             ...
             elif suites[0] != field:
     ```
   - `_last_log_line` and the I3 loop read through `_read` and skip a file that fails. Only reachable when log_whys is empty, so a skip there can only come from a race. Census only.
10. `_sent_back`: both try/excepts become `_read`, with the same result (skip / []).
11. `orphan_log_lines()` returns `(orphans, whys)`. The main print follows change 2.
12. `_item_lines`, `_run_seconds`: the try/except becomes `_read`. They keep returning `<file> unreadable` as today (N11/N13 unedited).
13. `open_branches` L1136-1139: `mine_text, _ = _read(mine) if mine.exists() else (None, None)`. The condition's last term becomes `theirs != mine_text`. The line `                clashes.append(item)` stays.
14. `_shallow_boundaries`:
    - `--git-common-dir` failure → `"unreadable" if sure else "full"` (unchanged);
    - `text, why = _read(Path.cwd() / d[0].strip() / "shallow", missing_ok=True)`;
    - why → "unreadable" whatever `sure` is;
    - text None (missing) → `"unreadable" if sure else "full"`;
    - the SHALLOW_LINE rule is unchanged;
    - docstring updated (item 089);
    - GIT_CENSUS is unchanged: no git call is added or removed.
15. `research_code.request_text_of`:
    - `_read` when `req.is_file()`;
    - on why it records `unread[item] = why` (a dict local to research_code) and returns None, so `_research_code` stays strict and the item is not counted as built;
    - after the loop, each flagged item in `unread` gets the detail `RESEARCH ONLY check: <why> (item 089)` in place of the "no request.md" text.
    - `_research_code`'s contract and open_branches' `requests.get` are unchanged.
16. `real_data_field`:
    - request unreadable → gap `request.md not checked (<why>; item 089)`, and 05/06 are still checked (change 6);
    - 05/06 unreadable → gap `<step> not checked (<why>; item 089)`.
17. `_inbox_gate` working template unreadable → `(f"not checked ({path.name} not committed; its {INBOX_TEMPLATE} unreadable)", False)`.
18. `inbox_section` newest unreadable → `(f"not checked ({newest.name} unreadable)", False)`.
19. `main`:
    - `_UNREAD.clear()` is its first statement;
    - ORPHAN LOG print follows change 2;
    - after `inbox, inbox_bad = inbox_section()` and before the INBOX print: `print(f"UNREADABLE: {', '.join(f'{p} ({d})' for p, d in sorted(_UNREAD.items())) or 'none'}")` and `unreadable = bool(_UNREAD)`;
    - add `or unreadable` to the final return expression only (the inbox early return is already an unconditional 1; 03 rows 53, 58).
20. Module docstring gains an UNREADABLE (item 089) paragraph, written from the code: the one reader; the detail forms; each consumer's not-checked text; the `_shallow_boundaries` sure-False change; exit 1.

**tests/test_pipeline_check.py**: `_run3`, the tests below, and test (c)'s new asserts. `_run`, GIT_CENSUS and GIT_LINES are unchanged.

Not changed:
- scripts/check_handoff.py L55/L62 (follow-up, below);
- the agent and template text (a1-auditor.md L20 names ORPHAN LOG only; exit 1 already surfaces UNREADABLE);
- globs (Q3);
- LOG BATCH's exit rule;
- `_git`.

## Tests and checks
Helper: `_run3(root, *args) -> (code, stdout, stderr)` runs check_pipeline.py with `capture_output=True` (bytes); stdout is decoded with "replace". Every fixture below asserts `b"Traceback" not in stderr`.

Common bad bytes:
- `LOG = logs/implementation/2026-11-19.md`;
- `BAD = b"\xff\xfe"`.

| Test | Setup | Expected |
|---|---|---|
| `test_read_contract` | `monkeypatch.setattr(cp, "_UNREAD", {})`, tmp files | valid → (text, None); BAD → (None, f"{p.as_posix()} unreadable") with `_UNREAD == {p: "not UTF-8 at byte 0"}`; a directory → detail `IsADirectoryError`; missing + missing_ok → (None, None), `_UNREAD` unchanged; missing, no missing_ok → detail `FileNotFoundError`; `b"a\rb\r\nc"` → "a\nb\nc" |
| `test_read_census` | AST walk as 03 step 7 (ast.Attribute attr in {read_text, read_bytes, open}, or ast.Name `open`; innermost FunctionDef) | `{("_read","read_bytes"): 1, ("write_log","open"): 1}`, both with a reason, total 2 |
| 6a `test_unreadable_log_exits_1_alone` (no git) | work/150/request.md (FULL, Date 2026-11-21) + LOG; `--today 2026-11-21` | clean twin (`# Implementation log\n`): exit 0, `UNREADABLE: none`, `ORPHAN LOG: none`. BAD twin: exit 1, `UNREADABLE: logs/implementation/2026-11-19.md (not UTF-8 at byte 0)`, `ORPHAN LOG: not checked (logs/implementation/2026-11-19.md unreadable; item 089)` |
| 6b | 6a tree with LOG as a directory | `UNREADABLE: logs/implementation/2026-11-19.md (IsADirectoryError)`, exit 1 |
| 6c | 6a tree + work/150/06 = `b"# 06\n\xff"` | `UNREADABLE: work/150/06-verification.md (not UTF-8 at byte 5)`; INCOMPLETE holds `06 not checked (work/150/06-verification.md unreadable; item 089)`; exit 1 (not exit-isolated: SKIPPED also fires) |
| 6d | request.md = `b"Scope: FULL\n\xff"` | `150: UNREADABLE (work/150/request.md unreadable)`, `UNREADABLE: work/150/request.md (not UTF-8 at byte 12)`, exit 1 (isolated, 03 Self-check) |
| 6e (NO_GIT) | repo with a commit; item 150 with 01 uncommitted; item 040 with 01-03; LOG BAD | `UNCOMMITTED STEP: not checked (logs/implementation/2026-11-19.md unreadable; item 089)`; INCOMPLETE has `150 (log lines not checked (logs/implementation/2026-11-19.md unreadable; item 089))` and no `no log line for`; no INCOMPLETE entry for 040 (CHECKLIST_FROM = 41) |
| 6f | N13's tree (two 999-shaped items + LOG BAD) via `_run3` | no Traceback, exit 1, UNREADABLE line names LOG, LOG BATCH not computable for both |
| 6h | `_item(tmp, "150", ALL)`, then 07 = `b"# 07\rA1 result: PASS\r"` | line `150: complete (FULL)` |
| 6i | 6a BAD tree, in-process `cp.main` twice (chdir, capsys); LOG fixed between the two runs | 1 then 0; the second output has `UNREADABLE: none` |
| 6j | 6a BAD tree; `cp.inbox_section` patched to `("x", True)` | output has the UNREADABLE line naming LOG; returns 1 |
| 6k | 6a BAD tree + a good logs/implementation/2026-11-18.md with `12:00 \| I2 \| 777 \| ...` (no work/777) | `ORPHAN LOG: 777 (logs/implementation/2026-11-18.md); not checked: logs/implementation/2026-11-19.md unreadable (item 089)` |
| 6l | `_item(tmp, "150", ALL)`, 07 BAD | `150: UNREADABLE (work/150/07-audit-task.md unreadable)`, UNREADABLE names it |
| 6m | `_item(tmp, "150", ALL)`, 05 BAD | INCOMPLETE holds `05 not checked (work/150/05-build-report.md unreadable; item 089)`; LOG BATCH not computable names 05 |
| T-sh (NO_GIT, unit) | `_history`; flag patched `("",129)` (sure False); `.git/shallow` = b"\xff"; then a directory named shallow; then `--git-common-dir` patched `("",128)` | "unreadable" with `_UNREAD` detail `not UTF-8 at byte 0`; "unreadable" with `IsADirectoryError`; "full" with `_UNREAD` empty; flag `("true\n",0)` + common-dir failure → "unreadable", `_UNREAD` empty |
| test (c) (edit) | unchanged setup | add: `UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow) (cutoff {c[:7]} from --untracked-from)`; a line starting `UNREADABLE: ` containing `shallow (not UTF-8 at byte 41)`; `RULE NOT SEEN: not checked (shallow clone; run git fetch --unshallow)` |
| T-rd (unit, no git) | chdir; `_git` → `("x", 0)`; `_item_triggers` → `({"150": ("abc1234", ["ccbot/realtest.py"])}, None)`; request.md BAD, 05 BAD; `real_data_field(c, walked=([], None, None))` | entries["150"] holds `request.md not checked (work/150/request.md unreadable; item 089)` and `05 not checked (work/150/05-build-report.md unreadable; item 089)`; "150" in names |
| T-rc (unit, no git) | `_git` → `("x",0)`; walked = `([("a"*40, ["work/150/01-research.md", "ccbot/x.py"])], None, None)`; request.md BAD | `research_code(c, walked)` == `("150", {"150": ("aaaaaaa", "RESEARCH ONLY check: work/150/request.md unreadable (item 089)")})` |
| T-ob (NO_GIT) | the clash test's setup (tests L293-298), then main's work/050/request.md overwritten with BAD (uncommitted) | `ID CLASH: 050 (origin/pr5)`, `050: UNREADABLE (work/050/request.md unreadable)`, UNREADABLE names it, exit 1 |
| T-is (unit) | `_inbox_gate` patched → None; logs/audit/2026-11-20.md BAD | `inbox_section(Path("logs/audit")) == ("not checked (2026-11-20.md unreadable)", False)` |
| T-ig (NO_GIT) | `_daily(tmp, "2026-11-18.md", INBOX_OK..., template=None, commit=False)`, templates/daily-audit.md BAD | `INBOX: not checked (2026-11-18.md not committed; its templates/daily-audit.md unreadable)`; UNREADABLE names the template |
| T-sb2 (unit) | chdir; work/150/request.md + 05; LOG BAD | `cp._sent_back("150") is False`, no exception |
| N13 (edit) | unchanged, plus the 6f `_run3` assert (the request's "N13 gains the `_run` assert") | as 6f |

Mutations (scratch copy only, `/tmp/claude-0/scratch/i2-089/`, never in the repo). I2 lists each one with its failing test in 05, and I3 re-runs them:

| ID | Mutation | Must fail |
|---|---|---|
| M1 | `_read` catches only OSError | 6a (Traceback) |
| M2 | `_read` catches only UnicodeDecodeError | 6b |
| M3 | `or unreadable` dropped | 6a (bad twin exits 0) |
| M4 | `_UNREAD.clear()` dropped | 6i |
| M5 | one site back to a raw read_text | test_read_census |
| M6 | UNREADABLE printed after the INBOX early return | 6j |
| M7 | `_shallow_boundaries` decode error → `"unreadable" if sure else "full"` | test (c), T-sh |
| M8 | shallow failure not recorded | test (c), T-sh |
| M9 | orphan_log_lines drops its whys | 6a, 6k |
| M10 | incomplete computes from "" | 6e |
| M11 | newline normalisation dropped | 6h, test_read_contract |
| M12 | `why` text changed | N13 L3165 |
| M13 | clash compare skipped when mine is unreadable | T-ob |
| M14 | classify 06 unreadable falls through as verdict None | 6c's classify line (and 6l for 07) |
| M15 | real_data_field skips an unreadable request | T-rd |
| M16 | research_code drops the unread detail | T-rc |

Done check:
- full suite green;
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` if present (RI-008);
- `tests/test_probe_guardrails.py` green (C12 anchors once);
- step 10: whole-output diff of `python3 scripts/check_pipeline.py` on the real repo, post-088 vs post-089, same args. Expected: exactly one added line, `UNREADABLE: none`, between ORPHAN LOG and INBOX (RI-013). Any real unreadable file shows as an entry instead, and I2 records it. UNVERIFIED until I2 runs it.

Follow-ups for 05 (03 step 9):
- scripts/check_handoff.py L55/L62 still read strictly (row 63); A1 to open an item today;
- 091 point 1's per-exit-term tests must include 089's `unreadable` term (already pinned by 6a/M3; 091 should not add a duplicate);
- 090: any new read it adds must go through `_read`, and the read census will fail otherwise.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Q1 hybrid: one UNREADABLE line + per-consumer not checked | Files 3, 19; consumers 6-18 |
| Q2 `_shallow_boundaries`: only missing / common-dir failure keeps "full" | Files 14; T-sh, test (c), M7/M8 |
| Q3 globs unchanged (44/44) | Files 7 (same globs); "Not changed" |
| Q4 templates/daily-audit.md uses the reader | Files 17; T-ig |
| Q5 check_handoff.py follow-up | Follow-ups |
| Q6 detail `not UTF-8 at byte N` / class name, no content | Files 3; test_read_contract, 6a-6d |
| Q7 F20 call order | 6e (UNCOMMITTED STEP not-checked form) |
| Step 1 `_read` | Files 2-3; test_read_contract |
| Step 2 route all 21 sites; read_request; `_i3_verdict_text`; `_log_text` tuple | Files 4-18; census; read_request deleted (no other caller) |
| Step 3 (i) uncommitted_steps | Files 8; 6e |
| Step 3 (ii) incomplete | Files 9; 6c, 6e, 6m |
| Step 3 (iii) orphan_log_lines | Files 11, change 2 (wording); 6a, 6k |
| Step 3 (iv) classify | Files 6; 6c, 6d, 6l |
| Step 3 (v) real_data_field | Files 16, change 6; T-rd |
| Step 3 (vi) research_code | Files 15; T-rc |
| Step 3 (vii) open_branches | Files 13, change 4 (strict clash); T-ob |
| Step 3 (viii) inbox_section | Files 18; T-is |
| Step 3 (ix) _inbox_gate | Files 17; T-ig |
| Step 4 main clear / line / exit term | Files 19; 6a, 6i, 6j |
| Step 5 shallow + test (c) asserts | Files 14; test (c) edit with the corrected UNTRACKED CHANGE text (change 1) |
| Step 6 fixtures 6a-6j | Tests table (6g is unused in 03; 6k-6m added) |
| Step 7 read census | test_read_census |
| Step 8 mutations M1-M12 | Mutations table, plus M13-M16 |
| Step 9 process note | Follow-ups |
| Step 10 whole-output diff | Done check |
| Row 24/53/58 fix: no inbox early-return term | Files 19 (final expression only); M6 |
| Row 52 fix: ≤ 51 INCOMPLETE entries | 6e pins 040 (< 41) gets none |
| Row 69 fix: lone `\r` risk | 6h, M11 |
| Row 70: surrogate file names | `_shown`, change 7 |
| Rule text the person follows (001) | None changed; no request needed |

## Guardrail tests
- Feasibility:
  - globs (44 of 44 files match both, 03 Q3) → unchanged code, existing log tests;
  - CHECKLIST_FROM bound (≤ 51 entries) → 6e (040 has no entry, 150 has one);
  - read census (22 today → 2) → test_read_census;
  - byte offsets 0/5/12/41 (03 Self-check) → 6a, 6c, 6d, test (c);
  - exit isolation → 6a/6d clean vs bad twins (M3).
- Missing inputs:
  - log file non-UTF-8 → 6a, 6f;
  - log path is a directory → 6b;
  - request.md → 6d, T-rd, T-rc, T-ob;
  - 05 → 6m, T-rd;
  - 06 → 6c;
  - 07 → 6l, 6h;
  - daily report → T-is;
  - template → T-ig;
  - shallow file (sure True and False, decode error and directory) → test (c), T-sh;
  - `--git-common-dir` failure → T-sh;
  - missing shallow file → existing L1607/L1619 tests, unedited;
  - `_sent_back` refusal side → T-sb2;
  - PermissionError → not fixturable as root (see research); covered by the shared except and the census.

## Expected result
- No input under logs/, work/, templates/daily-audit.md or the shallow file raises a traceback.
- Each unreadable file appears once on `UNREADABLE: <path> (<detail>)`, printed between ORPHAN LOG and INBOX, and the run exits 1.
- Each consumer says `not checked (... unreadable ...)` or lists the item strictly. Nothing computes from "" or prints a bare `none` for lost input.
- On the real repo the only output change is the added `UNREADABLE: none` line.
- Census total 2; GIT_CENSUS total 47 unchanged; probe anchors intact.
- M1-M16 each fail a named test.

Recurring issues checked:
- RI-001 (ESCALATED): every selector has a count with a pinning test (globs 44/44, ≤ 51 with the 040 case, census 22 → 2, offsets). Nothing is "always".
- RI-010 (ESCALATED): no log line typed here; the Log fields line is for the orchestrator. No step-order rule changes.
- RI-014 (OPEN): this item's family. The sure-False wrong reason is removed and pinned by test (c) (corrected text) and T-sh.
- RI-002 (GUARDED): ORPHAN LOG and ID CLASH are never a bare `none` for lost input (changes 2, 4). `real_data_field` and research_code stay strict.
- RI-012 (GUARDED): classified by exception class, never by message text.
- RI-013 (GUARDED): the whole-output diff is in the done check.
- RI-008 (GUARDED): py_compile with 3.11 is in the done check; no new syntax.
- RI-009 (GUARDED): build order (088 → 089 → 090/091) and the shared-file conflicts are stated.
- RI-004/RI-005: offsets re-derived (40 hex + "\n" = 41; "# 06\n" = 5; "Scope: FULL\n" = 12).
- RI-006: the file count (2) is counted from "Files to create/change".

Log fields: FIT WITH CHANGES | 2 files planned
