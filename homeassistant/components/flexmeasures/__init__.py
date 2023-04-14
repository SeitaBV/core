"""The FlexMeasures integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .authorisation import FlexMeasures
from .const import DOMAIN

ATTR_NAME = "name"
DEFAULT_NAME = "World"


# def setup(hass: HomeAssistant, config):
#     """Set up is called when Home Assistant is loading our component."""

#     # Return boolean to indicate that initialization was successful.
#     return True


# # List the platforms that you want to support.
# # For your initial PR, limit it to 1 platform.
# # PLATFORMS: list[Platform] = [Platform.LIGHT]
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FlexMeasures from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    flexmeasures = FlexMeasures()

    # 1. Create API instance
    # 2. Validate the API connection (and authentication)
    # 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    async def handle_api(call):
        """Handle the service call to the FlexMeasures REST API."""
        call.data.get(ATTR_NAME, DEFAULT_NAME)

        email = "guus@seita.nl"
        password = "test"

        data = await flexmeasures.get_access_token(password, email)

        # result = await hass.async_add_executor_job(auth.authenticate_with_fm)

        # hass.states.set("flexmeasures_api.schedule", result)

        hass.states.async_set("flexmeasures_api.message", data)

    # def handle_s2(call):
    #     """Handle the service call to the FlexMeasures S2 websockets implementation."""
    #     name = call.data.get(ATTR_NAME, DEFAULT_NAME)

    #     hass.states.set("flexmeasures_s2.message", name)

    # # Register services
    hass.services.async_register(DOMAIN, "api", handle_api)
    # hass.services.async_register(DOMAIN, "s2", handle_s2)

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    # Remove services
    hass.services.async_remove(DOMAIN, "api")
    hass.services.async_remove(DOMAIN, "s2")

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
