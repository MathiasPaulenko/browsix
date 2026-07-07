"""Integration tests for WebAuthn actions against a real Chrome browser."""

import pytest

from wavexis.actions.webauthn import WebAuthnAction, WebAuthnParams
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


async def test_webauthn_add_virtual_authenticator(
    backend: CDPBackend, browser_opts: BrowserOptions
) -> None:
    """Test webauthn add virtual authenticator."""
    params = WebAuthnParams(
        url="https://example.com",
        action="add-virtual-authenticator",
        protocol="ctap2",
        transport="usb",
        wait=WaitStrategy(strategy="load"),
        browser=browser_opts,
    )
    result = await WebAuthnAction(params).execute(backend)
    assert isinstance(result, str)
    assert len(result) > 0


async def test_webauthn_add_and_get_credentials(
    backend: CDPBackend, browser_opts: BrowserOptions
) -> None:
    """Test webauthn add and get credentials in a single session."""
    await backend.launch(browser_opts)
    try:
        await backend.navigate("https://example.com", WaitStrategy(strategy="load"))
        auth_id = await backend.webauthn_add_virtual_authenticator("ctap2", "usb")
        assert isinstance(auth_id, str)
        assert len(auth_id) > 0
        result = await backend.webauthn_get_credentials(auth_id)
        assert isinstance(result, list)
    finally:
        await backend.close()
