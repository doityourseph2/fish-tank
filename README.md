# Fish Tank installation — groundwork

Stack: **Netlify** (web + serverless API) · **Supabase** (Postgres + Storage) · **TouchDesigner** (poll + show textures).

## Layout

| Path | Purpose |
|------|---------|
| `supabase/migrations/` | SQL: `fish_submissions` table + `fish-textures` bucket |
| `web/` | Vite + React + Tailwind kiosk UI + Netlify Functions |
| `touchdesigner/scripts/` | Python snippet to poll pending fish from TD |

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

## 5. TouchDesigner

1. Copy `touchdesigner/scripts/fetch_pending_fish.py` logic into a **Script DAT** / **Execute DAT** (or `run` the module path TD exposes).
2. Set `NETLIFY_BASE` and `API_KEY` to match Netlify.
3. On a timer CHOP or pulse, parse JSON, download `texture_url` into a **File In TOP** or **Movie File In TOP** pattern you prefer, then call `mark-consumed` for applied IDs.

## Security notes (before public production)

- Public `submit-fish` can be abused: add rate limits, Turnstile, or a shared kiosk secret.
- Rotate `FISH_TANK_API_KEY` if leaked; TD only needs read + mark endpoints.

## Next steps when you return

- Wire TD: timer → fetch → TOP per fish + text COMP for `display_name`.
- Audio-reactive bubbles/water (inside TD, not this repo).
- Tighten CORS on functions if you lock origins.
