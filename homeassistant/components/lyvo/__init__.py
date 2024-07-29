"""The Clesyde cloud integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import logging

from clesydecloud import ClesydeCloud, InitializationError

from homeassistant.components.lyvo.services import ServicesSetup
from homeassistant.config_entries import SOURCE_SYSTEM, ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.signal_type import SignalType

from .client import CloudClient
from .const import DATA_CLOUD, DEV_PROVISIONING_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

SIGNAL_CLOUD_CONNECTION_STATE: SignalType[CloudConnectionState] = SignalType(
    "CLOUD_CONNECTION_STATE"
)


class CloudConnectionState(Enum):
    """Cloud connection state."""

    CLOUD_CONNECTED = "cloud_connected"
    CLOUD_INITIALIZED = "cloud_initialized"
    CLOUD_DISCONNECTED = "cloud_disconnected"


@dataclass
class RuntimeData:
    """Class to hold your data."""

    cancel_sensor_update_listener: Callable


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Clesyde cloud from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    cancel_sensor_update_listener = async_track_state_change_event(
        hass, ["sensor.system_monitor_memory_free"], _async_sensor_listener
    )

    hass.data[DOMAIN][entry.entry_id] = RuntimeData(cancel_sensor_update_listener)

    # Initialize Cloud
    websession = async_get_clientsession(hass)
    client = CloudClient(hass, websession)
    cloud = hass.data[DATA_CLOUD] = ClesydeCloud(client)

    async def _shutdown(event: Event) -> None:
        """Shutdown event."""
        await cloud.stop()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _shutdown)

    loaded = False

    async def _on_start() -> None:
        """Handle cloud started after login."""
        nonlocal loaded

        # Prevent multiple discovery
        if loaded:
            return
        loaded = True

        await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_SYSTEM}
        )
        _LOGGER.debug("Cloud started")

    async def _on_stop() -> None:
        """Handle cloud stopped."""
        _LOGGER.debug("Cloud stopped")
        async_dispatcher_send(
            hass, SIGNAL_CLOUD_CONNECTION_STATE, CloudConnectionState.CLOUD_DISCONNECTED
        )

    async def _on_initialized() -> None:
        """Handle cloud initialized."""
        _LOGGER.debug("Cloud initialized")
        async_dispatcher_send(
            hass, SIGNAL_CLOUD_CONNECTION_STATE, CloudConnectionState.CLOUD_INITIALIZED
        )

    cloud.register_on_stop(_on_start)
    cloud.register_on_stop(_on_stop)
    cloud.register_on_initialized(_on_initialized)
    cloud.register_on_start(_on_start)

    await cloud.provisioning.start_provisioning(provisioning_key=DEV_PROVISIONING_KEY)
    try:
        await cloud.initialize()
    except InitializationError as e:  # noqa: E722
        _LOGGER.error(e)

    ServicesSetup(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("CONFIG DIR: %s", hass.config.config_dir)

    return True


@callback
async def _async_sensor_listener(event: Event[EventStateChangedData]) -> None:
    """Handle config options update."""
    entity_id = event.data["entity_id"]
    old_state = event.data["old_state"]
    new_state = event.data["new_state"]

    _LOGGER.info("UPDATE RECEIVED: %s - %s > %s", entity_id, old_state, new_state)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Delete device if selected from UI."""
    # Adding this function shows the delete device option in the UI.
    # Remove this function if you do not want that option.
    # You may need to do some checks here before allowing devices to be removed.
    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
