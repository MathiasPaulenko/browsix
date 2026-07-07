# Extensions & Preferences

wavexis provides CLI commands and backend methods for managing browser extensions and browser preferences.

## WebExtension management

### Install an extension

Install from an unpacked extension directory or a `.crx` file:

```bash
# Unpacked directory
wavexis extension-install /path/to/my-extension/

# .crx file
wavexis extension-install /path/to/extension.crx
```

The command returns an extension ID (32-character hex string).

### List installed extensions

```bash
wavexis extension-list
```

Output:

```text
  abc123def456...  My Extension v1.0.0  (enabled)
  def789abc012...  Dark Mode v2.3.1  (disabled)
```

### Uninstall an extension

```bash
wavexis extension-uninstall <extension-id>
```

### Programmatic use

```python
backend = CDPBackend()
await backend.launch(opts)

ext_id = await backend.extension_install("/path/to/extension/")
await backend.extension_list()
await backend.extension_uninstall(ext_id)
```

## Browser preferences

### Get a preference

```bash
wavexis pref-get download.default_directory
```

### Set a preference

```bash
wavexis pref-set download.default_directory /tmp/downloads
```

### Programmatic use

```python
backend = CDPBackend()
await backend.launch(opts)

value = await backend.get_pref("download.default_directory")
await backend.set_pref("download.default_directory", "/tmp/downloads")
```

## Backend support

| Backend | Implementation |
|---------|---------------|
| CDP | `Extensions.loadUnpacked`, `Extensions.load`, `Extensions.uninstall`, `Extensions.getInfo`, `Browser.getPreference`, `Browser.setPreference` |
| BiDi | CDP bridge (`browser.cdp.sendCommand`) for all operations |

Both backends support all extension and preference operations. The BiDi backend uses the CDP bridge since WebDriver BiDi does not yet have native extension or preference APIs.
