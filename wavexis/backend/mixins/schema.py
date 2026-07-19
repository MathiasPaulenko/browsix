"""Schema mixin — domain schema introspection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SchemaBackend(ABC):
    """Schema domain for listing available CDP domains."""

    @abstractmethod
    async def schema_get_domains(self) -> dict[str, Any]:
        """Get all available CDP domains.

        Returns:
            Dict containing the list of available domains.
        """
