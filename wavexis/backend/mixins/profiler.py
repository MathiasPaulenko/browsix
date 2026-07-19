"""Profiler mixin — CPU profiler operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProfilerBackend(ABC):
    """CPU profiler operations for sampling and code coverage."""

    @abstractmethod
    async def profiler_disable(self) -> None:
        """Disable the Profiler domain."""

    @abstractmethod
    async def profiler_enable(self) -> None:
        """Enable the Profiler domain."""

    @abstractmethod
    async def profiler_get_best_effort_coverage(self) -> dict[str, Any]:
        """Get best effort coverage data."""

    @abstractmethod
    async def profiler_set_sampling_interval(self, interval: int) -> None:
        """Set the CPU sampling interval in microseconds.

        Args:
            interval: Sampling interval in microseconds.
        """

    @abstractmethod
    async def profiler_start(self) -> None:
        """Start CPU profiling."""

    @abstractmethod
    async def profiler_start_precise_coverage(
        self,
        call_count: bool = False,
        detailed: bool = False,
    ) -> dict[str, Any]:
        """Start precise code coverage tracking.

        Args:
            call_count: Whether to collect call count info.
            detailed: Whether to collect detailed coverage info.

        Returns:
            Dict containing the timestamp of the coverage update.
        """

    @abstractmethod
    async def profiler_stop(self) -> dict[str, Any]:
        """Stop CPU profiling and return the profile data."""

    @abstractmethod
    async def profiler_stop_precise_coverage(self) -> None:
        """Stop precise code coverage tracking."""

    @abstractmethod
    async def profiler_take_precise_coverage(self) -> dict[str, Any]:
        """Take a snapshot of precise code coverage data."""
