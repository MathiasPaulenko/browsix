"""workflow commands for wavexis CLI."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from typing import Annotated, Any

import typer

from wavexis.actions.eval import EvalAction
from wavexis.actions.pdf import PDFAction
from wavexis.actions.scrape import ScrapeAction
from wavexis.actions.screenshot import ScreenshotAction
from wavexis.cli._shared import (
    EXIT_BROWSER_ERROR,
    EXIT_CONFIG_ERROR,
    Output,
    WavexisError,
    _browser_options,
    _echo,
    _get_backend,
    _get_ctx,
    _handle_error,
    _run_async,
    _write_json_output,
    app,
    get_manager,
)
from wavexis.config import EvalParams, PDFParams, ScrapeParams, ScreenshotParams, WaitStrategy


@app.command()
def multi(
    config: str = typer.Argument(..., help="Path to YAML config file"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate config and show planned actions without launching browser",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        help="Re-execute actions when the config file changes (Ctrl+C to stop)",
    ),
    parallel: bool = typer.Option(
        False,
        "--parallel",
        help="Execute all actions concurrently instead of sequentially",
    ),
) -> None:
    """Execute multiple actions from a YAML config file.

    Use --watch to re-run automatically when the config file changes.
    Use --parallel to execute all actions concurrently on the same backend.
    """
    from pathlib import Path

    config_path = Path(config)

    if dry_run:
        try:
            actions = _parse_and_describe(config_path)
        except WavexisError as e:
            _handle_error(e)
            return
        typer.echo(f"Plan: {len(actions)} action(s)")
        for i, desc in enumerate(actions):
            typer.echo(f"  {i + 1}. {desc}")
        return

    if watch:
        _multi_watch(config_path, parallel=parallel)
        return

    results = _run_async(_multi(config_path, parallel=parallel))
    if results is None:
        return

    typer.echo(f"Completed {len(results)} actions")
    for i, result in enumerate(results):
        if isinstance(result, bytes):
            typer.echo(f"  Action {i + 1}: {len(result)} bytes")
        elif isinstance(result, str):
            typer.echo(f"  Action {i + 1}: {result[:100]}")
        else:
            typer.echo(f"  Action {i + 1}: {type(result).__name__}")

def _multi_watch(config_path: Any, parallel: bool = False) -> None:
    """Watch a config file and re-execute on change.

    Uses polling to detect file modifications (cross-platform compatible).

    Args:
        config_path: Path to the YAML config file to watch.
        parallel: If True, execute actions concurrently.
    """

    last_mtime = config_path.stat().st_mtime
    mode = "parallel" if parallel else "sequential"
    typer.echo(f"Watching {config_path} for changes ({mode}, Ctrl+C to stop)...")

    try:
        while True:
            try:
                results = asyncio.run(_multi(config_path, parallel=parallel))
                typer.echo(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"Completed {len(results)} actions"
                )
            except WavexisError as e:
                _handle_error(e)
                return

            typer.echo("  Waiting for changes...")
            while True:
                time.sleep(1)
                current_mtime = config_path.stat().st_mtime
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    typer.echo("\n  File changed, re-running...")
                    break
    except KeyboardInterrupt:
        typer.echo("\nStopped watching.")

async def _multi(config_path: Any, parallel: bool = False) -> list[Any]:
    """Async helper for multi-action execution.

    Args:
        config_path: Path to the YAML config file.
        parallel: If True, execute actions concurrently.
    """
    from wavexis.actions.multi import MultiAction

    backend = _get_backend()
    try:
        await backend.launch(_browser_options())
        action = MultiAction(config_path, parallel=parallel)
        return await action.execute(backend)
    finally:
        await backend.close()

def _parse_and_describe(config_path: Any) -> list[str]:
    """Parse YAML config and return human-readable action descriptions.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        List of description strings, one per action.
    """
    from wavexis.multi import parse_yaml

    actions = parse_yaml(config_path)
    descriptions: list[str] = []
    for item in actions:
        action_type = next(iter(item))
        params = item[action_type]
        url = params.get("url", "")
        if url:
            descriptions.append(f"{action_type}({url})")
        else:
            descriptions.append(f"{action_type}()")
    return descriptions

@app.command()
def batch(
    urls_file: str = typer.Argument(..., help="Path to file with one URL per line"),
    action: str = typer.Argument(..., help="Action to run: screenshot, pdf, scrape, eval"),
    output_dir: str = typer.Option(
        "output", "--output-dir", "-o", help="Directory for output files"
    ),
    expression: str = typer.Option(
        "document.title",
        "--expression",
        "-e",
        help="JS expression for scrape/eval",
    ),
    parallel: int = typer.Option(
        4, "--parallel", "-p", help="Number of parallel browser instances"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show plan without launching browser"),
) -> None:
    """Run a single action against multiple URLs in parallel."""
    from pathlib import Path

    urls_path = Path(urls_file)
    if not urls_path.exists():
        typer.echo(f"Error: URLs file not found: {urls_path}")
        raise typer.Exit(1)

    urls = [line.strip() for line in urls_path.read_text().splitlines() if line.strip()]
    if not urls:
        typer.echo("Error: No URLs found in file")
        raise typer.Exit(1)

    if dry_run:
        typer.echo(f"Plan: {len(urls)} URL(s) x {action}")
        for u in urls:
            typer.echo(f"  {action}({u})")
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = _run_async(_batch(urls, action, out_dir, expression, parallel))
    if results is None:
        return

    typer.echo(f"Completed {len(results)} / {len(urls)} actions")
    for i, (url, result) in enumerate(zip(urls, results, strict=False)):
        if isinstance(result, Exception):
            typer.echo(f"  {i + 1}. {url}: ERROR — {result}")
        elif isinstance(result, bytes):
            typer.echo(f"  {i + 1}. {url}: {len(result)} bytes")
        elif isinstance(result, str):
            typer.echo(f"  {i + 1}. {url}: {result[:100]}")
        else:
            typer.echo(f"  {i + 1}. {url}: {type(result).__name__}")

async def _batch(
    urls: list[str],
    action: str,
    out_dir: Any,
    expression: str,
    parallel: int,
) -> list[Any]:
    """Run an action against multiple URLs with limited concurrency.

    Args:
        urls: List of URLs to process.
        action: Action type — screenshot, pdf, scrape, or eval.
        out_dir: Output directory for saved files.
        expression: JS expression for scrape/eval.
        parallel: Maximum number of concurrent browser instances.

    Returns:
        List of results (or exceptions) in the same order as urls.
    """
    import asyncio as _asyncio

    semaphore = _asyncio.Semaphore(parallel)

    async def _run_one(url: str) -> Any:
        async with semaphore:
            try:
                return await _batch_single(url, action, out_dir, expression)
            except (WavexisError, OSError) as exc:
                return exc

    tasks = [_run_one(u) for u in urls]
    return await _asyncio.gather(*tasks)

async def _batch_single(
    url: str,
    action: str,
    out_dir: Any,
    expression: str,
) -> Any:
    """Execute a single action for one URL in batch mode.

    Args:
        url: URL to process.
        action: Action type — screenshot, pdf, scrape, or eval.
        out_dir: Output directory for saved files.
        expression: JS expression for scrape/eval.

    Returns:
        Result of the action.

    Raises:
        ValueError: If the action type is unknown.
    """
    from wavexis.config import (
        EvalParams,
        ScreenshotParams,
        WaitStrategy,
    )

    backend = _get_backend()
    try:
        await backend.launch(_browser_options())

        if action == "screenshot":
            sp = ScreenshotParams(url=url, full_page=True, wait=WaitStrategy(strategy="load"))
            result = await ScreenshotAction(sp).execute(backend)
            safe_url = url.replace("://", "_").replace("/", "_")[:80]
            (out_dir / f"{safe_url}.png").write_bytes(result)
            return result

        if action == "pdf":
            pp = PDFParams(url=url, wait=WaitStrategy(strategy="load"))
            result = await PDFAction(pp).execute(backend)
            safe_url = url.replace("://", "_").replace("/", "_")[:80]
            (out_dir / f"{safe_url}.pdf").write_bytes(result)
            return result

        if action == "scrape":
            scp = ScrapeParams(
                urls=[url],
                expression=expression,
                wait=WaitStrategy(strategy="load"),
            )
            return await ScrapeAction(scp).execute(backend)

        if action == "eval":
            ep = EvalParams(url=url, expression=expression, wait=WaitStrategy(strategy="load"))
            return await EvalAction(ep).execute(backend)

        raise ValueError(f"Unknown batch action: {action}")
    finally:
        await backend.close()

@app.command()
def backends() -> None:
    """List available backends."""
    manager = get_manager()
    available = manager.list_available()
    if not available:
        typer.echo("No backends available. Install cdpwave or bidiwave.")
        return
    for name in available:
        typer.echo(f"  {name}")

@app.command()
def install_check() -> None:
    """Check which backends are installed and their versions."""
    manager = get_manager()
    status = manager.install_check()
    for name, version in status.items():
        typer.echo(f"  {name}: {version}")

@app.command()
def a11y(
    url: str = typer.Argument(..., help="URL to navigate to"),
    action: str = typer.Option("tree", "--action", "-a", help="A11y action: tree, node, ancestors"),
    node_id: str = typer.Option("", "--node-id", help="Node ID for node/ancestors actions"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Get accessibility tree, node, or ancestors from a web page."""
    result = _run_async(_a11y(url, action, node_id))
    if result is None:
        return

    if output:
        Output.write_json(result, output)
        typer.echo(f"A11y data saved to {output}")
    else:
        typer.echo(json.dumps(result, indent=2, default=str))

async def _a11y(url: str, action: str, node_id: str) -> Any:
    """Execute an accessibility action on a web page.

    Args:
        url: URL to navigate to.
        action: Accessibility action ("tree", "node", or "ancestors").
        node_id: Node ID for node-specific actions.

    Returns:
        Accessibility tree or node data.
    """
    from wavexis.actions.accessibility import AccessibilityAction

    backend = _get_backend()
    act = AccessibilityAction(
        params=None,
        action=action,
        node_id=node_id,
        url=url,
        wait=WaitStrategy(strategy="load"),
    )
    return await act.execute(backend)

@app.command()
def download(
    url: str = typer.Argument(..., help="URL to navigate to (must trigger a download)"),
    pattern: str = typer.Option(".*", "--pattern", help="URL pattern to match downloads"),
    output: str = typer.Option("download.bin", "--output", "-o", help="Output file path"),
) -> None:
    """Intercept a file download from a web page."""
    data = _run_async(_download(url, pattern))
    if data is None:
        return

    Output.write_bytes(data, output)
    typer.echo(f"Download saved to {output} ({len(data)} bytes)")

async def _download(url: str, pattern: str) -> bytes:
    """Intercept a file download from a web page.

    Args:
        url: URL to navigate to that triggers a download.
        pattern: URL pattern to match download requests.

    Returns:
        Downloaded file bytes.
    """
    from wavexis.actions.download import DownloadAction

    backend = _get_backend()
    act = DownloadAction(
        params=pattern,
        url=url,
        wait=WaitStrategy(strategy="load"),
    )
    return await act.execute(backend)

@app.command()
def dialog(
    url: str = typer.Argument(..., help="URL to navigate to"),
    action: str = typer.Option("accept", "--action", "-a", help="Dialog action: accept, dismiss"),
    prompt_text: str = typer.Option("", "--text", help="Text for prompt dialogs"),
) -> None:
    """Accept or dismiss a JavaScript dialog on a web page."""
    _run_async(_dialog(url, action, prompt_text or None))
    typer.echo(f"Dialog {action}ed on {url}")

async def _dialog(url: str, action: str, prompt_text: str | None) -> None:
    """Accept or dismiss a JavaScript dialog on a web page.

    Args:
        url: URL to navigate to.
        action: Dialog action ("accept" or "dismiss").
        prompt_text: Text to enter in prompt dialogs, if applicable.
    """
    from wavexis.actions.dialog import DialogAction

    backend = _get_backend()
    act = DialogAction(
        params="",
        action=action,
        prompt_text=prompt_text,
        url=url,
        wait=WaitStrategy(strategy="load"),
    )
    await act.execute(backend)

@app.command()
def permissions(
    action: str = typer.Argument("grant", help="Permissions action: grant, reset"),
    permission: str = typer.Option(
        "geolocation", "--permission",
        help="Permission name (e.g. geolocation, notifications)",
    ),
    url: str = typer.Option("", "--url", help="URL to navigate to (optional)"),
) -> None:
    """Grant or reset browser permissions."""
    _run_async(_permissions(action, permission, url))
    typer.echo(f"Permissions {action} for '{permission}'")

async def _permissions(action: str, permission: str, url: str) -> None:
    """Grant or reset browser permissions.

    Args:
        action: Permission action ("grant", "deny", "reset", or "query").
        permission: Permission name (e.g. "geolocation").
        url: URL to navigate to (optional).
    """
    from wavexis.actions.permissions import PermissionsAction

    backend = _get_backend()
    act = PermissionsAction(
        params="",
        action=action,
        permission=permission,
        url=url,
        wait=WaitStrategy(strategy="load") if url else None,
    )
    await act.execute(backend)

@app.command()
def security(
    url: str = typer.Argument(..., help="URL to navigate to"),
    action: str = typer.Option(
        "state", "--action", "-a", help="Security action: state, ignore_cert"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
) -> None:
    """Get security state or ignore certificate errors."""
    result = _run_async(_security(url, action))
    if result is None:
        return

    if action == "state":
        if output:
            Output.write_json(result, output)
            typer.echo(f"Security state saved to {output}")
        else:
            typer.echo(json.dumps(result, indent=2, default=str))
    else:
        typer.echo(f"Certificate errors ignored on {url}")

async def _security(url: str, action: str) -> Any:
    """Execute a security action on a web page.

    Args:
        url: URL to navigate to.
        action: Security action ("state" or "ignore-cert-errors").

    Returns:
        Security state data if action is "state".
    """
    from wavexis.actions.security import SecurityAction

    backend = _get_backend()
    act = SecurityAction(
        params="",
        action=action,
        url=url,
        wait=WaitStrategy(strategy="load"),
    )
    return await act.execute(backend)

@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to listen on"),
    host: str = typer.Option("localhost", "--host", help="Host to bind to"),
    backend: str = typer.Option(
        None, "--backend", help="Preferred backend (cdp or bidi)"
    ),
) -> None:
    """Start the wavexis HTTP server."""
    from wavexis.serve import serve as _serve

    try:
        _serve(port=port, host=host, backend=backend or _get_ctx().preferred_backend)
    except WavexisError as e:
        _handle_error(e)

@app.command()
def plugins() -> None:
    """List discovered plugins (actions, backends, middleware)."""
    from wavexis.plugins import get_registry

    registry = get_registry()
    actions = registry.list_actions()
    backends = registry.list_backends()
    middleware = registry.list_middleware()

    if not actions and not backends and not middleware:
        typer.echo("No plugins discovered.")
        typer.echo(
            "\nInstall a plugin package with entry point group "
            "'wavexis.plugins' to extend wavexis."
        )
        return

    if actions:
        typer.echo("Actions:")
        for name in actions:
            plugin = registry.get_action(name)
            desc = plugin.description if plugin else ""
            typer.echo(f"  {name}: {desc}" if desc else f"  {name}")

    if backends:
        typer.echo("Backends:")
        for name in backends:
            typer.echo(f"  {name}")

    if middleware:
        typer.echo("Middleware:")
        for name in middleware:
            typer.echo(f"  {name}")

@app.command()
def completions(
    shell: str = typer.Argument(..., help="Shell: bash, zsh, fish, powershell"),
) -> None:
    """Install shell completions for wavexis."""
    import subprocess

    shells = {"bash", "zsh", "fish", "powershell"}
    if shell not in shells:
        Output.error(f"Unsupported shell: {shell}. Choose from: {', '.join(sorted(shells))}")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    try:
        subprocess.run(
            [sys.executable, "-m", "wavexis", "completion", shell],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        Output.error(f"Failed to install completions: {e}")
        raise typer.Exit(EXIT_BROWSER_ERROR) from e

    Output.success(f"Completions installed for {shell}")

@app.command()
def record(
    url: str = typer.Argument(..., help="URL to record"),
    output: str = typer.Option("session.yml", "-o", "--output", help="Output YAML file"),
    actions: str = typer.Option(
        "screenshot,eval",
        "--actions",
        help="Comma-separated action types to record "
             "(screenshot,eval,navigate,click,type,scrape,pdf,dom)",
    ),
    selector: str = typer.Option(
        "#button", "--selector", help="CSS selector for click/type actions",
    ),
    text: str = typer.Option("hello", "--text", help="Text for type action"),
    expression: str = typer.Option(
        "document.title", "--expression", help="JS expression for eval action",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help=(
            "Launch non-headless browser and capture real interactions "
            "(clicks, inputs, navigations)"
        ),
    ),
    duration: int = typer.Option(
        60, "--duration", "-d", help="Recording duration in seconds (interactive mode)"
    ),
) -> None:
    """Record a browsing session to YAML for later replay.

    Use --interactive to launch a real browser and capture your interactions.
    Without --interactive, generates a YAML from specified action types.
    """
    from pathlib import Path

    if interactive:
        from wavexis.actions.record import record_session

        backend = _get_backend()
        yaml_content = _run_async(record_session(backend, url, duration))
        if yaml_content is None:
            return

        out_path = Path(output)
        out_path.write_text(yaml_content, encoding="utf-8")
        _echo(f"Recorded config saved to {output}")
        _echo(f"Run with: wavexis multi {output}")
        return

    from wavexis.record import record_to_yaml

    action_types = [a.strip() for a in actions.split(",") if a.strip()]
    action_list: list[dict[str, Any]] = []
    for at in action_types:
        if at == "screenshot":
            action_list.append({"screenshot": {"url": url, "output": "screenshot.png"}})
        elif at == "eval":
            action_list.append({"eval": {"url": url, "expression": expression}})
        elif at == "navigate":
            action_list.append({"navigate": {"url": url}})
        elif at == "click":
            action_list.append({"dom": {"url": url, "action": "get", "selector": selector}})
        elif at == "type":
            action_list.append({
                "eval": {
                    "url": url,
                    "expression": f"document.querySelector('{selector}').value='{text}'",
                },
            })
        elif at == "scrape":
            action_list.append({
                "scrape": {"url": url, "expression": expression},
            })
        elif at == "pdf":
            action_list.append({"pdf": {"url": url, "paper": "a4"}})
        elif at == "dom":
            action_list.append({"dom": {"url": url, "action": "get", "selector": "body"}})
        else:
            typer.echo(f"Unknown action type: {at}", err=True)
            raise typer.Exit(2)

    if not action_list:
        typer.echo("No actions to record", err=True)
        raise typer.Exit(2)

    record_to_yaml(action_list, Path(output))
    _echo(f"Recorded {len(action_list)} actions to {output}")

@app.command()
def replay(
    config: str = typer.Argument(..., help="Path to YAML config file"),
) -> None:
    """Replay a recorded session from YAML."""
    from pathlib import Path

    from wavexis.record import replay_from_yaml

    config_path = Path(config)
    backend = _get_backend()

    async def _replay() -> list[Any]:
        await backend.launch(_browser_options())
        try:
            return await replay_from_yaml(config_path, backend)
        finally:
            await backend.close()

    results = _run_async(_replay())
    if results is None:
        return

    _echo(f"Replayed {len(results)} actions")
    for i, result in enumerate(results):
        if isinstance(result, bytes):
            _echo(f"  Action {i + 1}: {len(result)} bytes")
        elif isinstance(result, str):
            _echo(f"  Action {i + 1}: {result[:100]}")
        else:
            _echo(f"  Action {i + 1}: {type(result).__name__}")

@app.command()
def auth(
    context: str = typer.Argument(..., help="Path to auth context JSON file"),
    url: str = typer.Argument(..., help="URL to navigate to with auth context"),
    output: str = typer.Option("-", "-o", "--output", help="Output file (- for stdout)"),
    screenshot: bool = typer.Option(
        False, "--screenshot", help="Take screenshot after applying auth",
    ),
) -> None:
    """Apply auth context (cookies, headers, basic auth) and navigate to a URL."""
    from wavexis.auth import apply_auth_context, load_auth_context

    ctx = load_auth_context(context)

    async def _run_auth() -> Any:
        """Execute an authenticated browser session.

        Returns:
            Result of the authenticated action.
        """
        backend = _get_backend()
        await backend.launch(_browser_options())
        try:
            await apply_auth_context(backend, ctx, url)
            if screenshot:
                return await backend.screenshot(
                    ScreenshotParams(
                        url=url, wait=WaitStrategy(strategy="load"),
                    ),
                )
            return await backend.eval(
                EvalParams(
                    url=url,
                    expression="document.title",
                    wait=WaitStrategy(strategy="load"),
                ),
            )
        finally:
            await backend.close()

    result = _run_async(_run_auth())
    if result is None:
        return

    if isinstance(result, bytes):
        out = output or "auth_result.png"
        with open(out, "wb") as f:
            f.write(result)
        _echo(f"Screenshot saved to {out}")
    elif isinstance(result, str):
        typer.echo(result)
    else:
        _write_json_output(result, output, "auth result")

@app.command()
def repl(
    url: str = typer.Argument(
        "", help="Optional URL to navigate to before starting the REPL"
    ),
) -> None:
    """Start an interactive REPL session with a live browser.

    Launches a non-headless browser and provides a command prompt
    to execute actions interactively. Type 'help' for available commands.
    """
    from wavexis.repl import repl_loop

    backend = _get_backend()
    _run_async(repl_loop(backend, url or None))

@app.command()
def config(
    action: str = typer.Argument(
        "show", help="Config action: show, set, init, path"
    ),
    key: str = typer.Option(
        "", "--key", help="Config key to set (backend, headless, timeout, proxy)"
    ),
    value: str = typer.Option(
        "", "--value", help="Value to set for the given key"
    ),
) -> None:
    """Manage global wavexis configuration at ~/.wavexis/config.yml.

    \b
    Show current config:
        wavexis config show

    \b
    Set a default:
        wavexis config set --key backend --value cdp
        wavexis config set --key headless --value false
        wavexis config set --key timeout --value 60000
        wavexis config set --key proxy --value http://proxy:8080

    \b
    Create initial config file:
        wavexis config init

    \b
    Show config file path:
        wavexis config path
    """
    from pathlib import Path

    import yaml

    config_dir = Path.home() / ".wavexis"
    config_path = config_dir / "config.yml"

    if action == "path":
        typer.echo(str(config_path))
        return

    if action == "init":
        config_dir.mkdir(parents=True, exist_ok=True)
        if config_path.exists():
            typer.echo(f"Config already exists at {config_path}")
            return
        defaults: dict[str, Any] = {
            "backend": "cdp",
            "headless": True,
            "timeout": 30000,
        }
        config_path.write_text(
            yaml.dump(defaults, default_flow_style=False, sort_keys=True),
            encoding="utf-8",
        )
        typer.echo(f"Created config at {config_path}")
        return

    if action == "show":
        if not config_path.exists():
            typer.echo("No config file found. Run: wavexis config init")
            return
        typer.echo(config_path.read_text(encoding="utf-8"))
        return

    if action == "set":
        if not key:
            typer.echo("Error: --key is required for 'set'")
            raise typer.Exit(EXIT_CONFIG_ERROR)
        if not value:
            typer.echo("Error: --value is required for 'set'")
            raise typer.Exit(EXIT_CONFIG_ERROR)

        config_dir.mkdir(parents=True, exist_ok=True)
        current: dict[str, Any] = {}
        if config_path.exists():
            loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                current = loaded

        if key in ("headless",):
            current[key] = value.lower() in ("true", "1", "yes")
        elif key in ("timeout",):
            current[key] = int(value)
        else:
            current[key] = value

        config_path.write_text(
            yaml.dump(current, default_flow_style=False, sort_keys=True),
            encoding="utf-8",
        )
        typer.echo(f"Set {key} = {current[key]} in {config_path}")
        return

    typer.echo(f"Unknown action: {action}. Use: show, set, init, path")

@app.command()
def init(
    template: str = typer.Option(
        "",
        "--template",
        "-t",
        help="Template name (screenshot, pdf, scrape, eval, multi-step, cookies, har)",
    ),
    url: str = typer.Option(
        "", "--url", "-u", help="URL to use in the generated config"
    ),
    expression: str = typer.Option(
        "", "--expression", "-e", help="JS expression for scrape/eval templates"
    ),
    selector: str = typer.Option(
        "", "--selector", "-s", help="CSS selector for multi-step template"
    ),
    text: str = typer.Option(
        "", "--text", help="Text for type action in multi-step template"
    ),
    output: str = typer.Option(
        "wavexis.yaml", "--output", "-o", help="Output YAML file path"
    ),
    list_templates: bool = typer.Option(
        False, "--list", help="List available templates and exit"
    ),
) -> None:
    """Generate a wavexis.yaml config from a template.

    Run without --template for an interactive wizard.
    Use --list to see available templates.
    """
    from pathlib import Path

    from wavexis.init import generate_config
    from wavexis.init import list_templates as do_list

    if list_templates:
        for name, desc in do_list():
            typer.echo(f"  {name} — {desc}")
        return

    if template:
        try:
            yaml_content = generate_config(
                template=template,
                url=url or None,
                expression=expression or None,
                selector=selector or None,
                text=text or None,
            )
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1) from e
    else:
        from wavexis.init import interactive_init

        try:
            yaml_content = interactive_init()
        except (ValueError, EOFError, KeyboardInterrupt) as e:
            typer.echo(f"\nCancelled: {e}", err=True)
            raise typer.Exit(1) from e

    out_path = Path(output)
    out_path.write_text(yaml_content, encoding="utf-8")
    typer.echo(f"Config saved to {output}")
    typer.echo(f"Run with: wavexis multi {output}")

@app.command()
def session(
    action: str = typer.Argument(
        ..., help="Session action: save, load"
    ),
    url: str = typer.Argument(
        "", help="URL to navigate to (for save) or load before navigating (for load)"
    ),
    output: str = typer.Option(
        "session.json", "--output", "-o", help="Session file path"
    ),
) -> None:
    """Save or load browser session state (cookies + localStorage + sessionStorage).

    \b
    Save:  wavexis session save https://app.com -o mysession.json
    Load:  wavexis session load mysession.json https://app.com
    """
    from pathlib import Path

    from wavexis.actions.session import SessionLoadAction, SessionSaveAction

    session_path = Path(output)

    if action == "save":
        if not url:
            typer.echo("Error: URL required for session save", err=True)
            raise typer.Exit(1)

        async def _save_session() -> Any:
            backend = _get_backend()
            await backend.launch(_browser_options())
            try:
                await backend.navigate(url, WaitStrategy(strategy="load"))
                save_action = SessionSaveAction(session_path)
                return await save_action.execute(backend)
            finally:
                await backend.close()

        _run_async(_save_session())
        typer.echo(f"Session saved to {output}")

    elif action == "load":
        if not session_path.exists():
            typer.echo(f"Error: session file not found: {output}", err=True)
            raise typer.Exit(1)

        async def _load_session() -> Any:
            backend = _get_backend()
            await backend.launch(_browser_options())
            try:
                load_action = SessionLoadAction(session_path)
                await load_action.execute(backend)
                if url:
                    await backend.navigate(url, WaitStrategy(strategy="load"))
                    title = await backend.eval("document.title", await_promise=False)
                    return title
                return "Session loaded"
            finally:
                await backend.close()

        result = _run_async(_load_session())
        if result is None:
            return
        typer.echo(f"Session loaded from {output}: {result}")

    else:
        typer.echo(f"Error: unknown session action '{action}'. Use save or load.", err=True)
        raise typer.Exit(1)

@app.command()
def extract(
    url: str = typer.Argument(..., help="URL to extract data from"),
    schema: str = typer.Option(
        ..., "--schema", "-s",
        help=(
            'JSON schema mapping field names to CSS selectors, '
            'e.g. \'{"title":"h1","price":".price"}\''
        )
    ),
    selector: str = typer.Option(
        "", "--selector", help="CSS selector to scope extraction (repeats per match)"
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (.json)"
    ),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json)"),
) -> None:
    """Extract structured data from a web page using a CSS selector schema.

    \b
    Examples:
        wavexis extract https://shop.com -s '{"title":"h1","price":".price"}'
        wavexis extract https://shop.com/products \
            -s '{"name":".name","price":".price"}' --selector ".product"
    """
    from wavexis.actions.extract import ExtractAction, ExtractParams

    try:
        schema_dict = json.loads(schema)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: invalid JSON schema: {e}", err=True)
        raise typer.Exit(1) from e

    async def _extract() -> list[dict[str, Any]]:
        backend = _get_backend()
        params = ExtractParams(
            url=url,
            schema=schema_dict,
            selector=selector or None,
            wait=WaitStrategy(strategy="load"),
        )
        action = ExtractAction(params)
        return await action.execute(backend)

    results = _run_async(_extract())
    if results is None:
        return

    Output.write_formatted(results, format, output)
    if output:
        typer.echo(f"Extracted {len(results)} record(s), saved to {output}")
    else:
        typer.echo(f"Extracted {len(results)} record(s)")

@app.command()
def form(
    url: str = typer.Argument(..., help="URL to navigate to"),
    data: str = typer.Option(
        ..., "--data", "-d",
        help=(
            'JSON mapping CSS selectors to values, '
            'e.g. \'{"#name":"Mathias","#email":"test@test.com"}\''
        )
    ),
    submit: str = typer.Option(
        "", "--submit", help="CSS selector for submit button to click after filling"
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (.json)"
    ),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json)"),
) -> None:
    """Auto-fill form fields from JSON data and optionally submit.

    \b
    Examples:
        wavexis form https://app.com/register -d '{"#name":"Mathias","#email":"test@test.com"}'
        wavexis form https://app.com/register -d '{"#name":"Mathias"}' --submit "#submit-btn"
    """
    from wavexis.actions.form import FormAction, FormParams

    try:
        fields = json.loads(data)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: invalid JSON data: {e}", err=True)
        raise typer.Exit(1) from e

    async def _form() -> dict[str, Any]:
        backend = _get_backend()
        params = FormParams(
            url=url,
            fields=fields,
            submit=submit or None,
            wait=WaitStrategy(strategy="load"),
        )
        action = FormAction(params)
        return await action.execute(backend)

    result = _run_async(_form())
    if result is None:
        return

    Output.write_formatted(result, format, output)
    typer.echo(
        f"Filled {result['fields_filled']}/{result['fields_total']} fields"
        + (", submitted" if result["submitted"] else "")
    )

@app.command()
def ws(
    url: str = typer.Argument(..., help="URL to navigate to"),
    duration: int = typer.Option(
        5000, "--duration", help="How long to capture WS frames (ms)"
    ),
    pattern: str = typer.Option(
        "", "--pattern", help="Regex pattern to filter WS URLs (empty = all)"
    ),
    mock: str = typer.Option(
        "", "--mock",
        help='JSON mapping request payloads to mock response payloads'
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (.json)"
    ),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json)"),
) -> None:
    """Intercept WebSocket frames on a page. Capture sent/received or mock responses.

    \b
    Examples:
        wavexis ws https://app.com --duration 10000
        wavexis ws https://app.com --pattern '.*api.*' -o frames.json
        wavexis ws https://app.com --mock '{"ping":"pong"}' --duration 5000
    """
    from wavexis.actions.websocket import WebSocketInterceptAction, WebSocketParams

    mock_dict: dict[str, str] = {}
    if mock:
        try:
            mock_dict = json.loads(mock)
        except json.JSONDecodeError as e:
            typer.echo(f"Error: invalid JSON mock: {e}", err=True)
            raise typer.Exit(1) from e

    async def _ws() -> dict[str, Any]:
        backend = _get_backend()
        params = WebSocketParams(
            url=url,
            url_pattern=pattern,
            duration_ms=duration,
            mock_responses=mock_dict,
            wait=WaitStrategy(strategy="load"),
        )
        action = WebSocketInterceptAction(params)
        return await action.execute(backend)

    result = _run_async(_ws())
    if result is None:
        return

    Output.write_formatted(result, format, output)
    sent = len(result.get("sent", []))
    received = len(result.get("received", []))
    typer.echo(f"WS intercept: {sent} sent, {received} received frames")

@app.command()
def lighthouse(
    url: str = typer.Argument(..., help="URL to audit"),
    categories: Annotated[
        list[str] | None,
        typer.Option(
            "--category", "-c",
            help=(
                "Audit category: performance, accessibility, seo, "
                "best-practices (repeatable, empty=all)"
            ),
        ),
    ] = None,
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (.json)"
    ),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json)"),
) -> None:
    """Run a Lighthouse-style audit (performance, accessibility, SEO, best practices).

    \b
    Examples:
        wavexis lighthouse https://example.com
        wavexis lighthouse https://example.com -c performance -c seo -o report.json
    """
    from wavexis.actions.lighthouse import LighthouseAction, LighthouseParams

    cats = categories or []

    async def _lighthouse() -> dict[str, Any]:
        backend = _get_backend()
        params = LighthouseParams(
            url=url,
            categories=cats,
            wait=WaitStrategy(strategy="load"),
        )
        action = LighthouseAction(params)
        return await action.execute(backend)

    result = _run_async(_lighthouse())
    if result is None:
        return

    Output.write_formatted(result, format, output)
    scores = {
        cat: data.get("score", 0)
        for cat, data in result.get("categories", {}).items()
    }
    score_str = ", ".join(f"{k}: {v}" for k, v in scores.items())
    if output:
        typer.echo(f"Audit complete ({score_str}), saved to {output}")
    else:
        typer.echo(f"Audit complete ({score_str})")

