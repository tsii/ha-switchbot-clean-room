"""Support for SCNR numbers."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SCNRDataUpdateCoordinator
from .const import DOMAIN
from .entity import SCNREntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SCNR number based on a config entry."""
    coordinator: SCNRDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SCNRWaterLevel(coordinator),
        SCNRFanLevel(coordinator),
        SCNRCleanTimes(coordinator),
    ])

class SCNRWaterLevel(SCNREntity, NumberEntity):
    """Representation of a SCNR water level number."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "water_level")
        self._attr_name = "Water Level"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 2
        self._attr_native_step = 1
        self._attr_native_value = 1
        self._attr_icon = "mdi:water"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()

class SCNRFanLevel(SCNREntity, NumberEntity):
    """Representation of a SCNR fan level number."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "fan_level")
        self._attr_name = "Fan Level"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 4
        self._attr_native_step = 1
        self._attr_native_value = 1
        self._attr_icon = "mdi:fan"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()

class SCNRCleanTimes(SCNREntity, NumberEntity):
    """Representation of a SCNR clean times number."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "clean_times")
        self._attr_name = "Clean Times"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 2
        self._attr_native_step = 1
        self._attr_native_value = 1
        self._attr_icon = "mdi:refresh"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()