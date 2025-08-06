from abc import ABC, abstractmethod


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


class IPasswordHasher(ABC):
    """Interface for password hashing."""

    @abstractmethod
    def hash(self, password: str) -> str:
        pass
