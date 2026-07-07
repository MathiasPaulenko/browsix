# Stealth Mode

wavexis includes an anti-bot stealth mode that hides headless browser indicators, useful for scraping protected sites that detect automated browsers.

## Usage

Enable stealth mode with the global `--stealth` flag:

```bash
wavexis --stealth screenshot https://example.com -o out.png
wavexis --stealth scrape https://protected-site.com --selector "article"
wavexis --stealth multi actions.yml
```

## What it hides

Stealth mode injects JavaScript at browser launch that patches the following detection vectors:

| Vector | What it does |
|--------|-------------|
| `navigator.webdriver` | Sets to `undefined` |
| `navigator.plugins` | Fakes common plugins (Chrome PDF, Flash) |
| `navigator.mimeTypes` | Fakes MIME types matching plugins |
| `navigator.languages` | Sets to `["en-US", "en"]` |
| `window.chrome` | Fakes `chrome.runtime` object |
| `Permissions API` | Overrides `navigator.permissions.query` |
| `WebGL vendor/renderer` | Fakes `Intel Inc.` / `Intel Iris OpenGL Engine` |
| `navigator.connection` | Fakes `effectiveType: "4g"` |
| `hardwareConcurrency` | Sets to `4` |
| `deviceMemory` | Sets to `8` |
| `navigator.platform` | Sets to `Win32` |

## Programmatic use

```python
from wavexis.config import BrowserOptions

opts = BrowserOptions(stealth=True)
```

## Backend support

| Backend | Implementation |
|---------|---------------|
| CDP | `Runtime.evaluate` on launch |
| BiDi | `script.evaluate` on launch |

Both backends inject the same stealth JS payload. The JS is defined in `wavexis.actions.stealth` and can be retrieved with `get_stealth_js()`.
