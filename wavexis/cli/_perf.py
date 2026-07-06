"""perf commands for wavexis CLI."""

from __future__ import annotations

__all__ = ["_perf", "_print_perf_summary"]

from typing import Any

import typer

from wavexis.cli._shared import (
    Output,
    _browser_options,
    _get_backend,
    _run_async,
    _write_json_output,
    app,
)
from wavexis.config import WaitStrategy

perf_app = typer.Typer(help="Performance commands (metrics, trace, profile, heap, coverage)")
app.add_typer(perf_app, name="perf")

@perf_app.command("metrics")
def perf_metrics(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Get performance metrics from a web page."""
    result = _run_async(_perf_action(url, "metrics"))
    if result is None:
        return
    _write_json_output(result, output, "metrics")

@perf_app.command("trace")
def perf_trace(
    url: str = typer.Argument(..., help="URL to navigate to"),
    duration: int = typer.Option(3000, "--duration", help="Trace duration in ms"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Capture a performance trace from a web page."""
    result = _run_async(_perf_action(url, "trace", duration_ms=duration))
    if result is None:
        return
    _write_json_output(result, output, "trace")

@perf_app.command("profile")
def perf_profile(
    url: str = typer.Argument(..., help="URL to navigate to"),
    duration: int = typer.Option(3000, "--duration", help="Profile duration in ms"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Capture a CPU profile from a web page."""
    result = _run_async(_perf_action(url, "profile", duration_ms=duration))
    if result is None:
        return
    _write_json_output(result, output, "profile")

@perf_app.command("heap")
def perf_heap(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Capture a heap snapshot from a web page."""
    result = _run_async(_perf_action(url, "heap"))
    if result is None:
        return
    _write_json_output(result, output, "heap snapshot")

@perf_app.command("coverage")
def perf_coverage(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Get JavaScript code coverage from a web page."""
    result = _run_async(_perf_action(url, "coverage"))
    if result is None:
        return
    _write_json_output(result, output, "JS coverage")

@perf_app.command("css-coverage")
def perf_css_coverage(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
) -> None:
    """Get CSS rule usage coverage from a web page."""
    result = _run_async(_perf_action(url, "css-coverage"))
    if result is None:
        return
    _write_json_output(result, output, "CSS coverage")

async def _perf_action(
    url: str, action: str, duration_ms: int = 3000
) -> dict[str, Any]:
    """Execute a performance action on a web page.

    Args:
        url: URL to navigate to.
        action: Performance action ("metrics", "trace", "profile",
            "heap", "coverage", "css-coverage").
        duration_ms: Duration in milliseconds for trace/profile actions.

    Returns:
        Performance data as a dictionary.
    """
    from wavexis.actions.performance import PerformanceAction, PerformanceParams

    params = PerformanceParams(
        url=url, action=action, duration_ms=duration_ms,
        wait=WaitStrategy(strategy="load"),
    )
    backend = _get_backend()
    act = PerformanceAction(params)
    return await act.execute(backend)

@app.command()
def perf(
    url: str = typer.Argument(..., help="URL to navigate to"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, yaml"
    ),
    metric: str = typer.Option(
        "metrics",
        "--metric",
        "-m",
        help=(
            "Metric to capture: metrics, trace, profile, "
            "heap-snapshot, coverage, css-coverage"
        ),
    ),
    duration: int = typer.Option(
        3000, "--duration", "-d", help="Duration in ms (for trace/profile)"
    ),
) -> None:
    """Capture performance metrics from a web page.

    Supports: metrics (LCP/FCP/CLS/TTFB), trace, profile,
    heap-snapshot, coverage, css-coverage.
    """
    valid_metrics = {
        "metrics", "trace", "profile",
        "heap-snapshot", "coverage", "css-coverage",
    }
    if metric not in valid_metrics:
        typer.echo(
            f"Error: invalid metric '{metric}'. "
            f"Valid: {', '.join(sorted(valid_metrics))}",
            err=True,
        )
        raise typer.Exit(1)

    result = _run_async(_perf(url, metric, duration))
    if result is None:
        return

    if metric == "metrics":
        _print_perf_summary(result)

    Output.write_formatted(result, format, output)
    if output:
        typer.echo(f"Performance data saved to {output}")

def _print_perf_summary(metrics: Any) -> None:
    """Print a human-readable summary of key performance metrics.

    Args:
        metrics: Dict of performance metrics from backend.perf_metrics().
    """
    if not isinstance(metrics, dict):
        return

    key_metrics = [
        ("LargestContentfulPaint", "LCP"),
        ("FirstContentfulPaint", "FCP"),
        ("CumulativeLayoutShift", "CLS"),
        ("TimeToFirstByte", "TTFB"),
        ("DOMContentLoadEventEnd", "DCL"),
        ("LoadEventEnd", "Load"),
    ]

    typer.echo("\nPerformance Summary:")
    typer.echo("-" * 40)
    for raw_key, label in key_metrics:
        value = metrics.get(raw_key)
        if value is not None:
            if isinstance(value, (int, float)):
                if label in ("CLS",):
                    typer.echo(f"  {label:8s} {value:.3f}")
                else:
                    typer.echo(f"  {label:8s} {value:.0f} ms")
            else:
                typer.echo(f"  {label:8s} {value}")
    typer.echo("-" * 40)

async def _perf(url: str, metric: str, duration: int) -> Any:
    """Async helper for performance metrics capture.

    Args:
        url: URL to navigate to.
        metric: Metric type to capture.
        duration: Duration in ms for trace/profile.

    Returns:
        Performance data from the backend.
    """
    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        await backend.navigate(url, WaitStrategy(strategy="load"))

        if metric == "metrics":
            return await backend.perf_metrics()
        if metric == "trace":
            return await backend.perf_trace(duration_ms=duration)
        if metric == "profile":
            return await backend.perf_profile(duration_ms=duration)
        if metric == "heap-snapshot":
            return await backend.perf_heap_snapshot()
        if metric == "coverage":
            return await backend.perf_coverage()
        if metric == "css-coverage":
            return await backend.perf_css_coverage()
        return {}
    finally:
        await backend.close()

