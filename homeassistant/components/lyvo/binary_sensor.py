"""Interfaces with the Integration 101 Template api sensors."""

import logging

from clesydecloud import ClesydeCloud
from clesydecloud.client import ClesydeCloudClient

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_CLOUD, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Binary Sensors."""
    cloud = hass.data[DATA_CLOUD]
    async_add_entities([CloudRemoteBinary(cloud)])


class CloudRemoteBinary(BinarySensorEntity):
    """Implementation of the cloud connection state binary sensor."""

    _attr_name = "Clesyde Cloud"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_should_poll = False
    _attr_unique_id = "clesyde-cloud-connectivity"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, cloud: ClesydeCloud[ClesydeCloudClient]) -> None:
        """Initialize the binary sensor."""
        self.cloud = cloud

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.cloud.started

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.cloud.config.iot_cert_file
        # return self.cloud.config.iot_cert_file is not None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            name="LYVO",
            manufacturer="CLESYDE SA",
            model="V1",
            sw_version="1.0",
            serial_number=self.cloud.client.device_sn,
            identifiers={
                (
                    DOMAIN,
                    f"CLESYDE-LYVO-{self.cloud.client.device_sn}",
                )
            },
        )

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{DOMAIN}-{self.cloud.client.device_sn}"
