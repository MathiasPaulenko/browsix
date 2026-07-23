"""Integration tests for console and logs commands."""

import pytest

from wavexis.actions.console import ConsoleAction, ConsoleParams
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, WaitStrategy


@pytest.mark.integration
class TestConsoleIntegration:
    """Integration tests for console capture against real Chrome."""

    async def test_capture_console(self, local_http_server):
        """Test capture console."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = ConsoleParams(
                url=local_http_server,
                capture="console",
                wait=WaitStrategy(strategy="load"),
            )
            action = ConsoleAction(params)
            result = await action.execute(backend)
            assert "console" in result
            assert isinstance(result["console"], list)
        finally:
            await backend.close()

    async def test_capture_logs(self, local_http_server):
        """Test capture logs."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = ConsoleParams(
                url=local_http_server,
                capture="logs",
                wait=WaitStrategy(strategy="load"),
            )
            action = ConsoleAction(params)
            result = await action.execute(backend)
            assert "logs" in result
            assert isinstance(result["logs"], list)
        finally:
            await backend.close()
