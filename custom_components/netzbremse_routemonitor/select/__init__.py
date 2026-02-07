"""Select platform for netzbremse_routemonitor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.netzbremse_routemonitor.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.select import SelectEntityDescription

from .fan_speed import ENTITY_DESCRIPTIONS as FAN_SPEED_DESCRIPTIONS, NetzbremseRoutemonitorFanSpeedSelect

if TYPE_CHECKING:
    from custom_components.netzbremse_routemonitor.data import NetzbremseRoutemonitorConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (*FAN_SPEED_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetzbremseRoutemonitorConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        NetzbremseRoutemonitorFanSpeedSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in FAN_SPEED_DESCRIPTIONS
    )
