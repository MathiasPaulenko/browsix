"""wavexis — browser automation CLI."""

from __future__ import annotations

import warnings
from pathlib import Path

try:
    from importlib.metadata import version as _version

    __version__ = _version("wavexis")
except Exception:  # pragma: no cover - fallback when not installed
    # If the package is run from source without being installed, read the
    # version directly from pyproject.toml so it stays in sync.
    _pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        import tomllib

        _data = tomllib.loads(_pyproject.read_text(encoding="utf-8"))
        __version__ = _data["project"]["version"]
    except Exception:
        warnings.warn(
            "Unable to determine wavexis version from installed metadata "
            "or pyproject.toml",
            stacklevel=2,
        )
        __version__ = "unknown"

__all__ = ["__version__"]
