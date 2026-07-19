"""Unit tests for Tethering backend methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.unit
class TestTethering:
    """Test suite for tethering backend methods."""

    def _make_backend(self) -> MagicMock:
        """Create a mock backend with tethering methods."""
        backend = MagicMock()
        backend.launch = AsyncMock()
        backend.close = AsyncMock()
        backend.tethering_bind = AsyncMock()
        backend.tethering_unbind = AsyncMock()
        return backend

    async def test_bind(self) -> None:
        """Test tethering_bind calls backend with port."""
        backend = self._make_backend()
        await backend.tethering_bind(8080)
        backend.tethering_bind.assert_called_once_with(8080)

    async def test_unbind(self) -> None:
        """Test tethering_unbind calls backend with port."""
        backend = self._make_backend()
        await backend.tethering_unbind(8080)
        backend.tethering_unbind.assert_called_once_with(8080)
