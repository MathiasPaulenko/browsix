"""Integration tests for animation actions against a real Chrome browser."""

import pytest

from wavexis.actions.animation import AnimationAction
from wavexis.backend.cdp import CDPBackend
from wavexis.config import AnimationParams, BrowserOptions, WaitStrategy

pytestmark = [pytest.mark.integration, pytest.mark.chrome]


@pytest.fixture
def backend() -> CDPBackend:
    """Backend."""
    return CDPBackend()


@pytest.fixture
def browser_opts() -> BrowserOptions:
    """Browser opts."""
    return BrowserOptions(headless=True)


async def test_animation_list(
    backend: CDPBackend, browser_opts: BrowserOptions, local_http_server: str
) -> None:
    """Test animation list."""
    params = AnimationParams(
        url=local_http_server,
        action="list",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await AnimationAction(params).execute(backend)
    assert isinstance(result, list)
