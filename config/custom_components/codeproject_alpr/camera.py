"""Camera platform for CodeProject.AI ALPR."""
import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import ALPRDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the ALPR camera platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([ALPRCamera(coordinator)], True)


class ALPRCamera(Camera):
    """Representation of an ALPR annotated camera."""

    def __init__(self, coordinator: ALPRDataCoordinator) -> None:
        """Initialize the ALPR camera."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_name = "Object Detection Camera"
        self._attr_unique_id = f"{DOMAIN}_annotated_camera"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return image response."""
        return self.coordinator.get_annotated_image()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.get_annotated_image() is not None
