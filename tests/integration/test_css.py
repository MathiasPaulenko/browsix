"""Integration tests for CSS actions against a real Chrome browser."""

import pytest

from wavexis.actions.css import CSSAction, CSSActionParams
from wavexis.backend.cdp import CDPBackend
from wavexis.config import BrowserOptions, WaitStrategy

pytestmark = [pytest.mark.integration, pytest.mark.chrome]


@pytest.fixture
def backend() -> CDPBackend:
    """Backend."""
    return CDPBackend()


@pytest.fixture
def browser_opts() -> BrowserOptions:
    """Browser opts."""
    return BrowserOptions(headless=True)


async def test_css_styles(
    backend: CDPBackend, browser_opts: BrowserOptions, local_http_server: str
) -> None:
    """Test css styles."""
    params = CSSActionParams(
        url=local_http_server,
        action="styles",
        selector="body",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await CSSAction(params).execute(backend)
    assert isinstance(result, dict)
    assert "inlineStyles" in result


async def test_css_stylesheets(
    backend: CDPBackend, browser_opts: BrowserOptions, local_http_server: str
) -> None:
    """Test css stylesheets."""
    params = CSSActionParams(
        url=local_http_server,
        action="stylesheets",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await CSSAction(params).execute(backend)
    assert isinstance(result, list)


async def test_css_computed(
    backend: CDPBackend, browser_opts: BrowserOptions, local_http_server: str
) -> None:
    """Test css computed."""
    params = CSSActionParams(
        url=local_http_server,
        action="computed",
        selector="body",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await CSSAction(params).execute(backend)
    assert isinstance(result, dict)
    assert "color" in result or "display" in result
