"""The CodeProject.AI ALPR integration."""
import base64
import io
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from PIL import Image, ImageDraw, ImageFont

from homeassistant.components.camera import async_get_image
from homeassistant.const import CONF_TIMEOUT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import (
    ALPR_ENDPOINT,
    ATTR_ENTITY_ID,
    CONF_MIN_CONFIDENCE,
    CONF_SERVER_URL,
    DEFAULT_MIN_CONFIDENCE,
    DEFAULT_TIMEOUT,
    DETECTION_ENDPOINT,
    DOMAIN,
    SERVICE_ANALYZE_CAMERA,
)
from .coordinator import ALPRDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["camera", "sensor"]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SERVER_URL): cv.url,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
                vol.Optional(CONF_MIN_CONFIDENCE, default=DEFAULT_MIN_CONFIDENCE): vol.All(
                    vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_ANALYZE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_domain("camera"),
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the CodeProject.AI ALPR component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    server_url = conf[CONF_SERVER_URL]
    timeout = conf[CONF_TIMEOUT]
    min_confidence = conf[CONF_MIN_CONFIDENCE]

    # Create coordinator
    coordinator = ALPRDataCoordinator(hass)

    # Store config and coordinator
    hass.data[DOMAIN] = {
        "config": conf,
        "coordinator": coordinator,
        "server_url": server_url,
        "timeout": timeout,
        "min_confidence": min_confidence,
    }

    async def handle_analyze_camera(call: ServiceCall) -> None:
        """Handle the analyze_camera service call."""
        entity_id = call.data[ATTR_ENTITY_ID]

        _LOGGER.debug("Analyzing camera %s for objects", entity_id)

        try:
            # Capture snapshot from camera
            image = await async_get_image(hass, entity_id)
            image_bytes = image.content
            _LOGGER.info(
                "Captured image from %s: %d bytes, content_type=%s",
                entity_id,
                len(image_bytes),
                image.content_type,
            )

        except Exception as err:
            _LOGGER.error("Failed to capture image from %s: %s", entity_id, err)
            raise ServiceValidationError(
                f"Failed to capture image from {entity_id}: {err}"
            ) from err

        # Send to CodeProject.AI Object Detection API
        session = async_get_clientsession(hass)
        url = f"{server_url}{DETECTION_ENDPOINT}"

        try:
            data = aiohttp.FormData()
            data.add_field(
                "upload",
                image_bytes,
                filename="snapshot.jpg",
                content_type=image.content_type,
            )
            data.add_field("min_confidence", str(min_confidence))

            async with session.post(
                url, data=data, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "CodeProject.AI API returned status %s", response.status
                    )
                    return

                result = await response.json()

        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to connect to CodeProject.AI at %s: %s", url, err)
            return
        except Exception as err:
            _LOGGER.error("Unexpected error calling CodeProject.AI: %s", err, exc_info=True)
            return

        # Parse response
        _LOGGER.debug("CodeProject.AI response: %s", result)
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            _LOGGER.warning("Object detection failed: %s (full response: %s)", error_msg, result)
            return

        predictions = result.get("predictions", [])
        _LOGGER.info("Detected %d object(s)", len(predictions))

        # Draw bounding boxes on the image
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            draw = ImageDraw.Draw(pil_image)

            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()

            # Draw each detection
            for pred in predictions:
                x_min = pred.get("x_min", 0)
                y_min = pred.get("y_min", 0)
                x_max = pred.get("x_max", 0)
                y_max = pred.get("y_max", 0)
                label = pred.get("label", "unknown")
                confidence = pred.get("confidence", 0)

                # Draw rectangle
                draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=3)

                # Draw label
                text = f"{label} ({confidence:.2f})"
                draw.text((x_min, y_min - 25), text, fill="red", font=font)

            # Convert back to bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG")
            annotated_image = buffer.getvalue()

        except Exception as err:
            _LOGGER.warning("Failed to draw bounding boxes: %s", err)
            annotated_image = image_bytes

        # Update coordinator with results
        coordinator.update_data(
            image_bytes=annotated_image,
            predictions=predictions,
            source_camera=entity_id,
        )

        _LOGGER.debug("Successfully updated ALPR data for %s", entity_id)

    # Register service
    hass.services.async_register(
        DOMAIN,
        SERVICE_ANALYZE_CAMERA,
        handle_analyze_camera,
        schema=SERVICE_ANALYZE_SCHEMA,
    )

    # Set up platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
        )

    return True
