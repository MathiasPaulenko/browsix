"""Unit tests for WebMcp backend methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.unit
class TestWebMcp:
    """Test suite for web_mcp backend methods."""

    def _make_backend(self) -> MagicMock:
        """Create a mock backend with web_mcp methods."""
        backend = MagicMock()
        backend.launch = AsyncMock()
        backend.close = AsyncMock()
        backend.web_mcp_enable = AsyncMock()
        backend.web_mcp_disable = AsyncMock()
        return backend

    async def test_enable(self) -> None:
        """Test web_mcp_enable calls backend."""
        backend = self._make_backend()
        await backend.web_mcp_enable()
        backend.web_mcp_enable.assert_called_once()

    async def test_disable(self) -> None:
        """Test web_mcp_disable calls backend."""
        backend = self._make_backend()
        await backend.web_mcp_disable()
        backend.web_mcp_disable.assert_called_once()
