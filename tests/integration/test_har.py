"""Integration tests for HAR capture."""

import pytest

from wavexis.actions.har import HARAction
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, HarParams


@pytest.mark.integration
class TestHARIntegration:
    """Integration tests for HAR capture against real Chrome."""

    async def test_har_basic(self, local_http_server):
        """Test har basic."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = HarParams(url=f"{local_http_server}example", timeout=2000)
            action = HARAction(params)
            result = await action.execute(backend)
            assert "log" in result
            assert result["log"]["version"] == "1.2"
            assert "entries" in result["log"]
            assert len(result["log"]["entries"]) > 0
            entry = result["log"]["entries"][0]
            assert "request" in entry
            assert "response" in entry
            assert "startedDateTime" in entry
            assert "timings" in entry
        finally:
            await backend.close()

    async def test_har_with_filter(self, local_http_server):
        """Test har with filter."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = HarParams(
                url=f"{local_http_server}example",
                timeout=2000,
                filter="example",
            )
            action = HARAction(params)
            result = await action.execute(backend)
            assert "log" in result
            for entry in result["log"]["entries"]:
                url = entry["request"]["url"]
                assert "example" in url
        finally:
            await backend.close()
