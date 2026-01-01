"""Sensor platform for CodeProject.AI ALPR."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    ATTR_LAST_UPDATE,
    ATTR_OBJECTS,
    ATTR_SOURCE_CAMERA,
    DEFAULT_NAME,
    DOMAIN,
)
from .coordinator import ALPRDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the ALPR sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([ALPRSensor(coordinator)], True)


class ALPRSensor(SensorEntity):
    """Representation of an ALPR sensor."""

    def __init__(self, coordinator: ALPRDataCoordinator) -> None:
        """Initialize the ALPR sensor."""
        self.coordinator = coordinator
        self._attr_name = "Object Detection"
        self._attr_unique_id = f"{DOMAIN}_detected_objects"
        self._attr_icon = "mdi:image-search"

        # Listen to coordinator updates
        self.coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the number of detected objects."""
        return len(self.coordinator.get_predictions())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        predictions = self.coordinator.get_predictions()

        attributes = {
            ATTR_OBJECTS: predictions,
            ATTR_SOURCE_CAMERA: self.coordinator.last_source_camera,
        }

        if self.coordinator.last_update_time:
            attributes[ATTR_LAST_UPDATE] = self.coordinator.last_update_time.isoformat()

        return attributes

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_time is not None
