# backend/auth/repository.py
from ..utils.db import SQLiteConnection
from .interfaces import IUserRepository


class UserRepository(IUserRepository):
    """Concrete implementation of IUserRepository using SQLite."""

    def __init__(self, db_connection: SQLiteConnection) -> None:
        """
        Initialize UserRepository with a database connection.
        Args:
            db_connection (SQLiteConnection): The database connection abstraction.
        """
        self._db_connection = db_connection

    def create_user(self, email: str, password_hash: str) -> None:
        """
        Create a new user in the database.
        Args:
            email (str): The user's email address.
            password_hash (str): The hashed password.
        Raises:
            ValueError: If email or password_hash are not strings.
            DuplicateEmailError: If the email is already registered.
            DatabaseError: If a database error occurs.
        """
        if not isinstance(email, str) or not isinstance(password_hash, str):
            raise ValueError("Email and password_hash must be strings.")
        normalized_email = email.strip().lower()
        conn = None

    def get_user_by_email(self, email: str) -> dict | None:
        """
        Fetch a user by normalized email. Returns dict or None.
        Args:
            email (str): The email address to look up.
        Returns:
            dict: {"id": ..., "email": ..., "password_hash": ...} or None
        Raises:
            DatabaseError: If a database error occurs.
        """
        if not isinstance(email, str):
            raise ValueError("Email must be a string.")
        normalized_email = email.strip().lower()
        conn = None
        cursor = None
        from backend.auth.exceptions import DatabaseError

        try:
            conn = self._db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ? LIMIT 1",
                (normalized_email,),
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "password_hash": row[2]}
            return None
        except Exception as e:
            raise DatabaseError(f"Database error during user lookup: {e}")
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def is_email_taken(self, email: str) -> bool:
        """
        Check if an email exists in the users table.
        Args:
            email (str): The email address to check.
        Returns:
            bool: True if the email exists, False otherwise.
        Raises:
            DatabaseError: If a database error occurs.
        """
        if not isinstance(email, str):
            raise ValueError("Email must be a string.")
        normalized_email = email.strip().lower()
        conn = None
        cursor = None
        from backend.auth.exceptions import DatabaseError

        try:
            conn = self._db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE email = ? LIMIT 1", (normalized_email,)
            )
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            # Log error in production
            raise DatabaseError(f"Database error during email check: {e}")
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
