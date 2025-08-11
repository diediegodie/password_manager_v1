import pytest
from backend.vault.crypto_utils import encrypt_entry, decrypt_entry, derive_key
from backend.vault.salt_utils import get_or_create_user_salt
import os


@pytest.fixture
def test_data():
    return {"service": "github", "username": "octocat", "password": "supersecret"}


def test_fernet_encrypt_decrypt_roundtrip(test_data):
    password = "userpassword123"
    salt = os.urandom(16)
    encrypted = encrypt_entry(test_data, password, salt)
    assert isinstance(encrypted, str)
    decrypted = decrypt_entry(encrypted, password, salt)
    assert decrypted == test_data


def test_fernet_decrypt_wrong_password(test_data):
    password = "userpassword123"
    salt = os.urandom(16)
    encrypted = encrypt_entry(test_data, password, salt)
    with pytest.raises(Exception):
        decrypt_entry(encrypted, "wrongpassword", salt)


def test_fernet_decrypt_wrong_salt(test_data):
    password = "userpassword123"
    salt = os.urandom(16)
    encrypted = encrypt_entry(test_data, password, salt)
    wrong_salt = os.urandom(16)
    with pytest.raises(Exception):
        decrypt_entry(encrypted, password, wrong_salt)


def test_derive_key_consistency():
    password = "abc123"
    salt = b"1234567890123456"
    key1 = derive_key(password, salt)
    key2 = derive_key(password, salt)
    assert key1 == key2


def test_get_or_create_user_salt(tmp_path, monkeypatch):
    # Patch get_db to use a temp sqlite file
    import sqlite3
    from backend.vault import salt_utils

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE user_salts (user_id INTEGER PRIMARY KEY, salt BLOB NOT NULL)"
    )
    conn.commit()
    monkeypatch.setattr(salt_utils, "get_db", lambda: conn)
    salt1 = salt_utils.get_or_create_user_salt(42)
    assert isinstance(salt1, bytes)
    salt2 = salt_utils.get_or_create_user_salt(42)
    assert salt1 == salt2
    salt3 = salt_utils.get_or_create_user_salt(99)
    assert salt1 != salt3
