"""Integration tests for debug actions against a real Chrome browser."""

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
    """Test debug pause and resume."""
    params = DebugActionParams(
        url="https://example.com",
        action="pause",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    await DebugAction(params).execute(backend)

    params_resume = DebugActionParams(
        action="resume",
        browser=browser_opts,
    )
    await DebugAction(params_resume).execute(backend)


async def test_debug_step_over(backend: CDPBackend, browser_opts: BrowserOptions) -> None:
    """Test debug step over (requires pause first)."""
    params_pause = DebugActionParams(
        url="https://example.com",
        action="pause",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    await DebugAction(params_pause).execute(backend)

    params_step = DebugActionParams(
        action="step_over",
        browser=browser_opts,
    )
    await DebugAction(params_step).execute(backend)


async def test_debug_listeners(backend: CDPBackend, browser_opts: BrowserOptions) -> None:
    """Test debug listeners."""
    params = DebugActionParams(
        url="https://example.com",
        action="listeners",
        selector="body",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await DebugAction(params).execute(backend)
    assert isinstance(result, list)
