"""Unit tests for SystemInfoAction."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis.actions.system_info import SystemInfoAction
from wavexis.config import SystemInfoParams


@pytest.mark.unit
class TestSystemInfoAction:
    """Test suite for system_info action."""

    def _make_backend(self) -> MagicMock:
        """Create a mock backend for testing.

        Returns:
            A MagicMock backend instance.
        """
        backend = MagicMock()
        backend.launch = AsyncMock()
        backend.navigate = AsyncMock()
        backend.close = AsyncMock()
        backend.system_info_get_info = AsyncMock(
            return_value={"os": "linux", "gpu": {"vendor": "NVIDIA"}}
        )
        backend.system_info_get_process_info = AsyncMock(
            return_value=[{"pid": 1, "type": "browser"}]
        )
        backend.system_info_get_feature_state = AsyncMock(
            return_value={"featureName": "test", "featureState": "enabled"}
        )
        return backend

    async def test_get_info(self) -> None:
        """Test get-info action."""
        backend = self._make_backend()
        params = SystemInfoParams(action="get-info")
        result = await SystemInfoAction(params).execute(backend)
        assert result == {"os": "linux", "gpu": {"vendor": "NVIDIA"}}
        backend.system_info_get_info.assert_called_once()

    async def test_get_process_info(self) -> None:
        """Test get-process-info action."""
        backend = self._make_backend()
        params = SystemInfoParams(action="get-process-info")
        result = await SystemInfoAction(params).execute(backend)
        assert len(result) == 1
        assert result[0]["pid"] == 1
        backend.system_info_get_process_info.assert_called_once()

    async def test_get_feature_state(self) -> None:
        """Test get-feature-state action."""
        backend = self._make_backend()
        params = SystemInfoParams(action="get-feature-state", feature_name="test")
        result = await SystemInfoAction(params).execute(backend)
        assert result == {"featureName": "test", "featureState": "enabled"}
        backend.system_info_get_feature_state.assert_called_once_with("test")

    async def test_get_feature_state_missing_name_raises(self) -> None:
        """Test that get-feature-state without feature_name raises."""
        backend = self._make_backend()
        params = SystemInfoParams(action="get-feature-state")
        with pytest.raises(ValueError, match="feature_name is required"):
            await SystemInfoAction(params).execute(backend)

    async def test_unknown_action_raises(self) -> None:
        """Test that unknown action raises."""
        backend = self._make_backend()
        params = SystemInfoParams(action="invalid")
        with pytest.raises(ValueError, match="Unknown SystemInfo action"):
            await SystemInfoAction(params).execute(backend)

    async def test_lifecycle(self) -> None:
        """Test the action lifecycle (navigate, execute)."""
        backend = self._make_backend()
        params = SystemInfoParams(url="https://example.com", action="get-info")
        await SystemInfoAction(params).execute(backend)
        backend.navigate.assert_called_once()
        backend.system_info_get_info.assert_called_once()
