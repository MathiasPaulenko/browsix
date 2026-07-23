"""Integration tests for debug actions against a real Chrome browser."""

import asyncio

import pytest

from wavexis.actions.debug import DebugAction, DebugActionParams
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


async def test_debug_pause_resume(backend: CDPBackend, browser_opts: BrowserOptions) -> None:
    """Test debug pause and resume in a single session."""
    await backend.launch(browser_opts)
    try:
        await backend.navigate(
            "data:text/html,<script>setInterval(()=>{document.title=Date.now()},100)</script>",
            WaitStrategy(strategy="none"),
        )
        await asyncio.sleep(0.5)
        await backend.debug_pause()
        await backend.debug_resume()
    finally:
        await backend.close()


async def test_debug_step_over(backend: CDPBackend, browser_opts: BrowserOptions) -> None:
    """Test debug step over (requires pause first)."""
    await backend.launch(browser_opts)
    try:
        await backend.navigate(
            "data:text/html,<script>setInterval(()=>{document.title=Date.now()},100)</script>",
            WaitStrategy(strategy="none"),
        )
        await asyncio.sleep(0.5)
        await backend.debug_pause()
        await backend.debug_step_over()
    finally:
        await backend.close()


async def test_debug_listeners(
    backend: CDPBackend, browser_opts: BrowserOptions, local_http_server: str
) -> None:
    """Test debug listeners."""
    params = DebugActionParams(
        url=local_http_server,
        action="listeners",
        selector="body",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await DebugAction(params).execute(backend)
    assert isinstance(result, list)
