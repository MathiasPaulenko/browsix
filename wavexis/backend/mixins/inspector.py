"""Inspector mixin — inspector operations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class InspectorBackend(ABC):
    """Inspector operations."""

    @abstractmethod
    async def inspector_disable(self) -> None:
        """Disable the Inspector domain."""

    @abstractmethod
    async def inspector_enable(self) -> None:
        """Enable the Inspector domain."""
