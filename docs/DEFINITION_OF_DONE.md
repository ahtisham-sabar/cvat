# Definition of Done

Written before any code (commit `2d4855119`). A line counts as done only with evidence beside it.

## Floor (brief items 1–4)

- [x] `GET` endpoint returns, for a task, each label with its annotation count. Evidence: `GET /api/test/tasks/1/annotation-counts` → 200, body starts `{"task_id": 1, "total": 3953, "labels": [{"id": 1, "name": "person", "count": 1217}, {"id": 57, "name": "chair", "count": 227}, ...` (commit `98a4601ce`)
- [x] The counting happens in the database, not by loading annotations into Python. Evidence: `cvat/apps/test/views.py`, `count_annotations_per_label`: `values_list("label_id").annotate(count=Count("id"))`, one `GROUP BY` query per annotation kind
- [x] Counts for Task #1 match the source data. Evidence: comparison against `instances_subset.json` (see "Changes to this plan" in `PLAN.md` for why polygon parts, not COCO objects):
  ```
  COCO objects: 3541
  COCO polygon parts: 3953
  API total: 3953
  Labels that differ: none
  ```
- [x] A page in the web UI loads the counts for a task and shows them as a graph. Evidence: `/tasks/1/annotation-counts`, "3953 annotations across 78 labels (2 labels have none)", screenshot "Graph" in the PR description (commit `9cfebaab9`)
- [x] The page shows a clear empty state for a task with no annotations. Evidence: Task #2 (2 images, no annotations) shows "This task has no annotations yet", screenshot "Empty state" in the PR description
- [x] The page shows a clear error state, with retry, when the request fails. Evidence: `/tasks/99999/annotation-counts` shows "Could not load annotation counts / No Task matches the given query." with a Retry button, screenshot "Error state" in the PR description

## Access (brief item 5)

Same codes as CVAT's own `GET /api/tasks/1` (checked first: 200 / 403 / 401).

- [x] Request without login is refused with 401. Evidence: `curl ... /api/test/tasks/1/annotation-counts` → `401`
- [x] Logged-in user without access to the task (`outsider`) is refused with 403. Evidence: `curl -u 'outsider:***' ...` → `403`
- [x] Owner gets 200. Evidence: `curl -u 'admin:***' ...` → JSON above

## Objective (brief item 6)

- [x] Objective MO-1 has a target. Evidence: `docs/OBJECTIVES.md` (median ≤ 200 ms)
- [x] MO-1 measured 5 times on my machine, raw output pasted, median and spread reported. Evidence: `docs/OBJECTIVES.md`, median 63.1 ms, spread 45.2–70.1 ms
- [x] Target met. Evidence: 63.1 ms ≤ 200 ms

## Presentation

- [x] Backend change is contained in `cvat/apps/test`; existing files touched only to register the app, the URL and the UI route. Evidence: existing files changed: `cvat/settings/base.py` (+1 line), `cvat/urls.py` (+3), `cvat-ui/src/components/cvat-app.tsx` (import + route), `cvat-ui/src/components/tasks-page/actions-menu-items.tsx` (menu entry)
- [x] No dead code, commented-out code, debug output or stray files. Evidence: final `git diff develop...dev-test01` reviewed; Python passes the repo's `black` and `isort` config
- [x] Commits are small, in order, plan first. Evidence: `git log --oneline develop..dev-test01`
- [x] PR opened from `dev-test01` into `develop` of my own fork only. Evidence: PR link sent in the submission email

## Not finished, and why

- **Item 7 (filter or grouping):** not started. Not enough time left after items 1–6 to build it end to end and still finish the documents and recording.
- **Items 8–9 (WebSocket):** skipped on purpose, see `PLAN.md` ("Decided up front not to do" and decision 4).
- **Automated tests:** none added for the endpoint. Verified by hand with curl and the COCO comparison above.
