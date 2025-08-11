"""
VaultService: business logic for CRUD vault entries.
All data is handled as encrypted_entry (string, encrypted JSON).
"""


from backend.vault.interfaces import IVaultRepository
from backend.vault.crypto_utils import encrypt_entry, decrypt_entry
from backend.vault.salt_utils import get_or_create_user_salt



class VaultService:
    def __init__(self, repo: IVaultRepository):
        self.repo = repo

    def list_entries(self, user_id, password=None):
        entries = self.repo.list_entries(user_id)
        if password:
            salt = get_or_create_user_salt(user_id)
            for entry in entries:
                try:
                    entry['decrypted'] = decrypt_entry(entry['encrypted_entry'], password, salt)
                except Exception:
                    entry['decrypted'] = None
        return entries

    def add_entry(self, user_id, data, password=None):
        # data: dict (plaintext fields)
        if password:
            salt = get_or_create_user_salt(user_id)
            encrypted = encrypt_entry(data, password, salt)
            return self.repo.add_entry(user_id, {"encrypted_entry": encrypted})
        # fallback: expects already encrypted
        return self.repo.add_entry(user_id, data)

    def get_entry(self, user_id, entry_id, password=None):
        entry = self.repo.get_entry(user_id, entry_id)
        if entry and password:
            salt = get_or_create_user_salt(user_id)
            try:
                entry['decrypted'] = decrypt_entry(entry['encrypted_entry'], password, salt)
            except Exception:
                entry['decrypted'] = None
        return entry

    def update_entry(self, user_id, entry_id, data, password=None):
        if password:
            salt = get_or_create_user_salt(user_id)
            encrypted = encrypt_entry(data, password, salt)
            return self.repo.update_entry(user_id, entry_id, {"encrypted_entry": encrypted})
        return self.repo.update_entry(user_id, entry_id, data)

    def delete_entry(self, user_id, entry_id):
        return self.repo.delete_entry(user_id, entry_id)
