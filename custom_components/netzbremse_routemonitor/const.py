"""Constants for the Netzbremse Routemonitor integration."""

# Integration domain
from dataclasses import dataclass

DOMAIN = "netzbremse_routemonitor"

# Configuration keys
CONF_POLLING_INTERVAL = "polling_interval"

# Default values
DEFAULT_POLLING_INTERVAL = 1800  # 30 minutes in seconds
MIN_POLLING_INTERVAL = 30  # 30 seconds
MAX_POLLING_INTERVAL = 7200  # 2 hours


@dataclass
class RouteConfig:
    """Configuration for a single route.

    Attributes:
        route_id: Unique identifier for the route (e.g., "route_1").
        name: Display name for the route device.
        base_url: Base URL endpoint for this route's measurements.
        verify_ssl: Whether to verify SSL certificates for this route. Defaults to True.
    """

    route_id: str
    name: str
    base_url: str
    verify_ssl: bool = True


# ============================================================================
# CENTRAL ROUTE CONFIGURATION - USER CUSTOMIZATION POINT
# ============================================================================
# Replace the placeholder names and URLs below with your actual route
# configurations. Each route will become a separate device in Home Assistant
# with upload and download speed sensors.
#
# SSL Verification:
# By default, SSL certificates are verified (verify_ssl=True).
# To disable SSL verification (required cause some routes fail cert verification with the homeassistant certs),
# set verify_ssl=False:
#
# ============================================================================

ROUTES: list[RouteConfig] = [
    RouteConfig(
        route_id="route_a",
        name="Route A",
        base_url="https://custom-t0.speed.cloudflare.com",
        # I absolutely do not know why this is the only route that fails SSL verification, but it does, so here we are.
        # It also is the only route that uses cloudflare instead of google trust chains.
        verify_ssl=False,
    ),
    RouteConfig(
        route_id="route_b",
        name="Route B",
        base_url="https://custom-t1.speed.cloudflare.com",
    ),
    RouteConfig(
        route_id="route_c",
        name="Route C",
        base_url="https://custom-t2.speed.cloudflare.com",
    ),
    RouteConfig(
        route_id="route_d",
        name="Route D",
        base_url="https://custom-t3.speed.cloudflare.com",
    ),
    RouteConfig(
        route_id="route_e",
        name="Route E",
        base_url="https://custom-t4.speed.cloudflare.com",
    ),
]
