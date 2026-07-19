"""DOMStorage mixin — DOM storage (localStorage, sessionStorage) operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DOMStorageBackend(ABC):
    """DOM storage operations."""

    @abstractmethod
    async def dom_storage_clear(self, storage_id: dict[str, Any]) -> None:
        """Clear all entries in a DOM storage."""

    @abstractmethod
    async def dom_storage_clear_items(self, storage_id: dict[str, Any]) -> None:
        """Clear all items in a DOM storage (alias)."""

    @abstractmethod
    async def dom_storage_disable(self) -> None:
        """Disable the DOMStorage domain."""

    @abstractmethod
    async def dom_storage_enable(self) -> None:
        """Enable the DOMStorage domain."""

    @abstractmethod
    async def dom_storage_get_items(self, storage_id: dict[str, Any]) -> list[dict[str, Any]]:
        """Get all items in a DOM storage."""

    @abstractmethod
    async def dom_storage_remove_item(self, storage_id: dict[str, Any], key: str) -> None:
        """Remove an item from a DOM storage."""

    @abstractmethod
    async def dom_storage_set_item(self, storage_id: dict[str, Any], key: str, value: str) -> None:
        """Set an item in a DOM storage."""
