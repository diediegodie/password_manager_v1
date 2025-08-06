from .interfaces import (
    IPasswordHasher,
)  # import from interfaces to avoid circular import
import bcrypt


class BcryptPasswordHasher(IPasswordHasher):
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
            HashingError: For unexpected hashing errors.
        """
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string.")

        from backend.auth.exceptions import HashingError

        try:
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode("utf-8")
        except Exception as e:
            # Log the error in production
            raise HashingError(f"Password hashing failed: {e}")
