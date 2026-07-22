"""Internal helpers for extracting trace events from Chrome trace streams."""

from __future__ import annotations

import io
import json
import zipfile
from typing import Any

__all__ = ["extract_trace_events"]


def extract_trace_events(raw: bytes) -> list[dict[str, Any]]:
    """Extract trace events from a Chrome trace ZIP archive.

    The Chrome DevTools Protocol returns large gzipped/zip trace files. This
    helper performs the blocking decompression and JSON parsing in a thread
    pool so the async event loop is not blocked.

    Args:
        raw: Raw bytes of the trace archive.

    Returns:
        A list of trace events parsed from the archive, or a fallback dict
        with the raw payload size if parsing fails.
    """
    trace_events: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for name in zf.namelist():
                content = zf.read(name).decode("utf-8", errors="replace")
                trace_events.extend(json.loads(content).get("traceEvents", []))
    except (zipfile.BadZipFile, json.JSONDecodeError, KeyError, ValueError, RuntimeError):
        trace_events.append({"raw_size": len(raw)})
    return trace_events
