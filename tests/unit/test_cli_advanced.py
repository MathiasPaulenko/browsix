"""Unit tests for wavexis.cli._advanced commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from wavexis.cli.app import app

runner = CliRunner()


def _make_backend() -> AsyncMock:
    """Return a mock backend with methods used by _advanced commands."""
    backend = AsyncMock()
    backend.launch = AsyncMock()
    backend.close = AsyncMock()
    backend.navigate = AsyncMock()
    backend.a11y_tree = AsyncMock(return_value={"role": "RootWebArea"})
    backend.a11y_node = AsyncMock(return_value={"nodeId": "1"})
    backend.a11y_ancestors = AsyncMock(return_value=[])
    backend.intercept_download = AsyncMock(return_value=b"file-bytes")
    backend.click = AsyncMock()
    backend.eval = AsyncMock(return_value=True)
    backend.page_enable = AsyncMock()
    backend.dialog_wait_for_opening = AsyncMock()
    backend.dialog_accept = AsyncMock()
    backend.dialog_dismiss = AsyncMock()
    backend.grant_permission = AsyncMock()
    backend.reset_permissions = AsyncMock()
    backend.get_security_state = AsyncMock(return_value={"summary": "secure"})
    backend.ignore_cert_errors = AsyncMock()
    backend.extension_install = AsyncMock(return_value="ext-id")
    backend.extension_uninstall = AsyncMock()
    backend.extension_list = AsyncMock(
        return_value=[{"id": "ext", "name": "Test", "version": "1", "enabled": True}]
    )
    backend.get_pref = AsyncMock(return_value="/downloads")
    backend.set_pref = AsyncMock()
    backend.capture_console = AsyncMock(return_value=[])
    return backend


@pytest.mark.unit
class TestAdvancedCLI:
    """Exercise advanced CLI commands with a mocked backend."""

    def test_a11y_tree(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["a11y", "https://example.com"])
        assert result.exit_code == 0
        assert "RootWebArea" in result.output

    def test_a11y_node(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["a11y", "https://example.com", "-a", "node", "--node-id", "1"]
            )
        assert result.exit_code == 0

    def test_download(self, tmp_path: Path) -> None:
        backend = _make_backend()
        out = str(tmp_path / "file.bin")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["download", "https://example.com/file", "-o", out])
        assert result.exit_code == 0
        assert "saved" in result.output.lower()
        assert Path(out).read_bytes() == b"file-bytes"

    def test_download_selector_none(self, tmp_path: Path) -> None:
        backend = _make_backend()
        out = str(tmp_path / "file.bin")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["download", "https://example.com/file", "--selector", "none", "-o", out]
            )
        assert result.exit_code == 0
        backend.click.assert_not_called()

    def test_download_no_data(self, tmp_path: Path) -> None:
        backend = _make_backend()
        backend.intercept_download.return_value = b""
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["download", "https://example.com", "-o", "out.bin"])
        assert result.exit_code != 0

    def test_dialog_accept(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["dialog", "https://example.com", "-a", "accept", "--text", "ok"]
            )
        assert result.exit_code == 0
        backend.dialog_accept.assert_awaited_once_with("ok")

    def test_permissions_grant(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["permissions", "grant", "--permission", "camera", "--url", "https://example.com"],
            )
        assert result.exit_code == 0
        backend.grant_permission.assert_awaited_once_with("camera")

    def test_lighthouse(self, tmp_path: Path) -> None:
        backend = _make_backend()
        backend.perf_metrics.return_value = {}

        async def _eval(script: str, *, await_promise: bool = False) -> dict[str, Any]:
            if "domContentLoaded" in script:
                return {
                    "ttfb": 100,
                    "fcp": 200,
                    "loadComplete": 300,
                    "domSize": 50,
                    "transferSize": 0,
                    "encodedBodySize": 0,
                }
            if "largest-contentful-paint" in script:
                return {"lcp": 250, "cls": 0, "inp": 50, "tbt": 0}
            if "has_viewport" in script:
                return {"issues": [], "issue_count": 0, "has_lang": True, "has_viewport": True}
            if "title_length" in script:
                return {
                    "title": "T",
                    "title_length": 1,
                    "description": "D",
                    "description_length": 1,
                    "h1_count": 1,
                    "canonical": "c",
                    "og_title": "o",
                    "twitter_card": "t",
                }
            if "is_https" in script:
                return {"issues": [], "is_https": True, "console_errors": []}
            return {}

        backend.eval.side_effect = _eval
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            out = str(tmp_path / "report.json")
            result = runner.invoke(app, ["lighthouse", "https://example.com", "-o", out])
        assert result.exit_code == 0
        assert "performance" in result.output

    def test_extension_install(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-install", "/path/to/ext"])
        assert result.exit_code == 0
        assert "ext-id" in result.output

    def test_extension_list(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-list"])
        assert result.exit_code == 0
        assert "Test" in result.output

    def test_pref_get(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["pref-get", "download.default_directory"])
        assert result.exit_code == 0
        assert "/downloads" in result.output

    def test_pref_set(self) -> None:
        backend = _make_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["pref-set", "download.default_directory", "/tmp"])
        assert result.exit_code == 0
        backend.set_pref.assert_awaited_once_with("download.default_directory", "/tmp")
