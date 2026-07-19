"""Memory mixin — memory pressure and sampling operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MemoryBackend(ABC):
    """Memory domain operations."""

    @abstractmethod
    async def memory_forcibly_purge_javascript_memory(self) -> None:
        """Forcibly purge JavaScript memory."""

    @abstractmethod
    async def memory_get_all_time_sampling_profile(self) -> dict[str, Any]:
        """Get the all-time sampling profile."""

    @abstractmethod
    async def memory_get_browser_sampling_profile(self) -> dict[str, Any]:
        """Get the browser sampling profile."""

    @abstractmethod
    async def memory_get_dom_counters(self) -> dict[str, Any]:
        """Get DOM counters."""

    @abstractmethod
    async def memory_get_dom_counters_for_leak_detection(self) -> dict[str, Any]:
        """Get DOM counters for leak detection."""

    @abstractmethod
    async def memory_get_sampling_profile(self) -> dict[str, Any]:
        """Get the current sampling profile."""

    @abstractmethod
    async def memory_prepare_for_leak_detection(self) -> None:
        """Prepare for leak detection."""

    @abstractmethod
    async def memory_set_pressure_notifications_suppressed(self, suppressed: bool) -> None:
        """Set pressure notifications suppressed state."""

    @abstractmethod
    async def memory_simulate_pressure_notification(self, level: str) -> None:
        """Simulate a memory pressure notification."""

    @abstractmethod
    async def memory_start_sampling(self, sampling_interval: int = 0) -> None:
        """Start memory sampling."""

    @abstractmethod
    async def memory_stop_sampling(self) -> None:
        """Stop memory sampling."""
