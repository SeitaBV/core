"""The FlexMeasures integration."""

from __future__ import annotations

import logging

from flexmeasures_client import FlexMeasuresClient

# import isodate
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.dt import parse_duration

from .config_flow import get_host_and_ssl_from_url
from .const import DOMAIN, FRBC_CONFIG
from .control_types import FRBC_Config
from .services import (
    async_setup_services,
    async_unload_services,
    get_from_option_or_config,
)
from .websockets import WebsocketAPIView

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FlexMeasures from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # use entry.data directly instead of the config_data dict
    # config_data = dict(entry.data)
    # Registers update listener to update config entry when options are updated.
    # unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    # config_data["unsub_options_update_listener"] = unsub_options_update_listener
    host, ssl = get_host_and_ssl_from_url(entry.data["url"])
    client = FlexMeasuresClient(
        host=host,
        email=entry.data["username"],
        password=entry.data["password"],
        ssl=ssl,
        session=async_get_clientsession(hass),
    )

    # make dataclass FRBC
    # put all the data in the dataclass
    # hass.data[DOMAIN] = dataclass

    # store config
    # if shcedule_duration is not set, throw an error
    if not entry.data.get("schedule_duration"):
        _LOGGER.error("Schedule duration is not set")
        return False
    FRBC_data = FRBC_Config(
        power_sensor_id=get_from_option_or_config("power_sensor", entry),
        price_sensor_id=get_from_option_or_config("consumption_price_sensor", entry),
        soc_sensor_id=get_from_option_or_config("soc_sensor", entry),
        rm_discharge_sensor_id=get_from_option_or_config("rm_discharge_sensor", entry),
        schedule_duration=parse_duration(
            get_from_option_or_config("schedule_duration", entry)
        ),
    )
    hass.data[DOMAIN][FRBC_CONFIG] = FRBC_data

    hass.data[DOMAIN]["fm_client"] = client

    hass.http.register_view(WebsocketAPIView())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await async_setup_services(hass, entry)

    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""

    _LOGGER.debug("Configuration options updated, reloading FlexMeasures integration")
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN not in hass.data:
        return True

    # Remove services
    await async_unload_services(hass)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
