# Fish Tank installation — groundwork

Stack: **Netlify** (web + serverless API) · **Supabase** (Postgres + Storage) · **TouchDesigner** (poll + show textures).

## Layout

| Path | Purpose |
|------|---------|
| `supabase/migrations/` | SQL: `fish_submissions` table + `fish-textures` bucket |
| `web/` | Vite + React + Tailwind kiosk UI + Netlify Functions |
| `touchdesigner/` | `rebuild_fish_tank_poll_network.py` · `setup_fish_mesh_rig.py` · `cap_nc_resolution.py` · `repair_fish_tank_install_wiring.py` · `poll_pending_fish.py` · `apply_fish_display.py` (paste or load into Text DATs) |

## 1. Supabase

1. Open your project in the Supabase dashboard.
2. Run `supabase/migrations/20260417000000_init_fish_tank.sql` in **SQL Editor** (or use the Supabase CLI if you link the project).
3. Confirm **Storage** contains bucket `fish-textures` (public read).

Secrets you need later:

- **Project URL** (`https://….supabase.co`)
- **anon** key (only if you add browser-direct Supabase later)
- **service_role** key (Netlify functions only — never in the browser or `.toe`)

## 2. Netlify environment

In the Netlify site: **Site configuration → Environment variables**:

| Variable | Where |
|----------|--------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role (secret) |
| `FISH_TANK_API_KEY` | Long random string; TouchDesigner sends this as header `x-api-key` on `pending-fish` and `mark-consumed` |

## 3. Deploy the web app

From `web/`:

```bash
npm install
npm run build
```

Connect the repo/folder to Netlify with **base directory** `fish-tank/web` (or repo root with build settings pointing at `web`), or deploy manually:

- Build command: `npm run build`
- Publish directory: `web/dist`

Local full stack (functions + Vite):

```bash
cd web
npm install
npx netlify dev
```

Use the printed URL. For `netlify dev`, same-origin requests to `/.netlify/functions/*` work without `VITE_FUNCTIONS_ORIGIN`.

## 4. API contract (stable for TD)

- **POST** `/.netlify/functions/submit-fish`  
  Body JSON: `{ "displayName": string, "imageBase64": string }`  
  Image: data URL or raw base64 (PNG/JPEG/WebP). Max ~2MB.

- **GET** `/.netlify/functions/pending-fish`  
  Header: `x-api-key: <FISH_TANK_API_KEY>`  
  Response: `{ "fish": [ { "id", "display_name", "texture_url", "created_at", "status" } ] }`

- **POST** `/.netlify/functions/mark-consumed`  
  Header: `x-api-key`  
  Body: `{ "id": "<uuid>" }` — marks that submission consumed after TD applies the texture.

## 5. TouchDesigner — poll network (`/project1/fish_tank_poll`)

Built in-network (or paste `touchdesigner/rebuild_fish_tank_poll_network.py` into **Textport** to recreate):

| OP | Role |
|----|------|
| `netlify_config` | Table DAT: row0 = Netlify base URL, row1 = `FISH_TANK_API_KEY` |
| `poll_pending_fish` | GET `pending-fish`, stores `last_pending_json` / `last_poll_error` |
| `poll_lfo` | Square LFO (default **0.2 Hz → 5 s** edges — was 2 s; reduces hitching) |
| `poll_chopexec` | Off→On → run `poll_pending_fish` (non-blocking HTTP + deferred apply) |
| `debug_status` | Last error + JSON snippet |

**Realtime** must be **on**.

### Performance (frame drops when polling)

Polling used to block the main cook thread (HTTP + TOP reload), which showed up as short **60 → ~20 FPS** hitches every interval.

- **`poll_pending_fish`** now does the GET in a **background thread** and uses **`td.run(..., delayFrames=1)`** to write storage / `debug_status` and trigger **`apply_fish_display`** on the main thread.
- **`apply_fish_display`** runs **`mark-consumed`** POST in a **thread**; TOP parameters stay on the main thread. **`reloadpulse`** only runs when the texture **URL** changes.
- **`poll_lfo` frequency** is set to **0.2** (**5 s** between polls). Increase responsiveness by raising frequency (e.g. **0.33** ≈ 3 s); reduce load by lowering it.

## 6. TouchDesigner — show fish on screen (step 2)

### When a fish appears

Nothing is drawn until the backend has **at least one pending submission** and TouchDesigner has applied it:

1. Someone submits from the web → row stored as **pending** in Supabase.
2. **`poll_lfo` → `poll_pending_fish`** runs on your poll interval (e.g. every ~5 s).
3. **`apply_fish_display`** runs (from your CHOP Execute or manual pulse). It takes the **first** pending fish, assigns **`texture_url`** to **`fish_movie`**, sets the label, then **marks consumed** so the queue advances.

So fish show up on the **next successful poll + apply** after a kiosk submit—not instantly unless you shorten the LFO interval or trigger `poll_pending_fish` / `apply_fish_display` manually while testing.

### 3D mesh + kiosk texture (current install path)

The drawn image is still the **`texture_url`** loaded by **`fish_movie`**. That TOP is wired as the **PBR base color map** (`fish_pbr`) on a simple **subdivided grid** inside **`fish_mesh_rig`**, with light **noise** on vertices (“swim”) and a gentle **transform** wobble on the whole geometry. **`fish_render`** (1280×720, Non-Commercial–safe) draws the mesh; **`fish_comp`** layers **`fish_label`** on top → **`fish_out`**.

Scripts on disk:

- `touchdesigner/apply_fish_display.py` — loaded into the **`apply_fish_display` Text DAT**
- `touchdesigner/setup_fish_mesh_rig.py` — recreate **`fish_mesh_rig`**, **`fish_pbr`**, **`fish_cam`**, **`fish_light`**, **`fish_render`** if you lose the 3D setup

Behavior of **`apply_fish_display`**:

1. Reads `last_pending_json`, takes the **first** pending fish (if any).
2. Skips if `id` equals stored `last_applied_fish_id` (no duplicate work).
3. Sets **`fish_movie`** `file` to `texture_url` (HTTPS; `predownloadhttp` helps). The same TOP feeds the 3D material.
4. Sets **`fish_label`** to `display_name`.
5. **POST** `mark-consumed` with that `id`, then stores `last_applied_fish_id`.
6. On failure, stores `last_apply_error`.

Display chain: **`fish_render`** + **`fish_label`** → **`fish_comp`** (**over**) → **`fish_out`**. Set **`fish_tank_poll`** viewer to **`fish_out`** to preview.

If `apply_fish_display` fails to load from disk, paste the contents of `apply_fish_display.py` into the Text DAT manually.

### Non-Commercial resolution cap

Keep all generating **TOP** resolutions at **1280×1280 or smaller** (e.g. **1280×720** for 16:9). After edits, run `touchdesigner/cap_nc_resolution.py` in **Textport** to normalize **`fish_tank_install`** and **`fish_tank_poll`** TOPs. **`fish_movie`** texture decode is capped at **1024×1024** in that script to save GPU while staying under the limit.

## Security notes (before public production)

- Public `submit-fish` can be abused: add rate limits, Turnstile, or a shared kiosk secret.
- Rotate `FISH_TANK_API_KEY` if leaked; TD only needs read + mark endpoints.

## 7. TouchDesigner — full-screen installation (`/project1/fish_tank_install`)

Use the same **1280×720** (or smaller) output size as the poll network so Non-Commercial limits are respected. Run **`cap_nc_resolution.py`** if anything was built at 1920×1080.

Signal chain (bottom → top of stack, then fish):

1. **Sand:** `tank_deep` + `sand_ramp` → `sand_merge` (over).
2. **Seaweed (2D):** `seaweed_noise` + `seaweed_tint` → `seaweed_mat` (multiply) → `seaweed_xform` → merged in `env_base` with `sand_merge`.
3. **Water:** `env_base` + `water_caustic` → `water_over_bg` (add).
4. **Bubbles:** `bubble_noise` → `bubble_level` (thresholded specks) → `bubble_merge` (over) with `water_over_bg`.
5. **Fish:** `fish_plate` (**Select TOP** → `/project1/fish_tank_poll/fish_out`) → `fish_position` → `tank_scene` (over) with `bubble_merge`.
6. **Output:** `installation_out` → **Perform** window TOP or projector.

| OP | Role |
|----|------|
| `mic_in1` | **Audio Device In CHOP** — live input (set **device** if needed). |
| `audio_analyze` | **Analyze CHOP** — level from mic (feeds water caustics + `bubble_level` opacity expr). |
| `tank_deep` | **Constant TOP** — deep water tint (full frame). |
| `sand_ramp` | **Ramp TOP** — vertical sand strip (merged under water). |
| `sand_merge` | **Composite** — sand + deep tint. |
| `seaweed_*` | **Noise / Constant / Composite / Transform** — soft green overlay (not full 3D seaweed). |
| `env_base` | **Composite** — sand stack + seaweed. |
| `water_caustic` | **Noise TOP** — caustics; **amp** can follow **audio_analyze**; **tx/ty** drift. |
| `water_over_bg` | **Composite** — **add** caustics onto `env_base`. |
| `bubble_noise` / `bubble_level` / `bubble_merge` | Sparkle / level / composite — light “bubbles” layer before fish. |
| `fish_plate` | **Select TOP** — **`/project1/fish_tank_poll/fish_out`**. |
| `fish_position` | **Transform TOP** — scales / positions fish (tune **sx/sy/tx/ty**). |
| `tank_scene` | **Composite** — **over** — water stack + fish. |
| `installation_out` | **Out TOP** — assign to **Perform** or master. |

**Repair wiring:** If a **Composite** shows *Not enough sources*, run `touchdesigner/repair_fish_tank_install_wiring.py` in **Textport** (reconnects inputs; does not recreate missing OPs).

**Viewer:** open **`fish_tank_install`** and set the node viewer to **`installation_out`**, or assign **`installation_out`** as the window **TOP** for Perform mode.

**Audio:** If levels look flat, check macOS microphone permission for TouchDesigner and pick the right **device** on `mic_in1`.

**Bubble opacity:** `bubble_level` opacity uses a parameter expression on **`audio_analyze`** (absolute TD path). If you rename ops, update the expression or use **CHOP export** / **Bind** instead.

## Next steps (installation art)

- **Bubbles:** richer motion (e.g. **Particle GPU**, band-split **Audio Spectrum** driving spawn) — current chain is lightweight TOP “sparkle”.
- **Seaweed / sand:** tune colors, **Warp** / displacement, or optional **SOP** geometry if you want real 3D strands.
- **Multiple fish**: extend `apply_fish_display` to cycle several pending rows or use instancing.
- **Scale / position** `fish_position` and `fish_comp` inside `fish_tank_poll` for your output resolution.
- Tighten CORS on functions if you lock origins.
