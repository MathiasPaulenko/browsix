"""LayerTree mixin — layer tree snapshot and compositing operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LayerTreeBackend(ABC):
    """Layer tree operations."""

    @abstractmethod
    async def layer_tree_compositing_reasons(self, layer_id: str) -> dict[str, Any]:
        """Get compositing reasons for a layer."""

    @abstractmethod
    async def layer_tree_disable(self) -> None:
        """Disable the LayerTree domain."""

    @abstractmethod
    async def layer_tree_enable(self) -> None:
        """Enable the LayerTree domain."""

    @abstractmethod
    async def layer_tree_load_snapshot(self, snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        """Load a layer tree snapshot."""

    @abstractmethod
    async def layer_tree_make_snapshot(self, layer_id: str) -> dict[str, Any]:
        """Make a snapshot of a layer."""

    @abstractmethod
    async def layer_tree_profile_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        """Profile a layer snapshot."""

    @abstractmethod
    async def layer_tree_release_snapshot(self, snapshot_id: str) -> None:
        """Release a layer snapshot."""

    @abstractmethod
    async def layer_tree_replay_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        """Replay a layer snapshot."""

    @abstractmethod
    async def layer_tree_snapshot_command_log(self, snapshot_id: str) -> dict[str, Any]:
        """Get the command log for a layer snapshot."""
