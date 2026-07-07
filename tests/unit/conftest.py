"""Unit-level pytest fixtures and configuration.

Fixtures defined here are only available to tests under tests/unit/.
Root-level conftest.py provides the shared MockBackend and markers.
"""

from __future__ import annotations

import pytest

from tests.conftest import MockBackend


@pytest.fixture
def unit_mock_backend() -> MockBackend:
    """Return a MockBackend scoped to unit tests only."""
    return MockBackend()
