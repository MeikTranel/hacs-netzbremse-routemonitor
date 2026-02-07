"""Tests for the vendored cfspeedtest library and the coordinator's result handling."""

from __future__ import annotations

import requests_mock as rm

from custom_components.netzbremse_routemonitor.cloudflarepycli.cloudflare import (
    CloudflareSpeedtest,
    TestResult,
)
from custom_components.netzbremse_routemonitor.coordinator import (
    NetzbremseRoutemonitorCoordinator,
)

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://speed.cloudflare.com"

FAKE_META = {
    "clientIp": "203.0.113.42",
    "asOrganization": "Example ISP",
    "colo": "FRA",
    "region": "Europe",
    "city": "Frankfurt",
}

SERVER_TIMING_HEADER = "cfRequestDuration;dur=12.5,other;dur=1"


class TestFlattenResults:
    """Test the coordinator helper that transforms SuiteResults for sensors."""

    @staticmethod
    def _make_suite_results() -> dict:
        """Build a realistic SuiteResults dict."""
        return {
            "tests": {
                "90th_percentile_down_mbps": TestResult(95.5),
                "90th_percentile_up_mbps": TestResult(42.1),
                "latency": TestResult(12.34),
                "jitter": TestResult(1.23),
                "isp": TestResult("Example ISP"),
            },
            "meta": {
                "ip": TestResult("203.0.113.42"),
                "location_code": TestResult("FRA"),
                "location_city": TestResult("Frankfurt"),
                "location_region": TestResult("Europe"),
            },
        }

    def test_all_keys_present(self):
        flat = NetzbremseRoutemonitorCoordinator._flatten_results(self._make_suite_results())
        expected_keys = {
            "download_speed",
            "upload_speed",
            "latency",
            "jitter",
            "isp",
            "ip",
            "location_code",
            "location_city",
            "location_region",
        }
        assert set(flat.keys()) == expected_keys

    def test_values_extracted(self):
        flat = NetzbremseRoutemonitorCoordinator._flatten_results(self._make_suite_results())
        assert flat["download_speed"] == 95.5
        assert flat["upload_speed"] == 42.1
        assert flat["latency"] == 12.34
        assert flat["jitter"] == 1.23
        assert flat["isp"] == "Example ISP"
        assert flat["ip"] == "203.0.113.42"

    def test_missing_keys_return_none(self):
        empty: dict = {"tests": {}, "meta": {}}
        flat = NetzbremseRoutemonitorCoordinator._flatten_results(empty)
        assert flat["download_speed"] is None
        assert flat["upload_speed"] is None
        assert flat["latency"] is None

    def test_completely_empty_results(self):
        flat = NetzbremseRoutemonitorCoordinator._flatten_results({})
        assert flat["download_speed"] is None


# ---------------------------------------------------------------------------
#  Custom base_url tests
# ---------------------------------------------------------------------------


class TestCustomBaseUrl:
    """Verify that CloudflareSpeedtest respects a custom base_url."""

    def test_two_instances_different_urls(self, requests_mock: rm.Mocker):
        """Two instances with different base_urls hit different endpoints."""
        url_a = "https://custom-t0.speed.cloudflare.com"
        url_b = "https://custom-t1.speed.cloudflare.com"

        meta_a = {**FAKE_META, "colo": "FRA"}
        meta_b = {**FAKE_META, "colo": "AMS"}

        requests_mock.get(f"{url_a}/meta", json=meta_a)
        requests_mock.get(f"{url_b}/meta", json=meta_b)

        # Each instance should hit its own /meta endpoint
        st_a = CloudflareSpeedtest(base_url=url_a)
        assert st_a.metadata().location_code == "FRA"

        st_b = CloudflareSpeedtest(base_url=url_b)
        assert st_b.metadata().location_code == "AMS"
