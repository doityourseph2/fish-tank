# Text DAT body for poll_pending_fish — non-blocking poll (HTTP in background thread).
# Finishes with td.run on main thread: store results, refresh debug_status, run apply_fish_display.

import json
import ssl
import threading
import urllib.error
import urllib.request

import td

_ROOT = op("/project1/fish_tank_poll")
_CFG = _ROOT.op("netlify_config")
NETLIFY_BASE = str(_CFG[0, 0]).strip()
API_KEY = str(_CFG[1, 0]).strip()
POLL_PATH = "/.netlify/functions/pending-fish"
_SSL = ssl._create_unverified_context()


def _fetch_pending():
    url = NETLIFY_BASE.rstrip("/") + POLL_PATH
    req = urllib.request.Request(
        url,
        headers={"x-api-key": API_KEY, "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15, context=_SSL) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _worker():
    try:
        data = _fetch_pending()
        payload = json.dumps(data)
        err = ""
    except urllib.error.HTTPError as e:
        payload = ""
        err = e.read().decode("utf-8", errors="replace")
    except Exception as e:
        payload = ""
        err = str(e)

    def _finish():
        if payload:
            _ROOT.store("last_pending_json", payload)
        else:
            _ROOT.store("last_pending_json", "")
        _ROOT.store("last_poll_error", err)
        nl = chr(10)
        jtrunc = payload[:1200] if payload else ""
        msg = "ERR:" + nl + str(err)[:1200] + nl + nl + "JSON (trunc):" + nl + jtrunc
        _ROOT.op("debug_status").text = msg

        def _apply():
            op("/project1/fish_tank_poll/apply_fish_display").run()

        td.run(_apply, delayFrames=1)

    td.run(_finish, delayFrames=1)


threading.Thread(target=_worker, daemon=True).start()
