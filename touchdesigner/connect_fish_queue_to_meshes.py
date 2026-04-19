"""
Wire the live database queue to all 20 animated fish meshes (no manual per-fish links).

This runs setup_fish_tank_poll_from_repo.py, which:
  - Loads poll_pending_fish + apply_fish_display from this folder
  - Builds fish_movie_0..19 → fish_matalpha_0..19 (Reorder A→R) → fish_pbr_0..19 → fish_mesh_rig_0..19 → fish_render_0..19 → fish_out
  - Hooks poll_lfo → poll_chopexec → poll (GET pending-fish) → apply (push URLs to Movie File In)

TouchDesigner Textport (use YOUR path if different):

    exec(open(r"/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner/connect_fish_queue_to_meshes.py", encoding="utf-8").read())

Then:
  1. netlify_config: row0 = https://YOURSITE.netlify.app   row1 = FISH_TANK_API_KEY
  2. Turn Realtime ON on /project1/fish_tank_poll
  3. Set viewer to TOP: /project1/fish_tank_poll/fish_out
  4. Save the .toe

Textures are applied automatically by apply_fish_display (not by hand). Optional: pending_texture_links
Table DAT lists the same URLs for inspection / expressions.
"""
import os

import td


def _repo_root():
    env = os.environ.get("FISH_TANK_TD_REPO", "").strip()
    if env and os.path.isfile(os.path.join(env, "setup_fish_tank_poll_from_repo.py")):
        return env
    here = "/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner"
    if os.path.isfile(os.path.join(here, "setup_fish_tank_poll_from_repo.py")):
        return here
    try:
        cand = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(cand, "setup_fish_tank_poll_from_repo.py")):
            return cand
    except NameError:
        pass
    return here


ROOT = _repo_root()
SETUP = os.path.join(ROOT, "setup_fish_tank_poll_from_repo.py")
exec(compile(open(SETUP, encoding="utf-8").read(), "setup_fish_tank_poll_from_repo.py", "exec"))

P = op("/project1/fish_tank_poll")
if P:
    t = P.op("pending_texture_links")
    if not t:
        t = P.create(td.tableDAT, "pending_texture_links")
        t.clear()
        t.appendRow(["slot", "id", "display_name", "texture_url"])

print("")
print("========== FISH QUEUE → 20 MESHES: CONNECTED ==========")
print("Data: Supabase pending → Netlify GET pending-fish")
print("Poll: poll_lfo → poll_pending_fish → last_pending_json + pending_texture_links")
print("Apply: apply_fish_display → fish_movie_0..19.par.file (HTTPS texture URLs)")
print("Render: fish_movie_N + fish_matalpha_N → fish_pbr_N → fish_mesh_rig_N → fish_render_N → grid → fish_out")
print("")
print("NEXT: 1) netlify_config  2) Realtime ON  3) viewer = fish_out  4) Save .toe")
print("See: touchdesigner/FISH_MESH_PIPELINE.md")
print("======================================================")
print("")
