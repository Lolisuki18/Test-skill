# Vault Architecture and ERD

System architecture and logical entity-relationship diagram for Vault, derived from `vault/__main__.py`, `vault/server.py`, `vault/storage.py`, and `vault/migrations/001_init.sql`.

## System Architecture

Vault runs as a single-process Python `ThreadingHTTPServer` backed by a local SQLite database file (`vault/server.py:236-241`, `vault/storage.py:37-41`).

```mermaid
flowchart LR
  %% Evidence: vault/__main__.py, vault/server.py, vault/storage.py, vault/migrations/001_init.sql
  Client["HTTP Client / Browser"] -->|"HTTP JSON & HTML (:8095)"| Server["VaultHandler (vault/server.py)"]
  CLI["CLI (python -m vault)"] -->|"--migrate-only / --seed / run"| Server
  CLI -->|"apply_migrations / seed_users"| Storage["Storage Layer (vault/storage.py)"]
  Server -->|"authenticate / CRUD / summary"| Storage
  Storage -->|"sqlite3 (PRAGMA foreign_keys=ON)"| DB[("SQLite (vault.db)")]
```

Evidence: `vault/__main__.py:11-28`, `vault/server.py:77-241`, `vault/storage.py:37-158`.

## Logical ERD

Database schema for `users` and `vault_items` (`vault/migrations/001_init.sql:2-18`).

```mermaid
erDiagram
  %% Evidence: vault/migrations/001_init.sql
  users ||--o{ vault_items : "owns (owner_id)"
  users {
    INTEGER id PK
    TEXT username UK
    TEXT password_hash
    TEXT role
    TEXT created_at
  }
  vault_items {
    INTEGER id PK
    TEXT title
    TEXT url
    TEXT tag
    TEXT status
    INTEGER owner_id FK
    TEXT created_at
  }
```

Evidence: `vault/migrations/001_init.sql:2-21`.
