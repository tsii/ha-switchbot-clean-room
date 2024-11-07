"""Support for SCNR selects."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SCNRDataUpdateCoordinator
from .const import DOMAIN
from .entity import SCNREntity

ROOMS = ["ROOM_000", "ROOM_001", "ROOM_002", "ROOM_003", "ROOM_0044", "ROOM_005", "ROOM_006", "ROOM_007", "ROOM_008", "ROOM_009", ]
MODES = ["sweep", "sweep_mop"]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SCNR select based on a config entry."""
    coordinator: SCNRDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SCNRRoomSelect(coordinator),
        SCNRModeSelect(coordinator),
    ])

class SCNRRoomSelect(SCNREntity, SelectEntity):
    """Representation of a SCNR room select."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "room_select")
        self._attr_name = "Room"
        self._attr_options = ROOMS
        self._attr_current_option = ROOMS[0]
        self._attr_icon = "mdi:door"

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()

class SCNRModeSelect(SCNREntity, SelectEntity):
    """Representation of a SCNR mode select."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "mode_select")
        self._attr_name = "Mode"
        self._attr_options = MODES
        self._attr_current_option = MODES[0]
        self._attr_icon = "mdi:vacuum"

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()
