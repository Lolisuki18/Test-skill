"""SQLite connection, migrations, and domain operations for PulseBoard."""

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
VALID_STATUSES = ("open", "in_progress", "resolved", "closed")
VALID_PRIORITIES = ("P0", "P1", "P2", "P3")
ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "open": ("in_progress", "resolved"),
    "in_progress": ("resolved", "open"),
    "resolved": ("closed", "open"),
    "closed": (),
}


def utc_now() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256."""
    used_salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), used_salt.encode("utf-8"), 100_000
    ).hex()
    return f"{used_salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a plaintext password against a stored salt$hash string."""
    if "$" not in stored:
        return False
    salt, _ = stored.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), stored)


def get_conn(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_migrations(db_path: str | Path) -> int:
    """Apply pending SQL migrations tracked by PRAGMA user_version."""
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


def seed_default_users(db_path: str | Path) -> None:
    """Seed default admin and member accounts if the users table is empty."""
    now = utc_now()
    with closing(get_conn(db_path)) as conn, conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin-pass-123"), "admin", now),
        )
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("alice", hash_password("member-pass-123"), "member", now),
        )


def authenticate_user(db_path: str | Path, username: str, password: str) -> dict[str, Any] | None:
    """Validate credentials and return user dict or None."""
    with closing(get_conn(db_path)) as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"], "role": row["role"]}


def list_issues(db_path: str | Path, status: str | None = None) -> list[dict[str, Any]]:
    """List issues, optionally filtered by status."""
    query = (
        "SELECT i.id, i.title, i.description, i.status, i.priority, "
        "i.author_id, u.username AS author, i.created_at, i.updated_at "
        "FROM issues i JOIN users u ON u.id = i.author_id"
    )
    params: tuple[Any, ...] = ()
    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        query += " WHERE i.status = ?"
        params = (status,)
    query += " ORDER BY i.id DESC"
    with closing(get_conn(db_path)) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def create_issue(
    db_path: str | Path,
    title: str,
    description: str,
    priority: str,
    author_id: int,
) -> dict[str, Any]:
    """Create a new issue in open status and record an audit_log entry."""
    clean_title = title.strip()
    if not clean_title or len(clean_title) > 160:
        raise ValueError("title must be 1..160 non-whitespace characters")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
    now = utc_now()
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO issues (title, description, status, priority, author_id, created_at, updated_at) "
            "VALUES (?, ?, 'open', ?, ?, ?, ?)",
            (clean_title, description.strip(), priority, author_id, now, now),
        )
        issue_id = cur.lastrowid
        conn.execute(
            "INSERT INTO audit_log (actor_id, action, target_id, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (author_id, "issue.create", issue_id, f"priority={priority}", now),
        )
        row = conn.execute(
            "SELECT i.id, i.title, i.description, i.status, i.priority, "
            "i.author_id, u.username AS author, i.created_at, i.updated_at "
            "FROM issues i JOIN users u ON u.id = i.author_id WHERE i.id = ?",
            (issue_id,),
        ).fetchone()
    return dict(row)


def transition_issue(
    db_path: str | Path,
    issue_id: int,
    new_status: str,
    actor: dict[str, Any],
) -> dict[str, Any] | None:
    """Transition an issue status following ALLOWED_TRANSITIONS and role rules."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")
    with closing(get_conn(db_path)) as conn, conn:
        row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if row is None:
            return None
        current = row["status"]
        if new_status not in ALLOWED_TRANSITIONS[current]:
            raise ValueError(f"Transition {current} -> {new_status} is not allowed")
        if new_status == "closed" and actor["role"] != "admin":
            raise PermissionError("Only admin can close issues")
        now = utc_now()
        conn.execute(
            "UPDATE issues SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now, issue_id),
        )
        conn.execute(
            "INSERT INTO audit_log (actor_id, action, target_id, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (actor["id"], "issue.transition", issue_id, f"{current}->{new_status}", now),
        )
        updated = conn.execute(
            "SELECT i.id, i.title, i.description, i.status, i.priority, "
            "i.author_id, u.username AS author, i.created_at, i.updated_at "
            "FROM issues i JOIN users u ON u.id = i.author_id WHERE i.id = ?",
            (issue_id,),
        ).fetchone()
    return dict(updated)


def delete_issue(db_path: str | Path, issue_id: int, actor: dict[str, Any]) -> bool:
    """Delete an issue (admin only) and write an audit_log entry."""
    if actor["role"] != "admin":
        raise PermissionError("Only admin can delete issues")
    now = utc_now()
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
        if cur.rowcount == 0:
            return False
        conn.execute(
            "INSERT INTO audit_log (actor_id, action, target_id, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (actor["id"], "issue.delete", issue_id, "deleted", now),
        )
    return True


def get_admin_stats(db_path: str | Path, actor: dict[str, Any]) -> dict[str, Any]:
    """Return issue counts by status and recent audit count (admin only)."""
    if actor["role"] != "admin":
        raise PermissionError("Only admin can view stats")
    with closing(get_conn(db_path)) as conn:
        rows = conn.execute("SELECT status, COUNT(*) AS cnt FROM issues GROUP BY status").fetchall()
        audit_cnt = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    by_status = {s: 0 for s in VALID_STATUSES}
    for r in rows:
        by_status[r["status"]] = r["cnt"]
    return {"by_status": by_status, "total_issues": sum(by_status.values()), "audit_events": audit_cnt}
