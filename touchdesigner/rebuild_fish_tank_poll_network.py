"""
Paste into TouchDesigner Textport (or run from Script DAT) to rebuild /project1/fish_tank_poll
after a crash. Destroys existing fish_tank_poll if present.

Fill netlify_config after: row0 = https://yoursite.netlify.app  row1 = FISH_TANK_API_KEY
Turn Realtime ON. Open fish_tank_poll and watch debug_status after a few seconds.
"""
import td

_p = op("/project1")
_n = "fish_tank_poll"
_c = _p.op(_n)
if _c:
    _c.destroy()
_c = _p.create(td.baseCOMP, _n)

_tbl = _c.create(td.tableDAT, "netlify_config")
_tbl.clear()
_tbl.appendRow(["https://YOUR_SITE.netlify.app"])
_tbl.appendRow(["PASTE_FISH_TANK_API_KEY"])

_pl = [
    "import json",
    "import ssl",
    "import urllib.error",
    "import urllib.request",
    "",
    "_ROOT = op('/project1/fish_tank_poll')",
    "_cfg = _ROOT.op('netlify_config')",
    "NETLIFY_BASE = str(_cfg[0, 0]).strip()",
    "API_KEY = str(_cfg[1, 0]).strip()",
    "POLL_PATH = '/.netlify/functions/pending-fish'",
    "_SSL = ssl._create_unverified_context()",
    "",
    "def fetch_pending():",
    "    url = NETLIFY_BASE.rstrip('/') + POLL_PATH",
    "    req = urllib.request.Request(",
    "        url,",
    "        headers={'x-api-key': API_KEY, 'Accept': 'application/json'},",
    "        method='GET',",
    "    )",
    "    with urllib.request.urlopen(req, timeout=15, context=_SSL) as resp:",
    "        return json.loads(resp.read().decode('utf-8'))",
    "",
    "try:",
    "    data = fetch_pending()",
    "    _ROOT.store('last_pending_json', json.dumps(data))",
    "    _ROOT.store('last_poll_error', '')",
    "except urllib.error.HTTPError as e:",
    "    _ROOT.store('last_pending_json', '')",
    "    _ROOT.store('last_poll_error', e.read().decode('utf-8', errors='replace'))",
    "except Exception as e:",
    "    _ROOT.store('last_pending_json', '')",
    "    _ROOT.store('last_poll_error', str(e))",
]
_d = _c.create(td.textDAT, "poll_pending_fish")
_d.text = "\n".join(_pl)
_d.par.language = "python"

_dbg = _c.create(td.textDAT, "debug_status")
_dbg.text = "Fill netlify_config row0=URL row1=API key. Realtime ON."

_lfo = _c.create(td.lfoCHOP, "poll_lfo")
_lfo.par.wavetype = "square"
_lfo.par.frequency = 0.5

_ex = _c.create(td.chopexecuteDAT, "poll_chopexec")
_ex.par.chop = _lfo
_ex.par.channel = "chan1"
_ex.par.offtoon = True
_ex.par.ontooff = False
_ex.par.valuechange = False
_ex.par.active = True

_cbl = [
    "def onOffToOn(channel, sampleIndex, val, prev):",
    "    op('/project1/fish_tank_poll/poll_pending_fish').run()",
    "    _r = op('/project1/fish_tank_poll')",
    "    try:",
    "        _e = _r.fetch('last_poll_error')",
    "    except:",
    "        _e = ''",
    "    try:",
    "        _j = _r.fetch('last_pending_json')",
    "    except:",
    "        _j = ''",
    "    nl = chr(10)",
    "    msg = 'ERR:' + nl + str(_e)[:1200] + nl + nl + 'JSON (trunc):' + nl + str(_j)[:1200]",
    "    _r.op('debug_status').text = msg",
    "    return",
    "",
    "def whileOn(channel, sampleIndex, val, prev):",
    "    return",
    "",
    "def onOnToOff(channel, sampleIndex, val, prev):",
    "    return",
    "",
    "def whileOff(channel, sampleIndex, val, prev):",
    "    return",
]
_ex.text = "\n".join(_cbl)

_null = _c.create(td.nullCHOP, "null1")
_null.inputConnectors[0].connect(_lfo)
_c.par.opviewer = _null

print("OK:", _c.path, [x.name for x in _c.children])
