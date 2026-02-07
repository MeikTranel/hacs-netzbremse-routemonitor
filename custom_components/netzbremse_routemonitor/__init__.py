"""The Netzbremse Routemonitor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL, DOMAIN
from .coordinator import NetzbremseRoutemonitorCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Netzbremse Routemonitor from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry for this integration.

    Returns:
        True if setup was successful.
    """
    _LOGGER.debug("Setting up Netzbremse Routemonitor integration")

    # Get polling interval from config entry, use default if not set
    polling_interval = entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

    # Create the data update coordinator
    coordinator = NetzbremseRoutemonitorCoordinator(
        hass=hass,
        polling_interval=polling_interval,
    )

    # Store coordinator in hass.data for access by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms (sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Netzbremse Routemonitor integration setup completed")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry to unload.

    Returns:
        True if unload was successful.
    """
    _LOGGER.debug("Unloading Netzbremse Routemonitor integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info("Netzbremse Routemonitor integration unloaded")
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change.

    Args:
        hass: Home Assistant instance.
        entry: Config entry to reload.
    """
    _LOGGER.debug("Reloading Netzbremse Routemonitor integration")
    await hass.config_entries.async_reload(entry.entry_id)
