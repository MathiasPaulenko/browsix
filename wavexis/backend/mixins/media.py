"""Media mixin — media player enable/disable operations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MediaBackend(ABC):
    """Media domain operations."""

    @abstractmethod
    async def media_disable(self) -> None:
        """Disable the Media domain."""

    @abstractmethod
    async def media_enable(self) -> None:
        """Enable the Media domain."""
