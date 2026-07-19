"""Log mixin — log entry and violations reporting operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LogBackend(ABC):
    """Log domain operations."""

    @abstractmethod
    async def log_clear(self) -> None:
        """Clear the log."""

    @abstractmethod
    async def log_disable(self) -> None:
        """Disable the Log domain."""

    @abstractmethod
    async def log_enable(self) -> None:
        """Enable the Log domain."""

    @abstractmethod
    async def log_start_violations_report(self, config: list[dict[str, Any]]) -> None:
        """Start reporting violations."""

    @abstractmethod
    async def log_stop_violations_report(self) -> None:
        """Stop reporting violations."""
