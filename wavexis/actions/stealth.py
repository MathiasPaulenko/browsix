"""Anti-bot stealth mode for evading headless detection.

Injects JavaScript to hide common headless indicators:
- navigator.webdriver
- navigator.plugins / navigator.mimeTypes
- window.chrome runtime
- navigator.languages
- Permissions API
- WebGL vendor/renderer
- navigator.connection
"""

from __future__ import annotations

STEALTH_JS = """(() => {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {name: 'Chrome PDF Plugin'},
            {name: 'Chrome PDF Viewer'},
            {name: 'Native Client'},
        ],
    });

    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });

    Object.defineProperty(navigator, 'mimeTypes', {
        get: () => [
            {type: 'application/pdf', suffixes: 'pdf'},
            {type: 'application/x-google-chrome-pdf', suffixes: 'pdf'},
        ],
    });

    window.chrome = window.chrome || {};
    window.chrome.runtime = window.chrome.runtime || {};

    const originalQuery = window.navigator.permissions
        ? window.navigator.permissions.query.bind(window.navigator.permissions)
        : null;
    if (originalQuery) {
        window.navigator.permissions.query = (params) => {
            if (params.name === 'notifications') {
                return Promise.resolve({state: Notification.permission});
            }
            return originalQuery(params);
        };
    }

    try {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.call(this, param);
        };
    } catch(e) {}

    Object.defineProperty(navigator, 'connection', {
        get: () => ({
            effectiveType: '4g',
            rtt: 50,
            downlink: 10,
            saveData: false,
        }),
    });

    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 4,
    });

    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8,
    });

    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32',
    });
})()"""


def get_stealth_js() -> str:
    """Return the stealth JavaScript injection string.

    Returns:
        JavaScript code that patches navigator and window properties
        to hide headless browser indicators.
    """
    return STEALTH_JS
