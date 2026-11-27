# Test Summary Report — Vault (`vault/`)

- **Phase:** Phase 5/5 — Summary Report
- **Date:** 2026-11-27
- **Version:** 1.0
- **Build / Commit:** `09a555a`
- **Environment:** Local Windows (`Python 3.14.6`), `ThreadingHTTPServer` (`127.0.0.1`), isolated SQLite DB
- **Data Sources:** `qa-artifacts/vault/02-test-matrix.md`, `03-execution-notes.md`, `03c-accessibility.md`, `04-defects.md`

---

## 1. Executive Verdict: **Conditional Go** *(default thresholds — not yet confirmed)*

- **Met (Go criteria):** P0 Pass Rate `100%` (`6/6`), Open Blocker `0`, Open Critical `0`, Blocked cases `0`, Defects Fixed-not-Retested `0`, Permissions/Security P0 cases all Pass (`TC-AUTH-001..003, 006..007`, `TC-RBAC-001`).
- **Not meeting Go column (triggers Conditional Go):**
  - Overall Pass Rate `85.0%` (`17/20` non-informational cases; `< 90%` default Go/Conditional Go threshold — *note: 2 of 3 failures are against `approved default` or WCAG rather than formal spec*).
  - Open Major defects: `2` (`DEF-001`, `DEF-002`; `<= 3` allowed for Conditional Go).
  - RTM Coverage: `85.7%` (`6/7` full; `REQ-01` missing negative DB-error case).
- **Conditions for release:**
  1. Fix `DEF-001` (`POST /api/items` rejecting `title: null` with `400`) — Owner: `[Needs input]`, Due: `[Needs input]`.
  2. PO confirms `TC-RBAC-002` (whether `member` archiving `admin`'s item is intended) and `DEF-002` (rendering `url` in `GET /`).
  3. If conditions are not met before release: becomes **No-Go**.

*(This is QA's recommendation; the release decision belongs to the user/PO.)*

---

## 2. Execution Summary

*(Excludes `Informational` case `TC-RBAC-002` and `NF-PERF-01`/`NF-SEC-01` from Pass Rate per `release-gate-criteria.md`.)*

| Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|
| 20 | 17 | 3 | 0 | 0 | **85.0%** (`17/20`) |

### By Priority

| Priority | Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|---|
| **P0** | 6 | 6 | 0 | 0 | 0 | **100.0%** |
| **P1** | 10 *(+1 Info)* | 8 | 2 (`TC-ITEM-004`, `TC-UI-001`) | 0 | 0 | **80.0%** |
| **P2** | 4 | 3 | 1 (`TC-A11Y-001`) | 0 | 0 | **75.0%** |
| **P3** | 0 | 0 | 0 | 0 | 0 | N/A |

### Informational Observations (excluded from Pass Rate)
- `TC-RBAC-002`: `member` (`bob`) archived `admin`'s item (`PATCH /api/items/{id}/archive` -> `200`).
- `NF-PERF-01`: 50 sequential `GET /api/items` -> `p50=1.43ms`, `p95=1.94ms`, `max=24.45ms`.
- `NF-SEC-01`: No HTTP security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `Cache-Control`); no `429` rate limiting on 10 failed logins.

---

## 3. Defect Statistics

| Severity | New | Open | Fixed | Re-test | Closed | Total |
|---|---|---|---|---|---|---|
| Blocker | 0 | 0 | 0 | 0 | 0 | 0 |
| Critical | 0 | 0 | 0 | 0 | 0 | 0 |
| **Major** | 2 | 0 | 0 | 0 | 0 | **2** (`DEF-001`, `DEF-002`) |
| **Minor** | 1 | 0 | 0 | 0 | 0 | **1** (`DEF-003`) |
| Trivial | 0 | 0 | 0 | 0 | 0 | 0 |

---

## 4. Requirement Coverage (RTM)

- **Total Requirements:** 7
- **Fully Covered:** 6 (`REQ-02`..`REQ-07`)
- **Missing Negative:** 1 (`REQ-01` — DB-corrupt/unmigrated health check)
- **With Failed Cases:** 2 (`REQ-04` via `DEF-001`, `REQ-07` via `DEF-002`, `DEF-003`)

---

## 5. Residual Risks & Next Actions

- **Residual Risks:** Live keyboard/screen-reader accessibility checks (`03c-accessibility.md`) are `Not Run`; `PATCH /api/items/{id}/archive` allows cross-user archiving (`TC-RBAC-002`); no login rate limiting (`NF-SEC-01`).
- **Next Actions:** Developer to fix `DEF-001` (and `DEF-002`/`DEF-003` if confirmed by PO); QA to re-test and run `qa-regression-planner` on the fix commit.

---

## 6. Missing Data / Assumptions

- Formal SRS/SLA thresholds: `[Needs input]` (all requirements inferred from `vault/` code; default release-gate thresholds used).
- Owner and due dates for Conditional Go items: `[Needs input]`.
