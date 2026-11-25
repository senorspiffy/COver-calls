# 04 Build plan - 088
Fit verdict: FIT WITH CHANGES

Method: I1 has no shell (item 072). Line numbers below were re-read on daily-fixes/2026-11-21 (working tree, 2026-11-21) from `scripts/check_pipeline.py` and `tests/test_pipeline_check.py`; nothing was run. Inputs: work/088/request.md, 01-03, logs/recurring-issues.md, work/089-091/request.md.

Fit: process-only (no trade, broker or account input), so the ~$3k account and the 001 strategy rules are untouched. No rule the person follows changes. It fits the existing code: `_anchor_env` has one caller (main L1535), no test calls or patches it today (grep), and the only other users of the 084 gate are `incomplete`'s three `_rule_seen` calls (L710, L738, L754). The changes are:
1. **Build order.** 03 step 0 says to re-read after 089/090/091 land. Today 088 builds first, so step 0 runs against the current HEAD, and 089, 090 and 091 rebase on 088's census and exit-term changes (see "Conflicts with today's other items").
2. **One extra guardrail line (E1).** "RULE NOT SEEN:" is added to `GIT_LINES`, so the three all-git-fails tests also pin that the new failed-verify form is never `none` (RI-014).
3. **(u-s) becomes its own test.** It is not a third parametrize case of S13. The S13 body commits before it runs, and an uncommitted case would need a branch inside a parametrized body.

## Extra research (with sources)
- git `builtin/rev-parse.c` (https://raw.githubusercontent.com/git/git/master/builtin/rev-parse.c, opened 2026-11-21): `die_no_single_rev(int quiet) { if (quiet) exit(1); else die(...); }`. This confirms 03 F8. **Edge case R3 missed:** every `--verify` failure goes through the same path. That includes zero revisions, an unresolvable name, and a flag argument, all handled by `repo_get_oid_with_flags` with `GET_OID_QUIETLY`. So exit 1 means "HEAD names no commit", not strictly "unborn". A HEAD whose ref can't be resolved would also print `not checked (unborn HEAD)`. This is still safe:
  - no anchor is read, so every item keeps the strict numeric rule;
  - on such a HEAD, `uncommitted_steps`' `git ls-tree HEAD` also fails (L606-608), so main still exits 1.
  
  Plan: the `_anchor_env` docstring states it as a known gap ("exit 1 = HEAD names no commit: unborn, or a ref git can't resolve; both strict, and UNCOMMITTED STEP gives exit 1"). No extra git call to tell the two apart (simpler, and the census stays 47).
- The same file confirms that `--is-shallow-repository` prints `is_repository_shallow(...) ? "true" : "false"` (03 F6). No new source is needed for F13 (ce11360 + usage.c exit 128). The (h) fixture pins the observable result (step 3, M-b').
- Code finding, not in 03: `_inbox_gate` L1467 runs the same `rev-parse --verify -q HEAD` command. So `test_anchor_env_failure_exits_1` must patch `cp._anchor_env`, not `_git` for that argument tuple, because patching `_git` would also move INBOX. The unit test `test_anchor_env_reads_head_once` patches `_git` and calls `_anchor_env()` alone. This keeps 03's design and records why.
- Unborn repo end-to-end: P5h (tests L976-985) already runs `main` on an unborn repo with no traceback. So (h) can use `_run`.

Line table (step 0, re-read 2026-11-21; 03's numbers hold):

| Name | Line(s) |
|---|---|
| docstring sentence | L273-275 |
| `uncommitted_steps` | L600-620 |
| `_anchor_env` | L623-632 |
| `_rule_seen` | L635-664 (head block L643-648) |
| `incomplete` | L687 (gates L709, L725/L738, L745/L754) |
| `_git` | L1008 |
| `_shallow_boundaries` | L1183 |
| `main` | L1507 (unpack L1535, RULE NOT SEEN print L1618, inbox early return L1639-1641, exit expression L1643-1645) |
| GIT_CENSUS | tests L2369-2397 (total assert L2432 = 47) |
| d1 | tests L2703 |
| e1/e2 | tests L2744 |
| (i) | tests L2795 (exit 0 at L2813) |
| S13 | tests L3427 |
| GIT_LINES | tests L2365 |

The before-state lines from HEAD (`INCOMPLETE:`, `RULE NOT SEEN:`) need a run. I2 pastes them verbatim in 05 before the first edit, from `python3 scripts/check_pipeline.py` on the worktree. The expected `RULE NOT SEEN:` contains 083 (test f1 L2779-2780 pins `(False, "cfc0634")` for 083's 05 and 06). This is UNVERIFIED until I2 runs it.

## Files to create/change
2 files planned (plus I2's own work/088/05).

**`scripts/check_pipeline.py`**
- `_anchor_env()` returns `(env, failed)`:
  - `_git("rev-parse","--git-dir") is None` → `("no git", False)`
  - shallow → `("shallow clone; run git fetch --unshallow", False)`
  - `head = _git("rev-parse","--verify","-q","HEAD")`:
    - `None` → `("no git", False)`
    - exit 0 → `(None, False)`
    - exit 1 → `("unborn HEAD", False)`
    - other → `(f"git rev-parse --verify HEAD failed (exit {head[1]})", True)`
  - Docstring: return contract, the exit-1 known gap above, and "read once per run (item 088)".
- `_rule_seen`: delete L643-648 (the `head` block). `failed = ...` stays before the `log` call. Docstring: `(None, "")` with env set or an uncommitted file; HEAD is read once in `_anchor_env` (item 088).
- `main` L1535: `(env, env_failed), not_seen = _anchor_env(), []`. Add `or env_failed` to the return expression L1643-1645. The L1618 print is unchanged. The inbox early return already returns 1.
- Module docstring L273-275 is rewritten from the code:
  - an uncommitted 05/06 keeps the numeric cutoffs with no entry;
  - an unborn HEAD prints `not checked (unborn HEAD)`;
  - a failed verify prints `not checked (git rev-parse --verify HEAD failed (exit <n>))` and gives exit 1;
  - call counts are as in 03 step 5: full pair 3 wrapper calls = 6 git processes; early exits 0/1/2; +1 per run; at most 3 pairs per item; pre-088 it was 4 = 8.

**`tests/test_pipeline_check.py`**: the tests below, plus the census edit, plus E1.

Not changed: TESTS_FORMAT_FROM, SUITE_FROM, VERDICT_FROM, CHECKLIST_FROM, LOG_CHECK_FROM, `write_log`, `incomplete`'s gate logic, exception lists, work/084/03, and any agent or template text. Grep: no agent or template quotes the RULE NOT SEEN not-checked forms. run-item.md L13 names the line only.

## Tests and checks
Build in 03's two stages, so that A1's mutations are shown on the code A1 mutated.

**Stage A (today's code, before any check_pipeline.py edit):**

1. `test_rule_anchor_uncommitted_step_is_strict` **(u)**, `@NO_GIT`.
   - Setup: `git init -q -b main`; write RULE_FILE = `NEW_RULES`; commit as `root`; `_defective(repo, "150")` left uncommitted; `_run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-02")`.
   - Expected `INCOMPLETE:` line: `INCOMPLETE: 150 (log line for I2 does not match its format (item 045): {NEW_I2_WANT}; {NO_SENT_BACK})`.
   - Expected `RULE NOT SEEN:` line: `RULE NOT SEEN: none`.
   - Pins:
     - `subprocess.run(["git","log","--no-renames","--diff-filter=A","--format=%H","-1","--","work/150/05-build-report.md"], cwd=repo, capture_output=True, text=True)` gives `(returncode, stdout) == (0, "")`.
     - Under `monkeypatch.chdir(repo)`: `cp._rule_seen(Path("work/150"), "05", "TESTS_FORMAT_FROM", None) == (None, "")`, and the same for `("06", "VERDICT_FROM")`.
2. `test_suite_gate_uncommitted_05_is_strict` **(u-s)**, `@NO_GIT`.
   - Setup: RULE_FILE = S13b's rules (`TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\n`), committed as root; `_suite_item(repo, "x\n")` left uncommitted; `--untracked-from root --today SUITE_DAY`.
   - Expected: `INCOMPLETE: 151 ({NO_SUITE})` and `RULE NOT SEEN: none`.
3. `test_rule_anchor_unborn_head_is_strict` **(h)**, `@NO_GIT`.
   - Setup: `git init -q -b main`; write RULE_FILE `NEW_RULES` and `_defective(repo, "150")`; commit nothing; `_run(repo, "check_pipeline.py", "--today", "2026-11-02")`.
   - Expected: the same INCOMPLETE line as (u), and `RULE NOT SEEN: none`.
   - Pins: `git rev-parse --verify -q HEAD` returncode 1; `--is-shallow-repository` stdout `"false"`; under chdir, `cp._anchor_env() is None` and `cp._rule_seen(...) == (None, "")` for 05 and 06.
   - No assert on the exit code alone (it is 1 via UNCOMMITTED STEP, F5).
4. d1 (L2703) table gains two rows:
   - `("rev-parse","--verify","-q","HEAD"): ("",128)`
   - `("ls-tree","--name-only",added,"--","scripts/check_pipeline.py"): ("",128)`
   
   Both use the same three asserts.
   - Before adding them, I2 runs **M-c** (L647 → `return False, ""`) and **M-d** (L657-658 → `return False, ""`) in a scratch copy and records survived/failed in 05.
   - Then, with the tests added, I2 runs **M-a** (L654-655 → `return False, ""`; must fail (u) and (u-s)) and **M-b** (L644-645 → `return False, ""`; must fail (h)). I2 pastes the failed/passed counts for each.

**Stage B (the move):**

5. Code edits as in "Files to create/change".
6. (h) updates:
   - expected `RULE NOT SEEN: not checked (unborn HEAD)` (INCOMPLETE unchanged);
   - pin `cp._anchor_env() == ("unborn HEAD", False)`;
   - pin `cp._rule_seen(..., "unborn HEAD") == (None, "")`.
7. d1's `--verify` row moves out (`_rule_seen` no longer calls it) into new `test_anchor_env_reads_head_once`:
   - `_patched_git` with verify `("",128)` → `("git rev-parse --verify HEAD failed (exit 128)", True)`;
   - on a committed repo (`_history`) → `(None, False)`.
8. New `test_anchor_env_failure_exits_1`:
   - the (i)-shape clean repo (one EMBEDDED_RULES form, which exits 0);
   - in-process `cp.main(["--untracked-from", root, "--today", "2026-11-02"])` under chdir, with `cp._anchor_env` patched to `lambda: ("git rev-parse --verify HEAD failed (exit 128)", True)`;
   - expected: returns 1, and capsys shows `RULE NOT SEEN: not checked (git rev-parse --verify HEAD failed (exit 128))`;
   - unpatched → 0.
   - It patches `_anchor_env`, not `_git`, because of `_inbox_gate` L1467.
9. GIT_CENSUS:
   - delete `("_rule_seen","_git")`;
   - `("_anchor_env","_git")` → `(2, "084: no-git probe; 088: rev-parse --verify HEAD read once: exit 1 = no commit (unborn) -> not checked, None -> no git, other non-zero -> not checked + exit 1")`;
   - the total assert stays 47 and its comment holds.
10. **E1**: append `"RULE NOT SEEN:"` to `GIT_LINES`.
    - In `test_all_git_fails_no_line_says_none` the line becomes `not checked (git rev-parse --verify HEAD failed (exit 128))`; today it would be `none`.
    - In (b) and (c) the shallow file is malformed → `"unreadable"` → `not checked (shallow clone; ...)`.
    - The `endswith(": none")` assert holds in all three, so each now pins that a git failure never makes RULE NOT SEEN read `none`.
    - I2 confirms that (a) fails with E1 on stage-A code (expected) and passes after stage B.

**Mutations, scratch copy only (`/tmp/claude-0/scratch/i2-088/`, never in the repo):**

| Mutation | Change | Must fail |
|---|---|---|
| M-b' | exit-1 branch removed (falls to `(None, False)`) | (h) |
| M-e | `== 1` → `!= 0` | `test_anchor_env_reads_head_once` |
| M-f | `or env_failed` dropped | `test_anchor_env_failure_exits_1` |
| M-g | `_rule_seen` `if env is not None: return False, ""` | e1 and (h) |
| M-h (new) | `_anchor_env` verify-None branch → `(None, False)` | needs the d1-style unit row `_git` None for verify only → `("no git", False)`; add it to `test_anchor_env_reads_head_once` |
| census probe | old `rev-parse` line put back in `_rule_seen` | `test_git_call_census` |

Done check:
- full suite green;
- `python3 -m py_compile` with python3.11 if present (RI-008);
- HEAD's `INCOMPLETE:` and `RULE NOT SEEN:` lines equal the pasted before-state (0 lines expected to change: HEAD is born and 083's anchors are committed).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 0 re-read after 089/090/091 land | Changed: re-read done here on the current HEAD (line table), because 088 builds first. The before-state run → I2, pasted in 05 before the first edit |
| Step 1 (u) | Tests and checks 1 |
| Step 1 (u-s) as S13c case | Tests and checks 2, as its own test (fit change 3) |
| Step 1 (h) | Tests and checks 3, then 6 |
| Step 1 M-a, M-b on today's code | Tests and checks 4 (stage A) |
| Step 2 d1 rows + M-c/M-d before-run | Tests and checks 4 |
| Step 3 `_anchor_env` tuple, `_rule_seen` head block removed, main unpack + `or env_failed` | Files to create/change; Tests and checks 5-8 |
| Step 3 M-b', M-e, M-f, M-g | Mutations table; M-h added for the `None` branch |
| Step 4 census | Tests and checks 9 |
| Step 5 docstrings + counts; 084/03 not edited | Files to create/change (docstring bullets); scope note |
| Step 6 done check, I3 re-runs M-a..M-g in scratch | Done check; I3 runs M-a..M-h |
| Decision: read HEAD once, two stages | Stage A / Stage B |
| Decision: no anchor cache | DROPPED: 03 rejects it (R2 AGAINST 3); nothing depends on it |
| Removed claim (TESTS+SUITE cost 0) | DROPPED: removed in 03, no cache built |
| Scope lock | Files to create/change "Not changed" |
| F4 fix (the 06 window is i3 step 5, 05 window i2 commit) | Docstring wording: "uncommitted 05/06 (any check run before its commit)", no run-item.md edit |
| F13 (unborn `log` exits 128) | M-b' expected failure; pinned by (h) |
| F16 fix (`--untracked-from`, chdir) | Tests and checks 1-3 setup |
| R2 FOR 3 gap (bool, not text, RI-012) | `env_failed` bool; Tests and checks 8 |
| Missing inputs: no git | e2 unchanged (L2762) |
| Missing inputs: shallow | e1 unchanged (L2752) |
| Missing inputs: unborn HEAD | (h) |
| Missing inputs: verify other exit | `test_anchor_env_reads_head_once`, `test_anchor_env_failure_exits_1`, E1 |
| Missing inputs: uncommitted 05/06 | (u), (u-s) |
| Missing inputs: log/ls-tree/show exit ≠ 0 | d1 existing rows + ls-tree row |
| Missing inputs: RULE_FILE absent in anchor | d2 unchanged (L2723) |
| Rule text the person follows (001 slack/tolerance/cap) | None changed (process-only); no request needed |

## Guardrail tests
Feasibility (gate cutoffs; 03 counts):
- TESTS gate (≥ 76, "I2" in bad) → (u) and (h) reach it with item 150 (03 Self-check row "(u) gate reach"). M-a and M-b must fail it.
- VERDICT gate (≥ 71, a verdict-line check fires) → (u) and (h) via 150's missing Sent-back line.
- SUITE gate (≥ 87, last I2 line well-formed, Suite mismatch) → (u-s) with item 151.
- HEAD count: 083 = 2 pairs (audit fd2b139; f1 pins `cfc0634` for both). I2 records the live before-state, and the done check requires it unchanged.

Missing inputs:
- unborn HEAD → (h)
- failed verify → `test_anchor_env_reads_head_once` + `test_anchor_env_failure_exits_1` + E1
- verify `_git` None → M-h row
- uncommitted 05/06 → (u), (u-s)
- failed ls-tree → d1 row
- no git / shallow / no RULE_FILE → e2 / e1 / d2 (unchanged)

## Expected result
- Stage A:
  - (u), (u-s) and (h) pass on today's code;
  - M-a fails (u) and (u-s); M-b fails (h);
  - M-c and M-d each have a recorded before-result and fail d1 once its rows are added.
- Stage B:
  - full suite green, census total 47;
  - an unborn HEAD prints `RULE NOT SEEN: not checked (unborn HEAD)` with 150's strict INCOMPLETE text;
  - a failed verify prints `not checked (git rev-parse --verify HEAD failed (exit <n>))` and exits 1;
  - a full pair costs 3 wrapper calls (6 git processes) + 1 per run (083: 7 wrapper calls vs 8);
  - M-b', M-e, M-f, M-g and M-h each fail a named test;
  - HEAD's INCOMPLETE and RULE NOT SEEN lines are unchanged.

Conflicts with today's other items (all build on 088):
- **089**: its `_shallow_boundaries` decode change keeps (b)/(c) at `"unreadable"`, so E1 still holds. Its reader census is separate from GIT_CENSUS.
- **090**: no overlap with `_anchor_env` or `_rule_seen`.
- **091**: point 1 adds a test per exit-code term. `env_failed` already has `test_anchor_env_failure_exits_1`, so 091 should not add a second one. Point 5's unshallow sentence should also name 088's two new not-checked forms.
- **All three**: restate the census from 088's entries (`_anchor_env` 2, no `("_rule_seen","_git")`).

Recurring issues checked:
- RI-001 (ESCALATED): every gate-reach line has its fixture and count; nothing says "always".
- RI-010 (ESCALATED): no log line typed here; the log fields line below is for the orchestrator.
- RI-014 (OPEN): a failed verify is exit 1, never `none` (Tests and checks 8, E1).
- RI-002 (GUARDED, root cause): every unknown path is strict and has a fixture.
- RI-012 (GUARDED): `env_failed` is a bool, and no text match is used.
- RI-008 (GUARDED): py_compile with 3.11 is in the done check.
- RI-009 (GUARDED): build order and the shared-file conflicts are stated above.
- RI-004/RI-005: the worked lines above were re-derived from 03's Self-check and the code.
- RI-006: the file count (2) is counted from the "Files to create/change" list.

Log fields: FIT WITH CHANGES | 2 files planned
