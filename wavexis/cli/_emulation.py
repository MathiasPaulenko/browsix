"""emulation commands for wavexis CLI."""

from __future__ import annotations

import typer

from wavexis.cli._shared import (
    DEVICE_PRESETS,
    Output,
    _browser_options,
    _close_backend,
    _get_backend,
    _run_async,
    app,
)
from wavexis.config import WaitStrategy

emulation_app = typer.Typer(
    help="Emulation commands (device, viewport, geolocation, timezone, dark_mode)"
)
app.add_typer(emulation_app, name="emulation")

@app.command()
def devices() -> None:
    """List available device presets."""
    for name, preset in DEVICE_PRESETS.items():
        typer.echo(
            f"  {name}: {preset['width']}x{preset['height']} "
            f"(scale={preset['device_scale_factor']}, "
            f"mobile={preset['mobile']}, touch={preset['touch']})"
        )

@emulation_app.command("device")
def emulation_device(
    url: str = typer.Argument(..., help="URL to navigate to"),
    device: str = typer.Option(..., "--device", help="Device preset name"),
    output: str = typer.Option("screenshot.png", "--output", "-o", help="Output file path"),
) -> None:
    """Emulate a device and take a screenshot."""
    image_bytes = _run_async(_emulation_device(url, device))
    if image_bytes is None:
        return

    Output.write_bytes(image_bytes, output)
    typer.echo(f"Screenshot saved to {output}")

async def _emulation_device(url: str, device: str) -> bytes:
    """Async helper for device emulation + screenshot."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.navigate(url, WaitStrategy(strategy="load"))
        await backend.emulate_device(device)
        from wavexis.config import ScreenshotParams

        params = ScreenshotParams(url=url, full_page=True)
        return bytes(await backend.screenshot(params))
    finally:
        await _close_backend(backend)

@emulation_app.command("viewport")
def emulation_viewport(
    url: str = typer.Argument(..., help="URL to navigate to"),
    width: int = typer.Option(..., "--width", help="Viewport width in pixels"),
    height: int = typer.Option(..., "--height", help="Viewport height in pixels"),
    output: str = typer.Option("screenshot.png", "--output", "-o", help="Output file path"),
) -> None:
    """Set a custom viewport and take a screenshot."""
    image_bytes = _run_async(_emulation_viewport(url, width, height))
    if image_bytes is None:
        return

    Output.write_bytes(image_bytes, output)
    typer.echo(f"Screenshot saved to {output}")

async def _emulation_viewport(url: str, width: int, height: int) -> bytes:
    """Async helper for viewport emulation + screenshot."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.set_viewport(width, height)
        await backend.navigate(url, WaitStrategy(strategy="load"))
        from wavexis.config import ScreenshotParams

        params = ScreenshotParams(url=url, full_page=True)
        return bytes(await backend.screenshot(params))
    finally:
        await _close_backend(backend)

@emulation_app.command("geolocation")
def emulation_geolocation(
    url: str = typer.Argument(..., help="URL to navigate to"),
    lat: float = typer.Option(..., "--lat", help="Latitude in degrees"),
    lon: float = typer.Option(..., "--lon", help="Longitude in degrees"),
    output: str = typer.Option("screenshot.png", "--output", "-o", help="Output file path"),
) -> None:
    """Override geolocation and take a screenshot."""
    image_bytes = _run_async(_emulation_geolocation(url, lat, lon))
    if image_bytes is None:
        return

    Output.write_bytes(image_bytes, output)
    typer.echo(f"Screenshot saved to {output}")

async def _emulation_geolocation(url: str, lat: float, lon: float) -> bytes:
    """Async helper for geolocation override + screenshot."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.navigate(url, WaitStrategy(strategy="load"))
        await backend.set_geolocation(lat, lon)
        from wavexis.config import ScreenshotParams

        params = ScreenshotParams(url=url, full_page=True)
        return bytes(await backend.screenshot(params))
    finally:
        await _close_backend(backend)

@emulation_app.command("timezone")
def emulation_timezone(
    url: str = typer.Argument(..., help="URL to navigate to"),
    tz: str = typer.Option(..., "--tz", help="IANA timezone ID"),
    output: str = typer.Option("screenshot.png", "--output", "-o", help="Output file path"),
) -> None:
    """Override timezone and take a screenshot."""
    image_bytes = _run_async(_emulation_timezone(url, tz))
    if image_bytes is None:
        return

    Output.write_bytes(image_bytes, output)
    typer.echo(f"Screenshot saved to {output}")

async def _emulation_timezone(url: str, tz: str) -> bytes:
    """Async helper for timezone override + screenshot."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.navigate(url, WaitStrategy(strategy="load"))
        await backend.set_timezone(tz)
        from wavexis.config import ScreenshotParams

        params = ScreenshotParams(url=url, full_page=True)
        return bytes(await backend.screenshot(params))
    finally:
        await _close_backend(backend)

@emulation_app.command("dark_mode")
def emulation_dark_mode(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str = typer.Option("screenshot.png", "--output", "-o", help="Output file path"),
) -> None:
    """Enable dark mode and take a screenshot."""
    image_bytes = _run_async(_emulation_dark_mode(url))
    if image_bytes is None:
        return

    Output.write_bytes(image_bytes, output)
    typer.echo(f"Screenshot saved to {output}")

async def _emulation_dark_mode(url: str) -> bytes:
    """Async helper for dark mode + screenshot."""
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.navigate(url, WaitStrategy(strategy="load"))
        await backend.set_dark_mode(True)
        from wavexis.config import ScreenshotParams

        params = ScreenshotParams(url=url, full_page=True)
        return bytes(await backend.screenshot(params))
    finally:
        await _close_backend(backend)

