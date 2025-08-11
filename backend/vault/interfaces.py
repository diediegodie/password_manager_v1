from abc import ABC, abstractmethod
from typing import Any


class IVaultRepository(ABC):
    """Interface for VaultRepository."""

    @abstractmethod
    def list_entries(self, user_id: int) -> list[dict]:
        pass

    @abstractmethod
    def add_entry(self, user_id: int, data: dict) -> dict | None:
        pass

    @abstractmethod
    def get_entry(self, user_id: int, entry_id: int) -> dict | None:
        pass

    @abstractmethod
    def update_entry(self, user_id: int, entry_id: int, data: dict) -> dict | None:
        pass

    @abstractmethod
    def delete_entry(self, user_id: int, entry_id: int) -> None:
        pass


class IVaultService(ABC):
    """Interface for VaultService."""

    @abstractmethod
    def list_entries(self, user_id: int) -> list[dict]:
        pass

    @abstractmethod
    def add_entry(self, user_id: int, data: dict) -> dict | None:
        pass

    @abstractmethod
    def get_entry(self, user_id: int, entry_id: int) -> dict | None:
        pass

    @abstractmethod
    def update_entry(self, user_id: int, entry_id: int, data: dict) -> dict | None:
        pass

    @abstractmethod
    def delete_entry(self, user_id: int, entry_id: int) -> None:
        pass
