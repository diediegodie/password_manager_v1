class DuplicateEmailError(Exception):
    """Raised when attempting to register a duplicate email address."""

    pass


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    pass


class HashingError(Exception):
    """Raised when password hashing fails."""

    pass
