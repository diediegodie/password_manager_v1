"""
VaultService: business logic for CRUD vault entries.
All data is handled as encrypted_entry (string, encrypted JSON).
"""

from backend.vault.repository import VaultRepository


class VaultService:
    def __init__(self, repo: VaultRepository):
        self.repo = repo

    def list_entries(self, user_id):
        return self.repo.list_entries(user_id)

    def add_entry(self, user_id, data):
        return self.repo.add_entry(user_id, data)

    def get_entry(self, user_id, entry_id):
        return self.repo.get_entry(user_id, entry_id)

    def update_entry(self, user_id, entry_id, data):
        return self.repo.update_entry(user_id, entry_id, data)

    def delete_entry(self, user_id, entry_id):
        return self.repo.delete_entry(user_id, entry_id)
