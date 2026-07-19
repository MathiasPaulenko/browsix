"""FileSystem mixin — file system operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class FileSystemBackend(ABC):
    """File system operations."""

    @abstractmethod
    async def file_system_get_directory(self, origin: str, type: str) -> dict[str, Any]:
        """Get a file system directory by origin and type."""
