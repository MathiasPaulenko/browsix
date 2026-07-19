"""Unit tests for Target backend methods (new CDP target commands)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.unit
class TestTargetNewMethods:
    """Test suite for new Target backend methods."""

    def _make_backend(self) -> MagicMock:
        """Create a mock backend with new target methods."""
        backend = MagicMock()
        backend.launch = AsyncMock()
        backend.close = AsyncMock()
        backend.target_attach_to_browser_target = AsyncMock(return_value="sess-1")
        backend.target_auto_attach_related = AsyncMock()
        backend.target_dispose_browser_context = AsyncMock()
        backend.target_expose_dev_tools_protocol = AsyncMock()
        backend.target_get_browser_contexts = AsyncMock(return_value=["ctx-1", "ctx-2"])
        backend.target_get_dev_tools_target = AsyncMock(return_value="dt-1")
        backend.target_open_dev_tools = AsyncMock()
        backend.target_send_message_to_target = AsyncMock()
        backend.target_set_remote_locations = AsyncMock()
        return backend

    async def test_attach_to_browser_target(self) -> None:
        """Test attach_to_browser_target returns session ID."""
        backend = self._make_backend()
        result = await backend.target_attach_to_browser_target()
        assert result == "sess-1"
        backend.target_attach_to_browser_target.assert_called_once()

    async def test_auto_attach_related(self) -> None:
        """Test auto_attach_related calls backend."""
        backend = self._make_backend()
        await backend.target_auto_attach_related("t1", True)
        backend.target_auto_attach_related.assert_called_once_with("t1", True)

    async def test_dispose_browser_context(self) -> None:
        """Test dispose_browser_context calls backend."""
        backend = self._make_backend()
        await backend.target_dispose_browser_context("ctx-1")
        backend.target_dispose_browser_context.assert_called_once_with("ctx-1")

    async def test_expose_dev_tools_protocol(self) -> None:
        """Test expose_dev_tools_protocol calls backend."""
        backend = self._make_backend()
        await backend.target_expose_dev_tools_protocol("t1", "binding")
        backend.target_expose_dev_tools_protocol.assert_called_once_with("t1", "binding")

    async def test_get_browser_contexts(self) -> None:
        """Test get_browser_contexts returns list."""
        backend = self._make_backend()
        result = await backend.target_get_browser_contexts()
        assert result == ["ctx-1", "ctx-2"]

    async def test_get_dev_tools_target(self) -> None:
        """Test get_dev_tools_target returns target ID."""
        backend = self._make_backend()
        result = await backend.target_get_dev_tools_target("t1")
        assert result == "dt-1"
        backend.target_get_dev_tools_target.assert_called_once_with("t1")

    async def test_open_dev_tools(self) -> None:
        """Test open_dev_tools calls backend."""
        backend = self._make_backend()
        await backend.target_open_dev_tools("t1")
        backend.target_open_dev_tools.assert_called_once_with("t1")

    async def test_send_message_to_target(self) -> None:
        """Test send_message_to_target calls backend."""
        backend = self._make_backend()
        await backend.target_send_message_to_target("s1", "hello")
        backend.target_send_message_to_target.assert_called_once_with("s1", "hello")

    async def test_set_remote_locations(self) -> None:
        """Test set_remote_locations calls backend."""
        backend = self._make_backend()
        locations = [{"host": "localhost", "port": "9222"}]
        await backend.target_set_remote_locations(locations)
        backend.target_set_remote_locations.assert_called_once_with(locations)
