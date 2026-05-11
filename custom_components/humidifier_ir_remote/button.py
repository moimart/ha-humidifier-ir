"""Button entity — Cycle Timer."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import get_runtime
from .codes import HumidifierCommand
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the timer-cycle button."""
    async_add_entities([CycleTimerButton(entry)])


class CycleTimerButton(ButtonEntity):
    """One-shot button that advances the timer state on the humidifier.

    The physical button cycles through whatever timer presets the unit has
    (typically 1h → 2h → 4h → off, but varies by model). We don't track which
    preset is active — pressing this just sends one IR frame.
    """

    _attr_has_entity_name = True
    _attr_name = "Cycle Timer"
    _attr_icon = "mdi:timer-cog-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialise."""
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{entry.entry_id}_timer_cycle"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Generic",
            "model": "IR Humidifier",
        }

    @property
    def _runtime(self) -> Any:
        return get_runtime(self.hass, self._entry_id)

    async def async_press(self) -> None:
        """Send one timer-cycle press."""
        await self._runtime.send(HumidifierCommand.TIMER)
