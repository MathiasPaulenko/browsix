"""Security mixin — certificate error handling and security state inspection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SecurityBackend(ABC):
    """Security domain for monitoring and handling certificate errors."""

    @abstractmethod
    async def security_disable(self) -> None:
        """Disable the Security domain."""

    @abstractmethod
    async def security_enable(self) -> None:
        """Enable the Security domain."""

    @abstractmethod
    async def security_get_visible_security_state(self) -> dict[str, Any]:
        """Get the visible security state of the current page.

        Returns:
            Dict containing the security state information.
        """

    @abstractmethod
    async def security_handle_certificate_error(self, event_id: int, action: str) -> None:
        """Handle a certificate error event.

        Args:
            event_id: The ID of the certificate error event.
            action: The action to take (e.g. "continue", "cancel").
        """

    @abstractmethod
    async def security_set_ignore_certificate_errors(self, ignore: bool) -> None:
        """Set whether to ignore certificate errors.

        Args:
            ignore: Whether to ignore certificate errors.
        """

    @abstractmethod
    async def security_set_override_certificate_errors(self, override: bool) -> None:
        """Set whether to override certificate errors.

        Args:
            override: Whether to override certificate errors.
        """
