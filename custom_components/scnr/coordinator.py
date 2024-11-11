"""Data update coordinator for SCNR."""
import asyncio
import logging
import uuid
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (API_AUTH_HOST, API_HOST_EU, API_TIMEOUT, APP_VERSION,
                   CLIENT_ID, CONF_DEBUG, CONF_PASSWORD, CONF_USERNAME, DOMAIN)

_LOGGER = logging.getLogger(__name__)

class SCNRDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self._access_token = None
        self._device_id = None
        self._uuid = str(uuid.uuid4())
        self._debug = entry.data.get(CONF_DEBUG, False)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        # if not self._access_token:
          await self._login()
        # if not self._device_id:
          await self._get_device()
        return {}

    async def _login(self):
        """Login to Switchbot."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_AUTH_HOST}/account/api/v1/user/login",
                headers={
                    "authorization": "",
                    "uuid": self._uuid,
                    "requestid": str(uuid.uuid4()),
                    "appversion": APP_VERSION,
                    "content-type": "application/json; charset=UTF-8",
                },
                json={
                    "clientId": CLIENT_ID,
                    "deviceInfo": {
                        "deviceId": self._uuid,
                        "deviceName": "Home Assistant",
                        "model": "Home Assistant",
                    },
                    "grantType": "password",
                    "password": self.entry.data[CONF_PASSWORD],
                    "username": self.entry.data[CONF_USERNAME],
                    "verifyCode": "",
                },
                timeout=API_TIMEOUT,
            ) as response:
                data = await response.json()
                if self._debug:
                    _LOGGER.debug("Login response: %s", data)
                self._access_token = data["body"]["access_token"]
                if self._debug:
                    _LOGGER.debug("Access Token: %s",  data["body"]["access_token"])

    async def _get_device(self):
        """Get device info."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_HOST_EU}/wonder/device/v3/getdevice",
                headers={
                    "authorization": self._access_token,
                    "uuid": self._uuid,
                    "requestid": str(uuid.uuid4()),
                    "appversion": APP_VERSION,
                    "content-type": "application/json; charset=UTF-8",
                },
                json={"required_type": "All"},
                timeout=API_TIMEOUT,
            ) as response:
                data = await response.json()
                if self._debug:
                    _LOGGER.debug("Get device response: %s", data)
                for device in data["body"]["Items"]:
                    if "Floor Cleaning Robot S10" in device["device_name"]:
                        self._device_id = device["device_mac"]
                        break

    async def clean_room(self, room_id: str, mode: str, water: int, fan: int, times: int):
        """Clean a specific room."""
        await self._async_update_data()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_HOST_EU}/command/cmd/api/v1/func/invoke",
                headers={
                    "authorization": self._access_token,
                    "uuid": self._uuid,
                    "requestid": str(uuid.uuid4()),
                    "appversion": APP_VERSION,
                    "content-type": "application/json; charset=UTF-8",
                },
                json={
                    "deviceID": self._device_id,
                    "functionID": 1001,
                    "notify": {
                        "type": "mqtt",
                        "url": f"v1_1/{self._uuid}/APP_HA_{self._uuid}/funcResp"
                    },
                    "params": {
                        "0": "clean_rooms",
                        "1": {
                            "force_order": True,
                            "mode": {
                                "fan_level": fan,
                                "times": times,
                                "type": mode,
                                "water_level": water
                            },
                            "rooms": [{
                                "mode": {
                                    "fan_level": fan,
                                    "times": times,
                                    "type": mode,
                                    "water_level": water
                                },
                                "room_id": room_id
                            }]
                        }
                    }
                },
                timeout=API_TIMEOUT,
            ) as response:
                data = await response.json()
                if self._debug:
                    _LOGGER.debug("Clean room response: %s", data)
                return data
