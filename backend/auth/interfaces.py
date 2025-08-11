from abc import ABC, abstractmethod
from typing import Any


class IRegistrationValidator(ABC):
    """Interface for registration validation."""

    @abstractmethod
    def validate(self, email: str, password: str) -> None:
        """Validate registration data."""
        pass


class IUserRepository(ABC):
    """Interface for user repository."""

    @abstractmethod
    def is_email_taken(self, email: str) -> bool:
        pass

    @abstractmethod
    def create_user(self, email: str, password_hash: str) -> None:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> dict | None:
        pass


class IPasswordHasher(ABC):
    """Interface for password hashing."""

    @abstractmethod
    def hash(self, password: str) -> str:
        pass


# --- SOLID: Auth Provider Abstraction ---
class IAuthProvider(ABC):
    """Interface for authentication provider (e.g., JWT)."""

    @abstractmethod
    def require_auth(self, fn):
        """Decorator to require authentication on a route."""
        pass

    @abstractmethod
    def get_identity(self) -> Any:
        """Get the current user's identity (user_id, etc)."""
        pass
