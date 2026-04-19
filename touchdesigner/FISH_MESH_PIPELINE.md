# Live fish queue → 20 animated meshes (automatic)

You do **not** need to paste 20 URLs by hand. The scripts below connect **Supabase** (pending textures) to **Movie File In → PBR → geometry → Render** for each slot.

## One command in TouchDesigner (Textport)

```text
exec(open(r"/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner/connect_fish_queue_to_meshes.py", encoding="utf-8").read())
```

(Edit the path if your repo lives elsewhere, or set env `FISH_TANK_TD_REPO` to the folder that contains `setup_fish_tank_poll_from_repo.py`.)

## After it runs

| Step | Action |
|------|--------|
| 1 | **`/project1/fish_tank_poll/netlify_config`**: row **0** = `https://<your-site>.netlify.app`, row **1** = `FISH_TANK_API_KEY` |
| 2 | **`fish_tank_poll`**: **Realtime = On** |
| 3 | Viewer: set to TOP **`fish_out`** (1280×720 school composite) |
| 4 | **File → Save** the `.toe` |

## Signal flow (what talks to what)

```text
Kiosk submit
    → Supabase: fish_submissions (pending) + fish-textures/pending/<id>.png

TouchDesigner poll_lfo (timer)
    → poll_chopexec
        → poll_pending_fish Text DAT (GET /.netlify/functions/pending-fish)
            → stores last_pending_json
            → fills Table DAT pending_texture_links (optional inspection)
            → runs apply_fish_display
                → fish_movie_0 … fish_movie_19 .par.file = texture_url
                → fish_label_*, fish_slot_vis_*

Per slot N:
    fish_movie_N  (Movie File In – HTTP PNG/JPEG)
        → fish_pbr_N base color map
        → fish_mesh_rig_N (grid + noise “swim”)
        → fish_render_N (256×180 tile)
        → fish_label_N overlaid in fish_cell_N → fish_tr_swim_N (2D tile wobble) → grid → fish_school_canvas → fish_out
    fish_mesh_rig_N: **swim_wave** (Point SOP) adds a **traveling sine** along texture **U** (body-length S-wave) + light **Z**; **swim** Noise SOP is reduced so it does not overpower the wave. **ry** is a smooth **0°→180°** Y turn synced to tile motion.
```

## Files in this folder

| File | Role |
|------|------|
| `connect_fish_queue_to_meshes.py` | **Start here** — runs full setup |
| `setup_fish_tank_poll_from_repo.py` | Loads Text DATs + `build_fish_school.py` |
| `poll_pending_fish.py` | HTTP poll + table + triggers apply |
| `apply_fish_display.py` | Writes texture URLs into `fish_movie_*` |
| `build_fish_school.py` | Builds the 20 mini rigs and `fish_out` |

## Troubleshooting

- **`debug_status`** on `fish_tank_poll` shows poll errors or “Poll OK.”
- **`pending_texture_links`**: same URLs as applied to `fish_movie_*` (after a successful poll).
- Black / red square on Movie File In: see main `README.md` (WebP, empty file, `loadingerrorimage`).
- **Installation**: `fish_plate` Select TOP → `/project1/fish_tank_poll/fish_out` (see `repair_fish_tank_install_wiring.py`).
