"""Preload mixin — preload operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PreloadBackend(ABC):
    """Preload operations for managing preload and prefetch hints."""

    @abstractmethod
    async def preload_disable(self) -> None:
        """Disable the Preload domain."""

    @abstractmethod
    async def preload_enable(self) -> None:
        """Enable the Preload domain."""

    @abstractmethod
    async def preload_get_preload_policy(self) -> dict[str, Any]:
        """Get the current preload policy."""

    @abstractmethod
    async def preload_set_preload_policy(self, policy: dict[str, Any]) -> None:
        """Set the preload policy.

        Args:
            policy: Preload policy configuration dictionary.
        """
