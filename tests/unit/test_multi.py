"""Unit tests for wavexis.multi YAML parser and executor."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis.exceptions import MultiConfigError
from wavexis.multi import execute_actions, parse_yaml


@pytest.mark.unit
class TestParseYaml:
    """Test suite for parseyaml."""

    def test_valid_config(self, tmp_path: Path) -> None:
        """Test valid config."""
        config = tmp_path / "config.yml"
        config.write_text(
            """
actions:
  - screenshot:
      url: https://example.com
      full_page: true
  - pdf:
      url: https://example.com
      paper: a4
""",
            encoding="utf-8",
        )
        actions = parse_yaml(config)
        assert len(actions) == 2
        assert "screenshot" in actions[0]
        assert actions[0]["screenshot"]["url"] == "https://example.com"
        assert "pdf" in actions[1]

    def test_missing_file(self, tmp_path: Path) -> None:
        """Test that missing file raises an appropriate error."""
        with pytest.raises(MultiConfigError, match="file"):
            parse_yaml(tmp_path / "nonexistent.yml")

    def test_unreadable_file(self, tmp_path: Path) -> None:
        """An existing but unreadable config file should raise MultiConfigError."""
        config = tmp_path / "config.yml"
        config.write_text("actions:\n  - screenshot:\n      url: https://example.com\n")
        with (
            patch("pathlib.Path.read_text", side_effect=PermissionError("denied")),
            pytest.raises(MultiConfigError, match="unreadable"),
        ):
            parse_yaml(config)

    def test_non_dict_root(self, tmp_path: Path) -> None:
        """Test non dict root."""
        config = tmp_path / "bad.yml"
        config.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(MultiConfigError, match="root"):
            parse_yaml(config)

    def test_missing_actions_key(self, tmp_path: Path) -> None:
        """Test that missing actions key raises an appropriate error."""
        config = tmp_path / "bad.yml"
        config.write_text("foo: bar\n", encoding="utf-8")
        with pytest.raises(MultiConfigError, match="actions"):
            parse_yaml(config)

    def test_actions_not_list(self, tmp_path: Path) -> None:
        """Test actions not list."""
        config = tmp_path / "bad.yml"
        config.write_text("actions: notalist\n", encoding="utf-8")
        with pytest.raises(MultiConfigError, match="actions"):
            parse_yaml(config)

    def test_action_not_single_key(self, tmp_path: Path) -> None:
        """Test action not single key."""
        config = tmp_path / "bad.yml"
        config.write_text(
            "actions:\n  - screenshot: {}\n    pdf: {}\n",
            encoding="utf-8",
        )
        with pytest.raises(MultiConfigError, match="actions"):
            parse_yaml(config)

    def test_action_params_not_dict(self, tmp_path: Path) -> None:
        """Test action params not dict."""
        config = tmp_path / "bad.yml"
        config.write_text(
            "actions:\n  - screenshot: notadict\n",
            encoding="utf-8",
        )
        with pytest.raises(MultiConfigError, match="screenshot"):
            parse_yaml(config)

    def test_empty_actions(self, tmp_path: Path) -> None:
        """Test empty actions."""
        config = tmp_path / "empty.yml"
        config.write_text("actions: []\n", encoding="utf-8")
        actions = parse_yaml(config)
        assert actions == []


@pytest.mark.unit
class TestExecuteActions:
    """Test suite for executeactions."""

    async def test_execute_screenshot(self) -> None:
        """Test execute screenshot."""
        backend = MagicMock()
        backend.navigate = AsyncMock()
        backend.screenshot = AsyncMock(return_value=b"png")
        actions = [{"screenshot": {"url": "https://example.com", "full_page": True}}]
        results = await execute_actions(actions, backend)
        assert len(results) == 1
        assert results[0] == b"png"

    async def test_execute_multiple(self) -> None:
        """Test execute multiple."""
        backend = MagicMock()
        backend.navigate = AsyncMock()
        backend.screenshot = AsyncMock(return_value=b"png")
        backend.eval = AsyncMock(return_value="title")
        actions = [
            {"screenshot": {"url": "https://example.com"}},
            {"eval": {"url": "https://example.com", "expression": "document.title"}},
        ]
        results = await execute_actions(actions, backend)
        assert len(results) == 2
        assert results[0] == b"png"
        assert results[1] == "title"

    async def test_execute_empty(self) -> None:
        """Test execute empty."""
        backend = MagicMock()
        results = await execute_actions([], backend)
        assert results == []

    async def test_execute_unknown_action(self) -> None:
        """Test execute unknown action."""
        backend = MagicMock()
        actions = [{"unknown_action": {"url": "https://example.com"}}]
        with pytest.raises(MultiConfigError, match="unknown_action"):
            await execute_actions(actions, backend)

    async def test_parallel_returns_exceptions_without_aborting(self) -> None:
        """One failing action should not abort other parallel actions."""
        from wavexis.exceptions import WavexisError

        backend = MagicMock()
        tab_mock = MagicMock()
        tab_mock.close = AsyncMock()
        backend.new_tab_handle = AsyncMock(return_value=tab_mock)

        async def mixed_dispatch(
            action_type: str, params: dict, backend: Any, cache: Any = None
        ) -> Any:
            if action_type == "screenshot":
                return b"png"
            raise ValueError("intentional")

        with (
            pytest.raises(WavexisError, match="intentional"),
            patch("wavexis.multi._dispatch", side_effect=mixed_dispatch),
        ):
            await execute_actions(
                [
                    {"screenshot": {"url": "https://example.com"}},
                    {"eval": {"url": "https://example.com", "expression": "1"}},
                ],
                backend,
                parallel=True,
            )
