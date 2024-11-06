"""Base entity for SCNR."""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import SCNRDataUpdateCoordinator

class SCNREntity(CoordinatorEntity[SCNRDataUpdateCoordinator]):
    """Base class for SCNR entities."""

    def __init__(
        self,
        coordinator: SCNRDataUpdateCoordinator,
        entity_type: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._device_id}_{entity_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator._device_id)},
            name=DEFAULT_NAME,
            manufacturer="Switchbot",
            model="S10",
        )