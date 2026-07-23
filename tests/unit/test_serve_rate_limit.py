"""Tests for the HTTP API rate limiter."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from wavexis.serve import TokenBucket, _rate_limit_middleware


@pytest.mark.unit
class TestTokenBucket:
    """Direct unit tests for the TokenBucket implementation."""

    async def test_acquire_allows_up_to_capacity(self) -> None:
        bucket = TokenBucket(capacity=2, refill_period=60.0)
        assert await bucket.acquire() is True
        assert await bucket.acquire() is True
        assert await bucket.acquire() is False

    async def test_retry_after_positive_when_empty(self) -> None:
        bucket = TokenBucket(capacity=1, refill_period=60.0)
        await bucket.acquire()
        retry_after = await bucket.retry_after()
        assert retry_after > 0

    async def test_retry_after_zero_after_full_refill(self) -> None:
        with patch("wavexis.serve.time.monotonic", side_effect=[1.0, 1.0, 1.0, 61.0]):
            bucket = TokenBucket(capacity=1, refill_period=60.0)
            assert await bucket.acquire() is True
            assert await bucket.acquire() is False
            retry_after = await bucket.retry_after()
            assert retry_after == pytest.approx(0.0)

    async def test_rejects_invalid_capacity(self) -> None:
        with pytest.raises(ValueError, match="capacity must be a positive integer"):
            TokenBucket(capacity=0, refill_period=60.0)
        with pytest.raises(ValueError, match="capacity must be a positive integer"):
            TokenBucket(capacity=-1, refill_period=60.0)

    async def test_rejects_non_positive_refill_period(self) -> None:
        with pytest.raises(ValueError, match="refill_period must be positive"):
            TokenBucket(capacity=1, refill_period=0.0)
        with pytest.raises(ValueError, match="refill_period must be positive"):
            TokenBucket(capacity=1, refill_period=-1.0)

    async def test_concurrent_acquires_never_exceed_capacity(self) -> None:
        with patch("wavexis.serve.time.monotonic", return_value=1.0):
            bucket = TokenBucket(capacity=100, refill_period=60.0)

            async def _acquire() -> bool:
                return await bucket.acquire()

            results = await asyncio.gather(*(_acquire() for _ in range(150)))
            assert sum(1 for r in results if r is True) == 100
            assert sum(1 for r in results if r is False) == 50


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Tests for the aiohttp rate-limiting middleware."""

    async def _handler(self, request: web.Request) -> web.Response:
        return web.Response(text="ok")

    async def test_allows_requests_within_capacity(self) -> None:
        bucket = TokenBucket(capacity=2, refill_period=60.0)
        middleware = _rate_limit_middleware(bucket)
        request = make_mocked_request("GET", "/")

        response = await middleware(request, self._handler)
        assert response.status == 200
        response = await middleware(request, self._handler)
        assert response.status == 200

    async def test_returns_429_with_retry_after(self) -> None:
        bucket = TokenBucket(capacity=1, refill_period=60.0)
        middleware = _rate_limit_middleware(bucket)
        request = make_mocked_request("GET", "/")

        response = await middleware(request, self._handler)
        assert response.status == 200

        response = await middleware(request, self._handler)
        assert response.status == 429
        assert "Retry-After" in response.headers
        assert "rate limited" in response.text.lower()

    async def test_create_app_rate_limit_enabled(self) -> None:
        from aiohttp.test_utils import TestClient, TestServer

        from wavexis.serve import create_app

        app = create_app(rate_limit=1)
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        try:
            resp = await client.get("/health")
            assert resp.status == 200
            resp = await client.get("/health")
            assert resp.status == 429
            assert "Retry-After" in resp.headers
        finally:
            await client.close()

    async def test_create_app_rate_limit_zero_disabled(self) -> None:
        from wavexis.serve import create_app

        app = create_app(rate_limit=0)
        # Only the two default middlewares (logging + json error) should be present.
        assert len(app.middlewares) == 2

        app_none = create_app(rate_limit=None)
        assert len(app_none.middlewares) == 2
