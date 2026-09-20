"""Sign Up / Sign In use cases.

Passwords are hashed with PBKDF2-HMAC-SHA256 (standard library) and a random
per-user salt, so no extra dependency is needed. Raw passwords and hashes never
leave this module; callers only ever see the public user dict.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

from . import db

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ITERATIONS = 260_000
MIN_PASSWORD_LENGTH = 8

User = dict
Result = Tuple[Optional[User], Optional[str]]


def hash_password(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    """Return ``(hash_hex, salt_hex)``, generating a salt when none is given."""
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return digest.hex(), salt.hex()


def verify_password(password: str, password_hash: str, password_salt: str) -> bool:
    candidate, _ = hash_password(password, password_salt)
    return hmac.compare_digest(candidate, password_hash)


def _public(row: dict) -> User:
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def sign_up(
    name: str, email: str, password: str, confirm: str,
    path: Optional[str | Path] = None,
) -> Result:
    """Create an account. Returns ``(user, None)`` or ``(None, error message)``."""
    clean_name, clean_email = name.strip(), email.strip().lower()
    if not clean_name:
        return None, "Please enter your name."
    if not _EMAIL_RE.match(clean_email):
        return None, "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return None, "Passwords do not match."
    if db.get_user_by_email(clean_email, path):
        return None, "An account with this email already exists. Try signing in."

    password_hash, salt = hash_password(password)
    try:
        row = db.create_user(clean_name, clean_email, password_hash, salt, path)
    except sqlite3.IntegrityError:  # lost a race with another sign-up
        return None, "An account with this email already exists. Try signing in."
    return _public(row), None


def sign_in(email: str, password: str, path: Optional[str | Path] = None) -> Result:
    """Verify credentials. Returns ``(user, None)`` or ``(None, error message)``."""
    clean_email = email.strip().lower()
    if not clean_email or not password:
        return None, "Please enter your email and password."
    row = db.get_user_by_email(clean_email, path)
    if row is None or not verify_password(password, row["password_hash"], row["password_salt"]):
        return None, "Incorrect email or password."
    return _public(row), None
