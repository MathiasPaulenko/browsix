"""Sensor mixin — sensor emulation and override."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SensorBackend(ABC):
    """Sensor domain for emulating and overriding device sensors."""

    @abstractmethod
    async def sensor_clear_sensor_override(self, sensor_type: str) -> None:
        """Clear a sensor override.

        Args:
            sensor_type: The type of sensor to clear override for.
        """

    @abstractmethod
    async def sensor_disable(self) -> None:
        """Disable the Sensor domain."""

    @abstractmethod
    async def sensor_enable(self) -> None:
        """Enable the Sensor domain."""

    @abstractmethod
    async def sensor_set_sensor_override(
        self, sensor_type: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Set a sensor override.

        Args:
            sensor_type: The type of sensor to override.
            metadata: Optional sensor metadata.
        """
