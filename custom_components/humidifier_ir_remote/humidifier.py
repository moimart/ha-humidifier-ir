"""Humidifier entity — power + Continuous / Intermittent modes."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import get_runtime
from .codes import HumidifierCommand
from .const import (
    AVAILABLE_MODES,
    DOMAIN,
    MODE_CONTINUOUS,
    MODE_INTERMITTENT,
)

INTER_PRESS_DELAY = 0.15

_MODE_TO_BUTTON: dict[str, HumidifierCommand] = {
    MODE_CONTINUOUS: HumidifierCommand.CONTINUOUS,
    MODE_INTERMITTENT: HumidifierCommand.INTERMITTENT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the humidifier entity."""
    async_add_entities([IrHumidifier(entry)])


class IrHumidifier(HumidifierEntity, RestoreEntity):
    """A humidifier driven by a one-way IR remote.

    The physical remote has only a single POWER button that toggles on/off,
    so we send the same code in both turn_on and turn_off and assume state.
    """

    _attr_assumed_state = True
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_available_modes = AVAILABLE_MODES

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialise."""
        self._entry_id = entry.entry_id
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Generic",
            "model": "IR Humidifier",
        }
        self._attr_is_on = False
        self._attr_mode = MODE_CONTINUOUS

    @property
    def _runtime(self) -> Any:
        return get_runtime(self.hass, self._entry_id)

    async def async_added_to_hass(self) -> None:
        """Restore last state across restarts."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is None:
            return
        self._attr_is_on = last_state.state == "on"
        mode = last_state.attributes.get("mode")
        if isinstance(mode, str) and mode in AVAILABLE_MODES:
            self._attr_mode = mode

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Send the power-toggle code if we believe we're currently off."""
        if not self._attr_is_on:
            await self._runtime.send(HumidifierCommand.POWER)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Send the power-toggle code if we believe we're currently on."""
        if self._attr_is_on:
            await self._runtime.send(HumidifierCommand.POWER)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_set_mode(self, mode: str) -> None:
        """Set the mist mode (Continuous / Intermittent)."""
        button = _MODE_TO_BUTTON.get(mode)
        if button is None:
            return
        # Ensure the humidifier is on before sending a mode command — pressing
        # a mode button on a powered-off unit does nothing on most of these.
        if not self._attr_is_on:
            await self._runtime.send(HumidifierCommand.POWER)
            self._attr_is_on = True
            await asyncio.sleep(INTER_PRESS_DELAY)
        await self._runtime.send(button)
        self._attr_mode = mode
        self.async_write_ha_state()
