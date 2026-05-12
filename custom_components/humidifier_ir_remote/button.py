"""Button entities — Cycle Timer, Light, Mist Level."""

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
    """Set up the three press-to-toggle buttons."""
    async_add_entities(
        [
            OneShotButton(
                entry=entry,
                key="cycle_timer",
                friendly_name="Cycle Timer",
                button=HumidifierCommand.TIMER,
                icon="mdi:timer-cog-outline",
            ),
            OneShotButton(
                entry=entry,
                key="light",
                friendly_name="Light",
                button=HumidifierCommand.LIGHT,
                icon="mdi:lightbulb-night-outline",
            ),
            OneShotButton(
                entry=entry,
                key="mist_level",
                friendly_name="Mist Level",
                button=HumidifierCommand.MIST_LEVEL,
                icon="mdi:weather-fog",
            ),
        ]
    )


class OneShotButton(ButtonEntity):
    """A one-press button that sends a single IR code.

    The physical remote has one button for each of these — pressing it on
    the unit toggles the underlying state. We don't try to model that state
    in HA (no feedback channel = lying state would mislead automations);
    just expose the press as a simple action.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        entry: ConfigEntry,
        key: str,
        friendly_name: str,
        button: HumidifierCommand,
        icon: str,
    ) -> None:
        """Initialise the button entity."""
        self._entry_id = entry.entry_id
        self._button = button
        self._attr_name = friendly_name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = icon
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
        """Send one IR frame for the configured command."""
        await self._runtime.send(self._button)
