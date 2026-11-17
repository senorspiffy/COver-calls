# Work item 069
Type: IDEA
Scope: FULL
Opened by: person
Date: 2026-11-17

## What we want
The daily audit also checks, every day, whether another project sent this project something to test or try, and acts on it.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
Person, in the "Covered-call daily audit" thread, 2026-11-17 17:34 UTC: "Also daily check to make sure another project didn't send you guys something to test or try".
Where messages arrive today:
- Project files: /mnt/project-files/project-inbox/to/covered-calls/ (format and status rules in project-inbox/README.md). 2026-11-17: 2 files, both `status: read`, `priority: fyi`, both written by this project.
- Hub repo senorspiffy/Updated-folder-for-claude-projects: shared-facts.md and projects/*/inbox.md. 2026-11-17: no line addressed to covered calls (every covered-calls hit is "from Selling covered calls"). There is no projects/covered-calls/ folder.

## Done looks like
.claude/commands/daily-audit.md (and the a1-auditor daily-review steps) add an inbox step before the log review: read unread files in project-inbox/to/covered-calls/ and new hub lines addressed to this project; turn each test/try request into an IDEA work item (evidence = the file/line) run with the day's items; list FYI notes; set handled messages to read/done per the inbox README. The daily report template gets an "Inbox" section at the top ("nothing new" when empty). The scheduled task prompt can't be edited from a thread, so the rule must live in the repo.
