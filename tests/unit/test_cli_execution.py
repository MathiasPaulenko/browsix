"""Unit tests that execute CLI commands with mocked backends for coverage."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from wavexis.cli.app import app

runner = CliRunner()


def _make_mock_backend():
    """Create a mock backend where all methods are async by default."""
    backend = AsyncMock()
    backend.launch = AsyncMock()
    backend.close = AsyncMock()
    backend.navigate = AsyncMock()
    backend.screenshot = AsyncMock(return_value=b"png-bytes")
    backend.screenshot_selector = AsyncMock(return_value=b"sel-bytes")
    backend.pdf = AsyncMock(return_value=b"pdf-bytes")
    backend.eval = AsyncMock(return_value="result")
    backend.raw = AsyncMock(return_value={"result": {}})
    backend.get_cookies = AsyncMock(return_value=[{"name": "session", "value": "abc"}])
    backend.set_cookie = AsyncMock()
    backend.clear_cookies = AsyncMock()
    backend.delete_cookie = AsyncMock()
    backend.set_headers = AsyncMock()
    backend.set_user_agent = AsyncMock()
    backend.dom_get = AsyncMock(return_value="<html><body>content</body></html>")
    backend.dom_query = AsyncMock(return_value={"nodeId": 1, "children": []})
    backend.dom_set_attr = AsyncMock()
    backend.dom_get_attr = AsyncMock(return_value="value")
    backend.dom_remove_attr = AsyncMock()
    backend.dom_remove = AsyncMock()
    backend.dom_focus = AsyncMock()
    backend.dom_scroll = AsyncMock()
    backend.click = AsyncMock()
    backend.type = AsyncMock()
    backend.type_text = AsyncMock()
    backend.fill = AsyncMock()
    backend.hover = AsyncMock()
    backend.focus = AsyncMock()
    backend.select = AsyncMock()
    backend.press_key = AsyncMock()
    backend.key_press = AsyncMock()
    backend.scroll = AsyncMock()
    backend.go_back = AsyncMock()
    backend.go_forward = AsyncMock()
    backend.reload = AsyncMock()
    backend.stop_loading = AsyncMock()
    backend.wait_for = AsyncMock()
    backend.screencast = AsyncMock(return_value=[b"frame1"])
    backend.capture_console = AsyncMock(return_value=[{"type": "log", "text": "hi"}])
    backend.capture_logs = AsyncMock(return_value=[{"level": "info", "message": "ok"}])
    backend.capture_har = AsyncMock(return_value={"log": {"entries": []}})
    backend.new_context = AsyncMock(return_value="ctx-1")
    backend.list_contexts = AsyncMock(return_value=[{"contextId": "ctx-1"}])
    backend.close_context = AsyncMock()
    backend.new_tab = AsyncMock(return_value="tab-1")
    backend.list_tabs = AsyncMock(return_value=[{"targetId": "tab1", "url": "https://example.com"}])
    backend.close_tab = AsyncMock()
    backend.activate_tab = AsyncMock()
    backend.new_tab_handle = AsyncMock(return_value=AsyncMock(close=AsyncMock()))
    backend.emulate_device = AsyncMock()
    backend.set_viewport = AsyncMock()
    backend.set_timezone = AsyncMock()
    backend.set_dark_mode = AsyncMock()
    backend.set_geolocation = AsyncMock()
    backend.browser_version = AsyncMock(return_value="Chrome/120")
    backend.get_window_bounds = AsyncMock(
        return_value={"width": 1280, "height": 800, "x": 0, "y": 0}
    )
    backend.set_window_bounds = AsyncMock()
    backend.start_combined_trace = AsyncMock(return_value="trace-1")
    backend.stop_combined_trace = AsyncMock(
        return_value={"events": [], "screenshots": [], "network": [], "console": []}
    )
    backend.replay_har = AsyncMock()
    backend.modify_request = AsyncMock()
    backend.download = AsyncMock()
    backend.print_page = AsyncMock()
    backend.crash = AsyncMock()
    backend.reset_permissions = AsyncMock()
    backend.set_permission = AsyncMock()
    backend.handle_dialog = AsyncMock()
    backend.list_dialogs = AsyncMock(return_value=[])
    backend.set_extra_http_headers = AsyncMock()
    backend.reset_network_conditions = AsyncMock()
    backend.emulate_network_conditions = AsyncMock()
    backend.block_url = AsyncMock()
    backend.clear_blocked_urls = AsyncMock()
    backend.set_cache_disabled = AsyncMock()
    backend.attach_to_target = AsyncMock()
    backend.detach_from_target = AsyncMock()
    backend.execute_in_target = AsyncMock(return_value={})
    backend.get_storage_for_target = AsyncMock(return_value={})
    backend.set_storage_for_target = AsyncMock()
    backend.get_tree = AsyncMock(return_value={"frames": []})
    backend.get_opener = AsyncMock(return_value=None)
    backend.navigate_in_frame = AsyncMock()
    backend.evaluate_in_frame = AsyncMock(return_value={})
    backend.shadow_click = AsyncMock()
    backend.shadow_fill = AsyncMock()
    backend.shadow_eval = AsyncMock(return_value="{}")
    backend.iframe_eval = AsyncMock(return_value="{}")
    backend.iframe_click = AsyncMock()
    backend.iframe_fill = AsyncMock()
    backend.block_requests = AsyncMock()
    backend.throttle_network = AsyncMock()
    backend.storage_list = AsyncMock(return_value={})
    return backend


@pytest.mark.unit
class TestCLIExecutionCapture:
    """Execute capture commands with mocked backend."""

    def test_screenshot_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        out = str(tmp_path / "shot.png")
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["screenshot", "https://example.com", "-o", out])
        assert result.exit_code == 0
        assert "saved" in result.stdout.lower()

    def test_pdf_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        out = str(tmp_path / "out.pdf")
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["pdf", "https://example.com", "-o", out])
        assert result.exit_code == 0

    def test_page_pdf_executes_with_options(self, tmp_path: Path) -> None:
        """Regression for bug #18: page-pdf must accept header/footer options."""
        backend = _make_mock_backend()
        backend.page_print_to_pdf = AsyncMock(return_value="YmFzZTY0")
        out = str(tmp_path / "page.pdf")
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "page-pdf",
                    "-o",
                    out,
                    "--landscape",
                    "--display-header-footer",
                    "--print-background",
                    "--scale",
                    "1.5",
                    "--paper-width",
                    "5.0",
                    "--paper-height",
                    "8.0",
                ],
            )
        assert result.exit_code == 0, result.output
        backend.page_print_to_pdf.assert_awaited_once()
        kwargs = backend.page_print_to_pdf.await_args.kwargs
        assert kwargs["landscape"] is True
        assert kwargs["display_header_footer"] is True
        assert kwargs["print_background"] is True
        assert kwargs["scale"] == 1.5
        assert kwargs["paper_width"] == 5.0
        assert kwargs["paper_height"] == 8.0

    def test_crawl_exits_nonzero_when_no_pages_crawled(self) -> None:
        """Regression for bug #25: crawl must exit non-zero when 0 pages visited."""
        from wavexis.exceptions import WaitTimeoutError

        backend = _make_mock_backend()
        # Every navigate() call times out → 0 pages crawled.
        backend.navigate = AsyncMock(side_effect=WaitTimeoutError("load", 30000))
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["crawl", "https://example.com", "--depth", "1"])
        assert result.exit_code != 0, result.output
        assert "0 pages" in result.output

    def test_crawl_exits_zero_when_pages_crawled(self) -> None:
        """A successful crawl of at least one page must exit 0."""
        backend = _make_mock_backend()
        backend.navigate = AsyncMock()
        # eval is called twice per page (title, then links). Provide enough
        # values for the start page and any discovered links at depth 1.
        backend.eval = AsyncMock(side_effect=["Example Page", [], "About Page", []])
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["crawl", "https://example.com", "--depth", "1"])
        assert result.exit_code == 0, result.output
        assert "pages" in result.output

    def test_eval_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["eval", "https://example.com", "--expression", "1+1"])
        assert result.exit_code == 0

    def test_eval_unreadable_file(self, tmp_path: Path) -> None:
        """An unreadable expression file should exit cleanly."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["eval", "https://example.com", "--file", str(tmp_path / "expr.js")]
            )
        assert result.exit_code == 1
        assert "failed to read expression file" in result.output.lower()

    def test_dom_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["dom", "document", "https://example.com"])
        assert result.exit_code == 0

    def test_dom_describe_enables_dom_first(self) -> None:
        """DOM node commands must fetch the document before using node IDs."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["dom", "describe", "https://example.com", "1"])
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()
        backend.dom_describe_node.assert_awaited_once_with(1)

    def test_dom_query_selector_enables_dom_first(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["dom", "query-selector", "https://example.com", "1", "input"]
            )
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()
        backend.dom_query_selector.assert_awaited_once_with(1, "input")

    def test_scrape_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["scrape", "https://example.com"])
        assert result.exit_code == 0

    def test_har_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        out = str(tmp_path / "har.json")
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["har", "https://example.com", "-o", out])
        assert result.exit_code == 0

    def test_screencast_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        out = str(tmp_path / "cast")
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["screencast", "https://example.com", "-o", out])
        assert result.exit_code == 0

    def test_cookies_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._capture._get_backend", return_value=backend):
            result = runner.invoke(app, ["cookies", "https://example.com"])
        assert result.exit_code == 0

    def test_console_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["console", "enable", "https://example.com"])
        assert result.exit_code == 0

    def test_console_capture_executes(self, tmp_path: Path) -> None:
        """Regression for bug #21: `console capture` must exist and work."""
        backend = _make_mock_backend()
        backend.capture_console = AsyncMock(return_value=[{"type": "log", "text": "hello"}])
        out = str(tmp_path / "console.json")
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["console", "capture", "https://example.com", "-o", out])
        assert result.exit_code == 0, result.output
        backend.capture_console.assert_awaited_once()
        # Default level is "all"
        assert backend.capture_console.await_args.kwargs.get("level", "all") == "all"

    def test_console_capture_level_option(self) -> None:
        """The --level option must be forwarded to the backend."""
        backend = _make_mock_backend()
        backend.capture_console = AsyncMock(return_value=[])
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["console", "capture", "https://example.com", "--level", "warning"],
            )
        assert result.exit_code == 0, result.output
        assert backend.capture_console.await_args.kwargs.get("level") == "warning"

    def test_logs_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["logs", "https://example.com"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionNavigation:
    """Execute navigation commands with mocked backend."""

    def test_navigate_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["navigate", "https://example.com"])
        assert result.exit_code == 0

    def test_back_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["back"])
        assert result.exit_code == 0

    def test_forward_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["forward"])
        assert result.exit_code == 0

    def test_reload_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["reload"])
        assert result.exit_code == 0

    def test_stop_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionInput:
    """Execute input commands with mocked backend."""

    def test_click_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._input._get_backend", return_value=backend):
            result = runner.invoke(app, ["input", "click", "https://example.com", "#btn"])
        assert result.exit_code == 0

    def test_type_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._input._get_backend", return_value=backend):
            result = runner.invoke(app, ["input", "type", "https://example.com", "#field", "hello"])
        assert result.exit_code == 0

    def test_fill_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._input._get_backend", return_value=backend):
            result = runner.invoke(app, ["input", "fill", "https://example.com", "#field", "val"])
        assert result.exit_code == 0

    def test_tap_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._input._get_backend", return_value=backend):
            result = runner.invoke(app, ["input", "tap", "https://example.com", "#btn"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionNetwork:
    """Execute network commands with mocked backend."""

    def test_block_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["network", "block", "https://example.com", "*api*"])
        assert result.exit_code == 0

    def test_throttle_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["network", "throttle", "--latency", "100"])
        assert result.exit_code == 0

    def test_mock_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["network", "mock", "*api*", '{"status": 200}'])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionAdvanced:
    """Execute advanced commands with mocked backend."""

    def test_tabs_list_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["tabs", "list"])
        assert result.exit_code == 0

    def test_headers_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["headers", '{"X-Custom": "value"}'])
        assert result.exit_code == 0

    def test_headers_missing_file_exits_cleanly(self) -> None:
        """A missing @file should produce a clean error, not a traceback."""
        with patch("wavexis.cli._network._get_backend") as mock_get:
            result = runner.invoke(app, ["headers", "@does_not_exist.json"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "unreadable" in result.output.lower()
        mock_get.assert_not_called()

    def test_user_agent_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["user-agent", "MyBot/1.0"])
        assert result.exit_code == 0

    def test_storage_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._experimental._get_backend", return_value=backend):
            result = runner.invoke(app, ["storage", "list", "https://example.com"])
        assert result.exit_code == 0

    def test_modify_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network_inspect._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "modify",
                    "https://example.com",
                    "--pattern",
                    "*api*",
                    "--header",
                    "X-Custom: value",
                ],
            )
        assert result.exit_code == 0

    def test_har_replay_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network_inspect._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["har-replay", "/tmp/test.har", "--url", "https://example.com"]
            )
        assert result.exit_code == 0

    def test_trace_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network_inspect._get_backend", return_value=backend):
            result = runner.invoke(app, ["trace", "start"])
        assert result.exit_code == 0

    def test_raw_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._experimental._get_backend", return_value=backend):
            result = runner.invoke(app, ["raw", "Page.reload"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionEmulation:
    """Execute emulation commands with mocked backend."""

    def test_devices_list(self) -> None:
        result = runner.invoke(app, ["devices", "--help"])
        assert result.exit_code == 0

    def test_browser_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network._get_backend", return_value=backend):
            result = runner.invoke(app, ["browser", "version"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionPerf:
    """Execute performance commands with mocked backend."""

    def test_cwv_executes(self) -> None:
        backend = _make_mock_backend()
        backend.eval = AsyncMock(
            side_effect=[
                {"lcp": 2000, "cls": 0.05, "inp": 100, "tbt": 50},
                {"ttfb": 400, "fcp": 1200, "load": 2500, "domSize": 500, "transferSize": 10000},
            ]
        )
        with patch("wavexis.cli._perf._get_backend", return_value=backend):
            result = runner.invoke(app, ["cwv", "https://example.com"])
        assert result.exit_code == 0

    def test_perf_executes(self) -> None:
        backend = _make_mock_backend()
        backend.eval = AsyncMock(return_value={"numRequests": 10, "numCached": 5})
        with patch("wavexis.cli._perf._get_backend", return_value=backend):
            result = runner.invoke(app, ["perf", "metrics", "https://example.com"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionSession:
    """Execute session commands with mocked backend."""

    def test_session_save_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        backend.eval = AsyncMock(return_value={})
        backend.get_cookies = AsyncMock(return_value=[])
        out = str(tmp_path / "session.json")
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(app, ["session", "save", "https://example.com", "-o", out])
        assert result.exit_code == 0

    def test_session_save_unwritable(self, tmp_path: Path) -> None:
        """A write failure while saving a session should exit cleanly."""
        backend = _make_mock_backend()
        backend.eval = AsyncMock(return_value={})
        backend.get_cookies = AsyncMock(return_value=[])
        out = str(tmp_path / "session.json")
        with (
            patch("wavexis.cli._session._get_backend", return_value=backend),
            patch("wavexis.actions.session.Path.write_text", side_effect=PermissionError("denied")),
        ):
            result = runner.invoke(app, ["session", "save", "https://example.com", "-o", out])
        assert result.exit_code == 1
        assert "failed to write session" in result.output.lower()

    def test_session_list_executes(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["session", "list"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionShadow:
    """Execute shadow DOM commands with mocked backend."""

    def test_shadow_executes(self) -> None:
        backend = _make_mock_backend()
        backend.eval = AsyncMock(return_value="{}")
        with patch("wavexis.cli._shadow._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["shadow", "eval", "https://example.com", "-s", "#host", "-e", "1+1"],
            )
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionIframe:
    """Execute iframe commands with mocked backend."""

    def test_iframe_executes(self) -> None:
        backend = _make_mock_backend()
        backend.get_tree = AsyncMock(return_value={"frames": [{"id": "frame1"}]})
        backend.eval = AsyncMock(return_value="{}")
        with patch("wavexis.cli._iframe._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "iframe",
                    "eval",
                    "https://example.com",
                    "--iframe",
                    "iframe#myframe",
                    "-e",
                    "1+1",
                ],
            )
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionExperimental:
    """Execute experimental commands with mocked backend."""

    def test_webauthn_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._experimental._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["webauthn", "add-virtual-authenticator", "https://example.com"]
            )
        assert result.exit_code == 0

    def test_webaudio_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._experimental._get_backend", return_value=backend):
            result = runner.invoke(app, ["webaudio", "list", "https://example.com"])
        assert result.exit_code == 0

    def test_media_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["media", "enable", "https://example.com"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionWorkflow:
    """Execute workflow commands."""

    def test_multi_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("actions:\n  - screenshot:\n      url: https://example.com\n")
        with patch("wavexis.cli._workflow._get_backend", return_value=backend):
            result = runner.invoke(app, ["multi", str(yaml_file)])
        assert result.exit_code == 0

    def test_batch_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        backend.screenshot = AsyncMock(return_value=b"png-bytes")
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com\nhttps://other.com\n")
        with patch("wavexis.cli._workflow._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "batch",
                    str(urls_file),
                    "screenshot",
                    "--output-dir",
                    str(tmp_path / "out"),
                    "--dry-run",
                ],
            )
        assert result.exit_code == 0

    def test_batch_unreadable_urls_file_exits_cleanly(self, tmp_path: Path) -> None:
        """An unreadable URLs file should produce a clean error, not a traceback."""
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com\n")
        with (
            patch("pathlib.Path.read_text", side_effect=PermissionError("denied")),
            patch("wavexis.cli._workflow._get_backend") as mock_get,
        ):
            result = runner.invoke(
                app,
                [
                    "batch",
                    str(urls_file),
                    "screenshot",
                    "--output-dir",
                    str(tmp_path / "out"),
                ],
            )
        assert result.exit_code == 1
        assert "unreadable" in result.output.lower() or "not found" in result.output.lower()
        mock_get.assert_not_called()

    def test_record_unwritable_output_exits_cleanly(self, tmp_path: Path) -> None:
        """A failure to write the recorded config should produce a clean error."""
        with patch("pathlib.Path.write_text", side_effect=PermissionError("denied")):
            result = runner.invoke(
                app,
                [
                    "record",
                    "https://example.com",
                    "-o",
                    str(tmp_path / "out.yml"),
                    "--actions",
                    "screenshot",
                ],
            )
        assert result.exit_code == 1
        assert "failed to write" in result.output.lower()


@pytest.mark.unit
class TestCLIExecutionInspect:
    """Execute inspect commands with mocked backend."""

    def test_inspect_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network_inspect._get_backend", return_value=backend):
            result = runner.invoke(app, ["inspect", "https://example.com"])
        assert result.exit_code == 0

    def test_events_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._network_inspect._get_backend", return_value=backend):
            result = runner.invoke(app, ["events", "--help"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionAdvancedFull:
    """Execute all advanced commands with mocked backend."""

    def test_a11y_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["a11y", "https://example.com"])
        assert result.exit_code == 0

    def test_download_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        backend.intercept_download = AsyncMock(return_value=b"file-data")
        out = str(tmp_path / "dl.bin")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["download", "https://example.com", "-o", out])
        assert result.exit_code == 0

    def test_download_no_download_raises_error(self, tmp_path: Path) -> None:
        """Missing download within timeout should report a clean error."""
        backend = _make_mock_backend()
        backend.intercept_download = AsyncMock(return_value=b"")
        out = str(tmp_path / "dl.bin")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["download", "https://example.com", "-o", out])
        assert result.exit_code == 1
        assert "No download was intercepted" in result.output

    def test_download_pattern_wildcard_not_expanded(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Windows wildcards in option values must not expand to file lists."""
        if os.name != "nt":
            pytest.skip("Windows wildcard expansion only applies on Windows")
        out = str(tmp_path / "dl.bin")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "wavexis",
                "download",
                "https://example.com/",
                "--pattern",
                ".*",
                "--selector",
                "none",
                "-o",
                out,
            ],
        )
        backend = _make_mock_backend()
        backend.intercept_download = AsyncMock(return_value=b"file-data")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = app(standalone_mode=False)
        assert result in (None, 0)
        assert backend.intercept_download.called
        assert backend.intercept_download.call_args.args[0] == ".*"

    def test_dialog_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["dialog", "https://example.com"])
        assert result.exit_code == 0

    def test_dialog_dismiss(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["dialog", "https://example.com", "-a", "dismiss"])
        assert result.exit_code == 0

    def test_dialog_no_dialog_reports_clean_error(self) -> None:
        """When no dialog opens within the timeout, the CLI reports a clean error."""
        backend = _make_mock_backend()
        backend.dialog_wait_for_opening = AsyncMock(side_effect=TimeoutError())
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["dialog", "https://example.com"])
        assert result.exit_code == 1
        assert "No JavaScript dialog opened" in result.output

    def test_permissions_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["permissions", "grant"])
        assert result.exit_code == 0

    def test_permissions_reset(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["permissions", "reset"])
        assert result.exit_code == 0

    def test_security_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["security", "enable", "https://example.com"])
        assert result.exit_code == 0

    def test_security_no_subcommand_shows_help(self) -> None:
        """Running `wavexis security` without a subcommand should show help."""
        result = runner.invoke(app, ["security"])
        assert result.exit_code == 0
        assert "Commands" in result.output
        assert "enable" in result.output

    def test_security_ignore_cert(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["security", "set-ignore-certificate-errors", "https://example.com", "true"]
            )
        assert result.exit_code == 0

    def test_lighthouse_executes(self) -> None:
        backend = _make_mock_backend()
        backend.perf_metrics = AsyncMock(return_value={"ScriptCount": 1, "JSHeapUsedSize": 1000})
        backend.eval = AsyncMock(
            side_effect=[
                {"lcp": 2000, "cls": 0.05, "inp": 100, "tbt": 50, "fcp": 1200, "ttfb": 400},
                {"lcp": 2000, "cls": 0.05, "inp": 100},
                {"issues": [], "issue_count": 0},
                {"title": "Test", "meta_description": "desc"},
                {"issues": [], "is_https": True},
            ]
        )
        backend.capture_console = AsyncMock(return_value=[])
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["lighthouse", "https://example.com"])
        assert result.exit_code == 0

    def test_lighthouse_with_threshold(self) -> None:
        backend = _make_mock_backend()
        backend.perf_metrics = AsyncMock(return_value={"ScriptCount": 1, "JSHeapUsedSize": 1000})
        backend.eval = AsyncMock(
            side_effect=[
                {"lcp": 2000, "cls": 0.05, "inp": 100, "tbt": 50, "fcp": 1200, "ttfb": 400},
                {"lcp": 2000, "cls": 0.05, "inp": 100},
                {"issues": [], "issue_count": 0},
                {"title": "Test", "meta_description": "desc"},
                {"issues": [], "is_https": True},
            ]
        )
        backend.capture_console = AsyncMock(return_value=[])
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["lighthouse", "https://example.com", "-t", "ttfb_ms=800"])
        assert result.exit_code == 0

    def test_lighthouse_missing_budget_file_exits_cleanly(self) -> None:
        """A missing budget file should produce a clean error, not a traceback."""
        with patch("wavexis.cli._advanced._get_backend") as mock_get:
            result = runner.invoke(
                app, ["lighthouse", "https://example.com", "-b", "does_not_exist.json"]
            )
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "unreadable" in result.output.lower()
        mock_get.assert_not_called()

    def test_extension_install(self) -> None:
        backend = _make_mock_backend()
        backend.extension_install = AsyncMock(return_value="ext-123")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-install", "/tmp/ext"])
        assert result.exit_code == 0

    def test_extension_uninstall(self) -> None:
        backend = _make_mock_backend()
        backend.extension_uninstall = AsyncMock()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-uninstall", "ext-123"])
        assert result.exit_code == 0

    def test_extension_list_empty(self) -> None:
        backend = _make_mock_backend()
        backend.extension_list = AsyncMock(return_value=[])
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-list"])
        assert result.exit_code == 0

    def test_extension_list_with_ext(self) -> None:
        backend = _make_mock_backend()
        backend.extension_list = AsyncMock(
            return_value=[{"id": "ext1", "name": "Test", "version": "1.0", "enabled": True}]
        )
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["extension-list"])
        assert result.exit_code == 0

    def test_pref_get(self) -> None:
        backend = _make_mock_backend()
        backend.get_pref = AsyncMock(return_value="value")
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["pref-get", "download.default_directory"])
        assert result.exit_code == 0

    def test_pref_set(self) -> None:
        backend = _make_mock_backend()
        backend.set_pref = AsyncMock()
        with patch("wavexis.cli._advanced._get_backend", return_value=backend):
            result = runner.invoke(app, ["pref-set", "key", "value"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionDebug:
    """Execute debug commands with mocked backend."""

    def test_logs_executes(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._navigation._get_backend", return_value=backend):
            result = runner.invoke(app, ["logs", "https://example.com"])
        assert result.exit_code == 0

    def test_target_list_does_not_require_url(self) -> None:
        """Regression for bug #12/#23: `target list` must not require a URL."""
        backend = _make_mock_backend()
        backend.target_get_targets = AsyncMock(
            return_value=[{"targetId": "t1", "url": "https://example.com"}]
        )
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["target", "list"])
        assert result.exit_code == 0, result.output
        backend.target_get_targets.assert_awaited_once()
        # Crucially, navigate must NOT have been called.
        backend.navigate.assert_not_awaited()

    def test_target_list_with_url_is_rejected(self) -> None:
        """Passing a URL to `target list` should now be rejected (no such arg)."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["target", "list", "https://example.com"])
        # Typer rejects the extra positional argument.
        assert result.exit_code != 0


@pytest.mark.unit
class TestCLIExecutionEmulationFull:
    """Execute emulation commands with mocked backend."""

    def test_devices_emulate(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._emulation._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["emulation", "device", "https://example.com", "--device", "iPhone 12"],
            )
        assert result.exit_code == 0

    def test_devices_list(self) -> None:
        result = runner.invoke(app, ["devices"])
        assert result.exit_code == 0

    def test_emulation_can_emulate_no_url(self) -> None:
        """Regression for bug #23: `emulation can-emulate` must not require a URL."""
        backend = _make_mock_backend()
        backend.can_emulate = AsyncMock(return_value=True)
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["emulation", "can-emulate"])
        assert result.exit_code == 0, result.output
        backend.can_emulate.assert_awaited_once()
        backend.navigate.assert_not_awaited()


@pytest.mark.unit
class TestCLIExecutionConfig:
    """Execute config commands."""

    def test_config_init(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["config", "init"])
        assert result.exit_code == 0

    def test_config_show(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

    def test_config_set(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["config", "set", "--key", "backend", "--value", "cdp"])
        assert result.exit_code == 0

    def test_auth_missing_context_file_exits_cleanly(self) -> None:
        """A missing auth context file should produce a clean error, not a traceback."""
        with patch("wavexis.cli._config._get_backend") as mock_get:
            result = runner.invoke(app, ["auth", "does_not_exist.json", "https://example.com"])
        assert result.exit_code == 1
        assert "auth context" in result.output.lower()
        mock_get.assert_not_called()


@pytest.mark.unit
class TestCLIExecutionNL:
    """Execute natural language command."""

    def test_nl_executes(self) -> None:
        backend = _make_mock_backend()
        backend.nl_find = AsyncMock(return_value=["button#login"])
        with patch("wavexis.cli._nl._get_backend", return_value=backend):
            result = runner.invoke(app, ["nl", "find", "https://example.com", "login button"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionServe:
    """Execute serve command."""

    def test_serve_dry_run(self) -> None:
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionRecordReplay:
    """Execute record and replay commands."""

    def test_record_help(self) -> None:
        result = runner.invoke(app, ["record", "--help"])
        assert result.exit_code == 0

    def test_record_interactive_help(self) -> None:
        """--interactive help must be parseable so the batch runner can skip it."""
        result = runner.invoke(app, ["record", "https://example.com", "--interactive", "--help"])
        assert result.exit_code == 0

    def test_replay_help(self) -> None:
        result = runner.invoke(app, ["replay", "--help"])
        assert result.exit_code == 0

    def test_repl_help(self) -> None:
        """repl --help must be parseable so the batch runner can skip it."""
        result = runner.invoke(app, ["repl", "--help"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionSessionFull:
    """Execute all session commands with mocked backend."""

    def test_session_load_executes(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        session_file = tmp_path / "session.json"
        session_file.write_text('{"cookies":[],"local_storage":{},"session_storage":{},"url":""}')
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["session", "load", str(session_file), "--url", "https://example.com"],
            )
        assert result.exit_code == 0

    def test_session_load_no_url(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        session_file = tmp_path / "session.json"
        session_file.write_text('{"cookies":[],"local_storage":{},"session_storage":{},"url":""}')
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(app, ["session", "load", str(session_file)])
        assert result.exit_code == 0

    def test_session_load_not_found(self) -> None:
        result = runner.invoke(app, ["session", "load", "nonexistent.json"])
        assert result.exit_code == 1

    def test_session_load_unreadable(self, tmp_path: Path) -> None:
        """A read failure while loading a session should exit cleanly."""
        backend = _make_mock_backend()
        session_file = tmp_path / "session.json"
        session_file.write_text('{"cookies":[],"local_storage":{},"session_storage":{},"url":""}')
        with (
            patch("wavexis.cli._session._get_backend", return_value=backend),
            patch("wavexis.actions.session.Path.read_text", side_effect=PermissionError("denied")),
        ):
            result = runner.invoke(app, ["session", "load", str(session_file)])
        assert result.exit_code == 1
        assert "failed to read session" in result.output.lower()

    def test_session_load_invalid_json(self, tmp_path: Path) -> None:
        """A malformed session JSON file should exit cleanly."""
        backend = _make_mock_backend()
        session_file = tmp_path / "session.json"
        session_file.write_text("not valid json")
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(app, ["session", "load", str(session_file)])
        assert result.exit_code == 1
        assert "invalid session json" in result.output.lower()

    def test_session_delete(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / ".wavexis" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "test.json").write_text("{}")
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["session", "delete", "--name", "test"])
        assert result.exit_code == 0

    def test_session_delete_no_name(self) -> None:
        result = runner.invoke(app, ["session", "delete"])
        assert result.exit_code == 1

    def test_session_delete_not_found(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["session", "delete", "--name", "nonexistent"])
        assert result.exit_code == 1

    def test_session_save_named(self, tmp_path: Path) -> None:
        backend = _make_mock_backend()
        with (
            patch("wavexis.cli._session._get_backend", return_value=backend),
            patch("pathlib.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(
                app,
                ["session", "save", "https://example.com", "--name", "test"],
            )
        assert result.exit_code == 0

    def test_session_save_no_url(self) -> None:
        result = runner.invoke(app, ["session", "save"])
        assert result.exit_code == 1

    def test_session_unknown_action(self) -> None:
        result = runner.invoke(app, ["session", "unknown"])
        assert result.exit_code == 1

    def test_session_list_with_sessions(self, tmp_path: Path) -> None:
        sessions_dir = tmp_path / ".wavexis" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "test1.json").write_text("{}")
        (sessions_dir / "test2.json").write_text("{}")
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = runner.invoke(app, ["session", "list"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionExtractForm:
    """Execute extract and form commands."""

    def test_extract_executes(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value=[{"title": "Test"}])
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(app, ["extract", "https://example.com", "-s", '{"title":"h1"}'])
        assert result.exit_code == 0

    def test_extract_invalid_schema(self) -> None:
        result = runner.invoke(app, ["extract", "https://example.com", "-s", "invalid json"])
        assert result.exit_code == 1

    def test_form_executes(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value=True)
        backend.click = AsyncMock()
        with patch("wavexis.cli._session._get_backend", return_value=backend):
            result = runner.invoke(app, ["form", "https://example.com", "-d", '{"#name":"test"}'])
        assert result.exit_code == 0

    def test_form_invalid_data(self) -> None:
        result = runner.invoke(app, ["form", "https://example.com", "-d", "invalid json"])
        assert result.exit_code == 1


@pytest.mark.unit
class TestCLIExecutionMulti:
    """Execute multi command."""

    def test_multi_dry_run(self, tmp_path: Path) -> None:
        config = tmp_path / "config.yaml"
        config.write_text("actions:\n  - navigate:\n      url: https://example.com\n")
        result = runner.invoke(app, ["multi", str(config), "--dry-run"])
        assert result.exit_code == 0

    def test_multi_file_not_found(self) -> None:
        result = runner.invoke(app, ["multi", "nonexistent.yaml"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestCLIExecutionCSS:
    """Execute CSS debug commands."""

    def test_css_styles(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value={"color": "red"})
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["css", "styles", "https://example.com", "-s", "div"])
        assert result.exit_code == 0

    def test_css_stylesheets(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value=[])
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["css", "stylesheets", "https://example.com"])
        assert result.exit_code == 0

    def test_css_rules(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value=[])
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["css", "rules", "https://example.com", "--stylesheet-id", "1"],
            )
        assert result.exit_code == 0

    def test_css_computed(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value={"color": "red"})
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["css", "computed", "https://example.com", "-s", "div"])
        assert result.exit_code == 0

    def test_css_enable_enables_dom_first(self) -> None:
        """CSS enable command must enable DOM domain before CSS.enable."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["css", "enable", "https://example.com"])
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()

    def test_css_set_stylesheet_text_enables_dom_first(self) -> None:
        """CSS set-stylesheet-text must enable DOM domain before operating."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app, ["css", "set-stylesheet-text", "https://example.com", "s1", "body{}"]
            )
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()

    def test_css_collect_class_names_enables_dom_first(self) -> None:
        """CSS collect-class-names must enable DOM domain before operating."""
        backend = _make_mock_backend()
        backend.css_collect_class_names = AsyncMock(return_value=[])
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["css", "collect-class-names", "https://example.com", "1"])
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()


@pytest.mark.unit
class TestCLIExecutionDebugFull:
    """Execute debug subcommands."""

    def test_debug_breakpoint(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "debug",
                    "breakpoint",
                    "https://example.com",
                    "--url",
                    "script.js",
                    "--line",
                    "10",
                ],
            )
        assert result.exit_code == 0

    def test_debug_function_breakpoint(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["debug", "function-breakpoint", "https://example.com", "--function-name", "foo"],
            )
        assert result.exit_code == 0

    def test_debug_remove_breakpoint(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["debug", "remove-breakpoint", "https://example.com", "--breakpoint-id", "bp1"],
            )
        assert result.exit_code == 0

    def test_debug_step_over(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "step-over", "https://example.com"])
        assert result.exit_code == 0

    def test_debug_step_into(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "step-into", "https://example.com"])
        assert result.exit_code == 0

    def test_debug_step_out(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "step-out", "https://example.com"])
        assert result.exit_code == 0

    def test_debug_pause(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "pause", "https://example.com"])
        assert result.exit_code == 0

    def test_debug_resume(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "resume", "https://example.com"])
        assert result.exit_code == 0

    def test_debug_listeners(self) -> None:
        backend = _make_mock_backend()
        backend.dom_query = AsyncMock(return_value=[])
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["debug", "listeners", "https://example.com", "-s", "div"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionOverlay:
    """Execute overlay commands."""

    def test_overlay_highlight(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["overlay", "highlight", "https://example.com", "-s", "div"],
            )
        assert result.exit_code == 0

    def test_overlay_clear(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["overlay", "clear", "https://example.com"])
        assert result.exit_code == 0

    def test_overlay_paint_rects_uses_result_param(self) -> None:
        """overlay paint-rects must send 'result' not 'show' to CDP."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["overlay", "paint-rects", "https://example.com"])
        assert result.exit_code == 0
        backend.overlay_set_show_paint_rects.assert_awaited_once_with(True)

    def test_overlay_layout_shift_regions_uses_result_param(self) -> None:
        """overlay layout-shift-regions must send 'result' not 'show' to CDP."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["overlay", "layout-shift-regions", "https://example.com"])
        assert result.exit_code == 0
        backend.overlay_set_show_layout_shift_regions.assert_awaited_once_with(True)

    def test_overlay_enable_enables_dom_first(self) -> None:
        """overlay enable must enable DOM domain before Overlay.enable."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(app, ["overlay", "enable", "https://example.com"])
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()

    def test_dom_debugger_set_dom_breakpoint_enables_dom_first(self) -> None:
        """dom-debugger set-dom-breakpoint must enable DOM domain before operating."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "dom-debugger",
                    "set-dom-breakpoint",
                    "https://example.com",
                    "1",
                    "subtree-modified",
                ],
            )
        assert result.exit_code == 0
        backend.dom_get_document.assert_awaited_once()

    def test_dom_push_nodes_by_backend_ids_invalid_input(self) -> None:
        """dom push-nodes-by-backend-ids with non-integer input gives clean error."""
        backend = _make_mock_backend()
        with patch("wavexis.cli._debug._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["dom", "push-nodes-by-backend-ids", "https://example.com", "test"],
            )
        assert result.exit_code == 1
        backend.dom_push_nodes_by_backend_ids_to_frontend.assert_not_awaited()


@pytest.mark.unit
class TestCLIExecutionEmulationExtra:
    """Execute extra emulation commands."""

    def test_emulation_viewport(self) -> None:
        backend = _make_mock_backend()
        with patch("wavexis.cli._emulation._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "emulation",
                    "viewport",
                    "https://example.com",
                    "--width",
                    "800",
                    "--height",
                    "600",
                ],
            )
        assert result.exit_code == 0

    def test_emulation_geolocation(self) -> None:
        backend = _make_mock_backend()
        backend.screenshot = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
        with patch("wavexis.cli._emulation._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "emulation",
                    "geolocation",
                    "https://example.com",
                    "--lat",
                    "37.7",
                    "--lon",
                    "-122.4",
                ],
            )
        assert result.exit_code == 0

    def test_emulation_timezone(self) -> None:
        backend = _make_mock_backend()
        backend.screenshot = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
        with patch("wavexis.cli._emulation._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                ["emulation", "timezone", "https://example.com", "--tz", "America/New_York"],
            )
        assert result.exit_code == 0

    def test_emulation_dark_mode(self) -> None:
        backend = _make_mock_backend()
        backend.screenshot = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
        with patch("wavexis.cli._emulation._get_backend", return_value=backend):
            result = runner.invoke(app, ["emulation", "dark_mode", "https://example.com"])
        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIExecutionServeCLI:
    """Execute serve CLI commands."""

    def test_plugins_list(self) -> None:
        result = runner.invoke(app, ["plugins"])
        assert result.exit_code == 0

    def test_ws_help(self) -> None:
        result = runner.invoke(app, ["ws", "--help"])
        assert result.exit_code == 0

    def test_ws_duration_exceeds_timeout(self) -> None:
        """A WS capture duration >= command timeout should fail fast."""
        result = runner.invoke(app, ["ws", "https://example.com", "--duration", "30000"])
        assert result.exit_code == 1
        assert "shorter than the command timeout" in result.output


@pytest.mark.unit
class TestCLISameLoopCleanup:
    """Regression tests for Bug #89/#90: backend cleanup must run on the same event loop."""

    def test_record_interactive_closes_on_same_loop(self) -> None:
        """Verify record --interactive runs close_backend on the same event loop."""
        backend = _make_mock_backend()
        backend.new_tab_handle = AsyncMock()

        with (
            patch("wavexis.cli._workflow._get_backend", return_value=backend),
            patch(
                "wavexis.actions.record.record_session",
                new_callable=AsyncMock,
                return_value="yaml",
            ),
        ):
            result = runner.invoke(
                app,
                [
                    "record",
                    "https://example.com",
                    "--interactive",
                    "--duration",
                    "1",
                    "-o",
                    "out.yml",
                ],
            )
        assert result.exit_code == 0
        backend.close.assert_awaited()

    def test_repl_closes_on_same_loop(self) -> None:
        """Verify repl command runs close_backend on the same event loop."""
        backend = _make_mock_backend()

        with (
            patch("wavexis.cli._config._get_backend", return_value=backend),
            patch("wavexis.repl.repl_loop", new_callable=AsyncMock, return_value=[]),
        ):
            result = runner.invoke(app, ["repl"])
        assert result.exit_code == 0
        backend.close.assert_awaited()


class TestBatchFilenameSanitization:
    """Regression tests for filename sanitization in batch workflow writes."""

    def test_batch_screenshot_sanitizes_url_with_invalid_chars(self, tmp_path: Path) -> None:
        from tests.unit.test_concurrent_tabs import FakeBackend

        backend = FakeBackend()

        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com?x=1&y=2\n")
        out_dir = tmp_path / "out"

        with patch("wavexis.cli._workflow._get_backend", return_value=backend):
            result = runner.invoke(
                app,
                [
                    "batch",
                    str(urls_file),
                    "screenshot",
                    "--output-dir",
                    str(out_dir),
                ],
            )

        assert result.exit_code == 0, result.output
        assert any(out_dir.iterdir())

    def test_scrape_parallel_continues_on_error(self) -> None:
        """One failing URL must not abort parallel scraping for the rest."""
        from wavexis.actions.scrape import ScrapeAction

        backend = _make_mock_backend()
        tab = MagicMock()
        tab.close = AsyncMock()
        tab.navigate = AsyncMock()
        backend.new_tab_handle = AsyncMock(return_value=tab)

        side_effects = [
            ValueError("bad url"),
            [{"url": "https://ok.com", "result": "ok"}],
        ]

        with (
            patch("wavexis.cli._capture._get_backend", return_value=backend),
            patch.object(ScrapeAction, "execute", new=AsyncMock(side_effect=side_effects)),
        ):
            result = runner.invoke(
                app,
                [
                    "scrape",
                    "--concurrency",
                    "2",
                    "https://bad.com",
                    "https://ok.com",
                ],
            )

        assert result.exit_code == 0, result.output
        assert "ok" in result.output

    def test_sanitize_filename_handles_path_separators_and_reserved_chars(self) -> None:
        from wavexis.cli._workflow import _sanitize_filename

        assert "://" not in _sanitize_filename("https://a.com/b/c")
        assert "/" not in _sanitize_filename("https://a.com/b/c")
        assert "?" not in _sanitize_filename("https://a.com?q=1")
        assert _sanitize_filename("https://example.com") == "https_example.com"
