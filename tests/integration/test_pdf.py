"""Integration tests for PDF command."""

import pytest

from wavexis.actions.pdf import PDFAction
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, PDFParams, WaitStrategy


@pytest.mark.integration
class TestPDFIntegration:
    """Integration tests for PDF generation against real Chrome."""

    async def test_pdf_letter(self, local_http_server):
        """Test pdf letter."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = PDFParams(
                url=local_http_server,
                paper="letter",
                wait=WaitStrategy(strategy="load"),
            )
            action = PDFAction(params)
            result = await action.execute(backend)
            assert len(result) > 0
            assert result[:4] == b"%PDF"
        finally:
            await backend.close()

    async def test_pdf_a4(self, local_http_server):
        """Test pdf a4."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = PDFParams(
                url=local_http_server,
                paper="a4",
                wait=WaitStrategy(strategy="load"),
            )
            action = PDFAction(params)
            result = await action.execute(backend)
            assert len(result) > 0
            assert result[:4] == b"%PDF"
        finally:
            await backend.close()

    async def test_pdf_landscape(self, local_http_server):
        """Test pdf landscape."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = PDFParams(
                url=local_http_server,
                paper="a4",
                landscape=True,
                wait=WaitStrategy(strategy="load"),
            )
            action = PDFAction(params)
            result = await action.execute(backend)
            assert len(result) > 0
            assert result[:4] == b"%PDF"
        finally:
            await backend.close()
