# Definition of Done

Written before any code. A line counts as done only with evidence beside it (command output, number, screenshot link or commit hash).

## Floor (brief items 1–4)

- [ ] `GET` endpoint returns, for a task, each label with its annotation count. Evidence:
- [ ] The counting happens in the database (one aggregate query), not by loading annotations into Python. Evidence (file:line):
- [ ] Counts for Task #1 match the counts computed from `instances_subset.json` (total 3541). Evidence:
- [ ] A page in the web UI loads the counts for a task and shows them as a graph. Evidence (screenshot):
- [ ] The page shows a clear empty state for a task with no annotations. Evidence (screenshot):
- [ ] The page shows a clear error state, with retry, when the request fails. Evidence (screenshot):

## Access (brief item 5)

- [ ] Request without login is refused with 401. Evidence:
- [ ] Logged-in user without access to the task (`outsider`) is refused with 403. Evidence:
- [ ] Owner gets 200. Evidence:

## Objective (brief item 6)

- [ ] Objective MO-1 has a target written before measuring. Evidence: `docs/OBJECTIVES.md`
- [ ] MO-1 measured 5 times on my machine, raw output pasted, median and spread reported. Evidence:
- [ ] Target met, or missed with the reason. Evidence:

## Presentation

- [ ] Backend change is contained in `cvat/apps/test`; existing files touched only to register the app, the URL and the UI route. Evidence (PR file list):
- [ ] No dead code, commented-out code, debug output or stray files. Evidence (final diff review):
- [ ] Commits are small, in order, plan first. Evidence (`git log --oneline`):
- [ ] PR opened from `dev-test01` into `develop` of my own fork only. Evidence (PR link):

## Not finished, and why

_Filled in at the end._
