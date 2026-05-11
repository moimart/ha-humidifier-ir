"""Switch entities — Night Light, High Mist."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import get_runtime
from .codes import HumidifierCommand
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the two toggle switches."""
    async_add_entities(
        [
            ToggleSwitch(
                entry=entry,
                key="night_light",
                friendly_name="Night Light",
                button=HumidifierCommand.LIGHT,
                icon="mdi:lightbulb-night-outline",
            ),
            ToggleSwitch(
                entry=entry,
                key="high_mist",
                friendly_name="High Mist",
                button=HumidifierCommand.MIST_LEVEL,
                icon="mdi:weather-fog",
            ),
        ]
    )


class ToggleSwitch(SwitchEntity, RestoreEntity):
    """A binary toggle backed by a single IR code press.

    The humidifier remote has no "set to on" / "set to off" — only a button
    that flips state. We track assumed state and only send the IR code when
    HA's target state differs from ours.
    """

    _attr_assumed_state = True
    _attr_should_poll = False
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
        """Initialise."""
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
        self._attr_is_on = False

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

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Flip on if we believe we're currently off."""
        if not self._attr_is_on:
            await self._runtime.send(self._button)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Flip off if we believe we're currently on."""
        if self._attr_is_on:
            await self._runtime.send(self._button)
        self._attr_is_on = False
        self.async_write_ha_state()
