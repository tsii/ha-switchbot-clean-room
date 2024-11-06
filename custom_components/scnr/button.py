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
        # Wait for entities to be fully initialized (max 10 seconds)
        for _ in range(20):  # 20 attempts * 0.5 seconds = 10 seconds max
            room_state = self.hass.states.get(f"select.{self.coordinator._device_id}_room_select")
            mode_state = self.hass.states.get(f"select.{self.coordinator._device_id}_mode_select")
            water_state = self.hass.states.get(f"number.{self.coordinator._device_id}_water_level")
            fan_state = self.hass.states.get(f"number.{self.coordinator._device_id}_fan_level")
            times_state = self.hass.states.get(f"number.{self.coordinator._device_id}_clean_times")

            if all([room_state, mode_state, water_state, fan_state, times_state]):
                await self.coordinator.clean_room(
                    room_state.state,
                    mode_state.state,
                    int(float(water_state.state)),
                    int(float(fan_state.state)),
                    int(float(times_state.state))
                )
                return

            await asyncio.sleep(0.5)

        _LOGGER.error("Could not find all required entities: room=%s, mode=%s, water=%s, fan=%s, times=%s",
                     room_state, mode_state, water_state, fan_state, times_state)