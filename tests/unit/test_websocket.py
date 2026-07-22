"""Unit tests for the WebSocket intercept action."""

import pytest

from wavexis.actions.websocket import WebSocketInterceptAction, WebSocketParams
from wavexis.exceptions import ActionError


class TestWebSocketParams:
    """Tests for WebSocketParams validation."""

    @pytest.mark.unit
    def test_defaults(self) -> None:
        """Default parameters are accepted."""
        params = WebSocketParams()
        assert params.url == ""
        assert params.url_pattern == ""

    @pytest.mark.unit
    def test_invalid_url_raises(self) -> None:
        """Reject malformed URLs."""
        with pytest.raises(ActionError):
            WebSocketParams(url="not-a-url")

    @pytest.mark.unit
    def test_invalid_url_pattern_regex_raises(self) -> None:
        """Reject invalid regex for url_pattern."""
        with pytest.raises(ActionError):
            WebSocketParams(url_pattern="[")

    @pytest.mark.unit
    def test_non_positive_duration_raises(self) -> None:
        """Reject non-positive duration."""
        with pytest.raises(ActionError):
            WebSocketParams(duration_ms=0)

    @pytest.mark.unit
    def test_mock_responses_must_be_dict(self) -> None:
        """mock_responses must be a dict."""
        with pytest.raises(ActionError):
            WebSocketParams(mock_responses="not-a-dict")  # type: ignore[arg-type]


class TestWebSocketInterceptAction:
    """Tests for WebSocketInterceptAction behavior."""

    @pytest.mark.unit
    def test_action_requires_params(self) -> None:
        """Action stores params."""
        params = WebSocketParams(url="https://example.com")
        action = WebSocketInterceptAction(params)
        assert action.params is params
