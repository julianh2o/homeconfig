"""Constants for the CodeProject.AI ALPR integration."""

DOMAIN = "codeproject_alpr"

# Configuration keys
CONF_SERVER_URL = "server_url"
CONF_MIN_CONFIDENCE = "min_confidence"

# Service names
SERVICE_ANALYZE_CAMERA = "analyze_camera"

# Service data attributes
ATTR_ENTITY_ID = "entity_id"

# Sensor attributes
ATTR_OBJECTS = "objects"
ATTR_PLATES = "plates"
ATTR_PLATE = "plate"
ATTR_LABEL = "label"
ATTR_CONFIDENCE = "confidence"
ATTR_BOUNDING_BOX = "bounding_box"
ATTR_LAST_UPDATE = "last_update"
ATTR_SOURCE_CAMERA = "source_camera"

# API endpoints
ALPR_ENDPOINT = "/v1/vision/alpr"
DETECTION_ENDPOINT = "/v1/vision/detection"

# Default values
DEFAULT_TIMEOUT = 30
DEFAULT_MIN_CONFIDENCE = 0.4
DEFAULT_NAME = "ALPR"
