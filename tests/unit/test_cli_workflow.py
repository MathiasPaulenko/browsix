"""Unit tests for wavexis.cli._workflow commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from wavexis.cli.app import app

runner = CliRunner()


def _make_backend() -> AsyncMock:
    """Return a mock backend for workflow commands."""
    backend = AsyncMock()
    backend.launch = AsyncMock()
    backend.close = AsyncMock()
    backend.new_tab_handle = AsyncMock(return_value=MagicMock(close=AsyncMock()))
    return backend


@pytest.mark.unit
class TestMultiCLI:
    """Tests for the `multi` command."""

    def test_multi_dry_run(self, tmp_path: Path) -> None:
        config = tmp_path / "shots.yml"
        config.write_text(
            "actions:\n  - screenshot:\n      url: https://example.com\n", encoding="utf-8"
        )
        with patch(
            "wavexis.multi.parse_yaml",
            return_value=[{"screenshot": {"url": "https://example.com"}}],
        ):
            result = runner.invoke(app, ["multi", str(config), "--dry-run"])
        assert result.exit_code == 0
        assert "Plan" in result.output

    def test_multi_invalid_config_path(self) -> None:
        with patch("wavexis.cli._workflow.validate_path", side_effect=ValueError("bad path")):
            result = runner.invoke(app, ["multi", "bad/../path.yml"])
        assert result.exit_code != 0

    def test_multi_executes(self, tmp_path: Path) -> None:
        backend = _make_backend()
        config = tmp_path / "shots.yml"
        config.write_text(
            "actions:\n  - eval:\n      url: https://example.com\n      expression: '1'\n",
            encoding="utf-8",
        )
        with patch("wavexis.cli._workflow._get_backend", return_value=backend), patch(
            "wavexis.multi.parse_yaml",
            return_value=[{"eval": {"url": "https://example.com", "expression": "1"}}],
        ), patch("wavexis.multi.execute_actions", new=AsyncMock(return_value=["ok"])):
            result = runner.invoke(app, ["multi", str(config)])
        assert result.exit_code == 0
        assert "Completed" in result.output


@pytest.mark.unit
class TestBatchCLI:
    """Tests for the `batch` command."""

    def test_batch_dry_run(self, tmp_path: Path) -> None:
        urls = tmp_path / "urls.txt"
        urls.write_text("https://example.com\nhttps://example.org\n", encoding="utf-8")
        result = runner.invoke(app, ["batch", str(urls), "screenshot", "--dry-run"])
        assert result.exit_code == 0
        assert "Plan" in result.output
        assert "2 URL(s)" in result.output

    def test_batch_missing_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.txt"
        result = runner.invoke(app, ["batch", str(missing), "screenshot"])
        assert result.exit_code != 0

    def test_batch_empty_file(self, tmp_path: Path) -> None:
        urls = tmp_path / "urls.txt"
        urls.write_text("\n\n", encoding="utf-8")
        result = runner.invoke(app, ["batch", str(urls), "screenshot"])
        assert result.exit_code != 0

    def test_batch_screenshot(self, tmp_path: Path) -> None:
        urls = tmp_path / "urls.txt"
        urls.write_text("https://example.com\n", encoding="utf-8")
        out_dir = tmp_path / "out"
        backend = _make_backend()
        with (
            patch("wavexis.cli._workflow._get_backend", return_value=backend),
            patch("wavexis.cli._workflow.ScreenshotAction") as mock_action,
        ):
            mock_action.return_value.execute = AsyncMock(return_value=b"png")
            result = runner.invoke(
                app, ["batch", str(urls), "screenshot", "-o", str(out_dir), "-p", "1"]
            )
        assert result.exit_code == 0
        assert "Completed" in result.output

    def test_batch_invalid_action(self, tmp_path: Path) -> None:
        urls = tmp_path / "urls.txt"
        urls.write_text("https://example.com\n", encoding="utf-8")
        out_dir = tmp_path / "out"
        backend = _make_backend()
        with patch("wavexis.cli._workflow._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["batch", str(urls), "unknown", "-o", str(out_dir), "-p", "1"]
            )
        assert result.exit_code == 0
        assert "ERROR" in result.output
