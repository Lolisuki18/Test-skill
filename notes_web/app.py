"""Simple Notes Web + REST API backed by SQLite (stdlib only)."""
from contextlib import closing
import html
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DB_PATH = "notes.db"


def get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    with closing(get_conn(db_path)) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def list_notes(db_path: str = DB_PATH) -> list[dict]:
    with closing(get_conn(db_path)) as conn:
        rows = conn.execute("SELECT id, title, body, created_at FROM notes ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def create_note(title: str, body: str = "", db_path: str = DB_PATH) -> dict:
    if not title or not title.strip():
        raise ValueError("title is required")
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title.strip(), body))
        row = conn.execute("SELECT id, title, body, created_at FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


def search_notes(query: str, db_path: str = DB_PATH) -> list[dict]:
    with closing(get_conn(db_path)) as conn:
        # Intentional: unindexed LIKE scan + potential SQLi if someone refactors carelessly, currently parameterized
        rows = conn.execute(
            "SELECT id, title, body, created_at FROM notes WHERE title LIKE ? OR body LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_note(note_id: int, db_path: str = DB_PATH) -> bool:
    with closing(get_conn(db_path)) as conn, conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0


def render_index_html(notes: list[dict]) -> str:
    items = "".join(
        f"<li><b>{n['title']}</b>: {html.escape(n['body'])} "
        f"<button onclick='del({n['id']})'>X</button></li>"
        for n in notes
    )
    # Intentional accessibility & XSS issues for QA/Security skills to catch:
    # 1. Missing lang attribute on <html>
    # 2. Missing <label> on inputs
    # 3. n['title'] is NOT html-escaped in <li> (stored XSS)
    # 4. Button text is just "X" without aria-label
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Notes Web</title></head>
<body>
  <h1>Notes</h1>
  <form id="f">
    <input id="title" placeholder="Title" />
    <input id="body" placeholder="Body" />
    <button type="submit">Add</button>
  </form>
  <ul>{items}</ul>
</body>
</html>"""


class NotesHandler(BaseHTTPRequestHandler):
    db_path = DB_PATH

    def _send_json(self, status: int, payload: object) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if parsed.path == "/api/notes":
            self._send_json(200, {"notes": list_notes(self.db_path)})
            return
        if parsed.path == "/":
            body = render_index_html(list_notes(self.db_path)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/api/notes":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        try:
            note = create_note(data.get("title", ""), data.get("body", ""), self.db_path)
            self._send_json(201, note)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})

    def do_DELETE(self) -> None:
        if not self.path.startswith("/api/notes/"):
            self._send_json(404, {"error": "not found"})
            return
        note_id = int(self.path.rsplit("/", 1)[-1])
        if delete_note(note_id, self.db_path):
            self._send_json(200, {"deleted": note_id})
        else:
            self._send_json(404, {"error": "not found"})

    def log_message(self, format: str, *args: object) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8080, db_path: str = DB_PATH) -> None:
    init_db(db_path)
    NotesHandler.db_path = db_path
    HTTPServer((host, port), NotesHandler).serve_forever()
