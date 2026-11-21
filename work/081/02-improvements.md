# 02 Improvements - 081
## What past logs say
- RI-014 (logs/recurring-issues.md L152-158): OPEN. Its 2026-11-20 status note names this item ("near miss, not counted (A1 probe before merge)"). 079 fixed only the walk users (`_walk`, research_code, real_data_field). It left alone the three readers A1 named in logs/audit/2026-11-19-079.md P1 (L99-111) and the strict decode in P2 (L112-115).
- RI-002 (L24-36) is the family: an uncomputable result turned into "none". 079's audit found the same pattern in `research_code` (`files or []`, logs/audit/2026-11-19-079.md L59). It was fixed there with a None guard and pinned by mutation (L77-78). 081 should follow that shape: mutation, then a named failing test.
- RI-009 (L108-116): `--next-id` and ID CLASH exist to stop two threads sharing an ID (item 037). A wrong `--next-id` is the exact 037 failure, so on a git failure it must print no number.
- Precedents for how loud to be:
  - 069/070: a failing `git log` gives `(git log failed)` and exit 1. Tests: tests/test_pipeline_check.py L2068-2070 and tests/test_real_data_field.py L300-301, L340-343.
  - 077: `ls-tree HEAD` failure is an error (`UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)`, audit 079 L66).
  - 053/079: only *known benign* states (no git, shallow clone) give `not checked` with exit 0.
  - So 081 should make a git command that dies (exit 128) an error with exit 1, not a `not checked` with exit 0.
- Probe anchors: scripts/probe_guardrails.py L68-83 mutate three exact lines inside `open_branches`: `                clashes.append(item)`, `        rules = changed(*RULE_PATHS)` and `        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None`. A refactor that rewrites those lines gives ANCHOR MISSING in the daily probe run.
- Existing tests that 081 must keep or change on purpose:
  - tests/test_pipeline_check.py L201 asserts `"OPEN BRANCHES" not in out` when there is no git.
  - Five tests monkeypatch `_git` with lambdas that return 2-tuples: test_pipeline_check.py L1590, L1748, L2068 and test_real_data_field.py L300, L340 (grep).
- R2 precedent: 077, 078 and 079 (logs/research/2026-11-19.md L7, L11, L12) were all git-behaviour BUG fixes in this script and logged `languages: N/A`.

## 3 ways FOR
1. **Keep `_git`'s `(stdout, code)` contract, fix the decode in both `subprocess.run` calls, and add one thin helper. This answers R1's open question 1.**
   - Changing `_git` to a 3-tuple or a NamedTuple with `.ok` would break the five 2-tuple monkeypatch lambdas above, and every `[1]` reader would need a re-read. The diff would also grow in a file that 084 and 086 edit after 081 today.
   - Instead, add `errors="replace"` to L623-624 and L627. F9 explains why both: with only L627 changed, a non-UTF-8 top-level path still crashes at L624.
   - `'replace'` puts U+FFFD in place of the bad byte, and U+FFFD encodes in UTF-8 [https://docs.python.org/3/library/codecs.html]. So the `write_text(..., encoding="utf-8")` at L694 cannot re-raise. `surrogateescape` would re-raise there: `open()` has `errors=None` in its signature [https://docs.python.org/3/library/functions.html], and codecs calls `'strict'` "the default". This settles R1's UNVERIFIED point L16.
   - Add `_git_ok(*args) -> (out, why)`. `why` is None on exit 0, `"no git"` when `_git` gives None, and `f"git {args[0]} failed (exit {code})"` otherwise. The text is built only from argv and the exit code, never from stderr (AGAINST 2).
   - Guardrail for "every call site checks": a census test, not a data-flow lint.
     - It parses check_pipeline.py with `ast`, maps each `_git(`/`_git_ok(` call to the function it sits in, and compares the result with a dict `{function: (count, reason)}` kept in the test.
     - A new or moved call site fails the test until someone writes down why its failure branch is safe.
     - This is far easier to keep correct than an AST rule that tries to prove `[1]` is compared on every path. Reasoning: L647 and L685 index `[1]` inline inside boolean expressions, and L661/L668/L677/L713 use `x and x[1] == 0 else []`, a shape where the code is checked but the failure still becomes empty. A "`[1]` is used" lint would pass every one of the buggy sites.
2. **For each of the three cases with a legitimate empty answer, use one query that cannot be ambiguous (R1 open question 2), and pin each one with a fixture.**
   - **LOG TIME (F2).** Before the blame loop, run one `ls-tree -r --name-only HEAD -- logs/research/ logs/implementation/`. This is the 077 pattern already used at L499-502.
     - If it fails, LOG TIME prints `git ls-tree HEAD failed (item 081)` and the run exits 1.
     - A file not in the list (not committed yet) is skipped, as today.
     - A listed file whose blame fails becomes an entry `<file> (git blame failed)`, and the run exits 1. The skip stays only for the uncommitted case (A1 note, audit 079 L106).
   - **`--next-id` (F5).** Replace `ls-tree -d --name-only <ref>:work` with `ls-tree -d --name-only <ref> -- work/`.
     - The old form names a tree object that does not exist on a branch with no work/, so "absent" and "git died" are both non-zero (the cat-file/rev-parse findings, R1 L19-20).
     - The new form takes a pathspec on a commit that does exist. My expectation is exit 0 with empty output when nothing matches. That is UNVERIFIED by the docs (R1 L21), so a fixture must pin it: a branch with no work/ gives exit 0 and the other branches' IDs still count.
     - Output lines are `work/080`, so take the basename.
     - Any non-zero exit, and a failed `branch -r`, means `main()` prints `--next-id refused: git <cmd> failed (exit N); not counting open branches would risk an ID clash (item 037)` to stderr, prints nothing on stdout and returns 2. That is the existing refusal code of `write_log` (L561-569). It answers R1 open question 3: never print a number.
   - **MAIN AHEAD (F6).** Replace `rev-parse --verify -q origin/main` with `for-each-ref --format=%(objectname) refs/remotes/origin/main`. Empty output with exit 0 means "no origin/main", which gives 0 as the docstring says. That exit status is UNVERIFIED by the docs; pin it with the no-origin fixture. Any non-zero exit, or a failed `rev-list --count`, prints `MAIN AHEAD: git <cmd> failed (item 081)` and exits 1. Inside `open_branches`, an unknown `behind` stays False, which lists more branches and is the safe direction (F4 last bullet).
   - This puts MAIN AHEAD in scope (R1 open question 6). The request says "every check", and the change is two lines.
3. **Make OPEN BRANCHES' failure visible in every line that reads it, and test with two fixtures plus named mutations.**
   - **Output.**
     - `open_branches` returns `None` when `_git` is None (no git: keep today's absent line, so test L201 holds), or a string error when `branch -r` fails.
     - On the error, main prints `OPEN BRANCHES: git branch failed (exit N) (item 081)`, exits 1, and prints `not checked (see OPEN BRANCHES)` for IN PR, RULES BRANCH and ID CLASH. Today those six readers all look clean (F3).
     - When git ran and found no branch, print `OPEN BRANCHES: none` (R1 open question 5). A1 can then tell "none" apart from "not run". Older daily reports wrote "No OPEN BRANCHES line" (logs/audit/2026-11-05.md L5), and that wording changes.
     - Per-ref failures in `changed()`, `ls-tree`, `merge-base --all` and `show` go into a per-branch `errors` list. They print as `BRANCH ERROR: <ref> (git <cmd> failed)` and the run exits 1. The `show` body failure is the L70-documented gap.
     - `log -1` (age only) can stay cosmetic, with a census reason.
     - `_open_at` gets a census entry. Its reason: the same walk's `diff-tree` already succeeded, and an absent 07 must read as open (F8).
   - **Fixtures.**
     - (a) An all-fails fake: `monkeypatch.setattr(cp, "_git", lambda *a: ("", 128))`. Assert no git-reading line (LOG TIME, OPEN BRANCHES, IN PR, RULES BRANCH, ID CLASH, MAIN AHEAD, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, UNCOMMITTED STEP, INBOX) ends in `: none`, the exit code is non-zero, and `--next-id` returns 2 with empty stdout.
     - (b) A1's real-git repro: `.git/shallow` = `<40hex>\nzz\n`, with a scratch `origin/scratch-x` holding work/099 and a late log line. Assert the same lines, plus `--next-id` returns 2, not `080`. This covers F7's mixed state, where `rev-parse --verify HEAD` succeeds and blame/ls-tree die, which (a) cannot show.
     - (c) A `\xff` shallow line. Assert exit 1, `"Traceback" not in stderr`, and no line `: none`.
     - (d) The legitimate-empty cases from FOR 2 keep today's answers.
   - **Mutations, each of which must fail a named test:**
     - put back `continue` at the blame site;
     - put back `return []` in `open_branches`;
     - put back `else []` in `next_id`;
     - drop `errors=` at L627;
     - drop `errors=` at L624, with a fixture whose top-level path holds a `\xff` byte, if the platform allows it; otherwise record that as a known gap.

## 3 ways AGAINST
1. **Collision and anchor cost in a file three items edit today.**
   - 081 builds first, and 084 and 086 rebase onto it. R1 counted 39 call lines and 12 failure-to-empty sites. A broad refactor (wrapping all 39 calls, renaming locals, reflowing `open_branches`) raises merge-conflict risk for 084/086.
   - It can also rewrite the three probe anchor lines (probe_guardrails.py L68-83). That gives ANCHOR MISSING in A1's daily probe run, which is reported as a failure, not a hold.
   - Mitigation: change only the 12 sites plus the two decode lines, add new lines rather than rewriting the anchor lines, and run `probe_guardrails.py --ref HEAD` in I3. Keep F10 (strict `read_text` at L310, L369 and the others) out as a separate item, as R1 suggests. The request names only git output.
2. **Echoing git's stderr in the message can move the crash instead of removing it.**
   - With `errors="replace"`, stderr can hold U+FFFD (for example `fatal: bad shallow line: �`).
   - PEP 538 states that CPython's standard streams default to `surrogateescape` only for the C locale and its UTF-8 coercion targets. "For other locales, the default is `strict`" [https://peps.python.org/pep-0538/]. So under a non-UTF-8 locale such as a Latin-1 one, `print` of U+FFFD raises UnicodeEncodeError, and the traceback is back at the print line. That this applies to this repo's runners is my inference: no run was made here, so UNVERIFIED by a probe.
   - That is why FOR 1's `why` uses only argv and the exit code. If I1 wants git's first stderr line (R1 open question 4), render it with `.encode("ascii", "backslashreplace").decode()` and pin it with fixture (c). This also answers R1's UNVERIFIED point L17.
   - A smaller cost of `'replace'`: a log line that has a raw byte no longer matches LOG_LINE in blame output, so LOG TIME skips that one line. It is not a false pass of a format check, because ORPHAN LOG's strict `read_text` of the same file (L587) still tracebacks (F10). It is still a hole while F10 is open.
3. **The exit-code and output contract changes, and a transient git failure now blocks work.**
   - Today `--next-id` always prints a number and exits 0. README.md L8, templates/request.md L2 and a1-auditor.md L29 tell readers to take the ID from its output. After 081, a git failure gives exit 2 and empty stdout. A caller that does `ID=$(... --next-id)` without checking the code would get an empty ID.
   - The main run likewise goes from "clean-looking exit 1 via other lines" to an explicit exit 1 with new BRANCH ERROR, OPEN BRANCHES and MAIN AHEAD texts. A1's report wording (audit files quote these lines) changes.
   - Any git read failure, including a one-off (for example a ref being rewritten during a concurrent `git fetch`, UNVERIFIED as a real-world case here), now fails the run. Today it passes quietly.
   - Reasoning for accepting it anyway: RI-009/037 show that a wrong ID costs more than a refused one, and the 069/070 precedent already makes `git log failed` exit 1.
   - Mitigation: the refusal text says what to do ("run `git fetch origin` / fix the clone, then re-run"). Add one sentence to a1-auditor.md L29: "if `--next-id` refuses, do not pick an ID by hand". That sentence is a RULES change, so the person's OK is needed in PR review. Also add a test that `--next-id`'s stdout is empty on refusal.

## Settled decisions for I1
- Keep `_git` returning `(stdout, code)`. Use `errors="replace"` on both runs. Add `_git_ok(*args) -> (out, why)`, with `why` built from argv and the exit code only.
- Make a census test (AST, `{function: (count, reason)}`) the "every site checks" guardrail.
- Git died → error text + exit 1. No git or a shallow clone → the existing `not checked`, exit 0. `--next-id` on a failure → stderr message, empty stdout, return 2.
- Disambiguation:
  - logs: one `ls-tree HEAD` list;
  - next_id: `ls-tree -d --name-only <ref> -- work/`;
  - main_ahead: `for-each-ref refs/remotes/origin/main`.
  - Each "empty = absent" exit status is pinned by a fixture, because the docs don't state it.
- OPEN BRANCHES: no git → absent (L201 holds); failure → error line, plus `not checked (see OPEN BRANCHES)` for IN PR / RULES BRANCH / ID CLASH; truly none → `OPEN BRANCHES: none`. Per-ref failures go to `BRANCH ERROR:` lines.
- Leave the three probe anchor lines byte-identical. F10 is a separate item. In scope: MAIN AHEAD and `_open_at` (census entry with a reason).
- Fixtures (a)-(d) and the mutations listed in FOR 3. Re-count the sites after the tree is final (084/086 land after 081).

Languages: N/A (no new external claims). 081 is a BUG fix inside this repo's checker script (how it handles a failing git command, its decoding, its output and exit codes, and its tests). It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are Python and git tool behaviour, cited to the official English docs and PEP above, following the 077/078/079 precedent (logs/research/2026-11-19.md).

## Holes to watch out for (summary)
- A lint that only checks "`[1]` is used" passes the buggy `x and x[1] == 0 else []` sites. Use the census test, and rely on the behavioural fixtures for the real guarantee.
- The all-fails fake alone misses F7's mixed state (`rev-parse --verify HEAD` succeeds while blame and ls-tree die). Keep the real-git malformed-shallow fixture.
- Don't use a `rev-parse HEAD` health probe as the trigger. It does not fire in A1's repro (F7).
- `surrogateescape` only moves the crash to L694's `write_text`. Use `replace` on both `subprocess.run` calls (L624 and L627).
- Don't echo raw stderr. Under a non-UTF-8, non-C locale stdout is strict (PEP 538).
- `ref:work` cannot tell "absent" from "died". Don't keep it for `--next-id`.
- `--next-id` must print nothing on stdout when it refuses.
- Test L201 (no git → no OPEN BRANCHES) must still pass, and the probe anchor lines must not change.
- The exit status of "no match = exit 0" for `ls-tree <commit> -- <path>` and `for-each-ref <missing ref>` is UNVERIFIED by the docs. Pin it with a fixture, don't assume it.

Log fields: 3 for / 3 against | languages: N/A
