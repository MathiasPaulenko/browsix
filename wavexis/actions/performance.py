"""Performance action for metrics, tracing, profiling, heap, and coverage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from wavexis.actions.base import BaseAction
from wavexis.backend.base import AbstractBackend
from wavexis.config import BrowserOptions, WaitStrategy, _validate_url
from wavexis.exceptions import ActionError


@dataclass
class PerformanceParams:
    """Parameters for performance operations.

    Attributes:
        url: URL to navigate to before collecting performance data.
        action: Performance action — "metrics", "trace", "profile",
            "heap", "coverage", "css-coverage".
        duration_ms: Duration in milliseconds for trace and profile actions.
        wait: Wait strategy after navigation.
        browser: Browser launch options.
    """

    url: str = ""
    action: str = "metrics"
    duration_ms: int = 3000
    wait: WaitStrategy = field(default_factory=WaitStrategy)
    browser: BrowserOptions = field(default_factory=BrowserOptions)

    def __post_init__(self) -> None:
        """Validate performance parameters."""
        _validate_url(self.url)
        if self.duration_ms <= 0:
            raise ActionError(f"duration_ms must be positive; got {self.duration_ms}")


class PerformanceAction(BaseAction[PerformanceParams, dict[str, Any]]):
    """Action for collecting performance data from a web page."""

    async def execute(self, backend: AbstractBackend) -> dict[str, Any]:
        """Execute the performance action on the backend.

        Args:
            backend: The browser backend to use.

        Returns:
            Dict containing the performance data.

        Raises:
            ValueError: If the action is not recognized.
        """
        if self.params.url:
            await backend.navigate(self.params.url, self.params.wait)
        return await self._run_action(backend)

    async def _run_action(self, backend: AbstractBackend) -> dict[str, Any]:
        """Execute the performance action against the backend.

        Args:
            backend: The browser backend to use.

        Returns:
            Performance data as a dictionary.

        Raises:
            ValueError: If the action is not recognized.
        """
        action = self.params.action
        if action == "metrics":
            return await backend.perf_metrics()
        if action == "trace":
            return await backend.perf_trace(self.params.duration_ms)
        if action == "profile":
            return await backend.perf_profile(self.params.duration_ms)
        if action == "heap":
            return await backend.perf_heap_snapshot()
        if action == "coverage":
            return await backend.perf_coverage()
        if action == "css-coverage":
            return await backend.perf_css_coverage()
        raise ActionError(f"Unknown performance action: {action}")
