"""Constants for the Clesyde cloud integration."""

DOMAIN = "lyvo"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10

CONF_ROOT_PATH = "cloud-config-storage"
CONF_API_URL = "https://w7xs6miqla.execute-api.eu-west-1.amazonaws.com/api"  # TODO: move to library

# TODO: pass mode to library
MODE_DEV = "development"
MODE_PROD = "production"

DATA_CLOUD = "CLESYDE_LYVO"

DEV_SN = "aabbccddeeff1245"
DEV_PROVISIONING_KEY = (
    "c74e5eadba2b91c8a5aff9147ded17104f5dcbfb04a48061ff81831c880e4d2f"
)

CLOUD_MQTT_SERVICE_NAME = "cloud_mqtt_ping_service"
CLOUD_SEND_MQTT_MESSAGE_SERVICE_NAME = "cloud_send_mqtt_message_service"
ATT_PAYLOAD = "payload"
ATT_TOPIC = "topic"
RESPONSE_SERVICE_NAME = "response_service"

CONF_ENTRY_ID = "CLESYDE LYVO BOX"
