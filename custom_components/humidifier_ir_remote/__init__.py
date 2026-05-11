"""Humidifier IR Remote integration."""

from __future__ import annotations

import asyncio

from homeassistant.components.infrared import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .codes import HumidifierCommand
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.HUMIDIFIER, Platform.SWITCH, Platform.BUTTON]

# Per-config-entry runtime state stored on the entry.
type HumidifierIrEntryData = "_RuntimeData"


class _RuntimeData:
    """Shared state between the humidifier / switch / button entities."""

    def __init__(self, hass: HomeAssistant, transmitter: str) -> None:
        self.hass = hass
        self.transmitter = transmitter
        self.send_lock = asyncio.Lock()

    async def send(self, button: HumidifierCommand) -> None:
        """Send one IR frame, serialised so concurrent presses don't garble."""
        async with self.send_lock:
            await async_send_command(
                self.hass, self.transmitter, button.to_command()
            )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a humidifier from a config entry."""
    from .const import CONF_TRANSMITTER

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = _RuntimeData(
        hass=hass,
        transmitter=entry.data[CONF_TRANSMITTER],
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


def get_runtime(hass: HomeAssistant, entry_id: str) -> _RuntimeData:
    """Look up the shared runtime data for a config entry."""
    return hass.data[DOMAIN][entry_id]
