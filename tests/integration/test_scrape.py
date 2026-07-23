"""Integration tests for scrape command."""

import pytest

from wavexis.actions.scrape import ScrapeAction
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, ScrapeParams, WaitStrategy


@pytest.mark.integration
class TestScrapeIntegration:
    """Integration tests for scrape against real Chrome."""

    async def test_scrape_single_url(self, local_http_server):
        """Test scrape single url."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = ScrapeParams(
                urls=[f"{local_http_server}example"],
                expression="document.title",
                wait=WaitStrategy(strategy="load"),
            )
            action = ScrapeAction(params)
            results = await action.execute(backend)
            assert len(results) == 1
            assert results[0]["url"] == f"{local_http_server}example"
            assert "Example Domain" in results[0]["result"]
        finally:
            await backend.close()

    async def test_scrape_multiple_urls(self, local_http_server):
        """Test scrape multiple urls."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = ScrapeParams(
                urls=[f"{local_http_server}example", f"{local_http_server}example"],
                expression="document.title",
                wait=WaitStrategy(strategy="load"),
            )
            action = ScrapeAction(params)
            results = await action.execute(backend)
            assert len(results) == 2
            assert "Example" in results[0]["result"]
            assert "Example" in results[1]["result"]
        finally:
            await backend.close()

    async def test_scrape_with_file(self, local_http_server, tmp_path):
        """Test scrape with file."""
        js_file = tmp_path / "scraper.js"
        js_file.write_text("document.title", encoding="utf-8")
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = ScrapeParams(
                urls=[f"{local_http_server}example"],
                file=str(js_file),
                wait=WaitStrategy(strategy="load"),
            )
            action = ScrapeAction(params)
            results = await action.execute(backend)
            assert len(results) == 1
            assert "Example Domain" in results[0]["result"]
        finally:
            await backend.close()
