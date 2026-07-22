"""CLI entry point for wavexis."""

import sys
import warnings

from wavexis.cli.app import app


def _install_asyncio_cleanup_hooks() -> None:
    """Suppress noisy asyncio/Proactor cleanup artefacts on Windows.

    When the ProactorEventLoop is torn down, unclosed pipe transports can
    emit ``ResourceWarning`` / ``ValueError: I/O operation on closed pipe``
    messages even though the command completed successfully.  These are
    harmless cleanup artifacts from the cdpwave transport layer, not user
    errors, so we swallow them in the CLI entry point.
    """
    # Ignore ResourceWarnings about unclosed transports from asyncio.
    warnings.filterwarnings(
        "ignore",
        category=ResourceWarning,
        message=r"unclosed transport",
    )

    original_hook = sys.unraisablehook

    def _wavexis_unraisablehook(unraisable: sys.UnraisableHookArgs) -> None:
        err_msg = unraisable.err_msg or ""
        exc = unraisable.exc_value
        exc_msg = str(exc) if exc is not None else ""
        is_pipe_noise = "I/O operation on closed pipe" in exc_msg and (
            "Exception ignored while calling deallocator" in err_msg
            or "Exception ignored in:" in err_msg
        )
        if is_pipe_noise:
            return
        original_hook(unraisable)

    sys.unraisablehook = _wavexis_unraisablehook


def main() -> None:
    """Run the wavexis CLI."""
    _install_asyncio_cleanup_hooks()
    # Use a single-word program name so that shell-completion scripts generated
    # by Typer/Click are valid (e.g. `_WAVEXIS_COMPLETE` instead of the broken
    # `_PYTHON _M WAVEXIS_COMPLETE` produced for `python -m wavexis`).
    app(prog_name="wavexis")
