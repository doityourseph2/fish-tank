# Text DAT body: run via op('apply_fish_display').run()
# Main thread: TOP/label updates only. mark-consumed POST runs in a background thread.
# fish_movie is the kiosk texture URL; it also drives the PBR material on fish_mesh_rig (3D path).

import json
import ssl
import threading
import urllib.request

import td

_ROOT = op("/project1/fish_tank_poll")
_CFG = _ROOT.op("netlify_config")
BASE = str(_CFG[0, 0]).strip()
KEY = str(_CFG[1, 0]).strip()
_SSL = ssl._create_unverified_context()


def _post_mark_consumed(fid):
    url = BASE.rstrip("/") + "/.netlify/functions/mark-consumed"
    body = json.dumps({"id": fid}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "x-api-key": KEY},
    )
    urllib.request.urlopen(req, timeout=15, context=_SSL)


try:
    raw = _ROOT.fetch("last_pending_json")
except Exception:
    raw = None

if not raw:
    pass
else:
    data = json.loads(raw)
    fish = data.get("fish") or []
    if fish:
        item = fish[0]
        fid = item.get("id")
        try:
            last = _ROOT.fetch("last_applied_fish_id")
        except Exception:
            last = ""
        if fid != last:
            url_tex = item.get("texture_url", "")
            name = item.get("display_name", "")
            mov = _ROOT.op("fish_movie")
            lbl = _ROOT.op("fish_label")
            cur = str(mov.par.file.eval())
            if cur != url_tex:
                mov.par.file = url_tex
                try:
                    mov.par.reloadpulse.pulse()
                except Exception:
                    pass
            lbl.par.text = name

            def _bg_mark():
                try:
                    _post_mark_consumed(fid)
                    err = ""
                except Exception as e:
                    err = str(e)

                def _done():
                    if err:
                        _ROOT.store("last_apply_error", err)
                    else:
                        _ROOT.store("last_applied_fish_id", fid)
                        _ROOT.store("last_apply_error", "")

                td.run(_done, delayFrames=1)

            threading.Thread(target=_bg_mark, daemon=True).start()
