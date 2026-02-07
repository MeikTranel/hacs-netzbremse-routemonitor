# Vendored Dependencies

This directory contains third-party source files vendored into the project.
Vendored files are kept **unmodified** from their upstream sources to simplify
auditing and future updates.

## cfspeedtest/cloudflare.py

| Field       | Value                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------|
| **Source**  | [martinbrose/cloudflarepycli](https://github.com/martinbrose/cloudflarepycli)                                 |
| **File**    | `cloudflare.py`                                                                                               |
| **Commit**  | `c13517b9d9031c4ec1552a76c848e36ba2dd094f` (2024-11-13)                                                       |
| **License** | GNU General Public License v3.0 ([LICENSE](https://github.com/martinbrose/cloudflarepycli/blob/main/LICENSE)) |
| **Author**  | Martin Brose ([@martinbrose](https://github.com/martinbrose))                                                 |

### Why vendored?

The `CloudflareSpeedtest` class from `cloudflarepycli` provides a
well-structured, tested implementation of the Cloudflare speed-test protocol.
Vendoring the single source file (instead of depending on the full CLI package)
keeps the integration lightweight and avoids pulling in CLI-only entry points
that are irrelevant inside Home Assistant.

### Updating

To update the vendored file:

```bash
# 1. Download the latest version
curl -o custom_components/netzbremse_routemonitor/vendor/cfspeedtest/cloudflare.py \
  https://raw.githubusercontent.com/martinbrose/cloudflarepycli/main/cfspeedtest/cloudflare.py

# 2. Update the commit SHA in this README

# 3. Run tests to verify compatibility
./script/test -v
```

### License implications

`cloudflarepycli` is licensed under **GPLv3**. Because this file is included in
the project, this entire integration is also distributed under **GPLv3**.
See the root [LICENSE](../../../LICENSE) and [NOTICE](../../../NOTICE) files.
