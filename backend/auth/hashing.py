# Standard library
from abc import ABC, abstractmethod
from typing import Any

# Third-party
import bcrypt


class PasswordHasher(ABC):
    """Abstract base class for password hashing."""
    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plaintext password.
        Args:
            password (str): The plaintext password to hash.
        Returns:
            str: The hashed password.
        Raises:
            ValueError: If the password is invalid.
            Exception: For unexpected hashing errors.
        """
        pass


class BcryptPasswordHasher(PasswordHasher):
    """Password hasher implementation using bcrypt."""
    def hash(self, password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        Args:
            password (str): The plaintext password to hash.
        Returns:
            str: The bcrypt hash of the password.
        Raises:
            ValueError: If the password is empty or not a string.
            Exception: For unexpected hashing errors.
        """
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string.")
        try:
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode("utf-8")
        except Exception as e:
            # Log the error in production
            raise Exception(f"Password hashing failed: {e}")
