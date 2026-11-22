# Plan

**Feature:** per-label annotation counts for a CVAT task, served by a new API endpoint and shown as a graph on a new page.

## Start and environment

- Acknowledged (timer start): **21 Nov 2026, 20:00 PKT**. Deadline: **22 Nov 2026, 04:00 PKT**.
- I started the actual work late: this plan was committed at 23:19, 3 h 19 min after acknowledging. The plan is sized to the ~4 h 40 min that were left.
- Environment setup (fork, Docker images, COCO import) was done before acknowledging, as Section 2 of the brief says that waiting time does not count.
- Machine: MacBook Pro 16" 2019, 2.6 GHz 6-core Intel Core i7, 16 GB RAM, macOS Tahoe 26.5.2. Docker Desktop with 8 CPUs, ~7.6 GiB memory.
- CVAT commit: `d4d08dedb5ad7c5e980c0bc7319a7f5587365dad` (fork default branch `develop`; work on `dev-test01`).
- Data: COCO 2017 val, first 500 images by file name, 3541 annotations, 80 labels, imported as Task #1 (one job, 500 frames).

## Steps (in order)

| # | Step | Brief items | Budget |
|---|---|---|---|
| 1 | Write this plan and the Definition of Done, commit them first | — | 20 min |
| 2 | Django app `test`: endpoint returning counts per label for a task, counted in the database with one aggregate query | 1 | 45 min |
| 3 | Reuse CVAT's own auth and task permission check: 401 without login, 403 without access to the task | 5 | 25 min |
| 4 | Verify counts against `instances_subset.json` and the status codes with curl | 1, 5 | 15 min |
| 5 | UI page for a task: calls the endpoint, draws a bar chart with the chart library CVAT already ships | 2, 3 | 75 min |
| 6 | Empty state and failed-request state on the page | 4 | 25 min |
| 7 | Objective MO-1: endpoint response time, 5 measured runs, median and spread | 6 | 25 min |
| 8 | Finish the three documents with evidence, push, PR inside my fork | 10 | 30 min |
| 9 | Loom recording (under 5 minutes) and submission email | — | 30 min |

Hard stop for feature work: **4 hours after this plan is committed** (03:19 PKT). Whatever state the code is in, the remaining time goes to documents, PR and recording.

## Decided up front not to do

- **Item 7 (filter or grouping):** only if steps 2–7 are done with evidence and at least 1h15m is left.
- **Items 8–9 (WebSocket live update and reconnect):** skipped. CVAT at this commit has no WebSocket layer (`cvat/asgi.py` is plain Django ASGI, no Channels in requirements), and annotation saves go through `bulk_create` in `cvat/apps/dataset_manager/task.py`, so Django `post_save` signals would not fire. Adding a WebSocket stack and a reliable change hook does not fit in the time left.

## Changes to this plan

- **Expected total changed from 3541 to 3953 (after commit `98a4601ce`).** The endpoint returned 3953, not the 3541 COCO annotations. CVAT's COCO import stores each part of a multi-part COCO polygon as its own `LabeledShape`. Counting polygon parts in `instances_subset.json` gives exactly 3953, and every one of the 80 labels matches the endpoint (0 differences). The endpoint counts what CVAT stores (shapes), so the DoD check now compares against polygon parts.
- **Step 2 and 3 landed in one commit** (`98a4601ce`): the permission check is three lines in the same view, and the endpoint should never exist without it.
- **Measurement uses a token, not basic auth.** Basic auth runs Django's password hasher on every request, which would dominate the time and say nothing about this endpoint. Recorded in `OBJECTIVES.md`.
- **Item 7 done after all.** After the documents were drafted there was still time, so I added grouping by annotation type (API `by_type` per label, and a Total / By annotation type toggle with a stacked chart). Why this grouping: in COCO, normal objects are polygons but crowd regions are masks, and one crowd mask covers many objects. Splitting the count by type shows how much of a label is individual objects and how much is crowd masks, which matters when the data is used for training. In other tasks it also shows a label annotated inconsistently (some boxes, some polygons). Check on Task #1: 3916 polygons + 37 masks = 3953, and 37 equals the number of `iscrowd=1` annotations in `instances_subset.json`.

## Decision record (brief item 10)

**1. Count in the database, not through CVAT's annotation loader.**
Taken: three `GROUP BY label` queries (`LabeledShape`, `LabeledTrack`, `LabeledImage`) in `count_annotations_per_label`, `cvat/apps/test/views.py`.
Rejected: loading task annotations through CVAT's dataset manager (what `GET /api/tasks/{id}/annotations` uses) and counting in Python.
Cost of rejecting it: my query has its own definition of "an annotation" (annotation jobs only, no skeleton sub-points, a track counts once). If CVAT adds a new annotation kind or changes these rules, this endpoint will not follow automatically.

**2. Explicit `TaskPermission` check instead of CVAT's viewset permission pattern.**
Taken: a plain DRF `APIView` with `IsAuthenticated` (401) and `TaskPermission` with scope `view:annotations` (403), the same scope CVAT uses for reading a task's annotations.
Rejected: a `ViewSet` with `iam_permission_class` going through CVAT's `PolicyEnforcer`, plus a new OPA scope and Rego rule.
Cost of rejecting it: the access-token plugin checks that `PolicyEnforcer` runs (`cvat/apps/access_tokens/permissions.py`) are not applied to this endpoint, so a restricted access token is checked only by the task permission, not by its own token rules.

**3. Count shapes, not objects.**
Taken: one count per stored shape (3953 for Task #1).
Rejected: merging the parts of one object (shapes sharing a `group`) into one count (3541).
Cost of rejecting it: the number differs from what someone reading the COCO file expects, so it needs the explanation above.

**4. No WebSocket (items 8–9).** Reasons above under "Decided up front not to do".
Cost: the graph only updates on page load or Retry.
