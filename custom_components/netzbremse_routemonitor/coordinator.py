"""Data update coordinator for Netzbremse Routemonitor integration.

Uses the vendored CloudflareSpeedtest library to run periodic speed tests
against Cloudflare's edge network for each configured route, measuring
download/upload throughput, latency, and jitter.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import httpx

from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .cloudflarepycli.cloudflare import CloudflareSpeedtest, SuiteResults
from .const import DOMAIN, ROUTES, RouteConfig

_LOGGER = logging.getLogger(__name__)


class NetzbremseRoutemonitorCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator that runs Cloudflare speed tests for each route periodically.

    Results are stored as a nested dict keyed by route_id:
        {
            "route_a": {download_speed, upload_speed, latency, jitter, isp, ...},
            "route_b": {...},
            ...
        }
    All speed values are in Mbps.
    """

    def __init__(self, hass: HomeAssistant, polling_interval: int) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            polling_interval: Update interval in seconds.
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )
        _LOGGER.debug(
            "Coordinator initialized with %d second polling interval for %d routes",
            polling_interval,
            len(ROUTES),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Run a Cloudflare speed test per route and return keyed results."""
        data: dict[str, dict[str, Any]] = {}
        for route in ROUTES:
            try:
                _LOGGER.debug("Starting speed test for route %s (%s)", route.name, route.base_url)
                raw: SuiteResults = await self._run_speedtest(route, self.hass)
                flat = self._flatten_results(raw)
                flat["route_name"] = route.name
                data[route.route_id] = flat
                _LOGGER.debug(
                    "Route %s complete: down=%.2f Mbps, up=%.2f Mbps, latency=%.2f ms",
                    route.name,
                    flat.get("download_speed", 0) or 0,
                    flat.get("upload_speed", 0) or 0,
                    flat.get("latency", 0) or 0,
                )
            except Exception as err:
                _LOGGER.error("Speed test failed for route %s: %s", route.name, err)
                raise UpdateFailed(f"Speed test failed for route {route.name}: {err}") from err
        return data

    async def _run_speedtest(self, route: RouteConfig, hass: HomeAssistant) -> SuiteResults:
        """Execute the Cloudflare speed test for a single route."""
        if route.verify_ssl:
            # Use Home Assistant's managed client with SSL verification
            async with get_async_client(hass) as session:
                speedtest = CloudflareSpeedtest(session=session, base_url=route.base_url)
                return await speedtest.run_all(megabits=True)
        else:
            # Create custom client with SSL verification disabled for this route
            _LOGGER.warning(
                "SSL verification disabled for route %s (%s) - use with caution!",
                route.name,
                route.base_url,
            )
            async with httpx.AsyncClient(verify=False) as session:
                speedtest = CloudflareSpeedtest(session=session, base_url=route.base_url)
                return await speedtest.run_all(megabits=True)

    @staticmethod
    def _flatten_results(results: SuiteResults) -> dict[str, Any]:
        """Convert SuiteResults into a flat dict suitable for sensors.

        Extracts the 90th-percentile download/upload speeds (Mbps),
        latency (ms), jitter (ms), and metadata fields.
        """
        tests = results.get("tests", {})
        meta = results.get("meta", {})

        def _val(d: dict, key: str) -> Any:
            entry = d.get(key)
            if entry is None:
                return None
            # TestResult is a NamedTuple with .value as first field
            return entry.value if hasattr(entry, "value") else entry

        return {
            "download_speed": _val(tests, "90th_percentile_down_mbps"),
            "upload_speed": _val(tests, "90th_percentile_up_mbps"),
            "latency": _val(tests, "latency"),
            "jitter": _val(tests, "jitter"),
            "isp": _val(tests, "isp"),
            "ip": _val(meta, "ip"),
            "location_code": _val(meta, "location_code"),
            "location_city": _val(meta, "location_city"),
            "location_region": _val(meta, "location_region"),
        }
