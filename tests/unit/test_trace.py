"""Unit tests for trace extraction helpers."""

import io
import json
import zipfile

import pytest

from wavexis.backend._trace import extract_trace_events


class TestExtractTraceEvents:
    """Tests for extract_trace_events."""

    @pytest.mark.unit
    def test_extracts_events_from_valid_zip(self) -> None:
        """Parse traceEvents from a valid Chrome trace ZIP archive."""
        events = [{"name": "test", "ph": "X"}]
        content = json.dumps({"traceEvents": events}).encode("utf-8")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("trace.json", content)

        result = extract_trace_events(buffer.getvalue())
        assert result == events

    @pytest.mark.unit
    def test_invalid_zip_returns_fallback(self) -> None:
        """Return a fallback payload-size entry when the data is not a valid ZIP."""
        raw = b"not a zip"
        result = extract_trace_events(raw)
        assert result == [{"raw_size": len(raw)}]

    @pytest.mark.unit
    def test_bad_json_in_zip_returns_fallback(self) -> None:
        """Return a fallback when an entry inside the ZIP is not valid JSON."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("trace.json", b"not json")

        raw = buffer.getvalue()
        result = extract_trace_events(raw)
        assert result == [{"raw_size": len(raw)}]
