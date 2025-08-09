"""
VaultRepository: DB access for vault entries.
"""

from backend.utils.db import get_db


class VaultRepository:
    def __init__(self, db=None):
        self.db = db or get_db()

    def list_entries(self, user_id):
        cur = self.db.execute(
            "SELECT id, encrypted_entry FROM vault WHERE user_id = ?", (user_id,)
        )
        return [dict(row) for row in cur.fetchall()]

    def add_entry(self, user_id, data):
        # data['encrypted_entry'] should be a string (already encrypted JSON)
        cur = self.db.execute(
            "INSERT INTO vault (user_id, encrypted_entry) VALUES (?, ?)",
            (user_id, data["encrypted_entry"]),
        )
        self.db.commit()
        entry_id = cur.lastrowid
        return self.get_entry(user_id, entry_id)

    def get_entry(self, user_id, entry_id):
        cur = self.db.execute(
            "SELECT id, encrypted_entry FROM vault WHERE user_id = ? AND id = ?",
            (user_id, entry_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def update_entry(self, user_id, entry_id, data):
        # data['encrypted_entry'] should be a string (already encrypted JSON)
        self.db.execute(
            "UPDATE vault SET encrypted_entry = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND id = ?",
            (data["encrypted_entry"], user_id, entry_id),
        )
        self.db.commit()
        return self.get_entry(user_id, entry_id)

    def delete_entry(self, user_id, entry_id):
        cur = self.db.execute(
            "DELETE FROM vault WHERE user_id = ? AND id = ?", (user_id, entry_id)
        )
        self.db.commit()
        return cur.rowcount > 0
