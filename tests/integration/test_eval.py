"""Integration tests for eval command."""

from pathlib import Path

import pytest

from wavexis.actions.eval import EvalAction
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, EvalParams, WaitStrategy


@pytest.mark.integration
class TestEvalIntegration:
    """Integration tests for JS evaluation against real Chrome."""

    async def test_eval_expression(self, local_http_server):
        """Test eval expression."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = EvalParams(
                url=f"{local_http_server}example",
                expression="document.title",
                wait=WaitStrategy(strategy="load"),
            )
            action = EvalAction(params)
            result = await action.execute(backend)
            assert result == "Example Domain"
        finally:
            await backend.close()

    async def test_eval_from_file(self, local_http_server, tmp_path: Path):
        """Test eval from file."""
        js_file = tmp_path / "script.js"
        js_file.write_text("document.title", encoding="utf-8")

        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = EvalParams(
                url=f"{local_http_server}example",
                file=str(js_file),
                wait=WaitStrategy(strategy="load"),
            )
            action = EvalAction(params)
            result = await action.execute(backend)
            assert result == "Example Domain"
        finally:
            await backend.close()

    async def test_eval_await_promise(self, local_http_server):
        """Test eval await promise."""
        manager = BackendManager()
        backend = manager.select()
        try:
            await backend.launch(BrowserOptions())
            params = EvalParams(
                url=f"{local_http_server}example",
                expression="Promise.resolve(42)",
                await_promise=True,
                wait=WaitStrategy(strategy="load"),
            )
            action = EvalAction(params)
            result = await action.execute(backend)
            assert result == 42
        finally:
            await backend.close()
