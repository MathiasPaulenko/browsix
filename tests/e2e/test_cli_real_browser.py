"""End-to-end CLI tests that execute the real wavexis binary against a real Chrome browser.

Each test runs ``python -m wavexis <command>`` as a subprocess, launches
a real headless Chrome via cdpwave, and verifies exit codes, output files,
and stdout content.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.integration, pytest.mark.chrome]

EXAMPLE_URL = "https://example.com"


class TestCLIVersion:
    """Tests for the --version flag (no browser needed but validates CLI works)."""

    def test_version_flag(self, cli) -> None:
        """``wavexis --version`` prints the version and exits 0."""
        result = cli.run(["--version"])
        result.assert_success()
        result.assert_stdout_contains("wavexis")


class TestCLIBrowserVersion:
    """Test ``wavexis browser version`` against a real Chrome."""

    def test_browser_version(self, cli) -> None:
        """``wavexis browser version`` returns a Chrome version string."""
        result = cli.run(["browser", "version"])
        result.assert_success()
        # Output should contain a version-like string (e.g. "Chrome/120.0...")
        assert "Chrome" in result.stdout or "chromium" in result.stdout.lower(), (
            f"Expected Chrome version in stdout, got:\n{result.stdout}"
        )


class TestCLINavigate:
    """Test ``wavexis navigate`` against a real Chrome."""

    def test_navigate_success(self, cli) -> None:
        """``wavexis navigate <url>`` exits 0 and prints confirmation."""
        result = cli.run(["navigate", EXAMPLE_URL])
        result.assert_success()
        result.assert_stdout_contains("Navigated")


class TestCLIScreenshot:
    """Test ``wavexis screenshot`` against a real Chrome."""

    def test_screenshot_png(self, cli, tmp_path: Path) -> None:
        """``wavexis screenshot`` produces a non-empty PNG file."""
        out = tmp_path / "screenshot.png"
        result = cli.run(["screenshot", EXAMPLE_URL, "-o", str(out)])
        result.assert_success()
        result.assert_stdout_contains("saved")
        result.assert_file_exists(out)

        # PNG magic bytes
        assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "Screenshot file is not a valid PNG"

    def test_screenshot_full_page(self, cli, tmp_path: Path) -> None:
        """``wavexis screenshot --full-page`` produces a non-empty PNG."""
        out = tmp_path / "full_page.png"
        result = cli.run(["screenshot", EXAMPLE_URL, "-o", str(out), "--full-page"])
        result.assert_success()
        result.assert_file_exists(out)

    def test_screenshot_jpeg_format(self, cli, tmp_path: Path) -> None:
        """``wavexis screenshot --format jpeg`` produces a JPEG file."""
        out = tmp_path / "screenshot.jpg"
        result = cli.run(["screenshot", EXAMPLE_URL, "-o", str(out), "--format", "jpeg"])
        result.assert_success()
        result.assert_file_exists(out)
        # JPEG SOI marker
        assert out.read_bytes()[:2] == b"\xff\xd8", "File is not a valid JPEG"


class TestCLIEval:
    """Test ``wavexis eval`` against a real Chrome."""

    def test_eval_simple_expression(self, cli) -> None:
        """``wavexis eval --expression '1+1'`` returns 2."""
        result = cli.run(["eval", EXAMPLE_URL, "--expression", "1+1"])
        result.assert_success()
        # The result should contain "2" somewhere in stdout
        assert "2" in result.stdout, f"Expected '2' in eval output, got:\n{result.stdout}"

    def test_eval_document_title(self, cli) -> None:
        """``wavexis eval --expression 'document.title'`` returns the page title."""
        result = cli.run(["eval", EXAMPLE_URL, "--expression", "document.title"])
        result.assert_success()
        # example.com has title "Example Domain"
        assert "Example Domain" in result.stdout, (
            f"Expected 'Example Domain' in eval output, got:\n{result.stdout}"
        )

    def test_eval_with_assert_pass(self, cli) -> None:
        """``wavexis eval --assert '== Example Domain'`` exits 0 when assertion passes."""
        result = cli.run(
            [
                "eval",
                EXAMPLE_URL,
                "--expression",
                "document.title",
                "--assert",
                "== Example Domain",
            ]
        )
        result.assert_success()
        result.assert_stdout_contains("PASS")

    def test_eval_with_assert_fail(self, cli) -> None:
        """``wavexis eval --assert '== Wrong'`` exits 1 when assertion fails."""
        result = cli.run(
            [
                "eval",
                EXAMPLE_URL,
                "--expression",
                "document.title",
                "--assert",
                "== Wrong Title",
            ]
        )
        result.assert_exit_code(1)
        result.assert_stdout_contains("FAIL")


class TestCLIPDF:
    """Test ``wavexis pdf`` against a real Chrome."""

    def test_pdf_generation(self, cli, tmp_path: Path) -> None:
        """``wavexis pdf`` produces a non-empty PDF file."""
        out = tmp_path / "output.pdf"
        result = cli.run(["pdf", EXAMPLE_URL, "-o", str(out)])
        result.assert_success()
        result.assert_stdout_contains("saved")
        result.assert_file_exists(out)
        # PDF magic bytes
        assert out.read_bytes()[:5] == b"%PDF-", "File is not a valid PDF"


class TestCLIDom:
    """Test ``wavexis dom`` / ``wavexis eval`` against a real Chrome."""

    def test_dom_get(self, cli) -> None:
        """``wavexis eval`` returns the page HTML."""
        result = cli.run(
            [
                "eval",
                EXAMPLE_URL,
                "-e",
                "document.documentElement.outerHTML",
            ]
        )
        result.assert_success()
        # Should contain HTML tags from example.com
        assert "<html" in result.stdout.lower() or "example" in result.stdout.lower(), (
            f"Expected HTML content in dom output, got:\n{result.stdout}"
        )

    def test_dom_query(self, cli) -> None:
        """``wavexis eval`` returns a selected element's outer HTML."""
        result = cli.run(
            [
                "eval",
                EXAMPLE_URL,
                "-e",
                "document.querySelector('h1').outerHTML",
            ]
        )
        result.assert_success()


class TestCLICookies:
    """Test ``wavexis cookies`` against a real Chrome."""

    def test_cookies_get(self, cli, tmp_path: Path) -> None:
        """``wavexis cookies get --url <url>`` returns cookie data."""
        out = tmp_path / "cookies.json"
        result = cli.run(["cookies", "get", "--url", EXAMPLE_URL, "-o", str(out)])
        result.assert_success()
        result.assert_stdout_contains("saved")
        result.assert_file_exists(out)
        # Verify it's valid JSON
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, list)


class TestCLIConsole:
    """Test ``wavexis logs`` against a real Chrome."""

    def test_console_capture(self, cli, tmp_path: Path) -> None:
        """``wavexis logs <url>`` captures console/log output."""
        out = tmp_path / "console.json"
        result = cli.run(["logs", EXAMPLE_URL, "-o", str(out)])
        result.assert_success()
        result.assert_file_exists(out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "logs" in data
        assert isinstance(data["logs"], list)


class TestCLIScrape:
    """Test ``wavexis scrape`` against a real Chrome."""

    def test_scrape_single_url(self, cli) -> None:
        """``wavexis scrape <url>`` returns scrape results."""
        result = cli.run(["scrape", EXAMPLE_URL])
        result.assert_success()
        # Output should be JSON containing the scraped title
        data = json.loads(result.stdout.strip())
        assert isinstance(data, list)
        assert len(data) == 1
        assert "Example Domain" in str(data[0])


class TestCLIUserAgent:
    """Test ``wavexis user-agent`` against a real Chrome."""

    def test_set_user_agent(self, cli) -> None:
        """``wavexis user-agent <ua>`` exits 0."""
        result = cli.run(["user-agent", "WavexisTestBot/1.0"])
        result.assert_success()
        result.assert_stdout_contains("User-Agent")


class TestCLIHeaders:
    """Test ``wavexis headers`` against a real Chrome."""

    def test_set_headers(self, cli) -> None:
        """``wavexis headers '{"X-Test": "value"}'`` exits 0."""
        result = cli.run(["headers", '{"X-Test": "wavexis-e2e"}'])
        result.assert_success()
        result.assert_stdout_contains("Headers")


class TestCLIHelpAndCommands:
    """Test CLI help and command listing (no browser needed)."""

    def test_help(self, cli) -> None:
        """``wavexis --help`` exits 0 and shows usage."""
        result = cli.run(["--help"])
        result.assert_success()
        result.assert_stdout_contains("Usage")

    def test_no_args_shows_help(self, cli) -> None:
        """``wavexis`` with no args shows help (no_args_is_help=True)."""
        result = cli.run([])
        # Typer exits with code 0 for --help but 2 for missing command
        assert result.exit_code in (0, 2)

    def test_screenshot_help(self, cli) -> None:
        """``wavexis screenshot --help`` exits 0."""
        result = cli.run(["screenshot", "--help"])
        result.assert_success()
        result.assert_stdout_contains("screenshot")
