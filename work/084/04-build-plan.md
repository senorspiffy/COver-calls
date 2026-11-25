# 04 Build plan - 084
Fit verdict: FIT WITH CHANGES

I1 had no shell in this run. No git command, no pytest and no `check_pipeline.py` run was done by I1. Code facts below come from reading `scripts/check_pipeline.py` and `tests/test_pipeline_check.py` on daily-fixes/2026-11-20 (before 081 lands). Functions are named, not line numbers, because 081 rewrites the git call sites in `check_pipeline.py` first. The I1 log line has to be written by the orchestrator: `python3 scripts/check_pipeline.py --log I1 084 "FIT WITH CHANGES | 3 files planned"`.

Recurring issues checked (item 013), open or ESCALATED entries:
- **RI-001** (ESCALATED). Every gate below has a count: 10 VERDICT-gate items, 5 TESTS-gate items, and 1 suppressed pair-set {083} on HEAD. Step 0 re-measures each per-item anchor before any edit. Nothing here says "always".
- **RI-010** (ESCALATED, this item's family). Every exemption is printed by ID on `RULE NOT SEEN:`. The HEAD set is pinned to exactly {083}. A positive control (076) catches a renamed constant. No exemption is silent.
- **RI-014** (OPEN). No git or a shallow clone falls back to the strict numeric cutoff with a printed `not checked` line. Shallow detection reuses `_shallow_boundaries()`. A failing git call becomes an INCOMPLETE entry. The repo self-test skips loudly in a shallow clone, so its result never depends on clone depth without saying so.
- Also checked (GUARDED): RI-002 (an unknown anchor never becomes "not seen"), RI-006 (I2's tests field is the pytest line as printed), RI-007 (Scope FULL, nothing skipped), RI-011 (the add-commit lookup uses no `--first-parent`, see Extra research 1).

## Fit check
- **~$3k account.** Process-only. No trade, price, option, broker or ticker input changes. Nothing is connected to a brokerage. No 001 rule the person follows changes (no slack, tolerance or cap), so no rule-text update is needed.
- **Existing code.** The approach fits next to `_inbox_gate` (069, same add-commit plus tree test) and `_shallow_boundaries` (079). It conflicts with nothing built. It touches `incomplete()`, `log_fields_ok()`, `log_hint()` and `main()`, which 081 does not rewrite apart from their git calls (081 adds none of these). `write_log()` keeps its numeric rule.
- **Ordering today (081 → 084 → 086 …).** 081 replaces `_git`'s failure handling with "one helper that returns (out, ok)" and adds a lint test saying every `_git(` call site checks ok (work/081/request.md). 084's new git calls must use 081's helper and pass that lint test. If 081 renames `_git` or `_patched_git`, use the new names. Do not re-add the old pattern.
- **Changes to 03 (why "WITH CHANGES"):**
  1. Shallow detection calls `_shallow_boundaries()` (079), not the raw `rev-parse --is-shallow-repository` that `_inbox_gate` uses. The 079 helper already handles exit 129 (flag unknown), a malformed shallow file (rev-parse exits non-zero, `test_malformed_shallow_line_real_git_not_checked`) and an empty shallow file. `"full"` and `[]` mean full history. A non-empty list or `"unreadable"` means not checked (shallow).
  2. The add-commit lookup must **not** use `--first-parent` (Extra research 1). Fixture (a) catches it (mutation M4).
  3. If `scripts/check_pipeline.py` is absent from the anchor commit's tree, the result is still strict INCOMPLETE as 03 says, but with its own text (`anchor <sha7> has no scripts/check_pipeline.py`), not `git failed`. The two have different causes. Tell them apart with `git ls-tree --name-only <A> -- scripts/check_pipeline.py`: exit 0 with empty output means absent, exit != 0 means failed.
  4. `RULE NOT SEEN:` without git or in a shallow clone prints `not checked (no git)` / `not checked (shallow clone; run git fetch --unshallow)`. This follows the form of the LOG TIME and INBOX lines and replaces 03 step 3's appended note. No anchor is computed in those cases, so the list part would always be empty.
  5. A pair (ID, rule) is listed only when the gate **removed** an INCOMPLETE reason. If the old rule still fails (fixture b), the entry stays INCOMPLETE with the old hint (`LOG_HINT_BEFORE`) and is not listed.
  6. The repo self-test (`test_repo_pipeline_has_no_skipped_items`) gets a loud `pytest.skip` when REPO is a shallow clone. Without it, 083 is strict there and the test would fail only in shallow clones, which is the RI-014 pattern. A visible skip names the cause. A silent `return`, as in `test_untracked_from_is_fixed`, would hide it.

## Extra research (with sources)
1. **The add commit must come from default history simplification, not `--first-parent`.** git-log, default mode: "If the commit was a merge, and it was TREESAME to one parent, follow only that parent." `--first-parent`: "follow only the first parent commit upon seeing a merge commit." [https://git-scm.com/docs/git-log] On PR #33 + main, HEAD's first-parent chain reaches 083's files through the merge b2f11b9, and that merge's tree has both constants. With `--first-parent`, the `--diff-filter=A` commit would be the merge, 083 would be "seen", and the bug would come back. Without it, git follows the main parent (TREESAME for that path) down to cfc0634. `_inbox_gate` already calls it this way (no `--first-parent`). Keep that exact call.
2. **Path absent vs git failed.** `git cat-file -e` gives zero "if <object> exists and is a valid object" [https://git-scm.com/docs/git-cat-file], but a non-zero exit does not say why. `git ls-tree <A> -- <path>` exits 0 with empty output when the path is absent, so it separates the two cases. That ls-tree behaviour is UNVERIFIED by command here, so I2 pins it with fixture (d2). If it does not hold, both cases fall back to the `git failed` text, which is still strict.
3. **The shallow flag can't be trusted alone.** rev-parse documents `--is-shallow-repository` only as: "When the repository is shallow print "true", otherwise "false"" [https://git-scm.com/docs/git-rev-parse]. The repo's own 079 tests pin the other cases: exit 129 when git can't give the flag, and a non-zero exit with "bad shallow line" on a malformed file. That is why change 1 reuses `_shallow_boundaries()`.
4. **Edge case R3 missed: the lazy gate in existing git fixtures.** Several existing tests build git repos with no `scripts/check_pipeline.py` and an item >= 076 whose I2 line fails the new rule, e.g. `test_recommitted_log_line_is_checked_against_new_commit` (`150 | see 05 | tests 1/1`). In those repos the gate gets the absent-path result. Its INCOMPLETE entry gains the anchor text, and the item stays INCOMPLETE (strict). Those tests assert only `LOG TIME:` lines, so they stay green. I2 confirms this with the full suite. The plain tmp_path fixtures (`test_i2_tests_field_cutoff`, `test_old_06_without_round_headers_unchanged`, `test_malformed_log_line_names_expected_format`, `test_pass_without_sent_back_none_is_incomplete`) have no git and keep their exact text, apart from the new `RULE NOT SEEN: not checked (no git)` line, which none of them asserts against.

## Files to create/change
3 files (plus I2's own work/084/05).

1. `scripts/check_pipeline.py`
   - Module docstring: a new paragraph for item 084 covering the anchor rule (the commit that added 05 or 06, its tree's `^CONST = ` line), the `RULE NOT SEEN:` line and its `not checked` forms, and the known or decided gaps. Row 4 `WHOLE_DIFF_FROM` is not gated (known gap, 0 items today). Row 6 (06 verdict vs last I3 line) stays at `CHECKLIST_FROM` by decision. Rows 1-3 stay numeric. `write_log` stays numeric.
   - New constant `RULE_FILE = "scripts/check_pipeline.py"`, the file whose tree copy is read.
   - New `_anchor_env() -> str | None`: None when git can answer, `"no git"` when `_git` gives None, `"shallow clone; run git fetch --unshallow"` when `_shallow_boundaries()` is a non-empty list or `"unreadable"`. Computed once in `main()` and passed down. No call is made for items below either cutoff.
   - New `_rule_seen(item_dir, step, const, env) -> tuple[bool | None, str]`. `step` is `"05"` or `"06"`. It returns:
     - `(None, "")` when env is not None, HEAD is unborn, or `git log --no-renames --diff-filter=A --format=%H -1 -- work/<ID>/<STEPS[step]>` is empty (not committed). All of these keep the strict rule.
     - `(None, "<step> anchor: git failed (item 084)")` when that log, the ls-tree, or `git show <A>:RULE_FILE` fails. That is strict plus an INCOMPLETE entry.
     - `(None, "<step> anchor <sha7> has no scripts/check_pipeline.py (item 084)")` when the path is absent. Same treatment.
     - `(True, sha7)` or `(False, sha7)` from `re.search(rf"^{const} = ", text, re.M)`, one constant at a time and never a combined pattern.
     - No `--first-parent`. Every git call goes through 081's helper.
   - `log_fields_ok(agent, item, fields, new_rule=True)`: I2 uses I2_BEFORE when `int(item) < TESTS_FORMAT_FROM or not new_rule`. `log_hint(agent, item, new_rule=True)` does the same for `LOG_HINT_BEFORE`. `write_log` calls both with the default, so it stays numeric (03 step 2).
   - `incomplete(item_dir, logs=Path("logs"), env=None, not_seen=None)`. The return type is unchanged (a list), and `not_seen` is an optional list the function appends to.
     - **I2 (TESTS gate).** After `bad` is computed, if `"I2" in bad` and `int(ID) >= TESTS_FORMAT_FROM`, call `_rule_seen(item_dir, "05", "TESTS_FORMAT_FROM", env)`.
       - False: re-check every I2 line of the item with `new_rule=False`. If all pass, drop I2 from `bad` and append `(ID, "05", sha7, "TESTS_FORMAT_FROM", "076", "I2_BEFORE")` to `not_seen`. If any fails, keep I2 and use the old hint.
       - True or None: unchanged. A non-empty note is appended as its own entry.
     - **06 verdict (VERDICT gate).** In the `int(ID) >= VERDICT_FROM` branch, the three checks are computed as today. Only if one would fire, call `_rule_seen(item_dir, "06", "VERDICT_FROM", env)`.
       - False: drop those entries, because below VERDICT_FROM there is no verdict-line check (gap y), and append `(ID, "06", sha7, "VERDICT_FROM", "071", "no Sent-back check")`.
       - True or None: unchanged, plus any note.
     - The verdict-vs-last-I3 cross-check (row 6) is untouched.
     - Items below the cutoffs make no git call.
   - `main()`: call `env = _anchor_env()` once, collect `not_seen = []`, pass both to `incomplete(d, env=env, not_seen=not_seen)`. Directly after the `INCOMPLETE:` print, print one of:
     - `RULE NOT SEEN: not checked (<env>)` when env is set,
     - `RULE NOT SEEN: <ID> (<step> added in <sha7> without <CONST> (<rule item>): judged by <old rule>; item 084)`, joined by `, `, with multiple pairs for one ID joined by `; ` inside its parentheses,
     - `RULE NOT SEEN: none`.

     The exit code expression is unchanged. Not-seen pairs do not add to `unfinished`, and git-failed or absent notes already are entries in it.
   - Scope lock (03 step 5): no change to `CHECKLIST_FROM`, `LOG_CHECK_FROM`, `TESTS_FORMAT_FROM`, `VERDICT_FROM`, `LOG_TIME_EXCEPT`, `WHOLE_DIFF_FROM`, the cross-check block, `LEGACY`, `PRE_A1_LINE`, `write_log`'s refusal, or `late_log_lines`.
2. `tests/test_pipeline_check.py`: new tests (below) and the self-test addition. No existing assertion is edited.
3. `.claude/commands/run-item.md`: one new line directly after the line that mentions `RULES BRANCH`: "If an urgent fix goes on main while `RULES BRANCH:` is not `none`, its 05 says so and names that branch (item 084); `RULE NOT SEEN:` will then list it once the branch merges main, if it fails a rule it never saw."

## Tests and checks
**Step 0 (read-only, I2 runs these BEFORE any edit, in /home/claude/cover-calls, after 081 has landed):**
```
git rev-parse --is-shallow-repository            # must print false (if true: git fetch --unshallow, then re-run)
git status --porcelain -- scripts/check_pipeline.py tests/test_pipeline_check.py   # note 081's state
for id in 071 072 073 074 075 076 077 078 079 080 081 082 083 084 085 086; do
  for f in 05-build-report.md 06-verification.md; do
    sha=$(git log --no-renames --diff-filter=A --format=%H -1 -- work/$id/$f) || { echo "$id $f GIT FAILED"; continue; }
    [ -z "$sha" ] && { echo "$id $f not committed"; continue; }
    git ls-tree --name-only "$sha" -- scripts/check_pipeline.py | grep -q . || { echo "$id $f ${sha:0:7} NO FILE"; continue; }
    tree=$(git show "$sha":scripts/check_pipeline.py) || { echo "$id $f GIT FAILED"; continue; }
    echo "$id $f ${sha:0:7} VERDICT_FROM=$(grep -c '^VERDICT_FROM = ' <<<"$tree") TESTS_FORMAT_FROM=$(grep -c '^TESTS_FORMAT_FROM = ' <<<"$tree")"
  done
done
python3 scripts/check_pipeline.py | grep -E '^INCOMPLETE:'     # baseline: names 083 only
```
Paste the table into 05. **Send back to I1 (stop, no edits) if any of these hold:**
- (i) 083 05 or 06 is not at cfc0634, or shows either constant >= 1. The anchor would not exempt 083, so the design fails. Fall back to a named closed exception (02 AGAINST 2) only as a recorded decision.
- (ii) 076 05 `TESTS_FORMAT_FROM` = 0, or 076 06 `VERDICT_FROM` = 0. The positive control is impossible.
- (iii) 071 06 `VERDICT_FROM` != 1 (03 step 0 check).
- (iv) Any line `GIT FAILED` or `NO FILE` for 071-079 or 083.
- (v) The baseline INCOMPLETE line names anything other than 083. Or the expected set differs from {083}, where expected = {items with the constant at 0 for that step} ∩ {items that fail that rule today}. 03 expects {073 (06), 083 (05, 06)} ∩ {083} = {083}.

**New tests in `tests/test_pipeline_check.py` (all `@NO_GIT` except (e2)):**
- `test_rule_not_seen_item_merged_beside_rules_branch` (a). Tmp repo, branch `main`:
  - `scripts/check_pipeline.py` = `"CHECKLIST_FROM = 41\n"`, plus item 150 (ALL, 06 `sent_back=None`, I2 log line written as `1 files changed | tests 9/9`, every other line from `_field`). Commit.
  - Branch `rules` from the first commit: the file gains `VERDICT_FROM = 71\nTESTS_FORMAT_FROM = 76\n`. Commit. Then item 151 with the same two defects. Commit.
  - Run 1 on `main` checkout: `RULE NOT SEEN:` names 150 with both pairs (05 TESTS_FORMAT_FROM (076), 06 VERDICT_FROM (071)), and `INCOMPLETE:` does not name 150.
  - Checkout `rules`, `git merge main` (the PR #33 + main shape). Run 2: `RULE NOT SEEN:` names exactly 150, and `INCOMPLETE:` names 151 for both the I2 format and `Sent back to: none`, but not 150.
  - All runs use `--untracked-from <root sha>`.
- `test_rule_not_seen_still_checks_old_rule` (b): as (a), but 150's I2 line is `tests 10/9`. 150 stays INCOMPLETE with the hint `"<n> files changed | tests <pass>/<total> (pass <= total)"`. RULE NOT SEEN holds only 150's 06 pair, not its 05 pair.
- `test_unseen_item_that_passes_is_not_listed` (c): item 152 on `main` with good lines (new I2 form and `Sent back to: none`) gives `RULE NOT SEEN: none`. This is the 073 case.
- `test_rule_anchor_git_failure_is_incomplete` (d1): through `_patched_git` (or 081's replacement), `log --no-renames --diff-filter=A` fails (exit 128). `_rule_seen` returns `(None, "05 anchor: git failed (item 084)")`, and `incomplete()` keeps the strict I2 reason plus that entry. Same for `show` failing.
- `test_rule_anchor_without_rule_file` (d2): a repo whose commit has no `scripts/check_pipeline.py` gives the entry `05 anchor <sha7> has no scripts/check_pipeline.py (item 084)`, still INCOMPLETE and not listed.
- `test_rule_not_seen_shallow_and_no_git` (e1, e2). The repo from (a), run 2, with `_shallow(repo, <rules commit>)`: `RULE NOT SEEN: not checked (shallow clone; run git fetch --unshallow)` and 150 INCOMPLETE (strict). `_unshallow` gives the control, 150 not INCOMPLETE. (e2, no git) a plain tmp_path with item 150 failing both: `RULE NOT SEEN: not checked (no git)`, and 150 INCOMPLETE with today's exact text.
- `test_rule_seen_positive_control_on_head` (f1): skip with a reason if git is missing or REPO is shallow. With `monkeypatch.chdir(REPO)`, `_rule_seen(work/076, "05", "TESTS_FORMAT_FROM", None)[0] is True`, `(076, "06", "VERDICT_FROM")` is True, and 083's two are False.
- `test_repo_pipeline_has_no_skipped_items` (f2, extended). At the top: `pytest.skip("REPO is a shallow clone: 083 is judged strictly (item 084); run git fetch --unshallow")` if `git rev-parse --is-shallow-repository` is not `false`. New asserts: the `RULE NOT SEEN:` line equals exactly `RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)` (exact set {083}), and `INCOMPLETE: none`. I2 prints the real line in 05 and pins the exact text it shows. The ID set must be {083}.
- `test_write_log_stays_numeric` (g): `--log I2 083 "2 files changed | tests 344/344"` in a tmp copy is still refused (exit 2). The gate never loosens new log lines.

**Mutations (I2 runs, I3 re-runs; each must fail the named test):**
- M1, gate off (`incomplete` ignores `_rule_seen`, numeric only): (a) and (f2) fail.
- M2, the pattern in `_rule_seen` becomes `rf"^{const}_X = "`: (f1) fails (076 not seen). (a) run 2 fails too, because 151 would be exempted.
- M3, a failed read is treated as not seen (`(False, ...)` on a git failure): (d1) fails.
- M4, `--first-parent` added to the add-commit `git log`: (a) run 2 fails (150 seen through the merge).
- M5, `_anchor_env` returns None in a shallow clone: (e1) fails.

**Checks:** the full suite (`python3 -m pytest -q`) passes. `python3 -m py_compile scripts/check_pipeline.py` passes under python3.11 if present (RI-008). 081's call-site lint test passes with the new calls. `python3 scripts/check_pipeline.py` on this branch prints `INCOMPLETE: none` and `RULE NOT SEEN: 083 (...)`, with exit code unchanged apart from items 080-086 that are still in progress.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Fact-check row R1 F13 / R2 FOR 1c correction (073 = 0 at its add commits; per-constant counts) | Step 0 table counts each constant separately; send-back (iii) and (v); `_rule_seen` matches one constant at a time |
| Fact-check row R2 FOR 2 correction (lazy gate, 54 calls max, 4 on HEAD) | `incomplete()` calls `_rule_seen` only when a new-rule check would fire; items below the cutoffs make no git call |
| Fact-check row R2 FOR 3d correction (exact set {083} + positive control) | (f1) positive control on 076/083; (f2) exact set {083}; M2 |
| Fact-check row R2 AGAINST 3 correction (detect shallow first) | `_anchor_env()` via `_shallow_boundaries()` before any `--diff-filter=A` (change 1); (e1); M5 |
| Fact-check row R1 F15 removed (048) | DROPPED: 048 < 71, never reached; `LOG_TIME_EXCEPT` unchanged (scope lock) |
| Decision: exempt set and per-constant precision | Listed only when the gate removed a reason (change 5); (b), (c), (f2) |
| Step 0 read-only per-constant check | Tests and checks, Step 0 commands + send-back (i)-(v) |
| Step 1 `_rule_seen` helper | Files 1: `_rule_seen`, `_anchor_env`, `RULE_FILE` |
| Step 2 `incomplete()` gate; `log_fields_ok`/`log_hint` optional input; `write_log` numeric | Files 1: `incomplete`, `log_fields_ok(..., new_rule)`, `log_hint(..., new_rule)`; (g) |
| Step 3 `RULE NOT SEEN:` line, docstring with gaps | Files 1: `main()` print after INCOMPLETE; docstring paragraph; unknown-anchor note replaced by `not checked (<env>)` (change 4) |
| Step 4 run-item.md line | Files 3 |
| Step 5 scope lock | Files 1, scope-lock list; I3 checks the diff |
| Step 6 tests (a)-(f), M1-M3 | Tests (a)-(f2), M1-M3, plus M4 (first-parent) and M5 (shallow) |
| Step 7 done check | Checks: `INCOMPLETE: none`, `RULE NOT SEEN: 083 (...)`, self-test green |
| Missing input: git absent | (e2), `RULE NOT SEEN: not checked (no git)` |
| Missing input: shallow history | (e1) |
| Missing input: 05/06 not committed | `_rule_seen` returns `(None, "")`, strict; covered by (e2)'s plain fixture and by the in-progress items 080-086 on this branch |
| Missing input: git log/show exit != 0 | (d1) |
| Missing input: RULE_FILE absent from anchor tree | (d2), own text (change 3), still strict |
| Missing input: constant absent | the "not seen" result itself: (a) |
| request.md L13: anchor "request.md first reached main after the rule's commit" | DROPPED: replaced by the add-commit tree test (03 Fact check R1 F12: it exempts 073 and every open-rules-branch item) |
| request.md L13: text `not checked (<rule> reached main after <ID>)` | DROPPED: replaced by the `RULE NOT SEEN:` wording (02 FOR 2; the anchor differs) |
| request.md L13: "same item after the rule merges -> flagged" | DROPPED: under the 03 anchor 083 stays unflagged after the merge (it was never built under the rule). The fixture instead flags the item built on the rules branch (151) after the merge |
| request.md L13: mutation "cutoff back to item number" | M1 |
| request.md L17: Done looks like | Checks + (f2) |

## Guardrail tests
- Feasibility: VERDICT gate reaches 10 items with a committed 06 on HEAD (071-079, 083), and the TESTS gate 5 (076-079, 083), counted from work/ files on this branch. I2 re-counts in step 0 → the suppressed set {083} is pinned by (f2). Fixture counts: 2 items per repo, 1 exempt, 1 checked → (a).
- Feasibility: positive control, 076 at 2 of 2 constants → (f1).
- Missing inputs: git → (e2); shallow history → (e1); git failure → (d1); rule file absent → (d2); 05/06 uncommitted → strict path, the existing plain fixtures unchanged (`test_i2_tests_field_cutoff`, `test_old_06_without_round_headers_unchanged`).

## Expected result
- 3 files changed. On this branch, `check_pipeline.py` prints `INCOMPLETE:` without 083 and `RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)`.
- `test_repo_pipeline_has_no_skipped_items` passes in a full clone and is skipped with a reason in a shallow one.
- The full suite passes, with the count as printed by pytest (expected: today's count plus about 9 new tests).
- M1-M5 each fail at least one named test.
- No other item changes INCOMPLETE status, and no existing assertion changes.
- 084's own I2 line uses the new format, because 084's 05 is added after the rule code.
