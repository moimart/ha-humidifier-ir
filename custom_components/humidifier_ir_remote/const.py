"""Constants for the Humidifier IR Remote integration."""

from __future__ import annotations

DOMAIN = "humidifier_ir_remote"

CONF_TRANSMITTER = "transmitter"
CONF_NAME = "name"

MODE_CONTINUOUS = "continuous"
MODE_INTERMITTENT = "intermittent"
AVAILABLE_MODES: list[str] = [MODE_CONTINUOUS, MODE_INTERMITTENT]
