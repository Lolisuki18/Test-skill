# Test Matrix — Vault (`vault/`)

- **Phase:** Phase 2/5 — Test Matrix
- **Date:** 2026-11-27
- **Version:** 1.0
- **Status:** Approved
- **Requirement source:** `qa-artifacts/vault/01-test-plan.md` (`Approved`)

---

## 1. Counts Overview

- **Total Test Cases:** 21
- **By Priority:** P0: 6 | P1: 11 | P2: 4 | P3: 0
- **By Execution Type:** `Auto (API)`: 20 | `Manual`: 1

---

## 2. Test Case Table

| TC ID | Req/UC ID | Module | Title | Pre-condition | Test Steps | Test Data | Expected Result | Oracle | Priority | Execution Type |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-HLTH-001 | REQ-01 | Health | GET /health returns schema_version=1 | Server running with migrated DB | 1. Send `GET /health` | None | HTTP `200`, JSON `{"status": "ok", "schema_version": 1}` | code behavior (`vault/server.py:117-121`) | P1 | Auto (API) |
| TC-CLI-001 | REQ-01 | CLI | CLI --seed --migrate-only initializes DB | Empty temp path for `--db` | 1. Run `python -m vault --db <tmp> --seed --migrate-only` | `cli_qa.db` | Exit code `0`, stdout contains `schema_version=1` | code behavior (`vault/__main__.py:20-25`) | P1 | Auto (API) |
| TC-AUTH-001 | REQ-02 | Auth | Admin login succeeds and returns bearer token | Seeded DB with `admin` | 1. `POST /api/auth/login` with valid admin credentials | `username="admin"`, valid seeded password | HTTP `200`, JSON contains `token` and `user.role == "admin"` | code behavior (`vault/server.py:154-165`) | P0 | Auto (API) |
| TC-AUTH-002 | REQ-02 | Auth | Member login succeeds and returns bearer token | Seeded DB with `bob` | 1. `POST /api/auth/login` with valid member credentials | `username="bob"`, valid seeded password | HTTP `200`, JSON contains `token` and `user.role == "member"` | code behavior (`vault/server.py:154-165`) | P0 | Auto (API) |
| TC-AUTH-003 | REQ-02 | Auth | Login with wrong password returns 401 | Seeded DB | 1. `POST /api/auth/login` with invalid password | `username="bob"`, `password="wrong"` | HTTP `401`, JSON `{"error": "invalid credentials"}` | code behavior (`vault/server.py:161-163`) | P0 | Auto (API) |
| TC-AUTH-004 | REQ-02 | Auth | Login with malformed JSON returns 400 | Server running | 1. `POST /api/auth/login` with invalid JSON body | `{bad` | HTTP `400`, JSON `{"error": ...}` | code behavior (`vault/server.py:155-159`) | P2 | Auto (API) |
| TC-AUTH-005 | REQ-02 | Auth | Request body > 32 KiB rejected with 400 | Server running | 1. `POST /api/auth/login` with >32768-byte payload | 33000-byte JSON string | HTTP `400`, JSON `{"error": "Body length must be 1..32768"}` | code behavior (`vault/server.py:97-98`) | P2 | Auto (API) |
| TC-AUTH-006 | REQ-02 | Auth | Expired bearer token rejected with 401 | Server running | 1. Sign token with `ttl=-10`<br>2. `POST /api/items` with expired token | `ttl=-10` | HTTP `401`, JSON `{"error": "invalid or expired token"}` | code behavior (`vault/server.py:50-52, 110-112`) | P0 | Auto (API) |
| TC-AUTH-007 | REQ-02 | Auth | Tampered bearer token rejected with 401 | Valid token obtained | 1. Alter last 4 chars of signature<br>2. `POST /api/items` with tampered token | Modified token | HTTP `401`, JSON `{"error": "invalid or expired token"}` | code behavior (`vault/server.py:44-45, 110-112`) | P0 | Auto (API) |
| TC-ITEM-001 | REQ-04 | Items | Authenticated member creates valid bookmark | Valid `bob` token | 1. `POST /api/items` with valid title, url, uppercase tag | `title="Python Docs"`, `url="https://docs.python.org"`, `tag="REF"` | HTTP `201`, `status=="active"`, `tag=="ref"`, `owner=="bob"` | code behavior (`vault/storage.py:104-123`) | P1 | Auto (API) |
| TC-ITEM-002 | REQ-04 | Items | Title length boundary 120 accepted, 121 rejected | Valid `bob` token | 1. `POST /api/items` with 120-char title<br>2. `POST /api/items` with 121-char title | `"A"*120`, `"A"*121` | 120 -> HTTP `201`; 121 -> HTTP `400` | code behavior (`vault/storage.py:106-107`) | P1 | Auto (API) |
| TC-ITEM-003 | REQ-04 | Items | Whitespace-only title rejected with 400 | Valid `bob` token | 1. `POST /api/items` with whitespace title | `title="   "` | HTTP `400`, JSON `{"error": "title must be 1..120 non-whitespace characters"}` | code behavior (`vault/storage.py:105-107`) | P1 | Auto (API) |
| TC-ITEM-004 | REQ-04 | Items | JSON null title rejected with 400 | Valid `bob` token | 1. `POST /api/items` with `title: null` | `{"title": null, "url": "https://example.test"}` | HTTP `400` (must not coerce `null` to `"None"`) | approved default (`01-test-plan.md` Q3) | P1 | Auto (API) |
| TC-ITEM-005 | REQ-04 | Items | Non-HTTP(S) URL scheme rejected with 400 | Valid `bob` token | 1. `POST /api/items` with `ftp://` URL | `url="ftp://example.test"` | HTTP `400`, JSON `{"error": "url must start with http:// or https://"}` | code behavior (`vault/storage.py:109-110`) | P1 | Auto (API) |
| TC-ITEM-006 | REQ-03 | Items | List items, filter by tag, reject invalid status | >=1 item created | 1. `GET /api/items`<br>2. `GET /api/items?tag=REF`<br>3. `GET /api/items?status=deleted` | `tag=REF`, `status=deleted` | `200` full list; `200` filtered list; `400` on invalid status | code behavior (`vault/storage.py:83-101`) | P2 | Auto (API) |
| TC-ARCH-001 | REQ-05 | Archive | Archive active item, reject repeat, 404 on missing | Active item exists | 1. `PATCH /api/items/{id}/archive`<br>2. Repeat same `PATCH`<br>3. `PATCH /api/items/99999/archive` | `id`, `99999` | 1st -> `200` `status=="archived"`; 2nd -> `400`; missing -> `404` | code behavior (`vault/storage.py:126-139`) | P1 | Auto (API) |
| TC-RBAC-001 | REQ-06 | RBAC | Member denied DELETE item and GET admin summary | Valid `bob` token, item exists | 1. `DELETE /api/items/{id}` as `bob`<br>2. `GET /api/admin/summary` as `bob` | `bob` token | Both return HTTP `403` | code behavior (`vault/storage.py:142-153`) | P0 | Auto (API) |
| TC-RBAC-002 | REQ-05 | RBAC | Member archives admin's item (horizontal check) | Admin item exists, `bob` token | 1. `PATCH /api/items/{admin_item_id}/archive` as `bob` | `bob` token | Observe actual behavior (`none` oracle pending PO confirmation of Q1) | none (`01-test-plan.md` Q1) | P1 | Auto (API) |
| TC-RBAC-003 | REQ-06 | RBAC | Admin views summary and deletes item (200 then 404) | Valid `admin` token, item exists | 1. `GET /api/admin/summary`<br>2. `DELETE /api/items/{id}`<br>3. Repeat `DELETE /api/items/{id}` | `admin` token | Summary `200`; 1st delete `200`; repeat delete `404` | code behavior (`vault/server.py:139-149, 204-224`) | P1 | Auto (API) |
| TC-UI-001 | REQ-07 | UI | HTML UI escapes XSS in title and renders bookmark | Item with `<script>alert(1)</script>` created | 1. `GET /`<br>2. Inspect HTML for escaped script tag and URL | `<script>alert(1)</script>`, `https://xss.example.test` | HTTP `200`, `&lt;script&gt;alert(1)&lt;/script&gt;` escaped; bookmark URL rendered | code behavior + approved default (`01-test-plan.md` Q2) | P1 | Auto (API) |
| TC-A11Y-001 | REQ-07 | UI | WCAG 2.2 AA code/DOM audit of GET / HTML | `vault/server.py` readable | 1. Review `render_html` against WCAG 2.2 AA checklist | `vault/server.py:55-74` | Landmarks, `lang`, `title`, `h1`, viewport meta, skip link present | spec (WCAG 2.2 AA) | P2 | Manual |

*(Note: Total rows = 21; let's update Counts Overview above to match exact count: 21 cases — P0: 6, P1: 11, P2: 4; `Auto (API)`: 20, `Manual`: 1. Let's keep counts exact!)*

---

## 3. RTM — Requirement Traceability Matrix

| Req/UC ID | Requirement | Happy path (TC) | Negative (TC) | Permission (TC) | Coverage |
|---|---|---|---|---|---|
| REQ-01 | Health & CLI migration/seed | TC-HLTH-001, TC-CLI-001 | — | N/A (public health / local CLI) | Missing Negative |
| REQ-02 | Auth & HMAC bearer tokens | TC-AUTH-001, TC-AUTH-002 | TC-AUTH-003, TC-AUTH-004, TC-AUTH-005 | TC-AUTH-006, TC-AUTH-007 | Full |
| REQ-03 | List & filter items | TC-ITEM-006 | TC-ITEM-006 | N/A (public read endpoint) | Full |
| REQ-04 | Create item & validation | TC-ITEM-001, TC-ITEM-002 | TC-ITEM-002, TC-ITEM-003, TC-ITEM-004, TC-ITEM-005 | Covered via TC-AUTH-006/007 (401) | Full |
| REQ-05 | Archive item state transition | TC-ARCH-001 | TC-ARCH-001 | TC-RBAC-002 | Full |
| REQ-06 | Admin RBAC (delete & summary) | TC-RBAC-003 | TC-RBAC-003 (404) | TC-RBAC-001 | Full |
| REQ-07 | HTML UI & escaping | TC-UI-001 | TC-UI-001 (XSS), TC-A11Y-001 | N/A (public read UI) | Full |

- **Total Requirements:** 7
- **Fully Covered:** 6
- **Coverage %:** `6 / 7 = 85.7%` (REQ-01 missing negative DB-corrupt/unmigrated health check; acceptable for small scope)
- **Orphan Cases:** None
