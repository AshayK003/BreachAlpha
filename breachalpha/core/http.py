"""Shared HTTP session utilities.

Provides a curl_cffi session that impersonates Chrome browser to bypass
TLS fingerprinting blocks. Falls back to requests.Session if curl_cffi
is not installed.
"""

from __future__ import annotations

import requests


def get_browser_session():
    """Get a curl_cffi session that impersonates Chrome browser.

    Returns:
        Tuple of (session, is_curl_cffi) where is_curl_cffi indicates
        whether the session uses curl_cffi (True) or plain requests (False).
    """
    try:
        from curl_cffi import requests as curl_requests
        session = curl_requests.Session(impersonate="chrome")
        return session, True
    except ImportError:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        })
        return session, False
