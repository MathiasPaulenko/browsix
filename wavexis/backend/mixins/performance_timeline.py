"""Performance timeline mixin — performance timeline events."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PerformanceTimelineBackend(ABC):
    """Performance timeline event tracking."""

    @abstractmethod
    async def performance_timeline_enable(self) -> None:
        """Enable the PerformanceTimeline domain to start receiving timeline events."""
