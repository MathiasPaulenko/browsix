"""Integration tests for navigation commands."""

import pytest

from wavexis.actions.navigate import NavigateAction, NavigateParams, ReloadAction
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, WaitStrategy


@pytest.mark.integration
class TestNavigateIntegration:
    """Integration tests for navigation against real Chrome."""

    async def test_navigate_basic(self, local_http_server):
        """Test navigate basic."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            action = NavigateAction(
                NavigateParams(
                    url=local_http_server,
                    wait=WaitStrategy(strategy="load"),
                )
            )
            await action.execute(backend)
        finally:
            await backend.close()

    async def test_navigate_wait_for_selector(self, local_http_server):
        """Test navigate wait for selector."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            action = NavigateAction(
                NavigateParams(
                    url=local_http_server,
                    wait=WaitStrategy(strategy="selector", selector="h1", timeout=10000),
                )
            )
            await action.execute(backend)
        finally:
            await backend.close()

    async def test_reload(self, local_http_server):
        """Test reload."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            await backend.navigate(local_http_server, WaitStrategy(strategy="load"))
            action = ReloadAction(False)
            await action.execute(backend)
        finally:
            await backend.close()
