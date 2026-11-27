# 001. Use SQLite with Raw SQL Migrations for Vault

- **Status:** Accepted
- **Date:** 2026-11-27 (commit `09a555a` date)
- **Deciders:** `[Cần bổ sung: decision owners]`
- **Related:** `vault/storage.py`, `vault/migrations/001_init.sql`, [Architecture and ERD](../diagrams/architecture-and-erd.md)

## Context

Vault is a zero-dependency bookmark and snippet manager designed for local execution and end-to-end skill testing (`vault/__init__.py:1`). The project has no external package manifest (`requirements.txt` or `pyproject.toml`), and CI runs only Python 3.12 standard library tools (`compileall`, `unittest`, and `python -m vault --migrate-only` in `.github/workflows/ci.yml:16-24`). Persistent storage is needed for `users` (with roles and salted password hashes) and `vault_items` (with foreign-key ownership, status checks, and indexed filtering by `status` and `tag`). Schema evolution must be deterministic without requiring external migration frameworks.

## Options Considered

### Option 1: Python `sqlite3` stdlib + numbered `.sql` migrations via `PRAGMA user_version`
- Description: Store data in a local SQLite file (`vault/storage.py:37-41`), enable foreign keys per connection (`PRAGMA foreign_keys = ON`), and apply sorted `.sql` files in `vault/migrations/` tracked by `PRAGMA user_version` (`vault/storage.py:44-54`).
- Pros: Zero external dependencies; single-file database works identically in CI (`/tmp/vault-ci.db`) and local dev (`vault.db`); schema version is inspectable at `/health` (`vault/server.py:118-120`).
- Cons: Single-writer file locking limits concurrent write throughput; no built-in down-migrations (only forward `.sql` scripts); SQLite `ALTER TABLE` has limited column modification support.

### Option 2: External database server + ORM/migration tool (Implied alternative — not recorded as considered)
- Description: Use PostgreSQL or MySQL with an ORM (e.g., SQLAlchemy + Alembic). `[Cần bổ sung: confirm whether an external DB/ORM was considered]`
- Pros: Concurrent multi-process writes, richer type enforcement, and reversible migration scripts.
- Cons: Requires external service setup, third-party pip dependencies, and a dependency manifest, breaking the zero-dependency constraint.

## Decision

We will use Python's standard-library `sqlite3` with numbered forward-only `.sql` migrations tracked by `PRAGMA user_version`, because it satisfies the zero-dependency requirement while enforcing relational integrity (`PRAGMA foreign_keys = ON` and `CHECK` constraints in `vault/migrations/001_init.sql:6, 15-16`).

Scope: Applies to all persistence in the `vault` package (`vault/storage.py`, `vault/migrations/`). Does not apply to other modules in this repository (`taskbox`, `notes_web`, `pulseboard`).

## Consequences / Trade-offs

- **Positive:** Immediate setup with `python -m vault --db vault.db --migrate-only`; no external DB daemon or package install needed.
- **Negative / costs:** Forward-only migrations mean schema rollbacks require restoring a database file backup or writing a compensating migration script. SQLite file locking serializes concurrent writes across `ThreadingHTTPServer` threads.
- **Risks and how they are checked or mitigated:** Foreign key constraints are disabled by default in SQLite; `get_conn()` enforces `PRAGMA foreign_keys = ON` on every connection (`vault/storage.py:40`). Migration application is smoke-tested in CI (`.github/workflows/ci.yml:24`) and `tests/test_vault.py:98-105`.
- **Follow-ups:** Add a database backup/restore procedure before deploying to any shared environment (see [Runbook](../runbook.md)).
