# Fish Tank installation — groundwork

Stack: **Netlify** (web + serverless API) · **Supabase** (Postgres + Storage) · **TouchDesigner** (poll + show textures).

## Layout

| Path | Purpose |
|------|---------|
| `INSTALLATION_PIPELINE.md` | **Checklist:** what’s done vs open for the full install pipeline (cloud → venue). |
| `supabase/migrations/` | SQL: `fish_submissions` table + `fish-textures` bucket |
| `web/` | Vite + React + Tailwind kiosk UI + Netlify Functions |
| `touchdesigner/` | **`connect_fish_queue_to_meshes.py`** (recommended: DB → 20 meshes, see **`FISH_MESH_PIPELINE.md`**) · **`setup_fish_tank_poll_from_repo.py`** (poll + apply + `build_fish_school`) · `rebuild_fish_tank_poll_network.py` · `build_fish_school.py` · `setup_fish_mesh_rig.py` · `fix_fish_pbr_transparency.py` · `activate_fish_mesh_display.py` · `build_install_post_chain.py` · `cap_nc_resolution.py` · `repair_fish_tank_install_wiring.py` · `poll_pending_fish.py` · `apply_fish_display.py` |

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
  Response: `{ "fish": [ ... ], "returned": <n> }` — **`returned`** matches **`fish.length`**. **At most 20** rows, **newest pending first** (`created_at` descending). If more than 20 are pending in the DB, only the newest 20 are returned (older pendings stay queued until they rotate into the top 20 as others are consumed). TouchDesigner only **activates** as many slots as **`fish.length`** (zero if none pending).

- **POST** `/.netlify/functions/mark-consumed`  
  Header: `x-api-key`  
  Body: **`{ "id": "<uuid>" }`** (single) **or** **`{ "ids": ["<uuid>", ...] }`** (batch, up to 64 ids). Marks matching **pending** rows as **consumed** (optional — use for archiving or clearing the queue). **TouchDesigner does not call this automatically:** fish stay **pending** so the **GET** above always reflects the live **20 newest** drawings; otherwise rows would disappear from the queue after the first poll.

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
- **`apply_fish_display`** updates **`fish_movie_*`** on the main thread; **`reloadpulse`** when the texture **URL** changes. It does **not** POST **`mark-consumed`** so Supabase stays a live pending queue (20 newest).
- **`poll_lfo` frequency** is set to **0.2** (**5 s** between polls). Increase responsiveness by raising frequency (e.g. **0.33** ≈ 3 s); reduce load by lowering it.

## 6. TouchDesigner — show fish on screen (step 2)

### When a fish appears

Nothing is drawn until the backend has **at least one pending submission** and TouchDesigner has applied it:

1. Someone submits from the web → row stored as **pending** in Supabase.
2. **`poll_lfo` → `poll_pending_fish`** runs on your poll interval (e.g. every ~5 s).
3. **`apply_fish_display`** runs (from your CHOP Execute or manual pulse). It maps pending fish (**`texture_url`**) to **`fish_movie_0`…`19`** using **stable slots**: each grid cell keeps the same fish until that fish drops out of the API response or is evicted when the tank is full. **New** fish take the first empty slot, or replace the on-screen fish with the **oldest** `created_at`. Rows stay **pending** in the database; when there are **more than 20** pending, the API returns only the **20 newest** — older pendings are omitted until they appear in that window (or you **`mark-consumed`** / archive separately).

So fish show up on the **next successful poll + apply** after a kiosk submit—not instantly unless you shorten the LFO interval or trigger `poll_pending_fish` / `apply_fish_display` manually while testing.

### 3D mesh + kiosk texture (current install path)

To connect **live Supabase** textures to **all 20 fish meshes** without hand-wiring URLs, run **`touchdesigner/connect_fish_queue_to_meshes.py`** in **Textport** (see **`touchdesigner/FISH_MESH_PIPELINE.md`**). That runs **`setup_fish_tank_poll_from_repo.py`**, which creates/updates **`fish_tank_poll`**, loads **`poll_pending_fish`** / **`apply_fish_display`** from disk, and runs **`build_fish_school.py`**. Or run **`touchdesigner/build_fish_school.py`** alone in **Textport** to build **20** concurrent fish: **`fish_movie_0`…`fish_movie_19`**, each with its own **`fish_pbr_*`**, **`fish_mesh_rig_*`**, **`fish_render_*`** (256×180 tiles), labels, and a **5×4 grid** composited onto **`fish_out`**. **`apply_fish_display`** fills slots from the live API with **stable slot assignment** (see above), hides empty slots, and does **not** auto-**`mark-consumed`** (optional for archiving only).

Legacy single-fish path (`fish_movie`, one `fish_mesh_rig`) is replaced by this school; **`setup_fish_mesh_rig.py`** remains as a reference for one slot only.

**Viewer / empty mesh:** Inside a **Geometry COMP**, only one SOP should have **Display** and **Render** turned on (the terminal **`materialSOP`** — here **`mat1`**). If both flags are off on every SOP, the network looks empty and **`fish_render`** shows nothing. The setup script sets **`mat1.display` / `mat1.render`** to **True**; if you rebuild by hand, enable those flags on the last SOP in the chain.

**Transparent PNG / grey box around the fish:** The mesh is a full quad; the kiosk image is RGBA. **`fish_pbr`** should use **`alphamap`** = **`basecolormap`** and **`pointcolorpremult`** for straight-alpha PNGs. For a **hard cutout** (only drawn pixels shaded—true mask), enable **`alphatest`** with a small **`alphathreshold`** (~0.06); fragments below that alpha are discarded in the shader. Softer brush edges need a lower threshold; if fringes remain, raise it slightly. Run **`touchdesigner/fix_fish_pbr_transparency.py`** (edit `USE_ALPHATEST` / `ALPHATEST_THRESHOLD` at the top) to reapply.

Scripts on disk:

- `touchdesigner/setup_fish_tank_poll_from_repo.py` — **Textport**: create **`fish_tank_poll`**, load **`poll_pending_fish`** / **`apply_fish_display`**, run **`build_fish_school.py`** (optional env **`FISH_TANK_TD_REPO`** if scripts are not under the default path)
- `touchdesigner/apply_fish_display.py` — loaded into the **`apply_fish_display` Text DAT**
- `touchdesigner/setup_fish_mesh_rig.py` — recreate **`fish_mesh_rig`**, **`fish_pbr`**, **`fish_cam`**, **`fish_light`**, **`fish_render`** if you lose the 3D setup
- `touchdesigner/fix_fish_pbr_transparency.py` — apply PBR alpha settings only (no rebuild)

Behavior of **`apply_fish_display`**:

1. Reads `last_pending_json` (up to **20** fish; API order is newest first, but **slot order is stable** — see `last_slot_assignments` in **`fish_tank_poll`** storage).
2. Fills **`pending_texture_links`** (Table DAT) with one row per slot: **`slot`**, **`id`**, **`display_name`**, **`texture_url`**. Row **0** is the header; **rows 1–20** are **slots 0–19** in **stable grid order** (not “newest in row 1”). The table is updated when **`apply_fish_display`** runs (one frame after each successful poll by default). Use expressions like `op('/project1/fish_tank_poll/pending_texture_links')[slot + 1, 3]` for the HTTPS URL (column **3** = **`texture_url`**). Tune **`poll_lfo`** **frequency** to change how often the list updates.
3. Skips re-applying Movie File In textures if the per-slot **`id` + URL** fingerprint matches **`last_stable_display_fp`** (no duplicate work on the TOPs).
4. For each active slot, sets **`fish_movie_N.par.file`** to **`texture_url`**, **Specify Index** / **index 0**, **`loadingerrorimage` Zero**, **`predownloadhttp`**; **`fish_pbr_N`** samples that TOP.
5. Clears unused slots and hides them (**`fish_slot_vis_N`** opacity **0**).
6. Updates fingerprints and **`last_applied_fish_id`** (first occupied slot’s fish id when non-empty).

Display chain (20-fish): **`fish_grid_layer_19`** (stack) → **`fish_out`**. Set **`fish_tank_poll`** viewer to **`fish_out`** to preview.

If `apply_fish_display` fails to load from disk, paste the contents of `apply_fish_display.py` into the Text DAT manually.

### Non-Commercial resolution cap

Keep all generating **TOP** resolutions at **1280×1280 or smaller** (e.g. **1280×720** for 16:9). After edits, run `touchdesigner/cap_nc_resolution.py` in **Textport** to normalize **`fish_tank_install`** and **`fish_tank_poll`** TOPs. **`fish_movie`** texture decode is capped at **1024×1024** in that script to save GPU while staying under the limit.

### Troubleshooting: black plate + red square (Movie File In)

TouchDesigner’s **Movie File In** uses **Loading/Error Image → Colored Bottom Right Square** by default: **red** means the file failed to load (wrong format, bad URL, or empty `file`); **grey** means still downloading.

- **Empty slots** (`fish_movie_*` with no `file`) used to show that pattern; **`apply_fish_display`** + **`build_fish_school.py`** now set **`loadingerrorimage`** to **Zero** (blank) and **`playmode`** to **Specify Index** with **index 0** so still PNG/JPEG URLs from Supabase decode as a single frame.
- **WebP** is not in TouchDesigner’s documented still-image list for Movie File In. The kiosk **re-encodes uploaded files to PNG** in the browser; **`submit-fish`** rejects WebP if sent directly to the API.

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
5. **Fish:** `fish_plate` (**Select TOP** → `/project1/fish_tank_poll/fish_out`) → `fish_position` → `tank_scene` (**over** — `bubble_merge` under, fish on top).
6. **Grade & finish:** `tank_scene` → **`install_grade`** (HSV) → **`install_finish`** ( **add** a little **`install_grain`** noise ) → **`install_vignette`** ( **multiply** by radial **`vignette_ramp`** to darken edges / projector-friendly framing ).
7. **Output:** **`installation_out`** → **Perform** window TOP or projector.

If your project predates these nodes, run **`build_install_post_chain.py`** then **`repair_fish_tank_install_wiring.py`** in **Textport**.

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
| `install_grade` | **HSV Adjust TOP** — post color (sat/hue/value). |
| `install_grain` | **Noise TOP** — subtle animated grain (added in `install_finish`). |
| `install_finish` | **Composite** — **add** graded image + grain. |
| `vignette_ramp` | **Ramp TOP** (radial, table-driven) — cool edge darkening for multiply. |
| `install_vignette` | **Composite** — **multiply** finish × vignette. |
| `installation_out` | **Out TOP** — assign to **Perform** or master. |

**Repair wiring:** If a **Composite** shows *Not enough sources*, run `touchdesigner/repair_fish_tank_install_wiring.py` in **Textport** (reconnects inputs; use **`build_install_post_chain.py`** first if post nodes are missing).

**Viewer:** open **`fish_tank_install`** and set the node viewer to **`installation_out`**, or assign **`installation_out`** as the window **TOP** for Perform mode.

**Audio:** If levels look flat, check macOS microphone permission for TouchDesigner and pick the right **device** on `mic_in1`.

**Bubble opacity:** `bubble_level` opacity uses a parameter expression on **`audio_analyze`** (absolute TD path). If you rename ops, update the expression or use **CHOP export** / **Bind** instead.

## Installation pipeline checklist

See **`INSTALLATION_PIPELINE.md`** for a full **done / open** checklist (Supabase → Netlify → kiosk → TouchDesigner → venue Perform).

Optional art upgrades not yet in the default networks: **Particle GPU** bubbles, **Audio Spectrum** band-split, **Warp** / **SOP** seaweed, **multi-fish** queue in `apply_fish_display`, **CORS** / rate limits for production.
