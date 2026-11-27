"""SQLite storage, migrations, and domain logic for Vault."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import hmac
import os
from pathlib import Path
import sqlite3
from typing import Any

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
VALID_STATUSES = ("active", "archived")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_password(password: str, salt: str | None = None) -> str:
    used_salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), used_salt.encode("utf-8"), 100_000
    ).hex()
    return f"{used_salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    if "$" not in stored:
        return False
    salt, _ = stored.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), stored)


def get_conn(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_migrations(db_path: str | Path) -> int:
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    with closing(get_conn(db_path)) as conn, conn:
        current = int(conn.execute("PRAGMA user_version").fetchone()[0])
        for mig in migrations:
            version = int(mig.name.split("_", 1)[0])
            if version > current:
                conn.executescript(mig.read_text(encoding="utf-8"))
                conn.execute(f"PRAGMA user_version = {version}")
                current = version
    return current


def seed_users(db_path: str | Path) -> None:
    now = utc_now()
    with closing(get_conn(db_path)) as conn, conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("vault-admin-123"), "admin", now),
        )
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("bob", hash_password("vault-member-123"), "member", now),
        )


def authenticate(db_path: str | Path, username: str, password: str) -> dict[str, Any] | None:
    with closing(get_conn(db_path)) as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"], "role": row["role"]}


def list_items(db_path: str | Path, tag: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        clauses.append("v.status = ?")
        params.append(status)
    if tag is not None:
        clauses.append("v.tag = ?")
        params.append(tag.strip().lower())
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        "SELECT v.id, v.title, v.url, v.tag, v.status, v.owner_id, u.username AS owner, v.created_at "
        f"FROM vault_items v JOIN users u ON u.id = v.owner_id{where} ORDER BY v.id DESC"
    )
    with closing(get_conn(db_path)) as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
    return [dict(r) for r in rows]


def create_item(db_path: str | Path, title: str, url: str, tag: str, owner_id: int) -> dict[str, Any]:
    clean_title = title.strip()
    if not clean_title or len(clean_title) > 120:
        raise ValueError("title must be 1..120 non-whitespace characters")
    clean_url = url.strip()
    if clean_url and not clean_url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")
    clean_tag = (tag.strip().lower() or "general")[:32]
    now = utc_now()
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO vault_items (title, url, tag, status, owner_id, created_at) VALUES (?, ?, ?, 'active', ?, ?)",
            (clean_title, clean_url, clean_tag, owner_id, now),
        )
        row = conn.execute(
            "SELECT v.id, v.title, v.url, v.tag, v.status, v.owner_id, u.username AS owner, v.created_at "
            "FROM vault_items v JOIN users u ON u.id = v.owner_id WHERE v.id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return dict(row)


def archive_item(db_path: str | Path, item_id: int) -> dict[str, Any] | None:
    with closing(get_conn(db_path)) as conn, conn:
        row = conn.execute("SELECT status FROM vault_items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            return None
        if row["status"] == "archived":
            raise ValueError("item is already archived")
        conn.execute("UPDATE vault_items SET status = 'archived' WHERE id = ?", (item_id,))
        updated = conn.execute(
            "SELECT v.id, v.title, v.url, v.tag, v.status, v.owner_id, u.username AS owner, v.created_at "
            "FROM vault_items v JOIN users u ON u.id = v.owner_id WHERE v.id = ?",
            (item_id,),
        ).fetchone()
    return dict(updated)


def delete_item(db_path: str | Path, item_id: int, actor: dict[str, Any]) -> bool:
    if actor["role"] != "admin":
        raise PermissionError("Only admin can delete items")
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute("DELETE FROM vault_items WHERE id = ?", (item_id,))
    return cur.rowcount > 0


def get_summary(db_path: str | Path, actor: dict[str, Any]) -> dict[str, Any]:
    if actor["role"] != "admin":
        raise PermissionError("Only admin can view summary")
    with closing(get_conn(db_path)) as conn:
        rows = conn.execute("SELECT status, COUNT(*) AS cnt FROM vault_items GROUP BY status").fetchall()
    counts = {s: 0 for s in VALID_STATUSES}
    for r in rows:
        counts[r["status"]] = r["cnt"]
    return {"by_status": counts, "total": sum(counts.values())}
