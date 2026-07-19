"""Network interception, cookies, and HAR mixin."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from wavexis.config import CookieParams, HarParams, ThrottleParams


class NetworkBackend(ABC):
    """Network capture, cookies, headers, interception, and HAR replay."""

    @abstractmethod
    async def capture_har(self, params: HarParams) -> dict[str, Any]:
        """Navigate to a URL and capture network traffic as HAR 1.2 dict."""

    @abstractmethod
    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies for the current page."""

    @abstractmethod
    async def set_cookie(self, params: CookieParams) -> None:
        """Set a cookie in the browser."""

    @abstractmethod
    async def delete_cookie(self, name: str, domain: str) -> None:
        """Delete cookies matching name and domain."""

    @abstractmethod
    async def clear_cookies(self) -> None:
        """Clear all browser cookies."""

    @abstractmethod
    async def set_headers(self, headers: dict[str, str]) -> None:
        """Set extra HTTP headers for all requests."""

    @abstractmethod
    async def set_user_agent(self, user_agent: str) -> None:
        """Override the browser's User-Agent string."""

    @abstractmethod
    async def block_requests(self, patterns: list[str]) -> None:
        """Block requests matching URL patterns (glob-style)."""

    @abstractmethod
    async def throttle_network(self, params: ThrottleParams) -> None:
        """Throttle network conditions (latency, throughput, offline)."""

    @abstractmethod
    async def set_cache_disabled(self, disabled: bool = True) -> None:
        """Disable or enable the browser cache."""

    @abstractmethod
    async def intercept_requests(self, pattern: dict[str, Any]) -> None:
        """Intercept requests matching a pattern dict."""

    @abstractmethod
    async def mock_response(self, url: str, response: dict[str, Any]) -> None:
        """Mock a response for requests matching a URL pattern."""

    @abstractmethod
    async def get_request_body(self, request_id: str) -> str | None:
        """Get the body of a network request by ID.

        Args:
            request_id: The CDP/BiDi network request ID.

        Returns:
            The request body as a string, or None if not available.
        """

    @abstractmethod
    async def get_response_body(self, request_id: str) -> str | None:
        """Get the body of a network response by ID.

        Args:
            request_id: The CDP/BiDi network request ID.

        Returns:
            The response body as a string, or None if not available.
        """

    @abstractmethod
    async def modify_request(
        self,
        pattern: dict[str, Any],
        modifications: dict[str, Any],
    ) -> None:
        """Intercept and modify requests matching a pattern.

        Args:
            pattern: Pattern dict with optional keys: urlPattern, resourceType,
                requestStage.
            modifications: Dict with optional keys: headers, url, method, post_data.
        """

    @abstractmethod
    async def modify_response(
        self,
        pattern: dict[str, Any],
        modifications: dict[str, Any],
    ) -> None:
        """Intercept responses matching a pattern and modify them in-flight.

        Args:
            pattern: Pattern dict with optional keys: urlPattern, resourceType,
                requestStage (should be "Response").
            modifications: Dict with optional keys: status, headers, body.
        """

    @abstractmethod
    async def replay_har(self, har_path: str, url_filter: str = "") -> None:
        """Replay network requests from a HAR file.

        Args:
            har_path: Path to the HAR file.
            url_filter: Optional URL pattern to filter which entries to replay.
        """

    @abstractmethod
    async def handle_auth(
        self,
        url_pattern: str,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Handle HTTP authentication challenges for matching requests.

        Args:
            url_pattern: URL pattern to match auth challenges.
            username: Username to provide. If None, auth is canceled.
            password: Password to provide.
        """

    @abstractmethod
    async def network_clear_browser_cache(self) -> None:
        """Clear the browser cache."""

    @abstractmethod
    async def network_clear_browser_cookies(self) -> None:
        """Clear all browser cookies."""

    @abstractmethod
    async def network_delete_cookies(self, name: str, domain: str = "") -> None:
        """Delete cookies by name and optional domain."""

    @abstractmethod
    async def network_set_blocked_urls(self, urls: list[str]) -> None:
        """Block requests to specific URLs."""

    @abstractmethod
    async def network_set_bypass_service_worker(self, bypass: bool) -> None:
        """Bypass the service worker for all network requests."""

    @abstractmethod
    async def network_set_cookie_controls(
        self, mode: str = "allow", third_party_mode: str = "allow"
    ) -> None:
        """Set cookie controls (allow, block, only-existing)."""

    @abstractmethod
    async def network_set_extra_request_headers(self, headers: dict[str, str]) -> None:
        """Set extra HTTP headers for all requests."""

    @abstractmethod
    async def network_set_user_agent_override(
        self, user_agent: str, accept_language: str = "", platform: str = ""
    ) -> None:
        """Override the User-Agent string with metadata."""

    @abstractmethod
    async def network_replay_xhr(self, request_id: str) -> None:
        """Replay a previously captured XHR request by ID."""

    @abstractmethod
    async def network_load_network_resource(
        self, frame_id: str, url: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Load a network resource outside the context of a page."""
