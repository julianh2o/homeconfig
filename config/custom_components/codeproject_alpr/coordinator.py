"""DataUpdateCoordinator for CodeProject.AI ALPR."""
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ALPRDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ALPR data and coordinating updates."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),  # Not used for polling, but required
        )
        self.last_annotated_image: bytes | None = None
        self.last_predictions: list[dict[str, Any]] = []
        self.last_update_time: datetime | None = None
        self.last_source_camera: str | None = None

    def update_data(
        self,
        image_bytes: bytes | None,
        predictions: list[dict[str, Any]],
        source_camera: str,
    ) -> None:
        """Update the coordinator with new ALPR results."""
        self.last_annotated_image = image_bytes
        self.last_predictions = predictions
        self.last_update_time = datetime.now()
        self.last_source_camera = source_camera

        # Notify all entities that data has been updated
        self.async_set_updated_data({
            "image": image_bytes,
            "predictions": predictions,
            "timestamp": self.last_update_time,
            "source": source_camera,
        })

    def get_annotated_image(self) -> bytes | None:
        """Get the latest annotated image."""
        return self.last_annotated_image

    def get_predictions(self) -> list[dict[str, Any]]:
        """Get the latest predictions."""
        return self.last_predictions
