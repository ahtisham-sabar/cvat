# Objectives

## MO-1: Response time of the per-label count endpoint

| Field | Entry |
|---|---|
| ID | MO-1 |
| What is measured | Total time of `GET /api/test/tasks/1/annotation-counts` as seen by curl (`%{time_total}`), from the same machine through CVAT's Traefik on port 8080 |
| How | Authenticated with a CVAT API token (`Authorization: Token ***`). One warm-up request, not counted. Then 5 measured requests in a row. Raw output pasted below |
| Target | Median of the 5 runs **≤ 200 ms**. The page calls this endpoint once on load; under 200 ms the wait is not noticeable next to the rest of the page, and three `GROUP BY` queries over ~4k rows should be well inside it |
| Conditions | MacBook Pro 16" 2019, 2.6 GHz 6-core Intel Core i7, 16 GB RAM, macOS Tahoe 26.5.2. Docker Desktop, 8 CPUs, ~7.6 GiB memory. CVAT `d4d08dedb5ad7c5e980c0bc7319a7f5587365dad` + this branch, backend source mounted into the `cvat/server:dev` image. Task #1: 500 images, 1 job, 80 labels, 3953 shapes. Frontend dev server running, no other heavy apps |
| Not included | Browser rendering of the chart. First request after a container restart. Basic auth: it hashes the password on every request, which measures Django's password hasher rather than this endpoint, so a token was used instead |

## Raw output

```
$ for i in 1 2 3 4 5; do curl -s -o /dev/null -w "%{http_code} %{time_total}\n" -H "Authorization: Token $T" "$U"; done
200 0.047229
200 0.063112
200 0.070127
200 0.069323
200 0.045161
```

## Result

- Sorted (ms): 45.2, 47.2, 63.1, 69.3, 70.1
- **Median: 63.1 ms**
- **Spread: 45.2 – 70.1 ms** (range 24.9 ms)
- **Target met** (63.1 ms ≤ 200 ms).
