# 02 Improvements - 094
## What past logs say
- RI-009 (logs/recurring-issues.md L108-116) is GUARDED with 3 occurrences. Its 2026-11-22 entry names this item: "single-branch clone hides open branches → 094" (near miss, not counted). The 037 guardrail (`--next-id` over open branches, ID CLASH) assumes that `git branch -r` lists every open branch. 094 is the case where that assumption fails.
- RI-014 (L152-158) is OPEN. Its 2026-11-24 entry lists 094 as a near miss. The family rule from 081 is "failed git never none" (scripts/check_pipeline.py L1401-1411, `_git_ok`). 094 is the same shape, but git does not fail here. It succeeds and answers from a refspec that hides refs, so `_git_ok` cannot catch it.
- The reproduction is logs/audit/2026-11-22-090.md L102-120 (F2, git 2.43.0, real clones):
  - sb2 (`--single-branch`) and d1s (plain `--depth 1`) both print `OPEN BRANCHES: none` and `092`. The full clone prints 093.
  - It still happens after `git fetch --unshallow`, and `git fetch origin` still shows only origin/main.
  - A1's proposed recovery is `git remote set-branches origin '*' && git fetch origin`.
  - A1 also noted that the proxy refused git-scm.com (L26-28). This R2 run did reach git-scm.com and raw.githubusercontent.com.
- 090/02 already flagged this case as out of scope: "A single-branch shallow clone (01 B11) silently hides open branches and their IDs from `--next-id` (RI-009) ... Send it to A1 as a new item" (work/090/02-improvements.md L104). 090's fixture helper always adds `--no-single-branch` (tests/test_pipeline_check.py L4417). That is why 090's tests never saw this.
- Overlap with an in-flight item: 095 (work/095/request.md, EFFICIENCY, RI-014) changes the same OPEN BRANCHES print block (scripts/check_pipeline.py L2011-2029) and the same a1-auditor.md L22 not-checked sentence.
- Language precedent: 079, 084, 086 and 090 cover the same checker and the same git-tool topics, and all were logged `languages: N/A` (logs/research/2026-11-21.md L9, work/090/02 L80).

## 3 ways FOR
1. **Pick A1's recovery sentence, `git remote set-branches origin '*' && git fetch origin`, not the request's `git config remote.origin.fetch ...`. This closes R1's UNVERIFIED finding 19 from git's source.**
   - What `set-branches` does, from git master source (https://raw.githubusercontent.com/git/git/master/builtin/remote.c):
     - Without `--add`, `set_remote_branches()` first clears every fetch line: `if (!add_mode && remove_all_fetch_refspecs(key.buf))`, which calls `repo_config_set_multivar_gently(..., key, NULL, NULL, CONFIG_FLAGS_MULTI_REPLACE)`.
     - `add_branch()` then writes `+` followed by `refs/heads/<branch>:refs/remotes/<remote>/<branch>`.
     - With `<branch>` = `*`, that is exactly the default `+refs/heads/*:refs/remotes/origin/*`. Any negative `^` lines and extra branch lines are removed too.
   - Why the `git config` form is worse: git-config fails when "you try to unset/set an option for which multiple lines match (ret=5)", and "By default, this command refuses to write multi-valued config options" (https://git-scm.com/docs/git-config). So `git config remote.origin.fetch '+refs/heads/*:...'` errors in exactly the multi-line and `^` cases that R1's findings 11-12 say the check must flag. It does not remove a `^` line that is set separately either.
   - Version caveat: the code above is git master. Its behaviour on git 2.43.0 is UNVERIFIED. The real-clone fixture must run the sentence on a two-line clone and a `^` clone, then assert the result with `git config --get-all remote.origin.fetch`. That also pins the claim.
   - Quote `'*'` in the rule text, so a shell in a directory with files does not expand it.
2. **Coverage rule: read every value, compare exactly, and treat anything else as unknown, never as full. Expose the result as one constant compared by equality, as 090 did with SHALLOW_TEXT.**
   - Read: `git config --get-all remote.origin.fetch`. The `git config get` subcommand only arrived with the 2.46 change ("operation mode options (like "--get") ... deprecated and replaced with subcommands", https://www.kernel.org/pub/software/scm/git/docs/RelNotes/2.46.0.adoc), and the repo runs 2.43.0. So the mode option is the form that works on both.
   - "Full" means all three of these hold:
     - exit 0;
     - at least one non-empty value whose text, after removing one leading `+`, equals `refs/heads/*:refs/remotes/origin/*`;
     - no value starts with `^`.
   - Everything else is single-branch: named branches only, several lines, negative lines, a different destination, empty output with exit 0, or exit not in (0, 1). The empty-output case is the catch-all monkeypatch hole in R1 finding 25.
   - The output must be built from a module constant, for example `SINGLE_TEXT = "single-branch clone; run git remote set-branches origin '*' && git fetch origin"`. main() and check_handoff then test it with `==`, like `shallow = env == SHALLOW_TEXT` (L1958), not with a substring test (RI-012).
   - Exit 1 means the key is absent (git-config: "Returns error code 1 if key is not present"). Keep today's path for that case. Two current tests need it:
     - (h1) test_open_branches_none_line (L2594-2599): a repo with no remote says `none`, exit 0.
     - (d3) test_main_ahead_exact_ref_only (L2547-2558): refs/remotes/origin/main/x exists with no origin at all and must still be listed.
     - Write this down as a known gap in the docstring: with no origin fetch key, `git fetch` cannot hide or add anything.
3. **Make the refusal and the not-checked state reach every reader that would otherwise say "none". The harm is the ID, so put the hard stop there.**
   - `--next-id` (L1856-1870) must check coverage before the branch loop and return `(None, SINGLE_TEXT)`. main() L1936-1939 then refuses with exit 2 through the existing 081 path, with no new print code.
   - Fix that path's fixed tail, "Fix the clone (git fetch origin) and re-run", or make it depend on the reason. As written it gives the wrong recovery, because F2 shows that `git fetch origin` does not help (090 audit L110).
   - ID CLASH, IN PR and RULES BRANCH (L2002-2034) must print `not checked (see OPEN BRANCHES)`. `ID CLASH: none` in a single-branch clone is exactly the 037 failure (RI-009 occurrence 3).
   - check_handoff `_branch_with_handoff` (scripts/check_handoff.py L96-100) already maps a str to `(None, why)`. If `open_branches()` returns SINGLE_TEXT as a str, `--all` gets "not checked" for free.
   - Mutations that should each fail a named test:
     - (m1) coverage check returns "full" always: the sb fixture fails.
     - (m2) the `^` test is removed: the negative-refspec fixture fails.
     - (m3) only the last value is read (plain `--get`): the two-line fixture (`+refs/heads/main:...` after the glob, or the reverse) fails.

## 3 ways AGAINST
1. **Exit-code trap. Reusing the 081 str path makes every plain `--depth 1` clone exit 1. A separate sentinel makes it exit 0 with three checks off.**
   - Reasoning chain from the code:
     - main() L2086 includes `isinstance(branches, str)` in the failure condition. If `open_branches()` returns SINGLE_TEXT as a str, every single-branch run exits 1.
     - A plain `--depth 1` clone is single-branch ("Implies `--single-branch`", https://git-scm.com/docs/git-clone).
     - So tests L958, L1062 and L2082 (plain `--depth 1`, `assert code == 0`) all flip.
     - check_handoff `--all` would also exit 1 there (test h2 at L2602: a str is "not checked and exit 1").
   - The other way: a new non-str sentinel with exit unchanged follows the 090 precedent for not-checked lines (test L4450). But it leaves exit 0 while OPEN BRANCHES, ID CLASH and IN PR are unknown. That is the RI-002 shape for anyone who reads only the exit code.
   - Fix: decide on purpose and pin it.
     - My lean: exit unchanged for the main check (090 precedent; the three tests stay green, with an added assert on the new line), and exit 2 for `--next-id` (the request).
     - check_handoff `--all` needs its own explicit decision, because it currently turns any str into exit 1.
     - Put the choice in the PR, because run-item L12 lists the lines that may say "not checked".
2. **A full refspec does not prove the refs are there. Adding a network check brings a version trap and a new failure path.**
   - A clone that runs `set-branches origin '*'` but never `git fetch` has the full refspec and still no origin/<branch> refs. The check then says `none` again.
   - Stale refs can only over-report (01 finding 21), but missing refs under a full refspec under-report. That is the same silent `none`.
   - The obvious backstop, `git ls-remote --branches origin` (01 finding 20), has two problems:
     - It is a 2.46 option: ""--branches" replaces "--heads"" (RelNotes 2.46.0). On the repo's 2.43.0 it is probably unknown. That is my inference, and it is UNVERIFIED on 2.43. `--heads` is deprecated but present.
     - It needs the remote to be reachable. Agents work through a proxy that has refused hosts before (090 audit L26-27).
   - Fix:
     - Do not add ls-remote in this item.
     - Write the never-fetched gap in the docstring and in the rule sentence ("then `git fetch origin`" is part of the recovery).
     - If a later item adds ls-remote, use `--heads`, or pick the option by version, and make any failure "not checked".
3. **Cost and collision: a near miss with 0 real occurrences touches RULE_PATHS, the shared UNSHALLOW sentence and 095's lines.**
   - The request says it is a near miss, not counted (request L15).
   - The rule text is a hole of its own. The UNSHALLOW sentence (pinned once in three files, tests/test_pipeline_check.py L3707-3716) tells agents to `git fetch --unshallow`, "then test again. If it is still true, report ... OPEN BRANCHES ... as 'not checked'".
     - After unshallow the flag is false, so the sentence lets an agent in sb2 report `OPEN BRANCHES: none`.
     - A new single-branch sentence needs its own count-1 pin. Changing UNSHALLOW itself breaks 091's pin.
   - 095 edits the same print block (L2011-2029) and the same a1-auditor.md L22 sentence. Built in parallel, the two items conflict, or one silently drops the other's line.
   - scripts/check_pipeline.py and .claude/ are RULE_PATHS, so the person's OK is needed at PR review.
   - Fix:
     - Build 094 on top of 095, or 095 on top of 094 (RULES BRANCH rule, item 049).
     - Add a separate sentence next to UNSHALLOW, with its own pin, rather than editing UNSHALLOW.
     - Keep the code to one coverage function plus three call sites, each with a named test.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 094 is a BUG fix inside this repo's pipeline checker: how it reads its own clone's fetch refspec, plus a recovery sentence in its rule files. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git tool behaviour, cited above to the official English docs (git-scm clone/fetch/config/remote, the 2.46.0 release notes) and to git's source (builtin/remote.c). This follows 079, 084, 086 and 090, which cover the same checker and the same kind of fact and were all logged `languages: N/A`.

## Holes to watch out for (summary)
- Read all values (`--get-all`). Plain `--get` returns the last value only, so the order of lines decides the answer.
- `+` is optional. A `^` line negates the glob. Empty output with exit 0 is unknown. Exit 1 (no key) keeps today's path, so h1 and d3 stay green.
- Comparing against the literal `+refs/heads/*:refs/remotes/origin/*` would call a valid no-`+` refspec single-branch (01 finding 9). Strip one `+`, then compare.
- Use `git config --get-all`, not `git config get --all`, which needs git 2.46 or later. Use `ls-remote --heads`, not `--branches`, if ls-remote is ever used.
- The recovery is `git remote set-branches origin '*' && git fetch origin`. Per source it clears all fetch lines. The `git config` form exits 5 when several lines exist. Pin the result on git 2.43 in the fixture (two-line case and `^` case).
- Change `--next-id`'s refusal text "Fix the clone (git fetch origin)" for this reason. `git fetch origin` does not fix it (090 audit L110).
- ID CLASH, IN PR and RULES BRANCH must not say `none` in this state. check_handoff `--all` needs an explicit exit decision.
- Pin the exit code in the single-branch fixture, not just the text. Decide whether plain `--depth 1` tests L958, L1062 and L2082 stay exit 0, and add the new line's assert to them.
- The fixture must be a real clone: `git clone --single-branch` and plain `--depth 1`, with an open branch that holds work/<n>. `_clone` (L4417) cannot be reused as-is, because it forces `--no-single-branch`.
- After `set-branches` with no fetch, the refspec is full and the refs are missing, so the output is a silent `none`. Write this down as a known gap.
- The UNSHALLOW sentence lets an agent who unshallowed a single-branch clone report OPEN BRANCHES `none`. Add a separate pinned sentence. Build order with 095, which uses the same lines.
- Use an equality-compared constant for the not-checked text, never a substring test (RI-012).

Log fields: 3 for / 3 against | languages: N/A
