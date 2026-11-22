# Plan

**Feature:** per-label annotation counts for a CVAT task, served by a new API endpoint and shown as a graph on a new page.

## Start and environment

- Acknowledged (timer start): **[FILL: date and time, PKT]**. Deadline: **[FILL: start + 8h]**.
- Work on the feature started about 3 hours after acknowledging. This plan is sized to the ~5 hours left.
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

Hard stop for feature work: **4 hours after this plan is committed**. Whatever state the code is in, the remaining time goes to documents, PR and recording.

## Decided up front not to do

- **Item 7 (filter or grouping):** only if steps 2–7 are done with evidence and at least 1h15m is left.
- **Items 8–9 (WebSocket live update and reconnect):** skipped. CVAT at this commit has no WebSocket layer (`cvat/asgi.py` is plain Django ASGI, no Channels in requirements), and annotation saves go through `bulk_create` in `cvat/apps/dataset_manager/task.py`, so Django `post_save` signals would not fire. Adding a WebSocket stack and a reliable change hook does not fit in the time left.

## Changes to this plan

_Timestamped notes added here during the work._

## Decision record

_Filled in at the end (brief item 10)._
