# Runbook - Vault

Last verified: 2026-11-27 by QA/Docs evaluation against commit `09a555a`
Environments: Local / CI (`ubuntu-latest` in `.github/workflows/ci.yml:11`). `[Cần bổ sung: staging/production environment details — none defined in repo]`

## 1. Quick index

| Symptom | Go to |
|---|---|
| Service unreachable or fails to start | 5.1 |
| `401` / `403` authentication or permission errors | 5.2 |
| `400` validation or archive errors | 5.3 |
| Database schema mismatch or migration failure | 4.2, 4.3 |

## 2. System sheet

| Component | Purpose | Run command / image | Port | Health check | Logs |
|---|---|---|---|---|---|
| `vault` HTTP server | Serves HTML UI (`/`) and JSON API (`/api/*`) (`vault/server.py:77-241`) | `python -m vault --host 127.0.0.1 --port 8095 --db vault.db` | `8095` (default, `vault/__main__.py:14`) | `GET /health` -> `200 {"status": "ok", "schema_version": 1}` (`vault/server.py:117-121`) | Suppressed in code (`VaultHandler.log_message` is a no-op at `vault/server.py:81-82`; `[Cần bổ sung: external log sink if wrapped]`) |
| SQLite database | Stores `users` and `vault_items` (`vault/migrations/001_init.sql`) | Local file (`--db`, default `vault.db`) | N/A (file) | `PRAGMA user_version` via `/health` | N/A |

- **Dependencies:** Python `3.12+` stdlib (`sqlite3`, `http.server`). No external DB daemon, cache, queue, or third-party API (`vault/server.py:5-16`).
- **Configuration & secrets:**
  - `VAULT_SECRET` (required for `run_server`, `vault/server.py:238-240`): HMAC-SHA256 signing secret for bearer tokens. Store in runtime environment / secret manager; never hardcode or commit.

## 3. Access and contacts

| Role | Who | How to reach |
|---|---|---|
| Owner | `[Cần bổ sung: service owner]` | `[Cần bổ sung]` |
| On-call | `[Cần bổ sung: on-call rotation]` | `[Cần bổ sung]` |

## 4. Routine procedures

### 4.1 Start / Deploy (local)

**Pre-checks:**
- CI checks pass: `python -m compileall -q vault tests/test_vault.py` and `python -W error -m unittest tests.test_vault -v` (`.github/workflows/ci.yml:18-20`).
- `VAULT_SECRET` is set in the target shell/environment.

**Steps:**
1. Run migrations (add `--seed` only for initial dev/test setup when `users` is empty):
   ```bash
   python -m vault --db vault.db --migrate-only
   ```
   Expected output: `Migrated vault.db to schema_version=1` (`vault/__main__.py:24`).
2. Start the server:
   ```bash
   python -m vault --host 127.0.0.1 --port 8095 --db vault.db
   ```
3. Verify health:
   ```bash
   curl -s http://127.0.0.1:8095/health
   ```
   Expected output: `{"status": "ok", "schema_version": 1}` (`vault/server.py:120`).

### 4.2 Roll back

- **Application code:** Stop the `python -m vault` process, check out the previous commit/tag, and restart.
- **Database migrations:** **WARNING:** `apply_migrations` (`vault/storage.py:44-54`) only applies forward `.sql` files and has no down-migration support. To roll back a schema change, restore the SQLite `.db` file from a pre-migration backup.

### 4.3 Back up / Restore / Rotate `VAULT_SECRET`

- **Back up SQLite DB:** Stop writes (or use SQLite online backup) and copy `vault.db` before running new migrations. `[Cần bổ sung: automated backup script/schedule — none in repo]`
- **Restore SQLite DB:** **WARNING:** Overwrites current data. Verify you have the correct environment and database path, stop the server, replace `vault.db` with the backup file, and restart.
- **Rotate `VAULT_SECRET`:** Update `VAULT_SECRET` in the environment and restart the server. Note: all existing bearer tokens signed with the old secret immediately fail verification (`401 {"error": "invalid or expired token"}` at `vault/server.py:44-45, 110-112`) and users must re-authenticate via `POST /api/auth/login`.

## 5. Incident playbooks

### 5.1 Service unreachable or fails to start

- **Confirm:** `GET /health` fails to connect or process exits immediately.
- **Likely causes (from repo):**
  - `VAULT_SECRET` is unset -> `RuntimeError: VAULT_SECRET environment variable must be set` (`vault/server.py:239-240`).
  - Port `8095` already in use or invalid `--db` path permissions.
- **Steps:**
  1. Check that `VAULT_SECRET` is set (do not print its value).
  2. Run `python -m vault --db vault.db --migrate-only` to verify DB path accessibility and migration state.
  3. Start `python -m vault --host 127.0.0.1 --port 8095 --db vault.db` and check `GET /health`.
- **Escalate when:** Process still fails after verifying `VAULT_SECRET` and DB file permissions -> escalate to `[Cần bổ sung: owner]`.

### 5.2 High `401` or `403` rate

- **Confirm:** Clients receive `401 {"error": "invalid or expired token"}` or `403 {"error": "Only admin can ..."}`.
- **Likely causes (from repo):**
  - Token expired after `3600` seconds (`ttl=3600` in `vault/server.py:32, 50-51`).
  - `VAULT_SECRET` changed across restarts.
  - A `member` user is calling `GET /api/admin/summary` or `DELETE /api/items/{id}` (`vault/storage.py:143-144, 151-152`).
- **Steps:**
  1. Have the client re-authenticate via `POST /api/auth/login`.
  2. Verify the caller's `role` is `admin` for summary/delete endpoints.

### 5.3 `400` errors on item creation or archiving

- **Confirm:** Clients receive `400` JSON errors.
- **Likely causes (from repo):**
  - Body > `32768` bytes (`MAX_BODY_BYTES`, `vault/server.py:29, 97-98`).
  - `title` empty or > 120 chars, or `url` does not start with `http://`/`https://` (`vault/storage.py:106-110`).
  - `PATCH /api/items/{id}/archive` called on an already `archived` item (`vault/storage.py:131-132`).
- **Steps:**
  1. Inspect the returned `{"error": "..."}` message and align the client request with `docs/vault/api.md`.

## 6. After an incident

- [ ] Timeline written (detected, mitigated, resolved)
- [ ] Root cause and contributing factors recorded
- [ ] Follow-up tasks created with owners
- [ ] Runbook updated where a step was missing or inaccurate

## 7. Known gaps

- `VaultHandler.log_message` is a no-op (`vault/server.py:81-82`), so HTTP access logs are not emitted.
- No automated backup script, monitoring/alerting configuration, or production deployment manifest exists in the repository.
- No staging/production hostnames or contacts are defined in the repository.
