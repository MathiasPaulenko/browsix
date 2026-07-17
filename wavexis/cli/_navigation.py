"""navigation commands for wavexis CLI."""

from __future__ import annotations

__all__ = ["_console"]

import json
from typing import Any

import typer

from wavexis.actions.console import ConsoleAction, ConsoleParams
from wavexis.actions.navigate import (
    BackAction,
    ForwardAction,
    NavigateAction,
    NavigateParams,
    ReloadAction,
    StopAction,
)
from wavexis.actions.tabs import TabsAction, TabsParams
from wavexis.cli._shared import (
    Output,
    _browser_options,
    _close_backend,
    _get_backend,
    _run_async,
    app,
)
from wavexis.config import WaitStrategy


@app.command()
def navigate(
    url: str = typer.Argument(..., help="URL to navigate to"),
    wait_for: str | None = typer.Option(None, "--wait-for", help="CSS selector to wait for"),
) -> None:
    """Navigate to a URL and optionally wait for an element."""
    wait = (
        WaitStrategy(strategy="selector", selector=wait_for)
        if wait_for
        else WaitStrategy(strategy="load")
    )
    _run_async(_navigate(url, wait))
    typer.echo(f"Navigated to {url}")

async def _navigate(url: str, wait: WaitStrategy) -> None:
    """Async helper for navigation."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        action = NavigateAction(NavigateParams(url=url, wait=wait))
        await action.execute(backend)
    finally:
        await _close_backend(backend)

@app.command()
def back() -> None:
    """Navigate back in browser history."""
    _run_async(_nav_simple(lambda b: BackAction(None).execute(b)))
    typer.echo("Navigated back")

@app.command()
def forward() -> None:
    """Navigate forward in browser history."""
    _run_async(_nav_simple(lambda b: ForwardAction(None).execute(b)))
    typer.echo("Navigated forward")

@app.command()
def reload(
    ignore_cache: bool = typer.Option(False, "--ignore-cache", help="Bypass browser cache"),
) -> None:
    """Reload the current page."""
    _run_async(_nav_simple(lambda b: ReloadAction(ignore_cache).execute(b)))
    typer.echo("Page reloaded")

@app.command()
def stop() -> None:
    """Stop all pending navigations and resource loads."""
    _run_async(_nav_simple(lambda b: StopAction(None).execute(b)))
    typer.echo("Stopped loading")

async def _nav_simple(action_fn: Any) -> None:
    """Async helper for simple navigation actions (back, forward, reload, stop)."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await action_fn(backend)
    finally:
        await _close_backend(backend)

@app.command()
def tabs(
    action: str = typer.Argument("list", help="Tab action: list, new, close, activate"),
    url: str = typer.Option("about:blank", "--url", help="URL for new tab"),
    tab_id: str = typer.Option("", "--tab-id", help="Target ID for close/activate"),
) -> None:
    """Manage browser tabs (list, new, close, activate)."""
    result = _run_async(_tabs(action, url, tab_id))
    if result is None:
        return

    if action == "list":
        typer.echo(json.dumps(result, indent=2, default=str))
    elif action == "new":
        typer.echo(f"New tab created: {result}")
    elif action == "close":
        typer.echo(f"Tab closed: {tab_id}")
    elif action == "activate":
        typer.echo(f"Tab activated: {tab_id}")

async def _tabs(action: str, url: str, tab_id: str) -> Any:
    """Async helper for tab operations."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        params = TabsParams(action=action, url=url, tab_id=tab_id)
        return await TabsAction(params).execute(backend)
    finally:
        await _close_backend(backend)


@app.command()
def contexts(
    action: str = typer.Argument(
        "list", help="Context action: list, new, close, user-context"
    ),
    context_id: str = typer.Option("", "--context-id", "-c", help="Context ID for close"),
) -> None:
    """Manage browser contexts and user contexts."""
    result = _run_async(_contexts(action, context_id))
    if result is None:
        return

    if action == "list":
        typer.echo(json.dumps(result, indent=2, default=str))
    elif action == "new":
        typer.echo(f"New context created: {result}")
    elif action == "close":
        typer.echo(f"Context closed: {context_id}")
    elif action == "user-context":
        typer.echo(f"New user context created: {result}")


async def _contexts(action: str, context_id: str) -> Any:
    """Async helper for context operations."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        if action == "list":
            return await backend.list_contexts()
        if action == "new":
            return await backend.new_context()
        if action == "close":
            await backend.close_context(context_id)
            return None
        if action == "user-context":
            return await backend.new_user_context()
        raise ValueError(f"Unknown context action: {action}")
    finally:
        await _close_backend(backend)


@app.command()
def console(
    url: str = typer.Argument(..., help="URL to navigate to"),
    level: str = typer.Option(
        "all", "--level", help="Minimum log level (all, error, warning, info)"
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (JSON)"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, csv, yaml"
    ),
    capture: str = typer.Option(
        "console",
        "--capture",
        help="What to capture: console, logs, or both",
    ),
) -> None:
    """Capture console messages and/or browser logs from a web page."""
    result = _run_async(_console(url, level, capture))
    if result is None:
        return

    Output.write_formatted(result, format, output)
    if output:
        typer.echo(f"Console output saved to {output}")

async def _console(url: str, level: str, capture: str = "console") -> Any:
    """Async helper for console capture."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        params = ConsoleParams(
            url=url,
            level=level,
            wait=WaitStrategy(strategy="load"),
            capture=capture,
        )
        return await ConsoleAction(params).execute(backend)
    finally:
        await _close_backend(backend)

@app.command()
def logs(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (JSON)"
    ),
) -> None:
    """Capture browser log entries from a web page."""
    result = _run_async(_logs(url))
    if result is None:
        return

    if output:
        Output.write_json(result, output)
        typer.echo(f"Logs saved to {output}")
    else:
        typer.echo(json.dumps(result, indent=2, default=str))

async def _logs(url: str) -> Any:
    """Async helper for log capture."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        params = ConsoleParams(
            url=url,
            wait=WaitStrategy(strategy="load"),
            capture="logs",
        )
        return await ConsoleAction(params).execute(backend)
    finally:
        await _close_backend(backend)

