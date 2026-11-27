# Vault

Vault is a zero-dependency bookmark and snippet manager built with Python's standard library and SQLite (`vault/__init__.py:1`). It provides an HTTP JSON API with HMAC-SHA256 bearer authentication, role-based access control (`admin` and `member`), and a read-only HTML overview page (`vault/server.py:55-74`, `vault/migrations/001_init.sql:6`).

## Tech stack

| Layer | Technology | Version / Source |
|---|---|---|
| Language | Python | `3.12` (`.github/workflows/ci.yml:16`), stdlib only (no `requirements.txt` or `pyproject.toml`) |
| HTTP server | `http.server.ThreadingHTTPServer` | Python stdlib (`vault/server.py:10, 241`) |
| Database | SQLite (`sqlite3`) | Python stdlib (`vault/storage.py:11, 38`) |
| Auth & hashing | `hashlib.pbkdf2_hmac` + HMAC-SHA256 | Python stdlib (`vault/storage.py:24`, `vault/server.py:35`) |

## Prerequisites

- Python `3.12` or compatible (verified in CI on `3.12` in `.github/workflows/ci.yml:16`; verified locally on Python `3.14.6`).
- `[Needs input: minimum supported Python version if < 3.12]`
- No third-party packages required (stdlib-only; no dependency manifest exists in the repository).

## Getting started

### 1. Configure environment

Set `VAULT_SECRET` before starting the server (`vault/server.py:238-240`). If `VAULT_SECRET` is unset, `run_server` raises `RuntimeError`.

| Name | Description | Required | Default / Example |
|---|---|---|---|
| `VAULT_SECRET` | Secret key used to sign and verify HMAC-SHA256 bearer tokens (`vault/server.py:32-52, 238-240`) | Yes (for server) | None (example: set in local shell before running) |

### 2. Install dependencies

Nothing to install (Python standard library only; no `requirements.txt` or `pyproject.toml` is present).

### 3. Database setup, migrations, and seed

Run migrations (and optionally seed the demo `admin` and `bob` accounts defined in `vault/storage.py:57-69`) in a terminal at the repo root:

```bash
python -m vault --db vault.db --seed --migrate-only
```

Expected output: `Migrated vault.db to schema_version=1` (`vault/__main__.py:24`).

### 4. Run the server

```bash
python -m vault --host 127.0.0.1 --port 8095 --db vault.db
```

The server listens on `http://127.0.0.1:8095` by default (`vault/__main__.py:13-14`, `vault/server.py:236`).

## CLI options

Defined in `vault/__main__.py:12-18`:

| Flag | Default | Description |
|---|---|---|
| `--host` | `127.0.0.1` | Bind host address |
| `--port` | `8095` | Bind port (integer) |
| `--db` | `vault.db` | Path to the SQLite database file |
| `--seed` | `false` | Seed initial `admin` and `bob` users when `users` table is empty (`vault/storage.py:57-69`) |
| `--migrate-only` | `false` | Apply migrations (and seed if `--seed` is set), print schema version, and exit `0` |

## Project structure

```text
vault/
├── __init__.py            # Package docstring
├── __main__.py            # CLI entry point (`python -m vault`)
├── server.py              # HTTP server, bearer auth, JSON API, HTML view
├── storage.py             # SQLite connection, migrations, password hashing, domain queries
└── migrations/
    └── 001_init.sql       # Initial schema: `users` and `vault_items` tables + indexes
```

## Testing

Run the compile check and unit/integration tests from the repo root (`.github/workflows/ci.yml:18-24`):

```bash
python -m compileall -q vault tests/test_vault.py
```

```bash
python -W error -m unittest tests.test_vault -v
```

Latest verified run (commit `09a555a`, Python `3.14.6`): `Ran 2 tests in 1.317s OK`.

## Documentation

- [API Specification](api.md)
- [ADR 001: Use SQLite with Raw SQL Migrations for Vault](adr/001-sqlite-vault.md)
- [Architecture and ERD Diagrams](diagrams/architecture-and-erd.md)
- [User Guide](user-guide.md)
- [Operations Runbook](runbook.md)
- `[Needs input: project license — no LICENSE file exists in the repository]`
