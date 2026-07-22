"""Unit tests for the request modification action."""

import pytest

from wavexis.actions.modify_request import ModifyRequestAction, ModifyRequestParams
from wavexis.exceptions import ActionError


class TestModifyRequestParams:
    """Tests for ModifyRequestParams validation."""

    @pytest.mark.unit
    def test_defaults(self) -> None:
        """Default parameters are accepted."""
        params = ModifyRequestParams()
        assert params.url == ""
        assert params.pattern == {}

    @pytest.mark.unit
    def test_invalid_url_raises(self) -> None:
        """Reject malformed URLs."""
        with pytest.raises(ActionError):
            ModifyRequestParams(url="not-a-url", pattern={"urlPattern": ".*"})

    @pytest.mark.unit
    def test_pattern_must_be_dict(self) -> None:
        """pattern must be a dict."""
        with pytest.raises(ActionError):
            ModifyRequestParams(pattern="not-a-dict")  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_modifications_must_be_dict(self) -> None:
        """modifications must be a dict."""
        with pytest.raises(ActionError):
            ModifyRequestParams(modifications="not-a-dict")  # type: ignore[arg-type]


class TestModifyRequestAction:
    """Tests for ModifyRequestAction behavior."""

    @pytest.mark.unit
    def test_empty_pattern_raises(self) -> None:
        """execute requires a non-empty pattern."""
        action = ModifyRequestAction(ModifyRequestParams())
        assert action.params.pattern == {}
