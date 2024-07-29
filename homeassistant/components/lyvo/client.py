"""Interface implementation for cloud client."""

import asyncio
from pathlib import Path

import aiohttp
from clesydecloud import ClesydeCloudClient as Interface

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import SERVER_SOFTWARE

from .const import CONF_API_URL, CONF_ROOT_PATH
from .utility import get_serial_number


class CloudClient(Interface):
    """Interface class for Clesyde Cloud."""

    def __init__(
        self,
        hass: HomeAssistant,
        websession: aiohttp.ClientSession,
    ) -> None:
        """Initialize client interface to Cloud."""
        self._hass = hass
        self._websession = websession
        p = Path(self._hass.config.config_dir) / CONF_ROOT_PATH
        p.mkdir(exist_ok=True)
        self._base_path = p
        self._clesyde_api_base_url = CONF_API_URL
        self._sn = get_serial_number()

    @property
    def base_path(self) -> Path:
        """Return path to base dir."""
        return self._base_path

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Return client loop."""
        return self._hass.loop

    @property
    def websession(self) -> aiohttp.ClientSession:
        """Return client session for aiohttp."""
        return self._websession

    @property
    def aiohttp_runner(self) -> aiohttp.web.AppRunner | None:
        """Return client webinterface aiohttp application."""
        return self._hass.http.runner

    @property
    def client_name(self) -> str:
        """Return the client name that will be used for API calls."""
        return SERVER_SOFTWARE

    @property
    def api_base_url(self) -> str:
        """Return the api base url that will be used for API calls."""
        return self._clesyde_api_base_url

    @property
    def device_sn(self) -> str:
        """Return the LYVO box serial number."""
        return self._sn
