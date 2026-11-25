# 02 Improvements - 089
## What past logs say
- The bug has been reported 3 times and left out of scope twice:
  - logs/audit/2026-11-19-079.md L38 and L88: a non-UTF-8 shallow file was "caught as unreadable" only inside `_shallow_boundaries`. End to end it crashed earlier, in `_git`. 081 then fixed `_git`.
  - work/081/02 AGAINST 1 (L63) kept "F10 (strict `read_text` at L310, L369 and the others) out as a separate item". 081/02 AGAINST 2 (L68) said ORPHAN LOG's strict read of a log file "still tracebacks (F10). It is still a hole while F10 is open."
  - logs/audit/2026-11-21-086.md L53-57 reproduced the crash (`\xff\xfe bad` → `UnicodeDecodeError`, exit 1) and proposed this item.
  - So 089 is the F10 follow-up. It must not shrink again to the three functions the 086 audit names. R1's census shows 16 uncaught sites (01 F18).
- RI-014 (logs/recurring-issues.md L152-158) is the family named in the request. RI-002 (L24-37) is the shape to avoid: a lost file turned into "none". Neither gets a counted occurrence (request: "not counted").
- Precedents that fix the design space:
  - 079 `_shallow_boundaries`: "unreadable" means not checked, never skipped (docstring L1184-1187). A1's mutation X2 (`"unreadable" if sure else "full"` → `"full"`) was killed by `test_shallow_file_unreadable_not_checked` (079 audit L79). The sure-False branch was never pinned. That is why 081 audit F3 survived.
  - 086 `_item_lines`/`_run_seconds`: `<file> unreadable`, but only as a LOG BATCH "not computable" reason. That is **exit unchanged** (scripts/check_pipeline.py L956-961, L1628-1629, L1643-1645). So "086 already reports unreadable" (request L9) does not yet give exit 1.
  - 086 `_sent_back`: an unreadable file adds no send-back, on the refusal side (L776-777). This must stay.
  - 081 GIT_CENSUS (tests/test_pipeline_check.py L2369-2432): `(function, callee) → (count, reason)` plus a pinned total. Its walker matches only `ast.Name` callees (L2425).
  - 081/02 AGAINST 2 and holes (L66, L96): PEP 538 says stdout is strict outside the C locale, so never print undecoded content.
- Pinned text that the fix touches:
  - N13 (L3071) asserts `why.endswith(f"{bad.as_posix()} unreadable")`.
  - Test (c) (L2476-2487) asserts only no-Traceback, exit 1 and no `: none`.
- Same-day items in the same file:
  - 088: `_anchor_env` reads HEAD once.
  - 090: shallow handling in `late_log_lines`/`main_ahead`, rule C/D.
  - 091 pt 1: a patched test for each exit-code term, because A8/A9 survived.
  - All three edit scripts/check_pipeline.py next to the lines 089 edits (work/088, 090, 091 request.md).
- Languages precedent: 077-079, 081, 082, 084-086 were BUG/EFFICIENCY items inside this checker, and all logged `languages: N/A` (work/081/02 L15, L89; work/086/02 L54).

## 3 ways FOR
1. **One reader, `_read(path) -> (text, why)`, built on `read_bytes()` + `decode("utf-8")`, catching `(OSError, UnicodeDecodeError)`. Every why it returns goes into one `UNREADABLE:` line with its own exit term.**
   - Why both exceptions: `except OSError` misses the decode error, and `except UnicodeDecodeError` misses a directory named `2026-11-19.md` (01 F8). `_log_text` globs `*.md` (L591), so `IsADirectoryError` there is also a traceback today, by the same F8 reasoning. One `except` clause fixes both.
   - Why `read_bytes().decode()` rather than `read_text`: `err.object` is then the whole file's bytes. So `err.start` is the file byte offset by construction (01 F2, F9), and a reason like `not UTF-8 at byte 0` is exact. With `read_text`, the object is whatever chunk TextIOWrapper hands the decoder, which the docs do not specify (UNVERIFIED). The cost is a newline difference (hole 4).
   - `why` is built from `path.as_posix()`, the exception class name and `err.start`, never from file content (01 Q6; PEP 538 via 081/02 L66).
   - Answer to R1 open question 1: a hybrid of (a) and (b).
     - `main` prints one line, `UNREADABLE: <file> (<reason>); ...` or `UNREADABLE: none`, before INBOX, because INBOX can return early at L1639-1641 (01 F24). A new term `or unreadable` joins the exit expression at L1643 **and** the early-return path.
     - Each consumer whose answer depends on the lost text prints `not checked (<file> unreadable)` in its own line. It does not emit entries computed from "".
     - Reasoning chain: treating the file as "" gives a false `no log line for R1 R2 ...` for every item through `_logged` (01 F22). It also gives false UNCOMMITTED STEP entries (L617-619). Since `incomplete` runs once per item (L1566), one bad log file would turn into ~90 misleading INCOMPLETE entries. A per-item `log lines not checked (<file> unreadable)` entry repeats only the true reason. 086's LOG BATCH `not_computable` per item is the precedent.
   - Per-site safe side, which I1 should put in a table in 04:
     - `orphan_log_lines`: the file is named in UNREADABLE (it would otherwise be a silent pass, RI-002).
     - `classify` with an unreadable request.md: status `UNREADABLE (work/<ID>/request.md ...)`, which counts toward exit 1.
     - `open_branches` L1125 with an unreadable working-tree request.md: an UNREADABLE entry. A clash alone is not enough, because ID CLASH is not in the exit expression (L1643-1645).
     - `_sent_back`: unchanged (refusal side).
     - `_shallow_boundaries`: see FOR 3.
2. **Keep each caller's file set and its reason text, so 089 only removes crashes and changes no verdict (R1 open questions 3 and 4).**
   - Globs stay as they are: `*.md` for `_log_text`, `????-??-??.md` for the others (01 F21). Unifying them changes what `_logged` sees, which is a behaviour change with its own risk and its own item.
   - The reader's `why` keeps the exact 086 form `<posix path> unreadable`, so N13's `endswith` (L3071) and LOG BATCH's text stay byte-identical. The `(not UTF-8 at byte N)` / `(IsADirectoryError)` detail goes only on the UNREADABLE line. The alternative is to change N13 on purpose and record it in 05 as a whole-output diff line (RI-013, 01 F27).
   - Bring templates/daily-audit.md (L1478) under the same reader. It costs one call, and a census exception would need a reason anyway. An unreadable template then counts as `not checked (... unreadable)` plus UNREADABLE, not as a traceback.
   - `read_request` (L413) is called from `classify`, `real_data_field` (L1393) and the branch temp trees. The safest form is to have it take text and leave reading to its callers, so the census can see each read.
3. **Tests that kill each way the crash or the wrong reason could come back.** This builds on 01 F12, F16, F26, F29-F31.
   - **Read census.** An AST walk that matches `ast.Call` whose `func` is an `ast.Attribute` with `attr` in {`read_text`, `read_bytes`, `open`}, plus a builtin `open` `ast.Name` (01 F16). Expected: only `_read` reads, plus `write_log`'s append `open` (L825) with reason "write", and a pinned total. A new raw `read_text` fails it, in the 081 GIT_CENSUS shape.
   - **End-to-end, isolated exit term** (lesson of 081 A8/A9, 091 pt 1). Use a clean no-git tmp tree that exits 0. The same tree with `logs/implementation/2026-11-19.md = b"\xff\xfe"` must give:
     - stderr has no `Traceback`;
     - stdout has `UNREADABLE: logs/implementation/2026-11-19.md`;
     - exit 1.
     The bad byte must be the only difference, or a mutation that drops the exit term passes because of some other line (01 F12, F23). Repeat for a step file (`work/<ID>/05-build-report.md`), for `request.md`, and for a directory named `2026-11-19.md`.
   - **Stderr.** `_run` drops stderr (L62-65), and it decodes stdout with strict utf-8, so a bad byte reaching stdout would crash the test itself. Add a small helper that returns `(code, stdout, stderr)` from bytes, as test (c) does (L2481-2484). Do not change `_run`'s 2-tuple, which many tests unpack.
   - **N13** gains the CLI twin of its fixture through that helper.
   - **Test (c)** asserts `UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow)`, and names which line still carries exit 1 (MAIN AHEAD / OPEN BRANCHES, 01 F26). Its whole-output diff lists the RULE NOT SEEN change (01 F27).
   - **Mutations**, each of which must fail a named test:
     - catch only `OSError`;
     - catch only `UnicodeDecodeError` (directory fixture);
     - drop `or unreadable` from L1643;
     - drop it from the inbox early return;
     - one consumer back to raw `read_text` (census);
     - `_shallow_boundaries` back to `"unreadable" if sure else "full"` (test (c) text);
     - a consumer that treats why as "" and prints nothing (UNREADABLE line assert).

## 3 ways AGAINST
1. **Collision and scope: 16 sites in a rule file that 088, 090 and 091 also edit today.**
   - scripts/check_pipeline.py is in RULE_PATHS, so the person must approve it at PR review (086 audit L12).
   - 088 rewrites `_anchor_env`, 090 touches shallow handling and rule C/D, and 091 adds one test per exit-code term. 089 changes `_shallow_boundaries`, the exit expression and a dozen read lines nearby. Each later item rebases onto the others, and every exit-term test from 091 must include 089's new term, or one of them is stale on merge.
   - A broad rewrite also risks changing verdicts while "only removing crashes". Examples: unified globs (01 F21), changed newline handling (hole 4), or `read_request` reshaped wrongly.
   - Mitigation: build in a fixed order (state it in 04). Diff the whole output of check_pipeline on the real repo before and after, and expect one added `UNREADABLE: none` line plus nothing else (086 audit L10 did exactly this, `98a99`). Re-count the sites by AST after the tree is final, not from 01's 16 (RI-006, 01 Numbers).
2. **The shallow fix trades an exit-1 error for an exit-0 "not checked". It is safe only because git dies elsewhere.**
   - Today, sure False plus a decode error gives "full", then the wrong-reason UNTRACKED CHANGE line, **failed True** (01 F25). After the request's change, `_walk` L1218-1219 returns the not-checked tuple with **failed False** (01 F26).
   - Exit 1 then depends on `--is-shallow-repository` and the other git calls dying on the bad byte (A1 observed exit 128, 081 audit L12, L52). git's docs do not say what happens with a malformed shallow file (01 F15). If some git version tolerated the byte, a corrupt `.git/shallow` would leave the run at exit 0 with only a not-checked line. That is UNVERIFIED by a run, but nothing in the docs rules it out.
   - Option A: have `_shallow_boundaries` use `_read` and put its why into UNREADABLE whatever `sure` is. Then a decode error in an existing `.git/shallow` exits 1 on its own, and the UNTRACKED CHANGE text is still the not-checked form the request asks for.
   - Option B: keep the request's text-only change, and have test (c) name the line that carries exit 1, so a change in git's behaviour shows up as a failing test.
   - R1 open question 2: with sure False, only "no file" (FileNotFoundError) should give "full". PermissionError and IsADirectoryError prove the file exists, the same way a decode error does (01 F28). That widens the request slightly, so R3/I1 should decide it explicitly.
3. **It leaves the same crash in the sibling script, and it adds output and test cost.**
   - scripts/check_handoff.py L55 and L62 read 01/03 strictly (01 Q5). R3, I3 and A1 run it on every item (RI-006 guardrail), so a bad byte in 03 still gives a traceback there.
   - Fixing only check_pipeline.py while the census sits in check_pipeline's test gives a false sense of "every work/ read". This item's guardrail says "every logs/ and work/ read" (request L14). Either widen the census to both scripts or open a follow-up item the same day. Do not leave it unrecorded.
   - Cost:
     - one new always-printed line (`UNREADABLE: none`), which changes the text of A1's daily report;
     - per-item `not checked` entries, the same reason repeated once per item when a shared log is bad;
     - 5-7 new subprocess fixtures (seconds each) in a suite that already runs ~88 s (086 audit L31).
   - The repeat is honest but noisy. A cache across `incomplete` calls would remove it, but tests call `cp.main` several times in one process after rewriting files, so a module-level cache could serve stale text. Compute the unreadable set once per `main()` call, or accept the repeat.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 089 is a BUG fix inside this repo's checker: how it reads its own logs/, work/ and .git/shallow files, its output lines, exit code and tests. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are Python and git tool behaviour, cited to the official English docs below and by R1, following the 077-086 precedent (work/081/02 L89, work/086/02 L54).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | Hole: printing a non-UTF-8 file name | https://docs.python.org/3/library/os.html | "Python uses the surrogateescape encoding error handler, which means that undecodable bytes are replaced by a Unicode character U+DCxx on decoding" | (English source) |
| English | Hole: a surrogate in str is an error for the strict utf-8 codec | https://docs.python.org/3/library/codecs.html | 'surrogatepass': "Allow encoding and decoding surrogate code point (U+D800 - U+DFFF) as normal code point. Otherwise these codecs treat the presence of surrogate code point in str as an error." | (English source) |
| English | Hole: `read_text` translates newlines, raw `decode` does not | https://docs.python.org/3/library/functions.html | "if newline is None, universal newlines mode is enabled. Lines in the input can end in '\n', '\r', or '\r\n', and these are translated into '\n' before being returned to the caller." | (English source) |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |

## Holes to watch out for (summary)
1. **The exit term must be isolated.** The crash already exits 1 (01 F12), and so does a no-git tmp tree with other INCOMPLETE entries. Each fixture needs a clean twin that exits 0. Every exit path needs the term, including the INBOX early return at L1639-1641.
2. **Never print content, and watch file names.** Reasons use the path, the exception class and the byte offset only. `_log_text` globs `*.md`, so a file name with non-UTF-8 bytes becomes a str with U+DCxx surrogates (os docs). Printing it to strict stdout raises UnicodeEncodeError (codecs docs; PEP 538 via 081/02 L66). Render paths in the reason with `encode("utf-8", "backslashreplace").decode()`, or record the gap. A fixture with `os.fsdecode(b"\xff.md")` is optional but cheap on Linux.
3. **N13's text pin.** Keep the reader's why ending `<posix path> unreadable` (L3071), or change N13 on purpose and list the diff in 05.
4. **Newline behaviour.** `read_text` translates `\r\n`/`\r` to `\n` (open docs); `read_bytes().decode()` does not. Either normalise newlines in `_read`, or show by test that every consumer is CRLF-safe. Most readers use `splitlines()` and start-anchored regexes, but `re.M` `$` patterns (e.g. LOG_LINE on joined text) need a check. A CRLF fixture with the same verdict before and after pins this.
5. **No false entries from "".** A consumer must not compute INCOMPLETE, UNCOMMITTED STEP or ORPHAN results from a lost file's empty text. It prints `not checked (<file> unreadable)` instead. `_sent_back` stays on the refusal side, unchanged.
6. **Shallow.** The request's change makes UNTRACKED CHANGE exit-neutral (01 F26). Either route `.git/shallow` decode errors into UNREADABLE (AGAINST 2 option A), or have test (c) name the line that carries exit 1. RULE NOT SEEN changes too (01 F27) and must be listed in 05/06.
7. **The census must match `ast.Attribute`** (`f.read_text`), not only `ast.Name`. Pin the total, and give `write_log`'s append `open` a reason. Re-count the sites by AST after 088/090/091 land, never from 01's 16.
8. **Glob sets unchanged** (`*.md` vs `????-??-??.md`). Unifying them is a separate item.
9. **check_handoff.py L55/L62** are the same bug. Widen the census or open a follow-up item today. Do not leave it silent.
10. **No module-level cache.** Tests call `cp.main` several times in one process after rewriting files.
11. **F20 (UNVERIFIED by run).** With git, the first crash comes from `uncommitted_steps` → `_log_text` before `incomplete`. I2 should confirm it on the fixture, and the git-present fixture must also assert no traceback.

Log fields: 3 for / 3 against | languages: N/A
