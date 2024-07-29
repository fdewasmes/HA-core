"""Global services file.

This needs to be viewed with the services.yaml file
to demonstrate the different setup for using these services in the UI

IMPORTANT NOTES:
To ensure your service runs on the event loop, either make service function async
or decorate with @callback.  However, ensure that your function is non blocking or,
if it is, run in the executor.
Both examples are shown here.  Running services on different threads can cause issues.

https://developers.home-assistant.io/docs/dev_101_services/
"""

from clesydecloud import ClesydeCloud
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    ATT_PAYLOAD,
    ATT_TOPIC,
    CLOUD_MQTT_SERVICE_NAME,
    CLOUD_SEND_MQTT_MESSAGE_SERVICE_NAME,
    DATA_CLOUD,
    DOMAIN,
)

SEND_MSG_SCHEMA = vol.Schema(
    {
        vol.Required(ATT_PAYLOAD): str,
        vol.Required(ATT_TOPIC): str,
    }
)


class ServicesSetup:
    """Class to handle Integration Services."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialise services."""
        self.hass = hass
        self.config_entry = config_entry

        self.setup_services()

    def setup_services(self):
        """Initialise the services in Hass."""

        self.hass.services.async_register(
            DOMAIN,
            CLOUD_MQTT_SERVICE_NAME,
            self.send_mqtt_ping_message,
        )

        self.hass.services.async_register(
            DOMAIN,
            CLOUD_SEND_MQTT_MESSAGE_SERVICE_NAME,
            self.send_mqtt_message,
            schema=SEND_MSG_SCHEMA,
        )

    async def send_mqtt_ping_message(self, service_call: ServiceCall) -> None:
        """Send a ping message to AWS IOT thing over MQTT."""

        cloud: ClesydeCloud = self.hass.data[DATA_CLOUD]
        cloud.iot.publish(cloud.iot_message.status_topic, '{"state": "PING"}', 0, False)

    async def send_mqtt_message(self, service_call: ServiceCall) -> None:
        """Send a message to AWS IOT thing over MQTT."""

        payload = service_call.data[ATT_PAYLOAD]
        topic = service_call.data[ATT_TOPIC]

        cloud: ClesydeCloud = self.hass.data[DATA_CLOUD]
        target_topic = ""
        match topic:
            case "status":
                target_topic = cloud.iot_message.status_topic
            case "config":
                target_topic = (
                    f"$aws/things/{cloud.client.device_sn}/shadow/name/config/get"
                )

        cloud.iot.publish(target_topic, payload, 0, False)
