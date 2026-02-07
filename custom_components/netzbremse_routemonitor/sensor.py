"""Sensor platform for Netzbremse Routemonitor integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ROUTES
from .coordinator import NetzbremseRoutemonitorCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class NetzbremseSpeedtestSensorDescription(SensorEntityDescription):
    """Sensor description with a data-key into the coordinator's flat dict."""

    data_key: str


SENSOR_DESCRIPTIONS: tuple[NetzbremseSpeedtestSensorDescription, ...] = (
    NetzbremseSpeedtestSensorDescription(
        key="download_speed",
        data_key="download_speed",
        translation_key="download_speed",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    NetzbremseSpeedtestSensorDescription(
        key="upload_speed",
        data_key="upload_speed",
        translation_key="upload_speed",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    NetzbremseSpeedtestSensorDescription(
        key="latency",
        data_key="latency",
        translation_key="latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    NetzbremseSpeedtestSensorDescription(
        key="jitter",
        data_key="jitter",
        translation_key="jitter",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    NetzbremseSpeedtestSensorDescription(
        key="isp",
        data_key="isp",
        translation_key="isp",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Netzbremse Routemonitor sensors from a config entry.

    Creates one device per route, each with a full set of speed-test sensors.
    """
    coordinator: NetzbremseRoutemonitorCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NetzbremseSpeedtestSensor] = []
    for route in ROUTES:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                NetzbremseSpeedtestSensor(coordinator, description, entry, route.route_id, route.name)
            )

    async_add_entities(entities)
    _LOGGER.debug("Added %d speed-test sensors across %d routes", len(entities), len(ROUTES))


class NetzbremseSpeedtestSensor(CoordinatorEntity[NetzbremseRoutemonitorCoordinator], SensorEntity):
    """A single metric from the Cloudflare speed test for a specific route."""

    _attr_has_entity_name = True
    entity_description: NetzbremseSpeedtestSensorDescription

    def __init__(
        self,
        coordinator: NetzbremseRoutemonitorCoordinator,
        description: NetzbremseSpeedtestSensorDescription,
        entry: ConfigEntry,
        route_id: str,
        route_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._route_id = route_id
        self._route_name = route_name
        self._attr_unique_id = f"{entry.entry_id}_{route_id}_{description.key}"

    @property
    def native_value(self) -> Any | None:
        """Return the current sensor value."""
        if self.coordinator.data is None:
            return None
        route_data = self.coordinator.data.get(self._route_id)
        if route_data is None:
            return None
        return route_data.get(self.entity_description.data_key)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info — each route is a separate device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._route_id)},
            name=f"Route Monitor – {self._route_name}",
            manufacturer="Netzbremse",
            model="Route Monitor",
        )
