# browsix

[![CI](https://github.com/MathiasPaulenko/browsix/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/browsix/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/browsix.svg)](https://pypi.org/project/browsix/)
[![Python](https://img.shields.io/pypi/pyversions/browsix.svg)](https://pypi.org/project/browsix/)
[![License](https://img.shields.io/github/license/MathiasPaulenko/browsix.svg)](https://github.com/MathiasPaulenko/browsix/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://mathiaspaulenko.github.io/browsix/)

> Browser automation CLI — wraps cdpwave and bidiwave. No Node.js, no Chromium download. Uses your existing Chrome/Edge. 80+ commands across CDP and BiDi backends.

## Install

```bash
pip install browsix[cdp]
```

## Quick start

```bash
# Take a screenshot
browsix screenshot https://example.com -o out.png

# Full-page screenshot
browsix screenshot https://example.com -o full.png --full-page

# Screenshot of a specific element
browsix screenshot https://example.com -o el.png --selector "h1"

# Generate a PDF
browsix pdf https://example.com -o out.pdf --paper a4

# Evaluate JavaScript
browsix eval https://example.com -e "document.title"

# Scrape page content
browsix scrape https://example.com --selector "article"

# Emulate a device
browsix device https://example.com --preset iphone-15 -o shot.png
```

## Multi-action

Create a YAML config and run multiple actions in sequence:

```yaml
# actions.yml
actions:
  - screenshot:
      url: https://example.com
      full_page: true
  - eval:
      url: https://example.com
      expression: document.title
  - pdf:
      url: https://example.com
      paper: a4
```

```bash
browsix multi actions.yml
```

## Backends

browsix supports two backends:

- **CDP** (cdpwave) — default, full feature support. `pip install browsix[cdp]`
- **BiDi** (bidiwave) — WebDriver BiDi protocol, 23+ methods implemented. `pip install browsix[bidi]`

Select with `--backend`:

```bash
browsix --backend bidi screenshot https://example.com -o out.png
```

### BiDi backend support

The BiDi backend now supports 23+ methods via bidiwave:

| Category | Methods |
|----------|---------|
| Navigation | `navigate`, `go_back`, `go_forward`, `reload`, `stop_loading`, `wait_for` |
| Screenshots | `screenshot`, `screenshot_selector`, `pdf` |
| Tabs | `list_tabs`, `new_tab`, `close_tab`, `activate_tab` |
| DOM | `dom_get`, `dom_query`, `dom_set_attr`, `dom_get_attr`, `dom_remove_attr`, `dom_remove`, `dom_focus`, `dom_scroll` |
| Cookies | `get_cookies`, `set_cookie`, `delete_cookie`, `clear_cookies` |
| Network | `set_headers`, `set_user_agent`, `block_requests`, `throttle_network`, `set_cache_disabled`, `intercept_requests`, `mock_response` |
| Emulation | `emulate_device`, `set_viewport`, `set_geolocation`, `set_timezone`, `set_dark_mode`, `set_locale`, `set_touch_emulation`, `set_cpu_throttle`, `set_sensors` |
| Browser | `browser_version`, `eval`, `raw`, `capture_console`, `capture_logs` |
| Security | `get_security_state`, `ignore_cert_errors` |
| Contexts | `new_context`, `list_contexts`, `close_context`, `get_window_bounds`, `set_window_bounds` |
| Input | `click`, `type_text`, `fill`, `select_option`, `hover`, `key_press`, `drag`, `tap` |
| Storage | `storage_get`, `storage_set`, `storage_clear`, `storage_list` |
| Dialogs | `dialog_accept`, `dialog_dismiss`, `grant_permission`, `reset_permissions` |

CDP-only features (HAR, screencast, a11y, downloads, performance profiling,
CSS inspection, debugging, DOM snapshot, overlay, cache storage, IndexedDB,
service workers, animations, WebAuthn, WebAudio, Media, Cast, Bluetooth)
require `--backend cdp`.

## Commands

browsix provides 80+ CLI commands organized into categories:

| Category | Commands |
|----------|----------|
| Capture | `screenshot`, `pdf`, `screencast`, `scrape` |
| Navigate | `navigate`, `back`, `forward`, `reload`, `stop`, `tabs` |
| Console | `console`, `logs`, `har` |
| Cookies | `cookies` (get/set/delete/clear) |
| Network | `headers`, `user-agent`, `block`, `throttle`, `cache`, `intercept`, `mock` |
| Browser | `open`, `close`, `version` |
| Emulation | `device`, `viewport`, `geolocation`, `timezone`, `dark-mode` |
| Input | `click`, `type`, `fill`, `select`, `hover`, `key`, `drag`, `tap` |
| CSS | `css-styles`, `css-computed`, `css-rules` |
| Debug | `debug-break`, `debug-step`, `debug-pause`, `debug-resume` |
| Performance | `perf-metrics`, `perf-trace`, `perf-profile`, `perf-coverage` |
| Storage | `storage` (get/set/clear/list), `indexeddb` |
| Advanced | `sw`, `animation`, `record`, `replay`, `webauthn`, `cast`, `bluetooth` |

Run `browsix --help` for the full list.

## Comparison

| Feature | browsix | shot-scraper | Playwright |
|---------|---------|--------------|------------|
| Language | Python | Python | Multi |
| Node.js required | No | Yes | Yes |
| Chromium download | No | Yes | Yes |
| CDP backend | Yes | Yes | Yes |
| BiDi backend | Yes | No | No |
| CLI-first | Yes | Yes | No |
| Multi-action YAML | Yes | No | No |
| Device emulation | Yes | Yes | Yes |
| HAR capture | Yes | No | Yes |
| PDF generation | Yes | Yes | Yes |
| Network throttling | Yes | No | Yes |
| Cookie management | Yes | No | Yes |
| Session recording | Yes | No | No |
| Serve mode (HTTP API) | Yes | No | No |
| Shell completions | Yes | No | No |

## Documentation

Full docs at [mathiaspaulenko.github.io/browsix](https://mathiaspaulenko.github.io/browsix/).

## License

MIT