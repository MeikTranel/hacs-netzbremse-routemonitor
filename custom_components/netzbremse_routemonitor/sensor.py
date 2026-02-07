"""Sensor platform for Netzbremse Routemonitor integration."""

from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ROUTES, RouteConfig
from .coordinator import NetzbremseRoutemonitorCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Netzbremse Routemonitor sensors from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry for this integration.
        async_add_entities: Callback to add sensor entities.
    """
    coordinator: NetzbremseRoutemonitorCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create 2 sensors (upload + download) for each of the 5 routes = 10 total sensors
    sensors: list[NetzbremseRoutemonitorSensor] = []
    for route in ROUTES:
        sensors.append(
            NetzbremseRoutemonitorSensor(
                coordinator=coordinator,
                route=route,
                sensor_type="upload",
            )
        )
        sensors.append(
            NetzbremseRoutemonitorSensor(
                coordinator=coordinator,
                route=route,
                sensor_type="download",
            )
        )

    async_add_entities(sensors)
    _LOGGER.debug("Added %d sensors for %d routes", len(sensors), len(ROUTES))


class NetzbremseRoutemonitorSensor(CoordinatorEntity[NetzbremseRoutemonitorCoordinator], SensorEntity):
    """Representation of a route speed sensor.

    Each sensor monitors either upload or download speed for a specific route.
    Sensors are automatically grouped under their route's device.
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DATA_RATE
    _attr_native_unit_of_measurement = UnitOfDataRate.MEGABITS_PER_SECOND
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: NetzbremseRoutemonitorCoordinator,
        route: RouteConfig,
        sensor_type: Literal["upload", "download"],
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data update coordinator.
            route: Configuration for this route.
            sensor_type: Type of speed to monitor ("upload" or "download").
        """
        super().__init__(coordinator)
        self._route = route
        self._sensor_type = sensor_type

        # Set unique ID for this sensor
        self._attr_unique_id = f"netzbremse_{route.route_id}_{sensor_type}"

        # Set sensor name
        self._attr_name = f"{sensor_type.capitalize()} Speed"

    @property
    def native_value(self) -> float | None:
        """Return the current speed value.

        Returns:
            Speed in Mbps, or None if data is unavailable.
        """
        if self.coordinator.data is None:
            return None

        route_data = self.coordinator.data.get(self._route.route_id)
        if route_data is None:
            return None

        return route_data.get(f"{self._sensor_type}_speed")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this route.

        Each route is represented as a separate device in Home Assistant,
        with its upload and download sensors grouped together.

        Returns:
            Device information for this route.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self._route.route_id)},
            name=self._route.name,
            manufacturer="Netzbremse",
            model="Route Monitor",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if coordinator has data and this route's data is present.
        """
        return super().available and self.coordinator.data is not None and self._route.route_id in self.coordinator.data
