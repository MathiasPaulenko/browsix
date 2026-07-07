"""Type stubs for cdpwave package."""

from typing import Any

class CDPSession:
    """Type stub for CDPSession."""

    page: Any
    dom: Any
    runtime: Any
    network: Any
    emulation: Any
    target: Any
    browser: Any
    fetch: Any
    log: Any
    security: Any
    storage: Any
    debugger: Any
    profiler: Any
    tracing: Any
    input: Any
    css: Any
    overlay: Any
    animation: Any
    web_authn: Any
    media: Any

    target_id: str
    session_id: str

    async def close(self) -> None: ...
    async def send(self, method: str, params: dict[str, Any] | None = ...) -> dict[str, Any]: ...
    async def wait_for_event(self, event: str, timeout: float = ...) -> dict[str, Any]: ...
    def on(self, event: str, handler: Any) -> None: ...
    async def collect_events(
        self, event: str = ..., *, timeout: float = ...
    ) -> list[dict[str, Any]]: ...


class CDPClient:
    """Type stub for CDPClient."""

    browser: Any

    @classmethod
    async def launch(
        cls,
        headless: bool = ...,
        extra_args: list[str] | None = ...,
    ) -> CDPClient: ...

    @classmethod
    async def connect(
        cls,
        host: str = ...,
        port: int = ...,
        ws_url: str | None = ...,
    ) -> CDPClient: ...

    async def new_page(self, url: str = ...) -> CDPSession: ...
    async def connect_to_page(self, target_id: str) -> CDPSession: ...
    async def close(self) -> None: ...
    async def send(self, method: str, params: dict[str, Any] | None = ...) -> dict[str, Any]: ...


__version__: str
