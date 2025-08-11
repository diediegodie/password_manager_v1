"""
SQLite database initialization for password manager.
Creates users table if not exists.

Follows SOLID principles and PEP8.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "password_manager.db"

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
"""

CREATE_VAULT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS vault (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    encrypted_entry TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

CREATE_SALTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_salts (
    user_id INTEGER PRIMARY KEY,
    salt BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def get_db_connection():
    """Get a SQLite connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Initialize the database and create required tables if not present."""
    if not DB_PATH.exists():
        # Ensure parent directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.execute(CREATE_USERS_TABLE_SQL)
        conn.execute(CREATE_VAULT_TABLE_SQL)
        conn.execute(CREATE_SALTS_TABLE_SQL)
        conn.commit()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized. Users and vault tables created (if not exist).")
