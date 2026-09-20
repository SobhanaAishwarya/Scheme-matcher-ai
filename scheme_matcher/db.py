"""Tiny SQLite user store behind the sign-in gate.

The database file lives in ``data/users.db`` (override with ``SCHEME_DB_PATH``).
On hosts where the app folder is read-only, it falls back to the system temp
directory. Note that hosts such as Streamlit Community Cloud have an ephemeral
disk, so accounts reset whenever the app is rebuilt or restarted.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def db_path() -> Path:
    override = os.environ.get("SCHEME_DB_PATH")
    if override:
        return Path(override)
    folder = Path(__file__).resolve().parent.parent / "data"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        if os.access(folder, os.W_OK):
            return folder / "users.db"
    except OSError:
        pass
    return Path(tempfile.gettempdir()) / "scheme_matcher_users.db"


@contextmanager
def connect(path: Optional[str | Path] = None) -> Iterator[sqlite3.Connection]:
    target = Path(path) if path else db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email: str, path: Optional[str | Path] = None) -> Optional[dict]:
    with connect(path) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def create_user(
    name: str, email: str, password_hash: str, password_salt: str,
    path: Optional[str | Path] = None,
) -> dict:
    """Insert a user; raises ``sqlite3.IntegrityError`` if the email is taken."""
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, password_salt) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, password_salt),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)
