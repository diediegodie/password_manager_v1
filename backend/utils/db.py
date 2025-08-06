import os
import sqlite3
import logging
from typing import Any, Protocol, Optional


class IPathResolver(Protocol):
    """Abstraction for resolving database file paths."""
    def resolve_db_path(self, db_path: Optional[str] = None) -> str:
        ...


class ILogger(Protocol):
    """Abstraction for logging."""
    def error(self, msg: str) -> None:
        ...


class PathResolver(IPathResolver):
    def resolve_db_path(self, db_path: Optional[str] = None) -> str:
        if db_path is not None:
            return os.path.abspath(db_path)
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../database/password_manager.db"
            )
        )


class IDatabaseConnection(Protocol):
    def get_connection(self) -> sqlite3.Connection:
        ...


class SQLiteConnection(IDatabaseConnection):
    def __init__(
        self,
        db_path: Optional[str] = None,
        logger: Optional[ILogger] = None,
        path_resolver: Optional[IPathResolver] = None,
    ) -> None:
        self._path_resolver = path_resolver or PathResolver()
        self._db_path = self._path_resolver.resolve_db_path(db_path)
        self._logger = logger or logging.getLogger("SQLiteConnection")

    def get_connection(self) -> sqlite3.Connection:
        if not os.path.isfile(self._db_path):
            self._logger.error(f"Database file not found at {self._db_path}")
            raise FileNotFoundError(f"Database file not found at {self._db_path}")
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            self._logger.error(f"Failed to connect to database: {e}")
            raise Exception(f"Failed to connect to database: {e}")
