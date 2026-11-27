# Execution Notes — Vault (`vault/`)

- **Phase:** Phase 3/5 — Execution & Automation
- **Date:** 2026-11-27
- **Build / Commit:** `09a555a`
- **Environment:** Windows, PowerShell, `Python 3.14.6`, local `127.0.0.1` ephemeral port (`ThreadingHTTPServer` + isolated temp SQLite DB)

---

## 1. Existing Unit & Integration Suite (`tests/test_vault.py`)

Command:
```powershell
python -W error -m unittest tests/test_vault.py -v
```

Verbatim output:
```text
test_health_ui_and_rbac_flow (tests.test_vault.VaultTests.test_health_ui_and_rbac_flow) ... ok
test_validation_and_cli (tests.test_vault.VaultTests.test_validation_and_cli) ... ok

----------------------------------------------------------------------
Ran 2 tests in 1.330s

OK
```

---

## 2. API & CLI Track (`qa-api-tester` / `qa-e2e-writer`)

Command:
```powershell
python C:\Users\NinhLe\.gemini\antigravity\brain\228cf5ce-f701-4e89-a3c8-82758f8fd5ee\scratch\vault_qa_runner.py
```

Machine-readable results: `vault_qa_results.json` (20 `Auto (API)` cases executed + 2 `NF-*` checks).

| TC ID | Endpoint / Target | Expected | Actual | Status | Time (ms) |
|---|---|---|---|---|---|
| TC-HLTH-001 | `GET /health` | `200 {status: ok, schema_version: 1}` | `200 {'status': 'ok', 'schema_version': 1}` | **Pass** | — |
| TC-CLI-001 | `python -m vault --seed --migrate-only` | Exit `0` + `schema_version=1` | `rc=0`, `Migrated ... to schema_version=1` | **Pass** | — |
| TC-AUTH-001 | `POST /api/auth/login` (`admin`) | `200` + token + `role=admin` | `200`, `role=admin` | **Pass** | — |
| TC-AUTH-002 | `POST /api/auth/login` (`bob`) | `200` + token + `role=member` | `200`, `role=member` | **Pass** | — |
| TC-AUTH-003 | `POST /api/auth/login` (wrong pw) | `401 invalid credentials` | `401 {'error': 'invalid credentials'}` | **Pass** | — |
| TC-AUTH-004 | `POST /api/auth/login` (malformed JSON) | `400` JSON error | `400 {"error": "Expecting property name..."}` | **Pass** | — |
| TC-AUTH-005 | `POST /api/auth/login` (`>32 KiB`) | `400` Body length limit | `400 {"error": "Body length must be 1..32768"}` | **Pass** | — |
| TC-AUTH-006 | `POST /api/items` (expired token) | `401 invalid or expired token` | `401 {'error': 'invalid or expired token'}` | **Pass** | — |
| TC-AUTH-007 | `POST /api/items` (tampered token) | `401 invalid or expired token` | `401 {'error': 'invalid or expired token'}` | **Pass** | — |
| TC-ITEM-001 | `POST /api/items` (valid) | `201`, `status=active`, `tag=ref`, `owner=bob` | `201`, `status=active`, `tag=ref`, `owner=bob` | **Pass** | — |
| TC-ITEM-002 | `POST /api/items` (`title` 120 vs 121) | `120 -> 201`, `121 -> 400` | `120 -> 201`, `121 -> 400` | **Pass** | — |
| TC-ITEM-003 | `POST /api/items` (whitespace title) | `400` title validation | `400 {'error': 'title must be 1..120 non-whitespace characters'}` | **Pass** | — |
| TC-ITEM-004 | `POST /api/items` (`title: null`) | `400` rejected (not `"None"`) | `201 {'item': {'id': 3, 'title': 'None', ...}}` | **Fail** (`DEF-001`) | — |
| TC-ITEM-005 | `POST /api/items` (`ftp://` url) | `400` url validation | `400 {'error': 'url must start with http:// or https://'}` | **Pass** | — |
| TC-ITEM-006 | `GET /api/items` (list/filter/bad status) | `200` all, `200` tag=REF->1, `400` bad status | `all=3, tag=1, bad=400 {'error': 'Invalid status: deleted'}` | **Pass** | — |
| TC-ARCH-001 | `PATCH /api/items/{id}/archive` | `200` archived, repeat `400`, `99999 -> 404` | `1st=200, 2nd=400, missing=404` | **Pass** | — |
| TC-RBAC-001 | `DELETE` & `GET /api/admin/summary` (`bob`) | `403` on both | `del=403`, `sum=403` | **Pass** | — |
| TC-RBAC-002 | `PATCH /api/items/{admin_id}/archive` (`bob`) | Observe horizontal auth (`none` oracle) | `200` (`bob` archived `admin`'s item) | **Informational** | — |
| TC-RBAC-003 | Admin summary & `DELETE` (200 then 404) | `200` summary, `200` delete, `404` repeat | `sum=200`, `del=200`, `repeat=404` | **Pass** | — |
| TC-UI-001 | `GET /` (HTML escaping & URL rendering) | `200`, escaped `<script>`, URL rendered | `200`, `escaped=True`, `renders_url=False` | **Fail** (`DEF-002`) | — |
| TC-A11Y-001 | `GET /` WCAG 2.2 AA code/DOM audit | Landmarks, `lang`, `title`, `h1`, viewport, skip link | Missing `<meta name="viewport">`, no skip link (`03c-accessibility.md`) | **Fail** (`DEF-003`) | — |

**Execution Totals (functional matrix, excluding `Informational` TC-RBAC-002):**
- Total in matrix: `21` (`20` evaluated + `1` `Informational`)
- Passed: `17`
- Failed: `3` (`TC-ITEM-004`, `TC-UI-001`, `TC-A11Y-001`)
- Blocked: `0`
- Not Run: `0`
- Informational: `1` (`TC-RBAC-002`)

---

## 3. Non-functional Track (`qa-nonfunctional-writer`)

| NF ID | Scenario | Threshold | Actual Measurement | Status |
|---|---|---|---|---|
| NF-PERF-01 | `GET /api/items` x50 sequential | `[Needs input: SLA]` | `p50=1.43ms`, `p95=1.94ms`, `max=24.45ms` | **Informational** |
| NF-SEC-01 | Security headers & 10x failed login rate limit | Informational | `X-Content-Type-Options: None`, `X-Frame-Options: None`, `Content-Security-Policy: None`, `Cache-Control: None`; 10/10 failed logins returned `401` (no `429` throttling) | **Informational** |
