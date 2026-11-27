-- Migration 001: users and vault_items tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'member')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vault_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    tag TEXT NOT NULL DEFAULT 'general',
    status TEXT NOT NULL CHECK (status IN ('active', 'archived')),
    owner_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vault_items_status ON vault_items(status);
CREATE INDEX IF NOT EXISTS idx_vault_items_tag ON vault_items(tag);
