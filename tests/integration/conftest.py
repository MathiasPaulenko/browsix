"""Integration-level pytest fixtures and configuration.

Fixtures defined here are only available to tests under tests/integration/.
Root-level conftest.py provides shared markers.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer


@pytest.fixture
def integration_backend() -> Any:
    """Return a real backend instance for integration tests.

    This fixture is a placeholder — actual integration tests should
    override it with a real CDPBackend or BiDiBackend launch.
    """
    pytest.skip("No real backend available in this environment")


async def _local_handler(request: web.Request) -> web.Response:
    """Serve the default test HTML page."""
    return web.Response(
        text="<!DOCTYPE html><html><head><title>Local Test Page</title></head>"
        "<body><h1>Hello Local Server</h1><p id='greeting'>World</p></body></html>",
        content_type="text/html",
    )


async def _example_handler(request: web.Request) -> web.Response:
    """Serve an example.com-like page to keep existing assertions valid."""
    return web.Response(
        text="<!DOCTYPE html>"
        "<html><head><title>Example Domain</title></head>"
        "<body><h1>Example Domain</h1>"
        "<p><a href='https://www.iana.org/domains/example'>More information...</a></p>"
        "</body></html>",
        content_type="text/html",
    )


async def _json_handler(request: web.Request) -> web.Response:
    """Serve a JSON payload for network/response tests."""
    return web.json_response({"status": "ok", "items": [1, 2, 3]})


async def _headers_handler(request: web.Request) -> web.Response:
    """Echo request headers."""
    return web.json_response(dict(request.headers))


async def _echo_handler(request: web.Request) -> web.Response:
    """Echo the request body."""
    body = await request.text()
    return web.Response(text=body, content_type=request.content_type or "text/plain")


async def _slow_handler(request: web.Request) -> web.Response:
    """Wait a configurable delay before responding."""
    delay = float(request.query.get("seconds", "0.1"))
    await asyncio.sleep(delay)
    return web.Response(text=f"waited {delay}s", content_type="text/plain")


@pytest.fixture
async def local_http_server() -> str:
    """Start a local aiohttp server and yield its base URL.

    Returns the server base URL (e.g. ``http://127.0.0.1:12345/``). Tests
    can append paths like ``example``, ``json``, ``headers``, ``echo`` or ``slow``.
    """
    app = web.Application()
    app.router.add_get("/", _local_handler)
    app.router.add_get("/example", _example_handler)
    app.router.add_get("/json", _json_handler)
    app.router.add_get("/headers", _headers_handler)
    app.router.add_post("/echo", _echo_handler)
    app.router.add_get("/slow", _slow_handler)

    server = TestServer(app)
    await server.start_server()
    try:
        yield str(server.make_url("/"))
    finally:
        await server.close()
