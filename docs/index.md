# browsix

Browser automation CLI — wraps [cdpwave](https://pypi.org/project/cdpwave/) and [bidiwave](https://pypi.org/project/bidiwave/).

No Node.js. No Chromium download. Uses your existing Chrome/Edge installation.

---

# Overview

## Features

- **Screenshot** — full page, viewport, or element selector
- **PDF** — generate PDFs with paper size, orientation, margins
- **Eval** — evaluate JavaScript expressions on any page
- **Scrape** — batch scrape multiple URLs with a single expression
- **DOM** — get, query, set attributes, remove elements, scroll
- **HAR** — capture network traffic as HAR 1.2
- **Cookies** — get, set, delete, clear cookies
- **Tabs** — list, create, close, activate tabs
- **Console/Logs** — capture console messages and browser logs
- **Emulation** — device presets, viewport, geolocation, timezone, dark mode
- **Multi** — execute multiple actions from a YAML config file
- **Backends** — CDP (cdpwave) or WebDriver BiDi (bidiwave)
- **Raw Protocol** — escape hatch for direct CDP/BiDi commands
- **Experimental** — WebAuthn, WebAudio, Media, Cast, Bluetooth

---

# Quickstart

## 1. Install

```bash
pip install browsix[cdp]
```

This installs browsix with the CDP backend (cdpwave). You also need Chrome or Edge installed on your system.

## 2. First screenshot

```bash
browsix screenshot https://example.com -o out.png
```

Output: `Screenshot saved to out.png`

## 3. First PDF

```bash
browsix pdf https://example.com -o out.pdf --paper a4
```

Output: `PDF saved to out.pdf`

## 4. First eval

```bash
browsix eval https://example.com -e "document.title"
```

Output: `"Example Domain"`

## 5. Multi-action

Create a YAML config `actions.yml`:

```yaml
actions:
  - screenshot:
      url: https://example.com
      full_page: true
  - eval:
      url: https://example.com
      expression: document.title
```

Run it:

```bash
browsix multi actions.yml
```

## 6. Device emulation

```bash
browsix emulation device https://example.com --device iphone-15 -o mobile.png
```

---

# Installation

## pip

```bash
pip install browsix[cdp]
```

To use the WebDriver BiDi backend instead:

```bash
pip install browsix[bidi]
```

Both backends:

```bash
pip install browsix[cdp,bidi]
```

## pipx

For isolated installation:

```bash
pipx install browsix[cdp]
```

## Shell completions

browsix uses Typer's built-in completion support. Install completions for your shell:

```bash
browsix completions bash
browsix completions zsh
browsix completions fish
browsix completions powershell
```

## Requirements

- Python >= 3.11
- Chrome or Edge browser installed on your system
- cdpwave (for CDP backend) or bidiwave (for BiDi backend)

## Verify installation

```bash
browsix --version
browsix install_check
```

---

# Commands

## Global flags

| Flag | Description |
|------|-------------|
| `--backend cdp\|bidi` | Preferred backend |
| `--verbose, -v` | Show backend logs and timing info |
| `--quiet, -q` | Suppress all output except errors |
| `--version` | Print browsix version and exit |

## screenshot

Take a screenshot of a web page.

```bash
browsix screenshot <url> [options]
```

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `--full-page` | Capture full page, not just viewport |
| `--selector` | CSS selector to capture |
| `--device` | Device preset name |
| `--format` | Image format (png or jpeg) |
| `--js` | JavaScript to execute before screenshot |
| `--wait-for` | CSS selector to wait for |

## pdf

Generate a PDF of a web page.

```bash
browsix pdf <url> [options]
```

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `--paper` | Paper size (a4, letter, legal, a3, a5) |
| `--landscape` | Use landscape orientation |
| `--margins` | Margin size (e.g. 0.4in) |
| `--media` | CSS media type (print or screen) |
| `--no-header-footer` | Omit header and footer |

## eval

Evaluate a JavaScript expression on a web page.

```bash
browsix eval <url> [options]
```

| Option | Description |
|--------|-------------|
| `-e, --expression` | JavaScript expression to evaluate |
| `-o, --output` | Output file path (JSON) |
| `--await-promise` | Await a returned Promise |
| `--file` | Read expression from file |

## navigate

Navigate to a URL and optionally wait for an element.

```bash
browsix navigate <url> [options]
```

## back / forward / reload / stop

Browser history navigation commands.

```bash
browsix back
browsix forward
browsix reload [--ignore-cache]
browsix stop
```

## tabs

Manage browser tabs.

```bash
browsix tabs <action> [options]
```

Actions: `list`, `new`, `close`, `activate`

## console

Capture console messages from a web page.

```bash
browsix console <url> [options]
```

## logs

Capture browser log entries.

```bash
browsix logs <url> [options]
```

## dom

DOM operations on a web page.

```bash
browsix dom <url> [options]
```

Actions: `get`, `query`, `attr`, `remove_attr`, `remove`, `focus`, `scroll`

## scrape

Scrape multiple URLs by evaluating a JS expression on each.

```bash
browsix scrape <urls...> [options]
```

## har

Capture network traffic as HAR 1.2.

```bash
browsix har <url> [options]
```

## cookies

Manage browser cookies.

```bash
browsix cookies <action> [options]
```

Actions: `get`, `set`, `delete`, `clear`

## headers

Set extra HTTP headers for all requests.

```bash
browsix headers '<json>'
```

## user-agent

Override the browser's User-Agent string.

```bash
browsix user-agent <ua>
```

## browser

Browser management commands.

```bash
browsix browser <action>
```

Actions: `version`, `new_context`, `list_contexts`

## devices

List available device presets.

```bash
browsix devices
```

## multi

Execute multiple actions from a YAML config file.

```bash
browsix multi <config>
```

## backends

List available backends.

```bash
browsix backends
```

## install_check

Check which backends are installed and their versions.

```bash
browsix install_check
```

## emulation

Emulation subcommands.

```bash
browsix emulation device <url> --device <name> [-o output]
browsix emulation viewport <url> --width <w> --height <h> [-o output]
browsix emulation geolocation <url> --lat <lat> --lon <lon> [-o output]
browsix emulation timezone <url> --tz <timezone> [-o output]
browsix emulation dark_mode <url> [-o output]
```

## completions

Install shell completions.

```bash
browsix completions <shell>
```

Shells: `bash`, `zsh`, `fish`, `powershell`

---

# Multi Config

The `multi` command lets you execute multiple actions from a single YAML config file.

## Usage

```bash
browsix multi <config.yml>
```

## Config format

The YAML file must have an `actions` key containing a list of action entries. Each entry is a dict with a single key (the action type) and a dict of parameters.

```yaml
actions:
  - screenshot:
      url: https://example.com
      full_page: true
  - pdf:
      url: https://example.com
      paper: a4
  - eval:
      url: https://example.com
      expression: document.title
  - dom:
      url: https://example.com
      action: get
      selector: h1
  - navigate:
      url: https://example.org
  - scrape:
      urls:
        - https://example.com
        - https://example.org
      expression: document.title
```

## Supported actions

| Action | Parameters |
|--------|------------|
| `screenshot` | `url`, `full_page`, `format` |
| `pdf` | `url`, `paper` |
| `eval` | `url`, `expression` |
| `dom` | `url`, `action`, `selector` |
| `navigate` | `url` |
| `scrape` | `urls`, `expression` |

## Validation errors

Invalid config files raise `MultiConfigError` with exit code 2:

- Missing `actions` key
- `actions` is not a list
- Action entry has multiple keys
- Action parameters are not a dict
- Unknown action type

---

# Backends

browsix supports two backends via separate packages:

## CDP backend (cdpwave)

The default and most feature-complete backend. Uses the Chrome DevTools Protocol.

```bash
pip install browsix[cdp]
```

**Supported features:**

- Screenshots (full page, selector, device)
- PDF generation
- JavaScript evaluation
- DOM operations
- HAR capture
- Cookies, headers, user-agent
- Tab management
- Console/log capture
- Device emulation, viewport, geolocation, timezone, dark mode
- Browser contexts
- WebAuthn, WebAudio, Media, Cast, Bluetooth (experimental)

## BiDi backend (bidiwave)

WebDriver BiDi backend. Uses the WebDriver BiDi protocol.

```bash
pip install browsix[bidi]
```

**Supported features:**

- `launch`, `navigate`, `screenshot`, `eval`, `raw`, `close`
- `go_back`, `go_forward`, `reload`, `stop_loading`, `wait_for`
- `list_tabs`, `new_tab`, `close_tab`
- DOM methods, storage methods
- `new_context`, `list_contexts`, `close_context`
- `get_window_bounds`, `set_window_bounds`
- `dialog_accept`, `dialog_dismiss`
- `grant_permission`, `reset_permissions`
- `click`, `type_text`, `fill`, `select_option`, `hover`, `key_press`, `drag`, `tap`
- `block_requests`, `intercept_requests`

**Not supported (raises `NotImplementedError`):**

- All emulation methods
- HAR capture
- Cookies, headers
- PDF generation
- Performance profiling
- Accessibility
- Service workers, animations

## Selecting a backend

Use the `--backend` global flag:

```bash
browsix --backend cdp screenshot https://example.com -o out.png
browsix --backend bidi screenshot https://example.com -o out.png
```

## Checking installation

```bash
browsix install_check
```

Output:

```
  cdp: 2.0.1
  bidi: not installed
```

## Listing available backends

```bash
browsix backends
```

---

# Raw Protocol Access

The `raw` command is an escape hatch for sending protocol commands directly to the browser backend. It works with both CDP and BiDi backends.

## Usage

```bash
browsix raw <method> [params] [--backend cdp|bidi] [-o output]
```

- **method**: Protocol method name (e.g. `Page.reload`, `browsingContext.navigate`)
- **params**: JSON string with command parameters (default: `{}`)
- **--backend**: Choose backend (`cdp` or `bidi`). Defaults to CDP.
- **-o, --output**: Output file path (`-` for stdout, default)

## CDP Raw Commands

```bash
# Reload the page ignoring cache
browsix raw "Page.reload" '{"ignoreCache": true}'

# Get system info
browsix raw "SystemInfo.getInfo" '{}'

# Enable a specific domain
browsix raw "Network.enable" '{}'

# Get all cookies
browsix raw "Network.getCookies" '{}'
```

## BiDi Raw Commands

```bash
# Navigate to a URL via BiDi
browsix raw --backend bidi "browsingContext.navigate" '{"context": "id", "url": "https://example.com"}'

# Get browsing context tree
browsix raw --backend bidi "browsingContext.getTree" '{}'

# Subscribe to log events
browsix raw --backend bidi "session.subscribe" '{"events": ["log.entryAdded"]}'
```

## Notes

- The `raw` command launches a headless browser, sends the command, and closes the browser.
- Params must be valid JSON. Invalid JSON will result in an error.
- The result is printed as JSON to stdout (or saved to a file with `-o`).
- Use `raw` when browsix doesn't have a dedicated command for a protocol feature.

---

# Troubleshooting

## Chrome not found

**Error:** `BackendNotAvailableError` or Chrome fails to launch.

**Solution:** Ensure Chrome or Edge is installed on your system.

- Windows: Check `C:\Program Files\Google\Chrome\Application\chrome.exe`
- macOS: Check `/Applications/Google Chrome.app`
- Linux: Install via `sudo apt install google-chrome-stable`

## Backend not available

**Error:** `No backend available. Install cdpwave: pip install browsix[cdp]`

**Solution:** Install the CDP backend:

```bash
pip install browsix[cdp]
```

## Navigation timeout

**Error:** `Timeout waiting for ...`

**Solution:** Increase the wait time or use a different wait strategy:

```bash
browsix screenshot https://slow-site.com --wait-for "body"
```

## Element not found

**Error:** `Element not found: <selector>`

**Solution:** Verify the CSS selector exists on the page. Use `--wait-for` to wait for the element before acting.

## BiDi driver issues

**Error:** `ImportError: bidiwave is not installed`

**Solution:** Install the BiDi backend:

```bash
pip install browsix[bidi]
```

## Multi config errors

**Error:** `Invalid multi config field '...'`

**Solution:** Check your YAML config:

1. Must have an `actions` key with a list
2. Each action is a dict with a single key
3. Action parameters must be a dict
4. Action type must be one of: screenshot, pdf, eval, dom, navigate, scrape

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Browser error (navigation, timeout, element not found) |
| 2 | Config error (invalid multi YAML) |
| 3 | Backend not available |

---

# Contributing

## Setup

```bash
git clone https://github.com/MathiasPaulenko/browsix.git
cd browsix
pip install -e ".[dev,cdp]"
```

## Running tests

```bash
# Unit tests
pytest tests/unit/ -m unit -v

# Integration tests (requires Chrome)
pytest tests/integration/ -m integration -v

# All tests
pytest tests/ -v
```

## Code style

- **Linter:** ruff
- **Type checker:** mypy (strict mode)
- **Line length:** 100 chars
- **Python:** >= 3.11

```bash
ruff check .
mypy browsix/ --ignore-missing-imports
```

## PR process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Run linters: `ruff check .` and `mypy browsix/ --ignore-missing-imports`
6. Commit with conventional commits: `feat: add new command`, `fix: resolve timeout bug`
7. Push and open a PR

## Project structure

```
browsix/
  browsix/
    actions/     # Action classes (screenshot, pdf, eval, etc.)
    backend/     # Backend implementations (cdp, bidi, manager)
    cli/         # Typer CLI app
    config.py    # Dataclasses and presets
    exceptions.py
    multi.py     # YAML multi-action parser
    output.py    # Output helpers
  tests/
    unit/        # Unit tests (mocked)
    integration/ # Integration tests (real Chrome)
  docs/          # mkdocs documentation
```

## Releasing

Releases are automated via GitHub Actions:

1. Tag a release: `git tag v1.0.1`
2. Push the tag: `git push origin v1.0.1`
3. CI builds the package and publishes to PyPI
