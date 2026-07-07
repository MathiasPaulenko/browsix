"""wavexis CLI — thin orchestrator that imports domain modules."""

from wavexis.cli import _advanced  # noqa: F401
from wavexis.cli import _capture  # noqa: F401
from wavexis.cli import _config  # noqa: F401
from wavexis.cli import _debug  # noqa: F401
from wavexis.cli import _emulation  # noqa: F401
from wavexis.cli import _experimental  # noqa: F401
from wavexis.cli import _iframe  # noqa: F401
from wavexis.cli import _input  # noqa: F401
from wavexis.cli import _navigation  # noqa: F401
from wavexis.cli import _network  # noqa: F401
from wavexis.cli import _network_inspect  # noqa: F401
from wavexis.cli import _nl  # noqa: F401
from wavexis.cli import _perf  # noqa: F401
from wavexis.cli import _serve  # noqa: F401
from wavexis.cli import _session  # noqa: F401
from wavexis.cli import _shadow  # noqa: F401
from wavexis.cli import _workflow  # noqa: F401
from wavexis.cli._capture import _check_assertion  # noqa: F401
from wavexis.cli._shared import (  # noqa: F401
    EXIT_BACKEND_ERROR,
    EXIT_BROWSER_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_SUCCESS,
    CLIContext,
    _browser_options,
    _load_global_config,
    _ctx,
    app,
)

__all__ = ["app"]
