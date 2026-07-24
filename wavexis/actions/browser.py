"""Browser action for context and window management."""

from __future__ import annotations

from typing import Any

from wavexis.actions.base import BaseAction
from wavexis.backend.base import AbstractBackend
from wavexis.exceptions import ActionError


class BrowserAction(BaseAction[str, Any]):
    """Action for browser management operations.

    The params string specifies the action:

    - ``version`` — return the browser version string.
    - ``new_context`` — create a new browser context and return its ID.
    - ``list_contexts`` — return the list of browser contexts.
    - ``close_context`` — close the context given by ``context_id``.
    - ``get_window`` — return the current window bounds.
    - ``set_window`` — set the window bounds using ``width``, ``height``,
      ``x`` and ``y``.
    """

    def __init__(
        self,
        params: str,
        *,
        context_id: str | None = None,
        width: int | None = None,
        height: int | None = None,
        x: int = 0,
        y: int = 0,
    ) -> None:
        """Initialize the browser action.

        Args:
            params: Action name (version, new_context, list_contexts,
                close_context, get_window, set_window).
            context_id: Target context ID for ``close_context``.
            width: Window width for ``set_window``.
            height: Window height for ``set_window``.
            x: Window X position for ``set_window`` (default 0).
            y: Window Y position for ``set_window`` (default 0).
        """
        super().__init__(params)
        self.context_id = context_id
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    async def execute(self, backend: AbstractBackend) -> Any:
        """Execute the browser action.

        Args:
            backend: The browser backend to use.

        Returns:
            Action-dependent result (str, list, dict, or None).

        Raises:
            ActionError: When a required argument is missing or the action
                is unknown.
        """
        action = self.params

        if action == "version":
            return await backend.browser_version()

        if action == "new_context":
            return await backend.new_context()

        if action == "list_contexts":
            return await backend.list_contexts()

        if action == "close_context":
            if self.context_id is None:
                raise ActionError("--context-id is required for close_context")
            return await backend.close_context(self.context_id)

        if action == "get_window":
            return await backend.get_window_bounds()

        if action == "set_window":
            if self.width is None or self.height is None:
                raise ActionError("--width and --height are required for set_window")
            return await backend.set_window_bounds(self.width, self.height, self.x, self.y)

        raise ActionError(f"Unknown browser action: {action}")
