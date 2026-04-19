"""
Create / refresh /project1/fish_tank_poll and wire DB → fish_movie_0..19.

Run from TouchDesigner Textport (or via MCP execute_python_script):

    exec(open(r"/path/to/fish-tank/touchdesigner/setup_fish_tank_poll_from_repo.py").read())

Edit REPO_TD below if your repo lives elsewhere. Then set netlify_config row0 = Netlify URL,
row1 = FISH_TANK_API_KEY, turn Realtime ON on fish_tank_poll, save the .toe.
"""
import os

import td

# Directory that contains poll_pending_fish.py, apply_fish_display.py, build_fish_school.py
def _resolve_repo_td():
    env = os.environ.get("FISH_TANK_TD_REPO", "").strip()
    if env and os.path.isfile(os.path.join(env, "build_fish_school.py")):
        return env
    here = "/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner"
    if os.path.isfile(os.path.join(here, "build_fish_school.py")):
        return here
    try:
        cand = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(cand, "build_fish_school.py")):
            return cand
    except NameError:
        pass
    return here


REPO_TD = _resolve_repo_td()


def _read(name):
    p = os.path.normpath(os.path.join(REPO_TD, name))
    with open(p, encoding="utf-8") as f:
        return f.read()


_p1 = op("/project1")
if not _p1:
    raise RuntimeError("Missing /project1")

P = op("/project1/fish_tank_poll")
if not P:
    P = _p1.create(td.baseCOMP, "fish_tank_poll")

# --- netlify_config (do not wipe user URLs) ---
_tbl = P.op("netlify_config")
if not _tbl:
    _tbl = P.create(td.tableDAT, "netlify_config")
    _tbl.clear()
    _tbl.appendRow(["https://YOUR_SITE.netlify.app"])
    _tbl.appendRow(["PASTE_FISH_TANK_API_KEY"])

# --- Script Text DATs from repo ---
def _ensure_textdat(name, body, as_python=True):
    d = P.op(name)
    if not d:
        d = P.create(td.textDAT, name)
    d.text = body
    if as_python:
        d.par.language = "python"
    return d


_ensure_textdat("poll_pending_fish", _read("poll_pending_fish.py"))
_ensure_textdat("apply_fish_display", _read("apply_fish_display.py"))

_dbg = P.op("debug_status")
if not _dbg:
    _dbg = P.create(td.textDAT, "debug_status")
_dbg.text = (
    "Set netlify_config: row0 = Netlify base URL, row1 = FISH_TANK_API_KEY. "
    "Turn Realtime ON. poll_lfo triggers poll_pending_fish → apply_fish_display."
)

# --- LFO poll trigger + CHOP Execute ---
_lfo = P.op("poll_lfo")
if not _lfo:
    _lfo = P.create(td.lfoCHOP, "poll_lfo")
    _lfo.par.wavetype = "square"
    _lfo.par.frequency = 0.5

_null = P.op("null1")
if not _null:
    _null = P.create(td.nullCHOP, "null1")
_null.inputConnectors[0].connect(_lfo)

_ex = P.op("poll_chopexec")
if not _ex:
    _ex = P.create(td.chopexecuteDAT, "poll_chopexec")
_ex.par.chop = _lfo
_ex.par.channel = "chan1"
_ex.par.offtoon = True
_ex.par.ontooff = False
_ex.par.valuechange = False
_ex.par.active = True
_ex.text = (
    "def onOffToOn(channel, sampleIndex, val, prev):\n"
    "    op('/project1/fish_tank_poll/poll_pending_fish').run()\n"
    "    return\n"
    "\n"
    "def whileOn(channel, sampleIndex, val, prev):\n"
    "    return\n"
    "\n"
    "def onOnToOff(channel, sampleIndex, val, prev):\n"
    "    return\n"
    "\n"
    "def whileOff(channel, sampleIndex, val, prev):\n"
    "    return\n"
)

try:
    P.par.opviewer = _null
except Exception:
    pass

# --- Output TOP for fish school (build_fish_school connects here) ---
_fo = P.op("fish_out")
if not _fo:
    try:
        _fo = P.create(td.outTOP, "fish_out")
    except Exception:
        _fo = P.create(td.nullTOP, "fish_out")

# --- 20 fish slots + grid → fish_out ---
exec(compile(_read("build_fish_school.py"), "build_fish_school.py", "exec"))

try:
    P.par.realtime = True
except Exception:
    pass


def _prime_poll():
    """One GET + apply after the new TOPs have cooked — no need to wait for poll_lfo edge."""
    try:
        op("/project1/fish_tank_poll/poll_pending_fish").run()
    except Exception as ex:
        print("prime poll:", ex)


try:
    td.run(_prime_poll, delayFrames=3)
except Exception:
    pass

print("OK:", P.path, "| Reloaded scripts + build_fish_school. Set netlify_config and save .toe.")
