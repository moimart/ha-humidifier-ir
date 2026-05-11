"""NEC code table for the IR humidifier remote.

All 6 buttons captured + decoded with valid NEC inverse-byte checksums.
The humidifier uses standard NEC at 38 kHz with address 0x00.

The original remote always emits each press as **frame + NEC repeat code**
(verified across all 6 captures). The receiver appears to require the
repeat for the press to register reliably — single-frame transmissions
get ignored. So `to_command()` defaults to `repeat_count=1`.
"""

from __future__ import annotations

from enum import IntEnum

try:
    # infrared-protocols >= 3.0 — split into commands/ subpackage
    from infrared_protocols.commands.nec import NECCommand
except ImportError:
    # infrared-protocols == 2.0.0 (shipped with HA 2026.4/2026.5) — flat module
    from infrared_protocols.commands import NECCommand  # type: ignore[no-redef]

ADDRESS = 0x00


class HumidifierCommand(IntEnum):
    """Buttons on the humidifier remote."""

    POWER = 0x00          # onoff — toggle button
    INTERMITTENT = 0x01   # intermittent mist mode
    CONTINUOUS = 0x02     # continuous mist mode
    TIMER = 0x08          # cycles through timer presets (1h / 2h / off)
    MIST_LEVEL = 0x09     # bigsmall — toggles between high/low mist
    LIGHT = 0x0A          # night light — toggle

    def to_command(self, repeat_count: int = 1) -> NECCommand:
        """Build the NECCommand for this button press.

        Defaults to ``repeat_count=1`` because this humidifier's receiver
        requires the trailing NEC repeat frame — single-frame presses are
        ignored. See the module docstring for capture analysis.
        """
        return NECCommand(
            address=ADDRESS,
            command=self.value,
            repeat_count=repeat_count,
        )
