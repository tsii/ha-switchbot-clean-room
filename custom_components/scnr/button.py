"""Support for SCNR buttons."""
from __future__ import annotations

import logging
import asyncio

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SCNRDataUpdateCoordinator
from .const import DOMAIN
from .entity import SCNREntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SCNR button based on a config entry."""
    coordinator: SCNRDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Wait a bit to ensure other entities are set up
    await asyncio.sleep(2)
    async_add_entities([SCNRCleanButton(coordinator)])

class SCNRCleanButton(SCNREntity, ButtonEntity):
    """Representation of a SCNR clean button."""

    def __init__(self, coordinator: SCNRDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator, "clean_button")
        self._attr_name = "Clean Room"
        self._attr_icon = "mdi:robot-vacuum"

    async def async_press(self) -> None:
        """Press the button."""
        _LOGGER.debug("Clean button pressed, attempting to find required entities...")

        # Get entity states using the correct entity IDs
        room_state = self.hass.states.get("select.room")
        mode_state = self.hass.states.get("select.mode")
        water_state = self.hass.states.get("number.water_level")
        fan_state = self.hass.states.get("number.fan_level")
        times_state = self.hass.states.get("number.clean_times")

        # Log entity states for debugging
        _LOGGER.debug("Entity states found:")
        _LOGGER.debug("- Room select: %s (entity: %s)", 
                     room_state.state if room_state else None,
                     "select.room")
        _LOGGER.debug("- Mode select: %s (entity: %s)", 
                     mode_state.state if mode_state else None,
                     "select.mode")
        _LOGGER.debug("- Water level: %s (entity: %s)", 
                     water_state.state if water_state else None,
                     "number.water_level")
        _LOGGER.debug("- Fan level: %s (entity: %s)", 
                     fan_state.state if fan_state else None,
                     "number.fan_level")
        _LOGGER.debug("- Clean times: %s (entity: %s)", 
                     times_state.state if times_state else None,
                     "number.clean_times")

        if not all([room_state, mode_state, water_state, fan_state, times_state]):
            _LOGGER.error("Could not find all required entities:")
            _LOGGER.error("Missing entities:")
            if not room_state:
                _LOGGER.error("- Room select: select.room")
            if not mode_state:
                _LOGGER.error("- Mode select: select.mode")
            if not water_state:
                _LOGGER.error("- Water level: number.water_level")
            if not fan_state:
                _LOGGER.error("- Fan level: number.fan_level")
            if not times_state:
                _LOGGER.error("- Clean times: number.clean_times")
            return

        try:
            await self.coordinator.clean_room(
                room_state.state,
                mode_state.state,
                int(float(water_state.state)),
                int(float(fan_state.state)),
                int(float(times_state.state))
            )
            _LOGGER.debug("Clean command sent successfully")
        except Exception as e:
            _LOGGER.error("Error sending clean command: %s", str(e))