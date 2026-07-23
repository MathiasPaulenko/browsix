"""Unit tests for global CLI options: --headed, --timeout, --proxy, config."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import wavexis.cli._shared as _shared
import wavexis.cli.app  # noqa: F401 — ensure module is loaded
from wavexis.config import BrowserOptions

pytestmark = pytest.mark.unit

_cli = sys.modules["wavexis.cli.app"]


def _fresh_ctx() -> _cli.CLIContext:
    """Create a fresh CLIContext and set it as the current context."""
    ctx = _cli.CLIContext()
    _cli._ctx.set(ctx)
    return ctx


class TestBrowserOptions:
    """Tests for BrowserOptions with proxy and timeout fields."""

    def test_defaults(self) -> None:
        opts = BrowserOptions()
        assert opts.headless is True
        assert opts.proxy is None
        assert opts.timeout == 30000
        assert opts.user_data_dir is None
        assert opts.browser_url is None

    def test_with_browser_url(self) -> None:
        opts = BrowserOptions(browser_url="ws://localhost:9222")
        assert opts.browser_url == "ws://localhost:9222"

    def test_with_user_data_dir(self) -> None:
        opts = BrowserOptions(user_data_dir="/tmp/wavexis-profile")
        assert opts.user_data_dir == "/tmp/wavexis-profile"

    def test_with_proxy(self) -> None:
        opts = BrowserOptions(proxy="http://proxy:8080")
        assert opts.proxy == "http://proxy:8080"

    def test_with_timeout(self) -> None:
        opts = BrowserOptions(timeout=60000)
        assert opts.timeout == 60000

    def test_headed(self) -> None:
        opts = BrowserOptions(headless=False)
        assert opts.headless is False

    def test_socks_proxy(self) -> None:
        opts = BrowserOptions(proxy="socks5://proxy:1080")
        assert opts.proxy == "socks5://proxy:1080"


class TestBrowserOptionsHelper:
    """Tests for _browser_options() CLI helper."""

    def test_default_options(self) -> None:
        _fresh_ctx()
        opts = _cli._browser_options()
        assert opts.headless is True
        assert opts.timeout == 30000
        assert opts.proxy is None
        assert opts.user_data_dir is None
        assert opts.browser_url is None

    def test_browser_url_options(self) -> None:
        ctx = _fresh_ctx()
        ctx.browser_url = "ws://localhost:9222"
        opts = _cli._browser_options()
        assert opts.browser_url == "ws://localhost:9222"

    def test_user_data_dir_options(self) -> None:
        ctx = _fresh_ctx()
        ctx.user_data_dir = "/tmp/wavexis-profile"
        opts = _cli._browser_options()
        assert opts.user_data_dir == "/tmp/wavexis-profile"

    def test_headed_options(self) -> None:
        ctx = _fresh_ctx()
        ctx.headless = False
        opts = _cli._browser_options()
        assert opts.headless is False

    def test_proxy_options(self) -> None:
        ctx = _fresh_ctx()
        ctx.proxy = "http://proxy:8080"
        opts = _cli._browser_options()
        assert opts.proxy == "http://proxy:8080"

    def test_timeout_options(self) -> None:
        ctx = _fresh_ctx()
        ctx.timeout = 60000
        opts = _cli._browser_options()
        assert opts.timeout == 60000

    def test_wait_strategy_uses_global_timeout(self) -> None:
        """Regression for bug #3: _wait_strategy must honour --timeout."""
        ctx = _fresh_ctx()
        ctx.timeout = 60000
        ws = _shared._wait_strategy("load")
        assert ws.strategy == "load"
        assert ws.timeout == 60000

    def test_wait_strategy_explicit_timeout_overrides_ctx(self) -> None:
        """An explicit timeout wins over the global --timeout."""
        ctx = _fresh_ctx()
        ctx.timeout = 60000
        ws = _shared._wait_strategy("load", timeout=5000)
        assert ws.timeout == 5000

    def test_wait_strategy_default_uses_ctx_default(self) -> None:
        """With a fresh context, the default 30000ms is used."""
        ctx = _fresh_ctx()
        assert ctx.timeout == 30000
        ws = _shared._wait_strategy("load")
        assert ws.timeout == 30000

    def test_wait_strategy_selector_passes_selector(self) -> None:
        ctx = _fresh_ctx()
        ctx.timeout = 45000
        ws = _shared._wait_strategy("selector", selector="#foo")
        assert ws.strategy == "selector"
        assert ws.selector == "#foo"
        assert ws.timeout == 45000

    def test_wait_strategy_uses_global_wait_strategy_flag(self) -> None:
        """Regression for bug #4: --wait-strategy must be honoured."""
        ctx = _fresh_ctx()
        ctx.wait_strategy = "networkidle"
        ctx.timeout = 60000
        ws = _shared._wait_strategy()
        assert ws.strategy == "networkidle"
        assert ws.timeout == 60000

    def test_wait_strategy_explicit_strategy_overrides_flag(self) -> None:
        """An explicit strategy wins over the global --wait-strategy."""
        ctx = _fresh_ctx()
        ctx.wait_strategy = "networkidle"
        ws = _shared._wait_strategy("domcontentloaded")
        assert ws.strategy == "domcontentloaded"


class TestLoadGlobalConfig:
    """Tests for _load_global_config."""

    def test_no_config_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: Path("/nonexistent_home_12345"))
        ctx = _fresh_ctx()
        _cli._load_global_config()
        assert ctx.preferred_backend is None
        assert ctx.headless is True
        assert ctx.timeout == 30000
        assert ctx.proxy is None
        assert ctx.user_data_dir is None
        assert ctx.browser_url is None

    def test_loads_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_dir = tmp_path / ".wavexis"
        config_dir.mkdir()
        config_file = config_dir / "config.yml"
        config_file.write_text(
            "backend: bidi\n"
            "headless: false\n"
            "timeout: 60000\n"
            "proxy: http://proxy:9090\n"
            "user_data_dir: /tmp/profile\n"
            "browser_url: ws://localhost:9222\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        ctx = _fresh_ctx()
        _cli._load_global_config()

        assert ctx.preferred_backend == "bidi"
        assert ctx.headless is False
        assert ctx.timeout == 60000
        assert ctx.proxy == "http://proxy:9090"
        assert ctx.user_data_dir == "/tmp/profile"
        assert ctx.browser_url == "ws://localhost:9222"

    def test_cli_overrides_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_dir = tmp_path / ".wavexis"
        config_dir.mkdir()
        config_file = config_dir / "config.yml"
        config_file.write_text("backend: bidi\ntimeout: 60000\n", encoding="utf-8")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        ctx = _fresh_ctx()
        ctx.preferred_backend = "cdp"
        _cli._load_global_config()

        assert ctx.preferred_backend == "cdp"
        assert ctx.timeout == 60000


class TestConfigCommand:
    """Tests for wavexis config command."""

    def test_config_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "path"])
        assert result.exit_code == 0
        assert str(tmp_path / ".wavexis" / "config.yml") in result.output

    def test_config_init(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "init"])
        assert result.exit_code == 0
        config_path = tmp_path / ".wavexis" / "config.yml"
        assert config_path.exists()
        import yaml

        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert "backend" in data
        assert "headless" in data
        assert "timeout" in data

    def test_config_set(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "set", "--key", "timeout", "--value", "45000"])
        assert result.exit_code == 0
        config_path = tmp_path / ".wavexis" / "config.yml"
        import yaml

        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["timeout"] == 45000

    def test_config_set_headless(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "set", "--key", "headless", "--value", "false"])
        assert result.exit_code == 0
        config_path = tmp_path / ".wavexis" / "config.yml"
        import yaml

        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["headless"] is False

    @pytest.mark.parametrize(
        "key,value,expected_error",
        [
            ("backend", "invalid", "backend must be"),
            ("headless", "maybe", "headless must be"),
            ("timeout", "abc", "timeout must be an integer"),
            ("timeout", "-5", "timeout must be >= 0"),
            ("proxy", "ftp://proxy", "Invalid proxy scheme"),
            ("browser_url", "file:///tmp", "Invalid browser_url scheme"),
            ("remote_url", "http://example.com", "Invalid remote_url scheme"),
            ("user_data_dir", "../escape", "Invalid user_data_dir"),
            ("stealth", "sure", "stealth must be"),
            ("unknown_key", "x", "unknown config key"),
        ],
    )
    def test_config_set_rejects_invalid_values(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        key: str,
        value: str,
        expected_error: str,
    ) -> None:
        """Invalid config values must be rejected with a clear message."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(
            _cli.app, ["config", "set", "--key", key, "--value", value]
        )
        assert result.exit_code == 2
        assert expected_error.lower() in result.output.lower()

    def test_config_show_no_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "show"])
        assert result.exit_code == 0
        assert "No config file found" in result.output

    def test_config_show(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_dir = tmp_path / ".wavexis"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("backend: cdp\ntimeout: 30000\n", encoding="utf-8")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(_cli.app, ["config", "show"])
        assert result.exit_code == 0
        assert "backend: cdp" in result.output

    def test_config_init_permission_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A permission error writing the initial config should exit cleanly."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        with patch.object(Path, "write_text", side_effect=PermissionError("denied")):
            result = runner.invoke(_cli.app, ["config", "init"])
        assert result.exit_code == 1
        assert "failed to create config" in result.output.lower()

    def test_config_show_permission_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An unreadable config file should exit cleanly, not traceback."""
        config_dir = tmp_path / ".wavexis"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("backend: cdp\n", encoding="utf-8")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            result = runner.invoke(_cli.app, ["config", "show"])
        assert result.exit_code == 1
        assert "failed to read config" in result.output.lower()

    def test_config_set_permission_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A permission error updating the config should exit cleanly."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        from typer.testing import CliRunner

        runner = CliRunner()
        with patch.object(Path, "write_text", side_effect=PermissionError("denied")):
            result = runner.invoke(
                _cli.app, ["config", "set", "--key", "backend", "--value", "cdp"]
            )
        assert result.exit_code == 1
        assert "failed to write config" in result.output.lower()
