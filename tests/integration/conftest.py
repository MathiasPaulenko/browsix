"""Integration-level pytest fixtures and configuration.

Fixtures defined here are only available to tests under tests/integration/.
Root-level conftest.py provides shared markers.
"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def integration_backend() -> Any:
    """Return a real backend instance for integration tests.

    This fixture is a placeholder — actual integration tests should
    override it with a real CDPBackend or BiDiBackend launch.
    """
    pytest.skip("No real backend available in this environment")
