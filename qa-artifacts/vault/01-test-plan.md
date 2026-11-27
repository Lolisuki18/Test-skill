# Test Plan — Vault (`vault/`)

- **Phase:** Phase 1/5 — Test Plan
- **Date:** 2026-11-27
- **Version:** 1.0
- **Status:** Approved
- **Requirement source:** `[Inferred from code — needs confirmation]` (`vault/__init__.py`, `vault/__main__.py`, `vault/server.py`, `vault/storage.py`, `vault/migrations/001_init.sql`, `tests/test_vault.py`)

---

## 1. Requirement Audit

> Small scope (< ~500 lines: 431 lines across `vault/`). Skipped N/A groups: Dependencies (no external services), Money/payment.

| Req ID | Requirement (Inferred) | Issue | Type | Clarifying Question | Suggested Default |
|---|---|---|---|---|---|
| REQ-04 | `POST /api/items` creates bookmark (`title`, `url`, `tag`) (`vault/server.py:166-183`, `vault/storage.py:104-123`) | `str(data.get("title", ""))` coerces JSON `null` to `"None"` and numbers to strings; `http://` with empty host is accepted | Missing error flow / Data | Should non-string `title`/`url`/`tag` (especially `null`) be rejected with `400`? Should URLs require a non-empty host? | Reject `null` / non-string fields with `400`; require valid host in URL |
| REQ-05 | `PATCH /api/items/{id}/archive` archives an item (`vault/server.py:186-202`, `vault/storage.py:126-139`) | Any authenticated user (`member`) can archive items owned by `admin` or other users (no `owner_id` or `role` check) | Missing permission | Can `member` archive another user's item, or only own items + `admin`? | Owner or `admin` only (`403` otherwise) — `[Needs input: confirm RBAC]` |
| REQ-03, REQ-07 | `GET /api/items` and `GET /` list all bookmarks (`vault/server.py:122-138`) | Unauthenticated public access returns all items including `owner` username; `GET /` omits `url` from rendered HTML | Missing permission / Contradiction | Is `vault` intentionally public-read, and should `GET /` render clickable `url` links? | Confirm if public-read is intended; `GET /` should render `url` for bookmarks |
| REQ-02 | `POST /api/auth/login` issues HMAC-SHA256 bearer token (`vault/server.py:32-52, 154-165`) | No rate limiting or account lockout on failed logins; no token revocation/logout endpoint | Abuse protection | Is brute-force throttling required on `/api/auth/login`? | Informational check in local QA; recommend rate limiting before production |
| REQ-06 | `DELETE /api/items/{id}` & `GET /api/admin/summary` (`vault/server.py:139-149, 204-224`) | Sensitive admin deletions and login failures are not written to an audit log | Observability | Should admin deletions and auth failures be logged? | Recommend structured audit logging `[Needs input: confirm]` |

---

## 2. Scope

- **In-scope:**
  - `REQ-01`: Health check (`GET /health`) & CLI migration/seeding (`python -m vault --migrate-only --seed`) (`vault/__main__.py:11-27`, `vault/server.py:117-121`)
  - `REQ-02`: Authentication & HMAC token validation (`POST /api/auth/login`, `sign_token`, `verify_token`) (`vault/server.py:32-52, 154-165`)
  - `REQ-03`: List & filter items (`GET /api/items`, `?tag=`, `?status=`) (`vault/server.py:130-138`, `vault/storage.py:83-101`)
  - `REQ-04`: Create item (`POST /api/items`) (`vault/server.py:166-183`, `vault/storage.py:104-123`)
  - `REQ-05`: Archive item (`PATCH /api/items/{id}/archive`) (`vault/server.py:186-202`, `vault/storage.py:126-139`)
  - `REQ-06`: Admin RBAC (`DELETE /api/items/{id}`, `GET /api/admin/summary`) (`vault/server.py:139-149, 204-224`)
  - `REQ-07`: HTML UI rendering & XSS escaping (`GET /`, `render_html`) (`vault/server.py:55-74, 122-129`)
  - Non-functional: Local HTTP latency baseline, security headers/rate-limit check (`02b-nonfunctional.md`), WCAG 2.2 AA code/DOM review (`03c-accessibility.md`)
- **Out-of-scope:**
  - Production deployment/TLS termination (Vault is a local/zero-dependency `ThreadingHTTPServer`).
  - Live screen-reader / multi-browser Playwright runs (no browser/Playwright suite configured for `vault`; HTML is static server-rendered).

---

## 3. Risk Analysis

| Area | Likelihood | Impact | Risk | Driven Priority |
|---|---|---|---|---|
| Authentication & Token Verification (`REQ-02`) | Medium | High | **High** | P0 |
| Admin RBAC & Object Access (`REQ-05`, `REQ-06`) | High | High | **High** | P0 |
| Input Validation & JSON Coercion (`REQ-04`) | High | Medium | **High** | P1 |
| HTML Escaping & UI Completeness (`REQ-07`) | Medium | Medium | **Medium** | P1/P2 |
| Health, CLI Migrations & Filtering (`REQ-01`, `REQ-03`) | Low | Medium | **Low-Med** | P1/P2 |

---

## 4. Strategy Split

| Area | Execution Type | Reason |
|---|---|---|
| HTTP API endpoints (`REQ-01`..`REQ-07`) | `Auto (API)` | Direct HTTP/JSON contracts tested via Python `urllib` against live `VaultHandler` + existing `unittest` (`tests/test_vault.py`) |
| CLI `--migrate-only --seed` (`REQ-01`) | `Auto (API)` *(automated non-UI run)* | Subprocess CLI verification with isolated temp SQLite DB |
| Accessibility & HTML UI inspection (`REQ-07`) | `Manual` | Code/DOM review against WCAG 2.2 AA (`qa-accessibility-auditor`); live assistive-tech checks stay `Not Run` |

---

## 5. Environment & Test Data

- **Environment:** Local Windows (`Python 3.14.6`), `ThreadingHTTPServer(("127.0.0.1", 0), make_handler(db_path, secret))`, isolated `tempfile.TemporaryDirectory()` SQLite DB per run.
- **Seeded accounts (`vault/storage.py:57-69`):** `admin` (role `admin`), `bob` (role `member`). Credentials used only in-memory from `seed_users`.
- **Boundary data:** 120-char & 121-char `title`, whitespace `title`, JSON `null` `title`, `ftp://` URL, `> 32 KiB` JSON body, `<script>alert(1)</script>` XSS payload, expired/tampered HMAC tokens.

---

## 6. Entry / Exit Criteria

- **Entry:** `vault/` code present, `python -W error -m unittest tests/test_vault.py -v` passes.
- **Exit (`Proposed — user to confirm`):** 100% P0 Pass, 0 Open Blocker/Critical, >= 95% P1 Pass, 100% RTM coverage for in-scope requirements.

---

## 7. Open Questions & Assumptions

1. Confirm whether `member` should be blocked (`403`) from archiving another user's item (`REQ-05`). *Default: Owner or `admin` only.*
2. Confirm whether `GET /` should display bookmark `url` links (`REQ-07`). *Default: Yes, a bookmark manager should render clickable `http(s)://` links.*
3. Confirm whether `POST /api/items` should reject non-string JSON values like `{"title": null}` with `400` (`REQ-04`). *Default: Yes.*
