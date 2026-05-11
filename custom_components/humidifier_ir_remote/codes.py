"""NEC code table for the IR humidifier remote.

All 6 buttons captured + decoded with valid NEC inverse-byte checksums.
The humidifier uses standard NEC at 38 kHz with address 0x00.

The original remote always emits each press as **frame + NEC repeat code**
(verified across all 6 captures). The receiver appears to require the
repeat for the press to register reliably — single-frame transmissions
get ignored. ``to_command()`` defaults to ``repeat_count=3`` so the
transmission is reliable even when the Broadlink is at the edge of the
humidifier's IR range. Total transmission ≈340 ms, which is still a
"normal tap" duration — no risk of being interpreted as a held press.

If a specific button on your humidifier responds to "hold to fast-cycle"
(some timer buttons do), drop this to 1 or 2.
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

    def to_command(self, repeat_count: int = 3) -> NECCommand:
        """Build the NECCommand for this button press.

        Defaults to ``repeat_count=3``. See the module docstring for the
        rationale (range vs. hold-press tradeoff).
        """
        return NECCommand(
            address=ADDRESS,
            command=self.value,
            repeat_count=repeat_count,
        )
