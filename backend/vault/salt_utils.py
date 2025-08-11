"""
Vault salt utilities for per-user encryption salt management.
"""

import os
import sqlite3
from backend.utils.db import get_db

SALT_TABLE = "user_salts"


def get_or_create_user_salt(user_id: int) -> bytes:
    """Get or create a unique salt for a user (stored in DB)."""
    db = get_db()
    cur = db.execute(f"SELECT salt FROM {SALT_TABLE} WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        return row[0]
    # Create new salt
    salt = os.urandom(16)
    db.execute(
        f"INSERT INTO {SALT_TABLE} (user_id, salt) VALUES (?, ?)", (user_id, salt)
    )
    db.commit()
    return salt
