"""
TouchDesigner: poll pending fish from Netlify (used in a Script DAT or Execute DAT).

Set the constants below or drive them from Table DAT / custom parameters.
Requires Python 3 standard library only (urllib).

Returns JSON: { "fish": [ { "id", "display_name", "texture_url", ... } ] }
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

# --- edit for your deployment ---
NETLIFY_BASE = "https://YOUR_SITE.netlify.app"
API_KEY = "same-as-FISH_TANK_API_KEY-on-Netlify"
POLL_PATH = "/.netlify/functions/pending-fish"


def fetch_pending_fish() -> object:
    url = NETLIFY_BASE.rstrip("/") + POLL_PATH
    req = urllib.request.Request(
        url,
        headers={"x-api-key": API_KEY, "Accept": "application/json"},
        method="GET",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


# Example: call from Execute DAT after storing result in parent().var('pending_json', ...)
if __name__ == "__main__":
    try:
        data = fetch_pending_fish()
        print(json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code, e.read().decode("utf-8", errors="replace"))
    except urllib.error.URLError as e:
        print("URL error:", e.reason)
