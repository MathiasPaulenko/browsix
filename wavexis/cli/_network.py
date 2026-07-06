"""network commands for wavexis CLI."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from wavexis.actions.browser import BrowserAction
from wavexis.cli._shared import (
    Output,
    _browser_options,
    _get_backend,
    _run_async,
    app,
)
from wavexis.config import CookieParams, ThrottleParams, WaitStrategy

network_app = typer.Typer(help="Network commands (block, throttle, cache, intercept, mock)")
app.add_typer(network_app, name="network")

@app.command()
def cookies(
    action: str = typer.Argument(
        "get", help="Cookie action: get, set, delete, clear"
    ),
    url: str = typer.Option("", "--url", help="URL for cookie context"),
    name: str = typer.Option("", "--name", help="Cookie name"),
    value: str = typer.Option("", "--value", help="Cookie value"),
    domain: str = typer.Option("", "--domain", help="Cookie domain"),
    path: str = typer.Option("/", "--path", help="Cookie path"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (JSON)"
    ),
) -> None:
    """Manage browser cookies (get, set, delete, clear)."""
    result = _run_async(
        _cookies(action, url, name, value, domain, path)
    )
    if result is None:
        return

    if action == "get":
        if output:
            Output.write_json(result, output)
            typer.echo(f"Cookies saved to {output}")
        else:
            typer.echo(json.dumps(result, indent=2, default=str))
    else:
        typer.echo(f"Cookies {action} done")

async def _cookies(
    action: str,
    url: str,
    name: str,
    value: str,
    domain: str,
    path: str,
) -> Any:
    """Async helper for cookie operations."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        if url:
            await backend.navigate(url, WaitStrategy(strategy="load"))

        if action == "get":
            return await backend.get_cookies()
        if action == "set":
            cookie = CookieParams(
                name=name, value=value, domain=domain, path=path
            )
            await backend.set_cookie(cookie)
        elif action == "delete":
            await backend.delete_cookie(name, domain)
        elif action == "clear":
            await backend.clear_cookies()
        return None
    finally:
        await backend.close()

@app.command()
def headers(
    headers_json: str = typer.Argument(
        ..., help='JSON dict of headers, or @path to read from file'
    ),
) -> None:
    """Set extra HTTP headers for all requests."""
    if headers_json.startswith("@"):
        from pathlib import Path
        data = json.loads(Path(headers_json[1:]).read_text(encoding="utf-8"))
    else:
        data = json.loads(headers_json)

    _run_async(_headers(data))
    typer.echo("Headers set")

async def _headers(headers: dict[str, str]) -> None:
    """Async helper for setting headers."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.set_headers(headers)
    finally:
        await backend.close()

@app.command()
def user_agent(
    ua: str = typer.Argument(..., help="User-Agent string to set"),
) -> None:
    """Override the browser's User-Agent string."""
    _run_async(_user_agent(ua))
    typer.echo("User-Agent set")

async def _user_agent(ua: str) -> None:
    """Async helper for setting user agent."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.set_user_agent(ua)
    finally:
        await backend.close()

@app.command()
def browser(
    action: str = typer.Argument(
        "version", help="Browser action: version, new_context, list_contexts"
    ),
) -> None:
    """Browser management commands (version, contexts)."""
    result = _run_async(_browser(action))
    if result is None:
        return

    if isinstance(result, str):
        typer.echo(result)
    elif isinstance(result, list):
        typer.echo(json.dumps(result, indent=2, default=str))
    else:
        typer.echo("Done")

async def _browser(action: str) -> Any:
    """Async helper for browser management."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        return await BrowserAction(action).execute(backend)
    finally:
        await backend.close()

@network_app.command("block")
def network_block(
    patterns: Annotated[list[str], typer.Argument(help="URL patterns to block (glob-style)")],
) -> None:
    """Block requests matching URL patterns."""
    _run_async(_network_block(patterns))
    typer.echo(f"Blocked {len(patterns)} URL pattern(s)")

async def _network_block(patterns: list[str]) -> None:
    """Block network requests matching the given patterns.

    Args:
        patterns: List of URL patterns to block.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.block_requests(patterns)
    finally:
        await backend.close()

@network_app.command("throttle")
def network_throttle(
    offline: bool = typer.Option(False, "--offline", help="Emulate offline state"),
    latency: int = typer.Option(0, "--latency", help="Latency in milliseconds"),
    download: int = typer.Option(-1, "--download", help="Download bps (-1=unlimited)"),
    upload: int = typer.Option(-1, "--upload", help="Upload bps (-1=unlimited)"),
) -> None:
    """Throttle network conditions."""
    params = ThrottleParams(
        offline=offline, latency_ms=latency, download_bps=download, upload_bps=upload
    )
    _run_async(_network_throttle(params))
    typer.echo("Network throttling set")

async def _network_throttle(params: ThrottleParams) -> None:
    """Apply network throttling conditions.

    Args:
        params: Throttle parameters with offline, latency, and bandwidth settings.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.throttle_network(params)
    finally:
        await backend.close()

@network_app.command("cache")
def network_cache(
    disabled: bool = typer.Option(True, "--disabled/--enabled", help="Disable or enable cache"),
) -> None:
    """Disable or enable the browser cache."""
    _run_async(_network_cache(disabled))
    typer.echo(f"Cache {'disabled' if disabled else 'enabled'}")

async def _network_cache(disabled: bool) -> None:
    """Enable or disable the browser cache.

    Args:
        disabled: True to disable cache, False to enable.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.set_cache_disabled(disabled)
    finally:
        await backend.close()

@network_app.command("intercept")
def network_intercept(
    url_pattern: str = typer.Argument(..., help="URL pattern to intercept"),
    resource_type: str = typer.Option("", "--resource-type", help="Resource type filter"),
) -> None:
    """Intercept requests matching a URL pattern."""
    pattern: dict[str, Any] = {"urlPattern": url_pattern}
    if resource_type:
        pattern["resourceType"] = resource_type
    _run_async(_network_intercept(pattern))
    typer.echo(f"Intercepting requests matching '{url_pattern}'")

async def _network_intercept(pattern: dict[str, Any]) -> None:
    """Intercept network requests matching a pattern.

    Args:
        pattern: Fetch.enable pattern dict with urlPattern and optional resourceType.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.intercept_requests(pattern)
    finally:
        await backend.close()

@network_app.command("mock")
def network_mock(
    url: str = typer.Argument(..., help="URL pattern to mock"),
    body: str = typer.Argument(..., help="Response body (or JSON string)"),
    status: int = typer.Option(200, "--status", help="HTTP status code"),
    content_type: str = typer.Option(
        "application/json", "--content-type", help="Content-Type header"
    ),
) -> None:
    """Mock a response for requests matching a URL pattern."""
    response: dict[str, Any] = {"status": status, "body": body, "content_type": content_type}
    _run_async(_network_mock(url, response))
    typer.echo(f"Mocking responses for '{url}'")

async def _network_mock(url: str, response: dict[str, Any]) -> None:
    """Mock a response for requests matching a URL pattern.

    Args:
        url: URL pattern to mock.
        response: Response dict with status, body, and content_type.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.mock_response(url, response)
    finally:
        await backend.close()

