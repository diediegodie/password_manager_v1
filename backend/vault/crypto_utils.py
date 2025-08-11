"""
Encryption utilities for vault entries using Fernet.
Key is derived from user password using PBKDF2HMAC.
"""

import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_entry(data: dict, password: str, salt: bytes) -> str:
    """Encrypt a dict as a Fernet string using a user password and salt."""
    import json

    key = derive_key(password, salt)
    f = Fernet(key)
    plaintext = json.dumps(data).encode()
    return f.encrypt(plaintext).decode()


def decrypt_entry(token: str, password: str, salt: bytes) -> dict:
    """Decrypt a Fernet string to dict using a user password and salt."""
    import json

    key = derive_key(password, salt)
    f = Fernet(key)
    plaintext = f.decrypt(token.encode())
    return json.loads(plaintext.decode())
