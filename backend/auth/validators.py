import re
from abc import ABC, abstractmethod


class ValidationError(Exception):
    """Raised when registration data is invalid."""

    pass


class IValidator(ABC):
    """Interface for validators."""

    @abstractmethod
    def validate(self, value: str) -> None:
        """Validate the given value."""
        pass


class EmailValidator(IValidator):
    """Validates email addresses."""

    _email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def validate(self, value: str) -> None:
        if not isinstance(value, str) or not self._email_regex.match(value):
            raise ValidationError("Invalid email format.")


class PasswordValidator(IValidator):
    """Validates passwords."""

    def validate(self, value: str) -> None:
        if not isinstance(value, str) or len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise ValidationError(
                "Password must contain at least one letter and one number."
            )


# Import the interface from interfaces.py to avoid circular import
from .interfaces import IRegistrationValidator


class RegistrationValidator(IRegistrationValidator):
    """Validates registration data using injected validators."""

    def __init__(self, email_validator: IValidator, password_validator: IValidator):
        self._email_validator = email_validator
        self._password_validator = password_validator

    def validate(self, email: str, password: str) -> None:
        self._email_validator.validate(email)
        self._password_validator.validate(password)


# Usage example (do not remove, but do not execute at import time)
# email_validator = EmailValidator()
# password_validator = PasswordValidator()
# registration_validator = RegistrationValidator(email_validator, password_validator)
# registration_validator.validate(email, password)

# Login validation for login endpoint
def validate_login_data(email: str, password: str) -> None:
    """Validate login data: email format and non-empty password."""
    email_validator = EmailValidator()
    if not isinstance(password, str) or not password:
        raise ValidationError("Password must not be empty.")
    email_validator.validate(email)