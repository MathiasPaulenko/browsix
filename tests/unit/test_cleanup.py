"""Unit tests for resource cleanup module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

import wavexis.cleanup as cleanup_mod
from wavexis.cleanup import (
    _cleanup_sync,
    register_backend,
    unregister_backend,
)


@pytest.mark.unit
class TestCleanup:
    """Tests for browser cleanup on crash."""

    def setup_method(self) -> None:
        """Reset cleanup state before each test."""
        cleanup_mod._cleanup_done = False
        cleanup_mod._registered_backends.clear()

    def test_register_and_unregister(self) -> None:
        backend = MagicMock()
        register_backend(backend)
        unregister_backend(backend)

    def test_cleanup_with_no_backends(self) -> None:
        _cleanup_sync()

    def test_cleanup_closes_registered_backends(self) -> None:
        backend = MagicMock()
        backend.close = AsyncMock()
        register_backend(backend)
        _cleanup_sync()
        backend.close.assert_called_once()

    def test_cleanup_is_idempotent(self) -> None:
        backend = MagicMock()
        backend.close = AsyncMock()
        register_backend(backend)
        _cleanup_sync()
        _cleanup_sync()
        backend.close.assert_called_once()

    def test_cleanup_swallows_errors(self) -> None:
        backend = MagicMock()
        backend.close = AsyncMock(side_effect=RuntimeError("boom"))
        register_backend(backend)
        _cleanup_sync()
