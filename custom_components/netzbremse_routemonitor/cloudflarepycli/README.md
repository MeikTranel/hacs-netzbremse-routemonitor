# cloudflarepycli

The `CloudflareSpeedtest` class from `cloudflarepycli` provides a
well-structured, tested implementation of the Cloudflare speed-test protocol.
Vendoring the single source file (instead of depending on the full CLI package)
keeps the integration lightweight and avoids pulling in CLI-only entry points
that are irrelevant inside Home Assistant.

## cfspeedtest/cloudflare.py

| Field       | Value                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------|
| **Source**  | [martinbrose/cloudflarepycli](https://github.com/martinbrose/cloudflarepycli)                                 |
| **File**    | `cloudflare.py`                                                                                               |
| **Commit**  | `c13517b9d9031c4ec1552a76c848e36ba2dd094f` (2024-11-13)                                                       |
| **License** | GNU General Public License v3.0 ([LICENSE](https://github.com/martinbrose/cloudflarepycli/blob/main/LICENSE)) |
| **Author**  | Martin Brose ([@martinbrose](https://github.com/martinbrose))                                                 |

## Changes

* Switched to aiohttp to leverage homeassistant apis
* Enabled passing in custom baseurls
* let ruff do it's thing - i don't make the rules
