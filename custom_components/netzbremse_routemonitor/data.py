"""Custom types for netzbremse_routemonitor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import NetzbremseRoutemonitorApiClient
    from .coordinator import NetzbremseRoutemonitorDataUpdateCoordinator


type NetzbremseRoutemonitorConfigEntry = ConfigEntry[NetzbremseRoutemonitorData]


@dataclass
class NetzbremseRoutemonitorData:
    """Data for netzbremse_routemonitor."""

    client: NetzbremseRoutemonitorApiClient
    coordinator: NetzbremseRoutemonitorDataUpdateCoordinator
    integration: Integration
