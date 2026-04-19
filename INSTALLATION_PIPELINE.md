# Fish Tank — installation creation pipeline

Use this as a **run-of-show checklist** from infrastructure through venue. Items marked **done** reflect the current repo + TouchDesigner networks as built in this project; **open** items are still on you for production.

---

## 1. Cloud & secrets

| Status | Task |
|--------|------|
| done | Supabase project; run `supabase/migrations/20260417000000_init_fish_tank.sql` (table + `fish-textures` bucket + RLS). |
| done | Netlify site linked; `web/` build (`npm run build` → `dist`). |
| open | Production env on Netlify: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `FISH_TANK_API_KEY` (rotate if ever leaked). |
| open | Optional: custom domain, HTTPS-only, analytics. |

---

## 2. Kiosk (web)

| Status | Task |
|--------|------|
| done | React app: name, fish canvas (masked draw, palette, grain path PNG), file upload, submit to `submit-fish`. |
| open | Kiosk hardware: tablet/PC, fullscreen browser, **guided reset** / idle timeout if needed. |
| open | Abuse: rate limits, Turnstile, or shared secret on `submit-fish` (see README security). |

---

## 3. TouchDesigner — data path

| Status | Task |
|--------|------|
| done | `netlify_config` filled (site URL + API key). **Realtime** on. |
| done | Async poll + `apply_fish_display` filling **`fish_movie_0`…`19`**, 3D **`fish_mesh_rig_*`**. API returns **up to 20 newest** pending rows; rows stay pending (no auto **`mark-consumed`**) so the live queue matches the website. |
| done | **20-fish school**: run `build_fish_school.py` (5×4 grid → `fish_out`). |
| done | PBR alpha: `alphamap`, cutout / blend via `fix_fish_pbr_transparency.py` (per-slot materials follow the same pattern). |
| done | Geometry: `mat1` display/render flags; remove default torus if any. |
| open | **Poll interval** tuned for venue (responsiveness vs GPU hitches). |

---

## 4. TouchDesigner — installation look (`fish_tank_install`)

| Status | Task |
|--------|------|
| done | Water stack: sand, seaweed, caustics, bubbles, fish plate → scene. |
| done | Post: `install_grade`, grain, radial vignette → `installation_out`. |
| done | NC-safe resolution: run `cap_nc_resolution.py` after topology changes. |
| open | **Final grade**: tune HSV, vignette table, grain amp for your projector. |
| open | **Fish layout**: grid positions in `build_fish_school.py` (`CELL_W` / `CELL_H`, swim exprs) for your aspect ratio & safe title area. |
| open | **Audio**: correct mic device; levels; optional spectrum split instead of single `analyze` channel. |
| open | **Bubbles / seaweed**: optional Particle GPU, SOP strands, or Warp TOPs — current setup is lightweight 2D/TOP. |

---

## 5. Venue & output

| Status | Task |
|--------|------|
| open | **Perform mode** (or output): assign **`installation_out`** as window TOP / projector output; test resolution (1280×720 or your cap). |
| open | **Machine**: Mac/PC with TD Non-Commercial (or license tier that matches your resolution policy). |
| open | **Fail-safe**: if API down, decide idle loop / placeholder (not implemented in repo). |
| open | **CORS / origins** on Netlify functions if you restrict the kiosk URL. |

---

## 6. Operations

| Status | Task |
|--------|------|
| open | Backup `.toe` + document paths to `touchdesigner/*.py` on the show machine. |
| open | Dry run: submit → see fish in TD within poll window; reboot test. |

---

## Quick script reference (Textport)

| Script | Use |
|--------|-----|
| `cap_nc_resolution.py` | After edits, enforce 1280×720 TOP cap (skips per-slot tile TOPs in `fish_tank_poll`). |
| `build_fish_school.py` | Build or rebuild the 20 concurrent fish network under `fish_tank_poll`. |
| `repair_fish_tank_install_wiring.py` | Fix composite inputs / bubble expr. |
| `build_install_post_chain.py` | Create grain + vignette nodes if missing. |
| `setup_fish_mesh_rig.py` | Legacy: one-slot 3D rig reference. |
| `fix_fish_pbr_transparency.py` | Reapply PBR alpha / cutout. |

---

## Summary

**In place:** Supabase schema, Netlify functions + web UI, TD poll/apply/3D fish with alpha, full install composite with grade + grain + vignette, docs in `README.md`.

**Still on the checklist:** venue Perform wiring, production hardening (abuse + CORS), richer FX if desired, ops backup & dry run, and final art tuning on site.
