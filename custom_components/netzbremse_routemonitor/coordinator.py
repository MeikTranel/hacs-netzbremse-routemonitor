"""Data update coordinator for Netzbremse Routemonitor integration."""

import logging
import time
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, ROUTES

_LOGGER = logging.getLogger(__name__)


class NetzbremseRoutemonitorCoordinator(DataUpdateCoordinator[dict[str, dict[str, float]]]):
    """Class to manage fetching data from routes.

    This coordinator periodically fetches speed measurements for all configured routes.
    The update interval is configurable via the integration's config flow.
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
        _LOGGER.debug("Coordinator initialized with %d second polling interval", polling_interval)

    async def _async_update_data(self) -> dict[str, dict[str, float]]:
        """Fetch data from all routes."""
        results: dict[str, dict[str, float]] = {}

        try:
            for route in ROUTES:
                _LOGGER.debug("Measuring route %s at %s", route.name, route.base_url)

                # Measure upload and download speeds for this route
                upload_speed, download_speed = await self._measure_route(route.base_url)

                results[route.route_id] = {
                    "upload_speed": upload_speed,
                    "download_speed": download_speed,
                }

            _LOGGER.debug("Successfully fetched data for %d routes", len(results))

        except Exception as err:
            _LOGGER.error("Error updating route data: %s", err)
            raise UpdateFailed(f"Error communicating with routes: {err}") from err

        return results

    async def _measure_route(self, route_url: str, bytes_to_transfer: int = 10_000_000) -> tuple[float, float]:
        """Measure upload and download speeds for a single route.

        Args:
            route_url: Base URL of the route endpoint.
            bytes_to_transfer: Number of bytes to transfer for testing (default: 10MB).

        Returns:
            Tuple of (upload_speed, download_speed) in Mbps.
        """
        upload_speed = 0.0
        download_speed = 0.0

        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            upload_speed = await self._measure_upload(session, route_url)
            download_speed = await self._measure_download(session, route_url)

        return (upload_speed, download_speed)

    async def _measure_download(
        self, session: aiohttp.ClientSession, base_url: str, bytes_to_transfer: int = 10_000_000
    ) -> float:
        """Measure download speed for a route."""
        try:
            download_url = f"{base_url}/__down?bytes={bytes_to_transfer}"
            start_time = time.time()

            async with session.get(download_url) as response:
                # Read and discard the downloaded bytes
                async for _ in response.content.iter_any():
                    pass

            elapsed_time = time.time() - start_time

            if elapsed_time > 0:
                # Calculate download speed in Mbps: (bytes * 8 bits/byte) / (time_seconds * 1_000_000)
                download_speed = calculate_speed(bytes_to_transfer, elapsed_time)
                _LOGGER.debug(
                    "Download: %d bytes in %.2f seconds = %.2f Mbps",
                    bytes_to_transfer,
                    elapsed_time,
                    download_speed,
                )
                return download_speed
        except Exception as err:
            _LOGGER.warning("Download speed test failed for %s: %s", base_url, err)

        return 0.0

    async def _measure_upload(self, session: aiohttp.ClientSession, base_url: str) -> float:
        """Measure upload speed for a route."""
        try:
            upload_url = f"{base_url}/__up"
            # Create a stream of zeros
            transfer_size = 10_000_000
            upload_data = b"\x00" * transfer_size  # 10MB of zeros

            start_time = time.time()

            async with session.post(upload_url, data=upload_data) as response:
                # Wait for the upload to complete
                await response.read()

            elapsed_time = time.time() - start_time

            if elapsed_time > 0:
                upload_speed = calculate_speed(transfer_size, elapsed_time)
                _LOGGER.debug("Upload: %d bytes in %.2f seconds = %.2f Mbps", transfer_size, elapsed_time, upload_speed)
                return upload_speed

        except Exception as err:
            _LOGGER.warning("Upload speed test failed for %s: %s", base_url, err)

        return 0.0


def calculate_speed(bytes_transferred: int, elapsed: float) -> float:
    """Calculate speed in Mbps."""
    if elapsed > 0:
        return (bytes_transferred * 8) / (elapsed * 1000 * 1000)
    return 0.0
