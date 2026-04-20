# Text DAT body: run via op('apply_fish_display').run()
# Do NOT paste this script line-by-line into Textport — indented lines will IndentationError.
# Load the whole file: paste into this Text DAT, or in Textport:
#   exec(open(r"/absolute/path/to/apply_fish_display.py", encoding="utf-8").read())
# Maps live Supabase pending rows (via GET pending-fish) onto fish_movie_0 … fish_movie_19.
# Also fills Table DAT `pending_texture_links` — 20 rows (slot 0..19) with id, display_name,
# texture_url for wiring / inspection.
#
# Stable slots: each grid position keeps the same fish until that fish leaves the API
# response or is evicted. New submissions fill an empty slot, or replace the fish with
# the oldest created_at (LRU among on-screen). Other fish do not shuffle positions.
# Storage: last_slot_assignments = JSON list of 20 fish ids or null.
#
# Rows are NOT marked consumed here, so they stay pending until mark-consumed / status change.
#
# Per-slot swim: one float swim_<i>_tune from UUID (subtle ~±3%). Read only on TOP/COMP
# parms — not in pointSOP (per-vertex fetch was too heavy).

import json

import td

MAX_SLOTS = 20
_ROOT = op("/project1/fish_tank_poll")

_SWIM_KEYS = ("tune",)


def _fnv1a64(s):
    h = 1469598103934665603
    for b in (s or "").encode("utf-8"):
        h ^= b
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h


def _u01(h, salt):
    x = (h ^ (salt * 0x9E3779B97F4A7C15)) & 0xFFFFFFFFFFFFFFFF
    return (x % 1000000) / 1000000.0


def _swim_floats_from_uuid(fid):
    """Slight tempo scale only; same id → same value. Narrow band keeps motion near defaults."""
    h = _fnv1a64(fid)
    tune = round(0.97 + _u01(h, 1) * 0.06, 6)
    return {"tune": tune}


def _default_swim_floats():
    return {"tune": 1.0}


def _sync_swim_storage(slots):
    """Write swim_* keys for slots 0..19 from fish ids (neutral when empty)."""
    for i in range(MAX_SLOTS):
        fid = slots[i] if i < len(slots) else None
        vals = _swim_floats_from_uuid(fid) if fid else _default_swim_floats()
        for k in _SWIM_KEYS:
            try:
                _ROOT.store("swim_%d_%s" % (i, k), str(vals[k]))
            except Exception:
                pass


def _slot_ops(i):
    mov = _ROOT.op("fish_movie_%d" % i)
    lbl = _ROOT.op("fish_label_%d" % i)
    vis = _ROOT.op("fish_slot_vis_%d" % i)
    return mov, lbl, vis


def _fill_pending_texture_links_table(slots, by_id):
    """Table DAT: row 0 = header, rows 1..20 = slots 0..19 (stable slot order)."""
    t = _ROOT.op("pending_texture_links")
    if not t:
        try:
            t = _ROOT.create(td.tableDAT, "pending_texture_links")
        except Exception:
            return
    t.clear()
    t.appendRow(["slot", "id", "display_name", "texture_url"])
    for i in range(MAX_SLOTS):
        fid = slots[i] if i < len(slots) else None
        if fid and fid in by_id:
            b = by_id[fid]
            t.appendRow(
                [
                    str(i),
                    str(b.get("id", "")),
                    str(b.get("display_name", "")),
                    str(b.get("texture_url", "")),
                ]
            )
        else:
            t.appendRow([str(i), "", "", ""])


def _configure_movie_in(mov, has_url):
    """Movie File In: still PNG/JPEG from URL; avoid error-pattern + wrong frame index."""
    if not mov:
        return
    try:
        mov.par.playmode = "specify"
        mov.par.indexunit = "indices"
        mov.par.index = 0
        mov.par.loadingerrorimage = "zero"
    except Exception:
        pass
    if has_url:
        try:
            mov.par.predownloadhttp = True
        except Exception:
            pass


def _load_slot_assignments():
    try:
        raw = _ROOT.fetch("last_slot_assignments")
        if not raw:
            return None
        arr = json.loads(raw)
        if not isinstance(arr, list) or len(arr) != MAX_SLOTS:
            return None
        out = []
        for x in arr:
            if x is None or x == "":
                out.append(None)
            else:
                out.append(str(x))
        return out
    except Exception:
        return None


def _save_slot_assignments(slots):
    try:
        _ROOT.store(
            "last_slot_assignments",
            json.dumps([s if s else None for s in slots]),
        )
    except Exception:
        pass


def _bootstrap_slots_from_api_order(ordered_items, by_id):
    """First run: match legacy mapping — API order is newest first → slot 0 = newest."""
    slots = [None] * MAX_SLOTS
    idx = 0
    for it in ordered_items:
        if idx >= MAX_SLOTS:
            break
        raw_id = it.get("id")
        if raw_id is None:
            continue
        fid = str(raw_id)
        url = (it.get("texture_url") or "").strip()
        if not url:
            continue
        if fid not in by_id:
            continue
        slots[idx] = fid
        idx += 1
    return slots


def _merge_slots_stable(slots, by_id):
    """Drop ids no longer pending; assign newcomers to first gap or replace oldest on-screen."""
    api_ids = set(by_id.keys())
    slots = [(s if s in api_ids else None) for s in slots]
    assigned = {s for s in slots if s}
    newcomers = [fid for fid in api_ids if fid not in assigned]
    newcomers.sort(
        key=lambda fid: by_id[fid].get("created_at") or "",
        reverse=True,
    )
    for fid in newcomers:
        try:
            empty_i = slots.index(None)
            slots[empty_i] = fid
            continue
        except ValueError:
            pass
        occupied = [(i, slots[i]) for i in range(MAX_SLOTS) if slots[i]]
        if not occupied:
            slots[0] = fid
            continue
        victim_i = min(
            occupied,
            key=lambda t: by_id[t[1]].get("created_at") or "9999-12-31T23:59:59Z",
        )[0]
        slots[victim_i] = fid
    return slots


def _stable_display_fingerprint(slots, by_id):
    rows = []
    for i in range(MAX_SLOTS):
        fid = slots[i]
        u = by_id[fid]["texture_url"] if fid and fid in by_id else None
        rows.append([i, fid, u])
    return json.dumps(rows, sort_keys=True)


def _clear_all_slots():
    """No poll payload (or caller needs blank tank): empty every Movie File In + hide labels."""
    for i in range(MAX_SLOTS):
        mov, lbl, vis = _slot_ops(i)
        if not mov:
            continue
        _configure_movie_in(mov, False)
        mov.par.file = ""
        try:
            mov.par.reloadpulse.pulse()
        except Exception:
            pass
        if lbl:
            lbl.par.text = ""
        if vis:
            vis.par.opacity = 0


try:
    raw = _ROOT.fetch("last_pending_json")
except Exception:
    raw = None

if not raw:
    try:
        _ROOT.store("last_spawn_count", 0)
    except Exception:
        pass
    _sync_swim_storage([None] * MAX_SLOTS)
    _fill_pending_texture_links_table([None] * MAX_SLOTS, {})
    _clear_all_slots()
    try:
        _ROOT.store("last_stable_display_fp", "[]")
        _ROOT.store("last_slot_assignments", json.dumps([None] * MAX_SLOTS))
        _ROOT.store("last_apply_error", "")
        _ROOT.store("last_applied_fish_id", "")
    except Exception:
        pass
else:
    data = json.loads(raw)
    fish = data.get("fish") or []

    by_id = {}
    ordered_valid = []
    for it in fish:
        fid = it.get("id")
        url = (it.get("texture_url") or "").strip()
        if not fid or not url:
            continue
        fid = str(fid)
        rec = {
            "id": fid,
            "texture_url": url,
            "display_name": (it.get("display_name") or "").strip(),
            "created_at": str(it.get("created_at") or ""),
        }
        by_id[fid] = rec
        ordered_valid.append(it)

    if not by_id:
        _sync_swim_storage([None] * MAX_SLOTS)
        _fill_pending_texture_links_table([None] * MAX_SLOTS, {})
        _clear_all_slots()
        try:
            _ROOT.store("last_stable_display_fp", "[]")
            _ROOT.store("last_slot_assignments", json.dumps([None] * MAX_SLOTS))
            _ROOT.store("last_apply_error", "")
            _ROOT.store("last_applied_fish_id", "")
        except Exception:
            pass
        _ROOT.store("last_spawn_count", 0)
    else:
        prev = _load_slot_assignments()
        if prev is None:
            slots = _bootstrap_slots_from_api_order(ordered_valid, by_id)
        else:
            slots = _merge_slots_stable(prev, by_id)

        _save_slot_assignments(slots)
        _sync_swim_storage(slots)
        _fill_pending_texture_links_table(slots, by_id)

        fp = _stable_display_fingerprint(slots, by_id)
        try:
            last_fp = _ROOT.fetch("last_stable_display_fp")
        except Exception:
            last_fp = ""
        if fp != last_fp:
            for i in range(MAX_SLOTS):
                mov, lbl, vis = _slot_ops(i)
                if not mov:
                    continue
                fid = slots[i]
                if fid and fid in by_id:
                    b = by_id[fid]
                    url_tex = b["texture_url"]
                    name = b["display_name"]
                    cur = str(mov.par.file.eval())
                    _configure_movie_in(mov, True)
                    if cur != url_tex:
                        mov.par.file = url_tex
                        try:
                            mov.par.reloadpulse.pulse()
                        except Exception:
                            pass
                    if lbl:
                        lbl.par.text = name
                    if vis:
                        vis.par.opacity = 1
                else:
                    _configure_movie_in(mov, False)
                    mov.par.file = ""
                    try:
                        mov.par.reloadpulse.pulse()
                    except Exception:
                        pass
                    if lbl:
                        lbl.par.text = ""
                    if vis:
                        vis.par.opacity = 0

            _ROOT.store("last_apply_error", "")
            _ROOT.store("last_stable_display_fp", fp)
            try:
                first_id = next((slots[j] for j in range(MAX_SLOTS) if slots[j]), "")
                _ROOT.store("last_applied_fish_id", first_id or "")
            except Exception:
                pass

        _ROOT.store("last_spawn_count", sum(1 for s in slots if s))
