"""Run a live Cloudflare speed test and print the results.

Run directly from the IDE (e.g. right-click → "Run Python File")
or from the terminal:
    python custom_components/netzbremse_routemonitor/cloudflarepycli/live_speedtest.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import aiohttp

# Ensure the project root is on sys.path so custom_components can be imported.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from custom_components.netzbremse_routemonitor.cloudflarepycli.cloudflare import (
    SINGLEBIGDOWNLOAD,
    CloudflareSpeedtest,
)
from custom_components.netzbremse_routemonitor.coordinator import (
    NetzbremseRoutemonitorCoordinator,
)


async def main() -> None:
    # Use a small subset to keep runtime reasonable (~10-15 s)

    print("Running live Cloudflare speed test …")
    async with aiohttp.ClientSession() as session:
        st = CloudflareSpeedtest(
            tests=SINGLEBIGDOWNLOAD, base_url="https://custom-t0.speed.cloudflare.com", session=session
        )
        results = await st.run_all(megabits=True)
        print(results)
        flat = NetzbremseRoutemonitorCoordinator._flatten_results(results)

        print("\n--- Live Speed Test Results ---")
        for k, v in flat.items():
            print(f"  {k}: {v}")
        print("------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
