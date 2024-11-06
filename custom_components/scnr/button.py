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
        
        # Wait for entities to be fully initialized (max 10 seconds)
        for attempt in range(20):  # 20 attempts * 0.5 seconds = 10 seconds max
            _LOGGER.debug("Attempt %d/20 to find entities", attempt + 1)
            
            # Get entity states
            room_state = self.hass.states.get(f"select.{self.coordinator._device_id}_room_select")
            mode_state = self.hass.states.get(f"select.{self.coordinator._device_id}_mode_select")
            water_state = self.hass.states.get(f"number.{self.coordinator._device_id}_water_level")
            fan_state = self.hass.states.get(f"number.{self.coordinator._device_id}_fan_level")
            times_state = self.hass.states.get(f"number.{self.coordinator._device_id}_clean_times")

            # Log the current state of each entity
            _LOGGER.debug("Entity states found:")
            _LOGGER.debug("- Room select: %s (entity: %s)", 
                         room_state.state if room_state else None,
                         f"select.{self.coordinator._device_id}_room_select")
            _LOGGER.debug("- Mode select: %s (entity: %s)", 
                         mode_state.state if mode_state else None,
                         f"select.{self.coordinator._device_id}_mode_select")
            _LOGGER.debug("- Water level: %s (entity: %s)", 
                         water_state.state if water_state else None,
                         f"number.{self.coordinator._device_id}_water_level")
            _LOGGER.debug("- Fan level: %s (entity: %s)", 
                         fan_state.state if fan_state else None,
                         f"number.{self.coordinator._device_id}_fan_level")
            _LOGGER.debug("- Clean times: %s (entity: %s)", 
                         times_state.state if times_state else None,
                         f"number.{self.coordinator._device_id}_clean_times")

            if all([room_state, mode_state, water_state, fan_state, times_state]):
                _LOGGER.debug("All required entities found, proceeding with clean command")
                try:
                    await self.coordinator.clean_room(
                        room_state.state,
                        mode_state.state,
                        int(float(water_state.state)),
                        int(float(fan_state.state)),
                        int(float(times_state.state))
                    )
                    _LOGGER.debug("Clean command sent successfully")
                    return
                except Exception as e:
                    _LOGGER.error("Error sending clean command: %s", str(e))
                    return

            _LOGGER.debug("Not all entities found yet, waiting 0.5 seconds before next attempt")
            await asyncio.sleep(0.5)

        _LOGGER.error("Could not find all required entities after 20 attempts:")
        _LOGGER.error("Device ID: %s", self.coordinator._device_id)
        _LOGGER.error("Missing entities:")
        if not room_state:
            _LOGGER.error("- Room select: select.%s_room_select", self.coordinator._device_id)
        if not mode_state:
            _LOGGER.error("- Mode select: select.%s_mode_select", self.coordinator._device_id)
        if not water_state:
            _LOGGER.error("- Water level: number.%s_water_level", self.coordinator._device_id)
        if not fan_state:
            _LOGGER.error("- Fan level: number.%s_fan_level", self.coordinator._device_id)
        if not times_state:
            _LOGGER.error("- Clean times: number.%s_clean_times", self.coordinator._device_id)