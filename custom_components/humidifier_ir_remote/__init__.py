"""Humidifier IR Remote integration."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.infrared import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .codes import HumidifierCommand
from .const import CONF_TRANSMITTER, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.HUMIDIFIER, Platform.BUTTON]

IR_SEND_TIMEOUT = 8.0  # seconds; bail out if the transmitter hangs


class _RuntimeData:
    """Shared state between the humidifier / button entities of one entry."""

    def __init__(self, hass: HomeAssistant, transmitter: str) -> None:
        """Initialise the per-entry runtime state."""
        self.hass = hass
        self.transmitter = transmitter
        self.send_lock = asyncio.Lock()

    async def send(self, button: HumidifierCommand) -> None:
        """Send one IR frame, serialised so concurrent presses don't garble.

        Times out after ``IR_SEND_TIMEOUT`` so an unresponsive transmitter
        can't hold the lock indefinitely and queue every subsequent press
        behind it forever.
        """
        async with self.send_lock:
            try:
                async with asyncio.timeout(IR_SEND_TIMEOUT):
                    await async_send_command(
                        self.hass, self.transmitter, button.to_command()
                    )
            except TimeoutError as err:
                _LOGGER.warning(
                    "IR send via %s timed out after %ss",
                    self.transmitter,
                    IR_SEND_TIMEOUT,
                )
                raise HomeAssistantError(
                    f"IR transmitter {self.transmitter} did not respond "
                    f"within {IR_SEND_TIMEOUT}s"
                ) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a humidifier from a config entry."""
    runtime = _RuntimeData(
        hass=hass,
        transmitter=entry.data[CONF_TRANSMITTER],
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        # Roll back the runtime registration if any platform failed to set
        # up — otherwise get_runtime() would return a half-wired object.
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


def get_runtime(hass: HomeAssistant, entry_id: str) -> _RuntimeData:
    """Look up the shared runtime data for a config entry."""
    return hass.data[DOMAIN][entry_id]
